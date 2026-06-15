"""MCP tools for V2.25-V2.30 architecture intent public contracts."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from .code_assets.architecture_intent.service import ArchitectureIntentService
from .code_assets.envelope import v2_error_envelope, v2_success_envelope


ARCHITECTURE_INTENT_TOOL_NAMES = {
    "knowledge_architecture_intent_build",
    "knowledge_architecture_intent_report",
    "knowledge_architecture_context_pack_v4",
    "knowledge_diagram_code_verification",
    "knowledge_architecture_proof_graph",
    "knowledge_architecture_intent_governance",
    "knowledge_architecture_intent_confirm",
    "knowledge_architecture_intent_revoke",
}


ARCHITECTURE_INTENT_TOOL_SPECS = [
    {
        "name": "knowledge_architecture_intent_build",
        "description": "Build V2.25-V2.30 architecture intent artifacts from real codebase snapshot and architecture documents",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}, "snapshot_id": {"type": "string"}, "mode": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_architecture_intent_report",
        "description": "Read the V2.30 Architecture Intent human review report",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_architecture_context_pack_v4",
        "description": "Read the V2.30 Architecture Context Pack v4",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_diagram_code_verification",
        "description": "Read the V2.29 diagram-to-code verification board",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_architecture_proof_graph",
        "description": "Read the V2.27 code proof graph for architecture intent evidence",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_architecture_intent_governance",
        "description": "Read V2.30 architecture intent governance overlay",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_architecture_intent_confirm",
        "description": "Confirm an architecture target as a read-time overlay fact",
        "inputSchema": {
            "type": "object",
            "properties": {
                "workspace_id": {"type": "string"},
                "codebase_id": {"type": "string"},
                "snapshot_id": {"type": "string"},
                "target_type": {"type": "string"},
                "target_id": {"type": "string"},
                "note": {"type": "string"},
                "reviewer": {"type": "string"},
            },
            "required": ["workspace_id", "codebase_id", "target_type", "target_id"],
        },
    },
    {
        "name": "knowledge_architecture_intent_revoke",
        "description": "Revoke a read-time overlay architecture confirmation",
        "inputSchema": {
            "type": "object",
            "properties": {
                "workspace_id": {"type": "string"},
                "codebase_id": {"type": "string"},
                "snapshot_id": {"type": "string"},
                "target_type": {"type": "string"},
                "target_id": {"type": "string"},
                "note": {"type": "string"},
                "reviewer": {"type": "string"},
            },
            "required": ["workspace_id", "codebase_id", "target_type", "target_id"],
        },
    },
]


def handle_architecture_intent_tool(
    name: str,
    arguments: dict[str, Any],
    *,
    blocked: Callable[..., dict[str, Any]],
    envelope: Callable[..., dict[str, Any]],
    ensure_workspace_meta: Callable[..., dict[str, Any]],
    resolve_workspace: Callable[[str | None, str | None], Path],
) -> dict[str, Any]:
    if name not in ARCHITECTURE_INTENT_TOOL_NAMES:
        raise ValueError(f"Unknown architecture intent tool: {name}")
    workspace_path = resolve_workspace(arguments.get("workspace_id"), None)
    meta = ensure_workspace_meta(workspace_path)
    workspace_id = str(meta["workspace_id"])
    codebase_id = str(arguments.get("codebase_id") or "").strip()
    if not codebase_id:
        return blocked(workspace_id=workspace_id, message="codebase_id is required", next_actions=["knowledge_codebase_list"], code="invalid_codebase_id")
    snapshot_id = str(arguments.get("snapshot_id") or "").strip() or None
    service = ArchitectureIntentService(workspace_path, workspace_id=workspace_id)
    try:
        if name == "knowledge_architecture_intent_build":
            payload = service.build_pipeline(codebase_id, snapshot_id=snapshot_id, mode=str(arguments.get("mode") or "architecture_review"))
            data = {"architecture_intent": payload}
            return envelope(workspace_id=workspace_id, artifact_refs=payload.get("artifact_refs", []), next_actions=payload.get("next_actions", []), data=_with_v2(workspace_id, codebase_id, payload.get("snapshot_id"), data, payload.get("artifact_refs", []), warnings=payload.get("warnings", []), next_actions=payload.get("next_actions", [])))
        if name == "knowledge_architecture_intent_report":
            payload = service.read_report(codebase_id)
            data = {"architecture_intent_report": payload}
            return _ok(envelope, workspace_id, codebase_id, payload, data)
        if name == "knowledge_architecture_context_pack_v4":
            payload = service.read_context_pack(codebase_id)
            data = {"architecture_context_pack_v4": payload}
            return _ok(envelope, workspace_id, codebase_id, payload, data)
        if name == "knowledge_diagram_code_verification":
            payload = service.read_verification(codebase_id)
            data = {"diagram_code_verification": payload}
            return _ok(envelope, workspace_id, codebase_id, payload, data)
        if name == "knowledge_architecture_proof_graph":
            payload = service.read_proof_graph(codebase_id)
            data = {"architecture_proof_graph": payload}
            return _ok(envelope, workspace_id, codebase_id, payload, data)
        if name == "knowledge_architecture_intent_governance":
            payload = service.read_governance(codebase_id)
            data = {"architecture_intent_governance": payload}
            return _ok(envelope, workspace_id, codebase_id, payload, data)
        if name == "knowledge_architecture_intent_confirm":
            payload = service.confirm(
                codebase_id,
                snapshot_id=snapshot_id,
                target_type=str(arguments.get("target_type") or ""),
                target_id=str(arguments.get("target_id") or ""),
                note=str(arguments.get("note") or ""),
                reviewer=str(arguments.get("reviewer") or "local"),
            )
            data = {"architecture_intent_governance": payload}
            return _ok(envelope, workspace_id, codebase_id, payload, data)
        payload = service.revoke(
            codebase_id,
            snapshot_id=snapshot_id,
            target_type=str(arguments.get("target_type") or ""),
            target_id=str(arguments.get("target_id") or ""),
            note=str(arguments.get("note") or ""),
            reviewer=str(arguments.get("reviewer") or "local"),
        )
        data = {"architecture_intent_governance": payload}
        return _ok(envelope, workspace_id, codebase_id, payload, data)
    except (FileNotFoundError, ValueError) as exc:
        return envelope(
            workspace_id=workspace_id,
            status="blocked",
            warnings=[str(exc)],
            next_actions=["knowledge_architecture_intent_build"],
            data={
                "error": {"code": str(exc), "message": str(exc), "retryable": False},
                "v2": v2_error_envelope(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, code=str(exc), message=str(exc)),
            },
        )


def _ok(envelope: Callable[..., dict[str, Any]], workspace_id: str, codebase_id: str, payload: dict[str, Any], data: dict[str, Any]) -> dict[str, Any]:
    return envelope(workspace_id=workspace_id, artifact_refs=payload.get("artifact_refs", []), data=_with_v2(workspace_id, codebase_id, payload.get("snapshot_id"), data, payload.get("artifact_refs", [])))


def _with_v2(workspace_id: str, codebase_id: str, snapshot_id: str | None, data: dict[str, Any], refs: list[dict[str, Any]], *, warnings: list[Any] | None = None, next_actions: list[str] | None = None) -> dict[str, Any]:
    payload = dict(data)
    payload["v2"] = v2_success_envelope(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, data=data, artifact_refs=refs, warnings=warnings, next_actions=next_actions)
    return payload
