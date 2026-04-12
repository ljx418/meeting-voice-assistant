"""Core instance registry for GraphRAG implementations."""

from typing import TYPE_CHECKING, Optional

from .base import GraphRAGCore

if TYPE_CHECKING:
    from .microsoft import MicrosoftGraphRAGAdapter


class GraphRAGRegistry:
    """GraphRAG Core 实现注册表"""

    _instance: Optional[GraphRAGCore] = None

    @classmethod
    def get_instance(cls) -> GraphRAGCore:
        """获取或创建 GraphRAG Core 实例"""
        if cls._instance is None:
            # Import here to avoid circular imports
            from .microsoft import MicrosoftGraphRAGAdapter
            cls._instance = MicrosoftGraphRAGAdapter()
        return cls._instance

    @classmethod
    def set_instance(cls, impl: GraphRAGCore) -> None:
        """设置自定义 GraphRAG Core 实例"""
        cls._instance = impl

    @classmethod
    def reset(cls) -> None:
        """重置注册表（主要用于测试）"""
        cls._instance = None


# 便捷访问函数
def get_core() -> GraphRAGCore:
    """获取 GraphRAG Core 实例"""
    return GraphRAGRegistry.get_instance()
