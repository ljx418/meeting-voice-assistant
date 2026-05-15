"""V3.6/V4.0 preflight legacy approval route hardening tests."""

from __future__ import annotations

import asyncio

from apps.gateway.protocol import RpcRequest
from apps.gateway.service import GatewayService


def _scope() -> dict[str, str]:
    return {"app_id": "meeting", "project_id": "demo", "workspace_id": "local"}


def _approval_template() -> dict:
    return {
        "workflow_template_id": "workflow_legacy_approval",
        "name": "Legacy Approval Guard",
        "stations": [
            {"station_id": "station_a", "name": "A"},
            {"station_id": "station_b", "name": "B", "approval_required": True},
        ],
        "edges": [{"edge_id": "a_to_b", "from_station_id": "station_a", "to_station_id": "station_b"}],
    }


async def _rpc(service: GatewayService, method: str, params: dict | None = None):
    return await service.handle_rpc(RpcRequest(id=method, method=method, params=params or {}))


async def _waiting_workflow(service: GatewayService) -> tuple[str, str]:
    created = await _rpc(service, "workflow.template.create", {"template": _approval_template(), "scope": _scope()})
    assert created.error is None
    published = await _rpc(service, "workflow.template.publish", {"workflow_template_id": "workflow_legacy_approval", "version": "1.0.0", "scope": _scope()})
    assert published.error is None
    started = await _rpc(service, "workflow.instance.start", {"workflow_version_id": published.result["version"]["workflow_version_id"], "scope": _scope()})
    assert started.error is None
    instance_id = started.result["workflow_instance"]["workflow_instance_id"]
    approvals = await _rpc(service, "approval.list", {"scope": _scope()})
    approval_id = approvals.result["approvals"][0]["approval_id"]
    return instance_id, approval_id


def test_legacy_approve_reject_cannot_decide_workflow_bound_approval() -> None:
    async def run() -> None:
        for method in ("approval.approve", "approval.reject"):
            service = GatewayService()
            instance_id, approval_id = await _waiting_workflow(service)
            denied = await _rpc(service, method, {"approval_id": approval_id, "scope": _scope()})
            assert denied.error.code == "WORKFLOW_ACTION_FORBIDDEN"
            approval = await _rpc(service, "approval.get", {"approval_id": approval_id, "scope": _scope()})
            assert approval.result["approval"]["status"] == "pending"
            workflow = await _rpc(service, "workflow.instance.get", {"workflow_instance_id": instance_id, "scope": _scope()})
            assert workflow.result["workflow_instance"]["status"] == "waiting_approval"

    asyncio.run(run())


def test_legacy_approve_still_supports_standalone_approval() -> None:
    async def run() -> None:
        service = GatewayService()
        requested = await _rpc(
            service,
            "approval.request",
            {"action": "standalone.action", "request_summary": "Approve standalone action", "scope": _scope()},
        )
        assert requested.error is None
        approval_id = requested.result["approval"]["approval_id"]
        approved = await _rpc(service, "approval.approve", {"approval_id": approval_id, "scope": _scope()})
        assert approved.error is None
        assert approved.result["approval"]["status"] == "approved"

    asyncio.run(run())
