"""
ASR 适配器工厂

根据配置创建对应的 ASR 适配器实例

使用方式:
    adapter = ASRFactory.create("mock")  # 使用 Mock
    adapter = ASRFactory.create("aliyun")  # 使用阿里云
    adapter = ASRFactory.create()  # 从环境变量读取，默认 mock
"""

from typing import Optional, Type, Callable
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

# 适配器工厂函数类型
AdapterFactory = Callable[[], ASRAdapterBase]


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
    - funasr: FunASR 本地说话人分离
    - funasr_realtime: FunASR 实时语音转写 + 说话人分离
    """

    # 注册的适配器工厂函数映射
    # 每个工厂函数负责创建适配器实例并传递所需配置
    _adapter_factories: dict[str, AdapterFactory] = {}

    @classmethod
    def _init_adapter_factories(cls) -> dict[str, AdapterFactory]:
        """延迟初始化适配器工厂映射"""
        if not cls._adapter_factories:
            cls._adapter_factories = {
                "mock": cls._create_mock,
                "aliyun": cls._create_aliyun,
                "sensevoice": cls._create_sensevoice,
                "dashscope": cls._create_dashscope,
                "dashscope_file": cls._create_dashscope_file,
                "dashscope_realtime": cls._create_dashscope_realtime,
                "funasr": cls._create_funasr,
                "funasr_realtime": cls._create_funasr_realtime,
            }
        return cls._adapter_factories

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
        factories = cls._init_adapter_factories()

        if engine not in factories:
            available = list(factories.keys())
            raise ASRError(
                f"Unknown ASR engine: {engine}. "
                f"Available engines: {available}"
            )

        logger.info(f"[ASR Factory] Creating ASR adapter: {engine}")
        return factories[engine]()

    # 注册的转写器映射 (新架构)
    _transcribers: dict[str, Type[BaseTranscriber]] = {
        "realtime_transcriber": RealtimeTranscriber,
        "file_transcriber": FileTranscriber,
    }

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
            transcriber_type: 转写器类型 ("realtime_transcriber" 或 "file_transcriber")
            session_id: 会话 ID
            **kwargs: 传递给转写器的额外参数

        Returns:
            BaseTranscriber: 转写器实例

        Raises:
            ASRError: 未知的转写器类型
        """
        # 转写器工厂函数映射
        transcriber_factories = {
            "realtime_transcriber": lambda: cls._create_realtime_transcriber(session_id, **kwargs),
            "file_transcriber": lambda: cls._create_file_transcriber(session_id, **kwargs),
        }

        if transcriber_type not in transcriber_factories:
            available = list(transcriber_factories.keys())
            raise ASRError(
                f"Unknown transcriber type: {transcriber_type}. "
                f"Available types: {available}"
            )

        logger.info(f"[ASR Factory] Creating transcriber: {transcriber_type}")
        return transcriber_factories[transcriber_type]()

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
        """创建阿里云适配器 (使用 SenseVoice 兼容模式)"""
        logger.info("[ASR Factory] Using Aliyun ASR (SenseVoice compatibility mode)")
        return SenseVoiceAdapter(
            mode="api",
            endpoint=os.getenv("ALIYUN_ENDPOINT", "wss://nls-gateway.cn-shanghai.aliyuncs.com/ws/v1"),
            api_key=os.getenv("ALIYUN_API_KEY"),
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
    def register(cls, name: str, factory: AdapterFactory) -> None:
        """
        注册新的 ASR 适配器工厂

        用于插件扩展或运行时注册

        Args:
            name: 引擎名称
            factory: 适配器工厂函数
        """
        cls._init_adapter_factories()
        cls._adapter_factories[name] = factory
        logger.info(f"[ASR Factory] Registered ASR adapter factory: {name}")

    @classmethod
    def available_engines(cls) -> list[str]:
        """获取所有可用的引擎名称"""
        return list(cls._init_adapter_factories().keys())

    @classmethod
    def available_transcribers(cls) -> list[str]:
        """获取所有可用的转写器类型"""
        return ["realtime_transcriber", "file_transcriber"]
