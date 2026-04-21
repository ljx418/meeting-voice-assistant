"""Core instance registry for GraphRAG implementations."""

import uuid
from typing import TYPE_CHECKING, Optional

from .base import GraphRAGCore

if TYPE_CHECKING:
    from .microsoft import MicrosoftGraphRAGAdapter


class GraphRAGRegistry:
    """GraphRAG Core 实现注册表，支持会话隔离"""

    # 单例实例（用于默认/向后兼容）
    _instance: Optional[GraphRAGCore] = None
    # 会话实例池 {session_id: GraphRAGCore}
    _sessions: dict[str, GraphRAGCore] = {}

    @classmethod
    def get_instance(cls, session_id: Optional[str] = None) -> GraphRAGCore:
        """获取或创建 GraphRAG Core 实例

        Args:
            session_id: 会话 ID。如果为 None，使用单例实例（向后兼容）。
                       如果提供，创建/获取该会话的独立实例。
        """
        if session_id is None:
            # 返回单例实例（向后兼容）
            if cls._instance is None:
                from .microsoft import MicrosoftGraphRAGAdapter
                cls._instance = MicrosoftGraphRAGAdapter()
            return cls._instance
        else:
            # 返回或创建会话实例
            if session_id not in cls._sessions:
                from .microsoft import MicrosoftGraphRAGAdapter
                cls._sessions[session_id] = MicrosoftGraphRAGAdapter(session_id=session_id)
            return cls._sessions[session_id]

    @classmethod
    def set_instance(cls, impl: GraphRAGCore, session_id: Optional[str] = None) -> None:
        """设置自定义 GraphRAG Core 实例"""
        if session_id is None:
            cls._instance = impl
        else:
            cls._sessions[session_id] = impl

    @classmethod
    def reset(cls, session_id: Optional[str] = None) -> None:
        """重置注册表（主要用于测试或会话清理）

        Args:
            session_id: 如果为 None，重置单例。如果提供，只清理指定会话。
        """
        if session_id is None:
            cls._instance = None
        else:
            cls._sessions.pop(session_id, None)

    @classmethod
    def clear_all_sessions(cls) -> int:
        """清除所有会话实例，返回清除的数量"""
        count = len(cls._sessions)
        cls._sessions.clear()
        return count


# 便捷访问函数
def get_core(session_id: Optional[str] = None) -> GraphRAGCore:
    """获取 GraphRAG Core 实例

    Args:
        session_id: 会话 ID。如果为 None，使用默认实例。
    """
    return GraphRAGRegistry.get_instance(session_id)
