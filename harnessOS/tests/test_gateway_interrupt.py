from __future__ import annotations

import asyncio
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from apps.gateway.protocol import RpcRequest
from apps.gateway.runtime import GatewayRuntimePool
from apps.gateway.service import GatewayService
from apps.gateway.storage import GatewaySessionStore


class SlowBundleEngine:
    def __init__(self) -> None:
        self.entered = asyncio.Event()

    async def submit_message(self, user_input: str):
        self.entered.set()
        await asyncio.sleep(30)
        yield None


class SlowBundle:
    def __init__(self, engine: SlowBundleEngine) -> None:
        self.engine = engine


def test_active_turn_interrupt_cancels_running_bundle_turn(tmp_path):
    async def run():
        engine = SlowBundleEngine()
        service = GatewayService(
            GatewayRuntimePool(
                model="fake-model",
                runtime_factory=lambda _model: SlowBundle(engine),
                runtime_backend="openharness",
                store=GatewaySessionStore(tmp_path),
            )
        )
        started = await service.handle_rpc(RpcRequest(id="1", method="session.start"))
        session_id = started.result["session_id"]

        turn_task = asyncio.create_task(
            service.handle_rpc(
                RpcRequest(
                    id="2",
                    method="turn.start",
                    params={"session_id": session_id, "input": "long turn"},
                )
            )
        )
        await asyncio.wait_for(engine.entered.wait(), timeout=2)

        interrupted = await service.handle_rpc(
            RpcRequest(
                id="3",
                method="turn.interrupt",
                params={"session_id": session_id},
            )
        )
        assert interrupted.error is None
        assert interrupted.result["interrupted"] is True

        turn = await asyncio.wait_for(turn_task, timeout=2)
        assert turn.error is None
        assert turn.result["events"][-1]["type"] == "turn.interrupted"

        events = await service.handle_rpc(
            RpcRequest(
                id="4",
                method="session.events",
                params={"session_id": session_id},
            )
        )
        assert [event["type"] for event in events.result["events"]] == [
            "turn.started",
            "turn.interrupted",
        ]

        session = await service.handle_rpc(
            RpcRequest(
                id="5",
                method="session.read",
                params={"session_id": session_id},
            )
        )
        assert session.result["session"]["state"] == "interrupted"
        assert session.result["session"]["interrupted"] is True

    asyncio.run(run())
