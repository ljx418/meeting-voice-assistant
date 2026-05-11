"""V3.5-A Gateway RPC end-to-end contract tests."""

from __future__ import annotations

import asyncio
from pathlib import Path

from apps.gateway.approvals import ApprovalStore
from apps.gateway.protocol import RpcRequest
from apps.gateway.service import GatewayService
from apps.gateway.traces import TraceStore


def _service(tmp_path: Path) -> GatewayService:
    return GatewayService(
        trace_store=TraceStore(tmp_path / "traces"),
        approval_store=ApprovalStore(tmp_path / "approvals"),
    )


async def _request_approval(
    service: GatewayService,
    *,
    trace_id: str,
    scope: dict[str, str] | None = None,
) -> str:
    response = await service.handle_rpc(
        RpcRequest(
            id=f"request-{trace_id}",
            method="approval.request",
            params={
                "action": "publish",
                "request_summary": "Publish report",
                "trace_id": trace_id,
                **({"scope": scope} if scope else {}),
            },
        )
    )
    assert response.error is None
    return response.result["approval"]["approval_id"]


def test_v3_5_gateway_rpc_contract_e2e(tmp_path: Path) -> None:
    async def run() -> None:
        service = _service(tmp_path)

        initialized = await service.handle_rpc(RpcRequest(id="init", method="initialize", params={}))
        assert initialized.error is None
        assert "approval.respond" in {entry["method"] for entry in initialized.result["methods"]}
        assert "events.subscribe" in {entry["method"] for entry in initialized.result["methods"]}

        listed = await service.handle_rpc(RpcRequest(id="methods", method="method.list", params={}))
        assert listed.error is None
        methods = {entry["method"]: entry for entry in listed.result["methods"]}
        assert "approval.respond" in methods
        assert methods["events.subscribe"]["runtime_handler"] is True

        forbidden = await service.handle_rpc(
            RpcRequest(id="forbidden", method="method.list", params={"include_forbidden": True})
        )
        assert forbidden.error is None
        forbidden_methods = {entry["method"]: entry for entry in forbidden.result["methods"]}
        assert forbidden_methods["meeting.process_recording"]["surface"] == "forbidden_by_default"
        assert forbidden_methods["meeting.process_recording"]["sdk_exposure"] != "default"

        planned = await service.handle_rpc(
            RpcRequest(id="planned", method="method.list", params={"include_planned": True})
        )
        assert planned.error is None
        planned_methods = {entry["method"]: entry for entry in planned.result["methods"]}
        assert planned_methods["events.subscribe"]["schema_ref"] == "protocol.methods.events.subscribe"
        assert planned_methods["events.subscribe"]["runtime_handler"] is True

        approval_id = await _request_approval(service, trace_id="trace_e2e")
        approved = await service.handle_rpc(
            RpcRequest(
                id="approve",
                method="approval.respond",
                params={"approval_id": approval_id, "decision": "approve", "reason": "ok"},
            )
        )
        assert approved.error is None
        assert approved.result["status"] == "approved"
        assert approved.result["idempotent"] is False

        repeated = await service.handle_rpc(
            RpcRequest(id="repeat", method="approval.respond", params={"approval_id": approval_id, "decision": "approve"})
        )
        assert repeated.error is None
        assert repeated.result["idempotent"] is True

        conflict = await service.handle_rpc(
            RpcRequest(id="conflict", method="approval.respond", params={"approval_id": approval_id, "decision": "reject"})
        )
        assert conflict.result is None
        assert conflict.error is not None
        assert conflict.error.code == "APPROVAL_CONFLICT"
        assert set(conflict.error.data) >= {"approval_id", "decision", "current_status"}

        scoped_id = await _request_approval(
            service,
            trace_id="trace_e2e_scope",
            scope={"app_id": "knowledge", "workspace_id": "workspace_k"},
        )
        mismatch = await service.handle_rpc(
            RpcRequest(
                id="scope",
                method="approval.respond",
                params={"approval_id": scoped_id, "decision": "approve", "app_id": "meeting"},
            )
        )
        assert mismatch.result is None
        assert mismatch.error is not None
        assert mismatch.error.code == "SCOPE_MISMATCH"
        assert set(mismatch.error.data) >= {"approval_id", "trace_id"}

        direct_events = await service.handle_rpc(RpcRequest(id="events", method="events.subscribe", params={}))
        assert direct_events.result is None
        assert direct_events.error is not None
        assert direct_events.error.code == "AUTH_REQUIRED"

    asyncio.run(run())
