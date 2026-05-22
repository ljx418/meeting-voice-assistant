"""Shared V4.0-E reference workflow console E2E fixtures."""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from apps.gateway.approvals import ApprovalStore
from apps.gateway.artifacts import ArtifactRegistry
from apps.gateway.protocol import RpcRequest
from apps.gateway.runtime import GatewayRuntimePool
from apps.gateway.service import GatewayService
from apps.gateway.storage import GatewaySessionStore
from apps.gateway.traces import TraceStore
from core.apps.profiles import AppProfile


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "v3_6" / "dummy_pipeline"
LOCAL_ORIGIN = "http://localhost:5173"
SCOPE = {"app_id": "reference_app", "project_id": "demo_a", "workspace_id": "local"}
OTHER_SCOPE = {"app_id": "reference_app", "project_id": "demo_b", "workspace_id": "local"}
SCOPE_QUERY = "?app_id=reference_app&project_id=demo_a&workspace_id=local"
OTHER_SCOPE_QUERY = "?app_id=reference_app&project_id=demo_b&workspace_id=local"
FORBIDDEN_TEXT = (
    "capability_token",
    "subscription_token",
    "Authorization",
    "Bearer ",
    "secret-token-value",
    "raw_trace_payload",
    "raw_connector_payload",
    "raw_artifact_content",
    "upstream signed URL",
)
DEFAULT_CAPABILITIES = (
    "rpc",
    "events",
    "artifacts",
    "artifacts.read",
    "artifact_lineage",
    "jobs",
    "jobs.read",
    "approvals",
    "approvals.read",
    "workflows.read",
    "workflows.write",
    "workflows.execute",
    "workflow_versions.publish",
    "stations.read",
    "stations.execute",
    "quality.read",
    "quality.write",
    "board.read",
    "workflow_context.read",
    "workflow_context.write",
    "business_events.read",
    "business_events.write",
    "workflow_patches.read",
    "workflow_patches.write",
    "agent_talk.read",
    "agent_talk.write",
    "agent_suggestions.read",
    "agent_suggestions.write",
    "agent_actions.read",
    "agent_actions.write",
    "agent_handoffs.read",
    "agent_handoffs.write",
    "agent_audit.read",
    "operation_evidence.read",
    "governance_review.read",
)


def build_gateway(tmp_path) -> GatewayService:
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


async def rpc(service: GatewayService, method: str, params: dict[str, Any] | None = None):
    response = await service.handle_rpc(RpcRequest(id=method, method=method, params=params or {}))
    assert response.error is None, response.error
    return response.result


def load_template(template_id: str) -> dict[str, Any]:
    payload = json.loads((FIXTURE_DIR / "workflow_template.json").read_text(encoding="utf-8"))
    payload["workflow_template_id"] = template_id
    payload["name"] = "Reference Workflow Console E2E"
    return payload


async def seed_reference_console(
    service: GatewayService,
    *,
    template_id: str = "workflow_console_reference",
    scope: dict[str, str] | None = None,
) -> dict[str, Any]:
    scope = scope or SCOPE
    created = await rpc(service, "workflow.template.create", {"template": load_template(template_id), "scope": scope})
    published = await rpc(
        service,
        "workflow.template.publish",
        {"workflow_template_id": template_id, "version": "1.0.0", "scope": scope},
    )
    started = await rpc(
        service,
        "workflow.instance.start",
        {"workflow_version_id": published["version"]["workflow_version_id"], "scope": scope},
    )
    instance = started["workflow_instance"]
    runs = (await rpc(service, "station.run.list", {"workflow_instance_id": instance["workflow_instance_id"], "scope": scope}))["station_runs"]
    station_b = next(run for run in runs if run["station_id"] == "station_b")
    approval = service.approval_store.list_approvals(status="pending", app_id=scope["app_id"], project_id=scope["project_id"], workspace_id=scope["workspace_id"])[0]
    quality = await rpc(
        service,
        "quality.evaluation.create",
        {
            "evaluation": {
                "workflow_instance_id": instance["workflow_instance_id"],
                "station_run_id": station_b["station_run_id"],
                "artifact_id": station_b["output_artifact_ids"][0],
                "rubric_id": "dummy_quality",
                "evaluator_type": "rule",
                "score": 0.91,
                "issues": [{"raw_artifact_content": "secret-token-value", "summary": "ok"}],
                "suggestions": [{"raw_connector_payload": "secret-token-value", "summary": "keep"}],
            },
            "auto_attach": True,
            "scope": scope,
        },
    )
    context = await rpc(
        service,
        "workflow.context.update",
        {
            "workflow_instance_id": instance["workflow_instance_id"],
            "path": "context.business.reference.note",
            "value": "ready",
            "expected_revision": 1,
            "scope": scope,
        },
    )
    binding = await rpc(
        service,
        "business.event.bind",
        {
            "workflow_instance_id": instance["workflow_instance_id"],
            "event_type": "business.video.scene.selected",
            "target_path": "context.business.selected_scene",
            "payload_path": "event.payload.scene_id",
            "mode": "set",
            "scope": scope,
        },
    )
    event = await rpc(
        service,
        "business.event.emit",
        {
            "event": {
                "event_id": f"evt_{template_id}_scene",
                "type": "business.video.scene.selected",
                "workflow_instance_id": instance["workflow_instance_id"],
                "payload": {
                    "scene_id": "scene_001",
                    "secret": "secret-token-value",
                    "raw_trace_payload": "secret-token-value",
                },
            },
            "scope": scope,
        },
    )
    await rpc(
        service,
        "workflow.template.update_draft",
        {"workflow_template_id": template_id, "draft": deepcopy(published["version"]["snapshot"]), "scope": scope},
    )
    patch = await rpc(
        service,
        "workflow.patch.propose",
        {
            "workflow_template_id": template_id,
            "patch": {
                "operation": "update_station_prompt",
                "payload": {"station_id": "station_b", "prompt_ref": "reference.prompt.v2"},
                "actor_type": "agent",
                "actor_id": "agent_reference",
                "proposed_by": "agent_reference",
                "metadata": {
                    "workflow_instance_id": instance["workflow_instance_id"],
                    "secret": "secret-token-value",
                    "raw_trace_payload": "secret-token-value",
                },
            },
            "scope": scope,
        },
    )
    return {
        "template": created["template"],
        "version": published["version"],
        "instance": instance,
        "runs": runs,
        "station_b": station_b,
        "approval": approval,
        "quality": quality["evaluation"],
        "context": context["context"],
        "binding": binding["binding"],
        "event": event["event"],
        "patch": patch["patch"],
    }


def assert_no_forbidden_text(payload: Any) -> None:
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True)
    for forbidden in FORBIDDEN_TEXT:
        assert forbidden not in raw, f"{forbidden} leaked in payload"


def sse_events(body: str) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    for frame in body.strip().split("\n\n"):
        event_type = ""
        event_id = ""
        data = ""
        for line in frame.splitlines():
            if line.startswith("event: "):
                event_type = line.removeprefix("event: ")
            if line.startswith("id: "):
                event_id = line.removeprefix("id: ")
            if line.startswith("data: "):
                data += line.removeprefix("data: ")
        if data:
            item = json.loads(data)
            if event_type:
                item.setdefault("_sse_event", event_type)
            if event_id:
                item.setdefault("_sse_id", event_id)
            events.append(item)
    return events
