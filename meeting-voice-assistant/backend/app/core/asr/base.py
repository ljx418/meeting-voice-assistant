"""
ASR 会话基类

定义 ASR 业务的公共接口和通用功能
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional, List
from pathlib import Path
import asyncio
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


# ========== 旧版适配器接口 (向后兼容) ==========

class ASRError(Exception):
    """ASR 异常基类"""
    pass


class ASRInitError(ASRError):
    """ASR 初始化错误"""
    pass


class ASRRecognitionError(ASRError):
    """ASR 识别错误"""
    pass


@dataclass
class ASRResult:
    """
    ASR 识别结果

    Attributes:
        text: 识别文本
        start_time: 开始时间 (秒)
        end_time: 结束时间 (秒)
        speaker: 说话人 ID
        confidence: 置信度 0.0-1.0
        is_final: 是否为最终结果
    """
    text: str
    start_time: float
    end_time: float
    speaker: str = "unknown"
    confidence: float = 1.0
    is_final: bool = True


class ASRAdapterBase(ABC):
    """
    ASR 适配器抽象基类

    定义 ASR 适配器的基本接口
    """

    def __init__(self):
        self._initialized = False

    @property
    def is_initialized(self) -> bool:
        """是否已初始化"""
        return self._initialized

    @abstractmethod
    async def initialize(self) -> None:
        """初始化适配器"""
        pass

    @abstractmethod
    async def close(self) -> None:
        """关闭连接"""
        pass

    @abstractmethod
    async def recognize_stream(
        self,
        audio_stream,
        sample_rate: int = 16000,
        channels: int = 1,
        sample_width: int = 2
    ):
        """
        流式语音识别

        Args:
            audio_stream: 音频流
            sample_rate: 采样率
            channels: 声道数
            sample_width: 采样宽度
        """
        pass

    @abstractmethod
    async def recognize_file(self, file_path: Path):
        """
        识别音频文件

        Args:
            file_path: 音频文件路径
        """
        pass

    @property
    @abstractmethod
    def engine_name(self) -> str:
        """返回引擎名称"""
        pass


@dataclass
class TranscriptionSegment:
    """
    转写片段

    Attributes:
        text: 识别文本
        start_time: 开始时间 (秒)
        end_time: 结束时间 (秒)
        speaker: 说话人 ID
        confidence: 置信度 0.0-1.0
        language: 语种
        is_final: 是否为最终结果
    """
    text: str
    start_time: float
    end_time: float
    speaker: str = "unknown"
    confidence: float = 1.0
    language: str = "zh"
    is_final: bool = True


@dataclass
class TranscriptionResult:
    """
    转写结果

    Attributes:
        session_id: 会话 ID
        transcript: 转写片段列表
        audio_path: 音频文件路径 (如果有)
        duration: 音频时长 (秒)
        language: 主要语种
        created_at: 创建时间
    """
    session_id: str
    transcript: List[TranscriptionSegment] = field(default_factory=list)
    audio_path: Optional[Path] = None
    duration: float = 0.0
    language: str = "zh"
    created_at: datetime = field(default_factory=datetime.now)

    @property
    def full_text(self) -> str:
        """获取完整转写文本"""
        return " ".join(seg.text for seg in self.transcript)

    def add_segment(self, segment: TranscriptionSegment) -> None:
        """添加转写片段"""
        self.transcript.append(segment)


class BaseTranscriber(ABC):
    """
    转写器抽象基类

    定义转写器的基本接口和公共功能
    """

    def __init__(self, session_id: str):
        """
        初始化转写器

        Args:
            session_id: 会话 ID
        """
        self.session_id = session_id
        self._started_at = datetime.now()
        self._segments: List[TranscriptionSegment] = []
        self._audio_chunks: List[bytes] = []
        self._running = False
        logger.info(f"[Transcriber] Initialized: {self.__class__.__name__}, session_id={session_id}")

    @property
    def is_running(self) -> bool:
        """是否正在运行"""
        return self._running

    @property
    def duration(self) -> float:
        """获取当前音频时长"""
        # 假设 16kHz, 16-bit, mono
        total_bytes = sum(len(chunk) for chunk in self._audio_chunks)
        return total_bytes / (16000 * 2)

    @abstractmethod
    async def start(self) -> None:
        """开始转写"""
        pass

    @abstractmethod
    async def process_audio(self, audio_data: bytes) -> None:
        """
        处理音频数据

        Args:
            audio_data: 音频数据 (PCM)
        """
        pass

    @abstractmethod
    async def get_result(self) -> Optional[TranscriptionResult]:
        """
        获取转写结果

        Returns:
            TranscriptionResult 或 None (如果有)
        """
        pass

    @abstractmethod
    async def stop(self) -> TranscriptionResult:
        """
        停止转写并返回最终结果

        Returns:
            TranscriptionResult: 最终转写结果
        """
        pass

    @abstractmethod
    async def cancel(self) -> None:
        """取消转写"""
        pass

    def add_audio_chunk(self, audio_data: bytes) -> None:
        """添加音频块到缓冲区"""
        self._audio_chunks.append(audio_data)

    def get_audio_bytes(self) -> bytes:
        """获取所有音频数据"""
        return b''.join(self._audio_chunks)

    def create_segment(
        self,
        text: str,
        start_time: float = 0,
        end_time: float = 0,
        speaker: str = "unknown",
        confidence: float = 1.0,
        language: str = "zh",
        is_final: bool = True
    ) -> TranscriptionSegment:
        """创建转写片段"""
        return TranscriptionSegment(
            text=text,
            start_time=start_time,
            end_time=end_time,
            speaker=speaker,
            confidence=confidence,
            language=language,
            is_final=is_final
        )

    def build_result(self, audio_path: Optional[Path] = None) -> TranscriptionResult:
        """构建转写结果"""
        return TranscriptionResult(
            session_id=self.session_id,
            transcript=self._segments.copy(),
            audio_path=audio_path,
            duration=self.duration,
            language="zh"
        )
