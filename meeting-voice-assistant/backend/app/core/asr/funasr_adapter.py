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
import time
from typing import AsyncGenerator, Optional
from pathlib import Path
import aiohttp

from .base import ASRAdapterBase, ASRResult, ASRError, ASRInitError, ASRRecognitionError, TranscriptionResult
from app.config import config

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
        max_file_size_mb: Optional[int] = None,
        session_id: str = "funasr",
    ):
        """
        初始化 FunASR ASR 适配器

        Args:
            endpoint: FunASR 服务地址，默认从 config.asr.funasr_endpoint 读取
            timeout: 请求超时时间（秒），默认 3600s（1小时）用于大文件处理
            max_file_size_mb: 文件大小限制 (MB)，默认从 config.asr.funasr_max_file_size_mb 读取
            session_id: 会话 ID（用于 BaseTranscriber 兼容性）
        """
        super().__init__(session_id)  # 调用 ASRAdapterBase.__init__
        self.endpoint = endpoint or config.asr.funasr_endpoint
        self.timeout = timeout
        self.max_file_size_mb = max_file_size_mb or config.asr.funasr_max_file_size_mb
        self.session: Optional[aiohttp.ClientSession] = None
        self._running = False

    # ========== BaseTranscriber 抽象方法实现 ==========

    async def start(self) -> None:
        """开始转写 (BaseTranscriber 接口)"""
        if not self.session:
            self.session = aiohttp.ClientSession()
        self._running = True
        logger.info(f"[FunASR] Started with endpoint: {self.endpoint}")

    async def stop(self) -> "TranscriptionResult":
        """停止转写 (BaseTranscriber 接口)"""
        self._running = False
        if self.session:
            await self.session.close()
            self.session = None
        logger.info("[FunASR] Stopped")
        return self.build_result()

    async def process_audio(self, audio_data: bytes) -> None:
        """
        处理音频数据 (BaseTranscriber 接口)
        FunASR 适配器不支持流式处理，此方法为空操作
        """
        # FunASR 适配器为文件识别设计，不支持流式处理
        # 音频数据会被忽略，使用 recognize_file() 进行文件识别
        pass

    async def get_result(self) -> Optional["TranscriptionResult"]:
        """
        获取转写结果 (BaseTranscriber 接口)
        FunASR 适配器使用 recognize_file()，此方法返回 None
        """
        # 文件识别模式，结果通过 recognize_file 的 yield 返回
        return None

    # ========== ASRAdapterBase 方法实现 ==========

    async def initialize(self) -> None:
        """初始化适配器"""
        await self.start()

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

        Raises:
            ASRRecognitionError: 识别失败时抛出
        """
        if not self.session:
            raise ASRError("Adapter not initialized")

        start_time = time.time()
        logger.info(f"[FunASR] Recognizing file: {file_path}")

        # 安全检查: 文件大小限制，防止 OOM
        max_file_size = self.max_file_size_mb * 1024 * 1024
        file_size = file_path.stat().st_size
        if file_size > max_file_size:
            raise ASRRecognitionError(f"File too large: {file_size / (1024*1024):.1f}MB. Maximum allowed is {self.max_file_size_mb}MB.")

        try:
            # 构建表单数据（使用流式上传，避免将整个文件加载到内存）
            from aiohttp import FormData

            form = FormData()
            # 使用 with 语句确保文件句柄正确关闭
            with open(file_path, "rb") as file_handle:
                form.add_field(
                    "file",
                    file_handle,
                    filename=file_path.name,
                    content_type=self._get_content_type(file_path),
                )

                logger.info(f"[FunASR] Sending request to {self.endpoint}/recognize (file_size={file_size / (1024*1024):.1f}MB)")

                # 调用 FunASR 微服务
                request_start = time.time()
                async with self.session.post(
                    f"{self.endpoint}/recognize",
                    data=form,
                    timeout=aiohttp.ClientTimeout(total=self.timeout),
                ) as response:
                    request_elapsed = time.time() - request_start
                    logger.info(f"[FunASR] Received response in {request_elapsed:.2f}s, status={response.status}")
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"[FunASR] HTTP {response.status}: {error_text}")
                        raise ASRRecognitionError(f"FunASR recognition failed: HTTP {response.status}")

                    result = await response.json()

                    if not result.get("success"):
                        raise ASRRecognitionError(f"FunASR recognition failed: {result.get('message')}")

                    # 解析结果
                    sentences = result.get("sentences", [])
                    total_elapsed = time.time() - start_time
                    logger.info(f"[FunASR] Received {len(sentences)} sentences in {total_elapsed:.2f}s")

                    for idx, sent in enumerate(sentences):
                        if idx == 0 or idx == len(sentences) - 1:
                            logger.info(f"[FunASR] Sentence[{idx}]: speaker={sent.get('spk', 0)}, start={sent.get('start_time', 0):.1f}s, text={sent.get('text', '')[:30]}...")
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
            raise ASRRecognitionError(f"ASR 语音识别超时，请检查网络连接或稍后重试")
        except aiohttp.ClientError as e:
            logger.error(f"[FunASR] Connection error: {e}")
            raise ASRRecognitionError(f"FunASR 连接失败，请检查服务是否正常运行")
        except Exception as e:
            logger.error(f"[FunASR] Recognition error: {e}")
            raise ASRRecognitionError(f"FunASR 语音识别失败: {str(e)}")

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
