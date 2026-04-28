from __future__ import annotations

import asyncio
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from apps.gateway.approvals import ApprovalStore
from apps.gateway.policies import PolicyEvaluator
from apps.gateway.protocol import RpcRequest
from apps.gateway.runtime import GatewayRuntimePool
from apps.gateway.service import GatewayService
from apps.gateway.storage import GatewaySessionStore
from apps.gateway.traces import TraceStore


class RecordingAgent:
    def __init__(self) -> None:
        self.calls: list[str] = []

    def invoke(self, user_input: str):
        self.calls.append(user_input)
        return {"status": "success", "content": f"reply: {user_input}", "model": "fake-model"}


def _service(tmp_path: Path, agent: RecordingAgent) -> GatewayService:
    traces = TraceStore(tmp_path / "traces")
    approvals = ApprovalStore(tmp_path / "approvals")
    pool = GatewayRuntimePool(
        model="fake-model",
        agent_factory=lambda _model: agent,
        runtime_backend="simple",
        store=GatewaySessionStore(tmp_path / "sessions"),
        trace_store=traces,
        approval_store=approvals,
    )
    return GatewayService(runtime_pool=pool, trace_store=traces, approval_store=approvals)


def test_write_like_turn_creates_approval_without_invoking_agent(tmp_path):
    async def run():
        agent = RecordingAgent()
        service = _service(tmp_path, agent)
        started = await service.handle_rpc(RpcRequest(id="1", method="session.start"))
        session_id = started.result["session_id"]

        turn = await service.handle_rpc(
            RpcRequest(
                id="2",
                method="turn.start",
                params={"session_id": session_id, "input": "请在 workspace 下写入 phase2c.txt，内容为 hello"},
            )
        )

        assert turn.error is None
        assert agent.calls == []
        assert "操作需要审批" in turn.result["final_text"]

        completed = turn.result["events"][-1]
        assert completed["type"] == "turn.completed"
        assert completed["data"]["approval_required"] is True
        approval = completed["data"]["approval"]
        assert approval["status"] == "pending"
        assert approval["action"] == "workspace.write"
        assert approval["trace_id"] == turn.result["trace_id"]

        listed = await service.handle_rpc(
            RpcRequest(id="3", method="approval.list", params={"status": "pending"})
        )
        assert listed.error is None
        assert listed.result["count"] == 1
        assert listed.result["approvals"][0]["approval_id"] == approval["approval_id"]

        trace = await service.handle_rpc(
            RpcRequest(id="4", method="trace.get", params={"trace_id": turn.result["trace_id"]})
        )
        assert trace.error is None
        assert {record["event_type"] for record in trace.result["records"]} >= {
            "turn.started",
            "approval.request",
            "item.delta",
            "turn.completed",
        }

    asyncio.run(run())


def test_read_only_turn_does_not_create_approval(tmp_path):
    async def run():
        agent = RecordingAgent()
        service = _service(tmp_path, agent)
        started = await service.handle_rpc(RpcRequest(id="1", method="session.start"))
        session_id = started.result["session_id"]

        turn = await service.handle_rpc(
            RpcRequest(
                id="2",
                method="turn.start",
                params={"session_id": session_id, "input": "请读取 README 并总结当前项目"},
            )
        )

        assert turn.error is None
        assert agent.calls == ["请读取 README 并总结当前项目"]
        assert turn.result["final_text"].startswith("reply:")

        listed = await service.handle_rpc(
            RpcRequest(id="3", method="approval.list", params={"session_id": session_id})
        )
        assert listed.error is None
        assert listed.result["count"] == 0

    asyncio.run(run())


def test_policy_evaluate_rpc_and_tool_classification(tmp_path):
    async def run():
        service = _service(tmp_path, RecordingAgent())

        write_tool = await service.handle_rpc(
            RpcRequest(
                id="1",
                method="policy.evaluate",
                params={"tool_name": "workspace_write_file", "tool_input": {"file_path": "a.txt"}},
            )
        )
        assert write_tool.error is None
        assert write_tool.result["decision"]["requires_approval"] is True
        assert write_tool.result["decision"]["action"] == "workspace.write"

        read_tool = await service.handle_rpc(
            RpcRequest(
                id="2",
                method="policy.evaluate",
                params={"tool_name": "workspace_read_file", "tool_input": {"file_path": "README.md"}},
            )
        )
        assert read_tool.error is None
        assert read_tool.result["decision"]["requires_approval"] is False

        evaluator = PolicyEvaluator()
        meeting = evaluator.evaluate_user_input("请分析会议音频 /tmp/demo.mp3，生成会议纪要")
        assert meeting.requires_approval is False
        meeting_publish_plan = evaluator.evaluate_user_input(
            "今天会议讨论发布计划，张三负责测试，李四负责发布材料。",
            domain="meeting",
        )
        assert meeting_publish_plan.requires_approval is False

    asyncio.run(run())
