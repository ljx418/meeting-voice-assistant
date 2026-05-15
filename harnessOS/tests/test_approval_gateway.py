from __future__ import annotations

import asyncio
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from apps.gateway.approvals import ApprovalStore
from apps.gateway.protocol import RpcRequest
from apps.gateway.service import GatewayService
from apps.gateway.traces import TraceStore


def _service(tmp_path: Path) -> GatewayService:
    return GatewayService(
        trace_store=TraceStore(tmp_path / "traces"),
        approval_store=ApprovalStore(tmp_path / "approvals"),
    )


def test_approval_request_list_get_approve_and_trace(tmp_path):
    async def run():
        service = _service(tmp_path)
        requested = await service.handle_rpc(
            RpcRequest(
                id="a1",
                method="approval.request",
                params={
                    "action": "workspace.write",
                    "request_summary": "Write approval_test.txt",
                    "trace_id": "trace_demo",
                    "session_id": "sess_demo",
                    "turn_id": "turn_demo",
                    "risk_level": "high",
                },
            )
        )

        assert requested.error is None
        approval = requested.result["approval"]
        approval_id = approval["approval_id"]
        assert approval["status"] == "pending"
        assert approval["risk_level"] == "high"
        assert requested.result["trace_id"] == "trace_demo"

        listed = await service.handle_rpc(
            RpcRequest(id="a2", method="approval.list", params={"status": "pending"})
        )
        assert listed.error is None
        assert listed.result["count"] == 1
        assert listed.result["approvals"][0]["approval_id"] == approval_id

        fetched = await service.handle_rpc(
            RpcRequest(id="a3", method="approval.get", params={"approval_id": approval_id})
        )
        assert fetched.error is None
        assert fetched.result["approval"]["status"] == "pending"

        approved = await service.handle_rpc(
            RpcRequest(
                id="a4",
                method="approval.approve",
                params={"approval_id": approval_id, "reason": "manual ok"},
            )
        )
        assert approved.error is None
        assert approved.result["approval"]["status"] == "approved"
        assert approved.result["approval"]["decision_reason"] == "manual ok"

        trace = await service.handle_rpc(
            RpcRequest(id="a5", method="trace.get", params={"trace_id": "trace_demo"})
        )
        assert trace.error is None
        event_types = [record["event_type"] for record in trace.result["records"]]
        assert "approval.request" in event_types
        assert "approval.approve" in event_types
        assert all(approval_id in record["approval_ids"] for record in trace.result["records"])

    asyncio.run(run())


def test_approval_reject_and_double_decision_error(tmp_path):
    async def run():
        service = _service(tmp_path)
        requested = await service.handle_rpc(
            RpcRequest(
                id="r1",
                method="approval.request",
                params={
                    "action": "publish",
                    "request_summary": "Publish report",
                    "trace_id": "trace_reject",
                },
            )
        )
        approval_id = requested.result["approval"]["approval_id"]

        rejected = await service.handle_rpc(
            RpcRequest(
                id="r2",
                method="approval.reject",
                params={"approval_id": approval_id, "reason": "not ready"},
            )
        )
        assert rejected.error is None
        assert rejected.result["approval"]["status"] == "rejected"

        second = await service.handle_rpc(
            RpcRequest(id="r3", method="approval.approve", params={"approval_id": approval_id})
        )
        assert second.result is None
        assert second.error is not None
        assert second.error.code == "RUNTIME_ERROR"
        assert "not pending" in second.error.message

    asyncio.run(run())


def test_approval_invalid_status_filter_returns_error(tmp_path):
    async def run():
        service = _service(tmp_path)
        response = await service.handle_rpc(
            RpcRequest(id="bad", method="approval.list", params={"status": "unknown"})
        )
        assert response.result is None
        assert response.error is not None
        assert response.error.code == "RUNTIME_ERROR"

    asyncio.run(run())


def test_approval_gateway_scope_filters_and_blocks_cross_app_decisions(tmp_path):
    async def run():
        service = _service(tmp_path)
        requested = await service.handle_rpc(
            RpcRequest(
                id="s1",
                method="approval.request",
                params={
                    "action": "publish",
                    "request_summary": "Scoped approval",
                    "trace_id": "trace_scope",
                    "scope": {"app_id": "knowledge", "workspace_id": "workspace_k"},
                },
            )
        )
        assert requested.error is None
        approval_id = requested.result["approval"]["approval_id"]
        assert requested.result["approval"]["app_id"] == "knowledge"

        listed = await service.handle_rpc(
            RpcRequest(id="s2", method="approval.list", params={"app_id": "knowledge"})
        )
        assert listed.error is None
        assert listed.result["count"] == 1

        denied = await service.handle_rpc(
            RpcRequest(id="s3", method="approval.get", params={"approval_id": approval_id, "app_id": "meeting"})
        )
        assert denied.error is not None
        assert denied.error.code == "SCOPE_MISMATCH"

        denied_approve = await service.handle_rpc(
            RpcRequest(
                id="s4",
                method="approval.approve",
                params={"approval_id": approval_id, "app_id": "meeting", "reason": "wrong scope"},
            )
        )
        assert denied_approve.error is not None
        assert denied_approve.error.code == "SCOPE_MISMATCH"

        approved = await service.handle_rpc(
            RpcRequest(
                id="s5",
                method="approval.approve",
                params={
                    "approval_id": approval_id,
                    "scope": {"app_id": "knowledge", "workspace_id": "workspace_k"},
                    "reason": "ok",
                },
            )
        )
        assert approved.error is None
        assert approved.result["approval"]["status"] == "approved"

    asyncio.run(run())
