"""V3.6-I workflow patch / agent editing contract tests."""

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
from core.protocol.schemas.methods import METHOD_SCHEMAS
from core.protocol.schemas.workflow_events import WORKFLOW_EVENT_SCHEMAS


SECRET = "v3-6-i-secret"
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


def _template(template_id: str = "workflow_patch") -> dict:
    return {
        "workflow_template_id": template_id,
        "name": "Patch Workflow",
        "stations": [
            {
                "station_id": "station_a",
                "name": "A",
                "connector_refs": ["connector_a"],
                "output_contracts": [
                    {"contract_id": "out", "artifact_kind": "generic.report", "direction": "output"},
                ],
            },
            {"station_id": "station_b", "name": "B", "approval_required": True},
        ],
        "edges": [{"edge_id": "a_to_b", "from_station_id": "station_a", "to_station_id": "station_b"}],
        "quality_contracts": [
            {"contract_id": "quality_a", "rubric_id": "rubric_a", "threshold": 0.7, "required": True},
        ],
    }


async def _rpc(service: GatewayService, method: str, params: dict | None = None):
    return await service.handle_rpc(RpcRequest(id=method, method=method, params=params or {}))


async def _created(service: GatewayService, template_id: str = "workflow_patch") -> dict:
    created = await _rpc(service, "workflow.template.create", {"template": _template(template_id), "scope": _scope()})
    assert created.error is None
    return created.result


def _patch(operation: str, payload: dict, **overrides) -> dict:
    patch = {
        "operation": operation,
        "payload": payload,
        "actor_type": "user",
        "actor_id": "user_1",
        "proposed_by": "user_1",
    }
    patch.update(overrides)
    return patch


def _token(service: GatewayService, capabilities: tuple[str, ...]) -> str:
    return issue_capability_token(
        app_profile=service.app_registry.get("meeting"),
        project_id="demo",
        workspace_id="local",
        capabilities=capabilities,
        allowed_origins=(LOCAL_ORIGIN,),
        secret=SECRET,
    )


def _headers(service: GatewayService, capabilities: tuple[str, ...]) -> dict[str, str]:
    return {"Authorization": f"Bearer {_token(service, capabilities)}", "Origin": LOCAL_ORIGIN}


def _sse_events(body: str) -> list[dict]:
    events = []
    for frame in body.strip().split("\n\n"):
        data = "".join(line.removeprefix("data: ") for line in frame.splitlines() if line.startswith("data: "))
        if data:
            events.append(json.loads(data))
    return events


def test_propose_diff_apply_reject_state_machine_and_publish(tmp_path) -> None:
    async def run() -> None:
        service = _gateway(tmp_path)
        created = await _created(service)
        draft_id = created["draft"]["workflow_draft_id"]
        proposed = await _rpc(
            service,
            "workflow.patch.propose",
            {
                "workflow_template_id": "workflow_patch",
                "patch": _patch("add_station", {"station": {"station_id": "station_c", "name": "C"}}),
                "scope": _scope(),
            },
        )
        assert proposed.error is None
        patch_id = proposed.result["patch"]["workflow_patch_id"]
        assert proposed.result["patch"]["workflow_draft_id"] == draft_id
        assert proposed.result["patch"]["base_revision"] == 1
        assert proposed.result["patch"]["status"] == "proposed"

        diff = await _rpc(service, "workflow.patch.diff", {"workflow_patch_id": patch_id, "scope": _scope()})
        assert diff.error is None
        assert diff.result["diff"]["operation"] == "add_station"
        assert diff.result["diff"]["redacted"] is True
        assert "stations" not in diff.result["diff"]

        applied = await _rpc(service, "workflow.patch.apply", {"workflow_patch_id": patch_id, "actor_type": "user", "scope": _scope()})
        assert applied.error is None
        assert applied.result["patch"]["status"] == "applied"
        assert applied.result["patch"]["applied_revision"] == 1
        assert applied.result["patch"]["resulting_draft_revision"] == 2
        assert applied.result["draft"]["revision"] == 2
        assert any(station["station_id"] == "station_c" for station in applied.result["draft"]["draft"]["stations"])

        repeated = await _rpc(service, "workflow.patch.apply", {"workflow_patch_id": patch_id, "actor_type": "user", "scope": _scope()})
        assert repeated.error is None
        assert repeated.result["idempotent"] is True
        assert repeated.result["draft"]["revision"] == 2

        reject_applied = await _rpc(service, "workflow.patch.reject", {"workflow_patch_id": patch_id, "scope": _scope()})
        assert reject_applied.error.code == "WORKFLOW_PATCH_CONFLICT"

        published = await _rpc(
            service,
            "workflow.template.publish",
            {"workflow_template_id": "workflow_patch", "version": "1.0.0", "expected_revision": 2, "scope": _scope()},
        )
        assert published.error is None
        assert any(station["station_id"] == "station_c" for station in published.result["version"]["snapshot"]["stations"])

    asyncio.run(run())


def test_reject_prevents_apply_and_repeated_reject_is_idempotent(tmp_path) -> None:
    async def run() -> None:
        service = _gateway(tmp_path)
        await _created(service)
        proposed = await _rpc(
            service,
            "workflow.patch.propose",
            {
                "workflow_template_id": "workflow_patch",
                "patch": _patch("update_station_prompt", {"station_id": "station_a", "prompt_ref": "prompt.v2"}),
                "scope": _scope(),
            },
        )
        patch_id = proposed.result["patch"]["workflow_patch_id"]
        rejected = await _rpc(service, "workflow.patch.reject", {"workflow_patch_id": patch_id, "reason": "not needed", "scope": _scope()})
        assert rejected.error is None
        assert rejected.result["patch"]["status"] == "rejected"
        repeated = await _rpc(service, "workflow.patch.reject", {"workflow_patch_id": patch_id, "scope": _scope()})
        assert repeated.error is None
        assert repeated.result["idempotent"] is True
        apply_rejected = await _rpc(service, "workflow.patch.apply", {"workflow_patch_id": patch_id, "scope": _scope()})
        assert apply_rejected.error.code == "WORKFLOW_PATCH_CONFLICT"

    asyncio.run(run())


def test_stale_concurrent_apply_and_invalid_resulting_draft_rollback(tmp_path) -> None:
    async def run() -> None:
        service = _gateway(tmp_path)
        created = await _created(service)
        proposed = await _rpc(
            service,
            "workflow.patch.propose",
            {
                "workflow_template_id": "workflow_patch",
                "patch": _patch("update_station_prompt", {"station_id": "station_a", "prompt_ref": "prompt_b"}),
                "scope": _scope(),
            },
        )
        patch_id = proposed.result["patch"]["workflow_patch_id"]
        first, second = await asyncio.gather(
            _rpc(service, "workflow.patch.apply", {"workflow_patch_id": patch_id, "scope": _scope()}),
            _rpc(service, "workflow.patch.apply", {"workflow_patch_id": patch_id, "scope": _scope()}),
        )
        assert first.error is None
        assert second.error is None
        assert sorted([first.result["idempotent"], second.result["idempotent"]]) == [False, True]
        assert first.result["draft"]["revision"] == second.result["draft"]["revision"] == 2

        stale = await _rpc(
            service,
            "workflow.patch.propose",
            {
                "workflow_template_id": "workflow_patch",
                "patch": _patch("update_station_prompt", {"station_id": "station_a", "prompt_ref": "stale"}, base_revision=1),
                "scope": _scope(),
            },
        )
        assert stale.error.code == "WORKFLOW_PATCH_CONFLICT"

        invalid = await _rpc(
            service,
            "workflow.patch.propose",
            {
                "workflow_template_id": "workflow_patch",
                "patch": _patch("add_station", {"station": {"station_id": "station_a", "name": "Duplicate"}}),
                "scope": _scope(),
            },
        )
        invalid_patch_id = invalid.result["patch"]["workflow_patch_id"]
        failed = await _rpc(service, "workflow.patch.apply", {"workflow_patch_id": invalid_patch_id, "scope": _scope()})
        assert failed.error.code == "WORKFLOW_PATCH_INVALID"
        draft = await _rpc(service, "workflow.template.get", {"workflow_template_id": "workflow_patch", "scope": _scope()})
        assert draft.result["template"]["latest_draft_id"] == created["template"]["latest_draft_id"]
        stored = service.workflow_repository.get_patch(invalid_patch_id, scope=service._resolve_request_scope({"scope": _scope()}))
        assert stored.status == "proposed"

    asyncio.run(run())


def test_operation_payload_validation_and_archived_published_boundaries(tmp_path) -> None:
    async def run() -> None:
        service = _gateway(tmp_path)
        await _created(service)
        remove = await _rpc(
            service,
            "workflow.patch.propose",
            {
                "workflow_template_id": "workflow_patch",
                "patch": _patch("remove_station", {"station_id": "station_a"}),
                "scope": _scope(),
            },
        )
        failed_remove = await _rpc(service, "workflow.patch.apply", {"workflow_patch_id": remove.result["patch"]["workflow_patch_id"], "scope": _scope()})
        assert failed_remove.error.code == "WORKFLOW_ACTION_FORBIDDEN"

        missing_station_edge = await _rpc(
            service,
            "workflow.patch.propose",
            {
                "workflow_template_id": "workflow_patch",
                "patch": _patch("update_edge", {"edge_id": "a_to_b", "edge_patch": {"from_station_id": "missing"}}),
                "scope": _scope(),
            },
        )
        failed_edge = await _rpc(service, "workflow.patch.apply", {"workflow_patch_id": missing_station_edge.result["patch"]["workflow_patch_id"], "scope": _scope()})
        assert failed_edge.error.code == "WORKFLOW_ACTION_FORBIDDEN"

        unknown = await _rpc(
            service,
            "workflow.patch.propose",
            {
                "workflow_template_id": "workflow_patch",
                "patch": _patch("add_station", {"station": {"station_id": "x", "name": "X"}, "unknown": True}),
                "scope": _scope(),
            },
        )
        assert unknown.error.code == "WORKFLOW_PATCH_INVALID"

        secret = await _rpc(
            service,
            "workflow.patch.propose",
            {
                "workflow_template_id": "workflow_patch",
                "patch": _patch("add_station", {"station": {"station_id": "x", "name": "X", "metadata": {"raw_trace_payload": "secret-token"}}}),
                "scope": _scope(),
            },
        )
        assert secret.error.code == "WORKFLOW_PATCH_INVALID"

        published = await _rpc(service, "workflow.template.publish", {"workflow_template_id": "workflow_patch", "version": "1.0.0", "scope": _scope()})
        assert published.error is None
        patch_published = await _rpc(
            service,
            "workflow.patch.propose",
            {"workflow_template_id": "workflow_patch", "patch": _patch("add_station", {"station": {"station_id": "x", "name": "X"}}), "scope": _scope()},
        )
        assert patch_published.error.code == "WORKFLOW_PUBLISHED_IMMUTABLE"

        archived = _gateway(tmp_path / "archived")
        await _created(archived, "workflow_archived")
        await _rpc(archived, "workflow.template.archive", {"workflow_template_id": "workflow_archived", "scope": _scope()})
        archived_patch = await _rpc(
            archived,
            "workflow.patch.propose",
            {"workflow_template_id": "workflow_archived", "patch": _patch("add_station", {"station": {"station_id": "x", "name": "X"}}), "scope": _scope()},
        )
        assert archived_patch.error.code == "WORKFLOW_TEMPLATE_ARCHIVED"

    asyncio.run(run())


def test_agent_boundary_high_risk_no_approval_and_no_runtime_creep(tmp_path) -> None:
    async def run() -> None:
        service = _gateway(tmp_path)
        await _created(service)
        agent = await _rpc(
            service,
            "workflow.patch.propose",
            {
                "workflow_template_id": "workflow_patch",
                "patch": _patch(
                    "update_approval_point",
                    {"station_id": "station_b", "approval_required": False},
                    actor_type="agent",
                    actor_id="agent_1",
                    proposed_by="agent_1",
                ),
                "scope": _scope(),
            },
        )
        assert agent.error is None
        assert agent.result["patch"]["requires_approval"] is True
        assert "approval_removed" in agent.result["patch"]["risk_flags"]
        denied = await _rpc(service, "workflow.patch.apply", {"workflow_patch_id": agent.result["patch"]["workflow_patch_id"], "actor_type": "agent", "scope": _scope()})
        assert denied.error.code == "WORKFLOW_ACTION_FORBIDDEN"
        applied = await _rpc(service, "workflow.patch.apply", {"workflow_patch_id": agent.result["patch"]["workflow_patch_id"], "actor_type": "user", "scope": _scope()})
        assert applied.error.code == "WORKFLOW_ACTION_FORBIDDEN"
        assert service.approval_store.list_approvals(app_id="meeting", project_id="demo", workspace_id="local") == []
        assert await _rpc(service, "workflow.instance.list", {"scope": _scope()})
        assert service.core_service.list_jobs(app_id="meeting", project_id="demo", workspace_id="local") == []
        assert service.artifact_registry.list_artifacts(app_id="meeting", project_id="demo", workspace_id="local") == []
        assert service.workflow_repository.list_quality_evaluations(scope=service._resolve_request_scope({"scope": _scope()})) == []
        traces = "\n".join(str(record.get("event_type")) for record in service.trace_store.list_records())
        assert "business.event.received" not in traces
        assert "workflow.context.updated" not in traces

    asyncio.run(run())


def test_scope_capability_method_metadata_sdk_and_eventbridge(tmp_path, monkeypatch) -> None:
    async def setup() -> tuple[GatewayService, str]:
        service = _gateway(tmp_path)
        await _created(service)
        proposed = await _rpc(
            service,
            "workflow.patch.propose",
            {"workflow_template_id": "workflow_patch", "patch": _patch("update_station_prompt", {"station_id": "station_a", "prompt_ref": "v2"}), "scope": _scope()},
        )
        await _rpc(service, "workflow.patch.apply", {"workflow_patch_id": proposed.result["patch"]["workflow_patch_id"], "scope": _scope()})
        return service, proposed.result["patch"]["workflow_patch_id"]

    service, patch_id = asyncio.run(setup())
    schema_by_method = {entry["method"]: entry for entry in METHOD_SCHEMAS}
    for method in ("workflow.patch.propose", "workflow.patch.diff", "workflow.patch.apply", "workflow.patch.reject"):
        assert schema_by_method[method]["runtime_handler"] is True
        assert schema_by_method[method]["sdk_exposure"] == "workflow_runtime"
    assert not any(entry["sdk_exposure"] == "default" and entry["method"].startswith("workflow.patch.") for entry in METHOD_SCHEMAS)

    monkeypatch.setenv("HARNESS_CAPABILITY_TOKEN_SECRET", SECRET)
    monkeypatch.delenv("HARNESS_V3_5_DEV_MODE", raising=False)
    client = TestClient(create_app(gateway_service=service))
    no_cap = _headers(service, ("events",))
    read_cap = _headers(service, ("workflow_patches.read", "events"))
    write_cap = _headers(service, ("workflow_patches.write", "events"))
    diff_payload = {"id": "d", "method": "workflow.patch.diff", "params": {"workflow_patch_id": patch_id}}
    assert client.post("/v1/rpc", json=diff_payload, headers=no_cap).json()["error"]["code"] == "CAPABILITY_DENIED"
    assert client.post("/v1/rpc", json=diff_payload, headers=read_cap).json()["result"]["diff"]["workflow_patch_id"] == patch_id
    propose_payload = {
        "id": "p",
        "method": "workflow.patch.propose",
        "params": {"workflow_template_id": "workflow_patch", "patch": _patch("update_station_prompt", {"station_id": "station_a", "prompt_ref": "v3"})},
    }
    assert client.post("/v1/rpc", json=propose_payload, headers=read_cap).json()["error"]["code"] == "CAPABILITY_DENIED"
    assert client.post("/v1/rpc", json=propose_payload, headers=write_cap).json()["result"]["patch"]["status"] == "proposed"
    cross_scope = {"id": "x", "method": "workflow.patch.diff", "params": {"workflow_patch_id": patch_id, "scope": _scope(app_id="knowledge")}}
    assert client.post("/v1/rpc", json=cross_scope, headers=read_cap).json()["error"]["code"] == "SCOPE_MISMATCH"

    sse = client.get(
        "/v1/events/subscribe",
        params={"channels": "workflow_patch", "app_id": "meeting", "project_id": "demo", "workspace_id": "local", "workflow_patch_id": patch_id},
        headers=read_cap,
    )
    assert sse.status_code == 200
    events = _sse_events(sse.text)
    assert {event["type"] for event in events} >= {"workflow.patch.proposed", "workflow.patch.applied"}
    for event in events:
        schema = next(item for item in WORKFLOW_EVENT_SCHEMAS if item["type"] == event["type"])
        assert set(schema["envelope_schema"]["required"]) <= set(event)
        assert event["channel"] == "workflow_patch"
        assert event["data"]["workflow_patch_id"] == patch_id
        assert event["data"]["workflow_template_id"] == "workflow_patch"
        assert event["data"]["workflow_draft_id"]
        assert event["data"]["operation"]
        assert event["data"]["status"]
        assert "risk_flags" in event["data"]
    raw = json.dumps(events, ensure_ascii=False)
    for forbidden in ("Bearer ", "secret-token", "raw_trace_payload", "raw_connector_payload", "raw_artifact_content"):
        assert forbidden not in raw
