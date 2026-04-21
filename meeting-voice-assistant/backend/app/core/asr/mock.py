"""
Mock ASR 适配器 - 用于测试

在未接入真实 ASR 服务前，使用 Mock 适配器模拟识别结果。
当获取到阿里云 AccessKey 后，可切换到 aliyun 适配器。

使用方式:
    export ASR_ENGINE=mock
"""

import asyncio
import inspect
from typing import AsyncIterator, Optional
from pathlib import Path
import logging

from .base import BaseTranscriber, TranscriptionSegment, TranscriptionResult, ASRResult

logger = logging.getLogger(__name__)


class MockASRAdapter(BaseTranscriber):
    """
    Mock ASR 适配器 - 用于测试完整流程

    模拟特点:
    - 流式返回模拟识别结果
    - 模拟真实 ASR 的延迟
    - 返回包含说话人、时间戳等信息

    实现统一接口 BaseTranscriber，同时保留旧接口兼容性
    """

    # 模拟会议文本
    SAMPLE_TEXTS = [
        "大家好，欢迎参加今天的会议。",
        "今天我们主要讨论项目进度和下个季度的计划。",
        "首先，请张三介绍一下上个季度的工作成果。",
        "好的，那我来说一下。上个季度我们完成了核心功能的开发。",
        "具体来说，我们完成了用户管理模块和数据分析模块。",
        "这些模块目前已经开始在测试环境运行。",
        "那么下个季度有什么计划呢？",
        "下个季度我们计划完成移动端适配和性能优化。",
        "另外，我们还会加强安全方面的防护。",
        "好的，关于这些计划有没有什么问题？",
        "我有一个问题，关于移动端适配的时间安排。",
        "移动端适配预计需要两周时间。",
        "好的，那没有问题，今天的会议就到这里。",
        "谢谢大家，下次会议再见。",
    ]

    def __init__(
        self,
        session_id: str = "mock",
        delay: float = 0.8,  # 每个结果之间的延迟(秒)
        text_index: int = 0,  # 起始文本索引
    ):
        super().__init__(session_id)
        self.delay = delay
        self.text_index = text_index
        self._current_index = text_index
        self._results_buffer = []  # 用于存储待 yield 的结果
        self._audio_buffer = bytearray()

    async def start(self) -> None:
        """开始转写"""
        logger.info("[Mock ASR] Starting Mock ASR adapter")
        self._running = True
        self._current_index = self.text_index
        self._results_buffer = []
        self._audio_buffer = bytearray()
        logger.info("[Mock ASR] Mock ASR adapter started")

    async def process_audio(self, audio_data: bytes) -> None:
        """处理音频数据"""
        self.add_audio_chunk(audio_data)
        self._audio_buffer.extend(audio_data)

        # 每收到足够的音频块，生成一个识别结果
        if len(self._audio_buffer) >= 16000 * 2:  # 1 second of audio
            await self._generate_result()

    async def _generate_result(self) -> None:
        """生成识别结果"""
        if self._current_index >= len(self.SAMPLE_TEXTS):
            self._current_index = 0

        text = self.SAMPLE_TEXTS[self._current_index]
        start_time = self._current_index * 3.0
        end_time = start_time + 2.5

        segment = self.create_segment(
            text=text,
            start_time=start_time,
            end_time=end_time,
            speaker=f"speaker_{(self._current_index % 2) + 1}",
            confidence=0.92 + (self._current_index % 8) * 0.01,
            is_final=True
        )

        self._segments.append(segment)
        self._results_buffer.append(segment)
        self._current_index += 1

        # 清理缓冲区
        self._audio_buffer.clear()

        logger.debug(f"[Mock ASR] Generated result: {text[:20]}...")

        # 模拟 ASR 处理延迟
        await asyncio.sleep(self.delay)

    async def commit(self) -> Optional[TranscriptionSegment]:
        """提交缓冲区音频进行识别"""
        if self._results_buffer:
            return self._results_buffer.pop(0)
        return None

    async def get_result(self) -> Optional[TranscriptionResult]:
        """获取转写结果"""
        if self._results_buffer:
            segment = self._results_buffer.pop(0)
            return TranscriptionResult(
                session_id=self.session_id,
                transcript=[segment],
                duration=segment.end_time - segment.start_time
            )
        return None

    async def stop(self) -> TranscriptionResult:
        """停止转写并返回最终结果"""
        self._running = False
        self._results_buffer.clear()
        self._audio_buffer.clear()
        logger.info("[Mock ASR] Stopped")
        return self.build_result()

    async def finish(self) -> None:
        """结束会话"""
        self._running = False
        self._audio_buffer.clear()
        logger.info("[Mock ASR] Session finished")

    # 旧接口兼容
    async def initialize(self) -> None:
        """初始化 (兼容旧接口)"""
        await self.start()

    async def connect(self) -> None:
        """连接 (兼容旧接口)"""
        await self.start()

    async def close(self) -> None:
        """关闭 (兼容旧接口)"""
        await self.stop()

    async def append_audio(self, audio_data: bytes) -> None:
        """添加音频 (兼容旧接口)"""
        await self.process_audio(audio_data)

    async def recognize_file(self, file_path: Path):
        """
        识别音频文件（用于文件上传测试）

        Args:
            file_path: 音频文件路径

        Yields:
            ASRResult: 识别结果
        """
        logger.info(f"[Mock ASR] Recognizing file: {file_path}")

        # 获取文件大小
        file_size = file_path.stat().st_size if file_path.exists() else 0
        logger.info(f"[Mock ASR] File size: {file_size} bytes")

        # 模拟处理延迟
        await asyncio.sleep(self.delay)

        # 返回模拟结果
        for i, text in enumerate(self.SAMPLE_TEXTS):
            yield ASRResult(
                text=text,
                start_time=i * 3.0,
                end_time=i * 3.0 + 2.5,
                speaker=f"speaker_{(i % 2) + 1}",
                confidence=0.92 + (i % 8) * 0.01,
                is_final=True
            )

    @property
    def engine_name(self) -> str:
        return "Mock ASR"

    @property
    def mode(self) -> str:
        return "mock"
