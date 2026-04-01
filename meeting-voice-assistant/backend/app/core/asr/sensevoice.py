"""
SenseVoice ASR 适配器实现

参考: https://github.com/alibaba-damo-academy/SenseVoice

设计要点:
1. 支持本地部署 (Docker/ONNX)
2. 支持云端 API 调用
3. 流式识别接口
4. 说话人分离内置支持
"""

import asyncio
import struct
from typing import AsyncIterator, Optional
import logging
from dataclasses import dataclass

from .base import ASRAdapterBase, ASRResult, ASRInitError, ASRRecognitionError

logger = logging.getLogger(__name__)


@dataclass
class SenseVoiceConfig:
    """SenseVoice 配置"""
    mode: str = "local"  # "local" or "api"
    endpoint: str = "http://localhost:8000"
    api_key: Optional[str] = None
    timeout: float = 30.0
    buffer_size: int = 16000  # 1秒音频缓冲


class SenseVoiceAdapter(ASRAdapterBase):
    """
    SenseVoice ASR 适配器

    支持两种部署模式:
    1. local: 本地 ONNX 推理 (docker-compose 部署)
    2. api: 云端 API 调用
    """

    def __init__(
        self,
        mode: str = "local",
        endpoint: str = "http://localhost:8000",
        api_key: Optional[str] = None,
        timeout: float = 30.0,
    ):
        super().__init__()
        self.config = SenseVoiceConfig(
            mode=mode,
            endpoint=endpoint,
            api_key=api_key,
            timeout=timeout,
        )
        self._client = None
        self._buffer = bytearray()
        self._session_id: Optional[str] = None

    async def initialize(self) -> None:
        """
        初始化 SenseVoice 适配器

        根据 mode 初始化本地服务连接或云端 API 客户端
        """
        logger.info(f"Initializing SenseVoice adapter in {self.config.mode} mode")

        try:
            if self.config.mode == "local":
                await self._init_local()
            elif self.config.mode == "api":
                await self._init_api()
            else:
                raise ASRInitError(f"Unknown mode: {self.config.mode}")

            self._initialized = True
            logger.info(f"SenseVoice adapter initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize SenseVoice adapter: {e}")
            raise ASRInitError(f"SenseVoice initialization failed: {e}")

    async def _init_local(self) -> None:
        """初始化本地模式 - 验证本地服务可用性"""
        import aiohttp

        try:
            async with aiohttp.ClientSession() as session:
                # 构建正确的健康检查 URL
                health_url = f"{self.config.endpoint}/api/v1/health"
                async with session.get(
                    health_url,
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as resp:
                    if resp.status != 200:
                        raise ASRInitError(f"Local service unhealthy: {resp.status}")
                    logger.debug("Local SenseVoice service is healthy")
        except aiohttp.ClientError as e:
            logger.warning(f"Cannot connect to local SenseVoice service: {e}")
            logger.warning("Please ensure SenseVoice local service is running")
            # 不抛出错误，允许后续重试

    async def _init_api(self) -> None:
        """初始化 API 模式 - 配置云端 API"""
        if not self.config.api_key:
            raise ASRInitError("API key is required for cloud mode")
        logger.info("API mode initialized with key")

    async def recognize_stream(
        self,
        audio_stream: AsyncIterator[bytes],
        sample_rate: int = 16000,
        channels: int = 1,
        sample_width: int = 2,
    ) -> AsyncIterator[ASRResult]:
        """
        流式识别实现

        音频格式要求:
        - 采样率: 16000 Hz
        - 声道: 单声道 (mono)
        - 位深: 16-bit PCM
        - 编码: linear PCM

        Args:
            audio_stream: 音频数据流
            sample_rate: 采样率
            channels: 声道数
            sample_width: 采样位深

        Yields:
            ASRResult: 识别结果片段
        """
        if not self._initialized:
            await self.initialize()

        logger.debug("Starting stream recognition")

        try:
            async for audio_chunk in audio_stream:
                result = await self._process_chunk(
                    audio_chunk,
                    sample_rate,
                    channels,
                    sample_width
                )
                if result:
                    logger.debug(f"Recognized: {result.text[:50]}...")
                    yield result

        except Exception as e:
            logger.error(f"Stream recognition error: {e}")
            raise ASRRecognitionError(f"Recognition failed: {e}")

    async def _process_chunk(
        self,
        chunk: bytes,
        sample_rate: int,
        channels: int,
        sample_width: int,
    ) -> Optional[ASRResult]:
        """
        处理单个音频块

        Args:
            chunk: 原始音频字节
            sample_rate: 采样率
            channels: 声道数
            sample_width: 位深

        Returns:
            ASRResult 或 None (如果识别失败或等待更多数据)
        """
        # 将数据加入缓冲
        self._buffer.extend(chunk)

        # 等待足够的音频数据 (至少 0.5 秒)
        min_buffer_size = int(sample_rate * channels * sample_width * 0.5)
        if len(self._buffer) < min_buffer_size:
            return None

        # 如果是模拟模式 (无实际 ASR 服务)，返回模拟结果
        if self.config.mode == "local":
            return await self._process_local()
        else:
            return await self._process_api()

    async def _process_local(self) -> Optional[ASRResult]:
        """
        本地模式处理

        调用本地 ONNX Runtime 或 HTTP API
        TODO: 集成实际 SenseVoice 本地推理
        """
        # 模拟识别结果 (实际部署时替换为真实调用)
        # import time
        # 调用本地服务...
        return None

    async def _process_api(self) -> Optional[ASRResult]:
        """API 模式处理 - 调用云端 API"""
        # TODO: 实现云端 API 调用
        return None

    async def close(self) -> None:
        """关闭连接并释放资源"""
        logger.info("Closing SenseVoice adapter")
        self._buffer.clear()
        self._session_id = None
        self._initialized = False

    @property
    def engine_name(self) -> str:
        return "SenseVoice"

    @property
    def mode(self) -> str:
        return self.config.mode
