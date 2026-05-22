"""V4.0-A2 Workflow Console BFF structured route tests."""

from __future__ import annotations

import asyncio
import json

from fastapi.testclient import TestClient

from apps.api import create_app
from apps.gateway.approvals import ApprovalStore
from apps.gateway.artifacts import ArtifactRegistry
from apps.gateway.protocol import RpcRequest
from apps.gateway.runtime import GatewayRuntimePool
from apps.gateway.service import GatewayService
from apps.gateway.storage import GatewaySessionStore
from apps.gateway.traces import TraceStore
from core.protocol.auth import issue_capability_token


SECRET = "v4-a2-secret"
ORIGIN = "http://localhost:5173"
SCOPE_QUERY = "?app_id=meeting&project_id=demo&workspace_id=local"


def _scope(app_id: str = "meeting", project_id: str = "demo", workspace_id: str = "local") -> dict[str, str]:
    return {"app_id": app_id, "project_id": project_id, "workspace_id": workspace_id}


def _gateway(tmp_path) -> GatewayService:
    runtime = GatewayRuntimePool(
        store=GatewaySessionStore(tmp_path / "sessions"),
        artifact_registry=ArtifactRegistry(tmp_path / "artifacts"),
        trace_store=TraceStore(tmp_path / "traces"),
        approval_store=ApprovalStore(tmp_path / "approvals"),
    )
    return GatewayService(runtime_pool=runtime)


async def _rpc(service: GatewayService, method: str, params: dict | None = None):
    response = await service.handle_rpc(RpcRequest(id=method, method=method, params=params or {}))
    assert response.error is None, response.error
    return response.result


def _template(template_id: str = "v4_a2_console") -> dict:
    return {
        "workflow_template_id": template_id,
        "name": "V4 A2 Console Workflow",
        "stations": [
            {
                "station_id": "station_a",
                "name": "A",
                "output_contracts": [{"contract_id": "a_out", "artifact_kind": "artifact_a", "direction": "output"}],
            },
            {
                "station_id": "station_b",
                "name": "B",
                "input_contracts": [{"contract_id": "a_in", "artifact_kind": "artifact_a", "direction": "input"}],
                "output_contracts": [{"contract_id": "b_out", "artifact_kind": "artifact_b", "direction": "output"}],
            },
        ],
        "edges": [{"edge_id": "a_to_b", "from_station_id": "station_a", "to_station_id": "station_b"}],
    }


async def _seed(service: GatewayService, template_id: str = "v4_a2_console") -> dict:
    await _rpc(service, "workflow.template.create", {"template": _template(template_id), "scope": _scope()})
    published = await _rpc(
        service,
        "workflow.template.publish",
        {"workflow_template_id": template_id, "version": "1.0.0", "scope": _scope()},
    )
    started = await _rpc(
        service,
        "workflow.instance.start",
        {"workflow_version_id": published["version"]["workflow_version_id"], "scope": _scope()},
    )
    runs = (
        await _rpc(
            service,
            "station.run.list",
            {"workflow_instance_id": started["workflow_instance"]["workflow_instance_id"], "scope": _scope()},
        )
    )["station_runs"]
    return {"template": published["template"], "version": published["version"], "instance": started["workflow_instance"], "runs": runs}


def test_bff_routes_return_redacted_frontend_dtos(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("HARNESS_V3_5_DEV_MODE", "1")
    service = _gateway(tmp_path)
    seeded = asyncio.run(_seed(service))
    client = TestClient(create_app(gateway_service=service))
    instance_id = seeded["instance"]["workflow_instance_id"]
    station_run_id = seeded["runs"][0]["station_run_id"]
    artifact_id = seeded["runs"][0]["output_artifact_ids"][0]

    assert client.get(f"/bff/workflows{SCOPE_QUERY}").json()[0]["workflow_template_id"] == seeded["template"]["workflow_template_id"]
    assert client.get(f"/bff/workflows/{seeded['template']['workflow_template_id']}/versions{SCOPE_QUERY}").json()[0]["version"] == "1.0.0"
    assert client.get(f"/bff/instances{SCOPE_QUERY}").json()[0]["workflow_instance_id"] == instance_id
    assert client.get(f"/bff/instances/{instance_id}/status{SCOPE_QUERY}").json()["workflow_instance_id"] == instance_id
    board = client.get(f"/bff/instances/{instance_id}/board{SCOPE_QUERY}").json()
    assert board["workflow_instance"]["workflow_instance_id"] == instance_id
    outputs = client.get(f"/bff/instances/{instance_id}/stations/{station_run_id}/outputs{SCOPE_QUERY}").json()
    assert outputs[0]["artifact_id"] == artifact_id
    metadata = client.get(f"/bff/instances/{instance_id}/artifacts/{artifact_id}/metadata{SCOPE_QUERY}").json()
    assert metadata["artifact_id"] == artifact_id
    lineage = client.get(f"/bff/instances/{instance_id}/artifacts/{artifact_id}/lineage{SCOPE_QUERY}").json()
    assert lineage["artifacts"]
    raw = json.dumps({"board": board, "outputs": outputs, "metadata": metadata, "lineage": lineage}, ensure_ascii=False)
    for forbidden in ("capability_token", "subscription_token", "Authorization", "raw_trace_payload", "raw_artifact_content", "raw_connector_payload"):
        assert forbidden not in raw


def test_bff_patch_propose_and_diff_routes_return_redacted_dtos(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("HARNESS_V3_5_DEV_MODE", "1")
    service = _gateway(tmp_path)
    seeded = asyncio.run(_seed(service, "v4_a2_patch_routes"))
    template_id = seeded["template"]["workflow_template_id"]
    asyncio.run(
        _rpc(
            service,
            "workflow.template.update_draft",
            {"workflow_template_id": template_id, "draft": seeded["version"]["snapshot"], "scope": _scope()},
        )
    )
    client = TestClient(create_app(gateway_service=service))

    proposed = client.post(
        f"/bff/workflows/{template_id}/patches{SCOPE_QUERY}",
        json={
            "source": "inspector",
            "intent_type": "inspector_update",
            "operation": "update_station_prompt",
            "workflow_instance_id": seeded["instance"]["workflow_instance_id"],
            "payload": {"station_id": "station_a", "prompt_ref": "v4.a2.prompt"},
        },
    ).json()
    assert proposed["workflow_template_id"] == template_id
    diff = client.get(f"/bff/workflows/{template_id}/patches/{proposed['workflow_patch_id']}/diff{SCOPE_QUERY}").json()
    assert diff["workflow_patch_id"] == proposed["workflow_patch_id"]
    raw = json.dumps({"proposed": proposed, "diff": diff}, ensure_ascii=False)
    assert "secret" not in raw
    assert "raw_trace_payload" not in raw


def test_bff_routes_enforce_capability_and_instance_ownership(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("HARNESS_CAPABILITY_TOKEN_SECRET", SECRET)
    monkeypatch.delenv("HARNESS_V3_5_DEV_MODE", raising=False)
    service = _gateway(tmp_path)
    seeded = asyncio.run(_seed(service, "v4_a2_auth"))
    client = TestClient(create_app(gateway_service=service))
    instance_id = seeded["instance"]["workflow_instance_id"]
    station_run_id = seeded["runs"][0]["station_run_id"]

    def token(capabilities: tuple[str, ...], project_id: str = "demo") -> str:
        return issue_capability_token(
            app_profile=service.app_registry.get("meeting"),
            project_id=project_id,
            workspace_id="local",
            capabilities=capabilities,
            allowed_origins=(ORIGIN,),
            secret=SECRET,
        )

    no_board = {"Authorization": f"Bearer {token(('workflows.read',))}", "Origin": ORIGIN}
    board_headers = {"Authorization": f"Bearer {token(('board.read',))}", "Origin": ORIGIN}
    station_headers = {"Authorization": f"Bearer {token(('stations.read',))}", "Origin": ORIGIN}
    assert client.get(f"/bff/instances/{instance_id}/board", headers=no_board).json()["error"]["code"] == "CAPABILITY_DENIED"
    assert client.get(f"/bff/instances/{instance_id}/board", headers=board_headers).json()["workflow_instance"]["workflow_instance_id"] == instance_id
    assert (
        client.get(
            f"/bff/instances/{instance_id}/stations/not_a_run/outputs",
            headers=station_headers,
        ).json()["error"]["code"]
        == "STATION_RUN_NOT_FOUND"
    )
    assert client.get(f"/bff/instances/{instance_id}/stations/{station_run_id}/outputs", headers=station_headers).status_code == 200
