from __future__ import annotations

import asyncio
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from apps.gateway.approvals import ApprovalStore
from apps.gateway.protocol import RpcRequest
from apps.gateway.retries import RetryStore
from apps.gateway.runtime import GatewayRuntimePool
from apps.gateway.service import GatewayService
from apps.gateway.storage import GatewaySessionStore
from apps.gateway.traces import TraceStore


class WriteOnInvokeAgent:
    def __init__(self, output_path: Path) -> None:
        self.output_path = output_path
        self.calls: list[str] = []

    def invoke(self, user_input: str):
        self.calls.append(user_input)
        self.output_path.write_text("hello from retry\n", encoding="utf-8")
        return {"status": "success", "content": f"wrote: {self.output_path.name}", "model": "fake-model"}


def _service(tmp_path: Path, agent: WriteOnInvokeAgent) -> GatewayService:
    traces = TraceStore(tmp_path / "traces")
    approvals = ApprovalStore(tmp_path / "approvals")
    retries = RetryStore(tmp_path / "retries")
    pool = GatewayRuntimePool(
        model="fake-model",
        agent_factory=lambda _model: agent,
        runtime_backend="simple",
        store=GatewaySessionStore(tmp_path / "sessions"),
        trace_store=traces,
        approval_store=approvals,
        retry_store=retries,
    )
    return GatewayService(
        runtime_pool=pool,
        trace_store=traces,
        approval_store=approvals,
        retry_store=retries,
    )


def test_turn_retry_runs_approved_policy_blocked_turn(tmp_path):
    async def run():
        output_path = tmp_path / "approved_retry.txt"
        agent = WriteOnInvokeAgent(output_path)
        service = _service(tmp_path, agent)
        started = await service.handle_rpc(RpcRequest(id="1", method="session.start"))
        session_id = started.result["session_id"]

        blocked = await service.handle_rpc(
            RpcRequest(
                id="2",
                method="turn.start",
                params={"session_id": session_id, "input": "请写入 approved_retry.txt，内容为 hello"},
            )
        )
        assert blocked.error is None
        assert not output_path.exists()
        assert agent.calls == []
        approval = blocked.result["events"][-1]["data"]["approval"]
        retry_context = blocked.result["events"][-1]["data"]["retry_context"]

        pending_retry = await service.handle_rpc(
            RpcRequest(
                id="3",
                method="turn.retry",
                params={"session_id": session_id, "approval_id": approval["approval_id"]},
            )
        )
        assert pending_retry.result is None
        assert pending_retry.error is not None
        assert pending_retry.error.code == "INVALID_PARAMS"
        assert "not approved" in pending_retry.error.message

        approved = await service.handle_rpc(
            RpcRequest(
                id="4",
                method="approval.approve",
                params={"approval_id": approval["approval_id"], "reason": "manual ok"},
            )
        )
        assert approved.error is None

        retried = await service.handle_rpc(
            RpcRequest(
                id="5",
                method="turn.retry",
                params={"session_id": session_id, "approval_id": approval["approval_id"]},
            )
        )
        assert retried.error is None
        assert output_path.read_text(encoding="utf-8").strip() == "hello from retry"
        assert agent.calls == ["请写入 approved_retry.txt，内容为 hello"]
        assert retried.result["events"][0]["data"]["retry_of_turn_id"] == blocked.result["turn_id"]
        assert retried.result["events"][0]["data"]["approval_id"] == approval["approval_id"]
        assert retried.result["retry_context"]["retry_id"] == retry_context["retry_id"]
        assert retried.result["retry_context"]["status"] == "retried"
        assert retried.result["retry_context"]["retry_turn_id"] == retried.result["turn_id"]

        second_retry = await service.handle_rpc(
            RpcRequest(
                id="6",
                method="turn.retry",
                params={"session_id": session_id, "approval_id": approval["approval_id"]},
            )
        )
        assert second_retry.result is None
        assert second_retry.error is not None
        assert "already retried" in second_retry.error.message

        original_trace = await service.handle_rpc(
            RpcRequest(id="7", method="trace.get", params={"trace_id": blocked.result["trace_id"]})
        )
        assert original_trace.error is None
        assert any(
            approval["approval_id"] in record["approval_ids"]
            for record in original_trace.result["records"]
        )

    asyncio.run(run())


def test_turn_retry_can_find_context_by_source_turn_id(tmp_path):
    async def run():
        output_path = tmp_path / "turn_id_retry.txt"
        agent = WriteOnInvokeAgent(output_path)
        service = _service(tmp_path, agent)
        started = await service.handle_rpc(RpcRequest(id="1", method="session.start"))
        session_id = started.result["session_id"]
        blocked = await service.handle_rpc(
            RpcRequest(
                id="2",
                method="turn.start",
                params={"session_id": session_id, "input": "请写入 turn_id_retry.txt，内容为 hello"},
            )
        )
        approval_id = blocked.result["events"][-1]["data"]["approval"]["approval_id"]
        await service.handle_rpc(
            RpcRequest(id="3", method="approval.approve", params={"approval_id": approval_id})
        )

        retried = await service.handle_rpc(
            RpcRequest(
                id="4",
                method="turn.retry",
                params={"session_id": session_id, "turn_id": blocked.result["turn_id"]},
            )
        )

        assert retried.error is None
        assert output_path.exists()
        assert retried.result["final_text"] == "wrote: turn_id_retry.txt"

    asyncio.run(run())
