"""
配置管理 - 统一配置入口

使用 pydantic_settings 统一管理所有配置，支持：
- 环境变量自动加载
- 类型安全验证
- 分组配置访问

使用方式:
    from app.config import config

    # 访问配置
    engine = config.asr.engine
    llm_model = config.llm.model
"""

import logging
from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

_logger = logging.getLogger("config")


class ASRConfig(BaseSettings):
    """ASR 引擎配置"""

    engine: str = Field(default="mock", description="ASR 引擎: mock, aliyun, sensevoice, dashscope, dashscope_file, dashscope_realtime, funasr, funasr_realtime")

    # Mock ASR 配置
    mock_delay: float = Field(default=0.8, description="Mock ASR 延迟（秒）")

    # 阿里云 ASR 配置
    aliyun_endpoint: str = Field(default="wss://nls-gateway.cn-shanghai.aliyuncs.com/ws/v1")
    aliyun_access_key_id: Optional[str] = Field(default=None)
    aliyun_access_key_secret: Optional[str] = Field(default=None)
    aliyun_app_key: Optional[str] = Field(default=None)
    aliyun_region: str = Field(default="cn-shanghai")

    # SenseVoice 本地部署配置
    sensevoice_mode: str = Field(default="local")
    sensevoice_endpoint: str = Field(default="http://localhost:8000")
    sensevoice_api_key: Optional[str] = Field(default=None)

    # DashScope 配置
    dashscope_endpoint: str = Field(default="https://dashscope.aliyuncs.com/v1")
    dashscope_api_key: Optional[str] = Field(default=None)
    dashscope_model: str = Field(default="qwen3-asr-flash")

    # FunASR 本地服务配置
    funasr_endpoint: str = Field(default="http://localhost:8001")
    funasr_api_key: Optional[str] = Field(default=None)
    funasr_timeout: int = Field(default=3600)

    # FunASR 实时识别配置
    funasr_chunk_duration: float = Field(default=3.0, description="每块音频时长（秒）")
    funasr_min_chunk_duration: float = Field(default=1.0, description="最小音频块时长")
    funasr_max_buffer_duration: float = Field(default=10.0, description="最大缓冲时长")
    funasr_ws_url: str = Field(default="ws://localhost:10096", description="FunASR WebSocket 服务地址")
    funasr_realtime_mode: str = Field(default="2pass", description="实时识别模式: online, 2pass")
    funasr_max_file_size_mb: int = Field(default=500, description="FunASR 文件大小限制 (MB)")

    model_config = SettingsConfigDict(
        env_prefix="ASR_",
        extra="ignore",
        env_file=Path(__file__).parent / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


class LLMConfig(BaseSettings):
    """LLM 分析配置"""

    provider: str = Field(default="dashscope", description="LLM 提供商: dashscope, minimax, deepseek")

    # DashScope LLM 配置
    dashscope_api_key: Optional[str] = Field(default=None)
    dashscope_endpoint: str = Field(default="https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation")
    dashscope_model: str = Field(default="qwen-plus")

    # MiniMax LLM 配置
    minimax_api_key: Optional[str] = Field(default=None)
    minimax_endpoint: str = Field(default="https://api.minimax.chat/v1")
    minimax_model: str = Field(default="MiniMax-Text-01")

    # DeepSeek LLM 配置
    deepseek_api_key: Optional[str] = Field(default=None)
    deepseek_endpoint: str = Field(default="https://api.deepseek.com")
    deepseek_model: str = Field(default="deepseek-chat")

    # 音频分析器 LLM 提供商
    audio_analyzer_provider: str = Field(default="minimax", description="音频分析器 LLM: minimax, deepseek")

    model_config = SettingsConfigDict(
        env_prefix="LLM_",
        extra="ignore",
        env_file=Path(__file__).parent / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


class AudioConfig(BaseSettings):
    """音频配置"""

    sample_rate: int = Field(default=16000)
    channels: int = Field(default=1)
    buffer_duration: float = Field(default=1.0)

    model_config = SettingsConfigDict(env_prefix="AUDIO_", extra="ignore")


class CacheConfig(BaseSettings):
    """缓存配置"""

    enabled: bool = Field(default=True)
    cache_dir: Path = Field(default=Path("/tmp/openclaw_audio_cache"))

    model_config = SettingsConfigDict(env_prefix="AUDIO_CACHE_", extra="ignore")


class GraphRAGConfig(BaseSettings):
    """GraphRAG 知识管理配置"""

    auto_index: bool = Field(default=False, description="会议结束后自动触发索引")
    service_url: str = Field(default="http://localhost:8002")
    service_port: int = Field(default=8002, description="GraphRAG 服务端口")
    workspace: Path = Field(default=Path("./rag_workspace"))
    request_timeout: float = Field(default=30.0, description="GraphRAG 服务请求超时（秒）")
    index_timeout: float = Field(default=300.0, description="GraphRAG 索引超时（秒）")
    default_top_k: int = Field(default=10, description="默认返回结果数")

    model_config = SettingsConfigDict(env_prefix="GRAPHRAG_", extra="ignore")


class APIConfig(BaseSettings):
    """API 服务配置"""

    api_key: Optional[str] = Field(default=None, description="静态 API Key 认证，留空=禁用")
    log_level: str = Field(default="INFO")
    log_file: Optional[str] = Field(default=None)

    model_config = SettingsConfigDict(env_prefix="", extra="ignore")


class JWTConfig(BaseSettings):
    """JWT 认证配置"""

    secret_key: str = Field(default="your-super-secret-key-change-in-production", description="JWT 签名密钥")
    algorithm: str = Field(default="HS256", description="JWT 加密算法")
    access_token_expire_minutes: int = Field(default=60, description="访问令牌过期时间（分钟）")
    refresh_token_expire_days: int = Field(default=7, description="刷新令牌过期时间（天）")

    # 开发模式配置
    dev_mode: bool = Field(default=False, description="开发模式开关")
    dev_user_id: Optional[str] = Field(default=None, description="开发模式默认用户 ID")
    dev_bypass_auth: bool = Field(default=False, description="开发模式跳过认证")

    model_config = SettingsConfigDict(
        env_prefix="JWT_",
        extra="ignore",
        env_file=Path(__file__).parent / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


class TimeoutConfig(BaseSettings):
    """超时配置"""

    # WebSocket 超时
    ws_connect_timeout: float = Field(default=10.0, description="WebSocket 连接超时（秒）")
    ws_idle_timeout: float = Field(default=300.0, description="WebSocket 空闲超时（秒）")

    # ASR 超时
    asr_timeout: float = Field(default=60.0, description="ASR 单次请求超时（秒）")
    asr_file_timeout: float = Field(default=600.0, description="ASR 文件识别超时（秒）")

    # LLM 超时
    llm_timeout: float = Field(default=120.0, description="LLM API 调用超时（秒）")

    # GraphRAG 超时
    graphrag_timeout: float = Field(default=30.0, description="GraphRAG 服务请求超时（秒）")
    graphrag_index_timeout: float = Field(default=300.0, description="GraphRAG 索引超时（秒）")

    # 文件上传超时
    upload_timeout: float = Field(default=600.0, description="文件上传处理超时（秒）")

    model_config = SettingsConfigDict(env_prefix="TIMEOUT_", extra="ignore")


class WatchFolderConfig(BaseSettings):
    """文件夹监听配置"""

    path: Optional[str] = Field(default=None, description="监听文件夹路径（必填）")
    enabled: bool = Field(default=False, description="是否启用文件夹监听")
    auto_index_on_change: bool = Field(default=True, description="文件变化时自动触发索引")

    model_config = SettingsConfigDict(
        env_prefix="WATCH_FOLDER_",
        extra="ignore",
        env_file=Path(__file__).parent / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


class AppSettings(BaseSettings):
    """应用统一配置"""

    # 路径配置
    backend_dir: Path = Field(default=Path(__file__).parent.parent)
    transcripts_dir: Path = Field(default=Path(__file__).parent.parent / "transcripts")
    workspace_output_dir: Path = Field(default=Path(__file__).parent.parent.parent / "workspace" / "output")

    # 配置分组
    asr: ASRConfig = Field(default_factory=ASRConfig)
    llm: LLMConfig = Field(default_factory=LLMConfig)
    audio: AudioConfig = Field(default_factory=AudioConfig)
    cache: CacheConfig = Field(default_factory=CacheConfig)
    graphrag: GraphRAGConfig = Field(default_factory=GraphRAGConfig)
    api: APIConfig = Field(default_factory=APIConfig)
    timeout: TimeoutConfig = Field(default_factory=TimeoutConfig)
    watch_folder: WatchFolderConfig = Field(default_factory=WatchFolderConfig)
    jwt: JWTConfig = Field(default_factory=JWTConfig)

    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )


# 全局配置实例
config = AppSettings()

# 初始化日志
if config.api.log_level:
    logging.getLogger().setLevel(getattr(logging, config.api.log_level.upper(), logging.INFO))

# 确保必要目录存在
config.transcripts_dir.mkdir(exist_ok=True)
config.workspace_output_dir.mkdir(parents=True, exist_ok=True)
if config.cache.enabled:
    config.cache.cache_dir.mkdir(parents=True, exist_ok=True)

_logger.info(f"[Config] 统一配置加载完成")
_logger.info(f"[Config] ASR 引擎: {config.asr.engine}")
_logger.info(f"[Config] LLM 提供商: {config.llm.provider}")
_logger.info(f"[Config] GraphRAG 自动索引: {config.graphrag.auto_index}")
