"""MCP tools for V2.1 code quality governance."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from .code_assets.envelope import v2_error_envelope, v2_success_envelope
from .code_assets.quality.persistence import quality_artifact_refs
from .code_assets.quality.service import CodeQualityService, public_quality_payload


QUALITY_TOOL_NAMES = {
    "knowledge_code_quality_feedback",
    "knowledge_code_quality_summary",
    "knowledge_code_quality_rules_build",
    "knowledge_code_quality_rule_review",
    "knowledge_code_quality_plan",
}


QUALITY_TOOL_SPECS = [
    {
        "name": "knowledge_code_quality_feedback",
        "description": "Record V2.1 code quality feedback against a real project-intelligence target",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}, "target_type": {"type": "string"}, "target_id": {"type": "string"}, "action": {"type": "string"}, "rule_type": {"type": "string"}, "severity": {"type": "string"}, "reason": {"type": "string"}, "suggested_value": {"type": "string"}, "metadata": {"type": "object"}}, "required": ["workspace_id", "codebase_id", "target_type", "target_id", "action", "rule_type"]},
    },
    {
        "name": "knowledge_code_quality_summary",
        "description": "Read V2.1 code quality summary",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_quality_rules_build",
        "description": "Build deterministic draft V2.1 code quality rules from feedback",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_quality_rule_review",
        "description": "Approve, reject, or revoke a V2.1 code quality rule",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}, "rule_id": {"type": "string"}, "status": {"type": "string"}, "reviewer": {"type": "string"}, "note": {"type": "string"}}, "required": ["workspace_id", "codebase_id", "rule_id", "status"]},
    },
    {
        "name": "knowledge_code_quality_plan",
        "description": "Build a V2.1 code quality read-time overlay plan",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
]


def handle_quality_tool(name: str, arguments: dict[str, Any], *, blocked: Callable[..., dict[str, Any]], envelope: Callable[..., dict[str, Any]], ensure_workspace_meta: Callable[..., dict[str, Any]], resolve_workspace: Callable[[str | None, str | None], Path]) -> dict[str, Any]:
    if name not in QUALITY_TOOL_NAMES:
        raise ValueError(f"Unknown quality tool: {name}")
    workspace_path = resolve_workspace(arguments.get("workspace_id"), None)
    meta = ensure_workspace_meta(workspace_path)
    workspace_id = str(meta["workspace_id"])
    codebase_id = str(arguments.get("codebase_id") or "").strip()
    if not codebase_id:
        return blocked(workspace_id=workspace_id, message="codebase_id is required", next_actions=["knowledge_codebase_list"], code="invalid_codebase_id")
    service = CodeQualityService(workspace_path, workspace_id=workspace_id)
    try:
        if name == "knowledge_code_quality_feedback":
            result = service.record_feedback(
                codebase_id,
                target_type=str(arguments.get("target_type") or ""),
                target_id=str(arguments.get("target_id") or ""),
                action=str(arguments.get("action") or ""),
                rule_type=str(arguments.get("rule_type") or ""),
                severity=str(arguments.get("severity") or "medium"),
                reason=str(arguments.get("reason") or ""),
                suggested_value=str(arguments.get("suggested_value") or ""),
                metadata=arguments.get("metadata") if isinstance(arguments.get("metadata"), dict) else {},
            )
            next_actions = ["knowledge_code_quality_rules_build"]
        elif name == "knowledge_code_quality_summary":
            result = service.summary(codebase_id)
            next_actions = []
        elif name == "knowledge_code_quality_rules_build":
            result = service.build_rules(codebase_id)
            next_actions = ["knowledge_code_quality_rule_review"]
        elif name == "knowledge_code_quality_rule_review":
            result = service.review_rule(
                codebase_id,
                str(arguments.get("rule_id") or ""),
                status=str(arguments.get("status") or ""),
                reviewer=str(arguments.get("reviewer") or ""),
                note=str(arguments.get("note") or ""),
            )
            next_actions = ["knowledge_code_quality_plan"]
        else:
            result = service.build_plan(codebase_id)
            next_actions = []
        refs = result.get("artifact_refs", quality_artifact_refs(codebase_id))
        data = public_quality_payload(result)
        return envelope(workspace_id=workspace_id, artifact_refs=refs, next_actions=next_actions, data=_with_v2(workspace_id=workspace_id, codebase_id=codebase_id, data=data, artifact_refs=refs, next_actions=next_actions))
    except (FileNotFoundError, ValueError) as exc:
        code = _quality_error_code(str(exc))
        message = _quality_error_message(str(exc))
        return envelope(workspace_id=workspace_id, status="blocked", warnings=[message], data={"error": {"code": code, "message": message, "retryable": False}, "v2": v2_error_envelope(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=None, code=code, message=message)})


def _with_v2(*, workspace_id: str, codebase_id: str, data: dict[str, Any], artifact_refs: list[dict[str, Any]] | None = None, next_actions: list[str] | None = None) -> dict[str, Any]:
    payload = dict(data)
    payload["v2"] = v2_success_envelope(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=None, data=data, artifact_refs=artifact_refs, next_actions=next_actions)
    return payload


def _quality_error_code(error: str) -> str:
    for code in ["UNSUPPORTED_TARGET_TYPE", "UNSUPPORTED_RULE_TYPE", "UNSUPPORTED_REVIEW_STATUS", "QUALITY_RULE_NOT_FOUND", "QUALITY_TARGET_NOT_FOUND", "QUALITY_FEEDBACK_NOT_FOUND", "SNAPSHOT_NOT_FOUND"]:
        if code in error:
            return code
    return "CODE_QUALITY_ERROR"


def _quality_error_message(error: str) -> str:
    if "QUALITY_TARGET_NOT_FOUND" in error:
        return "Quality target was not found in persisted V2 project intelligence artifacts"
    if "QUALITY_FEEDBACK_NOT_FOUND" in error:
        return "No quality feedback records exist for this codebase"
    return _quality_error_code(error)
