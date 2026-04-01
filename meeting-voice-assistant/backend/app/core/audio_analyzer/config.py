"""
音频分析模块配置
"""

import os
from pathlib import Path
from typing import Optional
from dataclasses import dataclass
from dotenv import load_dotenv

# 加载 .env 文件（从 backend/app/.env）
_env_path = Path(__file__).parent.parent.parent / ".env"
if _env_path.exists():
    load_dotenv(_env_path)


@dataclass
class LLMConfig:
    """LLM 配置"""
    provider: str  # "minimax" or "deepseek"
    api_key: Optional[str] = None
    endpoint: Optional[str] = None
    model: str = "MiniMax/MiniMax-Text-01"

    # MiniMax 配置
    minimax_api_key: Optional[str] = None
    minimax_endpoint: Optional[str] = None
    minimax_model: str = "MiniMax-Text-01"

    # DeepSeek 配置
    deepseek_api_key: Optional[str] = None
    deepseek_endpoint: Optional[str] = None
    deepseek_model: str = "deepseek-chat"


def get_llm_config() -> LLMConfig:
    """从环境变量获取 LLM 配置"""
    return LLMConfig(
        provider=os.getenv("AUDIO_ANALYZER_LLM_PROVIDER", "minimax"),
        minimax_api_key=os.getenv("MINIMAX_API_KEY"),
        minimax_endpoint=os.getenv("MINIMAX_ENDPOINT", "https://api.minimax.chat/v1"),
        deepseek_api_key=os.getenv("DEEPSEEK_API_KEY"),
        deepseek_endpoint=os.getenv("DEEPSEEK_ENDPOINT", "https://api.deepseek.com"),
    )


# 全局配置实例
_config: Optional[LLMConfig] = None


def get_config() -> LLMConfig:
    """获取全局配置实例"""
    global _config
    if _config is None:
        _config = get_llm_config()
    return _config
