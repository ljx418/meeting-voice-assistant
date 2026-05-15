"""V3.6-D workflow approval point integration tests."""

from __future__ import annotations

import asyncio
import json
from concurrent.futures import ThreadPoolExecutor

from fastapi.testclient import TestClient

from apps.api import create_app
from apps.gateway.approvals import APPROVAL_APPROVED, APPROVAL_PENDING, ApprovalStore
from apps.gateway.artifacts import ArtifactRegistry
from apps.gateway.protocol import RpcRequest
from apps.gateway.runtime import GatewayRuntimePool
from apps.gateway.service import GatewayService
from apps.gateway.storage import GatewaySessionStore
from apps.gateway.traces import TraceStore
from core.protocol.auth import issue_capability_token
from core.protocol.schemas.events import EVENT_SCHEMAS


SECRET = "v3-6-d-secret"
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


def _approval_template(template_id: str = "workflow_approval") -> dict:
    return {
        "workflow_template_id": template_id,
        "name": "Approval Workflow",
        "stations": [
            {"station_id": "station_a", "name": "A"},
            {"station_id": "station_b", "name": "B", "approval_required": True},
            {"station_id": "station_c", "name": "C"},
        ],
        "edges": [
            {"edge_id": "edge_a_b", "from_station_id": "station_a", "to_station_id": "station_b", "order": 1},
            {"edge_id": "edge_b_c", "from_station_id": "station_b", "to_station_id": "station_c", "order": 2},
        ],
    }


def _single_approval_template(template_id: str = "workflow_single_approval") -> dict:
    payload = _approval_template(template_id)
    payload["stations"] = [payload["stations"][1]]
    payload["edges"] = []
    return payload


async def _rpc(service: GatewayService, method: str, params: dict | None = None):
    return await service.handle_rpc(RpcRequest(id=method, method=method, params=params or {}))


async def _publish(service: GatewayService, template: dict | None = None, *, version: str = "1.0.0") -> dict:
    payload = template or _approval_template()
    created = await _rpc(service, "workflow.template.create", {"template": payload, "scope": _scope()})
    assert created.error is None
    published = await _rpc(
        service,
        "workflow.template.publish",
        {"workflow_template_id": payload["workflow_template_id"], "version": version, "scope": _scope()},
    )
    assert published.error is None
    return published.result["version"]


async def _start_to_waiting(service: GatewayService, template: dict | None = None, *, max_steps: int | None = None):
    version = await _publish(service, template)
    params = {"workflow_version_id": version["workflow_version_id"], "scope": _scope()}
    if max_steps is not None:
        params["max_steps"] = max_steps
    started = await _rpc(service, "workflow.instance.start", params)
    assert started.error is None
    return started.result


def _waiting_approval(service: GatewayService) -> dict:
    approvals = service.approval_store.list_approvals(status=APPROVAL_PENDING, app_id="meeting", project_id="demo", workspace_id="local")
    assert len(approvals) == 1
    return approvals[0]


def _sse_events(body: str) -> list[dict]:
    events = []
    for frame in body.strip().split("\n\n"):
        data = "".join(line.removeprefix("data: ") for line in frame.splitlines() if line.startswith("data: "))
        if data:
            events.append(json.loads(data))
    return events


def _assert_event_matches_schema(event: dict, event_type: str, channel: str) -> None:
    schema = next(item for item in EVENT_SCHEMAS if item["type"] == event_type)
    assert set(schema["envelope_schema"]["required"]) <= set(event)
    assert event["type"] == event_type
    assert event["channel"] == channel
    assert isinstance(event["data"], dict)


def test_pre_execution_approval_waits_before_job_artifact_and_downstream(tmp_path) -> None:
    async def run() -> None:
        service = _gateway(tmp_path)
        started = await _start_to_waiting(service, _single_approval_template())
        instance = started["workflow_instance"]
        assert instance["status"] == "waiting_approval"
        runs = await _rpc(service, "station.run.list", {"workflow_instance_id": instance["workflow_instance_id"], "scope": _scope()})
        waiting = runs.result["station_runs"][0]
        assert waiting["status"] == "waiting_approval"
        assert waiting["job_id"] is None
        assert waiting["output_artifact_ids"] == []
        assert service.core_service.list_jobs(app_id="meeting", project_id="demo", workspace_id="local") == []
        assert service.artifact_registry.list_artifacts(app_id="meeting", project_id="demo", workspace_id="local") == []
        approval = _waiting_approval(service)
        binding = approval["metadata"]["workflow_binding"]
        assert binding["station_run_id"] == waiting["station_run_id"]
        assert binding["active"] is True
        assert binding["workflow_side_effect_status"] == "pending"

        resume = await _rpc(service, "workflow.instance.resume", {"workflow_instance_id": instance["workflow_instance_id"], "scope": _scope()})
        assert resume.error.code == "WORKFLOW_APPROVAL_REQUIRED"
        assert len(service.approval_store.list_approvals(status=APPROVAL_PENDING, app_id="meeting", project_id="demo", workspace_id="local")) == 1

    asyncio.run(run())


def test_approve_resumes_once_and_reject_blocks_workflow(tmp_path) -> None:
    async def run() -> None:
        service = _gateway(tmp_path)
        started = await _start_to_waiting(service)
        approval = _waiting_approval(service)
        approved = await _rpc(
            service,
            "approval.respond",
            {"approval_id": approval["approval_id"], "decision": "approve", "scope": _scope()},
        )
        assert approved.error is None
        assert approved.result["workflow_side_effect"]["status"] == "applied"
        assert approved.result["workflow_side_effect"]["replayed"] is False
        instance_id = started["workflow_instance"]["workflow_instance_id"]
        runs = await _rpc(service, "station.run.list", {"workflow_instance_id": instance_id, "scope": _scope()})
        assert [run["status"] for run in runs.result["station_runs"]] == ["completed", "completed", "completed"]
        assert [run["station_id"] for run in runs.result["station_runs"]] == ["station_a", "station_b", "station_c"]
        assert runs.result["station_runs"][1]["job_id"]
        assert runs.result["station_runs"][1]["output_artifact_ids"]

        repeated = await _rpc(
            service,
            "approval.respond",
            {"approval_id": approval["approval_id"], "decision": "approve", "scope": _scope()},
        )
        assert repeated.error is None
        assert repeated.result["idempotent"] is True
        assert repeated.result["workflow_side_effect"]["replayed"] is True
        again = await _rpc(service, "station.run.list", {"workflow_instance_id": instance_id, "scope": _scope()})
        assert len(again.result["station_runs"]) == 3

        reject_service = _gateway(tmp_path / "reject")
        reject_started = await _start_to_waiting(reject_service)
        reject_approval = _waiting_approval(reject_service)
        rejected = await _rpc(
            reject_service,
            "approval.respond",
            {"approval_id": reject_approval["approval_id"], "decision": "reject", "scope": _scope()},
        )
        assert rejected.error is None
        blocked = await _rpc(
            reject_service,
            "workflow.instance.get",
            {"workflow_instance_id": reject_started["workflow_instance"]["workflow_instance_id"], "scope": _scope()},
        )
        assert blocked.result["workflow_instance"]["status"] == "blocked"
        reject_runs = await _rpc(reject_service, "station.run.list", {"workflow_instance_id": blocked.result["workflow_instance"]["workflow_instance_id"], "scope": _scope()})
        assert reject_runs.result["station_runs"][1]["status"] == "failed"
        assert reject_runs.result["station_runs"][1]["failure_context"]["reason"] == "approval_rejected"
        assert len(reject_runs.result["station_runs"]) == 2

    asyncio.run(run())


def test_approve_recovery_for_approved_decision_missing_side_effect(tmp_path) -> None:
    async def run() -> None:
        service = _gateway(tmp_path)
        await _start_to_waiting(service, _single_approval_template())
        approval = _waiting_approval(service)
        service.approval_store.respond(approval["approval_id"], status=APPROVAL_APPROVED)

        recovered = await _rpc(
            service,
            "approval.respond",
            {"approval_id": approval["approval_id"], "decision": "approve", "scope": _scope()},
        )
        assert recovered.error is None
        assert recovered.result["idempotent"] is True
        assert recovered.result["workflow_side_effect"]["status"] == "recovered"
        final = service.approval_store.get_approval(approval["approval_id"])
        assert final["metadata"]["workflow_binding"]["workflow_side_effect_status"] == "applied"

    asyncio.run(run())


def test_cancel_waiting_approval_marks_inactive_and_late_approval_does_not_decide(tmp_path) -> None:
    async def run() -> None:
        service = _gateway(tmp_path)
        started = await _start_to_waiting(service, _single_approval_template())
        approval = _waiting_approval(service)
        instance_id = started["workflow_instance"]["workflow_instance_id"]
        cancelled = await _rpc(service, "workflow.instance.cancel", {"workflow_instance_id": instance_id, "scope": _scope()})
        assert cancelled.error is None
        late = await _rpc(
            service,
            "approval.respond",
            {"approval_id": approval["approval_id"], "decision": "approve", "scope": _scope()},
        )
        assert late.error.code == "WORKFLOW_APPROVAL_INACTIVE"
        unchanged = service.approval_store.get_approval(approval["approval_id"])
        assert unchanged["status"] == APPROVAL_PENDING
        assert unchanged["metadata"]["workflow_binding"]["active"] is False
        assert unchanged["metadata"]["workflow_binding"]["inactive_reason"] == "workflow_cancelled"
        runs = await _rpc(service, "station.run.list", {"workflow_instance_id": instance_id, "scope": _scope()})
        assert runs.result["station_runs"][0]["status"] == "cancelled"

    asyncio.run(run())


def test_approve_respects_step_mode_and_does_not_run_downstream(tmp_path) -> None:
    async def run() -> None:
        service = _gateway(tmp_path)
        version = await _publish(service)
        started = await _rpc(service, "workflow.instance.start", {"workflow_version_id": version["workflow_version_id"], "max_steps": 1, "scope": _scope()})
        instance_id = started.result["workflow_instance"]["workflow_instance_id"]
        paused = await _rpc(service, "workflow.instance.pause", {"workflow_instance_id": instance_id, "scope": _scope()})
        assert paused.error is None
        resumed = await _rpc(service, "workflow.instance.resume", {"workflow_instance_id": instance_id, "max_steps": 1, "scope": _scope()})
        assert resumed.error is None
        assert resumed.result["workflow_instance"]["status"] == "waiting_approval"
        approval = _waiting_approval(service)
        approved = await _rpc(service, "approval.respond", {"approval_id": approval["approval_id"], "decision": "approve", "scope": _scope()})
        assert approved.error is None
        instance = await _rpc(service, "workflow.instance.get", {"workflow_instance_id": instance_id, "scope": _scope()})
        assert instance.result["workflow_instance"]["status"] == "running"
        assert instance.result["workflow_instance"]["current_station_ids"] == ["station_c"]
        runs = await _rpc(service, "station.run.list", {"workflow_instance_id": instance_id, "scope": _scope()})
        assert [run["station_id"] for run in runs.result["station_runs"]] == ["station_a", "station_b"]

    asyncio.run(run())


def test_concurrent_approval_and_conflict_are_stable(tmp_path) -> None:
    service = _gateway(tmp_path)
    asyncio.run(_start_to_waiting(service, _single_approval_template()))
    approval = _waiting_approval(service)

    def approve_once() -> str:
        response = asyncio.run(_rpc(service, "approval.respond", {"approval_id": approval["approval_id"], "decision": "approve", "scope": _scope()}))
        return response.error.code if response.error else "ok"

    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(executor.map(lambda _: approve_once(), range(2)))
    assert results.count("ok") >= 1
    runs = asyncio.run(_rpc(service, "station.run.list", {"workflow_instance_id": approval["metadata"]["workflow_binding"]["workflow_instance_id"], "scope": _scope()}))
    assert len(runs.result["station_runs"]) == 1
    assert len(service.core_service.list_jobs(app_id="meeting", project_id="demo", workspace_id="local")) == 1

    conflict_service = _gateway(tmp_path / "conflict")
    asyncio.run(_start_to_waiting(conflict_service, _single_approval_template()))
    conflict_approval = _waiting_approval(conflict_service)
    approved = asyncio.run(_rpc(conflict_service, "approval.respond", {"approval_id": conflict_approval["approval_id"], "decision": "approve", "scope": _scope()}))
    assert approved.error is None
    rejected = asyncio.run(_rpc(conflict_service, "approval.respond", {"approval_id": conflict_approval["approval_id"], "decision": "reject", "scope": _scope()}))
    assert rejected.error.code == "APPROVAL_CONFLICT"


def test_eventbridge_auth_scope_redaction_and_standalone_approval(monkeypatch, tmp_path) -> None:
    service = _gateway(tmp_path)
    started = asyncio.run(_start_to_waiting(service, _single_approval_template()))
    approval = _waiting_approval(service)
    monkeypatch.setenv("HARNESS_CAPABILITY_TOKEN_SECRET", SECRET)
    monkeypatch.delenv("HARNESS_V3_5_DEV_MODE", raising=False)
    client = TestClient(create_app(gateway_service=service))

    approvals_only = issue_capability_token(
        app_profile=service.app_registry.get("meeting"),
        project_id="demo",
        workspace_id="local",
        capabilities=("approvals",),
        allowed_origins=(LOCAL_ORIGIN,),
        secret=SECRET,
    )
    no_approvals = issue_capability_token(
        app_profile=service.app_registry.get("meeting"),
        project_id="demo",
        workspace_id="local",
        capabilities=("workflows.execute",),
        allowed_origins=(LOCAL_ORIGIN,),
        secret=SECRET,
    )
    headers = {"Authorization": f"Bearer {approvals_only}", "Origin": LOCAL_ORIGIN}
    event_token = issue_capability_token(
        app_profile=service.app_registry.get("meeting"),
        project_id="demo",
        workspace_id="local",
        capabilities=("events", "approvals"),
        allowed_origins=(LOCAL_ORIGIN,),
        secret=SECRET,
    )
    event_headers = {"Authorization": f"Bearer {event_token}", "Origin": LOCAL_ORIGIN}
    subscribed = client.post("/v1/rpc", json={"id": "e", "method": "events.subscribe", "params": {"channels": ["approval"]}}, headers=event_headers).json()["result"]
    required_body = client.get(subscribed["eventsource_url"] + "&follow=0").text
    required_events = _sse_events(required_body)
    required = [event for event in required_events if event["approval_id"] == approval["approval_id"] and event["type"] == "approval.required"]
    assert required
    _assert_event_matches_schema(required[0], "approval.required", "approval")
    assert required[0]["data"]["workflow_binding"]["station_run_id"] == approval["metadata"]["workflow_binding"]["station_run_id"]

    denied = client.post("/v1/rpc", json={"id": "d", "method": "approval.respond", "params": {"approval_id": approval["approval_id"], "decision": "approve"}}, headers={"Authorization": f"Bearer {no_approvals}", "Origin": LOCAL_ORIGIN})
    assert denied.json()["error"]["code"] == "CAPABILITY_DENIED"
    ok = client.post("/v1/rpc", json={"id": "a", "method": "approval.respond", "params": {"approval_id": approval["approval_id"], "decision": "approve"}}, headers=headers)
    assert ok.json()["result"]["workflow_side_effect"]["status"] == "applied"

    body = client.get(subscribed["eventsource_url"] + "&follow=0").text
    events = _sse_events(body)
    required = [event for event in events if event["approval_id"] == approval["approval_id"] and event["type"] == "approval.approved"]
    assert required
    _assert_event_matches_schema(required[0], "approval.approved", "approval")
    assert required[0]["data"]["workflow_binding"]["workflow_instance_id"] == started["workflow_instance"]["workflow_instance_id"]

    raw = json.dumps(service.trace_store.list_records(app_id="meeting", project_id="demo", workspace_id="local"), ensure_ascii=False)
    for token_text in ("Bearer ", approvals_only, event_token, "subscription_token", "Authorization", "raw connector payload"):
        assert token_text not in raw

    standalone = service.approval_store.request(action="standalone", request_summary="Standalone", app_id="meeting", project_id="demo", workspace_id="local")
    standalone_result = asyncio.run(_rpc(service, "approval.respond", {"approval_id": standalone["approval_id"], "decision": "approve", "scope": _scope()}))
    assert standalone_result.error is None
    assert standalone_result.result["workflow_side_effect"] is None
