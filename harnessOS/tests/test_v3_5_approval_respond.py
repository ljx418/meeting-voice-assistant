"""V3.5-A approval.respond contract tests."""

from __future__ import annotations

import asyncio
from pathlib import Path

from apps.gateway.approvals import ApprovalStore
from apps.gateway.protocol import RpcRequest
from apps.gateway.service import GatewayService
from apps.gateway.traces import TraceStore
from core.protocol.schemas.errors import ERROR_SCHEMAS


def _service(tmp_path: Path) -> GatewayService:
    return GatewayService(
        trace_store=TraceStore(tmp_path / "traces"),
        approval_store=ApprovalStore(tmp_path / "approvals"),
    )


async def _request_approval(service: GatewayService, *, trace_id: str = "trace_v35", scope: dict | None = None) -> str:
    requested = await service.handle_rpc(
        RpcRequest(
            id="request",
            method="approval.request",
            params={
                "action": "publish",
                "request_summary": "Publish report",
                "trace_id": trace_id,
                **({"scope": scope} if scope else {}),
            },
        )
    )
    assert requested.error is None
    return requested.result["approval"]["approval_id"]


def test_approval_respond_approve_reject_success_paths(tmp_path: Path) -> None:
    async def run() -> None:
        service = _service(tmp_path)
        approve_id = await _request_approval(service, trace_id="trace_approve")
        approved = await service.handle_rpc(
            RpcRequest(
                id="approve",
                method="approval.respond",
                params={"approval_id": approve_id, "decision": "approve", "reason": "ok"},
            )
        )
        assert approved.error is None
        assert {"approval", "status", "trace_id", "idempotent"} <= set(approved.result)
        assert approved.result["status"] == "approved"
        assert approved.result["idempotent"] is False
        assert approved.result["approval"]["decision_reason"] == "ok"

        reject_id = await _request_approval(service, trace_id="trace_reject")
        rejected = await service.handle_rpc(
            RpcRequest(id="reject", method="approval.respond", params={"approval_id": reject_id, "decision": "reject"})
        )
        assert rejected.error is None
        assert rejected.result["status"] == "rejected"
        assert rejected.result["idempotent"] is False

    asyncio.run(run())


def test_approval_respond_repeated_same_decision_is_idempotent_without_duplicate_trace(tmp_path: Path) -> None:
    async def run() -> None:
        service = _service(tmp_path)
        approval_id = await _request_approval(service, trace_id="trace_idempotent")
        first = await service.handle_rpc(
            RpcRequest(
                id="first",
                method="approval.respond",
                params={"approval_id": approval_id, "decision": "approve", "reason": "first reason"},
            )
        )
        assert first.error is None

        second = await service.handle_rpc(
            RpcRequest(
                id="second",
                method="approval.respond",
                params={"approval_id": approval_id, "decision": "approve", "reason": "second reason"},
            )
        )
        assert second.error is None
        assert second.result["idempotent"] is True
        assert second.result["status"] == "approved"
        assert second.result["approval"]["decision_reason"] == "first reason"

        trace = await service.handle_rpc(RpcRequest(id="trace", method="trace.get", params={"trace_id": "trace_idempotent"}))
        respond_traces = [record for record in trace.result["records"] if record["event_type"] == "approval.respond"]
        assert len(respond_traces) == 1

    asyncio.run(run())


def test_approval_respond_repeated_reject_is_idempotent(tmp_path: Path) -> None:
    async def run() -> None:
        service = _service(tmp_path)
        approval_id = await _request_approval(service, trace_id="trace_reject_idempotent")
        first = await service.handle_rpc(
            RpcRequest(id="first", method="approval.respond", params={"approval_id": approval_id, "decision": "reject"})
        )
        assert first.error is None

        second = await service.handle_rpc(
            RpcRequest(id="second", method="approval.respond", params={"approval_id": approval_id, "decision": "reject"})
        )
        assert second.error is None
        assert second.result["status"] == "rejected"
        assert second.result["idempotent"] is True

        trace = await service.handle_rpc(
            RpcRequest(id="trace", method="trace.get", params={"trace_id": "trace_reject_idempotent"})
        )
        respond_traces = [record for record in trace.result["records"] if record["event_type"] == "approval.respond"]
        assert len(respond_traces) == 1

    asyncio.run(run())


def test_approval_respond_conflicting_decision_returns_approval_conflict(tmp_path: Path) -> None:
    async def run() -> None:
        service = _service(tmp_path)
        approval_id = await _request_approval(service)
        first = await service.handle_rpc(
            RpcRequest(id="first", method="approval.respond", params={"approval_id": approval_id, "decision": "reject"})
        )
        assert first.error is None

        conflict = await service.handle_rpc(
            RpcRequest(id="conflict", method="approval.respond", params={"approval_id": approval_id, "decision": "approve"})
        )
        assert conflict.result is None
        assert conflict.error is not None
        assert conflict.error.code == "APPROVAL_CONFLICT"
        assert conflict.error.data["approval_id"] == approval_id
        assert conflict.error.data["decision"] == "approve"
        assert conflict.error.data["current_status"] == "rejected"

        approval_id_2 = await _request_approval(service)
        approved = await service.handle_rpc(
            RpcRequest(id="approve", method="approval.respond", params={"approval_id": approval_id_2, "decision": "approve"})
        )
        assert approved.error is None
        conflict_2 = await service.handle_rpc(
            RpcRequest(id="conflict2", method="approval.respond", params={"approval_id": approval_id_2, "decision": "reject"})
        )
        assert conflict_2.error is not None
        assert conflict_2.error.code == "APPROVAL_CONFLICT"
        assert conflict_2.error.data["current_status"] == "approved"

    asyncio.run(run())


def test_approval_respond_not_found_invalid_decision_and_scope_mismatch(tmp_path: Path) -> None:
    async def run() -> None:
        service = _service(tmp_path)
        missing = await service.handle_rpc(
            RpcRequest(
                id="missing",
                method="approval.respond",
                params={"approval_id": "appr_missing", "decision": "approve"},
            )
        )
        assert missing.error is not None
        assert missing.error.code == "APPROVAL_NOT_FOUND"

        invalid = await service.handle_rpc(
            RpcRequest(
                id="invalid",
                method="approval.respond",
                params={"approval_id": "appr_any", "decision": "maybe"},
            )
        )
        assert invalid.error is not None
        assert invalid.error.code == "APPROVAL_INVALID_DECISION"

        approval_id = await _request_approval(
            service,
            trace_id="trace_scope_mismatch",
            scope={"app_id": "knowledge", "workspace_id": "workspace_k"},
        )
        mismatch = await service.handle_rpc(
            RpcRequest(
                id="scope",
                method="approval.respond",
                params={"approval_id": approval_id, "decision": "approve", "app_id": "meeting"},
            )
        )
        assert mismatch.error is not None
        assert mismatch.error.code == "SCOPE_MISMATCH"
        assert mismatch.error.data["approval_id"] == approval_id
        assert "trace_id" in mismatch.error.data

        bypass = await service.handle_rpc(
            RpcRequest(
                id="scope_all",
                method="approval.respond",
                params={
                    "approval_id": approval_id,
                    "decision": "approve",
                    "app_id": "meeting",
                    "scope_mode": "all",
                },
            )
        )
        assert bypass.error is not None
        assert bypass.error.code == "SCOPE_MISMATCH"
        fetched = await service.handle_rpc(RpcRequest(id="fetch", method="approval.get", params={"approval_id": approval_id, "scope_mode": "all"}))
        assert fetched.error is None
        assert fetched.result["approval"]["status"] == "pending"

    asyncio.run(run())


def test_approval_respond_nested_scope_match_and_mismatch(tmp_path: Path) -> None:
    async def run() -> None:
        service = _service(tmp_path)
        scope = {"app_id": "meeting", "project_id": "project_m", "workspace_id": "workspace_m"}
        approval_id = await _request_approval(service, trace_id="trace_nested_scope", scope=scope)

        approved = await service.handle_rpc(
            RpcRequest(
                id="approve",
                method="approval.respond",
                params={"approval_id": approval_id, "decision": "approve", "scope": dict(scope)},
            )
        )
        assert approved.error is None
        assert approved.result["status"] == "approved"

        mismatch_id = await _request_approval(service, trace_id="trace_nested_mismatch", scope=scope)
        mismatch_scope = {"app_id": "meeting", "project_id": "project_m", "workspace_id": "workspace_other"}
        mismatch = await service.handle_rpc(
            RpcRequest(
                id="mismatch",
                method="approval.respond",
                params={"approval_id": mismatch_id, "decision": "approve", "scope": mismatch_scope},
            )
        )
        assert mismatch.result is None
        assert mismatch.error is not None
        assert mismatch.error.code == "SCOPE_MISMATCH"
        assert set(mismatch.error.data) >= {"approval_id", "trace_id"}

    asyncio.run(run())


def test_approval_retry_consumed_is_reserved_not_regular_respond_path(tmp_path: Path) -> None:
    async def run() -> None:
        assert "APPROVAL_RETRY_CONSUMED" in {entry["code"] for entry in ERROR_SCHEMAS}
        service = _service(tmp_path)
        approval_id = await _request_approval(service)
        responded = await service.handle_rpc(
            RpcRequest(id="respond", method="approval.respond", params={"approval_id": approval_id, "decision": "approve"})
        )
        assert responded.error is None
        repeated = await service.handle_rpc(
            RpcRequest(id="repeat", method="approval.respond", params={"approval_id": approval_id, "decision": "approve"})
        )
        assert repeated.error is None
        assert repeated.result["idempotent"] is True
        assert repeated.error is None

    asyncio.run(run())


def test_approval_respond_concurrent_same_decision_has_one_side_effect(tmp_path: Path) -> None:
    async def run() -> None:
        service = _service(tmp_path)
        approval_id = await _request_approval(service, trace_id="trace_concurrent_approve")

        first, second = await asyncio.gather(
            service.handle_rpc(
                RpcRequest(id="approve1", method="approval.respond", params={"approval_id": approval_id, "decision": "approve"})
            ),
            service.handle_rpc(
                RpcRequest(id="approve2", method="approval.respond", params={"approval_id": approval_id, "decision": "approve"})
            ),
        )
        responses = [first, second]
        assert all(response.error is None for response in responses)
        assert sorted(response.result["idempotent"] for response in responses) == [False, True]

        trace = await service.handle_rpc(
            RpcRequest(id="trace", method="trace.get", params={"trace_id": "trace_concurrent_approve"})
        )
        respond_traces = [record for record in trace.result["records"] if record["event_type"] == "approval.respond"]
        assert len(respond_traces) == 1

    asyncio.run(run())


def test_approval_respond_concurrent_conflicting_decisions_are_stable(tmp_path: Path) -> None:
    async def run() -> None:
        service = _service(tmp_path)
        approval_id = await _request_approval(service, trace_id="trace_concurrent_conflict")

        approve, reject = await asyncio.gather(
            service.handle_rpc(
                RpcRequest(id="approve", method="approval.respond", params={"approval_id": approval_id, "decision": "approve"})
            ),
            service.handle_rpc(
                RpcRequest(id="reject", method="approval.respond", params={"approval_id": approval_id, "decision": "reject"})
            ),
        )
        responses = [approve, reject]
        successes = [response for response in responses if response.error is None]
        conflicts = [response for response in responses if response.error is not None]
        assert len(successes) == 1
        assert len(conflicts) == 1
        assert conflicts[0].error.code == "APPROVAL_CONFLICT"
        assert conflicts[0].error.data["current_status"] in {"approved", "rejected"}

    asyncio.run(run())
