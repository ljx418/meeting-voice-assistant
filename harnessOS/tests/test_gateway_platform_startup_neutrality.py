"""Gateway platform startup neutrality and repository abstraction tests."""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any

from apps.gateway.protocol import RpcRequest
from apps.gateway.runtime import GatewayRuntimePool
from apps.gateway.service import GatewayService
from apps.gateway.workflows import LeadOrchestrator, WorkflowRegistry
from core.workflows.store import InMemoryWorkflowStore, WorkflowRepository


def _scope() -> dict[str, str]:
    return {"app_id": "meeting", "project_id": "demo", "workspace_id": "local"}


def _template() -> dict:
    return {
        "workflow_template_id": "workflow_repo_abstraction",
        "name": "Repository Abstraction",
        "stations": [{"station_id": "station_a", "name": "A"}],
        "edges": [],
    }


async def _rpc(service: GatewayService, method: str, params: dict | None = None):
    return await service.handle_rpc(RpcRequest(id=method, method=method, params=params or {}))


class NoPrivateDraftStore:
    """Store wrapper that fails if Gateway touches private draft helpers."""

    def __init__(self) -> None:
        self.inner = InMemoryWorkflowStore()

    def _require_draft(self, *_: Any, **__: Any) -> None:
        raise AssertionError("Gateway must use WorkflowRepository.get_draft, not store._require_draft")

    def __getattr__(self, name: str) -> Any:
        return getattr(self.inner, name)


def test_platform_modules_do_not_hard_import_business_workflows_at_top_level() -> None:
    checked = [
        Path("apps/gateway/service.py"),
        Path("apps/gateway/runtime.py"),
        Path("apps/gateway/workflows.py"),
    ]
    for path in checked:
        text = path.read_text(encoding="utf-8")
        assert "from packs.meeting" not in "\n".join(line for line in text.splitlines()[:80])
        assert "from packs.knowledge" not in "\n".join(line for line in text.splitlines()[:80])
        assert "from packs.video_studio" not in "\n".join(line for line in text.splitlines()[:80])


def test_platform_gateway_can_start_with_empty_orchestrator_without_business_deps() -> None:
    pool = GatewayRuntimePool(meeting_workflow=None, orchestrator=LeadOrchestrator(WorkflowRegistry()))
    service = GatewayService(runtime_pool=pool)
    assert service.runtime_pool is pool
    assert service.core_service is not None


def test_workflow_patch_propose_uses_repository_get_draft_not_private_store_api() -> None:
    async def run() -> None:
        store = NoPrivateDraftStore()
        service = GatewayService(workflow_repository=WorkflowRepository(store))
        created = await _rpc(service, "workflow.template.create", {"template": _template(), "scope": _scope()})
        assert created.error is None
        proposed = await _rpc(
            service,
            "workflow.patch.propose",
            {
                "workflow_template_id": "workflow_repo_abstraction",
                "patch": {
                    "operation": "add_station",
                    "payload": {"station": {"station_id": "station_b", "name": "B"}},
                    "actor_type": "user",
                },
                "scope": _scope(),
            },
        )
        assert proposed.error is None

    asyncio.run(run())
