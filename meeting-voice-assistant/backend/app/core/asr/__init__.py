"""
ASR 适配器模块

提供统一的 ASR 接口，支持多种语音识别引擎

使用示例:
    from app.core.asr import ASRFactory, ASRAdapterBase

    # 创建适配器 (默认 mock)
    adapter = ASRFactory.create()

    # 或指定引擎
    adapter = ASRFactory.create("mock")  # Mock 测试
    adapter = ASRFactory.create("aliyun")  # 阿里云

    # 初始化
    await adapter.initialize()

    # 流式识别
    async for result in adapter.recognize_stream(audio_stream):
        print(result.text)
"""

from .base import ASRAdapterBase, ASRResult, ASRError, ASRInitError, ASRRecognitionError
from .base import BaseTranscriber, TranscriptionSegment, TranscriptionResult
from .mock import MockASRAdapter
from .sensevoice import SenseVoiceAdapter
from .dashscope import DashScopeASRAdapter
from .factory import ASRFactory
from .realtime_transcriber import RealtimeTranscriber
from .file_transcriber import FileTranscriber

__all__ = [
    # Old adapter pattern
    "ASRAdapterBase",
    "ASRResult",
    "ASRError",
    "ASRInitError",
    "ASRRecognitionError",
    "MockASRAdapter",
    "SenseVoiceAdapter",
    "DashScopeASRAdapter",
    "ASRFactory",
    # New transcriber pattern
    "BaseTranscriber",
    "TranscriptionSegment",
    "TranscriptionResult",
    "RealtimeTranscriber",
    "FileTranscriber",
]
