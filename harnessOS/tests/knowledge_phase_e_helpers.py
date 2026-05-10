from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any

from apps.gateway.artifacts import ArtifactRegistry
from apps.gateway.protocol import RpcRequest
from apps.gateway.runtime import GatewayRuntimePool
from apps.gateway.service import GatewayService
from apps.gateway.storage import GatewaySessionStore
from core.stores import CoreSQLiteStore


class FakeAgent:
    def invoke(self, user_input: str):
        return {
            "status": "success",
            "content": f"reply: {user_input}",
            "model": "fake-model",
        }


def run_async(coro: Any) -> Any:
    return asyncio.run(coro)


def build_knowledge_service(tmp_path: Path) -> GatewayService:
    service = GatewayService(
        GatewayRuntimePool(
            model="fake-model",
            agent_factory=lambda _model: FakeAgent(),
            runtime_backend="simple",
            store=GatewaySessionStore(tmp_path / "sessions"),
            artifact_registry=ArtifactRegistry(tmp_path / "artifacts"),
            core_store=CoreSQLiteStore(tmp_path / "core.sqlite3"),
        )
    )
    _disable_data_service_approval(service)
    return service


def _disable_data_service_approval(service: GatewayService) -> None:
    original_get_connector = service.connector_registry.get_connector

    def get_connector(connector_id: str):
        connector = dict(original_get_connector(connector_id))
        if connector_id == "data_service_mcp":
            connector["requires_approval_for"] = []
        return connector

    service.connector_registry.get_connector = get_connector  # type: ignore[method-assign]


async def run_knowledge_turn(
    service: GatewayService,
    *,
    workspace_id: str = "workspace_knowledge",
    user_input: str = "检索知识库 PhaseE 验收",
) -> tuple[str, dict[str, Any]]:
    started = await service.handle_rpc(
        RpcRequest(
            id=f"start-{workspace_id}",
            method="session.start",
            params={"scope": {"app_id": "knowledge", "workspace_id": workspace_id}},
        )
    )
    assert started.error is None
    session_id = started.result["session_id"]
    turn = await service.handle_rpc(
        RpcRequest(
            id=f"turn-{workspace_id}",
            method="turn.start",
            params={"session_id": session_id, "domain": "knowledge", "input": user_input},
        )
    )
    assert turn.error is None
    return session_id, turn.result
