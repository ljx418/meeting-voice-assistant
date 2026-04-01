"""
音频分块缓冲管理

负责累积音频数据，并在适当的时机切分音频块
"""

import asyncio
import logging
from typing import Optional, Tuple
from .vad import VAD
from . import config

logger = logging.getLogger("app.core.realtime_spk.chunk_buffer")


class ChunkBuffer:
    """
    音频分块缓冲器

    累积音频数据，当达到以下条件之一时触发提交：
    1. 累积时长达到 max_buffer_duration（最大缓冲时长）
    2. VAD 检测到静音且累积时长达到 min_chunk_duration
    """

    def __init__(
        self,
        sample_rate: int = None,
        chunk_duration: float = None,
        min_chunk_duration: float = None,
        max_buffer_duration: float = None,
    ):
        """
        初始化缓冲器

        Args:
            sample_rate: 采样率 (Hz)
            chunk_duration: 每块目标时长 (秒)
            min_chunk_duration: 最小音频块时长 (秒)，小于此时长的块会被跳过
            max_buffer_duration: 最大缓冲时长 (秒)，超过此时长强制提交
        """
        self.sample_rate = sample_rate or config.SAMPLE_RATE
        self.chunk_duration = chunk_duration or config.CHUNK_DURATION
        self.min_chunk_duration = min_chunk_duration or config.MIN_CHUNK_DURATION
        self.max_buffer_duration = max_buffer_duration or config.MAX_BUFFER_DURATION

        self._buffer = bytearray()
        self._vad = VAD(self.sample_rate)
        self._cumulative_time = 0.0  # 累积时间（从会话开始）
        self._buffer_start_time = 0.0  # 当前缓冲块的开始时间
        self._lock = asyncio.Lock()

        # 计算相关参数
        self._min_bytes = int(self.sample_rate * 2 * self.min_chunk_duration)
        self._max_bytes = int(self.sample_rate * 2 * self.max_buffer_duration)
        self._target_bytes = int(self.sample_rate * 2 * self.chunk_duration)

    def append(self, audio_data: bytes) -> None:
        """
        添加音频数据到缓冲区

        Args:
            audio_data: PCM 音频数据
        """
        self._buffer.extend(audio_data)

    def get_buffer_duration(self) -> float:
        """获取当前缓冲区的音频时长（秒）"""
        return len(self._buffer) / (self.sample_rate * 2)

    def should_commit(self) -> bool:
        """
        判断是否应该提交缓冲区

        Returns:
            True if should commit, False otherwise
        """
        buffer_size = len(self._buffer)

        # 如果缓冲区太小，不提交
        if buffer_size < self._min_bytes:
            return False

        # 达到最大缓冲时长，强制提交
        if buffer_size >= self._max_bytes:
            logger.info(f"[ChunkBuffer] Max buffer duration reached: {self.get_buffer_duration():.1f}s")
            return True

        # VAD 检测到静音
        if self._vad.update_state(bytes(self._buffer)):
            logger.info(f"[ChunkBuffer] VAD silence detected, buffer duration: {self.get_buffer_duration():.1f}s")
            return True

        return False

    def get_and_clear(self) -> Optional[Tuple[bytes, float, float]]:
        """
        获取缓冲区内容并清空

        Returns:
            (audio_data, start_time, end_time) 或 None（如果缓冲区为空）
        """
        if not self._buffer:
            return None

        audio_data = bytes(self._buffer)
        start_time = self._buffer_start_time
        end_time = start_time + len(audio_data) / (self.sample_rate * 2)

        # 清空缓冲区
        self._buffer.clear()

        # 更新累积时间
        self._cumulative_time = end_time

        # 更新缓冲块开始时间，为下一个音频块准备
        self._buffer_start_time = self._cumulative_time

        return audio_data, start_time, end_time

    def reset(self) -> None:
        """重置缓冲器和 VAD 状态"""
        self._buffer.clear()
        self._cumulative_time = 0.0
        self._buffer_start_time = 0.0
        self._vad.reset()

    def update_start_time(self, start_time: float) -> None:
        """更新当前缓冲块的开始时间"""
        self._buffer_start_time = start_time

    @property
    def cumulative_time(self) -> float:
        """获取累积时间"""
        return self._cumulative_time
