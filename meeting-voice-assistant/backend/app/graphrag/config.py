"""
GraphRAG 配置模块

已统一到 app.config.py，通过以下方式使用：
    from app.config import config
    workspace = config.graphrag.workspace
    llm_provider = config.llm.provider

本文件保留用于向后兼容，新代码应直接使用 app.config。
"""

from pathlib import Path
from typing import Optional

# 导入统一配置（延迟导入避免循环依赖）
_config: Optional["GraphRAGConfig"] = None


def get_settings():
    """获取全局 GraphRAG 配置实例（兼容旧接口）"""
    global _config
    if _config is None:
        from app.config import config as _app_config
        _config = _app_config.graphrag
    return _config


# 向后兼容的属性访问
class _CompatSettings:
    """兼容旧接口的属性访问器"""
    @property
    def GRAPHRAG_WORKSPACE(self) -> Path:
        from app.config import config
        return config.graphrag.workspace

    @property
    def LLM_PROVIDER(self) -> str:
        from app.config import config
        return config.llm.provider

    @property
    def LLM_API_KEY(self) -> str:
        from app.config import config
        return self._get_llm_api_key()

    @property
    def LLM_BASE_URL(self) -> str:
        from app.config import config
        return self._get_llm_base_url()

    @property
    def LLM_MODEL(self) -> str:
        from app.config import config
        return self._get_llm_model()

    def _get_llm_api_key(self) -> str:
        from app.config import config
        provider = config.llm.provider
        if provider == "minimax":
            return config.llm.minimax_api_key or ""
        elif provider == "deepseek":
            return config.llm.deepseek_api_key or ""
        elif provider == "dashscope":
            return config.llm.dashscope_api_key or ""
        return ""

    def _get_llm_base_url(self) -> str:
        from app.config import config
        provider = config.llm.provider
        if provider == "minimax":
            return config.llm.minimax_endpoint
        elif provider == "deepseek":
            return config.llm.deepseek_endpoint
        elif provider == "dashscope":
            return config.llm.dashscope_endpoint
        return ""

    def _get_llm_model(self) -> str:
        from app.config import config
        provider = config.llm.provider
        if provider == "minimax":
            return config.llm.minimax_model
        elif provider == "deepseek":
            return config.llm.deepseek_model
        elif provider == "dashscope":
            return config.llm.dashscope_model
        return ""


# 创建兼容对象
_compat_settings = _CompatSettings()

# 为向后兼容保留的别名
settings = _compat_settings
raw_settings = get_settings()
