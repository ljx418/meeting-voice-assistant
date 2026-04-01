"""
ASR 适配器工厂

根据配置创建对应的 ASR 适配器实例

使用方式:
    adapter = ASRFactory.create("mock")  # 使用 Mock
    adapter = ASRFactory.create("aliyun")  # 使用阿里云
    adapter = ASRFactory.create()  # 从环境变量读取，默认 mock
"""

from typing import Optional, Type
import os
import logging

from .base import ASRAdapterBase, ASRError
from .base import BaseTranscriber
from .mock import MockASRAdapter
from .sensevoice import SenseVoiceAdapter
from .dashscope import DashScopeASRAdapter
from .dashscope_file import DashScopeFileASRAdapter
from .realtime import DashScopeRealtimeASRAdapter
from .funasr_adapter import FunASRAdapter
from .realtime_transcriber import RealtimeTranscriber
from .file_transcriber import FileTranscriber
from ..realtime_spk import RealtimeSpkTranscriber

logger = logging.getLogger(__name__)


class ASRFactory:
    """
    ASR 适配器工厂类

    支持的引擎:
    - mock: Mock 模拟器 (默认，用于测试)
    - aliyun: 阿里云智能语音交互服务
    - sensevoice: SenseVoice 本地部署
    - dashscope: DashScope Qwen3-ASR-Flash (文件识别，最大6MB)
    - dashscope_file: DashScope 大文件识别 (最大512MB)
    - dashscope_realtime: DashScope 实时语音识别 (WebSocket 流式)
    - whisper: OpenAI Whisper (预留)
    """

    # 注册的适配器映射
    _adapters: dict[str, Type[ASRAdapterBase]] = {
        "mock": MockASRAdapter,
        "aliyun": SenseVoiceAdapter,  # TODO: 后续替换为 AliyunAdapter
        "sensevoice": SenseVoiceAdapter,
        "dashscope": DashScopeASRAdapter,
        "dashscope_file": DashScopeFileASRAdapter,
        "dashscope_realtime": DashScopeRealtimeASRAdapter,
        "funasr": FunASRAdapter,  # FunASR 本地说话人分离
        "funasr_realtime": None,  # FunASR 实时转写 + 说话人分离（使用 RealtimeSpkTranscriber）
        # 预留: 方便后续添加新的 ASR 引擎
        # "whisper": WhisperAdapter,
    }

    # 注册的转写器映射 (新架构)
    _transcribers: dict[str, Type[BaseTranscriber]] = {
        "realtime_transcriber": RealtimeTranscriber,
        "file_transcriber": FileTranscriber,
    }

    @classmethod
    def create(cls, engine: Optional[str] = None) -> ASRAdapterBase:
        """
        创建 ASR 适配器实例

        Args:
            engine: 引擎名称，默认从环境变量 ASR_ENGINE 获取

        Returns:
            ASRAdapterBase: ASR 适配器实例

        Raises:
            ASRError: 未知的引擎名称
        """
        engine = engine or os.getenv("ASR_ENGINE", "mock")

        if engine not in cls._adapters:
            available = list(cls._adapters.keys())
            raise ASRError(
                f"Unknown ASR engine: {engine}. "
                f"Available engines: {available}"
            )

        adapter_class = cls._adapters[engine]
        logger.info(f"[ASR Factory] Creating ASR adapter: {engine}")

        # 根据引擎类型传递不同配置
        if engine == "mock":
            return cls._create_mock()
        elif engine == "aliyun":
            return cls._create_aliyun()
        elif engine == "sensevoice":
            return cls._create_sensevoice()
        elif engine == "dashscope":
            return cls._create_dashscope()
        elif engine == "dashscope_file":
            return cls._create_dashscope_file()
        elif engine == "dashscope_realtime":
            return cls._create_dashscope_realtime()
        elif engine == "funasr":
            return cls._create_funasr()
        elif engine == "funasr_realtime":
            return cls._create_funasr_realtime()

        return adapter_class()

    @classmethod
    def create_transcriber(
        cls,
        transcriber_type: str,
        session_id: str,
        **kwargs
    ) -> BaseTranscriber:
        """
        创建转写器实例 (新架构)

        Args:
            transcriber_type: 转写器类型 ("realtime" 或 "file")
            session_id: 会话 ID
            **kwargs: 传递给转写器的额外参数

        Returns:
            BaseTranscriber: 转写器实例

        Raises:
            ASRError: 未知的转写器类型
        """
        if transcriber_type not in cls._transcribers:
            available = list(cls._transcribers.keys())
            raise ASRError(
                f"Unknown transcriber type: {transcriber_type}. "
                f"Available types: {available}"
            )

        transcriber_class = cls._transcribers[transcriber_type]
        logger.info(f"[ASR Factory] Creating transcriber: {transcriber_type}")

        if transcriber_type == "realtime_transcriber":
            return cls._create_realtime_transcriber(session_id, **kwargs)
        elif transcriber_type == "file_transcriber":
            return cls._create_file_transcriber(session_id, **kwargs)

        return transcriber_class(session_id=session_id, **kwargs)

    @classmethod
    def _create_realtime_transcriber(cls, session_id: str, **kwargs) -> RealtimeTranscriber:
        """创建实时转写器"""
        logger.info("[ASR Factory] Using RealtimeTranscriber (qwen3-asr-flash streaming with VAD)")
        return RealtimeTranscriber(
            session_id=session_id,
            api_key=os.getenv("DASHSCOPE_API_KEY"),
            model=kwargs.get("model", "qwen3-asr-flash"),
            language=kwargs.get("language", "zh"),
            max_segment_duration=kwargs.get("max_segment_duration", 10.0),
            min_segment_duration=kwargs.get("min_segment_duration", 1.0)
        )

    @classmethod
    def _create_file_transcriber(cls, session_id: str, **kwargs) -> FileTranscriber:
        """创建文件转写器"""
        logger.info("[ASR Factory] Using FileTranscriber (qwen3-asr-flash-filetrans)")
        return FileTranscriber(
            session_id=session_id,
            api_key=os.getenv("DASHSCOPE_API_KEY"),
            model=kwargs.get("model", "qwen3-asr-flash-filetrans"),
            language=kwargs.get("language", "zh"),
            max_wait=kwargs.get("max_wait", 300)
        )

    @classmethod
    def _create_mock(cls) -> MockASRAdapter:
        """创建 Mock 适配器"""
        logger.info("[ASR Factory] Using Mock ASR (for testing)")
        return MockASRAdapter(
            delay=float(os.getenv("MOCK_ASR_DELAY", "0.8")),
        )

    @classmethod
    def _create_aliyun(cls) -> SenseVoiceAdapter:
        """创建阿里云适配器"""
        # TODO: 后续替换为 AliyunAdapter
        logger.info("[ASR Factory] Using Aliyun ASR (SenseVoice adapter placeholder)")
        return SenseVoiceAdapter(
            mode="api",  # 切换到 API 模式
            endpoint=os.getenv("ALIYUN_ENDPOINT", "wss://nls-gateway.cn-shanghai.aliyuncs.com/ws/v1"),
            api_key=os.getenv("ALIYUN_API_KEY"),  # Token
        )

    @classmethod
    def _create_sensevoice(cls) -> SenseVoiceAdapter:
        """创建 SenseVoice 本地部署适配器"""
        return SenseVoiceAdapter(
            mode=os.getenv("SENSEVOICE_MODE", "local"),
            endpoint=os.getenv("SENSEVOICE_ENDPOINT", "http://localhost:8000"),
            api_key=os.getenv("SENSEVOICE_API_KEY"),
        )

    @classmethod
    def _create_dashscope(cls) -> DashScopeASRAdapter:
        """创建 DashScope 适配器 (用于文件识别)"""
        logger.info("[ASR Factory] Using DashScope ASR (file transcription)")
        return DashScopeASRAdapter(
            endpoint=os.getenv("DASHSCOPE_ENDPOINT", "https://dashscope.aliyuncs.com/api/v1/services/audio/asr"),
            api_key=os.getenv("DASHSCOPE_API_KEY"),
            model=os.getenv("DASHSCOPE_MODEL", "qwen3-asr-flash")
        )

    @classmethod
    def _create_dashscope_file(cls) -> DashScopeFileASRAdapter:
        """创建 DashScope 大文件识别适配器 (支持最大 512MB+)"""
        logger.info("[ASR Factory] Using DashScope File ASR (qwen3-asr-flash-filetrans, large file)")
        return DashScopeFileASRAdapter(
            api_key=os.getenv("DASHSCOPE_API_KEY"),
            model="qwen3-asr-flash-filetrans"
        )

    @classmethod
    def _create_dashscope_realtime(cls):
        """创建 DashScope 实时语音识别适配器 (使用新的 RealtimeTranscriber with VAD)"""
        logger.info("[ASR Factory] Using DashScope Realtime ASR (qwen3-asr-flash streaming with VAD)")
        return RealtimeTranscriber(
            session_id="temp",  # 临时，VoiceSession 会用真实的 session_id
            api_key=os.getenv("DASHSCOPE_API_KEY"),
            model="qwen3-asr-flash",
            language="zh",
            max_segment_duration=10.0,
            min_segment_duration=1.0
        )

    @classmethod
    def _create_funasr(cls) -> FunASRAdapter:
        """创建 FunASR 说话人分离适配器"""
        logger.info("[ASR Factory] Using FunASR (local speaker diarization)")
        return FunASRAdapter(
            endpoint=os.getenv("FUNASR_ENDPOINT", "http://localhost:8001"),
            timeout=int(os.getenv("FUNASR_TIMEOUT", "3600")),
        )

    @classmethod
    def _create_funasr_realtime(cls):
        """创建 FunASR 实时语音转写 + 说话人分离适配器"""
        logger.info("[ASR Factory] Using FunASR Realtime (streaming + speaker diarization)")
        return RealtimeSpkTranscriber(
            session_id="temp",  # 临时，VoiceSession 会用真实的 session_id
            funasr_endpoint=os.getenv("FUNASR_ENDPOINT", "http://localhost:8001"),
            chunk_duration=float(os.getenv("FUNASR_CHUNK_DURATION", "3.0")),
            min_chunk_duration=float(os.getenv("FUNASR_MIN_CHUNK_DURATION", "1.0")),
            max_buffer_duration=float(os.getenv("FUNASR_MAX_BUFFER_DURATION", "10.0")),
        )

    @classmethod
    def register(cls, name: str, adapter_class: Type[ASRAdapterBase]) -> None:
        """
        注册新的 ASR 适配器

        用于插件扩展或运行时注册

        Args:
            name: 引擎名称
            adapter_class: 适配器类
        """
        if not issubclass(adapter_class, ASRAdapterBase):
            raise TypeError(
                f"Adapter class must inherit from ASRAdapterBase, "
                f"got {adapter_class}"
            )

        cls._adapters[name] = adapter_class
        logger.info(f"[ASR Factory] Registered ASR adapter: {name}")

    @classmethod
    def available_engines(cls) -> list[str]:
        """获取所有可用的引擎名称"""
        return list(cls._adapters.keys())

    @classmethod
    def available_transcribers(cls) -> list[str]:
        """获取所有可用的转写器类型"""
        return list(cls._transcribers.keys())
