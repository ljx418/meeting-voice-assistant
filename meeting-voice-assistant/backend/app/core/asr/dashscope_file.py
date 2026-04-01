"""
DashScope 大文件 ASR 适配器

使用阿里云 DashScope 异步调用 API，支持最大 512MB+ 的长音频文件
API 文档: https://help.aliyun.com/zh/model-studio/qwen-speech-recognition

流程:
1. 提交任务 -> 获取 task_id
2. 轮询获取结果
"""

import asyncio
import json
import aiohttp
import base64
import logging
from typing import AsyncGenerator, Optional
from datetime import datetime
from pathlib import Path
import time
import uuid

from .base import ASRAdapterBase, ASRResult, ASRError, ASRInitError, ASRRecognitionError

logger = logging.getLogger("app.core.asr.dashscope_file")


class DashScopeFileASRAdapter(ASRAdapterBase):
    """
    DashScope 大文件 ASR 适配器

    使用阿里云 DashScope 异步调用 API (qwen3-asr-flash-filetrans)
    支持 mp3, mp4, wav, m4a, ogg, flac, webm 等格式
    最大支持 512MB+ 文件
    """

    # 异步任务状态
    TASK_STATUS_PENDING = "PENDING"
    TASK_STATUS_RUNNING = "RUNNING"
    TASK_STATUS_SUCCEEDED = "SUCCEEDED"
    TASK_STATUS_FAILED = "FAILED"

    def __init__(self,
                 api_key: Optional[str] = None,
                 model: str = "qwen3-asr-flash-filetrans"):
        """
        初始化 DashScope 大文件 ASR 适配器

        Args:
            api_key: API 密钥
            model: 模型名称 (默认 qwen3-asr-flash-filetrans)
        """
        self.api_key = api_key
        self.model = model
        self.session: Optional[aiohttp.ClientSession] = None

        # API 配置
        self.base_url = "https://dashscope.aliyuncs.com/api/v1"
        self.async_transcription_url = f"{self.base_url}/services/audio/asr/transcription"

    async def initialize(self) -> None:
        """初始化适配器"""
        if not self.api_key:
            raise ASRInitError("API key is required for DashScope File ASR")

        self.session = aiohttp.ClientSession()
        logger.info(f"[DashScopeFile] Initialized with model: {self.model}")

    async def close(self) -> None:
        """关闭适配器"""
        if self.session:
            await self.session.close()
            self.session = None
        logger.info("[DashScopeFile] Adapter closed")

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
        raise NotImplementedError("Use recognize_file() for large file transcription")

    async def recognize_file(self, file_path: Path) -> AsyncGenerator[ASRResult, None]:
        """
        识别音频文件（支持大文件，自动分片）

        Args:
            file_path: 音频文件路径

        Yields:
            ASRResult: 识别结果
        """
        if not self.session:
            raise ASRError("Adapter not initialized")

        logger.info(f"[DashScopeFile] Recognizing file: {file_path}")

        try:
            # 读取文件
            audio_bytes = file_path.read_bytes()
            file_size = len(audio_bytes)
            logger.info(f"[DashScopeFile] File size: {file_size / (1024*1024):.2f} MB")

            # 获取文件 MIME 类型
            ext = file_path.suffix.lower().lstrip('.')
            mime_map = {
                'mp3': 'audio/mpeg',
                'mp4': 'audio/mp4',
                'wav': 'audio/wav',
                'm4a': 'audio/m4a',
                'ogg': 'audio/ogg',
                'flac': 'audio/flac',
                'webm': 'audio/webm',
            }
            mime_type = mime_map.get(ext, 'audio/mpeg')

            # Base64 限制为 10MB，考虑 33% 开销，原始文件限制约 7.5MB
            max_original_size = int(7.5 * 1024 * 1024)  # 7.5MB

            if file_size <= max_original_size:
                # 小文件直接处理
                logger.info(f"[DashScopeFile] File within limit, processing directly")
                results = await self._process_single_chunk(audio_bytes, mime_type, start_offset=0.0)
                for result in results:
                    yield result
            else:
                # 大文件需要分片
                logger.info(f"[DashScopeFile] File too large, splitting into chunks...")
                results = await self._split_and_process(audio_bytes, mime_type, file_path, max_original_size)
                cumulative_offset = 0.0
                for result in results:
                    # 调整时间戳（加上前面所有 chunk 的时长）
                    adjusted_result = ASRResult(
                        text=result.text,
                        start_time=result.start_time + cumulative_offset,
                        end_time=result.end_time + cumulative_offset,
                        confidence=result.confidence,
                        speaker=result.speaker,
                        is_final=result.is_final
                    )
                    cumulative_offset = adjusted_result.end_time
                    yield adjusted_result

        except asyncio.TimeoutError:
            logger.error(f"[DashScopeFile] Request timeout for file: {file_path}")
            raise ASRRecognitionError(f"ASR request timeout")
        except Exception as e:
            logger.error(f"[DashScopeFile] File recognition error: {e}")
            raise ASRRecognitionError(f"DashScope file recognition failed: {str(e)}")

    async def _split_and_process(
        self,
        audio_bytes: bytes,
        mime_type: str,
        original_path: Path,
        max_chunk_size: int
    ) -> list:
        """
        分片处理大文件

        Args:
            audio_bytes: 原始音频数据
            mime_type: MIME 类型
            original_path: 原始文件路径（用于生成临时文件）
            max_chunk_size: 每个 chunk 的最大字节数

        Returns:
            list: 所有 chunk 的识别结果
        """
        all_results = []
        chunk_count = 0
        offset = 0

        # 计算总时长（假设 16kHz 16-bit mono）
        total_duration = len(audio_bytes) / (16000 * 2)
        chunk_duration = max_chunk_size / (16000 * 2)  # 每个 chunk 的时长（秒）

        logger.info(f"[DashScopeFile] Splitting {total_duration:.1f}s audio into chunks of {chunk_duration:.1f}s each")

        while offset < len(audio_bytes):
            chunk_count += 1
            chunk_end = min(offset + int(max_chunk_size), len(audio_bytes))
            chunk_data = audio_bytes[offset:chunk_end]

            logger.info(f"[DashScopeFile] Processing chunk {chunk_count}: bytes {offset}-{chunk_end} ({len(chunk_data) / (1024*1024):.2f} MB)")

            # 估算这个 chunk 的开始时间
            chunk_start_time = offset / (16000 * 2)

            try:
                # 处理单个 chunk
                results = await self._process_single_chunk(chunk_data, mime_type, start_offset=chunk_start_time)
                all_results.extend(results)
            except Exception as e:
                logger.error(f"[DashScopeFile] Chunk {chunk_count} failed: {e}")
                # 继续处理下一个 chunk

            offset = chunk_end

        logger.info(f"[DashScopeFile] Completed {chunk_count} chunks, total results: {len(all_results)}")
        return all_results

    async def _process_single_chunk(
        self,
        audio_bytes: bytes,
        mime_type: str,
        start_offset: float = 0.0
    ) -> list:
        """
        处理单个音频块

        Args:
            audio_bytes: 音频数据
            mime_type: MIME 类型
            start_offset: 时间偏移（秒）

        Returns:
            list: 识别结果列表
        """
        audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
        data_uri = f"data:{mime_type};base64,{audio_base64}"

        # 提交任务
        task_id = await self._submit_task(data_uri)
        if not task_id:
            raise ASRRecognitionError("Failed to submit transcription task")

        logger.info(f"[DashScopeFile] Chunk task submitted: {task_id}")

        # 等待结果
        result_url = await self._wait_for_result(task_id)
        if not result_url:
            raise ASRRecognitionError("Failed to get transcription result")

        # 下载结果
        transcription = await self._download_result(result_url)
        if not transcription:
            raise ASRRecognitionError("Failed to download transcription")

        # 解析结果
        results = []
        if transcription.get("transcripts"):
            for transcript in transcription["transcripts"]:
                channel_id = transcript.get("channel_id", 0)
                sentences = transcript.get("sentences", [])

                for sentence in sentences:
                    begin_time = sentence.get("begin_time", 0) / 1000.0 + start_offset
                    end_time = sentence.get("end_time", 0) / 1000.0 + start_offset
                    sentence_text = sentence.get("text", "")

                    if sentence_text:
                        # channel_id 可以是 0，所以用 is not None 判断
                        speaker_id = f"speaker_{channel_id}" if channel_id is not None else "unknown"
                        results.append(ASRResult(
                            text=sentence_text,
                            start_time=begin_time,
                            end_time=end_time,
                            confidence=0.95,
                            speaker=speaker_id,
                            is_final=True
                        ))

        return results

    def _compress_audio(self, input_path: Path, output_path: Path) -> bool:
        """
        使用 ffmpeg 压缩音频文件

        Args:
            input_path: 输入文件路径
            output_path: 输出文件路径

        Returns:
            bool: 是否成功
        """
        import shutil
        if not shutil.which('ffmpeg'):
            logger.error("[DashScopeFile] ffmpeg not found, cannot compress")
            return False

        try:
            # 使用 ffmpeg 压缩为 MP3，64kbps 比特率
            # 这样 10MB 的音频可以压缩到约 5MB
            result = subprocess.run([
                'ffmpeg', '-y',
                '-i', str(input_path),
                '-codec:a', 'libmp3lame',
                '-b:a', '64k',  # 低比特率压缩
                '-ar', '16000',  # 降采样到 16kHz（ASR 标准采样率）
                '-ac', '1',      # 单声道
                str(output_path)
            ], capture_output=True, check=True)
            logger.info(f"[DashScopeFile] Compression successful: {output_path}")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"[DashScopeFile] Compression failed: {e.stderr}")
            return False
        except Exception as e:
            logger.error(f"[DashScopeFile] Compression error: {e}")
            return False

    async def _submit_task(self, audio_data_uri: str) -> Optional[str]:
        """
        提交异步转写任务

        Args:
            audio_data_uri: Base64 编码的音频 Data URI

        Returns:
            task_id 或 None
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "X-DashScope-Async": "enable"
        }

        payload = {
            "model": self.model,
            "input": {
                "file_url": audio_data_uri  # Base64 Data URI
            },
            "parameters": {
                "language": "zh",
                "enable_itn": True,
                "enable_words": True,  # 启用词级别时间戳
                "channel_id": [0]
            }
        }

        try:
            logger.info(f"[DashScopeFile] Submitting task to {self.async_transcription_url}")
            async with self.session.post(
                self.async_transcription_url,
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=60)
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    logger.info(f"[DashScopeFile] Submit response: {result}")

                    if result.get("output") and result["output"].get("task_id"):
                        return result["output"]["task_id"]

                    # 检查错误
                    if result.get("code"):
                        logger.error(f"[DashScopeFile] Submit error: {result.get('code')}, {result.get('message')}")
                        # 记录完整响应以便调试
                        logger.error(f"[DashScopeFile] Full response: {result}")

                else:
                    error_text = await response.text()
                    logger.error(f"[DashScopeFile] Submit failed HTTP {response.status}: {error_text[:500]}")

                return None

        except Exception as e:
            logger.error(f"[DashScopeFile] Submit exception: {e}")
            import traceback
            logger.error(f"[DashScopeFile] Traceback: {traceback.format_exc()}")
            return None

    async def _wait_for_result(self, task_id: str, max_wait: int = 300) -> Optional[str]:
        """
        轮询等待转写结果

        Args:
            task_id: 任务 ID
            max_wait: 最大等待时间（秒）

        Returns:
            结果 URL 或 None
        """
        result_url = f"{self.base_url}/tasks/{task_id}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "X-DashScope-Async": "enable"
        }

        start_time = time.time()
        poll_interval = 2  # 轮询间隔（秒）

        while time.time() - start_time < max_wait:
            try:
                async with self.session.get(
                    result_url,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        task_status = result.get("output", {}).get("task_status")

                        logger.info(f"[DashScopeFile] Task status: {task_status}")

                        if task_status == self.TASK_STATUS_SUCCEEDED:
                            # 任务成功，获取结果 URL
                            result_data = result.get("output", {}).get("result", {})
                            transcription_url = result_data.get("transcription_url")
                            logger.info(f"[DashScopeFile] Transcription URL: {transcription_url}")
                            return transcription_url

                        elif task_status == self.TASK_STATUS_FAILED:
                            error_code = result.get("output", {}).get("code")
                            error_msg = result.get("output", {}).get("message")
                            logger.error(f"[DashScopeFile] Task failed: {error_code} - {error_msg}")
                            return None

                        # 继续等待
                        await asyncio.sleep(poll_interval)

                    else:
                        error_text = await response.text()
                        logger.error(f"[DashScopeFile] Poll failed: {response.status} - {error_text}")
                        return None

            except asyncio.TimeoutError:
                logger.warning("[DashScopeFile] Poll timeout, continuing...")
                await asyncio.sleep(poll_interval)
            except Exception as e:
                logger.error(f"[DashScopeFile] Poll exception: {e}")
                await asyncio.sleep(poll_interval)

        logger.error(f"[DashScopeFile] Timeout waiting for result (waited {max_wait}s)")
        return None

    async def _download_result(self, result_url: str) -> Optional[dict]:
        """
        下载转写结果

        Args:
            result_url: 结果文件 URL

        Returns:
            转写结果 dict 或 None
        """
        try:
            async with self.session.get(
                result_url,
                timeout=aiohttp.ClientTimeout(total=60)
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    logger.info(f"[DashScopeFile] Downloaded result: {str(result)[:200]}...")
                    return result
                else:
                    error_text = await response.text()
                    logger.error(f"[DashScopeFile] Download failed: {response.status} - {error_text}")
                    return None

        except Exception as e:
            logger.error(f"[DashScopeFile] Download exception: {e}")
            return None

    @property
    def engine_name(self) -> str:
        """返回引擎名称"""
        return f"DashScope File ASR ({self.model})"

    def _get_logger(self):
        """获取日志器"""
        import logging
        return logging.getLogger("app.core.asr.dashscope_file")
