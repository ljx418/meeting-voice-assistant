"""
实时语音转写器

使用 qwen3-asr-flash 流式输出实现实时语音识别
集成基于 FFT 的 VAD (Voice Activity Detection)
"""

import asyncio
import base64
import json
import aiohttp
import numpy as np
from typing import Optional, AsyncGenerator, Callable
from pathlib import Path
import logging

from .base import BaseTranscriber, TranscriptionSegment, TranscriptionResult

logger = logging.getLogger("app.core.asr.realtime_transcriber")


class RealtimeTranscriber(BaseTranscriber):
    """
    实时语音转写器

    使用 qwen3-asr-flash + stream:true 实现实时流式识别
    特点:
    - 基于 FFT 的 VAD 检测语音活动
    - 智能滑动窗口：检测到语音时延长到 10 秒再 commit
    - 检测到静音时立即 commit
    - 适合在线会议、实时对话等场景
    """

    # VAD 参数
    SAMPLE_RATE = 16000
    # 语音频率范围 (Hz) - 基频约 85-255Hz，但谐波也很重要
    SPEECH_FREQ_MIN = 80
    SPEECH_FREQ_MAX = 4000
    # 静音检测参数
    ENERGY_THRESHOLD = 0.01  # 短时能量阈值
    SILENCE_FRAMES_THRESHOLD = 5  # 连续多少帧静音认为语音结束
    FRAME_DURATION_MS = 50  # 每帧 50ms

    # 说话人分离参数
    NUM_BANDS = 8  # 频段数量
    SPEAKER_SIMILARITY_THRESHOLD = 0.85  # 说话人相似度阈值，低于此值认为是不同说话人

    def __init__(
        self,
        session_id: str,
        api_key: str,
        model: str = "qwen3-asr-flash",
        language: str = "zh",
        max_segment_duration: float = 10.0,
        min_segment_duration: float = 1.0,
        force_commit_interval: float = 3.0  # 强制 commit 间隔（秒）
    ):
        """
        初始化实时转写器

        Args:
            session_id: 会话 ID
            api_key: API 密钥
            model: 模型名称
            language: 语言代码
            max_segment_duration: 最大语段时长 (秒)，检测到语音时延长到此时长
            min_segment_duration: 最小语段时长 (秒)，静音时提前commit
            force_commit_interval: 强制 commit 间隔（秒），超过此时间即使没有静音也 commit
        """
        super().__init__(session_id)
        self.api_key = api_key
        self.model = model
        self.language = language
        self.max_segment_duration = max_segment_duration
        self.min_segment_duration = min_segment_duration
        self.force_commit_interval = 1.0  # 强制 commit 间隔（秒），测试用 1 秒

        self._session: Optional[aiohttp.ClientSession] = None
        self._audio_buffer = bytearray()
        self._speech_buffer = bytearray()  # 语音片段缓冲区
        self._buffer_lock = asyncio.Lock()

        # VAD 状态
        self._is_speaking = False
        self._silence_frames = 0
        self._cumulative_time = 0.0
        self._last_commit_cumulative_time = 0.0  # 上次 commit 时的累计时间
        self._last_commit_wall_time = 0.0  # 上次 commit 的墙钟时间

        # 每帧字节数
        self._frame_bytes = int(self.SAMPLE_RATE * 2 * (self.FRAME_DURATION_MS / 1000))

        self._result_queue: asyncio.Queue[TranscriptionSegment] = asyncio.Queue()

        # 说话人分离状态
        self._last_speaker_features: Optional[np.ndarray] = None  # 上一个片段的说话人特征
        self._current_speaker = "speaker_0"  # 当前说话人
        self._speaker_count = 0  # 说话人数量

        # 兼容性：适配旧的 VoiceSession 接口
        self._initialized = False

    # ========== 兼容性方法 (适配旧接口) ==========

    @property
    def engine_name(self) -> str:
        """返回引擎名称 (兼容性属性)"""
        return f"DashScope Realtime (qwen3-asr-flash)"

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
        self._initialized = True
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
        if self._audio_buffer:
            async with self._buffer_lock:
                if self._audio_buffer:
                    audio_data = bytes(self._audio_buffer)
                    self._audio_buffer.clear()
                    self._is_speaking = False
                    self._silence_frames = 0

                    if audio_data:
                        audio_duration = len(audio_data) / (self.SAMPLE_RATE * 2)
                        start_time = self._last_commit_cumulative_time
                        # 发送但不等待结果（因为 session 可能即将关闭）
                        asyncio.create_task(
                            self._send_for_transcription(audio_data, start_time, audio_duration)
                        )

    async def close(self) -> None:
        """关闭连接 (兼容旧接口)"""
        self._running = False
        if self._session:
            await self._session.close()
            self._session = None

    # ========== 原有接口 ==========

    async def start(self) -> None:
        """开始转写"""
        import time
        if self._running:
            print(f"[RT] start() called but _running is True, returning early")
            return

        print(f"[RT] start() creating session")
        self._session = aiohttp.ClientSession()
        self._running = True
        self._audio_buffer.clear()
        self._speech_buffer.clear()
        self._is_speaking = False
        self._silence_frames = 0
        self._cumulative_time = 0.0
        self._last_commit_cumulative_time = 0.0
        self._last_commit_wall_time = 0.0
        self._start_time = time.time()
        print(f"[RT] Started: session_id={self.session_id}, _start_time={self._start_time}")
        logger.info(f"[RealtimeTranscriber] Started: session_id={self.session_id}, model={self.model}")

    def _extract_speaker_features(self, audio_bytes: bytes) -> Optional[np.ndarray]:
        """
        提取说话人特征向量

        使用频段能量作为简化的说话人特征

        Args:
            audio_bytes: 原始 PCM 音频数据

        Returns:
            特征向量 (NUM_BANDS 维) 或 None
        """
        try:
            audio_data = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32)
            if len(audio_data) < self._frame_bytes:
                return None

            # FFT 分析
            fft_result = np.fft.rfft(audio_data)
            fft_magnitude = np.abs(fft_result)

            # 获取频率轴
            frequencies = np.fft.fftfreq(len(audio_data), 1.0/self.SAMPLE_RATE)
            freqs_positive = frequencies[:len(fft_magnitude)]

            # 语音频率范围内的频段划分
            speech_mask = (freqs_positive >= self.SPEECH_FREQ_MIN) & (freqs_positive <= self.SPEECH_FREQ_MAX)
            speech_magnitude = fft_magnitude * speech_mask

            # 将语音频率范围划分为 NUM_BANDS 个频段
            speech_freqs = freqs_positive[speech_mask]
            speech_mags = speech_magnitude[speech_mask]

            if len(speech_mags) == 0:
                return None

            # 对数划分频段（更符合人耳特性）
            log_freqs = np.log1p(speech_freqs)
            log_min, log_max = np.min(log_freqs), np.max(log_freqs)
            if log_max <= log_min:
                return None

            # 分配到频段
            band_edges = np.linspace(log_min, log_max, self.NUM_BANDS + 1)
            band_energies = np.zeros(self.NUM_BANDS)

            for i in range(len(speech_freqs)):
                band_idx = min(int((log_freqs[i] - log_min) / (log_max - log_min) * self.NUM_BANDS), self.NUM_BANDS - 1)
                band_energies[band_idx] += speech_mags[i] ** 2

            # 归一化
            total_energy = np.sum(band_energies)
            if total_energy > 0:
                band_energies = band_energies / total_energy

            return band_energies

        except Exception as e:
            logger.warning(f"[RealtimeTranscriber] Feature extraction error: {e}")
            return None

    def _compute_similarity(self, features1: np.ndarray, features2: np.ndarray) -> float:
        """
        计算两个特征向量之间的余弦相似度

        Returns:
            相似度 (0-1)，越大表示越相似
        """
        dot_product = np.dot(features1, features2)
        norm1 = np.linalg.norm(features1)
        norm2 = np.linalg.norm(features2)
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return dot_product / (norm1 * norm2)

    def _analyze_frame(self, audio_bytes: bytes) -> tuple[bool, float]:
        """
        分析单个音频帧，检测是否包含语音

        使用 FFT 分析频率成分，判断是否在语音频率范围内

        Args:
            audio_bytes: 原始 PCM 音频数据

        Returns:
            (is_speech, dominant_freq): 是否检测到语音, 主频率
        """
        try:
            # 转换为 numpy 数组 (16-bit PCM)
            audio_data = np.frombuffer(audio_bytes, dtype=np.int16)

            if len(audio_data) < 2:
                return False, 0.0

            # 计算短时能量
            energy = np.sqrt(np.mean(audio_data.astype(np.float32)**2))

            # 如果能量太低，直接判定为静音
            if energy < self.ENERGY_THRESHOLD * 32768:
                return False, 0.0

            # FFT 分析
            fft_result = np.fft.rfft(audio_data)
            fft_magnitude = np.abs(fft_result)

            # 获取频率轴
            frequencies = np.fft.fftfreq(len(audio_data), 1.0/self.SAMPLE_RATE)
            freqs_positive = frequencies[:len(fft_magnitude)]

            # 找主频率（在语音频率范围内）
            speech_mask = (freqs_positive >= self.SPEECH_FREQ_MIN) & (freqs_positive <= self.SPEECH_FREQ_MAX)
            speech_magnitude = fft_magnitude * speech_mask

            if np.max(speech_magnitude) > 0:
                dominant_freq_idx = np.argmax(speech_magnitude)
                dominant_freq = freqs_positive[dominant_freq_idx]
            else:
                dominant_freq = 0.0

            # 判断是否有语音：能量足够 + 主频率在语音范围内
            is_speech = energy > self.ENERGY_THRESHOLD * 32768

            return is_speech, dominant_freq

        except Exception as e:
            logger.warning(f"[RealtimeTranscriber] Frame analysis error: {e}")
            return False, 0.0

    def _update_vad_state(self) -> bool:
        """
        更新 VAD 状态，判断是否应该 commit

        基于 VAD + 说话人变化检测

        Returns:
            True if should commit, False otherwise
        """
        import time

        buffer_len = len(self._audio_buffer)
        current_duration = buffer_len / (self.SAMPLE_RATE * 2)
        min_bytes = int(self.SAMPLE_RATE * 2 * self.min_segment_duration)

        current_wall_time = time.time()
        time_since_start = getattr(self, '_start_time', 0)
        elapsed = current_wall_time - time_since_start if time_since_start > 0 else 0

        # 如果缓冲区为空，不commit
        if buffer_len < min_bytes:
            return False

        # 分析最后几帧，判断是否还在说话
        last_frames_bytes = min(self._frame_bytes * 10, buffer_len)
        recent_bytes = self._audio_buffer[-last_frames_bytes:]
        is_speech, _ = self._analyze_frame(bytes(recent_bytes))

        # 提取说话人特征并检测说话人变化
        speaker_changed = False
        current_features = self._extract_speaker_features(bytes(recent_bytes))
        if current_features is not None and self._last_speaker_features is not None:
            similarity = self._compute_similarity(current_features, self._last_speaker_features)
            if similarity < self.SPEAKER_SIMILARITY_THRESHOLD:
                print(f"[RT] Speaker change detected! similarity={similarity:.3f} < {self.SPEAKER_SIMILARITY_THRESHOLD}")
                speaker_changed = True
                self._speaker_count += 1
                self._current_speaker = f"speaker_{self._speaker_count % 2}"  # 交替使用两个说话人

        # 更新上一个片段的说话人特征
        if current_features is not None:
            self._last_speaker_features = current_features

        # 状态更新
        if is_speech:
            self._silence_frames = 0
            self._is_speaking = True
        else:
            self._silence_frames += 1
            if self._silence_frames >= self.SILENCE_FRAMES_THRESHOLD:
                self._is_speaking = False

        # 说话人变化时，且累积了一定时长，commit
        if speaker_changed and current_duration >= self.min_segment_duration:
            print(f"[RT] VAD: Speaker change commit")
            return True

        # 如果检测到静音，且之前在说话，且累积了一定时长，commit
        if not is_speech and self._is_speaking and current_duration >= self.min_segment_duration:
            print(f"[RT] VAD: Silence VAD commit")
            return True

        # 强制 commit：如果累积时间超过 force_commit_interval
        if time_since_start > 0 and elapsed >= self.force_commit_interval:
            print(f"[RT] VAD: Force commit! elapsed={elapsed:.1f}s >= {self.force_commit_interval}s")
            return True

        # 如果达到最大时长，强制 commit
        if current_duration >= self.max_segment_duration:
            print(f"[RT] VAD: Max duration commit: {current_duration:.1f}s >= {self.max_segment_duration}s")
            return True

        return False

    async def commit(self) -> Optional[TranscriptionSegment]:
        """
        提交缓冲区音频进行识别

        Returns:
            TranscriptionSegment 或 None
        """
        import time

        if not self._session:
            print(f"[RT] commit() returning None: _session is None")
            return None

        # VAD 状态更新和判断（加锁保护）
        async with self._buffer_lock:
            should_commit = self._update_vad_state()
            if not should_commit:
                return None

            audio_data = bytes(self._audio_buffer)
            self._audio_buffer.clear()
            self._is_speaking = False
            self._silence_frames = 0

            if not audio_data:
                return None

            # 计算时间戳
            audio_duration = len(audio_data) / (self.SAMPLE_RATE * 2)
            start_time = self._last_commit_cumulative_time
            self._last_commit_cumulative_time += audio_duration

            # 更新上次 commit 的墙钟时间
            self._last_commit_wall_time = time.time()
            print(f"[RT] commit() sending {audio_duration:.1f}s audio for transcription")

        return await self._send_for_transcription(audio_data, start_time, audio_duration)

    async def process_audio(self, audio_data: bytes) -> None:
        """
        处理音频数据

        Args:
            audio_data: 音频数据 (PCM 16kHz 16-bit mono)
        """
        if not self._running:
            return

        async with self._buffer_lock:
            self._audio_buffer.extend(audio_data)
            self.add_audio_chunk(audio_data)

    async def _send_for_transcription(
        self,
        audio_data: bytes,
        start_time: float,
        audio_duration: float
    ) -> Optional[TranscriptionSegment]:
        """发送音频到 ASR 服务"""
        print(f"[RT] _send_for_transcription called: {audio_duration:.1f}s audio")
        try:
            # 准备 Base64 编码的音频
            audio_b64 = base64.b64encode(audio_data).decode('utf-8')
            data_uri = f"data:audio/pcm;base64,{audio_b64}"

            # 构造请求
            request_data = {
                "model": self.model,
                "messages": [{
                    "content": [{
                        "type": "input_audio",
                        "input_audio": {"data": data_uri}
                    }],
                    "role": "user"
                }],
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

            # 发送流式请求
            full_text = ""

            async with self._session.post(
                "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
                headers=headers,
                json=request_data,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"[RealtimeTranscriber] Stream failed: {response.status} - {error_text}")
                    return None

                # 处理流式响应
                async for line in response.content:
                    line = line.decode('utf-8').strip()
                    if not line or not line.startswith('data:'):
                        continue

                    if line == 'data: [DONE]':
                        break

                    data_str = line[5:].strip()
                    try:
                        chunk = json.loads(data_str)
                    except json.JSONDecodeError:
                        continue

                    choices = chunk.get('choices', [])
                    if choices:
                        delta = choices[0].get('delta', {})
                        content = delta.get('content', '')
                        if content:
                            full_text += content

                        if choices[0].get('finish_reason') == 'stop':
                            break

            if full_text:
                segment = self.create_segment(
                    text=full_text,
                    start_time=start_time,
                    end_time=start_time + audio_duration,
                    speaker=self._current_speaker,
                    confidence=0.95,
                    is_final=True
                )
                self._segments.append(segment)
                print(f"[RT] Transcribed: {full_text[:50]}... [{start_time:.1f}s - {start_time + audio_duration:.1f}s] speaker={self._current_speaker}")
                return segment
            else:
                print(f"[RT] _send_for_transcription: no text transcribed from {audio_duration:.1f}s audio")

        except Exception as e:
            print(f"[RT] _send_for_transcription EXCEPTION: {e}")

        return None

    async def get_result(self, timeout: float = 1.0) -> Optional[TranscriptionResult]:
        """
        获取转写结果 (兼容接口)

        Args:
            timeout: 超时时间（秒）

        Returns:
            TranscriptionResult 或 None
        """
        # 尝试 commit 获取结果
        try:
            segment = await asyncio.wait_for(self.commit(), timeout=timeout)
            if segment:
                return TranscriptionResult(
                    session_id=self.session_id,
                    transcript=[segment],
                    duration=self.duration
                )
        except asyncio.TimeoutError:
            pass
        return None

    async def poll_results(self) -> AsyncGenerator[TranscriptionSegment, None]:
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
        transcription_task = None
        async with self._buffer_lock:
            if self._audio_buffer:
                audio_data = bytes(self._audio_buffer)
                self._audio_buffer.clear()

                if audio_data:
                    audio_duration = len(audio_data) / (self.SAMPLE_RATE * 2)
                    start_time = self._last_commit_cumulative_time
                    # 创建任务但不立即 await
                    transcription_task = asyncio.create_task(
                        self._send_for_transcription(audio_data, start_time, audio_duration)
                    )

        # 清理 session（在 await 之前）
        if self._session:
            await self._session.close()
            self._session = None

        # 等待最终转写完成
        if transcription_task:
            try:
                await asyncio.wait_for(transcription_task, timeout=30.0)
            except asyncio.TimeoutError:
                logger.warning(f"[RealtimeTranscriber] Final transcription timeout")

        result = self.build_result()
        logger.info(f"[RealtimeTranscriber] Stopped: session_id={self.session_id}, segments={len(self._segments)}")
        return result

    async def cancel(self) -> None:
        """取消转写"""
        self._running = False
        self._audio_buffer.clear()
        self._segments.clear()
        self._is_speaking = False
        self._silence_frames = 0

        if self._session:
            await self._session.close()
            self._session = None

        logger.info(f"[RealtimeTranscriber] Cancelled: session_id={self.session_id}")
