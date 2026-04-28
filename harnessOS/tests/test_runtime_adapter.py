from __future__ import annotations

import asyncio
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from apps.gateway.runtime import GatewayRuntimePool
from apps.gateway.storage import GatewaySessionStore
from core.runtime_adapter import OpenHarnessRuntimeAdapter, SimpleRuntimeAdapter


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

    asyncio.run(run())
