from __future__ import annotations

import asyncio
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from apps.gateway.runtime import GatewayRuntimePool
from apps.gateway.storage import GatewaySessionStore
from core.runtime_adapter import OpenHarnessRuntimeAdapter, RuntimeGovernanceContext, SimpleRuntimeAdapter


class FakeAgent:
    def __init__(self) -> None:
        self.messages = []

    def invoke(self, user_input: str):
        self.messages.append({"role": "user", "content": user_input})
        return {"status": "success", "content": f"agent: {user_input}"}


class AssistantTextDelta:
    text = "hello"


class AssistantTurnComplete:
    message = None
    usage = None


class FakeBundleEngine:
    def __init__(self) -> None:
        self.messages = [{"role": "user", "content": "restored"}]
        self.tool_metadata = {"existing": "keep"}

    async def submit_message(self, user_input: str):
        event = AssistantTextDelta()
        event.text = f"bundle: {user_input}"
        yield event
        yield AssistantTurnComplete()

    async def continue_pending(self):
        event = AssistantTextDelta()
        event.text = "continued"
        yield event
        yield AssistantTurnComplete()


class FakeBundle:
    def __init__(self) -> None:
        self.engine = FakeBundleEngine()


def test_simple_runtime_adapter_invokes_agent():
    async def run():
        adapter = SimpleRuntimeAdapter(agent_factory=lambda _model: FakeAgent())
        handle = await adapter.start(
            model="fake-model",
            restore_messages=[{"role": "assistant", "content": "old"}],
        )

        result = await adapter.invoke(handle, "hello")

        assert handle.backend == "simple"
        assert handle.agent.messages[0]["content"] == "old"
        assert result["content"] == "agent: hello"

    asyncio.run(run())


def test_simple_runtime_adapter_injects_governance_metadata():
    async def run():
        adapter = SimpleRuntimeAdapter(agent_factory=lambda _model: FakeAgent())
        handle = await adapter.start(model="fake-model", restore_messages=[])
        governance = RuntimeGovernanceContext(
            session_id="sess_meta",
            turn_id="turn_meta",
            trace_id="trace_meta",
            app_id="meeting",
            project_id="project_a",
            workspace_id="workspace_a",
            policy_evaluator=object(),
            approval_checker=lambda _approval_id: True,
        )

        await adapter.invoke(handle, "hello", governance=governance)

        assert handle.agent.tool_metadata["session_id"] == "sess_meta"
        assert handle.agent.tool_metadata["turn_id"] == "turn_meta"
        assert handle.agent.tool_metadata["trace_id"] == "trace_meta"
        assert handle.agent.tool_metadata["app_id"] == "meeting"
        assert handle.agent.tool_metadata["project_id"] == "project_a"
        assert handle.agent.tool_metadata["workspace_id"] == "workspace_a"
        assert "policy_evaluator" in handle.agent.tool_metadata
        assert callable(handle.agent.tool_metadata["approval_checker"])

    asyncio.run(run())


def test_openharness_runtime_adapter_streams_bundle_events():
    async def run():
        adapter = OpenHarnessRuntimeAdapter(runtime_factory=lambda _model: FakeBundle())
        handle = await adapter.start(model="fake-model", restore_messages=[])

        events = [event async for event in adapter.stream(handle, "hello")]
        continued = [event async for event in adapter.continue_pending(handle)]

        assert handle.backend == "openharness"
        assert events[0].text == "bundle: hello"
        assert type(events[-1]).__name__ == "AssistantTurnComplete"
        assert continued[0].text == "continued"

    asyncio.run(run())


def test_openharness_runtime_adapter_injects_governance_metadata():
    async def run():
        adapter = OpenHarnessRuntimeAdapter(runtime_factory=lambda _model: FakeBundle())
        handle = await adapter.start(model="fake-model", restore_messages=[])
        governance = RuntimeGovernanceContext(
            session_id="sess_bundle",
            turn_id="turn_bundle",
            trace_id="trace_bundle",
            policy_evaluator=object(),
            approval_checker=lambda _approval_id: False,
        )

        events = [event async for event in adapter.stream(handle, "hello", governance=governance)]
        continued = [
            event
            async for event in adapter.continue_pending(
                handle,
                governance=RuntimeGovernanceContext(
                    session_id="sess_bundle",
                    turn_id="turn_continue",
                    trace_id="trace_continue",
                    policy_evaluator=governance.policy_evaluator,
                    approval_checker=governance.approval_checker,
                ),
            )
        ]

        metadata = handle.bundle.engine.tool_metadata
        assert events[0].text == "bundle: hello"
        assert continued[0].text == "continued"
        assert metadata["existing"] == "keep"
        assert metadata["session_id"] == "sess_bundle"
        assert metadata["turn_id"] == "turn_continue"
        assert metadata["trace_id"] == "trace_continue"
        assert "policy_evaluator" in metadata
        assert callable(metadata["approval_checker"])

    asyncio.run(run())


def test_runtime_adapter_clears_stale_approval_id_between_turns():
    async def run():
        adapter = OpenHarnessRuntimeAdapter(runtime_factory=lambda _model: FakeBundle())
        handle = await adapter.start(model="fake-model", restore_messages=[])
        first = RuntimeGovernanceContext(
            session_id="sess_bundle",
            turn_id="turn_retry",
            trace_id="trace_retry",
            approval_id="appr_old",
            policy_evaluator=object(),
        )
        second = RuntimeGovernanceContext(
            session_id="sess_bundle",
            turn_id="turn_next",
            trace_id="trace_next",
            policy_evaluator=first.policy_evaluator,
        )

        _ = [event async for event in adapter.stream(handle, "retry", governance=first)]
        assert handle.bundle.engine.tool_metadata["approval_id"] == "appr_old"

        _ = [event async for event in adapter.stream(handle, "next", governance=second)]

        metadata = handle.bundle.engine.tool_metadata
        assert metadata["turn_id"] == "turn_next"
        assert "approval_id" not in metadata

    asyncio.run(run())


def test_gateway_runtime_pool_uses_adapter_handle_for_simple_backend(tmp_path):
    async def run():
        pool = GatewayRuntimePool(
            agent_factory=lambda _model: FakeAgent(),
            runtime_backend="simple",
            store=GatewaySessionStore(tmp_path),
        )

        session = await pool.start_session()
        result = await pool.run_turn(session_id=session.session_id, user_input="hello")

        assert session.handle is not None
        assert session.adapter is not None
        assert session.handle.backend == "simple"
        assert result.final_text == "agent: hello"

    asyncio.run(run())


def test_gateway_runtime_pool_uses_adapter_handle_for_openharness_backend(tmp_path):
    async def run():
        pool = GatewayRuntimePool(
            model="fake-model",
            runtime_factory=lambda _model: FakeBundle(),
            runtime_backend="openharness",
            store=GatewaySessionStore(tmp_path),
        )

        session = await pool.start_session()
        result = await pool.run_turn(session_id=session.session_id, user_input="hello")
        continued = await pool.continue_turn(session_id=session.session_id)

        assert session.handle is not None
        assert session.adapter is not None
        assert session.handle.backend == "openharness"
        assert result.final_text == "bundle: hello"
        assert continued.final_text == "continued"
        metadata = session.handle.bundle.engine.tool_metadata
        assert metadata["session_id"] == session.session_id
        assert metadata["turn_id"] == continued.turn_id
        assert metadata["trace_id"].startswith("trace_")
        assert "policy_evaluator" in metadata
        assert callable(metadata["approval_checker"])

    asyncio.run(run())


def test_gateway_runtime_pool_passes_approval_id_to_openharness_stream(tmp_path):
    async def run():
        pool = GatewayRuntimePool(
            model="fake-model",
            runtime_factory=lambda _model: FakeBundle(),
            runtime_backend="openharness",
            store=GatewaySessionStore(tmp_path),
        )

        session = await pool.start_session()
        result = await pool.run_turn(
            session_id=session.session_id,
            user_input="retry",
            retry_of_turn_id="turn_original",
            approval_id="appr_retry",
        )

        assert result.final_text == "bundle: retry"
        metadata = session.handle.bundle.engine.tool_metadata
        assert metadata["approval_id"] == "appr_retry"
        assert metadata["turn_id"] == result.turn_id

    asyncio.run(run())
