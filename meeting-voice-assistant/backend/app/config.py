"""
配置管理

支持从 .env 文件加载配置
"""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# 加载 .env 文件
_env_path = Path(__file__).parent / ".env"
if _env_path.exists():
    load_dotenv(_env_path)
    print(f"[Config] Loaded environment from {_env_path}")
else:
    print(f"[Config] .env file not found at {_env_path}")


class Config:
    """应用配置"""

    # ASR 配置
    # 可选值: mock (测试用), aliyun (阿里云), sensevoice (本地部署)
    ASR_ENGINE: str = os.getenv("ASR_ENGINE", "mock")

    # Mock ASR 配置 (用于测试)
    MOCK_ASR_DELAY: float = float(os.getenv("MOCK_ASR_DELAY", "0.8"))

    # 阿里云 ASR 配置
    ALIYUN_ENDPOINT: str = os.getenv("ALIYUN_ENDPOINT", "wss://nls-gateway.cn-shanghai.aliyuncs.com/ws/v1")
    ALIYUN_ACCESS_KEY_ID: Optional[str] = os.getenv("ALIYUN_ACCESS_KEY_ID")
    ALIYUN_ACCESS_KEY_SECRET: Optional[str] = os.getenv("ALIYUN_ACCESS_KEY_SECRET")
    ALIYUN_APP_KEY: Optional[str] = os.getenv("ALIYUN_APP_KEY")
    ALIYUN_REGION: str = os.getenv("ALIYUN_REGION", "cn-shanghai")

    # SenseVoice 本地部署配置
    SENSEVOICE_MODE: str = os.getenv("SENSEVOICE_MODE", "local")
    SENSEVOICE_ENDPOINT: str = os.getenv("SENSEVOICE_ENDPOINT", "http://localhost:8000")
    SENSEVOICE_API_KEY: Optional[str] = os.getenv("SENSEVOICE_API_KEY")

    # DashScope 配置
    DASHSCOPE_ENDPOINT: str = os.getenv("DASHSCOPE_ENDPOINT", "https://dashscope.aliyuncs.com/v1")
    DASHSCOPE_API_KEY: Optional[str] = os.getenv("DASHSCOPE_API_KEY")
    DASHSCOPE_MODEL: str = os.getenv("DASHSCOPE_MODEL", "qwen3-asr-flash")

    # FunASR 本地服务配置
    FUNASR_ENDPOINT: str = os.getenv("FUNASR_ENDPOINT", "http://localhost:8001")
    FUNASR_API_KEY: Optional[str] = os.getenv("FUNASR_API_KEY")
    FUNASR_TIMEOUT: int = int(os.getenv("FUNASR_TIMEOUT", "3600"))

    # LLM 分析配置
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "dashscope")  # dashscope, openai
    LLM_API_KEY: Optional[str] = os.getenv("LLM_API_KEY")
    LLM_ENDPOINT: str = os.getenv("LLM_ENDPOINT", "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "qwen-plus")

    # 音频缓存配置
    AUDIO_CACHE_DIR: Path = Path(os.getenv("AUDIO_CACHE_DIR", "/tmp/openclaw_audio_cache"))
    AUDIO_CACHE_ENABLED: bool = os.getenv("AUDIO_CACHE_ENABLED", "true").lower() == "true"

    # 转写文本保存配置
    TRANSCRIPTS_DIR: Path = Path(__file__).parent.parent / "transcripts"
    TRANSCRIPTS_DIR.mkdir(exist_ok=True)

    # 音频配置
    AUDIO_SAMPLE_RATE: int = int(os.getenv("AUDIO_SAMPLE_RATE", "16000"))
    AUDIO_CHANNELS: int = int(os.getenv("AUDIO_CHANNELS", "1"))
    AUDIO_BUFFER_DURATION: float = float(os.getenv("AUDIO_BUFFER_DURATION", "1.0"))

    # 日志配置
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: Optional[str] = os.getenv("LOG_FILE")


config = Config()
