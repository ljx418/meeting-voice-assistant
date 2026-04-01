"""
长录音文件转写器

使用 qwen3-asr-flash-filetrans 异步 API 实现大文件转写
"""

import asyncio
import base64
import json
import aiohttp
from typing import Optional
from pathlib import Path
import logging
import time

from .base import BaseTranscriber, TranscriptionSegment, TranscriptionResult

logger = logging.getLogger("app.core.asr.file_transcriber")


class FileTranscriber(BaseTranscriber):
    """
    长录音文件转写器

    使用 qwen3-asr-flash-filetrans 异步 API
    特点:
    - 支持最大 512MB+ 文件
    - 异步提交+轮询获取结果
    - 适合离线文件转写、长会议录音等场景
    """

    # 任务状态
    TASK_STATUS_PENDING = "PENDING"
    TASK_STATUS_RUNNING = "RUNNING"
    TASK_STATUS_SUCCEEDED = "SUCCEEDED"
    TASK_STATUS_FAILED = "FAILED"

    def __init__(
        self,
        session_id: str,
        api_key: str,
        model: str = "qwen3-asr-flash-filetrans",
        language: str = "zh",
        max_wait: int = 300
    ):
        """
        初始化文件转写器

        Args:
            session_id: 会话 ID
            api_key: API 密钥
            model: 模型名称
            language: 语言代码
            max_wait: 最大等待时间 (秒)
        """
        super().__init__(session_id)
        self.api_key = api_key
        self.model = model
        self.language = language
        self.max_wait = max_wait

        self._session: Optional[aiohttp.ClientSession] = None
        self._task_id: Optional[str] = None
        self._result_url: Optional[str] = None

        # API 配置
        self._base_url = "https://dashscope.aliyuncs.com/api/v1"
        self._async_url = f"{self._base_url}/services/audio/asr/transcription"

    async def start(self) -> None:
        """开始转写"""
        if self._running:
            return

        self._session = aiohttp.ClientSession()
        self._running = True
        logger.info(f"[FileTranscriber] Started: session_id={self.session_id}, model={self.model}")

    async def process_audio(self, audio_data: bytes) -> None:
        """
        处理音频数据 (累积到缓冲区)

        Args:
            audio_data: 音频数据
        """
        self.add_audio_chunk(audio_data)

    async def submit_task(self, audio_data: bytes, file_ext: str = "wav") -> Optional[str]:
        """
        提交转写任务

        Args:
            audio_data: 音频数据
            file_ext: 文件扩展名 (用于确定 MIME 类型)

        Returns:
            task_id 或 None
        """
        if not self._session:
            return None

        # 获取 MIME 类型
        mime_map = {
            'mp3': 'audio/mpeg',
            'mp4': 'audio/mp4',
            'wav': 'audio/wav',
            'm4a': 'audio/m4a',
            'ogg': 'audio/ogg',
            'flac': 'audio/flac',
            'webm': 'audio/webm',
        }
        mime_type = mime_map.get(file_ext.lower(), 'audio/mpeg')

        # Base64 编码
        audio_b64 = base64.b64encode(audio_data).decode('utf-8')
        data_uri = f"data:{mime_type};base64,{audio_b64}"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "X-DashScope-Async": "enable"
        }

        payload = {
            "model": self.model,
            "input": {
                "file_url": data_uri
            },
            "parameters": {
                "language": self.language,
                "enable_itn": True,
                "enable_words": True,
                "channel_id": [0]
            }
        }

        try:
            async with self._session.post(
                self._async_url,
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=60)
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    task_id = result.get("output", {}).get("task_id")
                    logger.info(f"[FileTranscriber] Task submitted: {task_id}")
                    return task_id
                else:
                    error_text = await response.text()
                    logger.error(f"[FileTranscriber] Submit failed: {response.status} - {error_text}")
                    return None

        except Exception as e:
            logger.error(f"[FileTranscriber] Submit error: {e}")
            return None

    async def poll_task_status(self) -> Optional[str]:
        """
        轮询任务状态直到完成

        Returns:
            结果 URL 或 None
        """
        if not self._session or not self._task_id:
            return None

        result_url = f"{self._base_url}/tasks/{self._task_id}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "X-DashScope-Async": "enable"
        }

        start_time = time.time()
        poll_interval = 2

        while time.time() - start_time < self.max_wait:
            try:
                async with self._session.get(
                    result_url,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        task_status = result.get("output", {}).get("task_status")

                        if task_status == self.TASK_STATUS_SUCCEEDED:
                            transcription_url = result.get("output", {}).get("result", {}).get("transcription_url")
                            logger.info(f"[FileTranscriber] Task succeeded: {transcription_url}")
                            return transcription_url

                        elif task_status == self.TASK_STATUS_FAILED:
                            error_code = result.get("output", {}).get("code")
                            error_msg = result.get("output", {}).get("message")
                            logger.error(f"[FileTranscriber] Task failed: {error_code} - {error_msg}")
                            return None

                        # 继续等待
                        logger.debug(f"[FileTranscriber] Task status: {task_status}")
                        await asyncio.sleep(poll_interval)

            except asyncio.TimeoutError:
                await asyncio.sleep(poll_interval)
            except Exception as e:
                logger.error(f"[FileTranscriber] Poll error: {e}")
                await asyncio.sleep(poll_interval)

        logger.error(f"[FileTranscriber] Timeout waiting for result")
        return None

    async def download_result(self, result_url: str) -> Optional[dict]:
        """
        下载转写结果

        Args:
            result_url: 结果文件 URL

        Returns:
            转写结果 dict 或 None
        """
        if not self._session:
            return None

        try:
            async with self._session.get(
                result_url,
                timeout=aiohttp.ClientTimeout(total=60)
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    logger.info(f"[FileTranscriber] Result downloaded")
                    return result
                else:
                    logger.error(f"[FileTranscriber] Download failed: {response.status}")
                    return None

        except Exception as e:
            logger.error(f"[FileTranscriber] Download error: {e}")
            return None

    async def get_result(self) -> Optional[TranscriptionResult]:
        """
        获取转写结果 (如果已完成)

        Returns:
            TranscriptionResult 或 None
        """
        # 需要先 submit_task 然后 poll_task_status
        return None

    async def transcribe_file(self, audio_data: bytes, file_ext: str = "wav") -> TranscriptionResult:
        """
        转写音频文件 (完整流程)

        Args:
            audio_data: 音频数据
            file_ext: 文件扩展名

        Returns:
            TranscriptionResult: 转写结果
        """
        if not self._running:
            await self.start()

        self.add_audio_chunk(audio_data)

        # 1. 提交任务
        self._task_id = await self.submit_task(audio_data, file_ext)
        if not self._task_id:
            raise RuntimeError("Failed to submit transcription task")

        # 2. 轮询等待结果
        self._result_url = await self.poll_task_status()
        if not self._result_url:
            raise RuntimeError("Failed to get transcription result")

        # 3. 下载结果
        result_data = await self.download_result(self._result_url)
        if not result_data:
            raise RuntimeError("Failed to download transcription result")

        # 4. 解析结果
        self._parse_result(result_data)

        return self.build_result()

    def _parse_result(self, result_data: dict) -> None:
        """解析转写结果"""
        transcripts = result_data.get("transcripts", [])

        for transcript in transcripts:
            channel_id = transcript.get("channel_id", 0)
            sentences = transcript.get("sentences", [])

            for sentence in sentences:
                begin_time = sentence.get("begin_time", 0) / 1000.0  # 毫秒转秒
                end_time = sentence.get("end_time", 0) / 1000.0
                text = sentence.get("text", "")
                language = sentence.get("language", "zh")

                if text:
                    segment = self.create_segment(
                        text=text,
                        start_time=begin_time,
                        end_time=end_time,
                        speaker=f"speaker_{channel_id}" if channel_id else "unknown",
                        confidence=0.95,
                        language=language,
                        is_final=True
                    )
                    self._segments.append(segment)

    async def stop(self) -> TranscriptionResult:
        """
        停止转写 (文件转写不支持中途停止)

        Returns:
            TranscriptionResult
        """
        # 文件转写已经开始就会执行完，这里只是做清理
        self._running = False

        if self._session:
            await self._session.close()
            self._session = None

        return self.build_result()

    async def cancel(self) -> None:
        """取消转写"""
        self._running = False
        self._task_id = None
        self._result_url = None
        self._segments.clear()

        if self._session:
            await self._session.close()
            self._session = None

        logger.info(f"[FileTranscriber] Cancelled: session_id={self.session_id}")
