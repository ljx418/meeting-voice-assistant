"""
WebSocket 服务器 - 对外暴露的实时识别接口
"""

import asyncio
import json
import logging
from typing import Dict
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from .session import RealtimeSession
from .config import FUNASR_WS_URL, REALTIME_MODE

logger = logging.getLogger("funasr_service.realtime.ws_server")

router = APIRouter()


class RealtimeServer:
    """实时识别 WebSocket 服务器，管理多个客户端会话"""

    def __init__(self):
        self._sessions: Dict[str, RealtimeSession] = {}
        self._ws_url = FUNASR_WS_URL
        self._mode = REALTIME_MODE

    async def handle_connection(self, websocket: WebSocket) -> None:
        """处理 WebSocket 连接"""
        await websocket.accept()
        session_id = None

        try:
            # 等待 start 消息
            msg = await websocket.receive_json()
            logger.info(f"[RealtimeServer] Received message: {msg}")

            if msg.get("type") == "start":
                session_id = msg.get("session_id", "default")
                mode = msg.get("mode", self._mode)

                # 创建会话
                session = RealtimeSession(
                    session_id=session_id,
                    ws_url=self._ws_url,
                    mode=mode
                )
                self._sessions[session_id] = session

                try:
                    await session.start()
                except Exception as e:
                    logger.error(f"[RealtimeServer] Failed to start session: {e}")
                    await websocket.send_json({
                        "type": "error",
                        "message": f"Failed to connect to FunASR service: {str(e)}"
                    })
                    return

                # 发送确认
                await websocket.send_json({
                    "type": "started",
                    "session_id": session_id,
                    "mode": mode
                })
                logger.info(f"[RealtimeServer] Session started: {session_id}")

                # 消息循环
                while True:
                    data = await websocket.receive()

                    # 二进制音频数据
                    if "bytes" in data:
                        await session.send_audio(data["bytes"])

                    # 文本消息
                    elif "text" in data:
                        msg = json.loads(data["text"])
                        if msg.get("type") == "stop":
                            break

        except WebSocketDisconnect:
            logger.info(f"[RealtimeServer] Client disconnected: {session_id}")
        except Exception as e:
            logger.error(f"[RealtimeServer] Error: {e}")
            try:
                await websocket.send_json({
                    "type": "error",
                    "message": str(e)
                })
            except Exception:
                pass
        finally:
            # 清理会话
            if session_id and session_id in self._sessions:
                await self._sessions[session_id].stop()
                del self._sessions[session_id]
                logger.info(f"[RealtimeServer] Session cleaned up: {session_id}")


# 全局服务器实例
realtime_server = RealtimeServer()


@router.websocket("/realtime")
async def realtime_websocket(websocket: WebSocket):
    """
    WebSocket 端点

    前端连接: ws://localhost:8001/ws/realtime

    消息格式:
    - 客户端 -> 服务端: {"type": "start", "session_id": "xxx", "mode": "2pass"}
    - 客户端 -> 服务端: (二进制 PCM 音频数据)
    - 客户端 -> 服务端: {"type": "stop"}
    - 服务端 -> 客户端: {"type": "started", "session_id": "xxx", "mode": "2pass"}
    - 服务端 -> 客户端: {"type": "transcript", "text": "...", "speaker": "speaker_0", ...}
    - 服务端 -> 客户端: {"type": "error", "message": "..."}
    """
    await realtime_server.handle_connection(websocket)
