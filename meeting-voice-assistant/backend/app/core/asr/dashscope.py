"""
DashScope ASR 适配器

使用 DashScope OpenAI兼容接口调用 Qwen3-ASR-Flash 模型
"""

import asyncio
import json
import aiohttp
import base64
from typing import AsyncGenerator, Optional, BinaryIO
from datetime import datetime
from pathlib import Path

from .base import ASRAdapterBase, ASRResult, ASRError, ASRInitError, ASRRecognitionError


class DashScopeASRAdapter(ASRAdapterBase):
    """
    DashScope ASR 适配器

    使用阿里云 DashScope OpenAI兼容接口调用 Qwen3-ASR-Flash 模型
    """

    def __init__(self,
                 endpoint: str = "https://dashscope.aliyuncs.com/v1",
                 api_key: Optional[str] = None,
                 model: str = "qwen3-asr-flash"):
        """
        初始化 DashScope ASR 适配器

        Args:
            endpoint: DashScope API 端点
            api_key: API 密钥
            model: 模型名称
        """
        self.base_url = endpoint
        self.api_key = api_key
        self.model = model
        self.session: Optional[aiohttp.ClientSession] = None
        self._running = False

    async def initialize(self) -> None:
        """初始化适配器"""
        if not self.api_key:
            raise ASRInitError("API key is required for DashScope ASR")

        self.session = aiohttp.ClientSession()
        logger = self._get_logger()
        logger.info(f"[DashScope] Initialized with model: {self.model}")

    async def close(self) -> None:
        """关闭适配器"""
        if self.session:
            await self.session.close()
            self.session = None

        logger = self._get_logger()
        logger.info("[DashScope] Adapter closed")

    async def recognize_stream(self, audio_stream: AsyncGenerator[bytes, None], sample_rate: int = 16000, channels: int = 1, sample_width: int = 2) -> AsyncGenerator[ASRResult, None]:
        """
        流式语音识别

        Args:
            audio_stream: 音频流生成器
            sample_rate: 采样率，默认 16000 Hz
            channels: 声道数，默认单声道
            sample_width: 采样位深，默认 16-bit (2 bytes)

        Yields:
            ASRResult: 识别结果
        """
        if not self.session:
            raise ASRError("Adapter not initialized")

        self._running = True

        try:
            # 将音频流转换为Base64
            audio_base64 = await self._audio_to_base64(audio_stream)

            # 构造请求数据
            request_data = {
                "model": self.model,
                "response_format": "json",
                "input": {
                    "type": "audio",
                    "format": "wav",
                    "sample_rate": sample_rate,
                    "channels": channels,
                    "audio": audio_base64
                }
            }

            # 发送请求
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            async with self.session.post(
                f"{self.base_url}/audio/transcriptions",
                headers=headers,
                json=request_data
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise ASRError(f"ASR request failed: {response.status} - {error_text}")

                result_data = await response.json()

                # 解析结果
                text = result_data.get("text", "")
                if text:
                    # 估算时间（基于音频长度）
                    start_time = 0
                    end_time = 1.0  # 1秒音频示例
                    confidence = result_data.get("confidence", 0.0)

                    yield ASRResult(
                        text=text,
                        start_time=start_time,
                        end_time=end_time,
                        confidence=confidence,
                        speaker="unknown",
                        is_final=True
                    )

        except Exception as e:
            logger = self._get_logger()
            logger.error(f"[DashScope] Recognition error: {e}")
            raise ASRRecognitionError(f"DashScope recognition failed: {str(e)}")
        finally:
            self._running = False

    async def recognize_file(self, file_path: Path) -> AsyncGenerator[ASRResult, None]:
        """
        识别音频文件 - 使用 OpenAI 兼容接口

        Args:
            file_path: 音频文件路径

        Yields:
            ASRResult: 识别结果
        """
        if not self.session:
            raise ASRError("Adapter not initialized")

        logger = self._get_logger()
        logger.info(f"[DashScope] Recognizing file: {file_path}")

        try:
            # 读取文件内容并转为 Base64
            audio_bytes = file_path.read_bytes()
            import base64
            audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')

            # 根据文件扩展名确定 MIME 类型
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
            data_uri = f"data:{mime_type};base64,{audio_base64}"

            # 使用 OpenAI 兼容接口
            request_data = {
                "model": self.model,
                "messages": [
                    {
                        "content": [
                            {
                                "type": "input_audio",
                                "input_audio": {
                                    "data": data_uri
                                }
                            }
                        ],
                        "role": "user"
                    }
                ],
                "stream": False,
                "extra_body": {
                    "asr_options": {
                        "enable_itn": True  # 启用逆文本标准化
                    }
                }
            }

            # 发送请求 - 使用兼容接口
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            # OpenAI 兼容接口
            openai_url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"

            async with self.session.post(
                openai_url,
                headers=headers,
                json=request_data
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"[DashScope] ASR request failed: {response.status} - {error_text}")
                    raise ASRError(f"ASR request failed: {response.status} - {error_text}")

                result_data = await response.json()
                logger.info(f"[DashScope] File transcription result: {result_data}")

                # 解析 OpenAI 兼容格式的响应
                if "choices" in result_data and len(result_data["choices"]) > 0:
                    message = result_data["choices"][0].get("message", {})
                    content = message.get("content", [])

                    # content 是一个数组，可能包含多个文本块
                    text_parts = []
                    for item in content:
                        if isinstance(item, dict) and item.get("type") == "audio":
                            text_parts.append(item.get("transcript", ""))
                        elif isinstance(item, str):
                            text_parts.append(item)

                    text = "".join(text_parts)
                    if text:
                        confidence = result_data.get("usage", {}).get("completion_tokens", 10) / 10.0
                        audio_duration = len(audio_bytes) / (16000 * 2)  # 估算时长

                        yield ASRResult(
                            text=text,
                            start_time=0,
                            end_time=audio_duration,
                            confidence=min(confidence, 1.0),
                            speaker="unknown",
                            is_final=True
                        )

        except Exception as e:
            logger.error(f"[DashScope] File recognition error: {e}")
            raise ASRRecognitionError(f"DashScope file recognition failed: {str(e)}")

    async def _audio_to_base64(self, audio_stream: AsyncGenerator[bytes, None]) -> str:
        """将音频流转换为Base64编码"""
        audio_bytes = b""
        async for chunk in audio_stream:
            audio_bytes += chunk

        # 添加WAV文件头（简化版）
        if not audio_bytes.startswith(b'RIFF'):
            # 创建简单的WAV文件头
            wav_header = self._create_wav_header(len(audio_bytes))
            audio_bytes = wav_header + audio_bytes

        return base64.b64encode(audio_bytes).decode('utf-8')

    def _create_wav_header(self, data_length: int) -> bytes:
        """创建WAV文件头"""
        # 简化的WAV文件头（16kHz, 16-bit, mono）
        header = bytearray(44)

        # RIFF header
        header[0:4] = b'RIFF'
        header[4:8] = (36 + data_length).to_bytes(4, 'little')
        header[8:12] = b'WAVE'

        # Format chunk
        header[12:16] = b'fmt '
        header[16:20] = (16).to_bytes(4, 'little')
        header[20:22] = (1).to_bytes(2, 'little')  # PCM
        header[22:24] = (1).to_bytes(2, 'little')  # Mono
        header[24:28] = (16000).to_bytes(4, 'little')  # Sample rate
        header[28:32] = (32000).to_bytes(4, 'little')  # Byte rate (16kHz * 2 bytes * 1 channel)
        header[32:34] = (2).to_bytes(2, 'little')  # Block align
        header[34:36] = (16).to_bytes(2, 'little')  # Bits per sample

        # Data chunk
        header[36:40] = b'data'
        header[40:44] = (data_length).to_bytes(4, 'little')

        return bytes(header)

    @property
    def engine_name(self) -> str:
        """返回引擎名称"""
        return "DashScope Qwen3 ASR"

    def _get_logger(self):
        """获取日志器"""
        import logging
        return logging.getLogger("app.core.asr.dashscope")