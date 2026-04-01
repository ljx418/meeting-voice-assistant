"""
DashScope 实时语音识别适配器

使用 qwen3-asr-flash 的流式输出实现实时语音识别
- 使用 OpenAI 兼容接口
- 支持 stream: true 边发送边识别
- 延迟约 2-3 秒

API 文档: https://help.aliyun.com/zh/model-studio/qwen-speech-recognition
"""

import asyncio
import base64
import json
import aiohttp
from typing import AsyncGenerator, Optional
from pathlib import Path
import logging

from .base import ASRAdapterBase, ASRResult, ASRError, ASRInitError, ASRRecognitionError

logger = logging.getLogger("app.core.asr.realtime")


class DashScopeRealtimeASRAdapter(ASRAdapterBase):
    """
    DashScope 实时语音识别适配器

    使用 qwen3-asr-flash + stream:true 实现实时流式识别
    每次发送累积的音频，获取流式识别结果
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "qwen3-asr-flash",
        language: str = "zh"
    ):
        """
        初始化实时 ASR 适配器

        Args:
            api_key: API 密钥
            model: 模型名称 (qwen3-asr-flash)
            language: 语言代码
        """
        super().__init__()
        self.api_key = api_key
        self.model = model
        self.language = language
        self.session: Optional[aiohttp.ClientSession] = None
        self._running = False
        self._audio_buffer = bytearray()
        self._buffer_lock = asyncio.Lock()

    async def initialize(self) -> None:
        """初始化适配器"""
        if not self.api_key:
            raise ASRInitError("API key is required for DashScope Realtime ASR")

        self.session = aiohttp.ClientSession()
        self._initialized = True
        logger.info(f"[RealtimeASR] Initialized with model: {self.model}, language: {self.language}")

    async def close(self) -> None:
        """关闭连接"""
        self._running = False
        if self.session:
            await self.session.close()
            self.session = None
        self._audio_buffer.clear()
        self._initialized = False
        logger.info("[RealtimeASR] Adapter closed")

    async def finish(self) -> None:
        """结束会话"""
        self._running = False
        self._audio_buffer.clear()
        logger.info("[RealtimeASR] Session finished")

    async def connect(self) -> None:
        """建立连接"""
        if not self.session:
            await self.initialize()
        self._running = True
        self._audio_buffer.clear()
        logger.info("[RealtimeASR] Connected (streaming mode)")

    async def append_audio(self, audio_chunk: bytes) -> None:
        """
        添加音频数据到缓冲区

        Args:
            audio_chunk: 音频数据 (PCM)
        """
        async with self._buffer_lock:
            self._audio_buffer.extend(audio_chunk)

    async def commit(self) -> Optional[ASRResult]:
        """
        提交缓冲区音频进行识别，返回流式结果

        Returns:
            ASRResult 或 None
        """
        if not self.session or not self._audio_buffer:
            logger.warning("[RealtimeASR] No session or empty buffer")
            return None

        audio_data = bytes(self._audio_buffer)
        self._audio_buffer.clear()

        if len(audio_data) < 1000:  # Less than ~60ms of audio
            logger.debug(f"[RealtimeASR] Buffer too small: {len(audio_data)} bytes")
            return None

        try:
            # 准备 Base64 编码的音频
            audio_b64 = base64.b64encode(audio_data).decode('utf-8')
            data_uri = f"data:audio/pcm;base64,{audio_b64}"

            # 构造请求
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
                "stream": True,
                "extra_body": {
                    "asr_options": {
                        "language": self.language,
                        "enable_itn": True
                    }
                }
            }

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            # 使用流式请求
            full_text = ""
            audio_seconds = len(audio_data) / (16000 * 2)  # 16kHz, 16-bit

            logger.info(f"[RealtimeASR] Sending stream request: {len(audio_data)} bytes, duration: {audio_seconds:.2f}s")

            async with self.session.post(
                "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
                headers=headers,
                json=request_data,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"[RealtimeASR] Stream request failed: {response.status} - {error_text}")
                    return None

                logger.info(f"[RealtimeASR] Stream response status: {response.status}")

                # 处理流式响应
                async for line in response.content:
                    line = line.decode('utf-8').strip()
                    if not line:
                        continue

                    if line.startswith('data: [DONE]'):
                        logger.info("[RealtimeASR] Stream DONE")
                        break

                    if line.startswith('data:'):
                        data_str = line[5:].strip()
                        try:
                            chunk = json.loads(data_str)
                            logger.debug(f"[RealtimeASR] Chunk: {str(chunk)[:100]}")

                            # 解析流式块
                            choices = chunk.get('choices', [])
                            if choices and len(choices) > 0:
                                delta = choices[0].get('delta', {})
                                content = delta.get('content', '')
                                if content:
                                    full_text += content
                                    logger.info(f"[RealtimeASR] Stream content: {content}")

                                # 检查是否结束
                                finish_reason = choices[0].get('finish_reason')
                                if finish_reason == 'stop':
                                    logger.info("[RealtimeASR] Stream finished")
                                    break

                        except json.JSONDecodeError as e:
                            logger.warning(f"[RealtimeASR] JSON decode error: {e}")
                            continue

                logger.info(f"[RealtimeASR] Full text: {full_text[:100] if full_text else '(empty)'}")

                if full_text:
                    return ASRResult(
                        text=full_text,
                        start_time=0,
                        end_time=audio_seconds,
                        speaker="unknown",
                        confidence=0.95,
                        is_final=True
                    )

        except Exception as e:
            logger.error(f"[RealtimeASR] Stream recognition error: {e}")
            import traceback
            traceback.print_exc()
            return None

        return None

    async def get_result(self, timeout: float = 1.0) -> Optional[ASRResult]:
        """
        获取一个识别结果 (兼容接口)
        """
        return await self.commit()

    async def recognize_stream(
        self,
        audio_stream: AsyncGenerator[bytes, None],
        sample_rate: int = 16000,
        channels: int = 1,
        sample_width: int = 2
    ) -> AsyncGenerator[ASRResult, None]:
        """
        流式语音识别 (兼容接口)

        累积音频流，每隔一段时间自动提交识别
        """
        if not self._initialized:
            await self.initialize()

        await self.connect()

        chunk_duration = 2  # 每 2 秒识别一次
        bytes_per_chunk = sample_rate * sample_width * channels * chunk_duration
        buffer = bytearray()

        async for audio_chunk in audio_stream:
            buffer.extend(audio_chunk)

            if len(buffer) >= bytes_per_chunk:
                # 提交识别
                self._audio_buffer = buffer
                result = await self.commit()
                if result:
                    yield result
                buffer = bytearray()

        # 处理剩余数据
        if buffer:
            self._audio_buffer = buffer
            result = await self.commit()
            if result:
                yield result

    async def recognize_file(self, file_path: Path) -> AsyncGenerator[ASRResult, None]:
        """
        识别音频文件
        """
        if not self._initialized:
            await self.initialize()

        logger.info(f"[RealtimeASR] Recognizing file: {file_path}")

        audio_bytes = file_path.read_bytes()

        # 跳过 WAV header
        if audio_bytes[:4] == b'RIFF':
            audio_data = audio_bytes[44:]
        else:
            audio_data = audio_bytes

        # 提交识别
        self._audio_buffer = bytearray(audio_data)
        result = await self.commit()

        if result:
            yield result

    @property
    def engine_name(self) -> str:
        return "DashScope Realtime ASR (qwen3-asr-flash streaming)"
