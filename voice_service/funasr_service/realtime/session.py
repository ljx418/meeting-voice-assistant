"""
会话管理
"""

import asyncio
import logging
from typing import Optional

from .ws_client import FunAsrWsClient
from .protocol import TranscriptMessage

logger = logging.getLogger("funasr_service.realtime.session")


class RealtimeSession:
    """管理单个实时识别会话"""

    def __init__(self, session_id: str, ws_url: str, mode: str = "2pass"):
        self.session_id = session_id
        self.ws_url = ws_url
        self.mode = mode
        self.funasr_client: Optional[FunAsrWsClient] = None
        self._result_queue: asyncio.Queue = asyncio.Queue()
        self._running = False

    async def start(self) -> None:
        """启动会话"""
        self.funasr_client = FunAsrWsClient(
            ws_url=self.ws_url,
            mode=self.mode,
            result_callback=self._on_result
        )
        await self.funasr_client.connect()
        self._running = True
        logger.info(f"[RealtimeSession] Started: session_id={self.session_id}, mode={self.mode}")

    async def stop(self) -> None:
        """停止会话"""
        self._running = False
        if self.funasr_client:
            await self.funasr_client.close()
        logger.info(f"[RealtimeSession] Stopped: session_id={self.session_id}")

    async def send_audio(self, audio_data: bytes) -> None:
        """发送音频数据"""
        if self.funasr_client and self._running:
            await self.funasr_client.send_audio(audio_data)

    def _on_result(self, result: dict) -> None:
        """FunASR 结果回调"""
        transcript = TranscriptMessage(
            session_id=self.session_id,
            text=result.get("text", ""),
            speaker=result.get("speaker", "speaker_0"),
            start_time=result.get("start_time", 0.0),
            end_time=result.get("end_time", 0.0),
            mode=result.get("mode")
        )
        # 将结果放入队列
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.create_task(self._result_queue.put(transcript))
            else:
                loop.run_until_complete(self._result_queue.put(transcript))
        except Exception as e:
            logger.error(f"[RealtimeSession] Failed to queue result: {e}")

    async def get_result(self, timeout: float = 1.0) -> Optional[TranscriptMessage]:
        """获取识别结果"""
        try:
            return await asyncio.wait_for(
                self._result_queue.get(),
                timeout=timeout
            )
        except asyncio.TimeoutError:
            return None
