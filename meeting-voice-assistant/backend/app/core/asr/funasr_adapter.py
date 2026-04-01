"""
FunASR 说话人分离 ASR 适配器

调用本地 FunASR 微服务进行带说话人分离的语音识别

依赖:
    - FunASR 微服务运行在 http://localhost:8001
    - 或设置 FUNASR_ENDPOINT 环境变量

使用方式:
    1. 启动 FunASR 微服务:
       cd backend/funasr_service
       python -m uvicorn main:app --host 0.0.0.0 --port 8001

    2. 设置环境变量:
       export ASR_ENGINE=funasr
       export FUNASR_ENDPOINT=http://localhost:8001

    3. 通过 upload.py 上传音频文件
"""

import asyncio
import logging
from typing import AsyncGenerator, Optional
from pathlib import Path
import aiohttp
import os

from .base import ASRAdapterBase, ASRResult, ASRError, ASRInitError, ASRRecognitionError

logger = logging.getLogger("app.core.asr.funasr")


class FunASRAdapter(ASRAdapterBase):
    """
    FunASR 说话人分离 ASR 适配器

    通过 HTTP 调用 FunASR 微服务，返回带说话人标签的识别结果
    """

    def __init__(
        self,
        endpoint: Optional[str] = None,
        timeout: int = 3600,
    ):
        """
        初始化 FunASR ASR 适配器

        Args:
            endpoint: FunASR 服务地址，默认从环境变量 FUNASR_ENDPOINT 读取
            timeout: 请求超时时间（秒），默认 3600s（1小时）用于大文件处理
        """
        self.endpoint = endpoint or os.getenv("FUNASR_ENDPOINT", "http://localhost:8001")
        self.timeout = timeout
        self.session: Optional[aiohttp.ClientSession] = None

    async def initialize(self) -> None:
        """初始化适配器"""
        self.session = aiohttp.ClientSession()
        logger.info(f"[FunASR] Initialized with endpoint: {self.endpoint}")

    async def close(self) -> None:
        """关闭适配器"""
        if self.session:
            await self.session.close()
            self.session = None
        logger.info("[FunASR] Adapter closed")

    async def recognize_stream(
        self,
        audio_stream: AsyncGenerator[bytes, None],
        sample_rate: int = 16000,
        channels: int = 1,
        sample_width: int = 2
    ) -> AsyncGenerator[ASRResult, None]:
        """
        流式语音识别 - 不支持，请使用 recognize_file
        """
        raise NotImplementedError("FunASR adapter does not support streaming. Use recognize_file() instead.")

    async def recognize_file(self, file_path: Path) -> AsyncGenerator[ASRResult, None]:
        """
        识别音频文件（支持说话人分离）

        Args:
            file_path: 音频文件路径

        Yields:
            ASRResult: 识别结果，包含 speaker 字段
        """
        if not self.session:
            raise ASRError("Adapter not initialized")

        logger.info(f"[FunASR] Recognizing file: {file_path}")

        try:
            # 读取文件
            with open(file_path, "rb") as f:
                file_data = f.read()

            # 构建表单数据
            from io import BytesIO
            from aiohttp import FormData

            form = FormData()
            form.add_field(
                "file",
                BytesIO(file_data),
                filename=file_path.name,
                content_type=self._get_content_type(file_path),
            )

            # 调用 FunASR 微服务
            async with self.session.post(
                f"{self.endpoint}/recognize",
                data=form,
                timeout=aiohttp.ClientTimeout(total=self.timeout),
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"[FunASR] HTTP {response.status}: {error_text}")
                    raise ASRRecognitionError(f"FunASR recognition failed: HTTP {response.status}")

                result = await response.json()

                if not result.get("success"):
                    raise ASRRecognitionError(f"FunASR recognition failed: {result.get('message')}")

                # 解析结果
                sentences = result.get("sentences", [])
                logger.info(f"[FunASR] Received {len(sentences)} sentences")

                for sent in sentences:
                    speaker_id = f"speaker_{sent.get('spk', 0)}"
                    yield ASRResult(
                        text=sent.get("text", ""),
                        start_time=sent.get("start_time", 0.0),
                        end_time=sent.get("end_time", 0.0),
                        speaker=speaker_id,
                        confidence=0.95,  # FunASR 不返回置信度，使用默认值
                        is_final=True,
                    )

        except asyncio.TimeoutError:
            logger.error(f"[FunASR] Request timeout for file: {file_path}")
            raise ASRRecognitionError(f"ASR request timeout (>{self.timeout}s)")
        except aiohttp.ClientError as e:
            logger.error(f"[FunASR] Connection error: {e}")
            raise ASRRecognitionError(f"FunASR connection error: {str(e)}")
        except Exception as e:
            logger.error(f"[FunASR] Recognition error: {e}")
            raise ASRRecognitionError(f"FunASR recognition failed: {str(e)}")

    @property
    def engine_name(self) -> str:
        """返回引擎名称"""
        return f"FunASR (endpoint={self.endpoint})"

    def _get_content_type(self, file_path: Path) -> str:
        """获取文件 MIME 类型"""
        ext = file_path.suffix.lower().lstrip(".")
        mime_map = {
            "wav": "audio/wav",
            "mp3": "audio/mpeg",
            "mp4": "audio/mp4",
            "m4a": "audio/m4a",
            "ogg": "audio/ogg",
            "flac": "audio/flac",
            "webm": "audio/webm",
        }
        return mime_map.get(ext, "audio/wav")
