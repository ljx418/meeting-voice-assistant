"""
FunASR 流式调用客户端

定期调用 FunASR /recognize 接口进行带说话人分离的语音识别
"""

import asyncio
import logging
from typing import List, Optional
from io import BytesIO
import aiohttp

from ..asr.base import ASRResult
from . import config

logger = logging.getLogger("app.core.realtime_spk.funasr_streamer")


class FunASRStreamer:
    """
    FunASR 流式调用客户端

    将累积的音频块定期提交给 FunASR 服务进行识别
    """

    def __init__(
        self,
        endpoint: str = None,
        timeout: int = None,
    ):
        """
        初始化 FunASR 流式客户端

        Args:
            endpoint: FunASR 服务地址
            timeout: 请求超时时间（秒）
        """
        self.endpoint = endpoint or config.FUNASR_ENDPOINT
        self.timeout = timeout or config.FUNASR_TIMEOUT
        self._session: Optional[aiohttp.ClientSession] = None

    async def initialize(self) -> None:
        """初始化 HTTP session"""
        if self._session is None:
            self._session = aiohttp.ClientSession()
            logger.info(f"[FunASRStreamer] Initialized with endpoint: {self.endpoint}")

    async def close(self) -> None:
        """关闭 HTTP session"""
        if self._session:
            await self._session.close()
            self._session = None
            logger.info("[FunASRStreamer] Session closed")

    def _pcm_to_wav(self, pcm_data: bytes, sample_rate: int = 16000, channels: int = 1, sample_width: int = 2) -> bytes:
        """
        将 PCM 数据转换为 WAV 格式

        Args:
            pcm_data: PCM 音频数据
            sample_rate: 采样率
            channels: 声道数
            sample_width: 采样宽度（字节）

        Returns:
            WAV 格式的音频数据
        """
        import struct
        import wave

        buffer = BytesIO()
        with wave.open(buffer, 'wb') as wav_file:
            wav_file.setnchannels(channels)
            wav_file.setsampwidth(sample_width)
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(pcm_data)

        return buffer.getvalue()

    async def recognize_chunk(
        self,
        audio_data: bytes,
        start_time: float,
        end_time: float,
    ) -> List[ASRResult]:
        """
        识别一个音频块

        Args:
            audio_data: PCM 音频数据
            start_time: 音频开始时间（秒，相对于会话开始）
            end_time: 音频结束时间（秒，相对于会话开始）

        Returns:
            ASRResult 列表，每个句子一个结果
        """
        if not self._session:
            raise RuntimeError("FunASRStreamer not initialized. Call initialize() first.")

        if not audio_data:
            return []

        try:
            # 将 PCM 转换为 WAV
            wav_data = self._pcm_to_wav(audio_data, self._session is not None and True or True)

            # 构建表单数据
            form = aiohttp.FormData()
            form.add_field(
                "file",
                BytesIO(wav_data),
                filename="audio.wav",
                content_type="audio/wav",
            )

            # 调用 FunASR 微服务
            logger.info(f"[FunASRStreamer] Recognizing chunk: {len(audio_data)} bytes, time=[{start_time:.1f}s, {end_time:.1f}s]")

            async with self._session.post(
                f"{self.endpoint}/recognize",
                data=form,
                timeout=aiohttp.ClientTimeout(total=self.timeout),
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"[FunASRStreamer] HTTP {response.status}: {error_text}")
                    return []

                result = await response.json()

                if not result.get("success"):
                    logger.error(f"[FunASRStreamer] Recognition failed: {result.get('message')}")
                    return []

                # 解析结果
                sentences = result.get("sentences", [])
                logger.info(f"[FunASRStreamer] Received {len(sentences)} sentences")

                results = []
                for sent in sentences:
                    speaker_id = f"speaker_{sent.get('spk', 0)}"
                    # FunASR 返回的时间是相对于本段音频的，需要转换为相对于会话开始
                    sent_start = sent.get("start_time", 0.0)
                    sent_end = sent.get("end_time", 0.0)

                    results.append(ASRResult(
                        text=sent.get("text", ""),
                        start_time=start_time + sent_start,
                        end_time=start_time + sent_end,
                        speaker=speaker_id,
                        confidence=0.95,
                        is_final=True,
                    ))

                return results

        except asyncio.TimeoutError:
            logger.error(f"[FunASRStreamer] Request timeout")
            return []
        except aiohttp.ClientError as e:
            logger.error(f"[FunASRStreamer] Connection error: {e}")
            return []
        except Exception as e:
            logger.error(f"[FunASRStreamer] Recognition error: {e}")
            return []
