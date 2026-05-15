"""V3.6-C deterministic workflow runtime MVP tests."""

from __future__ import annotations

import asyncio
import json

from fastapi.testclient import TestClient

from apps.api import create_app
from apps.gateway.protocol import RpcRequest
from apps.gateway.service import GatewayService
from core.protocol.auth import issue_capability_token


SECRET = "v3-6-c-secret"
LOCAL_ORIGIN = "http://localhost:5173"


def _scope(app_id: str = "meeting", project_id: str = "demo", workspace_id: str = "local") -> dict[str, str]:
    return {"app_id": app_id, "project_id": project_id, "workspace_id": workspace_id}


def _template(template_id: str = "workflow_demo", *, name: str = "Demo Workflow") -> dict:
    return {
        "workflow_template_id": template_id,
        "name": name,
        "stations": [
            {"station_id": "station_a", "name": "A"},
            {"station_id": "station_b", "name": "B"},
        ],
        "edges": [
            {
                "edge_id": "edge_a_b",
                "from_station_id": "station_a",
                "to_station_id": "station_b",
                "order": 1,
            }
        ],
    }


def _branching_template() -> dict:
    return {
        "workflow_template_id": "workflow_branching",
        "name": "Branching Workflow",
        "stations": [
            {"station_id": "station_a", "name": "A"},
            {"station_id": "station_b", "name": "B"},
            {"station_id": "station_c", "name": "C"},
        ],
        "edges": [
            {"edge_id": "edge_a_b", "from_station_id": "station_a", "to_station_id": "station_b", "order": 1},
            {"edge_id": "edge_a_c", "from_station_id": "station_a", "to_station_id": "station_c", "order": 2},
        ],
    }


async def _rpc(service: GatewayService, method: str, params: dict | None = None):
    return await service.handle_rpc(RpcRequest(id=method, method=method, params=params or {}))


async def _publish(service: GatewayService, template: dict | None = None, *, version: str = "1.0.0"):
    created = await _rpc(service, "workflow.template.create", {"template": template or _template(), "scope": _scope()})
    assert created.error is None
    published = await _rpc(
        service,
        "workflow.template.publish",
        {"workflow_template_id": (template or _template())["workflow_template_id"], "version": version, "scope": _scope()},
    )
    assert published.error is None
    return published.result["version"]


def test_start_uses_published_version_snapshot_and_step_mode() -> None:
    async def run() -> None:
        service = GatewayService()
        version = await _publish(service)
        update = await _rpc(
            service,
            "workflow.template.update_draft",
            {"workflow_template_id": "workflow_demo", "draft": _template(name="Draft changed"), "scope": _scope()},
        )
        assert update.error is None

        started = await _rpc(
            service,
            "workflow.instance.start",
            {"workflow_version_id": version["workflow_version_id"], "max_steps": 1, "scope": _scope()},
        )
        assert started.error is None
        instance = started.result["workflow_instance"]
        assert instance["workflow_version_id"] == version["workflow_version_id"]
        assert instance["status"] == "running"
        assert instance["metadata"]["station_order"] == ["station_a", "station_b"]
        assert started.result["resolved_version"]["workflow_version_id"] == version["workflow_version_id"]
        assert len(started.result["station_runs"]) == 1
        assert started.result["station_runs"][0]["station_id"] == "station_a"

        get_job = await _rpc(service, "job.get", {"job_id": started.result["station_runs"][0]["job_id"], "scope": _scope()})
        assert get_job.error is None
        assert get_job.result["job"]["metadata"]["workflow_instance_id"] == instance["workflow_instance_id"]

        artifact_id = started.result["station_runs"][0]["output_artifact_ids"][0]
        metadata = await _rpc(service, "artifact.read_metadata", {"artifact_id": artifact_id, "scope": _scope()})
        assert metadata.error is None
        assert metadata.result["artifact"]["metadata"]["workflow"]["workflow_instance_id"] == instance["workflow_instance_id"]

    asyncio.run(run())


def test_pause_resume_cancel_and_status_state_machine() -> None:
    async def run() -> None:
        service = GatewayService()
        version = await _publish(service)
        started = await _rpc(service, "workflow.instance.start", {"workflow_version_id": version["workflow_version_id"], "max_steps": 1, "scope": _scope()})
        instance_id = started.result["workflow_instance"]["workflow_instance_id"]

        paused = await _rpc(service, "workflow.instance.pause", {"workflow_instance_id": instance_id, "scope": _scope()})
        assert paused.error is None
        assert paused.result["workflow_instance"]["status"] == "paused"

        paused_again = await _rpc(service, "workflow.instance.pause", {"workflow_instance_id": instance_id, "scope": _scope()})
        assert paused_again.error.code == "WORKFLOW_INVALID_STATE"

        status = await _rpc(service, "workflow.instance.status", {"workflow_instance_id": instance_id, "scope": _scope()})
        assert status.result["status"]["status"] == "paused"
        assert status.result["status"]["station_run_count"] == 1

        resumed = await _rpc(service, "workflow.instance.resume", {"workflow_instance_id": instance_id, "max_steps": 1, "scope": _scope()})
        assert resumed.error is None
        assert resumed.result["workflow_instance"]["status"] == "completed"
        runs = await _rpc(service, "station.run.list", {"workflow_instance_id": instance_id, "scope": _scope()})
        assert [run["station_id"] for run in runs.result["station_runs"]] == ["station_a", "station_b"]
        assert runs.result["station_runs"][1]["input_artifact_ids"] == runs.result["station_runs"][0]["output_artifact_ids"]

        cancel_completed = await _rpc(service, "workflow.instance.cancel", {"workflow_instance_id": instance_id, "scope": _scope()})
        assert cancel_completed.error.code == "WORKFLOW_INVALID_STATE"

        second = await _rpc(service, "workflow.instance.start", {"workflow_version_id": version["workflow_version_id"], "max_steps": 1, "scope": _scope()})
        second_id = second.result["workflow_instance"]["workflow_instance_id"]
        cancelled = await _rpc(service, "workflow.instance.cancel", {"workflow_instance_id": second_id, "scope": _scope()})
        assert cancelled.error is None
        assert cancelled.result["workflow_instance"]["status"] == "cancelled"
        cancelled_again = await _rpc(service, "workflow.instance.cancel", {"workflow_instance_id": second_id, "scope": _scope()})
        assert cancelled_again.error is None
        assert cancelled_again.result["idempotent"] is True

    asyncio.run(run())


def test_full_auto_run_rerun_and_retry_boundaries() -> None:
    async def run() -> None:
        service = GatewayService()
        version = await _publish(service)
        started = await _rpc(service, "workflow.instance.start", {"workflow_version_id": version["workflow_version_id"], "scope": _scope()})
        assert started.error is None
        assert started.result["workflow_instance"]["status"] == "completed"
        instance_id = started.result["workflow_instance"]["workflow_instance_id"]

        runs = await _rpc(service, "station.run.list", {"workflow_instance_id": instance_id, "scope": _scope()})
        old = runs.result["station_runs"][0]
        rerun = await _rpc(service, "station.rerun", {"station_run_id": old["station_run_id"], "scope": _scope()})
        assert rerun.error is None
        assert rerun.result["station_run"]["attempt"] == old["attempt"] + 1
        assert rerun.result["station_run"]["rerun_of_station_run_id"] == old["station_run_id"]
        assert rerun.result["station_run"]["output_artifact_ids"] != old["output_artifact_ids"]

        retry_completed = await _rpc(service, "workflow.instance.retry", {"workflow_instance_id": instance_id, "scope": _scope()})
        assert retry_completed.error.code == "WORKFLOW_INVALID_STATE"

    asyncio.run(run())


def test_unsupported_graph_returns_contract_error_and_no_runtime_creep() -> None:
    async def run() -> None:
        service = GatewayService()
        approval_count_before = len(service.core_service.list_approvals(app_id="meeting", project_id="demo", workspace_id="local"))
        trace_count_before = len([
            record for record in service.trace_store.list_records(app_id="meeting", project_id="demo", workspace_id="local")
            if str(record.get("event_type", "")).startswith(("quality.", "workflow.patch.", "business."))
        ])
        version = await _publish(service, _branching_template())
        started = await _rpc(service, "workflow.instance.start", {"workflow_version_id": version["workflow_version_id"], "scope": _scope()})
        assert started.error.code == "WORKFLOW_RUNTIME_UNSUPPORTED"

        assert len(service.core_service.list_approvals(app_id="meeting", project_id="demo", workspace_id="local")) == approval_count_before
        assert len([
            record for record in service.trace_store.list_records(app_id="meeting", project_id="demo", workspace_id="local")
            if str(record.get("event_type", "")).startswith(("quality.", "workflow.patch.", "business."))
        ]) == trace_count_before
        raw_trace = json.dumps(service.trace_store.list_records(app_id="meeting", project_id="demo", workspace_id="local"), ensure_ascii=False)
        for token in ("capability_token", "subscription_token", "Authorization", "Bearer ", "secret"):
            assert token not in raw_trace

    asyncio.run(run())


def _client(monkeypatch, gateway: GatewayService) -> TestClient:
    monkeypatch.setenv("HARNESS_CAPABILITY_TOKEN_SECRET", SECRET)
    monkeypatch.delenv("HARNESS_V3_5_DEV_MODE", raising=False)
    return TestClient(create_app(gateway_service=gateway))


def _token(gateway: GatewayService, capabilities: tuple[str, ...]) -> str:
    return issue_capability_token(
        app_profile=gateway.app_registry.get("meeting"),
        project_id="demo",
        workspace_id="local",
        capabilities=capabilities,
        allowed_origins=(LOCAL_ORIGIN,),
        secret=SECRET,
    )


def _headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}", "Origin": LOCAL_ORIGIN}


def test_external_capabilities_for_runtime_methods(monkeypatch) -> None:
    gateway = GatewayService()
    version = asyncio.run(_publish(gateway))
    client = _client(monkeypatch, gateway)
    read = _headers(_token(gateway, ("workflows.read",)))
    execute = _headers(_token(gateway, ("workflows.execute",)))
    stations_read = _headers(_token(gateway, ("stations.read",)))
    stations_execute = _headers(_token(gateway, ("stations.execute",)))

    denied_start = client.post("/v1/rpc", json={"id": "s", "method": "workflow.instance.start", "params": {"workflow_version_id": version["workflow_version_id"]}}, headers=read)
    assert denied_start.json()["error"]["code"] == "CAPABILITY_DENIED"

    started = client.post("/v1/rpc", json={"id": "s", "method": "workflow.instance.start", "params": {"workflow_version_id": version["workflow_version_id"], "max_steps": 1}}, headers=execute)
    assert started.json()["result"]["workflow_instance"]["status"] == "running"
    instance_id = started.json()["result"]["workflow_instance"]["workflow_instance_id"]
    station_run_id = started.json()["result"]["station_runs"][0]["station_run_id"]

    denied_get = client.post("/v1/rpc", json={"id": "g", "method": "workflow.instance.get", "params": {"workflow_instance_id": instance_id}}, headers=execute)
    assert denied_get.json()["error"]["code"] == "CAPABILITY_DENIED"
    get_ok = client.post("/v1/rpc", json={"id": "g", "method": "workflow.instance.get", "params": {"workflow_instance_id": instance_id}}, headers=read)
    assert get_ok.json()["result"]["workflow_instance"]["workflow_instance_id"] == instance_id

    denied_station_get = client.post("/v1/rpc", json={"id": "r", "method": "station.run.get", "params": {"station_run_id": station_run_id}}, headers=read)
    assert denied_station_get.json()["error"]["code"] == "CAPABILITY_DENIED"
    station_get = client.post("/v1/rpc", json={"id": "r", "method": "station.run.get", "params": {"station_run_id": station_run_id}}, headers=stations_read)
    assert station_get.json()["result"]["station_run"]["station_run_id"] == station_run_id

    denied_rerun = client.post("/v1/rpc", json={"id": "rr", "method": "station.rerun", "params": {"station_run_id": station_run_id}}, headers=stations_read)
    assert denied_rerun.json()["error"]["code"] == "CAPABILITY_DENIED"
    rerun = client.post("/v1/rpc", json={"id": "rr", "method": "station.rerun", "params": {"station_run_id": station_run_id}}, headers=stations_execute)
    assert rerun.json()["result"]["station_run"]["rerun_of_station_run_id"] == station_run_id

    scope_all = client.post("/v1/rpc", json={"id": "bad", "method": "workflow.instance.get", "params": {"workflow_instance_id": instance_id, "scope_mode": "all"}}, headers=read)
    assert scope_all.json()["error"]["code"] == "METHOD_FORBIDDEN"
