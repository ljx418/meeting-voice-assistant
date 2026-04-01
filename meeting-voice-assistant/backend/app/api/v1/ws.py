"""
WebSocket 语音识别路由

提供实时语音识别接口
"""

import asyncio
import json
import uuid
from typing import Optional
from datetime import datetime

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse

import sys
from pathlib import Path

# Add backend directory to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from app.core.asr import ASRFactory, ASRResult
from app.core.parser import MeetingInfoExtractor
from app.core.audio_cache import AudioCache
from app.core.llm_analyzer import LLMAnalyzer, AnalysisResult
from app.config import config
from app.utils.logger import setup_logger, RequestContext

logger = setup_logger("ws.voice")

router = APIRouter()


class VoiceSession:
    """语音识别会话"""

    def __init__(self, websocket: WebSocket):
        self.session_id = f"sess_{uuid.uuid4().hex[:8]}"
        self.websocket = websocket
        # 使用配置的 ASR 引擎（支持 funasr_realtime 进行说话人分离）
        self.asr_adapter = ASRFactory.create(config.ASR_ENGINE)
        self.meeting_extractor = MeetingInfoExtractor()
        self.started_at = datetime.now()
        self.seq = 0
        self._audio_queue: asyncio.Queue = asyncio.Queue()
        self._running = False
        self._processing = False  # 是否正在处理（stop后）
        self._closed = False  # 连接是否已关闭

        # 音频缓存
        self.audio_cache = AudioCache(config.AUDIO_CACHE_DIR)
        self.audio_chunks: list[bytes] = []
        self.transcripts: list[ASRResult] = []

        # LLM 分析器
        self.llm_analyzer = LLMAnalyzer(
            provider=config.LLM_PROVIDER,
            api_key=config.LLM_API_KEY,
            endpoint=config.LLM_ENDPOINT,
            model=config.LLM_MODEL
        )

    async def initialize(self) -> None:
        """初始化会话"""
        logger.info(f"Initializing session {self.session_id}")
        await self.asr_adapter.initialize()

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
            logger.warning(f"[Session {self.session_id}] WebSocket already closed, skipping status send")
            return
        try:
            await self.websocket.send_json({
                "type": "status",
                "status": status,
                "message": message,
                "progress": progress
            })
            logger.info(f"[Session {self.session_id}] Status: {status} - {message} ({progress}%)")
        except Exception as e:
            logger.warning(f"[Session {self.session_id}] Failed to send status: {e}")
            self._closed = True

    async def handle_control(self, data: dict) -> None:
        """处理控制消息"""
        action = data.get("action")

        if action == "start":
            logger.info(f"Session {self.session_id}: Recognition started")
            self._processing = False
            self.audio_chunks.clear()
            self.transcripts.clear()

            # 初始化并连接 ASR 适配器（先于 _running 标志）
            if not self.asr_adapter.is_initialized:
                await self.asr_adapter.initialize()
            await self.asr_adapter.connect()

            # 连接建立后再设置运行标志
            self._running = True

            await self.websocket.send_json({
                "type": "ack",
                "action": "start",
                "message": "Recognition started"
            })
            # 启动实时识别循环
            asyncio.create_task(self.run_recognition())

        elif action == "stop":
            logger.info(f"Session {self.session_id}: Recognition stopped")
            self._running = False
            self._processing = True

            await self.websocket.send_json({
                "type": "ack",
                "action": "stop",
                "message": "Recognition stopped"
            })

            # 处理后续流程（缓存、识别、分析）
            asyncio.create_task(self._process_after_stop())

        elif action == "pause":
            self._running = False
            await self.websocket.send_json({
                "type": "ack",
                "action": "pause",
                "message": "Recognition paused"
            })

        elif action == "resume":
            self._running = True
            await self.websocket.send_json({
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
            audio_path = None
            logger.info(f"[Session {self.session_id}] _process_after_stop: AUDIO_CACHE_ENABLED={config.AUDIO_CACHE_ENABLED}, audio_chunks len={len(self.audio_chunks)}")
            if config.AUDIO_CACHE_ENABLED and self.audio_chunks:
                audio_data = b''.join(self.audio_chunks)
                logger.info(f"[Session {self.session_id}] Saving audio: {len(self.audio_chunks)} chunks, {len(audio_data)} bytes")
                audio_path = await self.audio_cache.save_audio(
                    self.session_id,
                    audio_data
                )
                logger.info(f"[Session {self.session_id}] Audio cached: {audio_path}")
            else:
                logger.warning(f"[Session {self.session_id}] Audio not saved: audio_chunks empty or cache disabled")

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
            analysis_result = await self._analyze_meeting(audio_path)

            # 4. 发送分析结果
            if self._closed:
                return
            try:
                await self.websocket.send_json({
                    "type": "analysis_result",
                    "data": {
                        "summary": analysis_result.summary,
                        "key_points": analysis_result.key_points,
                        "action_items": analysis_result.action_items,
                        "topics": analysis_result.topics
                    }
                })
            except Exception as e:
                logger.warning(f"[Session {self.session_id}] Failed to send analysis result: {e}")
                self._closed = True
                return

            # 5. 发送完成状态
            await self._send_status("completed", "处理完成", 100)

            # 6. 保存转写文本到文件 (带 LLM 分析结果)
            await self._save_transcript_text(analysis_result)

        except Exception as e:
            logger.error(f"[Session {self.session_id}] Processing error: {e}")
            if not self._closed:
                await self._send_status("error", f"处理失败: {str(e)}", 100)

    def _format_speaker(self, speaker: str) -> str:
        """将说话人 ID 转换为可读标签"""
        if not speaker or speaker == "unknown":
            return "发言人"
        # speaker_0 -> 发言人 A, speaker_1 -> 发言人 B, ...
        if speaker.startswith("speaker_"):
            try:
                idx = int(speaker.split("_")[1])
                # A=0, B=1, C=2, ...
                label = chr(ord('A') + idx)
                return f"发言人 {label}"
            except (IndexError, ValueError):
                return "发言人"
        return speaker

    def _format_timestamp(self, seconds: float) -> str:
        """将秒数格式化为 HH:MM:SS"""
        if seconds <= 0:
            return "00:00:00"
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"

    async def _save_transcript_text(self, analysis_result=None) -> None:
        """保存转写文本到文件"""
        if not self.transcripts:
            logger.warning(f"[Session {self.session_id}] No transcripts to save")
            return

        try:
            # 计算总时长
            total_duration = max(t.end_time for t in self.transcripts) if self.transcripts else 0

            # 构建文本内容
            lines = []
            lines.append(f"# 会议转写文本")
            lines.append(f"# Session ID: {self.session_id}")
            lines.append(f"# 开始时间: {self.started_at.strftime('%Y-%m-%d %H:%M:%S')}")
            lines.append(f"# 总时长: {self._format_timestamp(total_duration)}")
            lines.append(f"# 转写片段数: {len(self.transcripts)}")
            lines.append("")
            lines.append("=" * 60)
            lines.append("")

            for i, transcript in enumerate(self.transcripts, 1):
                speaker_label = self._format_speaker(transcript.speaker)
                start = self._format_timestamp(transcript.start_time)
                end = self._format_timestamp(transcript.end_time)
                lines.append(f"[{start} - {end}] {speaker_label}:")
                lines.append(f"  {transcript.text}")
                lines.append("")

            # 添加 LLM 分析结果
            if analysis_result:
                lines.append("=" * 60)
                lines.append("")
                lines.append("# LLM 分析结果")
                lines.append("")
                if analysis_result.summary:
                    lines.append(f"## 摘要")
                    lines.append(f"{analysis_result.summary}")
                    lines.append("")
                if analysis_result.key_points:
                    lines.append(f"## 关键点")
                    for point in analysis_result.key_points:
                        lines.append(f"- {point}")
                    lines.append("")
                if analysis_result.action_items:
                    lines.append(f"## 行动项")
                    for item in analysis_result.action_items:
                        lines.append(f"- [ ] {item}")
                    lines.append("")
                if analysis_result.topics:
                    lines.append(f"## 主题标签")
                    lines.append(f"、".join(f"`{t}`" for t in analysis_result.topics))
                    lines.append("")

            transcript_text = "\n".join(lines)

            # 保存到文件 (使用 TRANSCRIPTS_DIR)
            transcript_path = config.TRANSCRIPTS_DIR / f"{self.session_id}_transcript.txt"
            transcript_path.write_text(transcript_text, encoding='utf-8')
            logger.info(f"[Session {self.session_id}] Transcript saved to: {transcript_path}")

        except Exception as e:
            logger.error(f"[Session {self.session_id}] Failed to save transcript: {e}")

        finally:
            self._processing = False

    async def _finish_recognition(self) -> None:
        """完成识别流程，处理剩余的音频数据"""
        if not self.asr_adapter:
            return

        try:
            # 提交剩余的音频
            await self.asr_adapter.commit()
            await self.asr_adapter.finish()

            # 等待一段时间让结果返回
            await asyncio.sleep(2)

            # 收集所有剩余的识别结果
            while True:
                result = await asyncio.wait_for(
                    self.asr_adapter.get_result(timeout=0.5),
                    timeout=1.0
                )
                if result is None:
                    break

                # TranscriptionResult 包含 transcript 列表 (TranscriptionSegment)
                # 需要提取每个 segment 并发送
                segments = result.transcript if hasattr(result, 'transcript') else [result]

                for seg in segments:
                    self.transcripts.append(seg)
                    self.seq += 1
                    # 发送转写结果
                    try:
                        await self.websocket.send_json({
                            "type": "transcript",
                            "seq": self.seq,
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
                        logger.warning(f"[Session {self.session_id}] Failed to send transcript: {e}")

        except asyncio.TimeoutError:
            logger.info(f"[Session {self.session_id}] No more results to collect")
        except Exception as e:
            logger.warning(f"[Session {self.session_id}] ASR finish error: {e}")

    async def _audio_generator_final(self):
        """最终音频生成器（用于 stop 后）"""
        for chunk in self.audio_chunks:
            yield chunk

    async def _analyze_meeting(self, audio_path: Path) -> AnalysisResult:
        """分析会议"""
        try:
            result = await self.llm_analyzer.analyze_meeting(
                audio_path,
                self.transcripts
            )
            return result
        except Exception as e:
            logger.error(f"[Session {self.session_id}] LLM analysis error: {e}")
            # 返回默认结果
            return AnalysisResult(
                summary="会议分析暂时不可用。",
                key_points=[],
                action_items=[],
                topics=[]
            )

    async def process_audio(self, audio_data: bytes) -> None:
        """处理音频数据"""
        # 累积音频块用于缓存
        if config.AUDIO_CACHE_ENABLED:
            self.audio_chunks.append(audio_data)
            logger.info(f"[Session {self.session_id}] process_audio: audio_chunks len={len(self.audio_chunks)}, total_bytes={sum(len(c) for c in self.audio_chunks)}")

        await self._audio_queue.put(audio_data)

        # 实时发送音频到 DashScope 进行识别
        if self._running and self.asr_adapter and self.asr_adapter.is_initialized:
            try:
                await self.asr_adapter.append_audio(audio_data)
            except Exception as e:
                logger.warning(f"[Session {self.session_id}] Failed to append audio: {e}")

    async def run_recognition(self) -> None:
        """运行识别循环 - 实时发送识别结果

        使用 VAD 检测 + 定时 commit 相结合的方式
        """
        last_commit_time = 0.0
        commit_interval = 1.0  # 每1秒commit一次获取中间结果
        try:
            while self._running:
                await asyncio.sleep(0.1)  # 100ms 检查一次

                # 定时 commit 检查
                last_commit_time += 0.1
                if last_commit_time >= commit_interval:
                    try:
                        # commit() 会做 VAD 判断，同时也会定期强制 commit
                        result = await self.asr_adapter.commit()
                        if result and result.text:
                            self.seq += 1
                            self.transcripts.append(result)

                            # 发送识别结果到前端
                            await self.websocket.send_json({
                                "type": "transcript",
                                "seq": self.seq,
                                "data": {
                                    "text": result.text,
                                    "start_time": result.start_time,
                                    "end_time": result.end_time,
                                    "speaker": result.speaker,
                                    "confidence": result.confidence,
                                    "is_final": True  # 实时模式下都是最终结果
                                }
                            })
                            logger.info(f"[Session {self.session_id}] Interim transcript: {result.text[:50]}...")

                        last_commit_time = 0
                    except Exception as e:
                        logger.warning(f"[Session {self.session_id}] Commit error: {e}")

        except Exception as e:
            logger.error(f"Recognition error: {e}")
            if not self._processing:
                try:
                    await self.websocket.send_json({
                        "type": "error",
                        "code": "RECOGNITION_ERROR",
                        "message": str(e)
                    })
                except Exception:
                    pass

    async def _single_audio_generator(self, audio_data: bytes):
        """单次音频生成器"""
        yield audio_data

    async def _audio_generator(self):
        """音频数据生成器"""
        while self._running or not self._audio_queue.empty():
            try:
                data = await asyncio.wait_for(
                    self._audio_queue.get(),
                    timeout=1.0
                )
                yield data
            except asyncio.TimeoutError:
                continue

    async def cleanup(self) -> None:
        """清理会话资源"""
        logger.info(f"Cleaning up session {self.session_id}")
        self._running = False
        self._processing = False
        await self.asr_adapter.close()
        await self.llm_analyzer.close()
        self.meeting_extractor.reset()


@router.websocket("/ws/voice")
async def voice_websocket(websocket: WebSocket):
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
    """
    await websocket.accept()
    session: Optional[VoiceSession] = None

    try:
        with RequestContext():
            session = VoiceSession(websocket)
            await session.initialize()
            await session.send_welcome()

            # 消息处理循环
            while True:
                try:
                    data = await websocket.receive()
                    logger.info(f"[Session {session.session_id}] Received data keys: {list(data.keys())}")

                    # 二进制音频数据
                    if "bytes" in data:
                        audio_data = data["bytes"]
                        logger.info(f"[Session {session.session_id}] Received audio frame: {len(audio_data)} bytes")
                        await session.process_audio(audio_data)

                    # 文本控制消息 (FastAPI returns text as data["text"], not data["json"])
                    elif "text" in data:
                        import json
                        msg = json.loads(data["text"])
                        msg_type = msg.get("type")
                        logger.info(f"[Session {session.session_id}] Received text message: type={msg_type}, action={msg.get('action', 'N/A')}, _closed={session._closed}")

                        if msg_type == "control":
                            await session.handle_control(msg)
                        else:
                            logger.warning(f"Unknown message type: {msg_type}")
                except Exception as e:
                    logger.error(f"[Session {session.session_id}] Error in message loop: {e}")
                    break

    except WebSocketDisconnect:
        logger.info("Client disconnected")
        if session:
            session._closed = True

    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        if session and not session._closed:
            try:
                await session.websocket.send_json({
                    "type": "error",
                    "code": "WS_ERROR",
                    "message": str(e)
                })
            except Exception:
                pass

    finally:
        if session:
            session._closed = True
            await session.cleanup()
