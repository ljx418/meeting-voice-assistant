"""V3.6-J platform-neutral dummy pipeline E2E gate tests."""

from __future__ import annotations

import asyncio
import json
from copy import deepcopy
from pathlib import Path

from fastapi.testclient import TestClient

from apps.api import create_app
from apps.gateway.approvals import APPROVAL_PENDING, ApprovalStore
from apps.gateway.artifacts import ArtifactRegistry
from apps.gateway.protocol import RpcRequest
from apps.gateway.runtime import GatewayRuntimePool
from apps.gateway.service import GatewayService
from apps.gateway.storage import GatewaySessionStore
from apps.gateway.traces import TraceStore
from core.apps.profiles import AppProfile
from core.protocol.auth import issue_capability_token
from core.protocol.schemas.workflow_events import WORKFLOW_EVENT_SCHEMAS


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "v3_6" / "dummy_pipeline"
SECRET = "v3-6-j-secret"
LOCAL_ORIGIN = "http://localhost:5173"
DEFAULT_CAPABILITIES = (
    "rpc",
    "events",
    "artifacts",
    "artifact_lineage",
    "jobs",
    "approvals",
    "workflows.read",
    "workflows.write",
    "workflows.execute",
    "workflow_versions.publish",
    "stations.read",
    "quality.read",
    "quality.write",
    "board.read",
    "workflow_context.read",
    "workflow_context.write",
    "business_events.read",
    "business_events.write",
    "workflow_patches.read",
    "workflow_patches.write",
)
FORBIDDEN_TEXT = (
    "capability_token",
    "subscription_token",
    "Authorization",
    "Bearer ",
    "secret-token-value",
    "raw_trace_payload",
    "raw_connector_payload",
    "raw_artifact_content",
)


def _scope(project_id: str = "demo_a") -> dict[str, str]:
    return {"app_id": "reference_app", "project_id": project_id, "workspace_id": "local"}


def _load_json(name: str):
    return json.loads((FIXTURE_DIR / name).read_text(encoding="utf-8"))


def _template(template_id: str = "workflow_dummy_pipeline") -> dict:
    payload = deepcopy(_load_json("workflow_template.json"))
    payload["workflow_template_id"] = template_id
    return payload


def _gateway(tmp_path) -> GatewayService:
    runtime = GatewayRuntimePool(
        store=GatewaySessionStore(tmp_path / "sessions"),
        artifact_registry=ArtifactRegistry(tmp_path / "artifacts"),
        trace_store=TraceStore(tmp_path / "traces"),
        approval_store=ApprovalStore(tmp_path / "approvals"),
    )
    service = GatewayService(runtime_pool=runtime)
    service.app_registry.register(
        AppProfile(
            app_id="reference_app",
            display_name="Reference App",
            domain="reference",
            default_pack="reference_app",
            allowed_origins=(LOCAL_ORIGIN,),
            default_capabilities=DEFAULT_CAPABILITIES,
        )
    )
    return service


async def _rpc(service: GatewayService, method: str, params: dict | None = None):
    return await service.handle_rpc(RpcRequest(id=method, method=method, params=params or {}))


async def _create_publish_start(
    service: GatewayService,
    *,
    template_id: str = "workflow_dummy_pipeline",
    project_id: str = "demo_a",
):
    template = _template(template_id)
    created = await _rpc(service, "workflow.template.create", {"template": template, "scope": _scope(project_id)})
    assert created.error is None
    published = await _rpc(
        service,
        "workflow.template.publish",
        {"workflow_template_id": template_id, "version": "1.0.0", "scope": _scope(project_id)},
    )
    assert published.error is None
    started = await _rpc(
        service,
        "workflow.instance.start",
        {"workflow_version_id": published.result["version"]["workflow_version_id"], "scope": _scope(project_id)},
    )
    assert started.error is None
    return template, published.result["version"], started.result["workflow_instance"]


def _pending_approval(service: GatewayService, *, project_id: str = "demo_a") -> dict:
    approvals = service.approval_store.list_approvals(
        status=APPROVAL_PENDING,
        app_id="reference_app",
        project_id=project_id,
        workspace_id="local",
    )
    assert len(approvals) == 1
    return approvals[0]


def _sse_events(body: str) -> list[dict]:
    events = []
    for frame in body.strip().split("\n\n"):
        data = "".join(line.removeprefix("data: ") for line in frame.splitlines() if line.startswith("data: "))
        if data:
            events.append(json.loads(data))
    return events


def _token(service: GatewayService, capabilities: tuple[str, ...], *, project_id: str = "demo_a") -> str:
    return issue_capability_token(
        app_profile=service.app_registry.get("reference_app"),
        project_id=project_id,
        workspace_id="local",
        capabilities=capabilities,
        allowed_origins=(LOCAL_ORIGIN,),
        secret=SECRET,
    )


def _headers(service: GatewayService, capabilities: tuple[str, ...], *, project_id: str = "demo_a") -> dict[str, str]:
    return {"Authorization": f"Bearer {_token(service, capabilities, project_id=project_id)}", "Origin": LOCAL_ORIGIN}


def _assert_no_sensitive_payload(payload) -> None:
    raw = json.dumps(payload, ensure_ascii=False)
    for forbidden in FORBIDDEN_TEXT:
        assert forbidden not in raw


def _assert_workflow_event(event: dict, event_type: str, channel: str) -> None:
    schema = next((item for item in WORKFLOW_EVENT_SCHEMAS if item["type"] == event_type), None)
    if schema is not None:
        assert set(schema["envelope_schema"]["required"]) <= set(event)
    else:
        assert {"event_id", "type", "channel", "cursor", "timestamp", "scope", "data"} <= set(event)
    assert event["type"] == event_type
    assert event["channel"] == channel
    assert isinstance(event["data"], dict)


def test_dummy_pipeline_runtime_e2e(tmp_path) -> None:
    async def run() -> None:
        service = _gateway(tmp_path)
        _, version_v1, instance = await _create_publish_start(service)
        assert instance["status"] == "waiting_approval"
        instance_id = instance["workflow_instance_id"]
        assert instance["workflow_version_id"] == version_v1["workflow_version_id"]

        waiting_approval = _pending_approval(service)
        approved = await _rpc(
            service,
            "approval.respond",
            {"approval_id": waiting_approval["approval_id"], "decision": "approve", "scope": _scope()},
        )
        assert approved.error is None
        assert approved.result["workflow_side_effect"]["status"] == "applied"

        runs = (await _rpc(service, "station.run.list", {"workflow_instance_id": instance_id, "scope": _scope()})).result["station_runs"]
        assert [run["station_id"] for run in runs] == ["station_a", "station_b", "station_c"]
        assert [run["status"] for run in runs] == ["completed", "completed", "completed"]
        assert runs[1]["input_artifact_ids"] == runs[0]["output_artifact_ids"]
        assert runs[2]["input_artifact_ids"] == runs[1]["output_artifact_ids"]

        lineage = await _rpc(service, "artifact.lineage", {"domain": "workflow_runtime", "scope": _scope()})
        assert lineage.error is None
        assert {
            "source_artifact_id": runs[0]["output_artifact_ids"][0],
            "target_artifact_id": runs[1]["output_artifact_ids"][0],
            "relation": "derived_from",
        } in lineage.result["edges"]
        assert {
            "source_artifact_id": runs[1]["output_artifact_ids"][0],
            "target_artifact_id": runs[2]["output_artifact_ids"][0],
            "relation": "derived_from",
        } in lineage.result["edges"]

        final_artifact_id = runs[2]["output_artifact_ids"][0]
        metadata = await _rpc(service, "artifact.read_metadata", {"artifact_id": final_artifact_id, "scope": _scope()})
        assert metadata.error is None
        assert metadata.result["artifact"]["metadata"]["workflow"]["workflow_instance_id"] == instance_id

        quality = await _rpc(
            service,
            "quality.evaluation.create",
            {
                "evaluation": {
                    "workflow_instance_id": instance_id,
                    "station_run_id": runs[2]["station_run_id"],
                    "artifact_id": final_artifact_id,
                    "rubric_id": "dummy_quality",
                    "evaluator_type": "rule",
                    "score": 0.92,
                    "issues": [{"raw_artifact_content": "secret-token-value"}],
                    "suggestions": [{"Authorization": "Bearer secret-token-value"}],
                    "metadata": {"raw_trace_payload": "secret-token-value"},
                },
                "auto_attach": True,
                "scope": _scope(),
            },
        )
        assert quality.error is None
        assert quality.result["evaluation"]["status"] == "passed"

        board = await _rpc(service, "workflow.board.get", {"workflow_instance_id": instance_id, "scope": _scope()})
        assert board.error is None
        expected_board = _load_json("expected_board.json")
        payload = board.result["board"]
        assert set(expected_board["required_top_level_keys"]) <= set(payload)
        assert {entry["station"]["station_id"] for entry in payload["stations"]} == set(expected_board["expected_station_ids"])
        assert payload["workflow_instance"]["status"] == "completed"
        assert len(payload["jobs"]) == 3
        assert len(payload["artifacts"]) == 3
        assert payload["approvals"][0]["status"] == "approved"
        assert payload["quality_evaluations"][0]["evaluation_id"] == quality.result["evaluation"]["evaluation_id"]
        _assert_no_sensitive_payload(payload)

    asyncio.run(run())


def test_dummy_pipeline_business_context_e2e(tmp_path, monkeypatch) -> None:
    async def setup() -> tuple[GatewayService, dict]:
        service = _gateway(tmp_path)
        _, _, instance = await _create_publish_start(service, template_id="workflow_dummy_pipeline_context")
        approved = await _rpc(service, "approval.respond", {"approval_id": _pending_approval(service)["approval_id"], "decision": "approve", "scope": _scope()})
        assert approved.error is None
        waiting = await _create_publish_start(service, template_id="workflow_dummy_pipeline_context_waiting")
        assert waiting[2]["status"] == "waiting_approval"
        binding = await _rpc(
            service,
            "business.event.bind",
            {
                "workflow_instance_id": instance["workflow_instance_id"],
                "event_type": "business.reference.item.selected",
                "target_path": "context.business.reference.selected_item_id",
                "payload_path": "event.payload.item_id",
                "mode": "set",
                "scope": _scope(),
            },
        )
        assert binding.error is None
        context = await _rpc(service, "workflow.context.get", {"workflow_instance_id": instance["workflow_instance_id"], "scope": _scope()})
        stale_revision = context.result["context"]["revision"]
        emitted = await _rpc(
            service,
            "business.event.emit",
            {
                "event": {
                    "event_id": "business_event_1",
                    "type": "business.reference.item.selected",
                    "workflow_instance_id": instance["workflow_instance_id"],
                    "payload": {"item_id": "item_001", "secret": "secret-token-value", "raw_trace_payload": "secret-token-value"},
                },
                "scope": _scope(),
            },
        )
        assert emitted.error is None
        conflict = await _rpc(
            service,
            "workflow.context.update",
            {
                "workflow_instance_id": instance["workflow_instance_id"],
                "expected_revision": stale_revision,
                "path": "context.business.reference.manual",
                "value": "manual",
                "scope": _scope(),
            },
        )
        assert conflict.error.code == "WORKFLOW_CONTEXT_CONFLICT"
        return service, instance

    service, instance = asyncio.run(setup())
    monkeypatch.setenv("HARNESS_CAPABILITY_TOKEN_SECRET", SECRET)
    monkeypatch.delenv("HARNESS_V3_5_DEV_MODE", raising=False)
    client = TestClient(create_app(gateway_service=service))
    headers = _headers(service, ("events", "approvals", "workflow_context.read", "business_events.read", "business_events.write", "workflow_patches.read"))
    response = client.get(
        "/v1/events/subscribe",
        params={
            "channels": "approval,business,workflow_context",
            "app_id": "reference_app",
            "project_id": "demo_a",
            "workspace_id": "local",
        },
        headers=headers,
    )
    assert response.status_code == 200
    events = _sse_events(response.text)
    by_type = {event["type"]: event for event in events}
    _assert_workflow_event(by_type["approval.required"], "approval.required", "approval")
    _assert_workflow_event(by_type["business.event.received"], "business.event.received", "business")
    _assert_workflow_event(by_type["workflow.context.updated"], "workflow.context.updated", "workflow_context")
    assert by_type["workflow.context.updated"]["workflow_instance_id"] == instance["workflow_instance_id"]
    _assert_no_sensitive_payload(events)


def test_dummy_pipeline_patch_e2e(tmp_path, monkeypatch) -> None:
    async def setup() -> tuple[GatewayService, dict, dict]:
        service = _gateway(tmp_path)
        _, version_v1, instance = await _create_publish_start(service, template_id="workflow_dummy_pipeline_patch")
        await _rpc(service, "approval.respond", {"approval_id": _pending_approval(service)["approval_id"], "decision": "approve", "scope": _scope()})
        version_before = await _rpc(service, "workflow.version.get", {"workflow_version_id": version_v1["workflow_version_id"], "scope": _scope()})
        assert version_before.error is None
        fork = await _rpc(
            service,
            "workflow.template.update_draft",
            {"workflow_template_id": "workflow_dummy_pipeline_patch", "draft": version_v1["snapshot"], "scope": _scope()},
        )
        assert fork.error is None
        proposed = await _rpc(
            service,
            "workflow.patch.propose",
            {
                "workflow_template_id": "workflow_dummy_pipeline_patch",
                "workflow_draft_id": fork.result["draft"]["workflow_draft_id"],
                "patch": {
                    "operation": "update_station_prompt",
                    "payload": {"station_id": "station_a", "prompt_ref": "dummy.prompt.v2"},
                    "actor_type": "agent",
                    "actor_id": "agent_1",
                    "proposed_by": "agent_1",
                },
                "scope": _scope(),
            },
        )
        assert proposed.error is None
        patch_id = proposed.result["patch"]["workflow_patch_id"]
        diff = await _rpc(service, "workflow.patch.diff", {"workflow_patch_id": patch_id, "scope": _scope()})
        assert diff.error is None
        assert diff.result["diff"]["redacted"] is True
        applied = await _rpc(service, "workflow.patch.apply", {"workflow_patch_id": patch_id, "actor_type": "user", "scope": _scope()})
        assert applied.error is None
        published_v2 = await _rpc(
            service,
            "workflow.template.publish",
            {
                "workflow_template_id": "workflow_dummy_pipeline_patch",
                "version": "2.0.0",
                "expected_revision": applied.result["draft"]["revision"],
                "scope": _scope(),
            },
        )
        assert published_v2.error is None
        v1_after = await _rpc(service, "workflow.version.get", {"workflow_version_id": version_v1["workflow_version_id"], "scope": _scope()})
        assert v1_after.result["version"]["snapshot"] == version_before.result["version"]["snapshot"]
        completed_v1 = await _rpc(service, "workflow.instance.get", {"workflow_instance_id": instance["workflow_instance_id"], "scope": _scope()})
        assert completed_v1.result["workflow_instance"]["status"] == "completed"
        started_v2 = await _rpc(
            service,
            "workflow.instance.start",
            {"workflow_version_id": published_v2.result["version"]["workflow_version_id"], "max_steps": 1, "scope": _scope()},
        )
        assert started_v2.error is None
        assert started_v2.result["workflow_instance"]["workflow_version_id"] == published_v2.result["version"]["workflow_version_id"]
        assert started_v2.result["station_runs"][0]["station_id"] == "station_a"
        return service, instance, proposed.result["patch"]

    service, _, patch = asyncio.run(setup())
    monkeypatch.setenv("HARNESS_CAPABILITY_TOKEN_SECRET", SECRET)
    monkeypatch.delenv("HARNESS_V3_5_DEV_MODE", raising=False)
    client = TestClient(create_app(gateway_service=service))
    headers = _headers(service, ("events", "workflow_patches.read"))
    response = client.get(
        "/v1/events/subscribe",
        params={
            "channels": "workflow_patch",
            "app_id": "reference_app",
            "project_id": "demo_a",
            "workspace_id": "local",
            "workflow_patch_id": patch["workflow_patch_id"],
        },
        headers=headers,
    )
    assert response.status_code == 200
    events = _sse_events(response.text)
    by_type = {event["type"]: event for event in events}
    _assert_workflow_event(by_type["workflow.patch.proposed"], "workflow.patch.proposed", "workflow_patch")
    _assert_workflow_event(by_type["workflow.patch.applied"], "workflow.patch.applied", "workflow_patch")
    assert by_type["workflow.patch.applied"]["data"]["workflow_patch_id"] == patch["workflow_patch_id"]
    assert by_type["workflow.patch.applied"]["data"]["resulting_draft_revision"] >= 2
    _assert_no_sensitive_payload(events)


def test_dummy_pipeline_scope_isolation(tmp_path) -> None:
    async def run() -> None:
        service = _gateway(tmp_path)
        _, _, instance_a = await _create_publish_start(service, template_id="workflow_dummy_pipeline_scope", project_id="demo_a")
        artifact_a = (
            await _rpc(service, "station.run.list", {"workflow_instance_id": instance_a["workflow_instance_id"], "scope": _scope("demo_a")})
        ).result["station_runs"][0]["output_artifact_ids"][0]

        template_b = {
            "workflow_template_id": "workflow_dummy_pipeline_scope_b",
            "name": "Cross Scope Input",
            "stations": [
                {
                    "station_id": "station_input",
                    "name": "Input",
                    "input_contracts": [{"contract_id": "seed_in", "artifact_kind": "dummy.alpha", "direction": "input"}],
                    "output_contracts": [{"contract_id": "out", "artifact_kind": "dummy.final", "direction": "output"}],
                }
            ],
        }
        created_b = await _rpc(service, "workflow.template.create", {"template": template_b, "scope": _scope("demo_b")})
        assert created_b.error is None
        published_b = await _rpc(
            service,
            "workflow.template.publish",
            {"workflow_template_id": template_b["workflow_template_id"], "version": "1.0.0", "scope": _scope("demo_b")},
        )
        cross_input = await _rpc(
            service,
            "workflow.instance.start",
            {"workflow_version_id": published_b.result["version"]["workflow_version_id"], "input_artifact_ids": [artifact_a], "scope": _scope("demo_b")},
        )
        assert cross_input.error.code == "SCOPE_MISMATCH"

        context_cross = await _rpc(
            service,
            "workflow.context.update",
            {"workflow_instance_id": instance_a["workflow_instance_id"], "path": "context.business.x", "value": "bad", "scope": _scope("demo_b")},
        )
        assert context_cross.error.code == "SCOPE_MISMATCH"
        event_cross = await _rpc(
            service,
            "business.event.emit",
            {
                "event": {"type": "business.reference.item.selected", "workflow_instance_id": instance_a["workflow_instance_id"], "payload": {"item_id": "bad"}},
                "scope": _scope("demo_b"),
            },
        )
        assert event_cross.error.code == "SCOPE_MISMATCH"

        fork = await _rpc(
            service,
            "workflow.template.update_draft",
            {"workflow_template_id": "workflow_dummy_pipeline_scope", "draft": _template("workflow_dummy_pipeline_scope"), "scope": _scope("demo_a")},
        )
        proposed = await _rpc(
            service,
            "workflow.patch.propose",
            {
                "workflow_template_id": "workflow_dummy_pipeline_scope",
                "workflow_draft_id": fork.result["draft"]["workflow_draft_id"],
                "patch": {
                    "operation": "update_station_prompt",
                    "payload": {"station_id": "station_a", "prompt_ref": "scope.v2"},
                    "actor_type": "user",
                },
                "scope": _scope("demo_a"),
            },
        )
        cross_patch = await _rpc(service, "workflow.patch.apply", {"workflow_patch_id": proposed.result["patch"]["workflow_patch_id"], "scope": _scope("demo_b")})
        assert cross_patch.error.code == "SCOPE_MISMATCH"

        list_a = await _rpc(service, "workflow.instance.list", {"scope": _scope("demo_a")})
        list_b = await _rpc(service, "workflow.instance.list", {"scope": _scope("demo_b")})
        assert len(list_a.result["workflow_instances"]) == 1
        assert all(item["workflow_instance_id"] != instance_a["workflow_instance_id"] for item in list_b.result["workflow_instances"])

    asyncio.run(run())


def test_dummy_pipeline_external_auth_smoke(tmp_path, monkeypatch) -> None:
    async def setup() -> tuple[GatewayService, dict]:
        service = _gateway(tmp_path)
        _, _, instance = await _create_publish_start(service, template_id="workflow_dummy_pipeline_auth")
        return service, instance

    service, instance = asyncio.run(setup())
    monkeypatch.setenv("HARNESS_CAPABILITY_TOKEN_SECRET", SECRET)
    monkeypatch.delenv("HARNESS_V3_5_DEV_MODE", raising=False)
    client = TestClient(create_app(gateway_service=service))
    read_headers = _headers(service, ("workflows.read",))
    board_headers = _headers(service, ("board.read",))
    context_write_headers = _headers(service, ("workflow_context.write",))

    ok_read = client.post(
        "/v1/rpc",
        json={"id": "g", "method": "workflow.instance.get", "params": {"workflow_instance_id": instance["workflow_instance_id"]}},
        headers=read_headers,
    )
    assert ok_read.json()["result"]["workflow_instance"]["workflow_instance_id"] == instance["workflow_instance_id"]

    denied_read = client.post(
        "/v1/rpc",
        json={"id": "b", "method": "workflow.board.get", "params": {"workflow_instance_id": instance["workflow_instance_id"]}},
        headers=read_headers,
    )
    assert denied_read.json()["error"]["code"] == "CAPABILITY_DENIED"
    ok_board = client.post(
        "/v1/rpc",
        json={"id": "b", "method": "workflow.board.get", "params": {"workflow_instance_id": instance["workflow_instance_id"]}},
        headers=board_headers,
    )
    assert ok_board.json()["result"]["board"]["workflow_instance"]["workflow_instance_id"] == instance["workflow_instance_id"]

    denied_write = client.post(
        "/v1/rpc",
        json={
            "id": "u",
            "method": "workflow.context.update",
            "params": {"workflow_instance_id": instance["workflow_instance_id"], "path": "context.business.auth", "value": "denied"},
        },
        headers=read_headers,
    )
    assert denied_write.json()["error"]["code"] == "CAPABILITY_DENIED"
    ok_write = client.post(
        "/v1/rpc",
        json={
            "id": "u",
            "method": "workflow.context.update",
            "params": {"workflow_instance_id": instance["workflow_instance_id"], "path": "context.business.auth", "value": "ok"},
        },
        headers=context_write_headers,
    )
    assert ok_write.json()["result"]["context"]["business"]["auth"] == "ok"


def test_dummy_pipeline_redaction_and_no_dependency(tmp_path) -> None:
    service = _gateway(tmp_path)
    fixture_text = "\n".join(path.read_text(encoding="utf-8") for path in FIXTURE_DIR.glob("*.json"))
    for forbidden_dependency in ("meeting", "knowledge", "data_service", "voice_service", "funasr", "external MCP", "Workflow Studio", "AgentTalkWindow"):
        assert forbidden_dependency not in fixture_text

    async def run() -> dict:
        _, _, instance = await _create_publish_start(service, template_id="workflow_dummy_pipeline_redaction")
        await _rpc(service, "approval.respond", {"approval_id": _pending_approval(service)["approval_id"], "decision": "approve", "scope": _scope()})
        runs = (await _rpc(service, "station.run.list", {"workflow_instance_id": instance["workflow_instance_id"], "scope": _scope()})).result["station_runs"]
        final_artifact_id = runs[-1]["output_artifact_ids"][0]
        await _rpc(
            service,
            "quality.evaluation.create",
            {
                "evaluation": {
                    "workflow_instance_id": instance["workflow_instance_id"],
                    "station_run_id": runs[-1]["station_run_id"],
                    "artifact_id": final_artifact_id,
                    "rubric_id": "dummy_quality",
                    "evaluator_type": "manual",
                    "score": 0.9,
                    "status": "passed",
                    "metadata": {"secret": "secret-token-value", "raw_connector_payload": "secret-token-value"},
                },
                "auto_attach": True,
                "scope": _scope(),
            },
        )
        board = await _rpc(service, "workflow.board.get", {"workflow_instance_id": instance["workflow_instance_id"], "scope": _scope()})
        return {
            "board": board.result["board"],
            "traces": service.trace_store.list_records(app_id="reference_app", project_id="demo_a", workspace_id="local"),
            "expected_board": _load_json("expected_board.json"),
        }

    payload = asyncio.run(run())
    _assert_no_sensitive_payload(payload)
    assert "quality.evaluated" not in json.dumps(payload["traces"], ensure_ascii=False)
