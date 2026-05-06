"""
Runtime adapter for harnessOS.
Tries to use Deep Agents, falls back to simple runtime for Phase 0.
"""

import os
from typing import Optional, Sequence

from langchain_core.tools import BaseTool


def create_harness_agent(
    model: str = "deepseek/deepseek-chat",
    tools: Optional[Sequence[BaseTool]] = None,
):
    """Create a harnessOS agent.

    Attempts to use Deep Agents, falls back to simple runtime.

    Args:
        model: Model identifier (default: deepseek/deepseek-chat)
        tools: List of tools to expose to the agent

    Returns:
        Agent instance
    """
    try:
        from deepagents import create_deep_agent
        from deepagents.backends import StateBackend
        from langchain_openai import ChatOpenAI

        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            raise ValueError("DEEPSEEK_API_KEY not set")

        base_url = os.getenv("OPENAI_BASE_URL") or "https://api.deepseek.com/v1"

        llm = ChatOpenAI(
            model=model,
            api_key=api_key,
            base_url=base_url,
            temperature=0.7,
        )

        backend = StateBackend()

        return create_deep_agent(
            model=llm,
            tools=list(tools) if tools else [],
            backend=backend,
            name="harnessos-lead",
        )

    except (ImportError, ValueError):
        # Fall back to simple runtime - use relative import
        from core.runtime_adapter.simple_runtime import create_simple_agent
        return create_simple_agent(model=model, tools=tools)


def create_harness_agent_with_minimax(
    model: str = "MiniMax-M2.1",
    tools: Optional[Sequence[BaseTool]] = None,
):
    """Create a harnessOS agent using MiniMax LLM.

    Args:
        model: Model identifier (default: MiniMax-M2.1)
        tools: List of tools to expose to the agent

    Returns:
        Agent instance
    """
    try:
        from deepagents import create_deep_agent
        from deepagents.backends import StateBackend
        from langchain_openai import ChatOpenAI

        api_key = os.getenv("MINIMAX_API_KEY")
        if not api_key:
            raise ValueError("MINIMAX_API_KEY not set")

        base_url = os.getenv("MINIMAX_BASE_URL") or "https://api.minimax.chat/v1"

        llm = ChatOpenAI(
            model=model,
            api_key=api_key,
            base_url=base_url,
            temperature=0.7,
        )

        backend = StateBackend()

        return create_deep_agent(
            model=llm,
            tools=list(tools) if tools else [],
            backend=backend,
            name="harnessos-lead",
        )

    except (ImportError, ValueError):
        # Fall back to simple runtime - use relative import
        from core.runtime_adapter.simple_runtime import create_simple_agent
        return create_simple_agent(model=model, tools=tools)


from core.runtime_adapter.adapters import (  # noqa: E402
    OpenHarnessRuntimeAdapter,
    RuntimeAdapter,
    RuntimeGovernanceContext,
    RuntimeHandle,
    SimpleRuntimeAdapter,
    inject_runtime_governance,
    snapshot_messages,
)

__all__ = [
    "OpenHarnessRuntimeAdapter",
    "RuntimeAdapter",
    "RuntimeGovernanceContext",
    "RuntimeHandle",
    "SimpleRuntimeAdapter",
    "create_harness_agent",
    "create_harness_agent_with_minimax",
    "inject_runtime_governance",
    "snapshot_messages",
]
