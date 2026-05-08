"""Stable runtime adapter boundary for harnessOS Core.

The gateway should not need to know whether a session is backed by the
lightweight SimpleAgent or by a migrated OpenHarness RuntimeBundle.  This
module keeps those runtime-specific objects behind a small handle.
"""

from __future__ import annotations

import inspect
from dataclasses import dataclass, field
from typing import Any, AsyncIterator, Callable, Dict, Optional, Protocol

from langchain_core.tools import BaseTool

from core.runtime_adapter import create_harness_agent


AgentFactory = Callable[[str], Any]
RuntimeBundleFactory = Callable[[str], Any]
GOVERNANCE_METADATA_KEYS = (
    "session_id",
    "turn_id",
    "trace_id",
    "app_id",
    "project_id",
    "workspace_id",
    "user_input",
    "approval_id",
    "source_turn_id",
    "policy_evaluator",
    "approval_checker",
    "approval_requester",
)


@dataclass
class RuntimeHandle:
    """Opaque runtime handle owned by a RuntimeAdapter implementation."""

    backend: str
    agent: Any = None
    bundle: Any = None
    tool_metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class RuntimeGovernanceContext:
    """Governance metadata injected into runtime tool execution paths."""

    session_id: str
    turn_id: str
    trace_id: str
    app_id: str = "default"
    project_id: Optional[str] = None
    workspace_id: Optional[str] = None
    user_input: str = ""
    approval_id: Optional[str] = None
    source_turn_id: Optional[str] = None
    policy_evaluator: Any = None
    approval_checker: Any = None
    approval_requester: Any = None

    def to_tool_metadata(self) -> dict[str, Any]:
        """Return metadata keys consumed by tool policy middleware."""
        metadata: dict[str, Any] = {
            "session_id": self.session_id,
            "turn_id": self.turn_id,
            "trace_id": self.trace_id,
            "app_id": self.app_id,
            "user_input": self.user_input,
        }
        if self.project_id:
            metadata["project_id"] = self.project_id
        if self.workspace_id:
            metadata["workspace_id"] = self.workspace_id
        if self.approval_id:
            metadata["approval_id"] = self.approval_id
        if self.source_turn_id:
            metadata["source_turn_id"] = self.source_turn_id
        if self.policy_evaluator is not None:
            metadata["policy_evaluator"] = self.policy_evaluator
        if self.approval_checker is not None:
            metadata["approval_checker"] = self.approval_checker
        if self.approval_requester is not None:
            metadata["approval_requester"] = self.approval_requester
        return metadata


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

    async def invoke(
        self,
        handle: RuntimeHandle,
        user_input: str,
        *,
        governance: Optional[RuntimeGovernanceContext] = None,
    ) -> Any:
        """Run one non-streaming user input."""

    def stream(
        self,
        handle: RuntimeHandle,
        user_input: str,
        *,
        governance: Optional[RuntimeGovernanceContext] = None,
    ) -> AsyncIterator[Any]:
        """Stream one user input as runtime-native events."""

    def continue_pending(
        self,
        handle: RuntimeHandle,
        *,
        governance: Optional[RuntimeGovernanceContext] = None,
    ) -> AsyncIterator[Any]:
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

    async def invoke(
        self,
        handle: RuntimeHandle,
        user_input: str,
        *,
        governance: Optional[RuntimeGovernanceContext] = None,
    ) -> Any:
        if handle.agent is None:
            raise RuntimeError("Simple runtime handle has no agent")
        inject_runtime_governance(handle, governance)
        _inject_governance_metadata(handle)
        result = handle.agent.invoke(user_input)
        if inspect.isawaitable(result):
            return await result
        return result

    async def stream(
        self,
        handle: RuntimeHandle,
        user_input: str,
        *,
        governance: Optional[RuntimeGovernanceContext] = None,
    ) -> AsyncIterator[Any]:
        yield await self.invoke(handle, user_input, governance=governance)

    async def continue_pending(
        self,
        handle: RuntimeHandle,
        *,
        governance: Optional[RuntimeGovernanceContext] = None,
    ) -> AsyncIterator[Any]:
        inject_runtime_governance(handle, governance)
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

    async def invoke(
        self,
        handle: RuntimeHandle,
        user_input: str,
        *,
        governance: Optional[RuntimeGovernanceContext] = None,
    ) -> Any:
        del governance
        raise RuntimeError("OpenHarness runtime must be consumed through stream()")

    async def stream(
        self,
        handle: RuntimeHandle,
        user_input: str,
        *,
        governance: Optional[RuntimeGovernanceContext] = None,
    ) -> AsyncIterator[Any]:
        if handle.bundle is None or not hasattr(handle.bundle, "engine"):
            raise RuntimeError("OpenHarness runtime handle has no bundle engine")
        inject_runtime_governance(handle, governance)
        async for runtime_event in handle.bundle.engine.submit_message(user_input):
            yield runtime_event

    async def continue_pending(
        self,
        handle: RuntimeHandle,
        *,
        governance: Optional[RuntimeGovernanceContext] = None,
    ) -> AsyncIterator[Any]:
        if handle.bundle is None or not hasattr(handle.bundle, "engine"):
            return
        inject_runtime_governance(handle, governance)
        async for runtime_event in handle.bundle.engine.continue_pending():
            yield runtime_event


def inject_runtime_governance(
    handle: RuntimeHandle,
    governance: Optional[RuntimeGovernanceContext],
) -> None:
    """Merge per-turn governance metadata into a runtime handle."""
    if governance is None:
        return
    for key in GOVERNANCE_METADATA_KEYS:
        handle.tool_metadata.pop(key, None)
    handle.tool_metadata.update(governance.to_tool_metadata())
    _inject_governance_metadata(handle)


def _inject_governance_metadata(handle: RuntimeHandle) -> None:
    metadata = handle.tool_metadata
    if not metadata:
        return
    if handle.agent is not None:
        existing = getattr(handle.agent, "tool_metadata", None)
        if isinstance(existing, dict):
            for key in GOVERNANCE_METADATA_KEYS:
                existing.pop(key, None)
            existing.update(metadata)
        else:
            setattr(handle.agent, "tool_metadata", dict(metadata))
    bundle = handle.bundle
    engine = getattr(bundle, "engine", None) if bundle is not None else None
    if engine is not None:
        existing = getattr(engine, "tool_metadata", None)
        if isinstance(existing, dict):
            for key in GOVERNANCE_METADATA_KEYS:
                existing.pop(key, None)
            existing.update(metadata)
        else:
            setattr(engine, "tool_metadata", dict(metadata))


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
