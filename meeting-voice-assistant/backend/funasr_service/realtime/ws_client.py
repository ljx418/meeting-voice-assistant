"""
FunASR WebSocket 客户端
"""

import asyncio
import json
import base64
import logging
from typing import Callable, Optional
import websockets

from .config import FUNASR_WS_URL, CHUNK_SIZE, USE_ITN

logger = logging.getLogger("funasr_service.realtime.ws_client")


class FunAsrWsClient:
    """FunASR WebSocket 客户端，连接到 FunASR 实时识别服务"""

    def __init__(
        self,
        ws_url: str = FUNASR_WS_URL,
        mode: str = "2pass",
        result_callback: Callable[[dict], None] = None
    ):
        self.ws_url = ws_url
        self.mode = mode
        self.result_callback = result_callback
        self._ws: Optional[websockets.WebSocketClientProtocol] = None
        self._running = False
        self._receive_task: Optional[asyncio.Task] = None

    async def connect(self) -> None:
        """连接 FunASR 服务"""
        try:
            self._ws = await websockets.connect(self.ws_url)
            self._running = True

            # 发送开始信号
            start_msg = {
                "mode": self.mode,
                "wav_name": "realtime_audio",
                "is_speaking": True,
                "wav_format": "pcm",
                "chunk_size": CHUNK_SIZE,
                "audio_fs": 16000,
                "itn": USE_ITN
            }
            await self._ws.send(json.dumps(start_msg))
            logger.info(f"[FunAsrWsClient] Connected to {self.ws_url}, mode={self.mode}")

            # 启动接收任务
            self._receive_task = asyncio.create_task(self._receive_loop())

        except Exception as e:
            logger.error(f"[FunAsrWsClient] Failed to connect: {e}")
            self._running = False
            raise

    async def close(self) -> None:
        """关闭连接"""
        self._running = False

        if self._ws:
            try:
                # 发送结束信号
                await self._ws.send(json.dumps({"is_speaking": False}))
                await self._ws.close()
            except Exception as e:
                logger.warning(f"[FunAsrWsClient] Error closing websocket: {e}")

        if self._receive_task:
            self._receive_task.cancel()
            try:
                await self._receive_task
            except asyncio.CancelledError:
                pass

        logger.info("[FunAsrWsClient] Connection closed")

    async def send_audio(self, audio_data: bytes) -> None:
        """发送音频数据"""
        if self._ws and self._running:
            try:
                # FunASR 需要 base64 编码的 PCM
                audio_b64 = base64.b64encode(audio_data).decode('utf-8')
                await self._ws.send(json.dumps({
                    "audio_data": audio_b64,
                    "is_speaking": True
                }))
            except Exception as e:
                logger.error(f"[FunAsrWsClient] Failed to send audio: {e}")

    async def _receive_loop(self) -> None:
        """接收识别结果"""
        try:
            async for message in self._ws:
                if not self._running:
                    break

                try:
                    data = json.loads(message)

                    # 解析 FunASR 返回的结果
                    if data.get("text"):
                        result = {
                            "text": data.get("text", ""),
                            "start_time": 0.0,
                            "end_time": 0.0,
                            "speaker": f"speaker_{data.get('spk', 0)}",
                            "mode": data.get("mode")
                        }

                        # FunASR 2pass 模式会返回时间戳
                        if "start_time" in data:
                            result["start_time"] = data.get("start_time", 0.0)
                        if "end_time" in data:
                            result["end_time"] = data.get("end_time", 0.0)

                        if self.result_callback:
                            self.result_callback(result)

                except json.JSONDecodeError as e:
                    logger.warning(f"[FunAsrWsClient] JSON decode error: {e}")

        except asyncio.CancelledError:
            logger.info("[FunAsrWsClient] Receive loop cancelled")
        except Exception as e:
            logger.error(f"[FunAsrWsClient] Receive error: {e}")
            self._running = False
