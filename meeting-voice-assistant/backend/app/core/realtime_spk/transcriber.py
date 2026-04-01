"""
实时语音转写 + 说话人识别转写器

集成 VAD、音频缓冲、FunASR 调用，实现带说话人分离的实时语音转写
"""

import asyncio
import logging
from typing import Optional

from ..asr.base import BaseTranscriber, TranscriptionSegment, TranscriptionResult
from .chunk_buffer import ChunkBuffer
from .funasr_streamer import FunASRStreamer
from . import config

logger = logging.getLogger("app.core.realtime_spk.transcriber")


class RealtimeSpkTranscriber(BaseTranscriber):
    """
    实时语音转写 + 说话人识别转写器

    特点：
    - 集成 VAD 检测语音活动
    - 音频前处理（消噪、缓存、切分）
    - 流式调用 FunASR 服务
    - 支持说话人分离

    使用"伪流式"策略：
    1. 持续累积音频到缓冲区
    2. 达到 chunk_duration 或检测到静音时
    3. 将缓冲区音频发送到 FunASR /recognize
    4. FunASR 返回带说话人的识别结果
    5. 继续累积后续音频
    """

    def __init__(
        self,
        session_id: str,
        funasr_endpoint: str = None,
        chunk_duration: float = None,
        min_chunk_duration: float = None,
        max_buffer_duration: float = None,
    ):
        """
        初始化实时转写器

        Args:
            session_id: 会话 ID
            funasr_endpoint: FunASR 服务地址
            chunk_duration: 每块音频目标时长 (秒)
            min_chunk_duration: 最小音频块时长 (秒)
            max_buffer_duration: 最大缓冲时长 (秒)
        """
        super().__init__(session_id)

        self.funasr_endpoint = funasr_endpoint or config.FUNASR_ENDPOINT
        self.chunk_duration = chunk_duration or config.CHUNK_DURATION
        self.min_chunk_duration = min_chunk_duration or config.MIN_CHUNK_DURATION
        self.max_buffer_duration = max_buffer_duration or config.MAX_BUFFER_DURATION

        # 初始化组件
        self._chunk_buffer = ChunkBuffer(
            sample_rate=config.SAMPLE_RATE,
            chunk_duration=self.chunk_duration,
            min_chunk_duration=self.min_chunk_duration,
            max_buffer_duration=self.max_buffer_duration,
        )
        self._funasr_streamer = FunASRStreamer(
            endpoint=self.funasr_endpoint,
            timeout=config.FUNASR_TIMEOUT,
        )

        # 状态
        self._running = False
        self._commit_task: Optional[asyncio.Task] = None

        # 兼容性：适配旧的 VoiceSession 接口
        self._initialized = False

    # ========== 兼容性方法 (适配旧接口) ==========

    @property
    def engine_name(self) -> str:
        """返回引擎名称 (兼容性属性)"""
        return "FunASR Realtime (Speaker Diarization)"

    @property
    def mode(self) -> str:
        """返回模式 (兼容性属性)"""
        return "realtime"

    @property
    def is_initialized(self) -> bool:
        """是否已初始化 (兼容性属性)"""
        return self._initialized

    async def initialize(self) -> None:
        """初始化 (兼容旧接口)"""
        await self.start()

    async def connect(self) -> None:
        """连接 (兼容旧接口)"""
        if not self._session:
            await self.start()

    async def append_audio(self, audio_data: bytes) -> None:
        """添加音频 (兼容旧接口)"""
        await self.process_audio(audio_data)

    async def finish(self) -> None:
        """结束会话 (兼容旧接口)"""
        # 提交剩余音频
        if self._chunk_buffer.get_buffer_duration() >= self.min_chunk_duration:
            audio_data, start_time, end_time = self._chunk_buffer.get_and_clear()
            if audio_data:
                asyncio.create_task(
                    self._funasr_streamer.recognize_chunk(audio_data, start_time, end_time)
                )

    async def close(self) -> None:
        """关闭连接 (兼容旧接口)"""
        await self.cancel()

    # ========== 原有接口 ==========

    async def start(self) -> None:
        """开始转写"""
        if self._running:
            return

        await self._funasr_streamer.initialize()
        self._running = True
        self._chunk_buffer.reset()
        self._initialized = True

        logger.info(f"[RealtimeSpkTranscriber] Started: session_id={self.session_id}, endpoint={self.funasr_endpoint}")

    async def process_audio(self, audio_data: bytes) -> None:
        """
        处理音频数据

        Args:
            audio_data: 音频数据 (PCM 16kHz 16-bit mono)
        """
        if not self._running:
            return

        # 添加到缓冲区
        self._chunk_buffer.append(audio_data)
        # 同时添加到基类的 audio_chunks（用于计算总时长等）
        self.add_audio_chunk(audio_data)

    async def commit(self) -> Optional[TranscriptionSegment]:
        """
        提交缓冲区进行识别

        Returns:
            TranscriptionSegment 或 None
        """
        if not self._running:
            return None

        # 检查是否应该提交
        if not self._chunk_buffer.should_commit():
            return None

        # 获取并清空缓冲区
        result = self._chunk_buffer.get_and_clear()
        if not result:
            return None

        audio_data, start_time, end_time = result

        if not audio_data:
            return None

        # 调用 FunASR 识别
        try:
            asr_results = await self._funasr_streamer.recognize_chunk(
                audio_data, start_time, end_time
            )

            if not asr_results:
                return None

            # 返回第一个结果作为片段
            # 实际上 FunASR 可能返回多个句子，这里我们合并它们
            segments = []
            for asr_result in asr_results:
                segment = self.create_segment(
                    text=asr_result.text,
                    start_time=asr_result.start_time,
                    end_time=asr_result.end_time,
                    speaker=asr_result.speaker,
                    confidence=asr_result.confidence,
                    is_final=True,
                )
                segments.append(segment)
                self._segments.append(segment)

            if segments:
                # 返回合并后的第一个片段作为代表
                first = segments[0]
                logger.info(
                    f"[RealtimeSpkTranscriber] Transcribed: {first.text[:50]}... "
                    f"[{first.start_time:.1f}s - {first.end_time:.1f}s] speaker={first.speaker}"
                )
                return first

        except Exception as e:
            logger.error(f"[RealtimeSpkTranscriber] Commit error: {e}")

        return None

    async def poll_results(self):
        """
        轮询识别结果

        Yields:
            TranscriptionSegment: 识别片段
        """
        while self._running:
            segment = await self.commit()
            if segment:
                yield segment
            await asyncio.sleep(0.1)  # 100ms 检查一次

    async def stop(self) -> TranscriptionResult:
        """
        停止转写并返回最终结果

        Returns:
            TranscriptionResult: 最终转写结果
        """
        self._running = False

        # 提交剩余音频
        if self._chunk_buffer.get_buffer_duration() >= self.min_chunk_duration:
            result = self._chunk_buffer.get_and_clear()
            if result:
                audio_data, start_time, end_time = result
                if audio_data:
                    try:
                        asr_results = await self._funasr_streamer.recognize_chunk(
                            audio_data, start_time, end_time
                        )
                        for asr_result in asr_results:
                            segment = self.create_segment(
                                text=asr_result.text,
                                start_time=asr_result.start_time,
                                end_time=asr_result.end_time,
                                speaker=asr_result.speaker,
                                confidence=asr_result.confidence,
                                is_final=True,
                            )
                            self._segments.append(segment)
                    except Exception as e:
                        logger.error(f"[RealtimeSpkTranscriber] Final transcription error: {e}")

        # 关闭 FunASR 连接
        await self._funasr_streamer.close()

        result = self.build_result()
        logger.info(
            f"[RealtimeSpkTranscriber] Stopped: session_id={self.session_id}, "
            f"segments={len(self._segments)}"
        )
        return result

    async def cancel(self) -> None:
        """取消转写"""
        self._running = False
        self._chunk_buffer.reset()
        self._segments.clear()
        await self._funasr_streamer.close()
        logger.info(f"[RealtimeSpkTranscriber] Cancelled: session_id={self.session_id}")

    async def get_result(self) -> Optional[TranscriptionResult]:
        """
        获取转写结果 (兼容接口)

        Returns:
            TranscriptionResult 或 None
        """
        # 尝试 commit 获取结果
        segment = await self.commit()
        if segment:
            return TranscriptionResult(
                session_id=self.session_id,
                transcript=self._segments.copy(),
                duration=self.duration,
            )
        return None
