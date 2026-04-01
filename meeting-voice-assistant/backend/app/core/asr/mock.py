"""
Mock ASR 适配器 - 用于测试

在未接入真实 ASR 服务前，使用 Mock 适配器模拟识别结果。
当获取到阿里云 AccessKey 后，可切换到 aliyun 适配器。

使用方式:
    export ASR_ENGINE=mock
"""

import asyncio
from typing import AsyncIterator, Optional
from pathlib import Path
import logging

from .base import ASRAdapterBase, ASRResult

logger = logging.getLogger(__name__)


class MockASRAdapter(ASRAdapterBase):
    """
    Mock ASR 适配器 - 用于测试完整流程

    模拟特点:
    - 流式返回模拟识别结果
    - 模拟真实 ASR 的延迟
    - 返回包含说话人、时间戳等信息
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
        delay: float = 0.8,  # 每个结果之间的延迟(秒)
        text_index: int = 0,  # 起始文本索引
    ):
        super().__init__()
        self.delay = delay
        self.text_index = text_index
        self._is_running = False
        self._current_index = text_index

    async def initialize(self) -> None:
        """初始化 Mock ASR"""
        logger.info("[Mock ASR] Initializing Mock ASR adapter")
        self._initialized = True
        logger.info("[Mock ASR] Mock ASR adapter initialized successfully")

    async def recognize_stream(
        self,
        audio_stream: AsyncIterator[bytes],
        sample_rate: int = 16000,
        channels: int = 1,
        sample_width: int = 2,
    ) -> AsyncIterator[ASRResult]:
        """
        模拟流式识别

        监听音频流，当收到足够的音频数据时，生成模拟识别结果。
        实际使用时不关注音频内容，只是模拟识别流程。

        Args:
            audio_stream: 音频数据流
            sample_rate: 采样率
            channels: 声道数
            sample_width: 采样位深

        Yields:
            ASRResult: 模拟识别结果
        """
        if not self._initialized:
            await self.initialize()

        logger.info("[Mock ASR] Starting mock stream recognition")
        self._is_running = True
        self._current_index = self.text_index

        # 监听音频流，模拟处理
        audio_chunks_received = 0

        async for audio_chunk in audio_stream:
            audio_chunks_received += 1

            # 每收到 5 个音频块，生成一个识别结果
            if audio_chunks_received % 5 == 0:
                if self._current_index >= len(self.SAMPLE_TEXTS):
                    # 循环使用模拟文本
                    self._current_index = 0

                text = self.SAMPLE_TEXTS[self._current_index]
                start_time = self._current_index * 3.0
                end_time = start_time + 2.5

                result = ASRResult(
                    text=text,
                    start_time=start_time,
                    end_time=end_time,
                    speaker=f"speaker_{(self._current_index % 2) + 1}",
                    confidence=0.92 + (self._current_index % 8) * 0.01,
                )

                logger.debug(f"[Mock ASR] Yielding result: {text[:20]}...")
                self._current_index += 1

                yield result

                # 模拟 ASR 处理延迟
                await asyncio.sleep(self.delay)

            # 检查是否停止
            if not self._is_running:
                break

    async def close(self) -> None:
        """关闭 Mock ASR"""
        logger.info("[Mock ASR] Closing Mock ASR adapter")
        self._is_running = False
        self._initialized = False

    async def recognize_file(self, file_path: Path) -> AsyncIterator[ASRResult]:
        """
        识别音频文件 - Mock 版本

        Args:
            file_path: 音频文件路径

        Yields:
            ASRResult: 模拟识别结果
        """
        if not self._initialized:
            await self.initialize()

        logger.info(f"[Mock ASR] Processing file: {file_path}")

        # 模拟文件处理延迟
        await asyncio.sleep(0.5)

        # 返回所有模拟文本
        for i, text in enumerate(self.SAMPLE_TEXTS):
            result = ASRResult(
                text=text,
                start_time=i * 3.0,
                end_time=i * 3.0 + 2.5,
                speaker=f"speaker_{(i % 2) + 1}",
                confidence=0.92 + (i % 8) * 0.01,
            )
            yield result
            await asyncio.sleep(0.1)

    @property
    def engine_name(self) -> str:
        return "Mock ASR"

    @property
    def mode(self) -> str:
        return "mock"
