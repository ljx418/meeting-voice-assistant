"""
音频分析模块配置

已统一到 app.config.py，通过以下方式使用：
    from app.config import config
    llm_config = config.llm  # LLMConfig 实例

本文件保留用于向后兼容，建议逐步迁移到统一配置。
"""

from typing import Optional

# 导入统一配置（延迟导入避免循环依赖）
_config: Optional["LLMConfig"] = None


def get_config():
    """获取全局 LLM 配置实例（兼容旧接口）"""
    global _config
    if _config is None:
        from app.config import config as _app_config
        _config = _app_config.llm
    return _config


def get_llm_config():
    """获取 LLM 配置（兼容旧接口）"""
    return get_config()


# 为向后兼容保留的 LLMConfig 类型提示
class LLMConfig:
    """LLM 配置（兼容性别名，指向统一配置）"""
    pass
