"""
VAD (Voice Activity Detection) 语音活动检测

基于 FFT 的语音频率检测算法，用于判断音频是否包含语音
"""

import numpy as np
import logging
from typing import Tuple

logger = logging.getLogger("app.core.realtime_spk.vad")


class VAD:
    """
    语音活动检测器

    使用 FFT 分析频率成分，结合短时能量判断是否包含语音
    """

    # 语音频率范围 (Hz)
    SPEECH_FREQ_MIN = 80
    SPEECH_FREQ_MAX = 4000

    # 短时能量阈值（相对于满幅值 32768 的比例）
    ENERGY_THRESHOLD = 0.01

    # 连续静音帧阈值：超过此数量的静音帧认为语音结束
    SILENCE_FRAMES_THRESHOLD = 5

    # 每帧时长 (ms)
    FRAME_DURATION_MS = 50

    def __init__(self, sample_rate: int = 16000):
        """
        初始化 VAD

        Args:
            sample_rate: 采样率 (Hz)
        """
        self.sample_rate = sample_rate
        self._is_speaking = False
        self._silence_frames = 0

        # 每帧字节数 (16-bit mono = 2 bytes per sample)
        self._frame_bytes = int(sample_rate * 2 * (self.FRAME_DURATION_MS / 1000))

    def analyze_frame(self, audio_bytes: bytes) -> Tuple[bool, float]:
        """
        分析单个音频帧，检测是否包含语音

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
            energy = np.sqrt(np.mean(audio_data.astype(np.float32) ** 2))

            # 如果能量太低，直接判定为静音
            if energy < self.ENERGY_THRESHOLD * 32768:
                return False, 0.0

            # FFT 分析
            fft_result = np.fft.rfft(audio_data)
            fft_magnitude = np.abs(fft_result)

            # 获取频率轴
            frequencies = np.fft.fftfreq(len(audio_data), 1.0 / self.sample_rate)
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
            logger.warning(f"[VAD] Frame analysis error: {e}")
            return False, 0.0

    def update_state(self, audio_buffer: bytes) -> bool:
        """
        更新 VAD 状态，判断是否应该提交音频

        Args:
            audio_buffer: 当前音频缓冲区

        Returns:
            True if should commit, False otherwise
        """
        if len(audio_buffer) < self._frame_bytes:
            return False

        # 分析最后几帧，判断是否还在说话
        last_frames_bytes = min(self._frame_bytes * 10, len(audio_buffer))
        recent_bytes = audio_buffer[-last_frames_bytes:]
        is_speech, _ = self.analyze_frame(bytes(recent_bytes))

        # 状态更新
        if is_speech:
            self._silence_frames = 0
            self._is_speaking = True
        else:
            self._silence_frames += 1
            if self._silence_frames >= self.SILENCE_FRAMES_THRESHOLD:
                self._is_speaking = False

        # 如果检测到静音，且之前在说话
        if not is_speech and self._is_speaking:
            # 计算当前缓冲区时长
            current_duration = len(audio_buffer) / (self.sample_rate * 2)
            if current_duration >= 1.0:  # 至少1秒
                return True

        return False

    def reset(self) -> None:
        """重置 VAD 状态"""
        self._is_speaking = False
        self._silence_frames = 0

    @property
    def is_speaking(self) -> bool:
        """是否正在说话"""
        return self._is_speaking
