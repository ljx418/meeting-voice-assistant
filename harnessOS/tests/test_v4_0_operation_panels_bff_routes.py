"""V4.0-D operation panel BFF route tests."""

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


SCOPE_QUERY = "?app_id=meeting&project_id=demo&workspace_id=local"
SECRET = "v4-d-bff-routes"
ORIGIN = "http://localhost:5173"


def _scope() -> dict[str, str]:
    return {"app_id": "meeting", "project_id": "demo", "workspace_id": "local"}


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


def _template(template_id: str) -> dict:
    return {
        "workflow_template_id": template_id,
        "name": "V4 D Ops Workflow",
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
        "quality_contracts": [{"contract_id": "quality", "rubric_id": "rubric_a", "threshold": 0.8}],
    }


async def _seed(service: GatewayService, template_id: str = "v4_d_ops"):
    await _rpc(service, "workflow.template.create", {"template": _template(template_id), "scope": _scope()})
    published = await _rpc(service, "workflow.template.publish", {"workflow_template_id": template_id, "version": "1.0.0", "scope": _scope()})
    started = await _rpc(service, "workflow.instance.start", {"workflow_version_id": published["version"]["workflow_version_id"], "scope": _scope()})
    instance = started["workflow_instance"]
    runs = (await _rpc(service, "station.run.list", {"workflow_instance_id": instance["workflow_instance_id"], "scope": _scope()}))["station_runs"]
    station_a = next(run for run in runs if run["station_id"] == "station_a")
    approval = service.approval_store.list_approvals(status="pending", app_id="meeting", project_id="demo", workspace_id="local")[0]
    quality = await _rpc(
        service,
        "quality.evaluation.create",
        {
            "evaluation": {
                "workflow_instance_id": instance["workflow_instance_id"],
                "station_run_id": station_a["station_run_id"],
                "artifact_id": station_a["output_artifact_ids"][0],
                "rubric_id": "rubric_a",
                "evaluator_type": "rule",
                "score": 0.9,
                "issues": [{"raw_artifact_content": "do not leak"}],
                "suggestions": [{"secret": "do not leak"}],
            },
            "auto_attach": True,
            "scope": _scope(),
        },
    )
    return {"instance": instance, "runs": runs, "approval": approval, "quality": quality["evaluation"]}


def test_operation_panel_bff_routes_return_redacted_dtos(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("HARNESS_V3_5_DEV_MODE", "1")
    service = _gateway(tmp_path)
    seeded = asyncio.run(_seed(service))
    instance_id = seeded["instance"]["workflow_instance_id"]
    approval_id = seeded["approval"]["approval_id"]
    client = TestClient(create_app(gateway_service=service))

    approvals = client.get(f"/bff/instances/{instance_id}/approvals{SCOPE_QUERY}").json()
    quality = client.get(f"/bff/instances/{instance_id}/quality{SCOPE_QUERY}").json()
    context = client.get(f"/bff/instances/{instance_id}/context{SCOPE_QUERY}").json()
    assert approvals[0]["approval_id"] == approval_id
    assert quality[0]["rubric_id"] == "rubric_a"
    assert context["business"] == {}
    raw = json.dumps({"approvals": approvals, "quality": quality, "context": context}, ensure_ascii=False)
    for forbidden in ("raw_artifact_content", "secret", "Authorization", "capability_token", "subscription_token"):
        assert forbidden not in raw


def test_approval_respond_requires_explicit_user_action_and_instance_ownership(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("HARNESS_V3_5_DEV_MODE", "1")
    service = _gateway(tmp_path)
    first = asyncio.run(_seed(service, "v4_d_approval_a"))
    second = asyncio.run(_seed(service, "v4_d_approval_b"))
    client = TestClient(create_app(gateway_service=service))
    first_instance = first["instance"]["workflow_instance_id"]
    other_instance = second["instance"]["workflow_instance_id"]
    approval_id = first["approval"]["approval_id"]

    denied = client.post(
        f"/bff/instances/{first_instance}/approvals/{approval_id}/respond{SCOPE_QUERY}",
        json={"decision": "approve", "source": "agent"},
    )
    assert denied.json()["error"]["code"] == "WORKFLOW_ACTION_FORBIDDEN"
    wrong_instance = client.post(
        f"/bff/instances/{other_instance}/approvals/{approval_id}/respond{SCOPE_QUERY}",
        json={"decision": "approve", "source": "approval_panel", "user_confirmed": True},
    )
    assert wrong_instance.json()["error"]["code"] == "SCOPE_MISMATCH"
    ok = client.post(
        f"/bff/instances/{first_instance}/approvals/{approval_id}/respond{SCOPE_QUERY}",
        json={"decision": "approve", "source": "approval_panel", "user_confirmed": True},
    )
    assert ok.json()["status"] == "approved"
    assert ok.json()["resource"]["approval_id"] == approval_id


def test_context_update_and_business_event_are_business_only_and_idempotent(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("HARNESS_V3_5_DEV_MODE", "1")
    monkeypatch.setenv("HARNESS_CAPABILITY_TOKEN_SECRET", "v4-d-events")
    service = _gateway(tmp_path)
    seeded = asyncio.run(_seed(service, "v4_d_context"))
    instance_id = seeded["instance"]["workflow_instance_id"]
    client = TestClient(create_app(gateway_service=service))

    invalid = client.post(
        f"/bff/instances/{instance_id}/context/update{SCOPE_QUERY}",
        json={"op": "set", "path": "system.owner", "value": "bad"},
    )
    assert invalid.json()["error"]["code"] == "WORKFLOW_CONTEXT_SCOPE_MISMATCH"
    updated = client.post(
        f"/bff/instances/{instance_id}/context/update{SCOPE_QUERY}",
        json={"op": "set", "path": "business.review_note", "value": "需要复核", "expected_revision": 1},
    )
    assert updated.json()["resource"]["business"]["review_note"] == "需要复核"
    stale = client.post(
        f"/bff/instances/{instance_id}/context/update{SCOPE_QUERY}",
        json={"op": "set", "path": "business.review_note", "value": "stale", "expected_revision": 1},
    )
    assert stale.json()["error"]["code"] == "WORKFLOW_CONTEXT_CONFLICT"

    wildcard = client.post(
        f"/bff/instances/{instance_id}/business-events{SCOPE_QUERY}",
        json={"event_type": "business.*", "payload": {}},
    )
    assert wildcard.json()["error"]["code"] == "BUSINESS_EVENT_INVALID"
    event_body = {
        "event_type": "business.workflow.note_submitted",
        "event_id": "evt_once",
        "payload": {"note": "业务事件写入"},
        "binding": {"target_path": "context.business.event_note", "payload_path": "event.payload.note"},
    }
    first = client.post(f"/bff/instances/{instance_id}/business-events{SCOPE_QUERY}", json=event_body).json()
    second = client.post(f"/bff/instances/{instance_id}/business-events{SCOPE_QUERY}", json=event_body).json()
    assert first["resource"]["context"]["business"]["event_note"] == "业务事件写入"
    assert second["idempotent"] is True


def test_business_event_binding_requires_context_write_capability(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("HARNESS_CAPABILITY_TOKEN_SECRET", SECRET)
    monkeypatch.delenv("HARNESS_V3_5_DEV_MODE", raising=False)
    service = _gateway(tmp_path)
    seeded = asyncio.run(_seed(service, "v4_d_business_binding_auth"))
    instance_id = seeded["instance"]["workflow_instance_id"]
    client = TestClient(create_app(gateway_service=service))

    def token(capabilities: tuple[str, ...]) -> str:
        return issue_capability_token(
            app_profile=service.app_registry.get("meeting"),
            project_id="demo",
            workspace_id="local",
            capabilities=capabilities,
            allowed_origins=(ORIGIN,),
            secret=SECRET,
        )

    event_body = {
        "event_type": "business.workflow.note_submitted",
        "event_id": "evt_binding_auth",
        "payload": {"note": "needs context write"},
        "binding": {"target_path": "context.business.event_note", "payload_path": "event.payload.note"},
    }
    missing_context = client.post(
        f"/bff/instances/{instance_id}/business-events",
        json=event_body,
        headers={"Authorization": f"Bearer {token(('business_events.write',))}", "Origin": ORIGIN},
    )
    assert missing_context.json()["error"]["code"] == "CAPABILITY_DENIED"
    ok = client.post(
        f"/bff/instances/{instance_id}/business-events",
        json=event_body,
        headers={"Authorization": f"Bearer {token(('business_events.write', 'workflow_context.write'))}", "Origin": ORIGIN},
    )
    assert ok.json()["resource"]["context"]["business"]["event_note"] == "needs context write"


def test_business_event_rejects_non_business_canonical_namespaces(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("HARNESS_V3_5_DEV_MODE", "1")
    service = _gateway(tmp_path)
    seeded = asyncio.run(_seed(service, "v4_d_business_namespace"))
    instance_id = seeded["instance"]["workflow_instance_id"]
    client = TestClient(create_app(gateway_service=service))

    for event_type in ("meeting.note_submitted", "knowledge.note_submitted", "video.scene.selected"):
        response = client.post(
            f"/bff/instances/{instance_id}/business-events{SCOPE_QUERY}",
            json={"event_type": event_type, "payload": {}},
        )
        assert response.json()["error"]["code"] == "BUSINESS_EVENT_INVALID"
