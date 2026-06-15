"""MCP tools for V2.37 document-grounded architecture reconstruction."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from .code_assets.doc_grounded_architecture.service import DocGroundedArchitectureService
from .code_assets.envelope import v2_error_envelope, v2_success_envelope


DOC_GROUNDED_ARCHITECTURE_TOOL_NAMES = {
    "knowledge_code_doc_grounded_architecture_build",
    "knowledge_code_doc_grounded_architecture_report",
    "knowledge_code_doc_grounded_verification",
    "knowledge_code_doc_grounded_architecture_brief",
}


DOC_GROUNDED_ARCHITECTURE_TOOL_SPECS = [
    {
        "name": "knowledge_code_doc_grounded_architecture_build",
        "description": "Build V2.37 document-grounded target/current/diff architecture artifacts",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}, "snapshot_id": {"type": "string"}, "mode": {"type": "string"}, "max_tokens": {"type": "integer", "default": 12000}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_doc_grounded_architecture_report",
        "description": "Read the V2.37 document-grounded architecture reconstruction report",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_doc_grounded_verification",
        "description": "Read V2.37 claim-to-code verification rows",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_doc_grounded_architecture_brief",
        "description": "Create a V2.37 evidence-backed architecture brief for agents",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}, "mode": {"type": "string"}, "role": {"type": "string"}, "max_tokens": {"type": "integer", "default": 12000}}, "required": ["workspace_id", "codebase_id"]},
    },
]


def handle_doc_grounded_architecture_tool(
    name: str,
    arguments: dict[str, Any],
    *,
    blocked: Callable[..., dict[str, Any]],
    envelope: Callable[..., dict[str, Any]],
    ensure_workspace_meta: Callable[..., dict[str, Any]],
    resolve_workspace: Callable[[str | None, str | None], Path],
) -> dict[str, Any]:
    if name not in DOC_GROUNDED_ARCHITECTURE_TOOL_NAMES:
        raise ValueError(f"Unknown doc-grounded architecture tool: {name}")
    workspace_path = resolve_workspace(arguments.get("workspace_id"), None)
    meta = ensure_workspace_meta(workspace_path)
    workspace_id = str(meta["workspace_id"])
    codebase_id = str(arguments.get("codebase_id") or "").strip()
    if not codebase_id:
        return blocked(workspace_id=workspace_id, message="codebase_id is required", next_actions=["knowledge_codebase_list"], code="invalid_codebase_id")
    service = DocGroundedArchitectureService(workspace_path, workspace_id=workspace_id)
    snapshot_id = str(arguments.get("snapshot_id") or "").strip() or None
    try:
        if name == "knowledge_code_doc_grounded_architecture_build":
            payload = service.build_pipeline(
                codebase_id,
                snapshot_id=snapshot_id,
                mode=str(arguments.get("mode") or "architecture_review"),
                max_tokens=int(arguments.get("max_tokens") or 12000),
            )
            data = {"doc_grounded_architecture": payload}
            return _ok(envelope, workspace_id, codebase_id, payload, data)
        if name == "knowledge_code_doc_grounded_architecture_report":
            payload = service.read_reconstruction_report(codebase_id)
            data = {"doc_grounded_architecture_report": payload}
            return _ok(envelope, workspace_id, codebase_id, payload, data)
        if name == "knowledge_code_doc_grounded_verification":
            payload = service.read_verification(codebase_id)
            data = {"doc_grounded_verification": payload}
            return _ok(envelope, workspace_id, codebase_id, payload, data)
        payload = service.create_agent_brief(
            codebase_id,
            mode=str(arguments.get("mode") or "architecture_review"),
            role=str(arguments.get("role") or "coding_agent"),
            max_tokens=int(arguments.get("max_tokens") or 12000),
        )
        data = {"doc_grounded_architecture_brief": payload}
        return _ok(envelope, workspace_id, codebase_id, payload, data)
    except (FileNotFoundError, ValueError) as exc:
        return envelope(
            workspace_id=workspace_id,
            status="blocked",
            warnings=[str(exc)],
            next_actions=["knowledge_code_doc_grounded_architecture_build"],
            data={
                "error": {"code": str(exc), "message": str(exc), "retryable": False},
                "v2": v2_error_envelope(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, code=str(exc), message=str(exc)),
            },
        )


def _ok(envelope: Callable[..., dict[str, Any]], workspace_id: str, codebase_id: str, payload: dict[str, Any], data: dict[str, Any]) -> dict[str, Any]:
    return envelope(workspace_id=workspace_id, artifact_refs=payload.get("artifact_refs", []), warnings=payload.get("warnings", []), data=_with_v2(workspace_id, codebase_id, payload.get("snapshot_id"), data, payload.get("artifact_refs", []), warnings=payload.get("warnings", []), unresolved=payload.get("unresolved", []), next_actions=payload.get("next_actions", [])))


def _with_v2(workspace_id: str, codebase_id: str, snapshot_id: str | None, data: dict[str, Any], refs: list[dict[str, Any]], *, warnings: list[Any] | None = None, unresolved: list[Any] | None = None, next_actions: list[str] | None = None) -> dict[str, Any]:
    payload = dict(data)
    payload["v2"] = v2_success_envelope(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, data=data, artifact_refs=refs, warnings=warnings, unresolved=unresolved, next_actions=next_actions)
    return payload
