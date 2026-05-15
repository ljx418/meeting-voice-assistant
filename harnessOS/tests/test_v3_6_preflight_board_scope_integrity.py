"""V3.6/V4.0 preflight board and status scope integrity tests."""

from __future__ import annotations

import asyncio

from apps.gateway.protocol import RpcRequest
from apps.gateway.service import GatewayService


def _scope(app_id: str = "meeting") -> dict[str, str]:
    return {"app_id": app_id, "project_id": "demo", "workspace_id": "local"}


def _template() -> dict:
    return {
        "workflow_template_id": "workflow_board_scope",
        "name": "Board Scope",
        "stations": [{"station_id": "station_a", "name": "A"}],
        "edges": [],
    }


async def _rpc(service: GatewayService, method: str, params: dict | None = None):
    return await service.handle_rpc(RpcRequest(id=method, method=method, params=params or {}))


def test_board_and_status_reject_cross_scope_job_references() -> None:
    async def run() -> None:
        service = GatewayService()
        created = await _rpc(service, "workflow.template.create", {"template": _template(), "scope": _scope()})
        assert created.error is None
        published = await _rpc(service, "workflow.template.publish", {"workflow_template_id": "workflow_board_scope", "version": "1.0.0", "scope": _scope()})
        assert published.error is None
        started = await _rpc(service, "workflow.instance.start", {"workflow_version_id": published.result["version"]["workflow_version_id"], "scope": _scope()})
        assert started.error is None
        instance_id = started.result["workflow_instance"]["workflow_instance_id"]
        job_id = started.result["workflow_instance"]["job_ids"][0]

        job = service.core_service.get_job(job_id)
        job.app_id = "knowledge"
        service.core_service.store.save_job(job)

        status = await _rpc(service, "workflow.instance.status", {"workflow_instance_id": instance_id, "scope": _scope()})
        assert status.error.code == "SCOPE_MISMATCH"

        board = await _rpc(service, "workflow.board.get", {"workflow_instance_id": instance_id, "scope": _scope()})
        assert board.error.code == "SCOPE_MISMATCH"

    asyncio.run(run())
