"""V3.6-G pipeline board data API tests."""

from __future__ import annotations

import asyncio
import json

from fastapi.testclient import TestClient

from apps.api import create_app
from apps.gateway.approvals import APPROVAL_PENDING, ApprovalStore
from apps.gateway.artifacts import ArtifactRegistry
from apps.gateway.protocol import RpcRequest
from apps.gateway.runtime import GatewayRuntimePool
from apps.gateway.service import GatewayService
from apps.gateway.storage import GatewaySessionStore
from apps.gateway.traces import TraceStore
from core.protocol.auth import issue_capability_token
from core.protocol.schemas.methods import METHOD_SCHEMAS


SECRET = "v3-6-g-secret"
LOCAL_ORIGIN = "http://localhost:5173"


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


def _board_template(template_id: str = "workflow_board") -> dict:
    return {
        "workflow_template_id": template_id,
        "name": "Board Workflow",
        "stations": [
            {
                "station_id": "station_a",
                "name": "A",
                "output_contracts": [{"contract_id": "a_out", "artifact_kind": "artifact_a", "direction": "output"}],
            },
            {
                "station_id": "station_b",
                "name": "B",
                "approval_required": True,
                "input_contracts": [{"contract_id": "a_in", "artifact_kind": "artifact_a", "direction": "input"}],
                "output_contracts": [{"contract_id": "b_out", "artifact_kind": "artifact_b", "direction": "output"}],
            },
        ],
        "edges": [{"edge_id": "a_to_b", "from_station_id": "station_a", "to_station_id": "station_b"}],
        "quality_contracts": [{"contract_id": "q", "rubric_id": "rubric_a", "threshold": 0.8}],
    }


async def _rpc(service: GatewayService, method: str, params: dict | None = None):
    return await service.handle_rpc(RpcRequest(id=method, method=method, params=params or {}))


async def _started_board(service: GatewayService, template_id: str = "workflow_board"):
    created = await _rpc(service, "workflow.template.create", {"template": _board_template(template_id), "scope": _scope()})
    assert created.error is None
    published = await _rpc(
        service,
        "workflow.template.publish",
        {"workflow_template_id": template_id, "version": "1.0.0", "scope": _scope()},
    )
    assert published.error is None
    started = await _rpc(
        service,
        "workflow.instance.start",
        {"workflow_version_id": published.result["version"]["workflow_version_id"], "scope": _scope()},
    )
    assert started.error is None
    instance = started.result["workflow_instance"]
    runs = (await _rpc(service, "station.run.list", {"workflow_instance_id": instance["workflow_instance_id"], "scope": _scope()})).result["station_runs"]
    station_a = next(run for run in runs if run["station_id"] == "station_a")
    station_b = next(run for run in runs if run["station_id"] == "station_b")
    return instance, station_a, station_b


def test_board_get_returns_redacted_pipeline_summary_without_mutation(tmp_path) -> None:
    async def run() -> None:
        service = _gateway(tmp_path)
        instance, station_a, station_b = await _started_board(service)
        artifact_id = station_a["output_artifact_ids"][0]
        quality = await _rpc(
            service,
            "quality.evaluation.create",
            {
                "evaluation": {
                    "workflow_instance_id": instance["workflow_instance_id"],
                    "station_run_id": station_a["station_run_id"],
                    "artifact_id": artifact_id,
                    "rubric_id": "rubric_a",
                    "evaluator_type": "rule",
                    "score": 0.9,
                    "issues": [{"raw_artifact_content": "do not leak", "secret": "secret-token-value"}],
                    "metadata": {"raw_trace_payload": "do not leak"},
                },
                "auto_attach": True,
                "scope": _scope(),
            },
        )
        assert quality.error is None
        before_instance = (await _rpc(service, "workflow.instance.get", {"workflow_instance_id": instance["workflow_instance_id"], "scope": _scope()})).result["workflow_instance"]
        before_station = (await _rpc(service, "station.run.get", {"station_run_id": station_a["station_run_id"], "scope": _scope()})).result["station_run"]

        board = await _rpc(service, "workflow.board.get", {"workflow_instance_id": instance["workflow_instance_id"], "scope": _scope()})
        assert board.error is None
        payload = board.result["board"]
        assert payload["workflow_instance"]["workflow_instance_id"] == instance["workflow_instance_id"]
        assert {entry["station"]["station_id"] for entry in payload["stations"]} == {"station_a", "station_b"}
        assert payload["jobs"][0]["job_id"] == station_a["job_id"]
        assert payload["artifacts"][0]["artifact_id"] == artifact_id
        assert payload["quality_evaluations"][0]["evaluation_id"] == quality.result["evaluation"]["evaluation_id"]
        assert payload["approvals"][0]["status"] == APPROVAL_PENDING
        assert payload["trace_summary"]["count"] >= 1
        station_b_summary = next(entry for entry in payload["stations"] if entry["station"]["station_id"] == "station_b")
        assert station_b_summary["status"] == "waiting_approval"
        raw = json.dumps(payload, ensure_ascii=False)
        for forbidden in ("secret-token-value", "raw_artifact_content", "raw_trace_payload", "Authorization", "Bearer "):
            assert forbidden not in raw

        after_instance = (await _rpc(service, "workflow.instance.get", {"workflow_instance_id": instance["workflow_instance_id"], "scope": _scope()})).result["workflow_instance"]
        after_station = (await _rpc(service, "station.run.get", {"station_run_id": station_a["station_run_id"], "scope": _scope()})).result["station_run"]
        assert after_instance["status"] == before_instance["status"]
        assert after_station["status"] == before_station["status"]
        assert after_station["quality_evaluation_ids"] == before_station["quality_evaluation_ids"]

    asyncio.run(run())


def test_workflow_status_and_station_output_list(tmp_path) -> None:
    async def run() -> None:
        service = _gateway(tmp_path)
        instance, station_a, _ = await _started_board(service, "workflow_board_status")
        status = await _rpc(service, "workflow.instance.status", {"workflow_instance_id": instance["workflow_instance_id"], "scope": _scope()})
        assert status.error is None
        assert status.result["status"]["status"] == "waiting_approval"
        assert status.result["status"]["station_run_status_counts"]["completed"] == 1
        assert status.result["status"]["station_run_status_counts"]["waiting_approval"] == 1
        outputs = await _rpc(service, "station.output.list", {"station_run_id": station_a["station_run_id"], "scope": _scope()})
        assert outputs.error is None
        assert outputs.result["count"] == 1
        assert outputs.result["artifacts"][0]["artifact_id"] == station_a["output_artifact_ids"][0]
        raw = json.dumps(outputs.result, ensure_ascii=False)
        assert "raw_artifact_content" not in raw

    asyncio.run(run())


def test_board_scope_capability_and_method_metadata(monkeypatch, tmp_path) -> None:
    service = _gateway(tmp_path)
    monkeypatch.setenv("HARNESS_CAPABILITY_TOKEN_SECRET", SECRET)
    monkeypatch.delenv("HARNESS_V3_5_DEV_MODE", raising=False)
    client = TestClient(create_app(gateway_service=service))
    instance, station_a, _ = asyncio.run(_started_board(service, "workflow_board_auth"))
    schema_by_method = {entry["method"]: entry for entry in METHOD_SCHEMAS}
    assert schema_by_method["workflow.board.get"]["runtime_handler"] is True
    assert schema_by_method["workflow.board.get"]["sdk_exposure"] == "workflow_runtime"
    assert schema_by_method["station.output.list"]["runtime_handler"] is True

    def token(capabilities: tuple[str, ...]) -> str:
        return issue_capability_token(
            app_profile=service.app_registry.get("meeting"),
            project_id="demo",
            workspace_id="local",
            capabilities=capabilities,
            allowed_origins=(LOCAL_ORIGIN,),
            secret=SECRET,
        )

    no_board = {"Authorization": f"Bearer {token(('workflows.read',))}", "Origin": LOCAL_ORIGIN}
    board_headers = {"Authorization": f"Bearer {token(('board.read',))}", "Origin": LOCAL_ORIGIN}
    station_headers = {"Authorization": f"Bearer {token(('stations.read',))}", "Origin": LOCAL_ORIGIN}
    denied = client.post(
        "/v1/rpc",
        json={"id": "b", "method": "workflow.board.get", "params": {"workflow_instance_id": instance["workflow_instance_id"]}},
        headers=no_board,
    )
    assert denied.json()["error"]["code"] == "CAPABILITY_DENIED"
    ok = client.post(
        "/v1/rpc",
        json={"id": "b", "method": "workflow.board.get", "params": {"workflow_instance_id": instance["workflow_instance_id"]}},
        headers=board_headers,
    )
    assert ok.json()["result"]["board"]["workflow_instance"]["workflow_instance_id"] == instance["workflow_instance_id"]
    output_denied = client.post(
        "/v1/rpc",
        json={"id": "o", "method": "station.output.list", "params": {"station_run_id": station_a["station_run_id"]}},
        headers=board_headers,
    )
    assert output_denied.json()["error"]["code"] == "CAPABILITY_DENIED"
    output_ok = client.post(
        "/v1/rpc",
        json={"id": "o", "method": "station.output.list", "params": {"station_run_id": station_a["station_run_id"]}},
        headers=station_headers,
    )
    assert output_ok.json()["result"]["count"] == 1

    mismatch = asyncio.run(
        _rpc(service, "workflow.board.get", {"workflow_instance_id": instance["workflow_instance_id"], "scope": _scope(app_id="knowledge")})
    )
    assert mismatch.error.code == "SCOPE_MISMATCH"


def test_board_api_no_business_or_patch_runtime_creep(tmp_path) -> None:
    async def run() -> None:
        service = _gateway(tmp_path)
        instance, _, _ = await _started_board(service, "workflow_board_no_creep")
        board = await _rpc(service, "workflow.board.get", {"workflow_instance_id": instance["workflow_instance_id"], "scope": _scope()})
        assert board.error is None
        traces = json.dumps(service.trace_store.list_records(app_id="meeting", project_id="demo", workspace_id="local"), ensure_ascii=False)
        assert "business." not in traces
        assert "workflow.patch." not in traces

    asyncio.run(run())
