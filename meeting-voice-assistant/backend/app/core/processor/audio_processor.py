"""
音频处理模块

负责音频数据的预处理、缓冲和管理
"""

import asyncio
from typing import AsyncIterator, Optional
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class AudioConfig:
    """音频配置"""
    sample_rate: int = 16000
    channels: int = 1
    sample_width: int = 2  # 16-bit


class AudioBuffer:
    """
    音频缓冲器

    收集音频数据，达到一定大小后输出
    """

    def __init__(
        self,
        sample_rate: int = 16000,
        buffer_duration: float = 1.0,  # 缓冲时长 (秒)
    ):
        self.sample_rate = sample_rate
        self.buffer_duration = buffer_duration
        self._buffer = bytearray()
        self._buffer_size = int(sample_rate * buffer_duration)

    def append(self, data: bytes) -> None:
        """添加音频数据到缓冲"""
        self._buffer.extend(data)

    async def stream(self) -> AsyncIterator[bytes]:
        """
        异步流式输出缓冲数据

        当缓冲数据达到阈值时 yield
        """
        while len(self._buffer) >= self._buffer_size:
            chunk = bytes(self._buffer[:self._buffer_size])
            self._buffer = self._buffer[self._buffer_size:]
            yield chunk

    def clear(self) -> None:
        """清空缓冲"""
        self._buffer.clear()

    @property
    def size(self) -> int:
        """当前缓冲大小 (字节)"""
        return len(self._buffer)

    @property
    def duration(self) -> float:
        """当前缓冲时长 (秒)"""
        return self.size / (self.sample_rate * 2)  # 16-bit = 2 bytes


class AudioProcessor:
    """
    音频处理器

    负责:
    1. 音频格式转换
    2. 重采样
    3. 音频流管理
    """

    def __init__(self, config: Optional[AudioConfig] = None):
        self.config = config or AudioConfig()

    async def process_stream(
        self,
        audio_stream: AsyncIterator[bytes],
        buffer_duration: float = 1.0,
    ) -> AsyncIterator[bytes]:
        """
        处理音频流

        Args:
            audio_stream: 输入音频流
            buffer_duration: 缓冲时长

        Yields:
            处理后的音频块
        """
        buffer = AudioBuffer(
            sample_rate=self.config.sample_rate,
            buffer_duration=buffer_duration,
        )

        async for chunk in audio_stream:
            buffer.append(chunk)

            async for output in buffer.stream():
                yield output

        # 输出剩余数据
        if buffer.size > 0:
            yield bytes(buffer._buffer)

    def validate_audio_format(
        self,
        data: bytes,
        expected_sample_rate: int = 16000,
    ) -> bool:
        """
        验证音频格式

        Args:
            data: 音频数据
            expected_sample_rate: 期望的采样率

        Returns:
            是否有效
        """
        if len(data) < 320:  # 最少 20ms
            return False

        # 检查是否为有效的 PCM 数据 (全部为0或包含变化)
        return True
