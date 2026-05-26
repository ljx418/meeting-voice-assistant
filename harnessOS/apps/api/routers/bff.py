"""Workflow Console BFF structured routes for V4.0-A2."""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import uuid4

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse, StreamingResponse

from apps.api.auth import add_dev_warning, authorize_http_request, http_error_response
from apps.api.agent_handoff_store import HANDOFF_ACTIVE_STATES, InMemoryAgentHandoffStore
from apps.api.agent_operation_evidence_store import InMemoryAgentOperationEvidenceStore
from apps.api.dependencies import get_gateway_service
from apps.gateway.protocol import RpcRequest
from apps.gateway.service import GatewayService
from core.apps.scope import ScopeContext
from core.protocol.event_bridge import (
    collect_event_envelopes,
    ensure_channel_capabilities,
    heartbeat_frame,
    normalize_event_channels,
    read_event_cursor,
    sse_frame,
)
from core.protocol.schemas.errors import ProtocolError

router = APIRouter()

SENSITIVE_KEY_PARTS = (
    "token",
    "authorization",
    "secret",
    "raw_trace_payload",
    "raw_artifact_content",
    "raw_connector_payload",
)
SENSITIVE_KEY_COMPACT_PARTS = tuple(part.replace("_", "") for part in SENSITIVE_KEY_PARTS)
UI_LAYOUT_KEYS = {
    "x",
    "y",
    "position",
    "canvas",
    "layout",
    "zoom",
    "selection",
    "selectednode",
    "panelcollapsed",
    "activetab",
    "viewport",
}
CANVAS_PATCH_SOURCES = {"canvas", "inspector", "workflow_console", "agent"}
CANVAS_PATCH_INTENTS = {"node_add", "edge_add", "inspector_update"}
CANVAS_PATCH_OPERATIONS = {
    "node_add": {"add_station"},
    "edge_add": {"update_edge"},
    "inspector_update": {
        "update_station_prompt",
        "update_connector",
        "update_artifact_contract",
        "update_quality_rule",
        "update_approval_point",
    },
}
INSPECTOR_OPERATION_FIELDS = {
    "update_station_prompt": {"station_id", "prompt_ref", "prompt_patch"},
    "update_connector": {"station_id", "connector_refs", "connector_patch"},
    "update_artifact_contract": {"station_id", "contract_id", "contract_patch"},
    "update_quality_rule": {"quality_contract_id", "quality_patch"},
    "update_approval_point": {"station_id", "approval_required", "approval_policy"},
}
ALLOWED_NODE_CATALOG_IDS = {
    "user_input",
    "file_input",
    "form_input",
    "webhook_input",
    "data_source_input",
    "generic_agent",
    "planner_agent",
    "script_writer_agent",
    "director_agent",
    "reviewer_agent",
    "multi_agent",
    "story_outline",
    "script_generation",
    "storyboard_generation",
    "character_consistency",
    "image_prompt_generation",
    "video_render",
    "subtitle_generation",
    "cover_generation",
    "video_quality",
    "publish_output",
    "http_request",
    "file_processing",
    "database_query",
    "mcp_tool",
    "knowledge_search",
    "image_generation",
    "asset_storage",
    "quality_evaluation",
    "consistency_check",
    "safety_check",
    "cost_check",
    "manual_approval",
    "conditional_approval",
    "publish_approval",
    "condition",
    "branch",
    "merge",
    "loop",
    "retry",
    "wait",
    "end",
}
ALLOWED_CONNECTOR_REFS = {
    "http",
    "file",
    "database",
    "mcp",
    "knowledge",
    "image_generation",
    "video_render",
    "subtitle",
    "asset_storage",
}
ALLOWED_SKILL_REFS = {
    "generic.reasoning",
    "planning.plan",
    "video.outline",
    "video.script",
    "video.storyboard",
    "video.character_consistency",
    "video.image_prompt",
    "video.quality",
    "governance.review",
}
NODE_CATALOG_CONTRACTS: dict[str, dict[str, Any]] = {
    "user_input": {
        "catalog_id": "core.input.user",
        "catalog_version": "2026-05-21",
        "node_template_id": "user_input",
        "station_kind": "input",
        "schema_version": "v4.0-n",
        "allowed_skill_refs": ["generic.reasoning"],
        "allowed_connector_refs": [],
        "allowed_artifact_kinds": ["dummy.alpha", "text/plain"],
        "allowed_quality_rules": [],
        "allowed_approval_policies": [],
    },
    "file_input": {
        "catalog_id": "core.input.file",
        "catalog_version": "2026-05-21",
        "node_template_id": "file_input",
        "station_kind": "input",
        "schema_version": "v4.0-n",
        "allowed_skill_refs": ["generic.reasoning"],
        "allowed_connector_refs": ["file"],
        "allowed_artifact_kinds": ["file", "text/plain"],
        "allowed_quality_rules": [],
        "allowed_approval_policies": [],
    },
    "planner_agent": {
        "catalog_id": "core.agent.planner",
        "catalog_version": "2026-05-21",
        "node_template_id": "planner_agent",
        "station_kind": "planner",
        "schema_version": "v4.0-n",
        "allowed_skill_refs": ["planning.plan"],
        "allowed_connector_refs": [],
        "allowed_artifact_kinds": ["dummy.alpha", "dummy.beta"],
        "allowed_quality_rules": [],
        "allowed_approval_policies": [],
    },
    "script_writer_agent": {
        "catalog_id": "video.agent.script_writer",
        "catalog_version": "2026-05-21",
        "node_template_id": "script_writer_agent",
        "station_kind": "screenwriter",
        "schema_version": "v4.0-n",
        "allowed_skill_refs": ["video.script"],
        "allowed_connector_refs": [],
        "allowed_artifact_kinds": ["script", "dummy.beta"],
        "allowed_quality_rules": ["visual_consistency"],
        "allowed_approval_policies": [],
    },
    "director_agent": {
        "catalog_id": "video.agent.director",
        "catalog_version": "2026-05-21",
        "node_template_id": "director_agent",
        "station_kind": "director",
        "schema_version": "v4.0-n",
        "allowed_skill_refs": ["video.storyboard"],
        "allowed_connector_refs": [],
        "allowed_artifact_kinds": ["storyboard", "dummy.beta"],
        "allowed_quality_rules": ["visual_consistency"],
        "allowed_approval_policies": [],
    },
    "storyboard_generation": {
        "catalog_id": "video.station.storyboard",
        "catalog_version": "2026-05-21",
        "node_template_id": "storyboard_generation",
        "station_kind": "storyboard_agent",
        "schema_version": "v4.0-n",
        "allowed_skill_refs": ["video.storyboard"],
        "allowed_connector_refs": [],
        "allowed_artifact_kinds": ["storyboard", "dummy.beta"],
        "allowed_quality_rules": ["visual_consistency"],
        "allowed_approval_policies": [],
    },
    "character_consistency": {
        "catalog_id": "video.station.character_consistency",
        "catalog_version": "2026-05-21",
        "node_template_id": "character_consistency",
        "station_kind": "reviewer",
        "schema_version": "v4.0-n",
        "allowed_skill_refs": ["video.character_consistency"],
        "allowed_connector_refs": [],
        "allowed_artifact_kinds": ["dummy.beta", "dummy.final", "storyboard"],
        "allowed_quality_rules": ["visual_consistency"],
        "allowed_approval_policies": [],
    },
    "video_render": {
        "catalog_id": "video.station.render",
        "catalog_version": "2026-05-21",
        "node_template_id": "video_render",
        "station_kind": "renderer",
        "schema_version": "v4.0-n",
        "allowed_skill_refs": ["video.image_prompt"],
        "allowed_connector_refs": ["video_render"],
        "allowed_artifact_kinds": ["video", "dummy.final"],
        "allowed_quality_rules": ["visual_consistency"],
        "allowed_approval_policies": [],
    },
    "quality_evaluation": {
        "catalog_id": "governance.station.quality",
        "catalog_version": "2026-05-21",
        "node_template_id": "quality_evaluation",
        "station_kind": "quality",
        "schema_version": "v4.0-n",
        "allowed_skill_refs": ["video.quality"],
        "allowed_connector_refs": [],
        "allowed_artifact_kinds": ["dummy.final", "video"],
        "allowed_quality_rules": ["visual_consistency", "dummy_quality"],
        "allowed_approval_policies": [],
    },
    "manual_approval": {
        "catalog_id": "governance.station.manual_approval",
        "catalog_version": "2026-05-21",
        "node_template_id": "manual_approval",
        "station_kind": "approval",
        "schema_version": "v4.0-n",
        "allowed_skill_refs": ["governance.review"],
        "allowed_connector_refs": [],
        "allowed_artifact_kinds": ["dummy.final", "video"],
        "allowed_quality_rules": [],
        "allowed_approval_policies": ["manual"],
    },
    "publish_output": {
        "catalog_id": "core.station.publish_output",
        "catalog_version": "2026-05-21",
        "node_template_id": "publish_output",
        "station_kind": "publisher",
        "schema_version": "v4.0-n",
        "allowed_skill_refs": ["generic.reasoning"],
        "allowed_connector_refs": [],
        "allowed_artifact_kinds": ["dummy.final", "video"],
        "allowed_quality_rules": [],
        "allowed_approval_policies": ["publish"],
    },
    "http_request": {
        "catalog_id": "connector.station.http",
        "catalog_version": "2026-05-21",
        "node_template_id": "http_request",
        "station_kind": "connector",
        "schema_version": "v4.0-n",
        "allowed_skill_refs": ["generic.reasoning"],
        "allowed_connector_refs": ["http"],
        "allowed_artifact_kinds": ["json", "dummy.beta"],
        "allowed_quality_rules": [],
        "allowed_approval_policies": [],
    },
    "mcp_tool": {
        "catalog_id": "connector.station.mcp",
        "catalog_version": "2026-05-21",
        "node_template_id": "mcp_tool",
        "station_kind": "connector",
        "schema_version": "v4.0-n",
        "allowed_skill_refs": ["generic.reasoning"],
        "allowed_connector_refs": ["mcp"],
        "allowed_artifact_kinds": ["json", "dummy.beta"],
        "allowed_quality_rules": [],
        "allowed_approval_policies": [],
    },
    "condition": {
        "catalog_id": "control.station.condition",
        "catalog_version": "2026-05-21",
        "node_template_id": "condition",
        "station_kind": "control",
        "schema_version": "v4.0-n",
        "allowed_skill_refs": ["planning.plan"],
        "allowed_connector_refs": [],
        "allowed_artifact_kinds": ["dummy.alpha", "dummy.beta", "dummy.final"],
        "allowed_quality_rules": [],
        "allowed_approval_policies": [],
    },
    "end": {
        "catalog_id": "control.station.end",
        "catalog_version": "2026-05-21",
        "node_template_id": "end",
        "station_kind": "control",
        "schema_version": "v4.0-n",
        "allowed_skill_refs": ["generic.reasoning"],
        "allowed_connector_refs": [],
        "allowed_artifact_kinds": ["dummy.final", "video"],
        "allowed_quality_rules": [],
        "allowed_approval_policies": [],
    },
}
NODE_CATALOG_LABELS = {
    "user_input": "用户输入",
    "file_input": "文件输入",
    "planner_agent": "Planner Agent",
    "script_writer_agent": "Script Writer Agent",
    "director_agent": "Director Agent",
    "storyboard_generation": "分镜生成",
    "character_consistency": "角色一致性检查",
    "video_render": "视频渲染",
    "quality_evaluation": "质量评估",
    "manual_approval": "人工审批",
    "publish_output": "发布输出",
    "http_request": "HTTP 请求",
    "mcp_tool": "MCP 工具",
    "condition": "条件判断",
    "end": "结束节点",
}
PATCH_QUEUE_STATUSES = {"proposed", "selected", "applied", "rejected", "stale", "blocked", "conflicted"}
AGENT_ACTION_INTENTS = {
    "explain_workflow",
    "summarize_events",
    "summarize_quality",
    "summarize_context",
    "suggest_patch",
    "show_patch_diff",
    "show_approval_notice",
    "show_context_summary",
    "navigate_to_editing_panel",
    "open_editing_panel",
    "open_approval_panel",
    "open_context_panel",
    "open_quality_panel",
    "open_artifact_panel",
    "propose_patch",
    "propose_context_update",
    "propose_approval_decision",
    "propose_station_rerun",
}
FORBIDDEN_AGENT_ACTION_INTENTS = {
    "apply_patch",
    "reject_patch",
    "publish_version",
    "respond_approval",
    "update_context",
    "emit_business_event",
    "start_workflow",
    "rerun_station",
    "call_connector",
    "call_external_llm",
}
AGENT_ACTION_POLICY: dict[str, str] = {
    "explain_workflow": "display_only",
    "summarize_events": "display_only",
    "summarize_quality": "display_only",
    "summarize_context": "display_only",
    "show_approval_notice": "display_only",
    "show_patch_diff": "display_only",
    "show_context_summary": "display_only",
    "navigate_to_editing_panel": "navigation",
    "open_editing_panel": "navigation",
    "open_approval_panel": "navigation",
    "open_context_panel": "navigation",
    "open_quality_panel": "navigation",
    "open_artifact_panel": "navigation",
    "suggest_patch": "proposal_only",
    "propose_patch": "proposal_only",
    "propose_context_update": "proposal_only",
    "propose_approval_decision": "proposal_only",
    "propose_station_rerun": "proposal_only",
}
READ_ONLY_AGENT_ACTION_INTENTS = {
    "explain_workflow",
    "summarize_events",
    "summarize_quality",
    "summarize_context",
}
_AGENT_TALK_SESSIONS: dict[str, dict[str, Any]] = {}
_AGENT_TALK_MESSAGES: dict[str, list[dict[str, Any]]] = {}
_AGENT_TALK_SUGGESTIONS: dict[str, list[dict[str, Any]]] = {}
_AGENT_ACTION_PROPOSALS: dict[str, list[dict[str, Any]]] = {}
_AGENT_HANDOFF_REPOSITORY = InMemoryAgentHandoffStore()
_AGENT_OPERATION_EVIDENCE_REPOSITORY = InMemoryAgentOperationEvidenceStore()
_AGENT_TALK_AUDIT: list[dict[str, Any]] = []
AGENT_HANDOFF_TTL_MINUTES = 30
AGENT_HANDOFF_TARGET_PANELS = {"editing_panel", "approval_panel", "context_panel", "quality_panel", "artifact_panel"}


@router.get("/workflows")
async def list_workflows(request: Request, gateway: GatewayService = Depends(get_gateway_service)) -> Any:
    try:
        params: dict[str, Any] = _query_scope_params(request)
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="workflows.read")
        result = await _rpc(gateway, "workflow.template.list", params)
        response = JSONResponse(_redact([_workflow_summary(item) for item in result.get("templates", [])]))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.get("/workflows/{workflow_template_id}")
async def get_workflow(workflow_template_id: str, request: Request, gateway: GatewayService = Depends(get_gateway_service)) -> Any:
    try:
        params = {**_query_scope_params(request), "workflow_template_id": workflow_template_id}
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="workflows.read")
        result = await _rpc(gateway, "workflow.template.get", params)
        response = JSONResponse(_redact(_workflow_summary(result["template"])))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.get("/workflows/{workflow_template_id}/versions")
async def list_workflow_versions(workflow_template_id: str, request: Request, gateway: GatewayService = Depends(get_gateway_service)) -> Any:
    try:
        params = {**_query_scope_params(request), "workflow_template_id": workflow_template_id}
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="workflows.read")
        result = await _rpc(gateway, "workflow.version.list", params)
        response = JSONResponse(_redact([_version_summary(item) for item in result.get("versions", [])]))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.get("/workflows/{workflow_template_id}/node-catalog")
async def get_workflow_node_catalog(
    workflow_template_id: str,
    request: Request,
    gateway: GatewayService = Depends(get_gateway_service),
) -> Any:
    try:
        params = {**_query_scope_params(request), "workflow_template_id": workflow_template_id}
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="workflows.read")
        gateway.workflow_repository.get_template(workflow_template_id, scope=auth.scope)
        catalog = [_node_catalog_item_dto(node_template_id, contract) for node_template_id, contract in sorted(NODE_CATALOG_CONTRACTS.items())]
        response = JSONResponse(_redact(catalog))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.post("/workflows/{workflow_template_id}/publish")
async def publish_workflow_version(
    workflow_template_id: str,
    request: Request,
    gateway: GatewayService = Depends(get_gateway_service),
) -> Any:
    body: dict[str, Any] = {}
    auth: Any = None
    try:
        body = await request.json()
        if not isinstance(body, dict):
            raise ProtocolError("INVALID_PARAMS", "Request body must be an object.", {"field": "body"})
        _require_user_confirmed(body, allowed_sources={"editing_panel", "workflow_console"})
        version = str(body.get("version") or "").strip()
        if not version:
            raise ProtocolError("INVALID_PARAMS", "version is required.", {"field": "version"})
        expected_revision = body.get("expected_draft_revision", body.get("expected_revision"))
        if expected_revision is None:
            raise ProtocolError("INVALID_PARAMS", "expected_draft_revision is required.", {"field": "expected_draft_revision"})
        params = {
            **_query_scope_params(request),
            "workflow_template_id": workflow_template_id,
            "version": version,
            "expected_revision": expected_revision,
        }
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="workflow_versions.publish")
        _require_agent_handoff_for_action(body, target_panel="editing_panel", gateway=gateway, scope=auth.scope, auth=auth)
        template = gateway.workflow_repository.get_template(workflow_template_id, scope=auth.scope)
        draft = gateway.workflow_repository.get_draft(str(template.latest_draft_id), scope=auth.scope)
        if draft.revision != expected_revision:
            raise ProtocolError(
                "WORKFLOW_DRAFT_CONFLICT",
                "Workflow draft revision is stale.",
                {"expected_revision": expected_revision, "actual_revision": draft.revision},
            )
        result = await _rpc(gateway, "workflow.template.publish", params)
        evidence = _record_operation_evidence(
            gateway,
            auth.scope,
            operation="workflow.template.publish",
            workflow_instance_id=body.get("workflow_instance_id"),
            workflow_template_id=workflow_template_id,
            body=body,
            status="idempotent_replayed" if result.get("idempotent") else "succeeded",
            runtime_result_ref=_runtime_result_ref(
                "workflow_version",
                _publish_dto(result).get("workflow_version_id"),
                workflow_instance_id=body.get("workflow_instance_id"),
                workflow_template_id=workflow_template_id,
                operation="workflow.template.publish",
                status="published",
                trace_id=result.get("trace_id"),
            ),
        )
        response = JSONResponse(
            _redact(
                _operation_result(
                    "workflow.template.publish",
                    status="published",
                    resource=_publish_dto(result),
                    trace_id=result.get("trace_id"),
                    evidence=_operation_evidence_dto(evidence) if evidence else None,
                )
            )
        )
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        _record_operation_evidence_error(
            gateway,
            getattr(auth, "scope", None),
            operation="workflow.template.publish",
            workflow_instance_id=body.get("workflow_instance_id") if isinstance(body, dict) else None,
            workflow_template_id=workflow_template_id,
            body=body if isinstance(body, dict) else {},
            error=exc,
        )
        return http_error_response(exc)


@router.get("/instances")
async def list_instances(request: Request, gateway: GatewayService = Depends(get_gateway_service)) -> Any:
    try:
        params: dict[str, Any] = _query_scope_params(request)
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="workflows.read")
        result = await _rpc(gateway, "workflow.instance.list", params)
        response = JSONResponse(_redact([_instance_summary(item) for item in result.get("workflow_instances", [])]))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.get("/instances/{workflow_instance_id}/status")
async def get_instance_status(workflow_instance_id: str, request: Request, gateway: GatewayService = Depends(get_gateway_service)) -> Any:
    try:
        params = {**_query_scope_params(request), "workflow_instance_id": workflow_instance_id}
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="workflows.read")
        result = await _rpc(gateway, "workflow.instance.status", params)
        response = JSONResponse(_redact(_status_dto(result["status"])))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.get("/instances/{workflow_instance_id}/board")
async def get_instance_board(workflow_instance_id: str, request: Request, gateway: GatewayService = Depends(get_gateway_service)) -> Any:
    try:
        params = {**_query_scope_params(request), "workflow_instance_id": workflow_instance_id}
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="board.read")
        result = await _rpc(gateway, "workflow.board.get", params)
        response = JSONResponse(_redact(result["board"]))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.get("/instances/{workflow_instance_id}/canvas-projection")
async def get_instance_canvas_projection(workflow_instance_id: str, request: Request, gateway: GatewayService = Depends(get_gateway_service)) -> Any:
    try:
        params = {**_query_scope_params(request), "workflow_instance_id": workflow_instance_id}
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="board.read")
        instance = gateway.workflow_repository.get_instance(workflow_instance_id, scope=auth.scope)
        template = gateway.workflow_repository.get_template(instance.workflow_template_id, scope=auth.scope)
        draft = gateway.workflow_repository.get_draft(str(template.latest_draft_id), scope=auth.scope)
        board_result = await _rpc(gateway, "workflow.board.get", params)
        status_result = await _rpc(gateway, "workflow.instance.status", params)
        patches = [
            patch.model_dump(mode="json")
            for patch in gateway.workflow_repository.list_patches(scope=auth.scope, workflow_template_id=instance.workflow_template_id)
            if _patch_matches_instance(patch, workflow_instance_id)
        ]
        projection = _canvas_draft_projection_dto(
            workflow_instance_id=workflow_instance_id,
            template_id=instance.workflow_template_id,
            draft=draft.model_dump(mode="json"),
            board=board_result["board"],
            status=_status_dto(status_result["status"]),
            patches=patches,
        )
        response = JSONResponse(_redact(projection))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.get("/instances/{workflow_instance_id}/quality")
async def list_instance_quality(workflow_instance_id: str, request: Request, gateway: GatewayService = Depends(get_gateway_service)) -> Any:
    try:
        params = {**_query_scope_params(request), "workflow_instance_id": workflow_instance_id}
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="quality.read")
        result = await _rpc(gateway, "quality.evaluation.list", params)
        response = JSONResponse(_redact([_quality_dto(item) for item in result.get("evaluations", [])]))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.get("/instances/{workflow_instance_id}/quality/{evaluation_id}")
async def get_instance_quality(
    workflow_instance_id: str,
    evaluation_id: str,
    request: Request,
    gateway: GatewayService = Depends(get_gateway_service),
) -> Any:
    try:
        params = {**_query_scope_params(request), "workflow_instance_id": workflow_instance_id, "evaluation_id": evaluation_id}
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="quality.read")
        result = await _rpc(gateway, "quality.evaluation.get", params)
        evaluation = result["evaluation"]
        _ensure_quality_in_instance(evaluation, workflow_instance_id)
        response = JSONResponse(_redact(_quality_dto(evaluation)))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.get("/instances/{workflow_instance_id}/approvals")
async def list_instance_approvals(workflow_instance_id: str, request: Request, gateway: GatewayService = Depends(get_gateway_service)) -> Any:
    try:
        params = {**_query_scope_params(request), "workflow_instance_id": workflow_instance_id}
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="approvals.read")
        gateway.workflow_repository.get_instance(workflow_instance_id, scope=auth.scope)
        result = await _rpc(gateway, "approval.list", params)
        approvals = [
            _approval_dto(approval)
            for approval in result.get("approvals", [])
            if _approval_workflow_binding(approval).get("workflow_instance_id") == workflow_instance_id
        ]
        response = JSONResponse(_redact(approvals))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.post("/instances/{workflow_instance_id}/approvals/{approval_id}/respond")
async def respond_instance_approval(
    workflow_instance_id: str,
    approval_id: str,
    request: Request,
    gateway: GatewayService = Depends(get_gateway_service),
) -> Any:
    body: dict[str, Any] = {}
    auth: Any = None
    try:
        body = await request.json()
        if not isinstance(body, dict):
            raise ProtocolError("INVALID_PARAMS", "Request body must be an object.", {"field": "body"})
        if body.get("user_confirmed") is not True or body.get("source") != "approval_panel":
            raise ProtocolError("WORKFLOW_ACTION_FORBIDDEN", "Approval response requires explicit user confirmation.", {"source": body.get("source")})
        decision = body.get("decision")
        if decision not in {"approve", "reject"}:
            raise ProtocolError("APPROVAL_INVALID_DECISION", "decision must be approve or reject", {"decision": decision})
        params = {
            **_query_scope_params(request),
            "workflow_instance_id": workflow_instance_id,
            "approval_id": approval_id,
            "decision": decision,
            "reason": body.get("reason"),
        }
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="approvals")
        _require_agent_handoff_for_action(body, target_panel="approval_panel", gateway=gateway, scope=auth.scope, auth=auth, workflow_instance_id=workflow_instance_id, target_resource_id=approval_id)
        approval = gateway.approval_store.get_approval(approval_id)
        _ensure_approval_in_instance(approval, workflow_instance_id)
        result = await _rpc(gateway, "approval.respond", params)
        evidence = _record_operation_evidence(
            gateway,
            auth.scope,
            operation="approval.respond",
            workflow_instance_id=workflow_instance_id,
            workflow_template_id=_template_id_for_instance(gateway, workflow_instance_id, auth.scope),
            body=body,
            status="idempotent_replayed" if result.get("idempotent") else "succeeded",
            runtime_result_ref=_runtime_result_ref(
                "approval",
                approval_id,
                workflow_instance_id=workflow_instance_id,
                workflow_template_id=_template_id_for_instance(gateway, workflow_instance_id, auth.scope),
                operation="approval.respond",
                status=str(result.get("status") or ""),
            ),
        )
        response = JSONResponse(
            _redact(
                _operation_result(
                    "approval.respond",
                    status=str(result.get("status") or ""),
                    resource=_approval_dto(result.get("approval") or {}),
                    idempotent=bool(result.get("idempotent")),
                    workflow_side_effect=result.get("workflow_side_effect"),
                    evidence=_operation_evidence_dto(evidence) if evidence else None,
                )
            )
        )
        add_dev_warning(response, auth)
        return response
    except KeyError as exc:
        return http_error_response(ProtocolError("APPROVAL_NOT_FOUND", str(exc), {"approval_id": approval_id}))
    except ProtocolError as exc:
        _record_operation_evidence_error(
            gateway,
            getattr(auth, "scope", None),
            operation="approval.respond",
            workflow_instance_id=workflow_instance_id,
            workflow_template_id=_safe_template_id_for_instance(gateway, workflow_instance_id, getattr(auth, "scope", None)),
            body=body if isinstance(body, dict) else {},
            error=exc,
            resource_id=approval_id,
        )
        return http_error_response(exc)


@router.get("/instances/{workflow_instance_id}/context")
async def get_instance_context(workflow_instance_id: str, request: Request, gateway: GatewayService = Depends(get_gateway_service)) -> Any:
    try:
        params = {**_query_scope_params(request), "workflow_instance_id": workflow_instance_id}
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="workflow_context.read")
        result = await _rpc(gateway, "workflow.context.get", params)
        response = JSONResponse(_redact(_context_dto(result["context"])))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.post("/instances/{workflow_instance_id}/context/update")
async def update_instance_context(workflow_instance_id: str, request: Request, gateway: GatewayService = Depends(get_gateway_service)) -> Any:
    body: dict[str, Any] = {}
    auth: Any = None
    try:
        body = await request.json()
        if not isinstance(body, dict):
            raise ProtocolError("INVALID_PARAMS", "Request body must be an object.", {"field": "body"})
        if body.get("op") != "set":
            raise ProtocolError("WORKFLOW_CONTEXT_SCOPE_MISMATCH", "Only path-based set is supported.", {"op": body.get("op")})
        path = str(body.get("path") or "")
        if not path.startswith("business.") or path == "business.":
            raise ProtocolError("WORKFLOW_CONTEXT_SCOPE_MISMATCH", "Only business.* context paths can be updated.", {"path": path})
        params = {
            **_query_scope_params(request),
            "workflow_instance_id": workflow_instance_id,
            "path": path,
            "value": body.get("value"),
            "expected_revision": body.get("expected_revision"),
        }
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="workflow_context.write")
        _require_agent_handoff_for_action(body, target_panel="context_panel", gateway=gateway, scope=auth.scope, auth=auth, workflow_instance_id=workflow_instance_id)
        result = await _rpc(gateway, "workflow.context.update", params)
        template_id = _template_id_for_instance(gateway, workflow_instance_id, auth.scope)
        evidence = _record_operation_evidence(
            gateway,
            auth.scope,
            operation="workflow.context.update",
            workflow_instance_id=workflow_instance_id,
            workflow_template_id=template_id,
            body=body,
            status="succeeded",
            runtime_result_ref=_runtime_result_ref(
                "workflow_context",
                workflow_instance_id,
                workflow_instance_id=workflow_instance_id,
                workflow_template_id=template_id,
                operation="workflow.context.update",
                status="updated",
                trace_id=result.get("trace_id"),
            ),
        )
        response = JSONResponse(
            _redact(
                _operation_result(
                    "workflow.context.update",
                    status="updated",
                    resource=_context_dto(result["context"]),
                    trace_id=result.get("trace_id"),
                    evidence=_operation_evidence_dto(evidence) if evidence else None,
                )
            )
        )
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        _record_operation_evidence_error(
            gateway,
            getattr(auth, "scope", None),
            operation="workflow.context.update",
            workflow_instance_id=workflow_instance_id,
            workflow_template_id=_safe_template_id_for_instance(gateway, workflow_instance_id, getattr(auth, "scope", None)),
            body=body if isinstance(body, dict) else {},
            error=exc,
            resource_id=str(body.get("path") or "") if isinstance(body, dict) else None,
        )
        return http_error_response(exc)


@router.post("/instances/{workflow_instance_id}/business-events")
async def emit_instance_business_event(workflow_instance_id: str, request: Request, gateway: GatewayService = Depends(get_gateway_service)) -> Any:
    body: dict[str, Any] = {}
    auth: Any = None
    try:
        body = await request.json()
        if not isinstance(body, dict):
            raise ProtocolError("INVALID_PARAMS", "Request body must be an object.", {"field": "body"})
        event_type = str(body.get("event_type") or body.get("type") or "")
        for denied_prefix in ("meeting.", "knowledge.", "video."):
            if event_type.startswith(denied_prefix):
                raise ProtocolError("BUSINESS_EVENT_INVALID", "Business event cannot use a core business canonical namespace.", {"event_type": event_type})
        if not event_type.startswith("business.") or event_type == "business.*":
            raise ProtocolError("BUSINESS_EVENT_INVALID", "event_type must be a concrete business.* event.", {"event_type": event_type})
        params = {
            **_query_scope_params(request),
            "workflow_instance_id": workflow_instance_id,
            "event": {
                "event_id": body.get("event_id"),
                "idempotency_key": body.get("idempotency_key"),
                "type": event_type,
                "payload": body.get("payload") if isinstance(body.get("payload"), dict) else {},
                "workflow_instance_id": workflow_instance_id,
            },
        }
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="business_events.write")
        _require_agent_handoff_for_action(body, target_panel="context_panel", gateway=gateway, scope=auth.scope, auth=auth, workflow_instance_id=workflow_instance_id)
        binding = body.get("binding")
        if isinstance(binding, dict):
            if not _auth_has_capability(auth, "workflow_context.write"):
                raise ProtocolError(
                    "CAPABILITY_DENIED",
                    "Business event binding requires workflow_context.write capability.",
                    {"capability": "workflow_context.write"},
                )
            existing_bindings = gateway.workflow_repository.list_business_event_bindings(
                scope=auth.scope,
                workflow_instance_id=workflow_instance_id,
                event_type=event_type,
            )
            has_binding = any(
                existing.target_path == binding.get("target_path") and existing.payload_path == binding.get("payload_path")
                for existing in existing_bindings
            )
            bind_params = {
                **params,
                "binding": {
                    "binding_id": binding.get("binding_id") or f"bff_{workflow_instance_id}_{event_type}".replace(".", "_"),
                    "workflow_instance_id": workflow_instance_id,
                    "event_type": event_type,
                    "target_path": binding.get("target_path"),
                    "payload_path": binding.get("payload_path"),
                    "mode": binding.get("mode") or "set",
                    "enabled": binding.get("enabled", True),
                },
            }
            if not has_binding:
                await _rpc(gateway, "business.event.bind", bind_params)
        result = await _rpc(gateway, "business.event.emit", params)
        template_id = _template_id_for_instance(gateway, workflow_instance_id, auth.scope)
        evidence = _record_operation_evidence(
            gateway,
            auth.scope,
            operation="business.event.emit",
            workflow_instance_id=workflow_instance_id,
            workflow_template_id=template_id,
            body=body,
            status="idempotent_replayed" if result.get("idempotent") else "succeeded",
            runtime_result_ref=_runtime_result_ref(
                "business_event",
                result.get("event", {}).get("event_id") if isinstance(result.get("event"), dict) else body.get("event_id"),
                workflow_instance_id=workflow_instance_id,
                workflow_template_id=template_id,
                operation="business.event.emit",
                status="received",
                trace_id=result.get("trace_id"),
            ),
        )
        response = JSONResponse(
            _redact(
                _operation_result(
                    "business.event.emit",
                    status="received",
                    resource={"event": _business_event_dto(result.get("event") or {}), "context": _context_dto(result["context"])},
                    idempotent=bool(result.get("idempotent")),
                    trace_id=result.get("trace_id"),
                    evidence=_operation_evidence_dto(evidence) if evidence else None,
                )
            )
        )
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        _record_operation_evidence_error(
            gateway,
            getattr(auth, "scope", None),
            operation="business.event.emit",
            workflow_instance_id=workflow_instance_id,
            workflow_template_id=_safe_template_id_for_instance(gateway, workflow_instance_id, getattr(auth, "scope", None)),
            body=body if isinstance(body, dict) else {},
            error=exc,
            resource_id=str(body.get("event_id") or body.get("idempotency_key") or body.get("event_type") or "") if isinstance(body, dict) else None,
        )
        return http_error_response(exc)


@router.get("/instances/{workflow_instance_id}/agent/session")
async def get_agent_talk_session(
    workflow_instance_id: str,
    request: Request,
    gateway: GatewayService = Depends(get_gateway_service),
) -> Any:
    try:
        params = {**_query_scope_params(request), "workflow_instance_id": workflow_instance_id}
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="agent_talk.read")
        instance = gateway.workflow_repository.get_instance(workflow_instance_id, scope=auth.scope)
        session = _ensure_agent_talk_session(workflow_instance_id, instance.workflow_template_id, auth.scope, created_by="workflow_console")
        response = JSONResponse(_redact(_agent_session_dto(session)))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.get("/instances/{workflow_instance_id}/agent/interaction-state")
async def get_agent_talk_interaction_state(
    workflow_instance_id: str,
    request: Request,
    gateway: GatewayService = Depends(get_gateway_service),
) -> Any:
    try:
        params = {**_query_scope_params(request), "workflow_instance_id": workflow_instance_id}
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="agent_talk.read")
        instance = gateway.workflow_repository.get_instance(workflow_instance_id, scope=auth.scope)
        session = _ensure_agent_talk_session(workflow_instance_id, instance.workflow_template_id, auth.scope, created_by="workflow_console")
        response = JSONResponse(_redact(_agent_talk_interaction_state_dto(gateway, auth.scope, session)))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.post("/instances/{workflow_instance_id}/agent/messages")
async def create_agent_talk_message(
    workflow_instance_id: str,
    request: Request,
    gateway: GatewayService = Depends(get_gateway_service),
) -> Any:
    try:
        body = await request.json()
        if not isinstance(body, dict):
            raise ProtocolError("INVALID_PARAMS", "Request body must be an object.", {"field": "body"})
        params = {**_query_scope_params(request), "workflow_instance_id": workflow_instance_id}
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="agent_talk.write")
        instance = gateway.workflow_repository.get_instance(workflow_instance_id, scope=auth.scope)
        session = _ensure_agent_talk_session(
            workflow_instance_id,
            instance.workflow_template_id,
            auth.scope,
            created_by=str(body.get("created_by") or "workflow_console"),
        )
        content = str(body.get("content") or "").strip()
        if not content:
            raise ProtocolError("INVALID_PARAMS", "Agent message content is required.", {"field": "content"})
        _reject_forbidden_agent_actions(body.get("action_intent"))
        user_message = _agent_message(
            session,
            role="user",
            content=content,
            source="user",
            resource_refs=_agent_resource_refs(workflow_instance_id=workflow_instance_id, workflow_template_id=instance.workflow_template_id),
        )
        assistant_message = _agent_message(
            session,
            role="assistant",
            content=_agent_assistant_reply(content),
            source="assistant",
            resource_refs=_agent_resource_refs(workflow_instance_id=workflow_instance_id, workflow_template_id=instance.workflow_template_id),
        )
        messages = _AGENT_TALK_MESSAGES.setdefault(session["agent_session_id"], [])
        messages.extend([user_message, assistant_message])
        preferred_patch_id = await _maybe_create_agent_canvas_patch(
            gateway,
            workflow_instance_id,
            instance.workflow_template_id,
            auth.scope,
            content,
            body,
        )
        suggestions = _generate_agent_suggestions(
            gateway,
            workflow_instance_id,
            instance.workflow_template_id,
            auth.scope,
            preferred_patch_id=preferred_patch_id,
        )
        _AGENT_TALK_SUGGESTIONS[session["agent_session_id"]] = suggestions
        _AGENT_ACTION_PROPOSALS[session["agent_session_id"]] = []
        _ensure_agent_action_proposals(session, suggestions)
        _record_agent_audit(
            "agent.message.created",
            session=session,
            summary="Agent message created and deterministic suggestions generated.",
            resource_refs=user_message["resource_refs"],
        )
        response = JSONResponse(_redact(_agent_session_dto(session)))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.get("/instances/{workflow_instance_id}/agent/action-proposals")
async def list_agent_action_proposals(
    workflow_instance_id: str,
    request: Request,
    gateway: GatewayService = Depends(get_gateway_service),
) -> Any:
    try:
        params = {**_query_scope_params(request), "workflow_instance_id": workflow_instance_id}
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="agent_actions.read")
        instance = gateway.workflow_repository.get_instance(workflow_instance_id, scope=auth.scope)
        session = _ensure_agent_talk_session(workflow_instance_id, instance.workflow_template_id, auth.scope, created_by="workflow_console")
        suggestions = _AGENT_TALK_SUGGESTIONS.get(session["agent_session_id"])
        if not suggestions:
            suggestions = _generate_agent_suggestions(gateway, workflow_instance_id, instance.workflow_template_id, auth.scope)
            _AGENT_TALK_SUGGESTIONS[session["agent_session_id"]] = suggestions
        proposals = _ensure_agent_action_proposals(session, suggestions)
        response = JSONResponse(_redact([_agent_action_proposal_dto(item) for item in proposals]))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.post("/instances/{workflow_instance_id}/agent/action-proposals")
async def create_agent_action_proposal(
    workflow_instance_id: str,
    request: Request,
    gateway: GatewayService = Depends(get_gateway_service),
) -> Any:
    try:
        body = await request.json()
        if not isinstance(body, dict):
            raise ProtocolError("INVALID_PARAMS", "Request body must be an object.", {"field": "body"})
        params = {**_query_scope_params(request), "workflow_instance_id": workflow_instance_id}
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="agent_actions.write")
        instance = gateway.workflow_repository.get_instance(workflow_instance_id, scope=auth.scope)
        session = _ensure_agent_talk_session(workflow_instance_id, instance.workflow_template_id, auth.scope, created_by="workflow_console")
        proposal = _agent_action_proposal_from_request(session, body)
        _AGENT_ACTION_PROPOSALS.setdefault(session["agent_session_id"], []).append(proposal)
        _record_agent_audit(
            "agent.action_proposal.created",
            session=session,
            summary="Agent action proposal created.",
            resource_refs=proposal["resource_refs"],
        )
        response = JSONResponse(_redact(_agent_action_proposal_dto(proposal)))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.get("/instances/{workflow_instance_id}/agent/action-proposals/{proposal_id}")
async def get_agent_action_proposal(
    workflow_instance_id: str,
    proposal_id: str,
    request: Request,
    gateway: GatewayService = Depends(get_gateway_service),
) -> Any:
    try:
        params = {**_query_scope_params(request), "workflow_instance_id": workflow_instance_id}
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="agent_actions.read")
        instance = gateway.workflow_repository.get_instance(workflow_instance_id, scope=auth.scope)
        session = _ensure_agent_talk_session(workflow_instance_id, instance.workflow_template_id, auth.scope, created_by="workflow_console")
        proposal = _find_agent_action_proposal(session["agent_session_id"], proposal_id)
        response = JSONResponse(_redact(_agent_action_proposal_dto(proposal)))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.post("/instances/{workflow_instance_id}/agent/action-proposals/{proposal_id}/dismiss")
async def dismiss_agent_action_proposal(
    workflow_instance_id: str,
    proposal_id: str,
    request: Request,
    gateway: GatewayService = Depends(get_gateway_service),
) -> Any:
    try:
        params = {**_query_scope_params(request), "workflow_instance_id": workflow_instance_id}
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="agent_actions.write")
        instance = gateway.workflow_repository.get_instance(workflow_instance_id, scope=auth.scope)
        session = _ensure_agent_talk_session(workflow_instance_id, instance.workflow_template_id, auth.scope, created_by="workflow_console")
        proposal = _find_agent_action_proposal(session["agent_session_id"], proposal_id)
        proposal["lifecycle"] = "dismissed"
        proposal["status"] = "dismissed"
        proposal["updated_at"] = _now_iso()
        _record_agent_audit(
            "agent.action_proposal.dismissed",
            session=session,
            summary="Agent action proposal dismissed.",
            resource_refs=proposal["resource_refs"],
        )
        response = JSONResponse(_redact(_agent_action_proposal_dto(proposal)))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.post("/instances/{workflow_instance_id}/agent/action-proposals/{proposal_id}/handoff")
async def create_agent_action_handoff(
    workflow_instance_id: str,
    proposal_id: str,
    request: Request,
    gateway: GatewayService = Depends(get_gateway_service),
) -> Any:
    try:
        body = await request.json()
        if not isinstance(body, dict):
            raise ProtocolError("INVALID_PARAMS", "Request body must be an object.", {"field": "body"})
        params = {**_query_scope_params(request), "workflow_instance_id": workflow_instance_id}
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="agent_handoffs.write")
        instance = gateway.workflow_repository.get_instance(workflow_instance_id, scope=auth.scope)
        session = _ensure_agent_talk_session(workflow_instance_id, instance.workflow_template_id, auth.scope, created_by="workflow_console")
        proposal = _find_agent_action_proposal(session["agent_session_id"], proposal_id)
        target_panel = _normalize_handoff_target_panel(body.get("target_panel") or proposal.get("target_panel"))
        _ensure_proposal_can_handoff(proposal, target_panel)
        handoff = _AGENT_HANDOFF_REPOSITORY.create(_agent_action_handoff(gateway, auth.scope, session, proposal, target_panel, body))
        proposal["lifecycle"] = "reviewed"
        proposal["status"] = "reviewed"
        proposal["updated_at"] = _now_iso()
        _record_agent_audit(
            "agent.handoff_created",
            session=session,
            summary="Agent action handoff created for user-confirmed panel.",
            resource_refs=handoff["target_resource"],
        )
        _append_handoff_audit(handoff["handoff_id"], "handoff_created", summary="Agent action handoff created.", data=handoff["target_resource"])
        response = JSONResponse(_redact(_agent_action_handoff_dto(handoff)))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.get("/instances/{workflow_instance_id}/agent/action-handoffs")
async def list_agent_action_handoffs(
    workflow_instance_id: str,
    request: Request,
    gateway: GatewayService = Depends(get_gateway_service),
) -> Any:
    try:
        params = {**_query_scope_params(request), "workflow_instance_id": workflow_instance_id}
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="agent_handoffs.read")
        instance = gateway.workflow_repository.get_instance(workflow_instance_id, scope=auth.scope)
        session = _ensure_agent_talk_session(workflow_instance_id, instance.workflow_template_id, auth.scope, created_by="workflow_console")
        handoffs = [
            _refresh_handoff_for_read(gateway, auth.scope, handoff)
            for handoff in _AGENT_HANDOFF_REPOSITORY.list(agent_session_id=session["agent_session_id"], workflow_instance_id=workflow_instance_id)
        ]
        response = JSONResponse(_redact([_agent_action_handoff_dto(item) for item in handoffs]))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.get("/instances/{workflow_instance_id}/agent/action-handoffs/{handoff_id}")
async def get_agent_action_handoff(
    workflow_instance_id: str,
    handoff_id: str,
    request: Request,
    gateway: GatewayService = Depends(get_gateway_service),
) -> Any:
    try:
        params = {**_query_scope_params(request), "workflow_instance_id": workflow_instance_id}
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="agent_handoffs.read")
        instance = gateway.workflow_repository.get_instance(workflow_instance_id, scope=auth.scope)
        session = _ensure_agent_talk_session(workflow_instance_id, instance.workflow_template_id, auth.scope, created_by="workflow_console")
        handoff = _find_agent_action_handoff(session["agent_session_id"], handoff_id)
        handoff = _refresh_handoff_for_read(gateway, auth.scope, handoff)
        if handoff.get("status") == "active":
            handoff = _AGENT_HANDOFF_REPOSITORY.mark_opened(handoff_id)
            _append_handoff_audit(handoff_id, "handoff_opened", summary="Agent action handoff opened.", data=handoff.get("target_resource") if isinstance(handoff.get("target_resource"), dict) else {})
        _record_agent_audit(
            "agent.handoff_opened",
            session=session,
            summary="Agent action handoff opened.",
            resource_refs=handoff["target_resource"],
        )
        response = JSONResponse(_redact(_agent_action_handoff_dto(handoff)))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.get("/instances/{workflow_instance_id}/agent/action-handoffs/{handoff_id}/audit")
async def list_agent_action_handoff_audit(
    workflow_instance_id: str,
    handoff_id: str,
    request: Request,
    gateway: GatewayService = Depends(get_gateway_service),
) -> Any:
    try:
        params = {**_query_scope_params(request), "workflow_instance_id": workflow_instance_id}
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="agent_audit.read")
        instance = gateway.workflow_repository.get_instance(workflow_instance_id, scope=auth.scope)
        session = _ensure_agent_talk_session(workflow_instance_id, instance.workflow_template_id, auth.scope, created_by="workflow_console")
        handoff = _find_agent_action_handoff(session["agent_session_id"], handoff_id)
        if handoff.get("workflow_instance_id") != workflow_instance_id:
            raise ProtocolError("SCOPE_MISMATCH", "Agent handoff does not belong to workflow instance.", {"resource": "handoff_id"})
        response = JSONResponse(_redact(_AGENT_HANDOFF_REPOSITORY.list_audit(handoff_id)))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.get("/instances/{workflow_instance_id}/agent/operation-evidence")
async def list_agent_operation_evidence(
    workflow_instance_id: str,
    request: Request,
    gateway: GatewayService = Depends(get_gateway_service),
) -> Any:
    try:
        params = {**_query_scope_params(request), "workflow_instance_id": workflow_instance_id}
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="operation_evidence.read")
        gateway.workflow_repository.get_instance(workflow_instance_id, scope=auth.scope)
        records = _AGENT_OPERATION_EVIDENCE_REPOSITORY.list(workflow_instance_id=workflow_instance_id)
        response = JSONResponse(_redact([_operation_evidence_dto(item) for item in records]))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.get("/instances/{workflow_instance_id}/agent/operation-evidence/{evidence_id}")
async def get_agent_operation_evidence(
    workflow_instance_id: str,
    evidence_id: str,
    request: Request,
    gateway: GatewayService = Depends(get_gateway_service),
) -> Any:
    try:
        params = {**_query_scope_params(request), "workflow_instance_id": workflow_instance_id}
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="operation_evidence.read")
        gateway.workflow_repository.get_instance(workflow_instance_id, scope=auth.scope)
        evidence = _AGENT_OPERATION_EVIDENCE_REPOSITORY.get(evidence_id)
        if evidence.get("workflow_instance_id") != workflow_instance_id:
            raise ProtocolError("SCOPE_MISMATCH", "Operation evidence does not belong to workflow instance.", {"resource": "evidence_id"})
        response = JSONResponse(_redact(_operation_evidence_dto(evidence)))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.get("/instances/{workflow_instance_id}/agent/governance-review")
async def get_agent_governance_review(
    workflow_instance_id: str,
    request: Request,
    gateway: GatewayService = Depends(get_gateway_service),
) -> Any:
    try:
        params = {**_query_scope_params(request), "workflow_instance_id": workflow_instance_id}
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="governance_review.read")
        instance = gateway.workflow_repository.get_instance(workflow_instance_id, scope=auth.scope)
        records = _AGENT_OPERATION_EVIDENCE_REPOSITORY.list(workflow_instance_id=workflow_instance_id)
        handoffs = _AGENT_HANDOFF_REPOSITORY.list(workflow_instance_id=workflow_instance_id)
        response = JSONResponse(
            _redact(
                _governance_review_dto(
                    workflow_instance_id=workflow_instance_id,
                    workflow_template_id=instance.workflow_template_id,
                    evidence_records=records,
                    handoffs=handoffs,
                )
            )
        )
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.post("/instances/{workflow_instance_id}/agent/action-handoffs/{handoff_id}/dismiss")
async def dismiss_agent_action_handoff(
    workflow_instance_id: str,
    handoff_id: str,
    request: Request,
    gateway: GatewayService = Depends(get_gateway_service),
) -> Any:
    try:
        params = {**_query_scope_params(request), "workflow_instance_id": workflow_instance_id}
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="agent_handoffs.write")
        instance = gateway.workflow_repository.get_instance(workflow_instance_id, scope=auth.scope)
        session = _ensure_agent_talk_session(workflow_instance_id, instance.workflow_template_id, auth.scope, created_by="workflow_console")
        handoff = _find_agent_action_handoff(session["agent_session_id"], handoff_id)
        handoff = _refresh_handoff_for_read(gateway, auth.scope, handoff)
        dismissed = _AGENT_HANDOFF_REPOSITORY.dismiss(handoff_id)
        _append_handoff_audit(handoff_id, "handoff_dismissed", summary="Agent action handoff dismissed.", data=dismissed.get("target_resource") if isinstance(dismissed.get("target_resource"), dict) else {})
        response = JSONResponse(_redact(_agent_action_handoff_dto(dismissed)))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.get("/instances/{workflow_instance_id}/agent/suggestions")
async def list_agent_talk_suggestions(
    workflow_instance_id: str,
    request: Request,
    gateway: GatewayService = Depends(get_gateway_service),
) -> Any:
    try:
        params = {**_query_scope_params(request), "workflow_instance_id": workflow_instance_id}
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="agent_suggestions.read")
        instance = gateway.workflow_repository.get_instance(workflow_instance_id, scope=auth.scope)
        session = _ensure_agent_talk_session(workflow_instance_id, instance.workflow_template_id, auth.scope, created_by="workflow_console")
        suggestions = _AGENT_TALK_SUGGESTIONS.get(session["agent_session_id"])
        if not suggestions:
            suggestions = _generate_agent_suggestions(gateway, workflow_instance_id, instance.workflow_template_id, auth.scope)
            _AGENT_TALK_SUGGESTIONS[session["agent_session_id"]] = suggestions
        response = JSONResponse(_redact([_agent_suggestion_dto(item) for item in suggestions]))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.post("/instances/{workflow_instance_id}/agent/suggestions/{suggestion_id}/dismiss")
async def dismiss_agent_talk_suggestion(
    workflow_instance_id: str,
    suggestion_id: str,
    request: Request,
    gateway: GatewayService = Depends(get_gateway_service),
) -> Any:
    try:
        params = {**_query_scope_params(request), "workflow_instance_id": workflow_instance_id}
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="agent_suggestions.write")
        instance = gateway.workflow_repository.get_instance(workflow_instance_id, scope=auth.scope)
        session = _ensure_agent_talk_session(workflow_instance_id, instance.workflow_template_id, auth.scope, created_by="workflow_console")
        suggestions = _AGENT_TALK_SUGGESTIONS.get(session["agent_session_id"], [])
        suggestion = next((item for item in suggestions if item.get("suggestion_id") == suggestion_id), None)
        if suggestion is None:
            raise ProtocolError("METHOD_NOT_FOUND", "Agent suggestion was not found.", {"suggestion_id": suggestion_id})
        suggestion["status"] = "dismissed"
        _record_agent_audit(
            "agent.suggestion.dismissed",
            session=session,
            summary="Agent suggestion dismissed.",
            resource_refs=_agent_resource_refs(
                workflow_instance_id=workflow_instance_id,
                workflow_template_id=instance.workflow_template_id,
                suggestion_id=suggestion_id,
            ),
        )
        response = JSONResponse(_redact(_agent_suggestion_dto(suggestion)))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.post("/workflows/{workflow_template_id}/patches")
async def propose_workflow_patch(
    workflow_template_id: str,
    request: Request,
    gateway: GatewayService = Depends(get_gateway_service),
) -> Any:
    try:
        body = await request.json()
        if not isinstance(body, dict):
            raise ProtocolError("INVALID_PARAMS", "Request body must be an object.", {"field": "body"})
        patch = _canvas_patch_request_to_patch(workflow_template_id, body)
        params = {**_query_scope_params(request), "workflow_template_id": workflow_template_id, "patch": patch}
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="workflow_patches.write")
        _validate_canvas_patch_payload(gateway, workflow_template_id, patch, auth.scope)
        result = await _rpc(gateway, "workflow.patch.propose", params)
        response = JSONResponse(_redact(_patch_proposal_dto(result["patch"])))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.get("/instances/{workflow_instance_id}/patches")
async def list_instance_patches(
    workflow_instance_id: str,
    request: Request,
    gateway: GatewayService = Depends(get_gateway_service),
) -> Any:
    try:
        params = {**_query_scope_params(request), "workflow_instance_id": workflow_instance_id}
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="workflow_patches.read")
        instance = gateway.workflow_repository.get_instance(workflow_instance_id, scope=auth.scope)
        template = gateway.workflow_repository.get_template(instance.workflow_template_id, scope=auth.scope)
        draft = gateway.workflow_repository.get_draft(str(template.latest_draft_id), scope=auth.scope)
        patches = [
            patch.model_dump(mode="json")
            for patch in gateway.workflow_repository.list_patches(scope=auth.scope, workflow_template_id=instance.workflow_template_id)
            if _patch_matches_instance(patch, workflow_instance_id)
        ]
        response = JSONResponse(_redact(_patch_queue_dto(patches, current_draft_revision=draft.revision)))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.get("/workflows/{workflow_template_id}/patches")
async def list_workflow_patch_queue(
    workflow_template_id: str,
    request: Request,
    gateway: GatewayService = Depends(get_gateway_service),
) -> Any:
    try:
        params = {**_query_scope_params(request), "workflow_template_id": workflow_template_id}
        workflow_instance_id = request.query_params.get("workflow_instance_id")
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="workflow_patches.read")
        template = gateway.workflow_repository.get_template(workflow_template_id, scope=auth.scope)
        if isinstance(workflow_instance_id, str) and workflow_instance_id:
            instance = gateway.workflow_repository.get_instance(workflow_instance_id, scope=auth.scope)
            if instance.workflow_template_id != workflow_template_id:
                raise ProtocolError("SCOPE_MISMATCH", "Workflow instance does not belong to workflow template.", {"resource": "workflow_instance_id"})
        draft = gateway.workflow_repository.get_draft(str(template.latest_draft_id), scope=auth.scope)
        patches = [
            patch.model_dump(mode="json")
            for patch in gateway.workflow_repository.list_patches(scope=auth.scope, workflow_template_id=workflow_template_id)
            if not workflow_instance_id or _patch_matches_instance(patch, workflow_instance_id)
        ]
        response = JSONResponse(_redact(_patch_queue_dto(patches, current_draft_revision=draft.revision)))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.get("/workflows/{workflow_template_id}/patches/{workflow_patch_id}/diff")
async def get_workflow_patch_diff(
    workflow_template_id: str,
    workflow_patch_id: str,
    request: Request,
    gateway: GatewayService = Depends(get_gateway_service),
) -> Any:
    try:
        params = {**_query_scope_params(request), "workflow_template_id": workflow_template_id, "workflow_patch_id": workflow_patch_id}
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="workflow_patches.read")
        _ensure_patch_in_template(gateway, workflow_patch_id, workflow_template_id, auth.scope)
        result = await _rpc(gateway, "workflow.patch.diff", params)
        response = JSONResponse(_redact(_patch_diff_dto(result["diff"])))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.post("/workflows/{workflow_template_id}/patches/{workflow_patch_id}/apply")
async def apply_workflow_patch(
    workflow_template_id: str,
    workflow_patch_id: str,
    request: Request,
    gateway: GatewayService = Depends(get_gateway_service),
) -> Any:
    body: dict[str, Any] = {}
    auth: Any = None
    try:
        body = await request.json()
        if not isinstance(body, dict):
            raise ProtocolError("INVALID_PARAMS", "Request body must be an object.", {"field": "body"})
        _require_user_confirmed(body, allowed_sources={"editing_panel", "workflow_console"})
        params = {**_query_scope_params(request), "workflow_template_id": workflow_template_id, "workflow_patch_id": workflow_patch_id}
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="workflow_patches.write")
        _require_agent_handoff_for_action(
            body,
            target_panel="editing_panel",
            gateway=gateway,
            scope=auth.scope,
            auth=auth,
            workflow_instance_id=body.get("workflow_instance_id"),
            target_resource_id=workflow_patch_id,
        )
        patch = _ensure_patch_editable_for_template(gateway, workflow_patch_id, workflow_template_id, auth.scope, workflow_instance_id=body.get("workflow_instance_id"))
        if patch.status != "applied":
            diff_result = await _rpc(gateway, "workflow.patch.diff", params)
            diff = _patch_diff_dto(diff_result["diff"])
            if diff["requires_approval"]:
                raise ProtocolError(
                    "WORKFLOW_ACTION_FORBIDDEN",
                    "Patch requires approval before apply.",
                    {
                        "workflow_patch_id": workflow_patch_id,
                        "requires_approval": True,
                        "risk_flags": diff["risk_flags"],
                    },
                )
        result = await _rpc(gateway, "workflow.patch.apply", {**params, "actor_type": "user"})
        evidence = _record_operation_evidence(
            gateway,
            auth.scope,
            operation="workflow.patch.apply",
            workflow_instance_id=body.get("workflow_instance_id"),
            workflow_template_id=workflow_template_id,
            body=body,
            status="idempotent_replayed" if result.get("idempotent") else "succeeded",
            runtime_result_ref=_runtime_result_ref(
                "workflow_patch",
                workflow_patch_id,
                workflow_instance_id=body.get("workflow_instance_id"),
                workflow_template_id=workflow_template_id,
                operation="workflow.patch.apply",
                status=str(result.get("patch", {}).get("status") or "applied"),
                trace_id=result.get("trace_id"),
            ),
            resource_id=workflow_patch_id,
        )
        response = JSONResponse(
            _redact(
                _operation_result(
                    "workflow.patch.apply",
                    status=str(result.get("patch", {}).get("status") or "applied"),
                    resource=_patch_action_dto(result),
                    trace_id=result.get("trace_id"),
                    idempotent=bool(result.get("idempotent")),
                    evidence=_operation_evidence_dto(evidence) if evidence else None,
                )
            )
        )
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        _record_operation_evidence_error(
            gateway,
            getattr(auth, "scope", None),
            operation="workflow.patch.apply",
            workflow_instance_id=body.get("workflow_instance_id") if isinstance(body, dict) else None,
            workflow_template_id=workflow_template_id,
            body=body if isinstance(body, dict) else {},
            error=exc,
            resource_id=workflow_patch_id,
        )
        return http_error_response(exc)


@router.post("/workflows/{workflow_template_id}/patches/{workflow_patch_id}/reject")
async def reject_workflow_patch(
    workflow_template_id: str,
    workflow_patch_id: str,
    request: Request,
    gateway: GatewayService = Depends(get_gateway_service),
) -> Any:
    body: dict[str, Any] = {}
    auth: Any = None
    try:
        body = await request.json()
        if not isinstance(body, dict):
            raise ProtocolError("INVALID_PARAMS", "Request body must be an object.", {"field": "body"})
        _require_user_confirmed(body, allowed_sources={"editing_panel", "workflow_console"})
        params = {**_query_scope_params(request), "workflow_template_id": workflow_template_id, "workflow_patch_id": workflow_patch_id}
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="workflow_patches.write")
        _require_agent_handoff_for_action(
            body,
            target_panel="editing_panel",
            gateway=gateway,
            scope=auth.scope,
            auth=auth,
            workflow_instance_id=body.get("workflow_instance_id"),
            target_resource_id=workflow_patch_id,
        )
        _ensure_patch_editable_for_template(gateway, workflow_patch_id, workflow_template_id, auth.scope, workflow_instance_id=body.get("workflow_instance_id"))
        result = await _rpc(gateway, "workflow.patch.reject", {**params, "reason": body.get("reason")})
        evidence = _record_operation_evidence(
            gateway,
            auth.scope,
            operation="workflow.patch.reject",
            workflow_instance_id=body.get("workflow_instance_id"),
            workflow_template_id=workflow_template_id,
            body=body,
            status="idempotent_replayed" if result.get("idempotent") else "succeeded",
            runtime_result_ref=_runtime_result_ref(
                "workflow_patch",
                workflow_patch_id,
                workflow_instance_id=body.get("workflow_instance_id"),
                workflow_template_id=workflow_template_id,
                operation="workflow.patch.reject",
                status=str(result.get("patch", {}).get("status") or "rejected"),
                trace_id=result.get("trace_id"),
            ),
            resource_id=workflow_patch_id,
        )
        response = JSONResponse(
            _redact(
                _operation_result(
                    "workflow.patch.reject",
                    status=str(result.get("patch", {}).get("status") or "rejected"),
                    resource=_patch_action_dto(result),
                    trace_id=result.get("trace_id"),
                    idempotent=bool(result.get("idempotent")),
                    evidence=_operation_evidence_dto(evidence) if evidence else None,
                )
            )
        )
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        _record_operation_evidence_error(
            gateway,
            getattr(auth, "scope", None),
            operation="workflow.patch.reject",
            workflow_instance_id=body.get("workflow_instance_id") if isinstance(body, dict) else None,
            workflow_template_id=workflow_template_id,
            body=body if isinstance(body, dict) else {},
            error=exc,
            resource_id=workflow_patch_id,
        )
        return http_error_response(exc)


@router.get("/instances/{workflow_instance_id}/patches/{workflow_patch_id}/diff")
async def get_instance_patch_diff(
    workflow_instance_id: str,
    workflow_patch_id: str,
    request: Request,
    gateway: GatewayService = Depends(get_gateway_service),
) -> Any:
    try:
        params = {**_query_scope_params(request), "workflow_instance_id": workflow_instance_id, "workflow_patch_id": workflow_patch_id}
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="workflow_patches.read")
        _ensure_patch_in_instance(gateway, workflow_patch_id, workflow_instance_id, auth.scope)
        result = await _rpc(gateway, "workflow.patch.diff", params)
        response = JSONResponse(_redact(_patch_diff_dto(result["diff"])))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.get("/stations/{station_run_id}/outputs")
async def list_station_outputs(station_run_id: str, request: Request, gateway: GatewayService = Depends(get_gateway_service)) -> Any:
    try:
        params = {**_query_scope_params(request), "station_run_id": station_run_id}
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="stations.read")
        result = await _rpc(gateway, "station.output.list", params)
        response = JSONResponse(_redact(result.get("artifacts", [])))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.get("/instances/{workflow_instance_id}/stations/{station_run_id}/outputs")
async def list_instance_station_outputs(
    workflow_instance_id: str,
    station_run_id: str,
    request: Request,
    gateway: GatewayService = Depends(get_gateway_service),
) -> Any:
    try:
        params = {**_query_scope_params(request), "workflow_instance_id": workflow_instance_id, "station_run_id": station_run_id}
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="stations.read")
        _ensure_station_run_in_instance(gateway, station_run_id, workflow_instance_id, auth.scope)
        result = await _rpc(gateway, "station.output.list", params)
        response = JSONResponse(_redact(result.get("artifacts", [])))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.get("/artifacts/{artifact_id}/metadata")
async def get_artifact_metadata(artifact_id: str, request: Request, gateway: GatewayService = Depends(get_gateway_service)) -> Any:
    return await _artifact_metadata_response(artifact_id, request, gateway, workflow_instance_id=None)


@router.get("/instances/{workflow_instance_id}/artifacts/{artifact_id}/metadata")
async def get_instance_artifact_metadata(
    workflow_instance_id: str,
    artifact_id: str,
    request: Request,
    gateway: GatewayService = Depends(get_gateway_service),
) -> Any:
    return await _artifact_metadata_response(artifact_id, request, gateway, workflow_instance_id=workflow_instance_id)


@router.get("/artifacts/{artifact_id}/lineage")
async def get_artifact_lineage(artifact_id: str, request: Request, gateway: GatewayService = Depends(get_gateway_service)) -> Any:
    return await _artifact_lineage_response(artifact_id, request, gateway, workflow_instance_id=None)


@router.get("/instances/{workflow_instance_id}/artifacts/{artifact_id}/lineage")
async def get_instance_artifact_lineage(
    workflow_instance_id: str,
    artifact_id: str,
    request: Request,
    gateway: GatewayService = Depends(get_gateway_service),
) -> Any:
    return await _artifact_lineage_response(artifact_id, request, gateway, workflow_instance_id=workflow_instance_id)


@router.get("/events/subscribe")
async def subscribe_events(request: Request, gateway: GatewayService = Depends(get_gateway_service)) -> Any:
    params = dict(request.query_params)
    try:
        channels = normalize_event_channels(params.get("channels"))
        auth_params = dict(params)
        auth = await authorize_http_request(request, gateway=gateway, params=auth_params, capability="events")
        capabilities = tuple(auth_params.get("_auth_capabilities") or ())
        ensure_channel_capabilities(channels, capabilities)
        cursor = request.headers.get("last-event-id") or params.get("cursor") or params.get("last_event_id")
        start_sequence = read_event_cursor(cursor, auth.scope)
    except ProtocolError as exc:
        return http_error_response(exc)

    filters = {
        key: params.get(key)
        for key in ("workflow_instance_id", "workflow_patch_id", "approval_id", "artifact_id", "job_id", "trace_id")
        if params.get(key)
    }
    follow = _truthy(params.get("follow"))
    heartbeat_interval = _float_param(params.get("heartbeat_interval"), default=15.0)
    max_heartbeats = _int_param(params.get("max_heartbeats"))

    async def event_source():
        last_sequence = start_sequence
        sent_keys: set[tuple[str, str]] = set()
        events, last_sequence = _collect_unsent_events(
            gateway,
            scope=auth.scope,
            channels=channels,
            filters=filters,
            last_sequence=last_sequence,
            sent_keys=sent_keys,
        )
        for event in events:
            yield sse_frame(_redact(event))
        if not follow:
            return
        sent_heartbeats = 0
        while True:
            await asyncio.sleep(max(heartbeat_interval, 0.01))
            events, last_sequence = _collect_unsent_events(
                gateway,
                scope=auth.scope,
                channels=channels,
                filters=filters,
                last_sequence=last_sequence,
                sent_keys=sent_keys,
            )
            if events:
                for event in events:
                    yield sse_frame(_redact(event))
                continue
            yield heartbeat_frame()
            sent_heartbeats += 1
            if max_heartbeats is not None and sent_heartbeats >= max_heartbeats:
                return

    response = StreamingResponse(event_source(), media_type="text/event-stream")
    response.headers["Cache-Control"] = "no-cache"
    add_dev_warning(response, auth)
    return response


async def _artifact_metadata_response(
    artifact_id: str,
    request: Request,
    gateway: GatewayService,
    *,
    workflow_instance_id: str | None,
) -> Any:
    try:
        params = {**_query_scope_params(request), "artifact_id": artifact_id}
        if workflow_instance_id:
            params["workflow_instance_id"] = workflow_instance_id
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="artifacts.read")
        if workflow_instance_id:
            _ensure_artifact_in_instance(gateway, artifact_id, workflow_instance_id, auth.scope)
        result = await _rpc(gateway, "artifact.read_metadata", params)
        response = JSONResponse(_redact(result["artifact"]))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


async def _artifact_lineage_response(
    artifact_id: str,
    request: Request,
    gateway: GatewayService,
    *,
    workflow_instance_id: str | None,
) -> Any:
    try:
        params = {**_query_scope_params(request), "artifact_id": artifact_id}
        if workflow_instance_id:
            params["workflow_instance_id"] = workflow_instance_id
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="artifacts.read")
        if workflow_instance_id:
            _ensure_artifact_in_instance(gateway, artifact_id, workflow_instance_id, auth.scope)
        result = await _rpc(gateway, "artifact.lineage", params)
        response = JSONResponse(_redact(result))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


async def _rpc(gateway: GatewayService, method: str, params: dict[str, Any]) -> dict[str, Any]:
    response = await gateway.handle_rpc(RpcRequest(id=method, method=method, params=params))
    if response.error is not None:
        raise ProtocolError(response.error.code, response.error.message, response.error.data or {})
    return response.result or {}


def _workflow_summary(template: dict[str, Any]) -> dict[str, Any]:
    return {
        "workflow_template_id": template.get("workflow_template_id"),
        "name": template.get("name"),
        "latest_version_id": template.get("latest_published_version_id"),
        "status": template.get("status"),
    }


def _version_summary(version: dict[str, Any]) -> dict[str, Any]:
    return {
        "workflow_version_id": version.get("workflow_version_id"),
        "workflow_template_id": version.get("workflow_template_id"),
        "version": version.get("version"),
    }


def _instance_summary(instance: dict[str, Any]) -> dict[str, Any]:
    return {
        "workflow_instance_id": instance.get("workflow_instance_id"),
        "workflow_template_id": instance.get("workflow_template_id"),
        "workflow_version_id": instance.get("workflow_version_id"),
        "status": instance.get("status"),
    }


def _status_dto(status: dict[str, Any]) -> dict[str, Any]:
    return {
        "workflow_instance_id": status.get("workflow_instance_id"),
        "status": status.get("status"),
        "current_station_ids": status.get("current_station_ids") or [],
        "station_counts": status.get("station_run_status_counts") or {},
        "job_counts": status.get("job_status_counts") or {},
        "artifact_count": status.get("artifact_count") or 0,
        "quality_count": status.get("quality_evaluation_count") or 0,
    }


def _quality_dto(evaluation: dict[str, Any]) -> dict[str, Any]:
    return {
        "evaluation_id": evaluation.get("evaluation_id"),
        "workflow_instance_id": evaluation.get("workflow_instance_id"),
        "station_run_id": evaluation.get("station_run_id"),
        "artifact_id": evaluation.get("artifact_id"),
        "rubric_id": evaluation.get("rubric_id"),
        "evaluator_type": evaluation.get("evaluator_type"),
        "score": evaluation.get("score"),
        "status": evaluation.get("status"),
        "issues": evaluation.get("issues") or [],
        "suggestions": evaluation.get("suggestions") or [],
        "created_at": evaluation.get("created_at"),
    }


def _approval_dto(approval: dict[str, Any]) -> dict[str, Any]:
    binding = _approval_workflow_binding(approval)
    return {
        "approval_id": approval.get("approval_id"),
        "workflow_instance_id": binding.get("workflow_instance_id"),
        "station_run_id": binding.get("station_run_id"),
        "station_id": binding.get("station_id"),
        "status": approval.get("status"),
        "action": approval.get("action"),
        "request_summary": approval.get("request_summary"),
        "risk_level": approval.get("risk_level"),
        "decision_reason": approval.get("decision_reason"),
        "active": binding.get("active", True),
        "inactive_reason": binding.get("inactive_reason"),
        "created_at": approval.get("created_at"),
        "decided_at": approval.get("decided_at"),
    }


def _context_dto(context: dict[str, Any]) -> dict[str, Any]:
    return {
        "workflow_instance_id": context.get("workflow_instance_id"),
        "revision": context.get("revision"),
        "business": context.get("business") if isinstance(context.get("business"), dict) else {},
        "updated_at": context.get("updated_at"),
        "trace_id": context.get("trace_id"),
    }


def _business_event_dto(event: dict[str, Any]) -> dict[str, Any]:
    return {
        "event_id": event.get("event_id"),
        "idempotency_key": event.get("idempotency_key"),
        "type": event.get("type"),
        "workflow_instance_id": event.get("workflow_instance_id"),
        "payload": event.get("payload") if isinstance(event.get("payload"), dict) else {},
    }


def _node_catalog_item_dto(node_template_id: str, contract: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": node_template_id,
        "label": NODE_CATALOG_LABELS.get(node_template_id, node_template_id.replace("_", " ").title()),
        "catalog_id": contract.get("catalog_id"),
        "catalog_version": contract.get("catalog_version"),
        "node_template_id": contract.get("node_template_id"),
        "station_kind": contract.get("station_kind"),
        "schema_version": contract.get("schema_version"),
        "allowed_skill_refs": contract.get("allowed_skill_refs") if isinstance(contract.get("allowed_skill_refs"), list) else [],
        "allowed_connector_refs": contract.get("allowed_connector_refs") if isinstance(contract.get("allowed_connector_refs"), list) else [],
        "allowed_artifact_kinds": contract.get("allowed_artifact_kinds") if isinstance(contract.get("allowed_artifact_kinds"), list) else [],
        "allowed_quality_rules": contract.get("allowed_quality_rules") if isinstance(contract.get("allowed_quality_rules"), list) else [],
        "allowed_approval_policies": contract.get("allowed_approval_policies") if isinstance(contract.get("allowed_approval_policies"), list) else [],
    }


def _patch_diff_dto(diff: dict[str, Any]) -> dict[str, Any]:
    return {
        "workflow_patch_id": diff.get("workflow_patch_id"),
        "workflow_draft_id": diff.get("workflow_draft_id"),
        "base_revision": diff.get("base_revision"),
        "operation": diff.get("operation"),
        "target": diff.get("target") if isinstance(diff.get("target"), dict) else {},
        "before_summary": diff.get("before_summary"),
        "after_summary": diff.get("after_summary"),
        "risk_flags": diff.get("risk_flags") if isinstance(diff.get("risk_flags"), list) else [],
        "requires_approval": bool(diff.get("requires_approval")),
        "redacted": True,
    }


def _patch_proposal_dto(patch: dict[str, Any]) -> dict[str, Any]:
    metadata = patch.get("metadata") if isinstance(patch.get("metadata"), dict) else {}
    return {
        "workflow_patch_id": patch.get("workflow_patch_id"),
        "workflow_template_id": patch.get("workflow_template_id"),
        "workflow_draft_id": patch.get("workflow_draft_id"),
        "operation": patch.get("operation"),
        "status": patch.get("status"),
        "proposed_by": patch.get("proposed_by"),
        "source": metadata.get("source"),
        "intent_type": metadata.get("intent_type"),
        "requires_approval": bool(metadata.get("requires_approval") or patch.get("requires_approval")),
        "risk_flags": metadata.get("risk_flags") if isinstance(metadata.get("risk_flags"), list) else patch.get("risk_flags", []),
    }


def _patch_queue_dto(patches: list[dict[str, Any]], *, current_draft_revision: int | None) -> list[dict[str, Any]]:
    selected_id = _selected_patch_id(patches, current_draft_revision=current_draft_revision)
    return [
        _patch_queue_item_dto(patch, current_draft_revision=current_draft_revision, selected=patch.get("workflow_patch_id") == selected_id)
        for patch in patches
    ]


def _selected_patch_id(patches: list[dict[str, Any]], *, current_draft_revision: int | None) -> str | None:
    queue = [_patch_queue_item_dto(patch, current_draft_revision=current_draft_revision, selected=False) for patch in patches]
    for status in ("proposed", "blocked", "applied", "rejected", "stale", "conflicted"):
        candidate = next((item for item in queue if item["status"] == status), None)
        if candidate:
            return str(candidate["patch_id"])
    return None


def _patch_queue_item_dto(patch: dict[str, Any], *, current_draft_revision: int | None, selected: bool) -> dict[str, Any]:
    proposal = _patch_proposal_dto(patch)
    base_revision = patch.get("base_revision")
    raw_status = str(patch.get("status") or proposal.get("status") or "proposed")
    requires_approval = bool(proposal.get("requires_approval") or patch.get("requires_approval"))
    stale_reason = None
    conflict_reason = None
    status = raw_status if raw_status in PATCH_QUEUE_STATUSES else "proposed"
    if raw_status == "proposed" and current_draft_revision is not None and base_revision != current_draft_revision:
        status = "stale"
        stale_reason = "base_revision_mismatch"
        conflict_reason = f"base_revision {base_revision} does not match current draft revision {current_draft_revision}"
    elif raw_status == "proposed" and requires_approval:
        status = "blocked"
        conflict_reason = "requires_approval"
    return {
        **proposal,
        "patch_id": patch.get("workflow_patch_id"),
        "base_revision": base_revision,
        "current_draft_revision": current_draft_revision,
        "status": status,
        "selected": selected,
        "stale_reason": stale_reason,
        "conflict_reason": conflict_reason,
        "created_at": patch.get("created_at"),
        "updated_at": patch.get("updated_at") or patch.get("applied_at") or patch.get("rejected_at") or patch.get("created_at"),
    }


def _patch_action_dto(result: dict[str, Any]) -> dict[str, Any]:
    patch = result.get("patch") if isinstance(result.get("patch"), dict) else {}
    draft = result.get("draft") if isinstance(result.get("draft"), dict) else {}
    return {
        "workflow_patch_id": patch.get("workflow_patch_id"),
        "workflow_template_id": patch.get("workflow_template_id"),
        "workflow_draft_id": patch.get("workflow_draft_id"),
        "status": patch.get("status"),
        "operation": patch.get("operation"),
        "base_revision": patch.get("base_revision"),
        "applied_revision": patch.get("applied_revision"),
        "resulting_draft_revision": patch.get("resulting_draft_revision") or draft.get("revision"),
        "requires_approval": bool(patch.get("requires_approval")),
        "risk_flags": patch.get("risk_flags") if isinstance(patch.get("risk_flags"), list) else [],
    }


def _canvas_draft_projection_dto(
    *,
    workflow_instance_id: str,
    template_id: str,
    draft: dict[str, Any],
    board: dict[str, Any],
    status: dict[str, Any],
    patches: list[dict[str, Any]],
) -> dict[str, Any]:
    draft_payload = draft.get("draft") if isinstance(draft.get("draft"), dict) else {}
    generated_at = _now_iso()
    patch_queue = _patch_queue_dto(patches, current_draft_revision=draft.get("revision"))
    selected_patch = next((patch for patch in patch_queue if patch.get("selected")), None)
    proposed_patch = next((patch for patch in patches if patch.get("workflow_patch_id") == selected_patch.get("patch_id")), None) if selected_patch else None
    board_status_timestamp = status.get("updated_at") or status.get("timestamp") or generated_at
    freshness_state, stale_reasons = _projection_freshness_state(
        draft_revision=draft.get("revision"),
        selected_patch=selected_patch,
        board_status_timestamp=board_status_timestamp,
        generated_at=generated_at,
    )
    return {
        "projection_id": f"canvas_projection:{workflow_instance_id}:{draft.get('revision')}",
        "workflow_instance_id": workflow_instance_id,
        "workflow_template_id": template_id,
        "workflow_draft_id": draft.get("workflow_draft_id"),
        "draft_revision": draft.get("revision"),
        "generated_at": generated_at,
        "board_status_timestamp": board_status_timestamp,
        "status_updated_at": board_status_timestamp,
        "patch_queue_revision": _patch_queue_revision(patch_queue),
        "freshness_state": freshness_state,
        "stale_reasons": stale_reasons,
        "source_refs": {
            "design_structure": {
                "kind": "WorkflowDraft",
                "workflow_draft_id": draft.get("workflow_draft_id"),
                "workflow_template_id": template_id,
                "draft_revision": draft.get("revision"),
            },
            "runtime_state": {
                "kind": "BoardDTO/InstanceStatusDTO",
                "workflow_instance_id": workflow_instance_id,
                "status": status.get("status"),
                "freshness_marker": board_status_timestamp,
            },
            "pending_diff": {
                "kind": "PatchDiffDTO",
                "workflow_patch_id": proposed_patch.get("workflow_patch_id") if proposed_patch else None,
                "status": proposed_patch.get("status") if proposed_patch else None,
                "patch_queue_revision": _patch_queue_revision(patch_queue),
            },
        },
        "nodes": [
            _canvas_projection_node(station, board)
            for station in draft_payload.get("stations", [])
            if isinstance(station, dict)
        ],
        "edges": [
            _canvas_projection_edge(edge)
            for edge in draft_payload.get("edges", [])
            if isinstance(edge, dict)
        ],
        "runtime_summary": {
            "current_station_ids": status.get("current_station_ids") or [],
            "station_counts": status.get("station_counts") or {},
            "job_counts": status.get("job_counts") or {},
        },
        "patch_queue": patch_queue,
        "pending_patch": selected_patch,
        "redaction_status": "redacted",
    }


def _projection_freshness_state(
    *,
    draft_revision: Any,
    selected_patch: dict[str, Any] | None,
    board_status_timestamp: str,
    generated_at: str,
) -> tuple[str, list[str]]:
    stale_reasons: list[str] = []
    if selected_patch and selected_patch.get("status") == "stale":
        stale_reasons.append("stale_patch")
    if selected_patch and selected_patch.get("base_revision") not in (None, draft_revision):
        stale_reasons.append("stale_draft")
    if board_status_timestamp > generated_at:
        stale_reasons.append("stale_board")
    if "stale_draft" in stale_reasons:
        return "stale_draft", stale_reasons
    if "stale_patch" in stale_reasons:
        return "stale_patch", stale_reasons
    if "stale_board" in stale_reasons:
        return "stale_board", stale_reasons
    if draft_revision is None:
        return "unknown", ["unknown_draft_revision"]
    return "fresh", []


def _patch_queue_revision(patch_queue: list[dict[str, Any]]) -> str:
    if not patch_queue:
        return "patch_queue:empty"
    parts = [
        f"{item.get('patch_id')}:{item.get('status')}:{item.get('updated_at') or ''}:{item.get('base_revision')}:{item.get('current_draft_revision')}"
        for item in patch_queue
    ]
    return "patch_queue:" + "|".join(parts)


def _canvas_projection_node(station: dict[str, Any], board: dict[str, Any]) -> dict[str, Any]:
    station_id = station.get("station_id")
    board_station = next(
        (
            item
            for item in board.get("stations", [])
            if isinstance(item, dict)
            and isinstance(item.get("station"), dict)
            and item["station"].get("station_id") == station_id
        ),
        {},
    )
    metadata = station.get("metadata") if isinstance(station.get("metadata"), dict) else {}
    return {
        "station_id": station_id,
        "name": station.get("name"),
        "role": station.get("role"),
        "station_kind": metadata.get("station_kind"),
        "skill_refs": station.get("skill_refs") if isinstance(station.get("skill_refs"), list) else [],
        "connector_refs": station.get("connector_refs") if isinstance(station.get("connector_refs"), list) else [],
        "status": board_station.get("status"),
        "run_count": len(board_station.get("runs", [])) if isinstance(board_station.get("runs"), list) else 0,
    }


def _canvas_projection_edge(edge: dict[str, Any]) -> dict[str, Any]:
    return {
        "edge_id": edge.get("edge_id"),
        "from_station_id": edge.get("from_station_id"),
        "to_station_id": edge.get("to_station_id"),
        "order": edge.get("order"),
    }


def _agent_session_key(workflow_instance_id: str, scope: ScopeContext) -> str:
    return "|".join(
        [
            scope.app_id or "",
            scope.project_id or "",
            scope.workspace_id or "",
            workflow_instance_id,
        ]
    )


def _now_iso() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def _scope_dto(scope: ScopeContext) -> dict[str, Any]:
    return {
        "app_id": scope.app_id,
        "project_id": scope.project_id,
        "workspace_id": scope.workspace_id,
    }


def _ensure_agent_talk_session(
    workflow_instance_id: str,
    workflow_template_id: str,
    scope: ScopeContext,
    *,
    created_by: str,
) -> dict[str, Any]:
    key = _agent_session_key(workflow_instance_id, scope)
    session = _AGENT_TALK_SESSIONS.get(key)
    if session is not None:
        return session
    session = {
        "agent_session_id": f"ats_{uuid4().hex[:12]}",
        "workflow_instance_id": workflow_instance_id,
        "workflow_template_id": workflow_template_id,
        "scope": _scope_dto(scope),
        "created_by": _redact(created_by),
        "created_at": _now_iso(),
        "updated_at": _now_iso(),
        "redaction_status": "redacted",
    }
    _AGENT_TALK_SESSIONS[key] = session
    _AGENT_TALK_MESSAGES[session["agent_session_id"]] = []
    _AGENT_TALK_SUGGESTIONS[session["agent_session_id"]] = []
    _AGENT_ACTION_PROPOSALS[session["agent_session_id"]] = []
    _record_agent_audit(
        "agent.session.created",
        session=session,
        summary="AgentTalk session created.",
        resource_refs=_agent_resource_refs(workflow_instance_id=workflow_instance_id, workflow_template_id=workflow_template_id),
    )
    return session


def _agent_resource_refs(**refs: Any) -> dict[str, Any]:
    return {key: value for key, value in refs.items() if value is not None}


def _agent_message(
    session: dict[str, Any],
    *,
    role: str,
    content: str,
    source: str,
    resource_refs: dict[str, Any],
) -> dict[str, Any]:
    session["updated_at"] = _now_iso()
    return {
        "message_id": f"atm_{uuid4().hex[:12]}",
        "agent_session_id": session["agent_session_id"],
        "workflow_instance_id": session["workflow_instance_id"],
        "workflow_template_id": session["workflow_template_id"],
        "role": role,
        "source": source,
        "content": _redact(content),
        "resource_refs": _redact(resource_refs),
        "created_at": _now_iso(),
        "redaction_status": "redacted",
    }


def _agent_assistant_reply(content: str) -> str:
    text = content.lower()
    node_template_id = _agent_node_template_for_content(content)
    if node_template_id == "quality_evaluation":
        return "我已生成一个新增质量检查节点的 Patch proposal。该建议只进入 Diff 和编辑面板，应用仍需要用户显式确认。"
    if node_template_id:
        return "我已生成一个新增画布节点的 Patch proposal。该建议只进入 Diff 和编辑面板，应用仍需要用户显式确认。"
    if "优化" in content or "prompt" in text:
        return "我已为当前节点生成 Prompt Patch proposal。该建议只进入 Diff 和编辑面板，应用仍需要用户显式确认。"
    if "连接" in content or "edge" in text:
        return "我可以生成连线 Patch proposal；连线写入仍需要用户在编辑面板显式确认。"
    if "优化" in content or "patch" in text or "diff" in text:
        return "我已基于当前工作流事实源生成可审计建议。建议只会进入 Patch proposal / Diff，应用与发布仍需要用户到编辑面板显式确认。"
    if "解释" in content or "summary" in text:
        return "我会从 board、status、context 和 patch DTO 重新读取事实源，并只给出摘要，不直接修改工作流。"
    return "我可以解释当前流程、总结事件、显示审批提醒、展示上下文摘要，或生成受治理的 Patch 建议。"


def _generate_agent_suggestions(
    gateway: GatewayService,
    workflow_instance_id: str,
    workflow_template_id: str,
    scope: ScopeContext,
    *,
    preferred_patch_id: str | None = None,
) -> list[dict[str, Any]]:
    instance = gateway.workflow_repository.get_instance(workflow_instance_id, scope=scope)
    patches = [
        patch.model_dump(mode="json")
        for patch in gateway.workflow_repository.list_patches(scope=scope, workflow_template_id=workflow_template_id)
        if _patch_matches_instance(patch, workflow_instance_id)
    ]
    patch = (
        next((item for item in patches if item.get("workflow_patch_id") == preferred_patch_id), None)
        if preferred_patch_id
        else None
    )
    patch = patch or next((item for item in patches if item.get("status") == "proposed"), None) or (patches[0] if patches else None)
    station_ids = list(instance.current_station_ids or [])
    target_station_id = station_ids[0] if station_ids else None
    suggestions = [
        _agent_suggestion(
            workflow_instance_id=workflow_instance_id,
            workflow_template_id=workflow_template_id,
            suggestion_type="explain",
            title="解释当前流程",
            summary="基于 workflow.board.get 与 workflow.instance.status 生成运行摘要，不采信事件 payload 作为事实。",
            action="explain_workflow",
        ),
        _agent_suggestion(
            workflow_instance_id=workflow_instance_id,
            workflow_template_id=workflow_template_id,
            suggestion_type="show_context_summary",
            title="展示业务上下文摘要",
            summary="只展示 redacted context.business，不展示 context.system 或 context.runtime。",
            action="show_context_summary",
        ),
    ]
    if patch:
        suggestions.append(
            _agent_suggestion(
                workflow_instance_id=workflow_instance_id,
                workflow_template_id=workflow_template_id,
                suggestion_type="show_diff",
                title="查看 Diff",
                summary="打开已有 Patch Diff；Agent 不会执行 Apply / Publish。",
                action="show_patch_diff",
                workflow_patch_id=patch.get("workflow_patch_id"),
                risk_flags=patch.get("risk_flags") if isinstance(patch.get("risk_flags"), list) else [],
                requires_approval=bool(patch.get("requires_approval")),
            )
        )
    approval = next(
        (
            item
            for item in gateway.approval_store.list_approvals(status="pending")
            if _approval_workflow_binding(item).get("workflow_instance_id") == workflow_instance_id
        ),
        None,
    )
    if approval:
        suggestions.append(
            _agent_suggestion(
                workflow_instance_id=workflow_instance_id,
                workflow_template_id=workflow_template_id,
                suggestion_type="show_approval_notice",
                title="查看待审批事项",
                summary="跳转审批面板，由用户显式确认后才能响应 approval.respond。",
                action="show_approval_notice",
            )
        )
    if target_station_id:
        preferred_operation = str(patch.get("operation") or "") if patch else ""
        if preferred_operation == "add_station":
            preferred_title = "生成节点调整建议"
            preferred_summary = "新增画布节点的 Patch proposal 已生成；后续应用仍必须进入编辑面板由用户确认。"
            preferred_intent_type = "node_add"
        elif preferred_operation == "update_edge":
            preferred_title = "生成连线调整建议"
            preferred_summary = "新增连线的 Patch proposal 已生成；后续应用仍必须进入编辑面板由用户确认。"
            preferred_intent_type = "edge_add"
        elif preferred_operation == "update_station_prompt":
            preferred_title = "生成 Prompt 调整建议"
            preferred_summary = "当前节点 Prompt Patch proposal 已生成；后续应用仍必须进入编辑面板由用户确认。"
            preferred_intent_type = "inspector_update"
        else:
            preferred_title = "生成优化建议"
            preferred_summary = "生成 source=agent 的 Patch proposal payload；后续应用仍必须进入编辑面板由用户确认。"
            preferred_intent_type = "inspector_update"
        suggestions.append(
            _agent_suggestion(
                workflow_instance_id=workflow_instance_id,
                workflow_template_id=workflow_template_id,
                suggestion_type="propose_patch",
                title=preferred_title if preferred_patch_id else "生成优化建议",
                summary=preferred_summary if preferred_patch_id else "生成 source=agent 的 Patch proposal payload；后续应用仍必须进入编辑面板由用户确认。",
                action="suggest_patch",
                workflow_patch_id=preferred_patch_id,
                patch_intent={
                    "source": "agent",
                    "intent_type": preferred_intent_type if preferred_patch_id else "inspector_update",
                    "operation": preferred_operation if preferred_patch_id else "update_station_prompt",
                    "workflow_instance_id": workflow_instance_id,
                    "payload": patch.get("payload") if preferred_patch_id and isinstance(patch.get("payload"), dict) else {
                        "station_id": target_station_id,
                        "prompt_patch": "增强角色一致性、镜头衔接和输出结构约束。",
                    },
                },
            )
        )
    _record_agent_audit(
        "agent.suggestion.generated",
        session={"agent_session_id": "", "workflow_instance_id": workflow_instance_id, "workflow_template_id": workflow_template_id, "scope": _scope_dto(scope)},
        summary="Deterministic Agent suggestions generated.",
        resource_refs=_agent_resource_refs(workflow_instance_id=workflow_instance_id, workflow_template_id=workflow_template_id),
    )
    return suggestions


async def _maybe_create_agent_canvas_patch(
    gateway: GatewayService,
    workflow_instance_id: str,
    workflow_template_id: str,
    scope: ScopeContext,
    content: str,
    body: dict[str, Any],
) -> str | None:
    template = gateway.workflow_repository.get_template(workflow_template_id, scope=scope)
    draft = gateway.workflow_repository.get_draft(str(template.latest_draft_id), scope=scope)
    draft_payload = draft.draft if isinstance(draft.draft, dict) else {}
    patch = _agent_canvas_patch_for_content(workflow_instance_id, content, body, draft_payload)
    if patch is None:
        return None
    _validate_canvas_patch_payload(gateway, workflow_template_id, patch, scope)
    result = await _rpc(
        gateway,
        "workflow.patch.propose",
        {
            "workflow_template_id": workflow_template_id,
            "patch": patch,
            "scope": _scope_dto(scope),
        },
    )
    patch_result = result.get("patch") if isinstance(result, dict) else {}
    if isinstance(patch_result, dict):
        return str(patch_result.get("workflow_patch_id") or "") or None
    return None


def _agent_canvas_patch_for_content(
    workflow_instance_id: str,
    content: str,
    body: dict[str, Any],
    draft_payload: dict[str, Any],
) -> dict[str, Any] | None:
    node_template_id = _agent_node_template_for_content(content)
    if node_template_id:
        station_id = _unique_agent_station_id(f"station_agent_{node_template_id}", draft_payload)
        return {
            "operation": "add_station",
            "payload": _agent_node_payload(node_template_id, station_id=station_id),
            "actor_type": "agent",
            "actor_id": "agent_proposal",
            "proposed_by": "agent_proposal",
            "metadata": {
                "source": "agent",
                "intent_type": "node_add",
                "workflow_instance_id": workflow_instance_id,
            },
        }
    if _is_agent_prompt_update_request(content):
        station_id = _selected_or_first_station_id(body, draft_payload)
        if not station_id:
            return None
        return {
            "operation": "update_station_prompt",
            "payload": {
                "station_id": station_id,
                "prompt_patch": _agent_prompt_patch(content),
            },
            "actor_type": "agent",
            "actor_id": "agent_proposal",
            "proposed_by": "agent_proposal",
            "metadata": {
                "source": "agent",
                "intent_type": "inspector_update",
                "workflow_instance_id": workflow_instance_id,
            },
        }
    edge_pair = _agent_edge_pair_for_content(content, body, draft_payload)
    if edge_pair:
        from_station_id, to_station_id = edge_pair
        return {
            "operation": "update_edge",
            "payload": {
                "edge_id": f"edge_{from_station_id}_to_{to_station_id}",
                "edge_patch": {
                    "action": "add",
                    "from_station_id": from_station_id,
                    "to_station_id": to_station_id,
                },
            },
            "actor_type": "agent",
            "actor_id": "agent_proposal",
            "proposed_by": "agent_proposal",
            "metadata": {
                "source": "agent",
                "intent_type": "edge_add",
                "workflow_instance_id": workflow_instance_id,
            },
        }
    return None


def _agent_node_template_for_content(content: str) -> str | None:
    if not any(token in content for token in ("增加", "新增", "添加", "加一个")):
        return None
    if "审批" in content:
        return "manual_approval"
    if "角色" in content or "一致性" in content:
        return "character_consistency"
    if "质量" in content or "检查" in content or "评估" in content:
        return "quality_evaluation"
    return None


def _is_agent_prompt_update_request(content: str) -> bool:
    lowered = content.lower()
    return ("优化" in content or "修改" in content or "调整" in content) and ("prompt" in lowered or "提示词" in content or "节点" in content)


def _agent_prompt_patch(content: str) -> str:
    if "角色" in content or "一致性" in content:
        return "增强角色一致性、镜头衔接和输出结构约束。"
    if "质量" in content:
        return "补充质量检查标准，明确输出可验收条件和失败原因。"
    return "根据用户自然语言要求优化当前节点 Prompt，并保持输出结构可审计。"


def _selected_or_first_station_id(body: dict[str, Any], draft_payload: dict[str, Any]) -> str:
    station_ids = [str(item.get("station_id")) for item in draft_payload.get("stations", []) if isinstance(item, dict) and item.get("station_id")]
    selected = body.get("selected_station_id")
    if isinstance(selected, str) and selected in station_ids:
        return selected
    return station_ids[0] if station_ids else ""


def _agent_edge_pair_for_content(content: str, body: dict[str, Any], draft_payload: dict[str, Any]) -> tuple[str, str] | None:
    if "连接" not in content and "edge" not in content.lower():
        return None
    station_ids = [str(item.get("station_id")) for item in draft_payload.get("stations", []) if isinstance(item, dict) and item.get("station_id")]
    selected = body.get("selected_station_id")
    target = body.get("target_station_id")
    if isinstance(selected, str) and isinstance(target, str) and selected in station_ids and target in station_ids and selected != target:
        return selected, target
    if len(station_ids) >= 2:
        return station_ids[-2], station_ids[-1]
    return None


def _unique_agent_station_id(base_id: str, draft_payload: dict[str, Any]) -> str:
    existing_ids = {item.get("station_id") for item in draft_payload.get("stations", []) if isinstance(item, dict)}
    if base_id not in existing_ids:
        return base_id
    index = 2
    while f"{base_id}_{index}" in existing_ids:
        index += 1
    return f"{base_id}_{index}"


def _agent_node_payload(node_template_id: str, *, station_id: str) -> dict[str, Any]:
    contract = NODE_CATALOG_CONTRACTS[node_template_id]
    node_label = "质量检查节点" if node_template_id == "quality_evaluation" else NODE_CATALOG_LABELS.get(node_template_id, node_template_id)
    return {
        "station": {
            "station_id": station_id,
            "name": node_label,
            "role": contract["station_kind"],
            "skill_refs": list(contract["allowed_skill_refs"]),
            "connector_refs": list(contract["allowed_connector_refs"]),
            "metadata": {
                "node_catalog_id": node_template_id,
                "node_label": node_label,
                **contract,
            },
        }
    }


async def _maybe_create_agent_node_add_patch(
    gateway: GatewayService,
    workflow_instance_id: str,
    workflow_template_id: str,
    scope: ScopeContext,
    content: str,
) -> str | None:
    if not _is_agent_node_add_request(content):
        return None
    template = gateway.workflow_repository.get_template(workflow_template_id, scope=scope)
    draft = gateway.workflow_repository.get_draft(str(template.latest_draft_id), scope=scope)
    draft_payload = draft.draft if isinstance(draft.draft, dict) else {}
    station_id = _unique_agent_station_id("station_agent_quality_check", draft_payload)
    patch = {
        "operation": "add_station",
        "payload": _agent_quality_node_payload(station_id=station_id),
        "actor_type": "agent",
        "actor_id": "agent_proposal",
        "proposed_by": "agent_proposal",
        "metadata": {
            "source": "agent",
            "intent_type": "node_add",
            "workflow_instance_id": workflow_instance_id,
        },
    }
    _validate_canvas_patch_payload(gateway, workflow_template_id, patch, scope)
    result = await _rpc(
        gateway,
        "workflow.patch.propose",
        {
            "workflow_template_id": workflow_template_id,
            "patch": patch,
            "scope": _scope_dto(scope),
        },
    )
    patch_result = result.get("patch") if isinstance(result, dict) else {}
    if isinstance(patch_result, dict):
        return str(patch_result.get("workflow_patch_id") or "") or None
    return None


def _is_agent_node_add_request(content: str) -> bool:
    return (
        any(token in content for token in ("增加", "新增", "添加"))
        and any(token in content for token in ("质量", "检查", "评估"))
        and any(token in content for token in ("节点", "node"))
    )


def _agent_quality_node_payload(*, station_id: str = "station_agent_quality_check") -> dict[str, Any]:
    contract = NODE_CATALOG_CONTRACTS["quality_evaluation"]
    return {
        "station": {
            "station_id": station_id,
            "name": "质量检查节点",
            "role": contract["station_kind"],
            "skill_refs": ["video.quality"],
            "connector_refs": [],
            "metadata": {
                "node_catalog_id": "quality_evaluation",
                **contract,
            },
        }
    }


def _agent_suggestion(
    *,
    workflow_instance_id: str,
    workflow_template_id: str,
    suggestion_type: str,
    title: str,
    summary: str,
    action: str,
    workflow_patch_id: Any = None,
    risk_flags: list[Any] | None = None,
    requires_approval: bool = False,
    patch_intent: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if action not in AGENT_ACTION_INTENTS:
        raise ProtocolError("WORKFLOW_ACTION_FORBIDDEN", "Agent action intent is not allowed.", {"action": action})
    if patch_intent is not None:
        _reject_sensitive_or_layout_fields(patch_intent)
    return {
        "suggestion_id": f"ags_{uuid4().hex[:12]}",
        "workflow_instance_id": workflow_instance_id,
        "workflow_template_id": workflow_template_id,
        "workflow_patch_id": workflow_patch_id,
        "type": suggestion_type,
        "title": _redact(title),
        "summary": _redact(summary),
        "status": "active",
        "action_intent": {
            "action": action,
            "executable": False,
        },
        "patch_intent": _redact(patch_intent) if patch_intent else None,
        "risk_flags": risk_flags or [],
        "requires_approval": requires_approval,
        "created_at": _now_iso(),
        "redaction_status": "redacted",
    }


def _agent_session_dto(session: dict[str, Any]) -> dict[str, Any]:
    messages = _AGENT_TALK_MESSAGES.get(str(session.get("agent_session_id")), [])
    suggestions = _AGENT_TALK_SUGGESTIONS.get(str(session.get("agent_session_id")), [])
    return {
        "agent_session_id": session.get("agent_session_id"),
        "workflow_instance_id": session.get("workflow_instance_id"),
        "workflow_template_id": session.get("workflow_template_id"),
        "scope": session.get("scope"),
        "created_by": session.get("created_by"),
        "created_at": session.get("created_at"),
        "updated_at": session.get("updated_at"),
        "redaction_status": "redacted",
        "messages": [_agent_message_dto(item) for item in messages],
        "suggestions": [_agent_suggestion_dto(item) for item in suggestions],
    }


def _agent_message_dto(message: dict[str, Any]) -> dict[str, Any]:
    return {
        "message_id": message.get("message_id"),
        "agent_session_id": message.get("agent_session_id"),
        "workflow_instance_id": message.get("workflow_instance_id"),
        "workflow_template_id": message.get("workflow_template_id"),
        "role": message.get("role"),
        "source": message.get("source"),
        "content": _redact(message.get("content")),
        "resource_refs": _redact(message.get("resource_refs") if isinstance(message.get("resource_refs"), dict) else {}),
        "created_at": message.get("created_at"),
        "redaction_status": "redacted",
    }


def _agent_suggestion_dto(suggestion: dict[str, Any]) -> dict[str, Any]:
    return {
        "suggestion_id": suggestion.get("suggestion_id"),
        "workflow_instance_id": suggestion.get("workflow_instance_id"),
        "workflow_template_id": suggestion.get("workflow_template_id"),
        "workflow_patch_id": suggestion.get("workflow_patch_id"),
        "type": suggestion.get("type"),
        "title": _redact(suggestion.get("title")),
        "summary": _redact(suggestion.get("summary")),
        "status": suggestion.get("status"),
        "action_intent": _redact(suggestion.get("action_intent") if isinstance(suggestion.get("action_intent"), dict) else {}),
        "patch_intent": _redact(suggestion.get("patch_intent") if isinstance(suggestion.get("patch_intent"), dict) else None),
        "risk_flags": suggestion.get("risk_flags") if isinstance(suggestion.get("risk_flags"), list) else [],
        "requires_approval": bool(suggestion.get("requires_approval")),
        "created_at": suggestion.get("created_at"),
        "redaction_status": "redacted",
    }


def _ensure_agent_action_proposals(session: dict[str, Any], suggestions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    proposals = _AGENT_ACTION_PROPOSALS.setdefault(str(session["agent_session_id"]), [])
    if proposals:
        return proposals
    for suggestion in suggestions:
        action_intent = suggestion.get("action_intent") if isinstance(suggestion.get("action_intent"), dict) else {}
        action = str(action_intent.get("action") or "")
        if not action:
            continue
        proposals.append(
            _agent_action_proposal(
                session=session,
                intent_type=action,
                title=str(suggestion.get("title") or "Agent proposal"),
                summary=str(suggestion.get("summary") or "Agent action proposal."),
                source_suggestion_id=str(suggestion.get("suggestion_id") or ""),
                workflow_patch_id=suggestion.get("workflow_patch_id"),
                risk_flags=suggestion.get("risk_flags") if isinstance(suggestion.get("risk_flags"), list) else [],
                requires_approval=bool(suggestion.get("requires_approval")),
            )
        )
    return proposals


def _agent_action_proposal_from_request(session: dict[str, Any], body: dict[str, Any]) -> dict[str, Any]:
    intent_type = str(body.get("intent_type") or body.get("action") or "")
    if not intent_type:
        raise ProtocolError("INVALID_PARAMS", "intent_type is required.", {"field": "intent_type"})
    payload = body.get("payload") if isinstance(body.get("payload"), dict) else {}
    _reject_sensitive_or_layout_fields(payload)
    return _agent_action_proposal(
        session=session,
        intent_type=intent_type,
        title=str(body.get("title") or intent_type),
        summary=str(body.get("summary") or "Agent action proposal."),
        payload=payload,
        target_panel=body.get("target_panel"),
        risk_flags=body.get("risk_flags") if isinstance(body.get("risk_flags"), list) else [],
        requires_approval=bool(body.get("requires_approval")),
    )


def _agent_action_proposal(
    *,
    session: dict[str, Any],
    intent_type: str,
    title: str,
    summary: str,
    source_suggestion_id: str | None = None,
    workflow_patch_id: Any = None,
    payload: dict[str, Any] | None = None,
    target_panel: Any = None,
    risk_flags: list[Any] | None = None,
    requires_approval: bool = False,
) -> dict[str, Any]:
    policy = _agent_action_policy(intent_type)
    resource_refs = _agent_resource_refs(
        workflow_instance_id=session.get("workflow_instance_id"),
        workflow_template_id=session.get("workflow_template_id"),
        source_suggestion_id=source_suggestion_id,
        workflow_patch_id=workflow_patch_id,
    )
    lifecycle = "blocked" if policy == "forbidden" else "proposed"
    return {
        "proposal_id": f"aap_{uuid4().hex[:12]}",
        "agent_session_id": session.get("agent_session_id"),
        "workflow_instance_id": session.get("workflow_instance_id"),
        "workflow_template_id": session.get("workflow_template_id"),
        "intent_type": intent_type,
        "policy_class": policy,
        "lifecycle": lifecycle,
        "status": lifecycle,
        "title": _redact(title),
        "summary": _redact(summary),
        "target_panel": _normalize_agent_target_panel(target_panel, intent_type),
        "workflow_patch_id": workflow_patch_id,
        "risk_level": _agent_risk_level(risk_flags or [], requires_approval, policy),
        "risk_flags": risk_flags or [],
        "requires_approval": requires_approval,
        "policy_decision": "blocked" if policy == "forbidden" else "proposal_only",
        "payload_summary": _redact(payload or {}),
        "resource_refs": _redact(resource_refs),
        "created_by": "agent",
        "created_at": _now_iso(),
        "updated_at": _now_iso(),
        "redaction_status": "redacted",
    }


def _agent_action_policy(intent_type: str) -> str:
    if intent_type in FORBIDDEN_AGENT_ACTION_INTENTS:
        raise ProtocolError("WORKFLOW_ACTION_FORBIDDEN", "Agent action intent is forbidden.", {"intent_type": intent_type})
    policy = AGENT_ACTION_POLICY.get(intent_type)
    if policy is None:
        raise ProtocolError("WORKFLOW_ACTION_FORBIDDEN", "Agent action intent is not allowed.", {"intent_type": intent_type})
    return policy


def _normalize_agent_target_panel(target_panel: Any, intent_type: str) -> str | None:
    allowed = {"editing", "approval", "context", "quality", "artifact", "events"}
    if isinstance(target_panel, str) and target_panel in allowed:
        return target_panel
    defaults = {
        "show_patch_diff": "editing",
        "suggest_patch": "editing",
        "propose_patch": "editing",
        "navigate_to_editing_panel": "editing",
        "open_editing_panel": "editing",
        "show_approval_notice": "approval",
        "open_approval_panel": "approval",
        "show_context_summary": "context",
        "open_context_panel": "context",
        "summarize_context": "context",
        "open_quality_panel": "quality",
        "summarize_quality": "quality",
        "open_artifact_panel": "artifact",
    }
    return defaults.get(intent_type)


def _agent_risk_level(risk_flags: list[Any], requires_approval: bool, policy: str) -> str:
    if policy == "forbidden" or requires_approval:
        return "high"
    if risk_flags:
        return "medium"
    return "low"


def _find_agent_action_proposal(agent_session_id: str, proposal_id: str) -> dict[str, Any]:
    proposals = _AGENT_ACTION_PROPOSALS.get(agent_session_id, [])
    proposal = next((item for item in proposals if item.get("proposal_id") == proposal_id), None)
    if proposal is None:
        raise ProtocolError("METHOD_NOT_FOUND", "Agent action proposal was not found.", {"proposal_id": proposal_id})
    return proposal


def _agent_action_proposal_dto(proposal: dict[str, Any]) -> dict[str, Any]:
    return {
        "proposal_id": proposal.get("proposal_id"),
        "agent_session_id": proposal.get("agent_session_id"),
        "workflow_instance_id": proposal.get("workflow_instance_id"),
        "workflow_template_id": proposal.get("workflow_template_id"),
        "intent_type": proposal.get("intent_type"),
        "policy_class": proposal.get("policy_class"),
        "lifecycle": proposal.get("lifecycle"),
        "status": proposal.get("status"),
        "title": _redact(proposal.get("title")),
        "summary": _redact(proposal.get("summary")),
        "target_panel": proposal.get("target_panel"),
        "workflow_patch_id": proposal.get("workflow_patch_id"),
        "risk_level": proposal.get("risk_level"),
        "risk_flags": proposal.get("risk_flags") if isinstance(proposal.get("risk_flags"), list) else [],
        "requires_approval": bool(proposal.get("requires_approval")),
        "policy_decision": proposal.get("policy_decision"),
        "payload_summary": _redact(proposal.get("payload_summary") if isinstance(proposal.get("payload_summary"), dict) else {}),
        "resource_refs": _redact(proposal.get("resource_refs") if isinstance(proposal.get("resource_refs"), dict) else {}),
        "created_by": proposal.get("created_by"),
        "created_at": proposal.get("created_at"),
        "updated_at": proposal.get("updated_at"),
        "redaction_status": "redacted",
    }


def _normalize_handoff_target_panel(target_panel: Any) -> str:
    aliases = {
        "editing": "editing_panel",
        "approval": "approval_panel",
        "context": "context_panel",
        "quality": "quality_panel",
        "artifact": "artifact_panel",
    }
    normalized = aliases.get(str(target_panel), str(target_panel))
    if normalized not in AGENT_HANDOFF_TARGET_PANELS:
        raise ProtocolError("WORKFLOW_ACTION_FORBIDDEN", "Agent handoff target panel is not allowed.", {"target_panel": target_panel})
    return normalized


def _proposal_panel(proposal: dict[str, Any]) -> str:
    return _normalize_handoff_target_panel(proposal.get("target_panel"))


def _ensure_proposal_can_handoff(proposal: dict[str, Any], target_panel: str) -> None:
    lifecycle = str(proposal.get("lifecycle") or proposal.get("status") or "")
    if lifecycle in {"dismissed", "blocked", "expired"}:
        raise ProtocolError("WORKFLOW_ACTION_FORBIDDEN", "Agent action proposal is not active.", {"proposal_id": proposal.get("proposal_id"), "status": lifecycle})
    if str(proposal.get("policy_class")) == "forbidden":
        raise ProtocolError("WORKFLOW_ACTION_FORBIDDEN", "Forbidden proposal cannot be handed off.", {"proposal_id": proposal.get("proposal_id")})
    if str(proposal.get("intent_type")) in READ_ONLY_AGENT_ACTION_INTENTS:
        raise ProtocolError("WORKFLOW_ACTION_FORBIDDEN", "Read-only Agent proposal cannot be handed off.", {"proposal_id": proposal.get("proposal_id")})
    if _proposal_panel(proposal) != target_panel:
        raise ProtocolError(
            "WORKFLOW_ACTION_FORBIDDEN",
            "Agent handoff target panel does not match proposal target.",
            {"proposal_id": proposal.get("proposal_id"), "target_panel": target_panel},
        )


def _agent_action_handoff(
    gateway: GatewayService,
    scope: ScopeContext,
    session: dict[str, Any],
    proposal: dict[str, Any],
    target_panel: str,
    body: dict[str, Any],
) -> dict[str, Any]:
    now = datetime.now(UTC)
    target_resource = _handoff_target_resource(gateway, scope, session, proposal, target_panel, body)
    prefill = body.get("suggested_form_prefill") if isinstance(body.get("suggested_form_prefill"), dict) else {}
    return {
        "handoff_id": f"aah_{uuid4().hex[:12]}",
        "agent_session_id": session.get("agent_session_id"),
        "proposal_id": proposal.get("proposal_id"),
        "workflow_instance_id": session.get("workflow_instance_id"),
        "workflow_template_id": session.get("workflow_template_id"),
        "target_panel": target_panel,
        "target_resource": _redact(target_resource),
        "suggested_form_prefill": _redact(prefill),
        "expires_at": (now + timedelta(minutes=AGENT_HANDOFF_TTL_MINUTES)).isoformat(),
        "status": "active",
        "created_at": now.isoformat(),
        "created_by": "agent",
        "redaction_status": "redacted",
    }


def _handoff_target_resource(
    gateway: GatewayService,
    scope: ScopeContext,
    session: dict[str, Any],
    proposal: dict[str, Any],
    target_panel: str,
    body: dict[str, Any],
) -> dict[str, Any]:
    workflow_instance_id = str(session.get("workflow_instance_id") or "")
    if target_panel == "editing_panel":
        workflow_patch_id = str(body.get("workflow_patch_id") or proposal.get("workflow_patch_id") or "")
        if not workflow_patch_id:
            raise ProtocolError("INVALID_PARAMS", "editing handoff requires workflow_patch_id.", {"field": "workflow_patch_id"})
        _ensure_patch_in_instance(gateway, workflow_patch_id, workflow_instance_id, scope)
        patch = gateway.workflow_repository.get_patch(workflow_patch_id, scope=scope)
        draft = gateway.workflow_repository.get_draft(patch.workflow_draft_id, scope=scope)
        return {
            "workflow_patch_id": workflow_patch_id,
            "patch_id": workflow_patch_id,
            "patch_status": patch.status,
            "draft_revision": draft.revision,
            "base_revision": patch.base_revision,
            "requires_approval": bool(proposal.get("requires_approval")),
            "risk_flags": proposal.get("risk_flags") if isinstance(proposal.get("risk_flags"), list) else [],
        }
    if target_panel == "approval_panel":
        approval_id = str(body.get("approval_id") or body.get("target_resource_id") or "")
        if not approval_id:
            approval_id = _first_workflow_bound_approval_id(gateway, workflow_instance_id)
        approval = gateway.approval_store.get_approval(approval_id)
        _ensure_approval_in_instance(approval, workflow_instance_id)
        binding = _approval_workflow_binding(approval)
        return {
            "approval_id": approval_id,
            "approval_status": approval.get("status"),
            "workflow_instance_id": workflow_instance_id,
            "station_run_id": binding.get("station_run_id"),
        }
    if target_panel == "context_panel":
        context = gateway.workflow_repository.get_or_create_context(workflow_instance_id, scope=scope)
        path = str(body.get("target_path") or body.get("path") or "business.operator_note")
        if not path.startswith("business.") or path == "business.":
            raise ProtocolError("WORKFLOW_CONTEXT_SCOPE_MISMATCH", "Context handoff target path must start with business.", {"path": path})
        return {
            "expected_revision": context.revision,
            "target_path": path,
            "workflow_instance_id": workflow_instance_id,
        }
    return {"workflow_instance_id": workflow_instance_id}


def _first_workflow_bound_approval_id(gateway: GatewayService, workflow_instance_id: str) -> str:
    for approval in gateway.approval_store.list_approvals(status="pending"):
        if _approval_workflow_binding(approval).get("workflow_instance_id") == workflow_instance_id:
            return str(approval.get("approval_id"))
    raise ProtocolError("APPROVAL_NOT_FOUND", "No workflow-bound approval found for handoff.", {"workflow_instance_id": workflow_instance_id})


def _find_agent_action_handoff(agent_session_id: str, handoff_id: str) -> dict[str, Any]:
    handoff = _AGENT_HANDOFF_REPOSITORY.get(handoff_id)
    if handoff.get("agent_session_id") != agent_session_id:
        raise ProtocolError("METHOD_NOT_FOUND", "Agent action handoff was not found.", {"handoff_id": handoff_id})
    return handoff


def _agent_action_handoff_dto(handoff: dict[str, Any]) -> dict[str, Any]:
    return {
        "handoff_id": handoff.get("handoff_id"),
        "proposal_id": handoff.get("proposal_id"),
        "workflow_instance_id": handoff.get("workflow_instance_id"),
        "workflow_template_id": handoff.get("workflow_template_id"),
        "target_panel": handoff.get("target_panel"),
        "target_resource": _redact(handoff.get("target_resource") if isinstance(handoff.get("target_resource"), dict) else {}),
        "suggested_form_prefill": _redact(handoff.get("suggested_form_prefill") if isinstance(handoff.get("suggested_form_prefill"), dict) else {}),
        "expires_at": handoff.get("expires_at"),
        "status": handoff.get("status"),
        "inactive_reason": _redact(handoff.get("inactive_reason")),
        "updated_at": handoff.get("updated_at"),
        "created_at": handoff.get("created_at"),
        "created_by": handoff.get("created_by"),
        "redaction_status": "redacted",
    }


def _refresh_handoff_for_read(gateway: GatewayService, scope: ScopeContext, handoff: dict[str, Any]) -> dict[str, Any]:
    handoff = _expire_handoff_if_needed(handoff)
    if handoff.get("status") not in HANDOFF_ACTIVE_STATES:
        return handoff
    return _mark_handoff_stale_or_blocked_if_needed(gateway, scope, handoff)


def _expire_handoff_if_needed(handoff: dict[str, Any]) -> dict[str, Any]:
    if handoff.get("status") not in HANDOFF_ACTIVE_STATES:
        return handoff
    expires_at = handoff.get("expires_at")
    try:
        expires = datetime.fromisoformat(str(expires_at))
    except ValueError as exc:
        raise ProtocolError("WORKFLOW_ACTION_FORBIDDEN", "Agent action handoff expiration is invalid.", {"handoff_id": handoff.get("handoff_id")}) from exc
    if expires < datetime.now(UTC):
        expired = _AGENT_HANDOFF_REPOSITORY.expire(str(handoff.get("handoff_id")), reason="handoff_expired")
        _append_handoff_audit(str(handoff.get("handoff_id")), "handoff_expired", summary="Agent action handoff expired.", data={"reason": "handoff_expired"})
        return expired
    return handoff


def _mark_handoff_stale_or_blocked_if_needed(gateway: GatewayService, scope: ScopeContext, handoff: dict[str, Any]) -> dict[str, Any]:
    target_panel = str(handoff.get("target_panel") or "")
    resource = handoff.get("target_resource") if isinstance(handoff.get("target_resource"), dict) else {}
    handoff_id = str(handoff.get("handoff_id") or "")
    try:
        if target_panel == "editing_panel":
            workflow_patch_id = str(resource.get("workflow_patch_id") or resource.get("patch_id") or "")
            patch = gateway.workflow_repository.get_patch(workflow_patch_id, scope=scope)
            patch_status = _enum_text(patch.status)
            if patch_status != "proposed":
                return _mark_handoff_stale(handoff_id, f"patch_status_{patch_status}")
            draft = gateway.workflow_repository.get_draft(patch.workflow_draft_id, scope=scope)
            if int(resource.get("draft_revision") or -1) != draft.revision:
                return _mark_handoff_stale(handoff_id, "draft_revision_changed")
            if bool(resource.get("requires_approval")):
                return _mark_handoff_blocked(handoff_id, "patch_requires_approval")
            return handoff
        if target_panel == "approval_panel":
            approval_id = str(resource.get("approval_id") or "")
            approval = gateway.approval_store.get_approval(approval_id)
            binding = _approval_workflow_binding(approval)
            if approval.get("status") != "pending":
                return _mark_handoff_stale(handoff_id, f"approval_status_{approval.get('status')}")
            if binding.get("active") is False:
                return _mark_handoff_stale(handoff_id, "approval_workflow_binding_inactive")
            instance = gateway.workflow_repository.get_instance(str(handoff.get("workflow_instance_id")), scope=scope)
            if instance.status in {"completed", "failed", "cancelled"}:
                return _mark_handoff_stale(handoff_id, f"workflow_instance_{instance.status}")
            return handoff
        if target_panel == "context_panel":
            path = str(resource.get("target_path") or "")
            if not path.startswith("business.") or path == "business.":
                return _mark_handoff_stale(handoff_id, "context_target_path_invalid")
            context = gateway.workflow_repository.get_or_create_context(str(handoff.get("workflow_instance_id")), scope=scope)
            if int(resource.get("expected_revision") or -1) != context.revision:
                return _mark_handoff_stale(handoff_id, "context_revision_changed")
            return handoff
    except ProtocolError:
        raise
    except Exception as exc:
        return _mark_handoff_stale(handoff_id, type(exc).__name__)
    return handoff


def _mark_handoff_stale(handoff_id: str, reason: str) -> dict[str, Any]:
    stale = _AGENT_HANDOFF_REPOSITORY.mark_stale(handoff_id, reason=reason)
    _append_handoff_audit(handoff_id, "handoff_stale", summary="Agent action handoff became stale.", data={"reason": reason})
    return stale


def _mark_handoff_blocked(handoff_id: str, reason: str) -> dict[str, Any]:
    blocked = _AGENT_HANDOFF_REPOSITORY.mark_blocked(handoff_id, reason=reason)
    _append_handoff_audit(handoff_id, "handoff_blocked", summary="Agent action handoff was blocked.", data={"reason": reason})
    return blocked


def _enum_text(value: Any) -> str:
    return str(getattr(value, "value", value))


def _ensure_handoff_usable(gateway: GatewayService, scope: ScopeContext, handoff: dict[str, Any]) -> dict[str, Any]:
    refreshed = _refresh_handoff_for_read(gateway, scope, handoff)
    if refreshed.get("status") not in HANDOFF_ACTIVE_STATES:
        raise ProtocolError(
            "WORKFLOW_ACTION_FORBIDDEN",
            "Agent action handoff is not usable.",
            {"handoff_id": refreshed.get("handoff_id"), "status": refreshed.get("status"), "reason": refreshed.get("inactive_reason")},
        )
    return refreshed


def _require_agent_handoff_for_action(
    body: dict[str, Any],
    *,
    target_panel: str,
    gateway: GatewayService | None = None,
    scope: ScopeContext | None = None,
    auth: Any = None,
    workflow_instance_id: Any = None,
    target_resource_id: Any = None,
) -> None:
    if body.get("source") == "agent":
        raise ProtocolError("WORKFLOW_ACTION_FORBIDDEN", "Agent cannot execute user-confirmed actions.", {"source": "agent"})
    proposal_id = str(body.get("proposal_id") or "")
    handoff_id = str(body.get("handoff_id") or "")
    if not proposal_id or not handoff_id:
        if not proposal_id and not handoff_id:
            return
        raise ProtocolError("WORKFLOW_ACTION_FORBIDDEN", "User-confirmed operation requires proposal_id and handoff_id.", {"proposal_id": bool(proposal_id), "handoff_id": bool(handoff_id)})
    if auth is not None and not _auth_has_capability(auth, "agent_handoffs.write"):
        raise ProtocolError("CAPABILITY_DENIED", "Agent handoff usage requires agent_handoffs.write capability.", {"capability": "agent_handoffs.write"})
    handoff = _find_handoff_by_id(handoff_id)
    if gateway is not None and scope is not None:
        handoff = _ensure_handoff_usable(gateway, scope, handoff)
    elif handoff.get("status") not in HANDOFF_ACTIVE_STATES:
        raise ProtocolError("WORKFLOW_ACTION_FORBIDDEN", "Agent action handoff is not usable.", {"handoff_id": handoff_id, "status": handoff.get("status")})
    if handoff.get("proposal_id") != proposal_id:
        raise ProtocolError("WORKFLOW_ACTION_FORBIDDEN", "Agent handoff does not belong to proposal.", {"proposal_id": proposal_id, "handoff_id": handoff_id})
    if handoff.get("target_panel") != target_panel:
        raise ProtocolError("WORKFLOW_ACTION_FORBIDDEN", "Agent handoff target panel mismatch.", {"target_panel": target_panel, "handoff_id": handoff_id})
    if workflow_instance_id and handoff.get("workflow_instance_id") != workflow_instance_id:
        raise ProtocolError("SCOPE_MISMATCH", "Agent handoff does not belong to workflow instance.", {"resource": "handoff_id"})
    resource = handoff.get("target_resource") if isinstance(handoff.get("target_resource"), dict) else {}
    if target_resource_id:
        allowed_ids = {str(value) for key, value in resource.items() if key.endswith("_id") or key == "patch_id"}
        if str(target_resource_id) not in allowed_ids:
            raise ProtocolError("SCOPE_MISMATCH", "Agent handoff does not target selected resource.", {"resource": "handoff_id"})
    _AGENT_HANDOFF_REPOSITORY.mark_used(handoff_id)
    _append_handoff_audit(handoff_id, "handoff_used_for_user_confirmed_action", summary="Agent action handoff used for user-confirmed action.", data={"target_panel": target_panel})


def _find_handoff_by_id(handoff_id: str) -> dict[str, Any]:
    return _AGENT_HANDOFF_REPOSITORY.get(handoff_id)


def _reject_forbidden_agent_actions(action_intent: Any) -> None:
    if action_intent is None:
        return
    if not isinstance(action_intent, dict):
        raise ProtocolError("WORKFLOW_ACTION_FORBIDDEN", "Agent action intent must be an object.", {"field": "action_intent"})
    action = str(action_intent.get("action") or "")
    if action in FORBIDDEN_AGENT_ACTION_INTENTS or action not in AGENT_ACTION_INTENTS:
        raise ProtocolError("WORKFLOW_ACTION_FORBIDDEN", "Agent action intent is not executable in this phase.", {"action": action or None})


def _record_agent_audit(
    event_type: str,
    *,
    session: dict[str, Any],
    summary: str,
    resource_refs: dict[str, Any],
) -> None:
    _AGENT_TALK_AUDIT.append(
        _redact(
            {
                "event_type": event_type,
                "agent_session_id": session.get("agent_session_id"),
                "workflow_instance_id": session.get("workflow_instance_id"),
                "workflow_template_id": session.get("workflow_template_id"),
                "scope": session.get("scope"),
                "summary": summary,
                "resource_refs": resource_refs,
                "created_at": _now_iso(),
                "redaction_status": "redacted",
            }
        )
    )


def _append_handoff_audit(handoff_id: str, event_type: str, *, summary: str, data: dict[str, Any] | None = None) -> None:
    _AGENT_HANDOFF_REPOSITORY.append_audit(handoff_id, event_type, summary=summary, data=_redact(data or {}))


def _publish_dto(result: dict[str, Any]) -> dict[str, Any]:
    template = result.get("template") if isinstance(result.get("template"), dict) else {}
    draft = result.get("draft") if isinstance(result.get("draft"), dict) else {}
    version = result.get("version") if isinstance(result.get("version"), dict) else {}
    return {
        "workflow_template_id": template.get("workflow_template_id"),
        "workflow_draft_id": draft.get("workflow_draft_id"),
        "draft_status": draft.get("status"),
        "draft_revision": draft.get("revision"),
        "workflow_version_id": version.get("workflow_version_id"),
        "version": version.get("version"),
    }


def _operation_result(
    operation: str,
    *,
    status: str,
    resource: Any,
    trace_id: Any = None,
    idempotent: bool = False,
    workflow_side_effect: Any = None,
    evidence: Any = None,
) -> dict[str, Any]:
    result = {
        "operation": operation,
        "status": status,
        "resource": resource,
        "idempotent": idempotent,
    }
    if trace_id:
        result["trace_id"] = trace_id
    if workflow_side_effect is not None:
        result["workflow_side_effect"] = workflow_side_effect
    if evidence is not None:
        result["evidence"] = evidence
    return result


def _runtime_result_ref(
    result_type: str,
    resource_id: Any,
    *,
    workflow_instance_id: Any,
    workflow_template_id: Any,
    operation: str,
    status: str,
    trace_id: Any = None,
) -> dict[str, Any]:
    ref = {
        "type": result_type,
        "resource_id": resource_id,
        "workflow_instance_id": workflow_instance_id,
        "workflow_template_id": workflow_template_id,
        "operation": operation,
        "status": status,
    }
    if trace_id:
        ref["trace_id"] = trace_id
    return _redact(ref)


def _record_operation_evidence(
    gateway: GatewayService,
    scope: ScopeContext,
    *,
    operation: str,
    workflow_instance_id: Any,
    workflow_template_id: Any,
    body: dict[str, Any],
    status: str,
    runtime_result_ref: dict[str, Any],
    resource_id: Any = None,
) -> dict[str, Any] | None:
    if not workflow_instance_id:
        return None
    gateway.workflow_repository.get_instance(str(workflow_instance_id), scope=scope)
    proposal_id = str(body.get("proposal_id") or "")
    handoff_id = str(body.get("handoff_id") or "")
    handoff = _safe_handoff(handoff_id)
    proposal = _safe_agent_action_proposal(proposal_id)
    operation_id = _operation_id(
        operation=operation,
        workflow_instance_id=workflow_instance_id,
        resource_id=resource_id or _operation_resource_id(operation, body, runtime_result_ref),
        proposal_id=proposal_id,
        handoff_id=handoff_id,
    )
    idempotency_key = str(body.get("idempotency_key") or body.get("event_id") or operation_id)
    evidence = {
        "evidence_id": f"evd_{uuid4().hex[:12]}",
        "workflow_instance_id": workflow_instance_id,
        "workflow_template_id": workflow_template_id,
        "operation": operation,
        "status": status,
        "correlation_id": str(body.get("correlation_id") or handoff_id or proposal_id or operation_id),
        "operation_id": operation_id,
        "idempotency_key": idempotency_key,
        "handoff_id": handoff_id or None,
        "proposal_id": proposal_id or None,
        "handoff_status_at_execution": handoff.get("status") if handoff else None,
        "proposal_status_at_execution": proposal.get("status") if proposal else None,
        "user_confirmed": body.get("user_confirmed") is True,
        "source": body.get("source"),
        "risk_flags": _risk_flags_for_evidence(proposal, handoff),
        "policy_decision": _policy_decision_for_evidence(status, proposal),
        "runtime_result_ref": runtime_result_ref,
        "audit_refs": _audit_refs_for_evidence(handoff_id),
        "created_at": _now_iso(),
        "created_by": str(body.get("source") or "workflow_console"),
        "redaction_status": "redacted",
    }
    record = _AGENT_OPERATION_EVIDENCE_REPOSITORY.create(evidence)
    if handoff_id:
        _append_handoff_audit(
            handoff_id,
            "operation_evidence_created",
            summary="User-confirmed operation evidence created.",
            data={"evidence_id": record["evidence_id"], "operation": operation, "status": status},
        )
    return record


def _record_operation_evidence_error(
    gateway: GatewayService,
    scope: ScopeContext | None,
    *,
    operation: str,
    workflow_instance_id: Any,
    workflow_template_id: Any,
    body: dict[str, Any],
    error: ProtocolError,
    resource_id: Any = None,
) -> dict[str, Any] | None:
    if scope is None or not isinstance(body, dict) or body.get("user_confirmed") is not True or not workflow_instance_id:
        return None
    status = _evidence_status_from_error(error, body)
    try:
        return _record_operation_evidence(
            gateway,
            scope,
            operation=operation,
            workflow_instance_id=workflow_instance_id,
            workflow_template_id=workflow_template_id,
            body=body,
            status=status,
            runtime_result_ref=_runtime_result_ref(
                "operation_error",
                resource_id or _operation_resource_id(operation, body, {}),
                workflow_instance_id=workflow_instance_id,
                workflow_template_id=workflow_template_id,
                operation=operation,
                status=str(error.code),
            ),
            resource_id=resource_id,
        )
    except Exception:
        return None


def _evidence_status_from_error(error: ProtocolError, body: dict[str, Any]) -> str:
    code = str(error.code)
    data = error.data if isinstance(error.data, dict) else {}
    handoff_status = str(data.get("status") or "")
    reason = str(data.get("reason") or "")
    if handoff_status == "expired" or "expired" in reason:
        return "expired_rejected"
    if handoff_status == "stale" or "stale" in reason or "CONFLICT" in code:
        return "stale_rejected"
    if code in {"WORKFLOW_ACTION_FORBIDDEN", "CAPABILITY_DENIED"}:
        return "blocked"
    return "failed"


def _operation_resource_id(operation: str, body: dict[str, Any], runtime_result_ref: dict[str, Any]) -> str:
    if runtime_result_ref.get("resource_id"):
        return str(runtime_result_ref["resource_id"])
    for key in ("workflow_patch_id", "approval_id", "event_id", "path", "version", "handoff_id"):
        if body.get(key):
            return str(body[key])
    return operation


def _operation_id(*, operation: str, workflow_instance_id: Any, resource_id: Any, proposal_id: str, handoff_id: str) -> str:
    parts = [operation, str(workflow_instance_id or ""), str(resource_id or "")]
    if proposal_id:
        parts.append(proposal_id)
    if handoff_id:
        parts.append(handoff_id)
    return ":".join(parts)


def _safe_handoff(handoff_id: str) -> dict[str, Any] | None:
    if not handoff_id:
        return None
    try:
        return _AGENT_HANDOFF_REPOSITORY.get(handoff_id)
    except ProtocolError:
        return None


def _safe_agent_action_proposal(proposal_id: str) -> dict[str, Any] | None:
    if not proposal_id:
        return None
    for proposals in _AGENT_ACTION_PROPOSALS.values():
        for proposal in proposals:
            if proposal.get("proposal_id") == proposal_id:
                return proposal
    return None


def _risk_flags_for_evidence(proposal: dict[str, Any] | None, handoff: dict[str, Any] | None) -> list[Any]:
    if proposal and isinstance(proposal.get("risk_flags"), list):
        return proposal["risk_flags"]
    resource = handoff.get("target_resource") if handoff and isinstance(handoff.get("target_resource"), dict) else {}
    return resource.get("risk_flags") if isinstance(resource.get("risk_flags"), list) else []


def _policy_decision_for_evidence(status: str, proposal: dict[str, Any] | None) -> str:
    if proposal and proposal.get("policy_decision"):
        return str(proposal["policy_decision"])
    if status in {"blocked", "stale_rejected", "expired_rejected"}:
        return status
    return "user_confirmed"


def _audit_refs_for_evidence(handoff_id: str) -> list[dict[str, Any]]:
    if not handoff_id:
        return []
    try:
        return [
            {"audit_id": item.get("audit_id"), "event_type": item.get("event_type"), "created_at": item.get("created_at")}
            for item in _AGENT_HANDOFF_REPOSITORY.list_audit(handoff_id)
        ]
    except ProtocolError:
        return []


def _operation_evidence_dto(evidence: dict[str, Any]) -> dict[str, Any]:
    return {
        "evidence_id": evidence.get("evidence_id"),
        "workflow_instance_id": evidence.get("workflow_instance_id"),
        "workflow_template_id": evidence.get("workflow_template_id"),
        "operation": evidence.get("operation"),
        "status": evidence.get("status"),
        "correlation_id": evidence.get("correlation_id"),
        "operation_id": evidence.get("operation_id"),
        "idempotency_key": evidence.get("idempotency_key"),
        "handoff_id": evidence.get("handoff_id"),
        "proposal_id": evidence.get("proposal_id"),
        "handoff_status_at_execution": evidence.get("handoff_status_at_execution"),
        "proposal_status_at_execution": evidence.get("proposal_status_at_execution"),
        "user_confirmed": bool(evidence.get("user_confirmed")),
        "source": evidence.get("source"),
        "risk_flags": evidence.get("risk_flags") if isinstance(evidence.get("risk_flags"), list) else [],
        "policy_decision": evidence.get("policy_decision"),
        "runtime_result_ref": _redact(evidence.get("runtime_result_ref") if isinstance(evidence.get("runtime_result_ref"), dict) else {}),
        "audit_refs": _redact(evidence.get("audit_refs") if isinstance(evidence.get("audit_refs"), list) else []),
        "created_at": evidence.get("created_at"),
        "created_by": evidence.get("created_by"),
        "redaction_status": "redacted",
    }


def _governance_review_dto(
    *,
    workflow_instance_id: str,
    workflow_template_id: str,
    evidence_records: list[dict[str, Any]],
    handoffs: list[dict[str, Any]],
) -> dict[str, Any]:
    status_counts: dict[str, int] = {}
    operation_counts: dict[str, int] = {}
    for record in evidence_records:
        status_counts[str(record.get("status") or "unknown")] = status_counts.get(str(record.get("status") or "unknown"), 0) + 1
        operation_counts[str(record.get("operation") or "unknown")] = operation_counts.get(str(record.get("operation") or "unknown"), 0) + 1
    return {
        "workflow_instance_id": workflow_instance_id,
        "workflow_template_id": workflow_template_id,
        "summary": {
            "evidence_count": len(evidence_records),
            "handoff_count": len(handoffs),
            "status_counts": status_counts,
            "operation_counts": operation_counts,
        },
        "operation_evidence": [_operation_evidence_dto(item) for item in evidence_records],
        "handoff_summary": [
            {
                "handoff_id": item.get("handoff_id"),
                "proposal_id": item.get("proposal_id"),
                "target_panel": item.get("target_panel"),
                "status": item.get("status"),
                "inactive_reason": _redact(item.get("inactive_reason")),
            }
            for item in handoffs
        ],
        "audit_timeline": _governance_audit_timeline(evidence_records, handoffs),
        "redaction_status": "redacted",
    }


def _agent_talk_interaction_state_dto(
    gateway: GatewayService,
    scope: ScopeContext,
    session: dict[str, Any],
) -> dict[str, Any]:
    workflow_instance_id = str(session.get("workflow_instance_id") or "")
    workflow_template_id = str(session.get("workflow_template_id") or "")
    template = gateway.workflow_repository.get_template(workflow_template_id, scope=scope)
    draft = gateway.workflow_repository.get_draft(str(template.latest_draft_id), scope=scope)
    patch_queue = _patch_queue_dto(
        [
            patch.model_dump(mode="json")
            for patch in gateway.workflow_repository.list_patches(scope=scope, workflow_template_id=workflow_template_id)
            if _patch_matches_instance(patch, workflow_instance_id)
        ],
        current_draft_revision=draft.revision,
    )
    suggestions = _AGENT_TALK_SUGGESTIONS.get(str(session.get("agent_session_id")), [])
    proposals = _AGENT_ACTION_PROPOSALS.get(str(session.get("agent_session_id")), [])
    handoffs = [
        _refresh_handoff_for_read(gateway, scope, handoff)
        for handoff in _AGENT_HANDOFF_REPOSITORY.list(agent_session_id=str(session.get("agent_session_id")), workflow_instance_id=workflow_instance_id)
    ]
    evidence = _AGENT_OPERATION_EVIDENCE_REPOSITORY.list(workflow_instance_id=workflow_instance_id)

    selected_suggestion = next((item for item in suggestions if item.get("status") == "active"), None)
    selected_proposal = next(
        (
            item
            for item in proposals
            if item.get("lifecycle") not in {"dismissed", "blocked", "expired"} and item.get("policy_class") != "display_only"
        ),
        None,
    )
    selected_handoff = next((item for item in handoffs if item.get("status") in HANDOFF_ACTIVE_STATES), None)
    selected_patch = next((item for item in patch_queue if item.get("selected")), None)
    selected_evidence = sorted(evidence, key=lambda item: str(item.get("created_at") or ""))[-1] if evidence else None

    stale_reasons = _agent_interaction_stale_reasons(
        selected_proposal=selected_proposal,
        selected_handoff=selected_handoff,
        selected_patch=selected_patch,
        proposals=proposals,
        handoffs=handoffs,
    )
    return {
        "workflow_instance_id": workflow_instance_id,
        "workflow_template_id": workflow_template_id,
        "agent_session_id": session.get("agent_session_id"),
        "selected_suggestion_id": selected_suggestion.get("suggestion_id") if selected_suggestion else None,
        "selected_proposal_id": selected_proposal.get("proposal_id") if selected_proposal else None,
        "selected_handoff_id": selected_handoff.get("handoff_id") if selected_handoff else None,
        "selected_patch_id": selected_patch.get("patch_id") if selected_patch else None,
        "selected_evidence_id": selected_evidence.get("evidence_id") if selected_evidence else None,
        "stale_reasons": stale_reasons,
        "refresh_generation": _agent_interaction_refresh_generation(
            session=session,
            suggestions=suggestions,
            proposals=proposals,
            handoffs=handoffs,
            patch_queue=patch_queue,
            evidence=evidence,
        ),
        "source_refs": {
            "agent_session": {"kind": "AgentTalkSessionDTO", "agent_session_id": session.get("agent_session_id")},
            "suggestions": {"kind": "AgentTalkSuggestionDTO", "count": len(suggestions)},
            "action_proposals": {"kind": "AgentActionProposalDTO", "count": len(proposals)},
            "handoffs": {"kind": "AgentActionHandoffDTO", "count": len(handoffs)},
            "patch_queue": {"kind": "PatchQueueDTO", "revision": _patch_queue_revision(patch_queue)},
            "canvas_projection": {"kind": "CanvasDraftProjection", "workflow_instance_id": workflow_instance_id},
            "evidence": {"kind": "OperationEvidenceDTO", "count": len(evidence)},
        },
        "generated_at": _now_iso(),
        "redaction_status": "redacted",
    }


def _agent_interaction_stale_reasons(
    *,
    selected_proposal: dict[str, Any] | None,
    selected_handoff: dict[str, Any] | None,
    selected_patch: dict[str, Any] | None,
    proposals: list[dict[str, Any]],
    handoffs: list[dict[str, Any]],
) -> list[str]:
    reasons: list[str] = []
    if selected_proposal and selected_proposal.get("lifecycle") in {"dismissed", "blocked", "expired"}:
        reasons.append("selected_proposal_stale")
    if selected_handoff and selected_handoff.get("status") not in HANDOFF_ACTIVE_STATES:
        reasons.append("selected_handoff_stale")
    if selected_patch and selected_patch.get("status") in {"stale", "blocked", "conflicted"}:
        reasons.append(f"selected_patch_{selected_patch.get('status')}")
    if any(item.get("lifecycle") == "dismissed" for item in proposals):
        reasons.append("dismissed_proposal_not_handoffable")
    if any(item.get("status") in {"expired", "stale", "blocked", "dismissed"} for item in handoffs):
        reasons.append("inactive_handoff_not_usable")
    return reasons


def _agent_interaction_refresh_generation(
    *,
    session: dict[str, Any],
    suggestions: list[dict[str, Any]],
    proposals: list[dict[str, Any]],
    handoffs: list[dict[str, Any]],
    patch_queue: list[dict[str, Any]],
    evidence: list[dict[str, Any]],
) -> str:
    parts = [
        f"session:{session.get('agent_session_id')}:{session.get('updated_at') or session.get('created_at')}",
        "suggestions:" + "|".join(f"{item.get('suggestion_id')}:{item.get('status')}" for item in suggestions),
        "proposals:" + "|".join(f"{item.get('proposal_id')}:{item.get('lifecycle')}:{item.get('updated_at')}" for item in proposals),
        "handoffs:" + "|".join(f"{item.get('handoff_id')}:{item.get('status')}:{item.get('updated_at')}" for item in handoffs),
        _patch_queue_revision(patch_queue),
        "evidence:" + "|".join(f"{item.get('evidence_id')}:{item.get('status')}:{item.get('created_at')}" for item in evidence),
    ]
    return "agent_interaction:" + "||".join(parts)


def _governance_audit_timeline(evidence_records: list[dict[str, Any]], handoffs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for record in evidence_records:
        items.append(
            {
                "type": "operation_evidence",
                "resource_id": record.get("evidence_id"),
                "operation": record.get("operation"),
                "status": record.get("status"),
                "created_at": record.get("created_at"),
            }
        )
    for handoff in handoffs:
        items.append(
            {
                "type": "agent_handoff",
                "resource_id": handoff.get("handoff_id"),
                "target_panel": handoff.get("target_panel"),
                "status": handoff.get("status"),
                "created_at": handoff.get("created_at"),
            }
        )
    return sorted(items, key=lambda item: str(item.get("created_at") or ""))


def _template_id_for_instance(gateway: GatewayService, workflow_instance_id: str, scope: ScopeContext) -> str:
    return gateway.workflow_repository.get_instance(workflow_instance_id, scope=scope).workflow_template_id


def _safe_template_id_for_instance(gateway: GatewayService, workflow_instance_id: Any, scope: ScopeContext | None) -> str | None:
    if not workflow_instance_id or scope is None:
        return None
    try:
        return _template_id_for_instance(gateway, str(workflow_instance_id), scope)
    except Exception:
        return None


def _approval_workflow_binding(approval: dict[str, Any]) -> dict[str, Any]:
    metadata = approval.get("metadata") if isinstance(approval.get("metadata"), dict) else {}
    binding = metadata.get("workflow_binding") if isinstance(metadata.get("workflow_binding"), dict) else {}
    return binding


def _canvas_patch_request_to_patch(
    workflow_template_id: str,
    body: dict[str, Any],
) -> dict[str, Any]:
    source = str(body.get("source") or "")
    intent_type = str(body.get("intent_type") or "")
    operation = str(body.get("operation") or "")
    payload = body.get("payload")
    if source not in CANVAS_PATCH_SOURCES:
        raise ProtocolError("WORKFLOW_PATCH_INVALID", "Patch proposal source must be canvas, inspector, agent, or workflow_console.", {"source": source or None})
    if intent_type not in CANVAS_PATCH_INTENTS:
        raise ProtocolError("WORKFLOW_PATCH_INVALID", "Patch proposal intent_type is invalid.", {"intent_type": intent_type or None})
    if operation not in CANVAS_PATCH_OPERATIONS[intent_type]:
        raise ProtocolError(
            "WORKFLOW_PATCH_INVALID",
            "Patch proposal operation does not match intent_type.",
            {"intent_type": intent_type, "operation": operation or None},
        )
    if not isinstance(payload, dict):
        raise ProtocolError("WORKFLOW_PATCH_INVALID", "Patch proposal payload must be an object.", {"field": "payload"})
    _reject_sensitive_or_layout_fields(payload)
    workflow_instance_id = body.get("workflow_instance_id")
    metadata: dict[str, Any] = {"source": source, "intent_type": intent_type}
    if isinstance(workflow_instance_id, str) and workflow_instance_id:
        metadata["workflow_instance_id"] = workflow_instance_id
    actor_id = f"{source}_proposal"
    actor_type = "agent" if source == "agent" else "user"
    return {
        "operation": operation,
        "payload": payload,
        "actor_type": actor_type,
        "actor_id": actor_id,
        "proposed_by": actor_id,
        "metadata": metadata,
    }


def _reject_sensitive_or_layout_fields(value: Any) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            normalized = str(key).lower().replace("-", "_")
            compact = normalized.replace("_", "")
            is_sensitive = any(part in normalized for part in SENSITIVE_KEY_PARTS) or any(part in compact for part in SENSITIVE_KEY_COMPACT_PARTS)
            if is_sensitive or compact in UI_LAYOUT_KEYS:
                field = "sensitive" if is_sensitive else str(key)
                raise ProtocolError("WORKFLOW_PATCH_INVALID", "Patch proposal payload contains forbidden field.", {"field": field})
            _reject_sensitive_or_layout_fields(item)
    elif isinstance(value, list):
        for item in value:
            _reject_sensitive_or_layout_fields(item)


def _validate_canvas_patch_payload(gateway: GatewayService, workflow_template_id: str, patch: dict[str, Any], scope: ScopeContext) -> None:
    operation = str(patch.get("operation") or "")
    payload = patch.get("payload") if isinstance(patch.get("payload"), dict) else {}
    template = gateway.workflow_repository.get_template(workflow_template_id, scope=scope)
    draft = gateway.workflow_repository.get_draft(str(template.latest_draft_id), scope=scope)
    draft_payload = draft.draft if isinstance(draft.draft, dict) else {}
    metadata = patch.get("metadata") if isinstance(patch.get("metadata"), dict) else {}
    workflow_instance_id = metadata.get("workflow_instance_id")
    if isinstance(workflow_instance_id, str) and workflow_instance_id:
        instance = gateway.workflow_repository.get_instance(workflow_instance_id, scope=scope)
        if instance.workflow_template_id != workflow_template_id:
            raise ProtocolError("SCOPE_MISMATCH", "Workflow instance does not belong to workflow template.", {"resource": "workflow_instance_id"})
    if operation == "add_station":
        _validate_node_add_payload(payload, draft_payload)
    elif operation == "update_edge":
        _validate_edge_intent_payload(payload, draft_payload)
    elif operation in INSPECTOR_OPERATION_FIELDS:
        _validate_inspector_patch_payload(operation, payload, draft_payload)
    elif operation == "update_connector":
        refs = payload.get("connector_refs")
        if refs is not None and (not isinstance(refs, list) or any(ref not in ALLOWED_CONNECTOR_REFS for ref in refs)):
            raise ProtocolError("WORKFLOW_PATCH_INVALID", "connector_refs contains unsupported connector.", {"field": "connector_refs"})
        connector_patch = payload.get("connector_patch")
        if isinstance(connector_patch, dict):
            _reject_sensitive_or_layout_fields(connector_patch)
    elif operation == "update_quality_rule":
        patch_payload = payload.get("quality_patch")
        if isinstance(patch_payload, dict):
            threshold = patch_payload.get("threshold")
            if threshold is not None and not (isinstance(threshold, (int, float)) and 0 <= float(threshold) <= 1):
                raise ProtocolError("WORKFLOW_PATCH_INVALID", "quality threshold must be between 0 and 1.", {"field": "threshold"})
    elif operation == "update_approval_point":
        if "approval_required" in payload and not isinstance(payload.get("approval_required"), bool):
            raise ProtocolError("WORKFLOW_PATCH_INVALID", "approval_required must be boolean.", {"field": "approval_required"})


def _validate_node_add_payload(payload: dict[str, Any], draft_payload: dict[str, Any]) -> None:
    station = payload.get("station")
    if not isinstance(station, dict):
        raise ProtocolError("WORKFLOW_PATCH_INVALID", "add_station requires station descriptor.", {"field": "station"})
    metadata = station.get("metadata") if isinstance(station.get("metadata"), dict) else {}
    catalog_id = metadata.get("node_catalog_id")
    if catalog_id not in ALLOWED_NODE_CATALOG_IDS:
        raise ProtocolError("WORKFLOW_PATCH_INVALID", "Station descriptor must come from allowed node catalog.", {"node_catalog_id": catalog_id})
    catalog_contract = NODE_CATALOG_CONTRACTS.get(str(catalog_id))
    if not catalog_contract:
        raise ProtocolError("WORKFLOW_PATCH_INVALID", "Station descriptor has no controlled catalog contract.", {"node_catalog_id": catalog_id})
    for required_field in (
        "catalog_id",
        "catalog_version",
        "node_template_id",
        "station_kind",
        "schema_version",
        "allowed_skill_refs",
        "allowed_connector_refs",
        "allowed_artifact_kinds",
        "allowed_quality_rules",
        "allowed_approval_policies",
    ):
        if metadata.get(required_field) != catalog_contract.get(required_field):
            raise ProtocolError("WORKFLOW_PATCH_INVALID", "Station descriptor does not match controlled catalog contract.", {"field": required_field})
    station_id = station.get("station_id")
    existing_ids = {item.get("station_id") for item in draft_payload.get("stations", []) if isinstance(item, dict)}
    if not isinstance(station_id, str) or not station_id:
        raise ProtocolError("WORKFLOW_PATCH_INVALID", "station_id is required.", {"field": "station_id"})
    if station_id in existing_ids:
        raise ProtocolError("WORKFLOW_PATCH_INVALID", "Station already exists.", {"station_id": station_id})
    refs = station.get("skill_refs")
    if refs is not None and (not isinstance(refs, list) or any(ref not in ALLOWED_SKILL_REFS for ref in refs)):
        raise ProtocolError("WORKFLOW_PATCH_INVALID", "skill_refs contains unsupported skill.", {"field": "skill_refs"})
    allowed_skill_refs = set(catalog_contract["allowed_skill_refs"])
    if refs is not None and any(ref not in allowed_skill_refs for ref in refs):
        raise ProtocolError("WORKFLOW_PATCH_INVALID", "skill_refs not allowed by node catalog contract.", {"field": "skill_refs"})
    connector_refs = station.get("connector_refs")
    if connector_refs is not None and (not isinstance(connector_refs, list) or any(ref not in ALLOWED_CONNECTOR_REFS for ref in connector_refs)):
        raise ProtocolError("WORKFLOW_PATCH_INVALID", "connector_refs contains unsupported connector.", {"field": "connector_refs"})
    allowed_connector_refs = set(catalog_contract["allowed_connector_refs"])
    if connector_refs is not None and any(ref not in allowed_connector_refs for ref in connector_refs):
        raise ProtocolError("WORKFLOW_PATCH_INVALID", "connector_refs not allowed by node catalog contract.", {"field": "connector_refs"})
    if station.get("role") and station.get("role") != catalog_contract["station_kind"]:
        raise ProtocolError("WORKFLOW_PATCH_INVALID", "station role must match node catalog station_kind.", {"field": "role"})


def _validate_inspector_patch_payload(operation: str, payload: dict[str, Any], draft_payload: dict[str, Any]) -> None:
    allowed = INSPECTOR_OPERATION_FIELDS[operation]
    unknown = sorted(set(payload) - allowed)
    if unknown:
        raise ProtocolError("WORKFLOW_PATCH_INVALID", "Inspector patch payload contains unknown fields.", {"fields": unknown, "operation": operation})
    if operation != "update_quality_rule":
        station_id = payload.get("station_id")
        station_ids = {item.get("station_id") for item in draft_payload.get("stations", []) if isinstance(item, dict)}
        if not isinstance(station_id, str) or station_id not in station_ids:
            raise ProtocolError("WORKFLOW_PATCH_INVALID", "Inspector patch references missing station.", {"field": "station_id"})
    if operation == "update_connector":
        refs = payload.get("connector_refs")
        if refs is not None and (not isinstance(refs, list) or any(ref not in ALLOWED_CONNECTOR_REFS for ref in refs)):
            raise ProtocolError("WORKFLOW_PATCH_INVALID", "connector_refs contains unsupported connector.", {"field": "connector_refs"})
    if operation == "update_artifact_contract":
        patch = payload.get("contract_patch")
        if not isinstance(payload.get("contract_id"), str) or not isinstance(patch, dict):
            raise ProtocolError("WORKFLOW_PATCH_INVALID", "Artifact contract patch requires contract_id and contract_patch.", {"field": "contract_patch"})
        artifact_kind = patch.get("artifact_kind")
        if artifact_kind is not None and not isinstance(artifact_kind, str):
            raise ProtocolError("WORKFLOW_PATCH_INVALID", "artifact_kind must be a string.", {"field": "artifact_kind"})
        direction = patch.get("direction")
        if direction is not None and direction not in {"input", "output"}:
            raise ProtocolError("WORKFLOW_PATCH_INVALID", "artifact contract direction must be input or output.", {"field": "direction"})
        schema_ref = patch.get("schema_ref")
        if schema_ref is not None and not isinstance(schema_ref, str):
            raise ProtocolError("WORKFLOW_PATCH_INVALID", "schema_ref must be a string.", {"field": "schema_ref"})
    if operation == "update_quality_rule":
        quality_ids = {item.get("contract_id") for item in draft_payload.get("quality_contracts", []) if isinstance(item, dict)}
        if payload.get("quality_contract_id") not in quality_ids:
            raise ProtocolError("WORKFLOW_PATCH_INVALID", "Quality contract not found.", {"field": "quality_contract_id"})
        patch = payload.get("quality_patch")
        if not isinstance(patch, dict):
            raise ProtocolError("WORKFLOW_PATCH_INVALID", "quality_patch must be an object.", {"field": "quality_patch"})
        threshold = patch.get("threshold")
        if threshold is not None and not (isinstance(threshold, (int, float)) and 0 <= float(threshold) <= 1):
            raise ProtocolError("WORKFLOW_PATCH_INVALID", "quality threshold must be between 0 and 1.", {"field": "threshold"})
    if operation == "update_approval_point" and "approval_required" in payload and not isinstance(payload.get("approval_required"), bool):
        raise ProtocolError("WORKFLOW_PATCH_INVALID", "approval_required must be boolean.", {"field": "approval_required"})


def _validate_edge_intent_payload(payload: dict[str, Any], draft_payload: dict[str, Any]) -> None:
    edge_patch = payload.get("edge_patch")
    if not isinstance(edge_patch, dict):
        raise ProtocolError("WORKFLOW_PATCH_INVALID", "update_edge requires edge_patch.", {"field": "edge_patch"})
    action = edge_patch.get("action", "update")
    if action not in {"add", "remove", "update"}:
        raise ProtocolError("WORKFLOW_PATCH_INVALID", "edge_patch.action must be add, remove, or update.", {"action": action})
    station_ids = {item.get("station_id") for item in draft_payload.get("stations", []) if isinstance(item, dict)}
    edges = [item for item in draft_payload.get("edges", []) if isinstance(item, dict)]
    edge_id = payload.get("edge_id")
    if not isinstance(edge_id, str) or not edge_id:
        raise ProtocolError("WORKFLOW_PATCH_INVALID", "edge_id is required.", {"field": "edge_id"})
    if action == "add":
        from_station_id = edge_patch.get("from_station_id")
        to_station_id = edge_patch.get("to_station_id")
        if from_station_id not in station_ids or to_station_id not in station_ids:
            raise ProtocolError("WORKFLOW_PATCH_INVALID", "Workflow edge references missing station.", {"edge_id": edge_id})
        if from_station_id == to_station_id:
            raise ProtocolError("WORKFLOW_PATCH_INVALID", "Workflow edge cannot be a self-loop.", {"edge_id": edge_id})
        if any(edge.get("edge_id") == edge_id or (edge.get("from_station_id") == from_station_id and edge.get("to_station_id") == to_station_id) for edge in edges):
            raise ProtocolError("WORKFLOW_PATCH_INVALID", "Workflow edge already exists.", {"edge_id": edge_id})
        if _would_create_cycle(edges, str(from_station_id), str(to_station_id)):
            raise ProtocolError("WORKFLOW_PATCH_INVALID", "Workflow edge would create a cycle.", {"edge_id": edge_id})
        if not _edge_artifact_contracts_compatible(draft_payload, str(from_station_id), str(to_station_id), edge_patch):
            raise ProtocolError("WORKFLOW_PATCH_INVALID", "Workflow edge artifact contracts are incompatible.", {"edge_id": edge_id})
    else:
        existing_edge = next((edge for edge in edges if edge.get("edge_id") == edge_id), None)
        if existing_edge is None:
            raise ProtocolError("WORKFLOW_PATCH_INVALID", "Workflow edge not found.", {"edge_id": edge_id})
        if action == "update":
            from_station_id = edge_patch.get("from_station_id", existing_edge.get("from_station_id"))
            to_station_id = edge_patch.get("to_station_id", existing_edge.get("to_station_id"))
            if from_station_id not in station_ids or to_station_id not in station_ids:
                raise ProtocolError("WORKFLOW_PATCH_INVALID", "Workflow edge references missing station.", {"edge_id": edge_id})
            if from_station_id == to_station_id:
                raise ProtocolError("WORKFLOW_PATCH_INVALID", "Workflow edge cannot be a self-loop.", {"edge_id": edge_id})
            peer_edges = [edge for edge in edges if edge.get("edge_id") != edge_id]
            if any(edge.get("from_station_id") == from_station_id and edge.get("to_station_id") == to_station_id for edge in peer_edges):
                raise ProtocolError("WORKFLOW_PATCH_INVALID", "Workflow edge already exists.", {"edge_id": edge_id})
            if _would_create_cycle(peer_edges, str(from_station_id), str(to_station_id)):
                raise ProtocolError("WORKFLOW_PATCH_INVALID", "Workflow edge would create a cycle.", {"edge_id": edge_id})
            if not _edge_artifact_contracts_compatible(draft_payload, str(from_station_id), str(to_station_id), edge_patch):
                raise ProtocolError("WORKFLOW_PATCH_INVALID", "Workflow edge artifact contracts are incompatible.", {"edge_id": edge_id})


def _would_create_cycle(edges: list[dict[str, Any]], from_station_id: str, to_station_id: str) -> bool:
    adjacency: dict[str, set[str]] = {}
    for edge in edges:
        if not isinstance(edge.get("from_station_id"), str) or not isinstance(edge.get("to_station_id"), str):
            continue
        adjacency.setdefault(str(edge["from_station_id"]), set()).add(str(edge["to_station_id"]))
    adjacency.setdefault(from_station_id, set()).add(to_station_id)
    seen: set[str] = set()
    stack = [to_station_id]
    while stack:
        current = stack.pop()
        if current == from_station_id:
            return True
        if current in seen:
            continue
        seen.add(current)
        stack.extend(adjacency.get(current, set()))
    return False


def _edge_artifact_contracts_compatible(
    draft_payload: dict[str, Any],
    from_station_id: str,
    to_station_id: str,
    edge_patch: dict[str, Any],
) -> bool:
    stations = [item for item in draft_payload.get("stations", []) if isinstance(item, dict)]
    source = next((station for station in stations if station.get("station_id") == from_station_id), None)
    target = next((station for station in stations if station.get("station_id") == to_station_id), None)
    if not source or not target:
        return False
    outputs = [item for item in source.get("output_contracts", []) if isinstance(item, dict)]
    inputs = [item for item in target.get("input_contracts", []) if isinstance(item, dict)]
    if not outputs or not inputs:
        return True
    requested = edge_patch.get("artifact_contract")
    requested_kind = requested.get("artifact_kind") if isinstance(requested, dict) else None
    requested_schema_ref = requested.get("schema_ref") if isinstance(requested, dict) else None
    for output in outputs:
        for input_contract in inputs:
            if output.get("direction", "output") != "output" or input_contract.get("direction", "input") != "input":
                continue
            kind_matches = output.get("artifact_kind") == input_contract.get("artifact_kind")
            schema_matches = bool(output.get("schema_ref") and output.get("schema_ref") == input_contract.get("schema_ref"))
            requested_matches = (
                requested_kind is None
                or requested_kind in {output.get("artifact_kind"), input_contract.get("artifact_kind")}
            ) and (
                requested_schema_ref is None
                or requested_schema_ref in {output.get("schema_ref"), input_contract.get("schema_ref")}
            )
            if (kind_matches or schema_matches) and requested_matches:
                return True
    return False


def _ensure_approval_in_instance(approval: dict[str, Any], workflow_instance_id: str) -> None:
    if _approval_workflow_binding(approval).get("workflow_instance_id") != workflow_instance_id:
        raise ProtocolError("SCOPE_MISMATCH", "Approval does not belong to workflow instance.", {"resource": "approval_id"})


def _ensure_quality_in_instance(evaluation: dict[str, Any], workflow_instance_id: str) -> None:
    if evaluation.get("workflow_instance_id") != workflow_instance_id:
        raise ProtocolError("SCOPE_MISMATCH", "Quality evaluation does not belong to workflow instance.", {"resource": "evaluation_id"})


def _ensure_station_run_in_instance(gateway: GatewayService, station_run_id: str, workflow_instance_id: str, scope: ScopeContext) -> None:
    station_run = gateway.workflow_repository.get_station_run(station_run_id, scope=scope)
    if station_run.workflow_instance_id != workflow_instance_id:
        raise ProtocolError("SCOPE_MISMATCH", "Station run does not belong to workflow instance.", {"resource": "station_run_id"})


def _ensure_artifact_in_instance(gateway: GatewayService, artifact_id: str, workflow_instance_id: str, scope: ScopeContext) -> None:
    instance = gateway.workflow_repository.get_instance(workflow_instance_id, scope=scope)
    if artifact_id in set(instance.artifact_ids):
        return
    station_runs = gateway.workflow_repository.list_station_runs(workflow_instance_id, scope=scope)
    for run in station_runs:
        if artifact_id in set(run.input_artifact_ids) or artifact_id in set(run.output_artifact_ids):
            return
    raise ProtocolError("SCOPE_MISMATCH", "Artifact does not belong to workflow instance.", {"resource": "artifact_id"})


def _ensure_patch_in_template(gateway: GatewayService, workflow_patch_id: str, workflow_template_id: str, scope: ScopeContext) -> None:
    patch = gateway.workflow_repository.get_patch(workflow_patch_id, scope=scope)
    if patch.workflow_template_id != workflow_template_id:
        raise ProtocolError("SCOPE_MISMATCH", "Workflow patch does not belong to workflow template.", {"resource": "workflow_patch_id"})


def _ensure_patch_editable_for_template(
    gateway: GatewayService,
    workflow_patch_id: str,
    workflow_template_id: str,
    scope: ScopeContext,
    *,
    workflow_instance_id: Any = None,
):
    template = gateway.workflow_repository.get_template(workflow_template_id, scope=scope)
    patch = gateway.workflow_repository.get_patch(workflow_patch_id, scope=scope)
    if patch.workflow_template_id != workflow_template_id:
        raise ProtocolError("SCOPE_MISMATCH", "Workflow patch does not belong to workflow template.", {"resource": "workflow_patch_id"})
    if patch.workflow_draft_id != template.latest_draft_id:
        raise ProtocolError("SCOPE_MISMATCH", "Workflow patch does not target the latest workflow draft.", {"resource": "workflow_draft_id"})
    metadata = patch.metadata if isinstance(patch.metadata, dict) else {}
    bound_instance_id = metadata.get("workflow_instance_id")
    if workflow_instance_id and bound_instance_id and bound_instance_id != workflow_instance_id:
        raise ProtocolError("SCOPE_MISMATCH", "Workflow patch is not bound to the selected workflow instance.", {"resource": "workflow_instance_id"})
    if patch.status != "applied":
        draft = gateway.workflow_repository.get_draft(patch.workflow_draft_id, scope=scope)
        if draft.revision != patch.base_revision:
            raise ProtocolError(
                "WORKFLOW_PATCH_CONFLICT",
                "Workflow patch base revision does not match current draft revision.",
                {"base_revision": patch.base_revision, "actual_revision": draft.revision},
            )
    return patch


def _ensure_patch_in_instance(gateway: GatewayService, workflow_patch_id: str, workflow_instance_id: str, scope: ScopeContext) -> None:
    instance = gateway.workflow_repository.get_instance(workflow_instance_id, scope=scope)
    patch = gateway.workflow_repository.get_patch(workflow_patch_id, scope=scope)
    if patch.workflow_template_id != instance.workflow_template_id:
        raise ProtocolError("SCOPE_MISMATCH", "Workflow patch does not belong to workflow instance template.", {"resource": "workflow_patch_id"})
    metadata = patch.metadata if isinstance(patch.metadata, dict) else {}
    bound_instance_id = metadata.get("workflow_instance_id")
    if bound_instance_id != workflow_instance_id:
        raise ProtocolError("SCOPE_MISMATCH", "Workflow patch is not bound to this workflow instance.", {"resource": "workflow_patch_id"})


def _patch_matches_instance(patch: Any, workflow_instance_id: str) -> bool:
    metadata = patch.metadata if hasattr(patch, "metadata") and isinstance(patch.metadata, dict) else {}
    bound_instance_id = metadata.get("workflow_instance_id")
    return bound_instance_id in (None, workflow_instance_id)


def _require_user_confirmed(body: dict[str, Any], *, allowed_sources: set[str]) -> None:
    source = str(body.get("source") or "")
    if body.get("user_confirmed") is not True or source not in allowed_sources:
        raise ProtocolError(
            "WORKFLOW_ACTION_FORBIDDEN",
            "Workflow editing action requires explicit user confirmation.",
            {"source": source or None},
        )


def _auth_has_capability(auth: Any, capability: str) -> bool:
    if getattr(auth, "dev_mode", False):
        return True
    claims = getattr(auth, "claims", None)
    capabilities = getattr(claims, "capabilities", ()) if claims is not None else ()
    return capability in set(capabilities)


def _collect_unsent_events(
    gateway: GatewayService,
    *,
    scope: ScopeContext,
    channels: list[str],
    filters: dict[str, Any],
    last_sequence: int,
    sent_keys: set[tuple[str, str]],
) -> tuple[list[dict[str, Any]], int]:
    events: list[dict[str, Any]] = []
    current_sequence = last_sequence
    for event in collect_event_envelopes(gateway, scope=scope, channels=channels, filters=filters):
        sequence = read_event_cursor(event["cursor"], scope)
        key = (str(event.get("channel") or ""), str(event.get("event_id") or ""))
        if sequence > current_sequence and key not in sent_keys:
            events.append(event)
            current_sequence = max(current_sequence, sequence)
            sent_keys.add(key)
    return events, current_sequence


def _query_scope_params(request: Request) -> dict[str, Any]:
    params: dict[str, Any] = {}
    for key in ("app_id", "project_id", "workspace_id"):
        value = request.query_params.get(key)
        if value:
            params[key] = value
    return params


def _redact(value: Any) -> Any:
    if isinstance(value, dict):
        redacted: dict[str, Any] = {}
        for key, item in value.items():
            lower = str(key).lower()
            if any(part in lower for part in SENSITIVE_KEY_PARTS):
                continue
            redacted[key] = _redact(item)
        return redacted
    if isinstance(value, list):
        return [_redact(item) for item in value]
    if isinstance(value, str) and (
        "Bearer " in value
        or "subscription_token" in value
        or "capability_token" in value
        or "Authorization" in value
        or "secret-token-value" in value
        or "raw_trace_payload" in value
        or "raw_artifact_content" in value
        or "raw_connector_payload" in value
    ):
        return "[redacted]"
    return value


def _truthy(value: Any) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "on"}


def _float_param(value: Any, *, default: float) -> float:
    if value in (None, ""):
        return default
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise ProtocolError("INVALID_PARAMS", "heartbeat_interval must be numeric.", {"field": "heartbeat_interval"}) from exc


def _int_param(value: Any) -> int | None:
    if value in (None, ""):
        return None
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise ProtocolError("INVALID_PARAMS", "max_heartbeats must be an integer.", {"field": "max_heartbeats"}) from exc
