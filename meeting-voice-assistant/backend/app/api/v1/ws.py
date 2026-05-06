"""
WebSocket 语音识别路由

提供实时语音识别接口
"""

import asyncio
import json
import uuid
from typing import Optional
from datetime import datetime

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from app.core.asr import ASRFactory, ASRResult
from app.core.parser import MeetingInfoExtractor
from app.core.llm_analyzer import LLMAnalyzer
from app.core.session_store import SessionStatus, get_session_store_sync
from app.config import config
from app.utils.logger import setup_logger, RequestContext
from app.api.v1.auth import verify_ws_api_key
from app.core.auth.jwt_handler import verify_token as verify_jwt_token
from app.config import config
from app.api.v1.voice_session import (
    AudioBuffer,
    TranscriptionHandler,
    SessionStateManager,
    MeetingAnalyzer,
    GraphRAGNotifier,
)

logger = setup_logger("ws.voice")

router = APIRouter()


class VoiceSession:
    """语音识别会话"""

    def __init__(self, websocket: WebSocket, session_id: Optional[str] = None):
        self.websocket = websocket
        self.asr_adapter = ASRFactory.create(config.asr.engine)
        self.meeting_extractor = MeetingInfoExtractor()
        self._running = False
        self._processing = False
        self._closed = False
        self._tasks: list[asyncio.Task] = []

        # 初始化组件
        self.audio_buffer = AudioBuffer(
            cache_dir=config.cache.cache_dir,
            max_chunks=1000,
            max_total_bytes=100 * 1024 * 1024
        )
        self.transcription_handler = TranscriptionHandler(
            session_id=session_id or f"sess_{uuid.uuid4().hex[:8]}"
        )
        self.state_manager = SessionStateManager(
            session_id=self.transcription_handler.session_id,
            started_at=datetime.now()
        )
        self.llm_analyzer = LLMAnalyzer(
            provider=config.llm.provider,
            api_key=config.llm.dashscope_api_key,
            endpoint=config.llm.dashscope_endpoint,
            model=config.llm.dashscope_model
        )
        self.meeting_analyzer = MeetingAnalyzer(
            session_id=self.transcription_handler.session_id,
            started_at=datetime.now(),
            llm_analyzer=self.llm_analyzer,
            transcripts_holder=self.transcription_handler.transcripts
        )
        self.graphrag_notifier = GraphRAGNotifier(
            session_id=self.transcription_handler.session_id,
            started_at=datetime.now(),
            transcripts_holder=self.transcription_handler.transcripts
        )

        # 会话 ID 和状态恢复
        if session_id:
            self.transcription_handler.session_id = session_id
            self.state_manager.session_id = session_id
            self.meeting_analyzer.session_id = session_id
            self.graphrag_notifier.session_id = session_id
            self._restore_state()
        else:
            self.transcription_handler.session_id = f"sess_{uuid.uuid4().hex[:8]}"
            self.state_manager.session_id = self.transcription_handler.session_id
            self.meeting_analyzer.session_id = self.transcription_handler.session_id
            self.graphrag_notifier.session_id = self.transcription_handler.session_id
            self.state_manager.create()

    @property
    def session_id(self) -> str:
        return self.transcription_handler.session_id

    @property
    def started_at(self) -> datetime:
        return self.state_manager.started_at

    @property
    def seq(self) -> int:
        return self.transcription_handler.seq

    @seq.setter
    def seq(self, value: int) -> None:
        self.transcription_handler.seq = value

    @property
    def transcripts(self) -> list:
        return self.transcription_handler.transcripts

    @property
    def audio_chunks(self) -> list[bytes]:
        """Compatibility view for older tests and integrations."""
        return self.audio_buffer.chunks

    @property
    def _max_audio_chunks(self) -> int:
        return self.audio_buffer.max_chunks

    @property
    def _max_audio_bytes(self) -> int:
        return self.audio_buffer.max_total_bytes

    @property
    def _max_total_bytes(self) -> int:
        return self.audio_buffer.max_total_bytes

    def _restore_state(self) -> None:
        """恢复会话状态"""
        if self.state_manager.restore():
            restored_transcripts = self.state_manager.get_transcripts_for_restore()
            self.transcription_handler.transcripts = restored_transcripts
            self.transcription_handler.seq = self.state_manager.get_seq_for_restore()
            logger.info(
                f"[Session {self.session_id}] Restored state: "
                f"{len(restored_transcripts)} transcripts, seq={self.seq}"
            )

    async def _save_state(self) -> None:
        """保存当前会话状态"""
        status = SessionStatus.PROCESSING if self._processing else (
            SessionStatus.RECORDING if self._running else SessionStatus.IDLE
        )
        await self.state_manager.save(
            status=status,
            transcripts=self.transcription_handler.transcripts,
            audio_chunks_count=len(self.audio_buffer.chunks),
            seq=self.transcription_handler.seq
        )

    async def initialize(self) -> None:
        """初始化会话"""
        logger.info(f"Initializing session {self.session_id}")
        await self.asr_adapter.start()

    async def send_welcome(self) -> None:
        """发送欢迎消息"""
        await self.websocket.send_json({
            "type": "welcome",
            "session_id": self.session_id,
            "config": {
                "sample_rate": 16000,
                "channels": 1,
            }
        })

    async def _send_status(
        self,
        status: str,
        message: str,
        progress: int = 0
    ) -> None:
        """发送状态消息"""
        if self._closed:
            logger.warning(
                f"[Session {self.session_id}] WebSocket already closed, "
                "skipping status send"
            )
            return
        try:
            await self.websocket.send_json({
                "type": "status",
                "status": status,
                "message": message,
                "progress": progress
            })
            logger.info(
                f"[Session {self.session_id}] Status: {status} - "
                f"{message} ({progress}%)"
            )
        except Exception as e:
            logger.warning(
                f"[Session {self.session_id}] Failed to send status: {e}"
            )
            self._closed = True

    async def _send_json(self, data: dict) -> None:
        """发送 JSON 消息到 WebSocket"""
        if self._closed:
            return
        try:
            await self.websocket.send_json(data)
        except Exception as e:
            logger.warning(
                f"[Session {self.session_id}] Failed to send JSON: {e}"
            )
            self._closed = True

    async def handle_control(self, data: dict) -> None:
        """处理控制消息"""
        action = data.get("action")

        if action == "start":
            logger.info(
                f"Session {self.session_id}: Recognition started"
            )
            self._processing = False
            self.audio_buffer.clear()
            self.transcription_handler.clear()

            if not self.asr_adapter.is_running:
                await self.asr_adapter.start()

            self._running = True
            await self._save_state()

            await self._send_json({
                "type": "ack",
                "action": "start",
                "message": "Recognition started"
            })
            self._tasks.append(
                asyncio.create_task(self.run_recognition())
            )

        elif action == "stop":
            logger.info(
                f"Session {self.session_id}: Recognition stopped"
            )
            self._running = False
            self._processing = True
            await self._save_state()

            await self._send_json({
                "type": "ack",
                "action": "stop",
                "message": "Recognition stopped"
            })
            self._tasks.append(
                asyncio.create_task(self._process_after_stop())
            )

        elif action == "pause":
            self._running = False
            await self._send_json({
                "type": "ack",
                "action": "pause",
                "message": "Recognition paused"
            })

        elif action == "resume":
            self._running = True
            await self._send_json({
                "type": "ack",
                "action": "resume",
                "message": "Recognition resumed"
            })

    async def _process_after_stop(self) -> None:
        """停止后的处理流程"""
        try:
            # 1. 发送状态：正在缓存音频
            if self._closed:
                return
            await self._send_status("processing", "正在保存音频...", 10)
            if self._closed:
                return

            # 保存音频
            audio_path = await self.audio_buffer.save(self.session_id)

            # 2. 发送状态：正在识别
            if self._closed:
                return
            await self._send_status("transcribing", "正在识别语音...", 30)

            # 完成 ASR 识别
            await self._finish_recognition()

            # 3. 发送状态：正在分析
            if self._closed:
                return
            await self._send_status("analyzing", "正在分析会议内容...", 70)

            # 调用 LLM 分析
            try:
                analysis_result = await self.meeting_analyzer.analyze(audio_path)
            except Exception as e:
                error_msg = str(e)
                if "timeout" in error_msg.lower():
                    logger.error(f"[Session {self.session_id}] LLM analysis timeout")
                    if not self._closed:
                        await self._send_status("error", "LLM 分析超时，服务器负载较高，请稍后重试", 100)
                    return
                raise

            # 4. 发送分析结果
            if self._closed:
                return
            try:
                await self._send_json({
                    "type": "analysis_result",
                    "data": {
                        "summary": analysis_result.summary,
                        "key_points": analysis_result.key_points,
                        "action_items": analysis_result.action_items,
                        "topics": analysis_result.topics
                    }
                })
            except Exception as e:
                logger.warning(
                    f"[Session {self.session_id}] Failed to send analysis result: {e}"
                )
                self._closed = True
                return

            # 5. 发送完成状态
            await self._send_status("completed", "处理完成", 100)

            # 发送完成控制消息
            await self._send_json({
                "type": "control",
                "action": "completed"
            })

            # 6. 保存转写文本到文件
            await self.meeting_analyzer.save_transcript_text(analysis_result)

            # 7. 触发 GraphRAG 自动索引
            if config.graphrag.auto_index:
                task = asyncio.create_task(
                    self.graphrag_notifier.notify(analysis_result)
                )
                self._tasks.append(task)

        except Exception as e:
            logger.error(f"[Session {self.session_id}] Processing error: {e}")
            if not self._closed:
                await self._send_status("error", f"处理失败: {str(e)}", 100)

    async def _finish_recognition(self) -> None:
        """完成识别流程，处理剩余的音频数据"""
        if not self.asr_adapter:
            return

        try:
            await self.asr_adapter.commit()
            await self.asr_adapter.finish()

            await asyncio.sleep(2)

            while True:
                result = await asyncio.wait_for(
                    self.asr_adapter.get_result(timeout=0.5),
                    timeout=1.0
                )
                if result is None:
                    break

                segments = result.transcript if hasattr(result, 'transcript') else [result]

                for seg in segments:
                    self.transcription_handler.transcripts.append(seg)
                    self.transcription_handler.seq += 1
                    try:
                        await self._send_json({
                            "type": "transcript",
                            "seq": self.transcription_handler.seq,
                            "data": {
                                "text": seg.text,
                                "start_time": seg.start_time,
                                "end_time": seg.end_time,
                                "speaker": seg.speaker,
                                "confidence": seg.confidence,
                                "is_final": True
                            }
                        })
                    except Exception as e:
                        logger.warning(
                            f"[Session {self.session_id}] Failed to send transcript: {e}"
                        )

        except asyncio.TimeoutError:
            logger.info(
                f"[Session {self.session_id}] No more results to collect"
            )
        except Exception as e:
            logger.warning(
                f"[Session {self.session_id}] ASR finish error: {e}"
            )

    async def process_audio(self, audio_data: bytes) -> None:
        """处理音频数据"""
        self.audio_buffer.append(audio_data)

        if self._running and self.asr_adapter and self.asr_adapter.is_running:
            try:
                await self.asr_adapter.process_audio(audio_data)
            except Exception as e:
                logger.warning(
                    f"[Session {self.session_id}] Failed to append audio: {e}"
                )

        # 每处理 100 个音频块保存一次状态
        if len(self.audio_buffer.chunks) % 100 == 0:
            await self._save_state()

    async def run_recognition(self) -> None:
        """运行识别循环 - 实时发送识别结果"""
        last_commit_time = 0.0
        commit_interval = 1.0

        try:
            while self._running:
                await asyncio.sleep(0.1)
                last_commit_time += 0.1

                if last_commit_time >= commit_interval:
                    try:
                        result = await self.asr_adapter.commit()
                        if result and result.text:
                            await self.transcription_handler.handle_result(
                                result,
                                self._send_json
                            )
                            await self._save_state()

                        last_commit_time = 0
                    except Exception as e:
                        logger.warning(
                            f"[Session {self.session_id}] Commit error: {e}"
                        )

        except Exception as e:
            logger.error(f"Recognition error: {e}")
            if not self._processing:
                try:
                    await self._send_json({
                        "type": "error",
                        "code": "RECOGNITION_ERROR",
                        "message": str(e)
                    })
                except Exception:
                    pass

    async def cleanup(self) -> None:
        """清理会话资源"""
        logger.info(f"Cleaning up session {self.session_id}")
        self._running = False
        self._processing = False

        await self._save_state()

        for task in self._tasks:
            if not task.done():
                task.cancel()
        if self._tasks:
            await asyncio.gather(*self._tasks, return_exceptions=True)
        self._tasks.clear()

        await self.asr_adapter.stop()
        await self.llm_analyzer.close()
        self.meeting_extractor.reset()
        self.audio_buffer.close()


async def verify_ws_jwt_token(token: str) -> bool:
    """
    验证 WebSocket JWT token

    Args:
        token: query param 中的 JWT token

    Returns:
        True 表示认证成功，False 表示认证失败
    """
    # 开发模式：跳过 JWT 验证
    if config.jwt.dev_mode and config.jwt.dev_bypass_auth:
        logger.debug("WS JWT Auth disabled: dev_mode with bypass")
        return True

    if not token:
        logger.warning("WS JWT auth failed: missing token")
        return False

    payload = verify_jwt_token(token)
    if payload is None:
        logger.warning("WS JWT auth failed: invalid token")
        return False

    if payload.get("type") != "access":
        logger.warning("WS JWT auth failed: invalid token type")
        return False

    return True


@router.websocket("/ws/voice")
async def voice_websocket(
    websocket: WebSocket,
    api_key: str = Query(None),
    token: str = Query(None),
    session_id: Optional[str] = Query(None)
):
    """
    实时语音识别 WebSocket 端点

    连接流程:
    1. 建立 WebSocket 连接
    2. 接收欢迎消息 (包含 session_id)
    3. 发送 start 控制消息
    4. 发送音频数据 (二进制)
    5. 接收识别结果 (JSON)
    6. 发送 stop 控制消息
    7. 关闭连接

    认证（优先级: JWT > API Key）:
    - JWT: ?token=<jwt_token> (推荐方式)
    - API Key: ?api_key=<key> (兼容旧版)
    - 开发模式: DEV_BYPASS_AUTH=true 时跳过认证

    会话恢复:
    - 支持通过 session_id query 参数恢复断开的会话
    - 格式: ws://host/api/v1/ws/voice?session_id=<session_id>
    - 恢复后会收到恢复确认消息，包含已保存的转写记录
    """
    # JWT 认证优先
    if token:
        if not await verify_ws_jwt_token(token):
            await websocket.close(code=4001, reason="Unauthorized")
            return
        logger.debug("WS auth: JWT token verified")
    elif api_key:
        # API Key 认证（兼容旧版）
        if not await verify_ws_api_key(websocket, api_key):
            await websocket.close(code=4001, reason="Unauthorized")
            return
        logger.debug("WS auth: API key verified")
    else:
        # 开发模式认证
        if config.jwt.dev_mode and config.jwt.dev_bypass_auth:
            logger.debug("WS auth: dev mode bypass")
        else:
            # 无认证凭证且非开发模式
            logger.warning("WS auth failed: no credentials provided")
            await websocket.close(code=4001, reason="Unauthorized")
            return

    session_store = get_session_store_sync()
    session_store.cleanup_expired_sessions(max_age_seconds=3600)

    # 获取超时配置
    ws_connect_timeout = config.timeout.ws_connect_timeout if hasattr(config, 'timeout') else 10.0

    try:
        # WebSocket 连接超时
        await asyncio.wait_for(websocket.accept(), timeout=ws_connect_timeout)
        logger.info("WebSocket connection accepted")
    except asyncio.TimeoutError:
        logger.error("WebSocket connection timeout")
        await websocket.close(code=4002, reason="Connection timeout")
        return

    session: Optional[VoiceSession] = None

    try:
        with RequestContext():
            restored = False
            if session_id:
                existing = session_store.get_session(session_id)
                if existing and existing.status in [SessionStatus.IDLE, SessionStatus.RECORDING]:
                    restored = True
                    logger.info(f"Reconnecting to existing session: {session_id}")

            session = VoiceSession(
                websocket,
                session_id=session_id if restored else None
            )

            # 会话初始化超时
            try:
                await asyncio.wait_for(session.initialize(), timeout=ws_connect_timeout)
            except asyncio.TimeoutError:
                logger.error(f"Session initialization timeout for {session.session_id}")
                await websocket.send_json({
                    "type": "error",
                    "code": "INIT_TIMEOUT",
                    "message": "ASR 初始化超时，请检查网络连接后重试"
                })
                session._closed = True
                return

            await session.send_welcome()

            if restored and session.transcription_handler.transcripts:
                await websocket.send_json({
                    "type": "session_restored",
                    "session_id": session.session_id,
                    "transcripts": [
                        {
                            "text": t.text,
                            "start_time": t.start_time,
                            "end_time": t.end_time,
                            "speaker": t.speaker,
                            "confidence": t.confidence,
                            "is_final": t.is_final
                        }
                        for t in session.transcription_handler.transcripts
                    ],
                    "seq": session.seq
                })
                logger.info(
                    f"[Session {session.session_id}] Sent restoration data: "
                    f"{len(session.transcription_handler.transcripts)} transcripts"
                )

            # 空闲超时配置
            ws_idle_timeout = config.timeout.ws_idle_timeout if hasattr(config, 'timeout') else 300.0

            while True:
                try:
                    # 使用空闲超时接收消息
                    data = await asyncio.wait_for(websocket.receive(), timeout=ws_idle_timeout)
                    logger.debug(
                        f"[Session {session.session_id}] Received data keys: {list(data.keys())}"
                    )

                    if "bytes" in data:
                        audio_data = data["bytes"]
                        logger.debug(
                            f"[Session {session.session_id}] Received audio frame: "
                            f"{len(audio_data)} bytes"
                        )
                        await session.process_audio(audio_data)

                    elif "text" in data:
                        import json
                        msg = json.loads(data["text"])
                        msg_type = msg.get("type")
                        logger.info(
                            f"[Session {session.session_id}] Received text message: "
                            f"type={msg_type}, action={msg.get('action', 'N/A')}, "
                            f"_closed={session._closed}"
                        )

                        if msg_type == "control":
                            await session.handle_control(msg)
                        else:
                            logger.warning(f"Unknown message type: {msg_type}")
                            await websocket.send_json({
                                "type": "error",
                                "code": "UNKNOWN_MESSAGE_TYPE",
                                "message": f"Unknown message type: {msg_type}"
                            })
                except asyncio.TimeoutError:
                    logger.warning(f"[Session {session.session_id}] WebSocket idle timeout")
                    await websocket.send_json({
                        "type": "error",
                        "code": "IDLE_TIMEOUT",
                        "message": "WebSocket 空闲超时，请检查网络连接"
                    })
                    break

    except WebSocketDisconnect:
        logger.info("Client disconnected")
        if session:
            session._closed = True

    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        error_message = str(e)
        # 判断是否是超时错误
        if "timeout" in error_message.lower():
            error_code = "TIMEOUT_ERROR"
            user_message = "请求超时，请检查网络连接后重试"
        else:
            error_code = "WS_ERROR"
            user_message = "WebSocket 连接错误，请稍后重试"

        if session and not session._closed:
            try:
                await session.websocket.send_json({
                    "type": "error",
                    "code": error_code,
                    "message": user_message
                })
            except Exception:
                pass

    finally:
        if session:
            session._closed = True
            await session.cleanup()
