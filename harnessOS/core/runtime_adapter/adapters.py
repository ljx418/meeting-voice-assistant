"""Stable runtime adapter boundary for harnessOS Core.

The gateway should not need to know whether a session is backed by the
lightweight SimpleAgent or by a migrated OpenHarness RuntimeBundle.  This
module keeps those runtime-specific objects behind a small handle.
"""

from __future__ import annotations

import inspect
from dataclasses import dataclass
from typing import Any, AsyncIterator, Callable, Dict, Optional, Protocol

from langchain_core.tools import BaseTool

from core.runtime_adapter import create_harness_agent


AgentFactory = Callable[[str], Any]
RuntimeBundleFactory = Callable[[str], Any]


@dataclass
class RuntimeHandle:
    """Opaque runtime handle owned by a RuntimeAdapter implementation."""

    backend: str
    agent: Any = None
    bundle: Any = None


class RuntimeAdapter(Protocol):
    """Runtime implementation contract used by Gateway/Core callers."""

    backend: str

    async def start(
        self,
        *,
        model: str,
        restore_messages: Optional[list[Dict[str, Any]]] = None,
    ) -> RuntimeHandle:
        """Start a runtime session and return an opaque handle."""

    async def close(self, handle: RuntimeHandle) -> None:
        """Close a runtime session handle."""

    async def invoke(self, handle: RuntimeHandle, user_input: str) -> Any:
        """Run one non-streaming user input."""

    def stream(self, handle: RuntimeHandle, user_input: str) -> AsyncIterator[Any]:
        """Stream one user input as runtime-native events."""

    def continue_pending(self, handle: RuntimeHandle) -> AsyncIterator[Any]:
        """Continue a pending runtime-native turn when supported."""


class SimpleRuntimeAdapter:
    """Adapter for the local SimpleAgent/deepagents-compatible invocation path."""

    backend = "simple"

    def __init__(
        self,
        *,
        agent_factory: Optional[AgentFactory] = None,
        tools: Optional[list[BaseTool]] = None,
    ) -> None:
        self._agent_factory = agent_factory
        self._tools = tools

    async def start(
        self,
        *,
        model: str,
        restore_messages: Optional[list[Dict[str, Any]]] = None,
    ) -> RuntimeHandle:
        agent = self._create_agent(model)
        if restore_messages is not None and hasattr(agent, "messages"):
            agent.messages = list(restore_messages)
        return RuntimeHandle(backend=self.backend, agent=agent)

    async def close(self, handle: RuntimeHandle) -> None:
        return None

    async def invoke(self, handle: RuntimeHandle, user_input: str) -> Any:
        if handle.agent is None:
            raise RuntimeError("Simple runtime handle has no agent")
        result = handle.agent.invoke(user_input)
        if inspect.isawaitable(result):
            return await result
        return result

    async def stream(self, handle: RuntimeHandle, user_input: str) -> AsyncIterator[Any]:
        yield await self.invoke(handle, user_input)

    async def continue_pending(self, handle: RuntimeHandle) -> AsyncIterator[Any]:
        if False:
            yield None

    def _create_agent(self, model: str) -> Any:
        if self._agent_factory is not None:
            return self._agent_factory(model)
        return create_harness_agent(model=model, tools=self._tools)


class OpenHarnessRuntimeAdapter:
    """Adapter for the migrated OpenHarness RuntimeBundle path."""

    backend = "openharness"

    def __init__(
        self,
        *,
        runtime_factory: Optional[RuntimeBundleFactory] = None,
    ) -> None:
        self._runtime_factory = runtime_factory

    async def start(
        self,
        *,
        model: str,
        restore_messages: Optional[list[Dict[str, Any]]] = None,
    ) -> RuntimeHandle:
        if self._runtime_factory is not None:
            created = self._runtime_factory(model)
            bundle = await created if inspect.isawaitable(created) else created
            return RuntimeHandle(backend=self.backend, bundle=bundle)

        from cli.tui.runtime import build_runtime, start_runtime

        bundle = await build_runtime(
            model=model,
            restore_messages=restore_messages or [],
            enforce_max_turns=False,
        )
        await start_runtime(bundle)
        return RuntimeHandle(backend=self.backend, bundle=bundle)

    async def close(self, handle: RuntimeHandle) -> None:
        if handle.bundle is None:
            return
        from cli.tui.runtime import close_runtime

        await close_runtime(handle.bundle)

    async def invoke(self, handle: RuntimeHandle, user_input: str) -> Any:
        raise RuntimeError("OpenHarness runtime must be consumed through stream()")

    async def stream(self, handle: RuntimeHandle, user_input: str) -> AsyncIterator[Any]:
        if handle.bundle is None or not hasattr(handle.bundle, "engine"):
            raise RuntimeError("OpenHarness runtime handle has no bundle engine")
        async for runtime_event in handle.bundle.engine.submit_message(user_input):
            yield runtime_event

    async def continue_pending(self, handle: RuntimeHandle) -> AsyncIterator[Any]:
        if handle.bundle is None or not hasattr(handle.bundle, "engine"):
            return
        async for runtime_event in handle.bundle.engine.continue_pending():
            yield runtime_event


def snapshot_messages(handle: Optional[RuntimeHandle]) -> list[Any]:
    """Return portable messages from a runtime handle for snapshot persistence."""
    if handle is None:
        return []
    if handle.agent is not None:
        return list(getattr(handle.agent, "messages", []) or [])
    bundle = handle.bundle
    if bundle is not None and hasattr(bundle, "engine"):
        return [
            message.model_dump(mode="json") if hasattr(message, "model_dump") else message
            for message in getattr(bundle.engine, "messages", []) or []
        ]
    return []
