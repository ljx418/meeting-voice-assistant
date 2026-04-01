"""
音频缓存模块

负责管理和缓存录音文件
"""

import asyncio
from pathlib import Path
from typing import Optional
import logging
import subprocess
import shutil

logger = logging.getLogger(__name__)


class AudioCache:
    """音频缓存管理器"""

    # 音频格式配置 (16kHz, 16-bit, mono PCM)
    SAMPLE_RATE = 16000
    SAMPLE_WIDTH = 2  # 16-bit
    CHANNELS = 1

    def __init__(self, cache_dir: Path):
        self.cache_dir = cache_dir
        # 确保缓存目录存在
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"[AudioCache] Initialized with cache dir: {self.cache_dir}")

    def _get_audio_path(self, session_id: str) -> Path:
        """获取音频文件路径"""
        # 如果 ffmpeg 可用，使用 MP3；否则使用 WAV
        if shutil.which('ffmpeg'):
            return self.cache_dir / f"{session_id}.mp3"
        return self.cache_dir / f"{session_id}.wav"

    def _get_raw_pcm_path(self, session_id: str) -> Path:
        """获取临时 PCM 文件路径"""
        return self.cache_dir / f"{session_id}_raw.pcm"

    async def save_audio(self, session_id: str, audio_data: bytes) -> Path:
        """
        保存音频数据到缓存，转换为 MP3 格式

        Args:
            session_id: 会话ID
            audio_data: 音频数据（原始 PCM 16kHz 16-bit mono）

        Returns:
            Path: 保存的音频文件路径 (MP3)
        """
        audio_path = self._get_audio_path(session_id)
        raw_path = self._get_raw_pcm_path(session_id)

        try:
            # 异步写入并转换文件
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: self._convert_to_mp3(raw_path, audio_path, audio_data)
            )
            logger.info(f"[AudioCache] Saved audio for session {session_id}: {len(audio_data)} bytes -> {audio_path}")
            return audio_path
        except Exception as e:
            logger.error(f"[AudioCache] Failed to save audio for session {session_id}: {e}")
            raise

    def _write_audio_file(self, path: Path, data: bytes) -> None:
        """写入音频文件"""
        with open(path, 'wb') as f:
            f.write(data)

    def _convert_to_mp3(self, raw_path: Path, mp3_path: Path, pcm_data: bytes) -> None:
        """
        将 PCM 数据转换为 MP3 格式

        Args:
            raw_path: 临时 PCM 文件路径
            mp3_path: 输出 MP3 文件路径
            pcm_data: 原始 PCM 数据
        """
        # 1. 先写入临时 PCM 文件
        with open(raw_path, 'wb') as f:
            f.write(pcm_data)

        try:
            # 2. 使用 ffmpeg 转换为 MP3
            # 检查 ffmpeg 是否可用
            if shutil.which('ffmpeg'):
                subprocess.run([
                    'ffmpeg', '-y',
                    '-f', 's16le',           # 输入格式: signed 16-bit little-endian
                    '-ar', str(self.SAMPLE_RATE),
                    '-ac', str(self.CHANNELS),
                    '-i', str(raw_path),
                    '-codec:a', 'libmp3lame',
                    '-b:a', '128k',          # MP3 比特率
                    str(mp3_path)
                ], check=True, capture_output=True)
                logger.info(f"[AudioCache] Converted to MP3 using ffmpeg: {mp3_path}")
            else:
                # 如果没有 ffmpeg，尝试使用 pydub
                try:
                    from pydub import AudioSegment

                    # 从 PCM 数据创建 AudioSegment
                    audio = AudioSegment(
                        data=pcm_data,
                        sample_width=self.SAMPLE_WIDTH,
                        frame_rate=self.SAMPLE_RATE,
                        channels=self.CHANNELS
                    )
                    # 导出为 MP3
                    audio.export(mp3_path, format='mp3', bitrate='128k')
                    logger.info(f"[AudioCache] Converted to MP3 using pydub: {mp3_path}")
                except ImportError:
                    # 降级: 保存为 WAV 格式 (带正确头)，使用正确的扩展名
                    logger.warning(f"[AudioCache] ffmpeg not found, falling back to WAV format")
                    wav_path = mp3_path.with_suffix('.wav')
                    self._save_as_wav(wav_path, pcm_data)
                    # 不要重命名为 .mp3，直接使用 .wav
                    # 如果需要 MP3，用户应安装 ffmpeg: brew install ffmpeg
        finally:
            # 3. 清理临时文件
            if raw_path.exists():
                raw_path.unlink()

    def _save_as_wav(self, path: Path, pcm_data: bytes) -> None:
        """保存为 WAV 格式 (带正确头)"""
        import wave
        with wave.open(str(path), 'wb') as wav_file:
            wav_file.setnchannels(self.CHANNELS)
            wav_file.setsampwidth(self.SAMPLE_WIDTH)
            wav_file.setframerate(self.SAMPLE_RATE)
            wav_file.writeframes(pcm_data)
        logger.info(f"[AudioCache] Saved as WAV: {path}")

    def get_audio_path(self, session_id: str) -> Optional[Path]:
        """
        获取缓存的音频路径

        Args:
            session_id: 会话ID

        Returns:
            Optional[Path]: 音频文件路径，如果不存在则返回 None
        """
        # 先找 MP3，不存在则找 WAV (向后兼容)
        audio_path = self._get_audio_path(session_id)
        if audio_path.exists():
            return audio_path
        wav_path = audio_path.with_suffix('.wav')
        if wav_path.exists():
            return wav_path
        return None

    def list_cached_audio(self) -> list[Path]:
        """
        列出所有缓存的音频文件

        Returns:
            list[Path]: 缓存的音频文件路径列表
        """
        if not self.cache_dir.exists():
            return []
        return list(self.cache_dir.glob("*.mp3")) + list(self.cache_dir.glob("*.wav"))

    async def delete_audio(self, session_id: str) -> bool:
        """
        删除缓存的音频文件

        Args:
            session_id: 会话ID

        Returns:
            bool: 是否删除成功
        """
        audio_path = self._get_audio_path(session_id)

        try:
            if audio_path.exists():
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, lambda: audio_path.unlink())
                logger.info(f"[AudioCache] Deleted audio for session {session_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"[AudioCache] Failed to delete audio for session {session_id}: {e}")
            return False

    async def cleanup_old_files(self, max_age_hours: int = 24) -> int:
        """
        清理旧的缓存文件

        Args:
            max_age_hours: 文件最大保留时间（小时）

        Returns:
            int: 删除的文件数量
        """
        import time

        if not self.cache_dir.exists():
            return 0

        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        deleted_count = 0

        for audio_file in list(self.cache_dir.glob("*.wav")) + list(self.cache_dir.glob("*.mp3")):
            try:
                file_age = current_time - audio_file.stat().st_mtime
                if file_age > max_age_seconds:
                    loop = asyncio.get_event_loop()
                    await loop.run_in_executor(None, lambda: audio_file.unlink())
                    deleted_count += 1
                    logger.info(f"[AudioCache] Cleaned up old file: {audio_file}")
            except Exception as e:
                logger.warning(f"[AudioCache] Failed to clean up {audio_file}: {e}")

        if deleted_count > 0:
            logger.info(f"[AudioCache] Cleaned up {deleted_count} old audio files")

        return deleted_count
