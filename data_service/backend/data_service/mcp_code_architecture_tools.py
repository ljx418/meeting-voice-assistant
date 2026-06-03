"""MCP tools for V2.3 Architecture Abstraction."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from .code_assets.architecture.persistence import architecture_artifact_refs, code_architecture_artifact_refs
from .code_assets.architecture.service import ArchitectureService, public_architecture_payload, public_code_architecture_payload
from .code_assets.envelope import v2_error_envelope, v2_success_envelope


ARCHITECTURE_TOOL_NAMES = {
    "knowledge_architecture_sources_scan",
    "knowledge_architecture_model_build",
    "knowledge_architecture_model_read",
    "knowledge_architecture_alignment",
    "knowledge_architecture_findings",
    "knowledge_architecture_view",
    "knowledge_code_architecture_build",
    "knowledge_code_architecture_roles",
    "knowledge_code_architecture_patterns",
    "knowledge_code_architecture_view",
}


ARCHITECTURE_TOOL_SPECS = [
    {
        "name": "knowledge_architecture_sources_scan",
        "description": "Scan and build V2.3 architecture source index",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}, "snapshot_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_architecture_model_build",
        "description": "Build a V2.3 Architecture Model from architecture docs, Drawio/Mermaid, and V2.1 code artifacts",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}, "snapshot_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_architecture_model_read",
        "description": "Read the persisted V2.3 Architecture Model",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_architecture_alignment",
        "description": "Read V2.3 design-code alignment",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_architecture_findings",
        "description": "Read V2.3 architecture gap findings",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_architecture_view",
        "description": "Read V2.3 architecture view content",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}, "view_id": {"type": "string", "default": "architecture.html"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_architecture_build",
        "description": "Build V2.4 code-derived architecture roles and layers from accepted code artifacts",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}, "snapshot_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_architecture_roles",
        "description": "Read V2.4 code-derived architecture roles and layers",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_architecture_patterns",
        "description": "Read V2.4 code-derived architecture boundaries and pattern candidates",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_architecture_view",
        "description": "Read V2.4 code-derived architecture HTML or Mermaid view",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}, "view_id": {"type": "string", "default": "code_derived_architecture.html"}}, "required": ["workspace_id", "codebase_id"]},
    },
]


def handle_architecture_tool(name: str, arguments: dict[str, Any], *, blocked: Callable[..., dict[str, Any]], envelope: Callable[..., dict[str, Any]], ensure_workspace_meta: Callable[..., dict[str, Any]], resolve_workspace: Callable[[str | None, str | None], Path]) -> dict[str, Any]:
    if name not in ARCHITECTURE_TOOL_NAMES:
        raise ValueError(f"Unknown architecture tool: {name}")
    workspace_path = resolve_workspace(arguments.get("workspace_id"), None)
    meta = ensure_workspace_meta(workspace_path)
    workspace_id = str(meta["workspace_id"])
    codebase_id = str(arguments.get("codebase_id") or "").strip()
    if not codebase_id:
        return blocked(workspace_id=workspace_id, message="codebase_id is required", next_actions=["knowledge_codebase_list"], code="invalid_codebase_id")
    service = ArchitectureService(workspace_path, workspace_id=workspace_id)
    snapshot_id = str(arguments.get("snapshot_id") or "").strip() or None
    try:
        if name == "knowledge_code_architecture_build":
            payload = service.build_code_architecture(codebase_id, snapshot_id=snapshot_id)
            data = {"code_architecture": {"summary": payload["summary"]}}
            refs = code_architecture_artifact_refs(codebase_id)
            return envelope(workspace_id=workspace_id, artifact_refs=refs, next_actions=["knowledge_code_architecture_roles"], data=_with_v2(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=str(payload["snapshot_id"]), data=data, artifact_refs=refs))
        if name == "knowledge_code_architecture_roles":
            payload = public_code_architecture_payload(service.read_code_architecture(codebase_id))
            refs = code_architecture_artifact_refs(codebase_id)
            data = {"code_architecture": payload}
            return envelope(workspace_id=workspace_id, artifact_refs=refs, data=_with_v2(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=str(payload.get("snapshot_id") or ""), data=data, artifact_refs=refs))
        if name == "knowledge_code_architecture_patterns":
            payload = public_code_architecture_payload(service.read_code_architecture(codebase_id))
            refs = code_architecture_artifact_refs(codebase_id)
            data = {"patterns": payload.get("patterns", []), "boundaries": payload.get("boundaries", []), "summary": payload.get("summary", {})}
            return envelope(workspace_id=workspace_id, artifact_refs=refs, data=_with_v2(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=str(payload.get("snapshot_id") or ""), data=data, artifact_refs=refs))
        if name == "knowledge_code_architecture_view":
            view = service.read_code_view(codebase_id, str(arguments.get("view_id") or "code_derived_architecture.html"))
            refs = code_architecture_artifact_refs(codebase_id)
            data = {"view": view}
            return envelope(workspace_id=workspace_id, artifact_refs=refs, data=_with_v2(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=str(view["snapshot_id"]), data=data, artifact_refs=refs))
        if name in {"knowledge_architecture_model_build", "knowledge_architecture_sources_scan"}:
            bundle = service.build_architecture(codebase_id, snapshot_id=snapshot_id)
            data = {"architecture": {"summary": bundle["summary"]}}
            return envelope(workspace_id=workspace_id, artifact_refs=architecture_artifact_refs(codebase_id), next_actions=["knowledge_architecture_model_read", "knowledge_architecture_findings"], data=_with_v2(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=str(bundle["summary"]["snapshot_id"]), data=data, artifact_refs=architecture_artifact_refs(codebase_id)))
        if name == "knowledge_architecture_view":
            view = service.read_view(codebase_id, str(arguments.get("view_id") or "architecture.html"))
            data = {"view": view}
            return envelope(workspace_id=workspace_id, artifact_refs=architecture_artifact_refs(codebase_id), data=_with_v2(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=str(view["snapshot_id"]), data=data, artifact_refs=architecture_artifact_refs(codebase_id)))
        bundle = service.read_architecture(codebase_id)
        payload = public_architecture_payload(bundle)
        data = {"architecture": payload}
        if name == "knowledge_architecture_alignment":
            data = {"alignment": payload["alignment"]}
        if name == "knowledge_architecture_findings":
            data = {"findings": payload["findings"], "summary": payload["summary"]}
        return envelope(workspace_id=workspace_id, artifact_refs=architecture_artifact_refs(codebase_id), data=_with_v2(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=str(bundle["model"]["snapshot_id"]), data=data, artifact_refs=architecture_artifact_refs(codebase_id)))
    except FileNotFoundError as exc:
        return _blocked_v2(envelope, workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, code=_architecture_error_code(str(exc)), message=_architecture_error_message(str(exc)), next_actions=["knowledge_codebase_snapshot", "knowledge_code_graph_build", "knowledge_architecture_model_build"])
    except ValueError as exc:
        return _blocked_v2(envelope, workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, code=str(exc), message=str(exc), next_actions=["knowledge_architecture_model_build"])


def _with_v2(*, workspace_id: str, data: dict[str, Any], codebase_id: str, snapshot_id: str | None, artifact_refs: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    payload = dict(data)
    payload["v2"] = v2_success_envelope(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, data=data, artifact_refs=artifact_refs)
    return payload


def _blocked_v2(envelope: Callable[..., dict[str, Any]], *, workspace_id: str, codebase_id: str, snapshot_id: str | None, code: str, message: str, next_actions: list[str] | None = None) -> dict[str, Any]:
    return envelope(workspace_id=workspace_id, status="blocked", warnings=[message], next_actions=next_actions, data={"error": {"code": code, "message": message, "retryable": False}, "v2": v2_error_envelope(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, code=code, message=message, next_actions=next_actions)})


def _architecture_error_code(error: str) -> str:
    if "ARCHITECTURE_SOURCE_NOT_FOUND" in error:
        return "ARCHITECTURE_SOURCE_NOT_FOUND"
    if "ARCHITECTURE_MODEL_NOT_BUILT" in error:
        return "ARCHITECTURE_MODEL_NOT_BUILT"
    if "CODE_ARCHITECTURE_NOT_BUILT" in error:
        return "CODE_ARCHITECTURE_NOT_BUILT"
    if "INVENTORY_NOT_FOUND" in error:
        return "INVENTORY_NOT_FOUND"
    if "SYMBOL_INDEX_NOT_FOUND" in error:
        return "SYMBOL_INDEX_NOT_FOUND"
    if "DRAWIO_PARSE_FAILED" in error:
        return "DRAWIO_PARSE_FAILED"
    if "SNAPSHOT_NOT_FOUND" in error:
        return "SNAPSHOT_NOT_FOUND"
    return "ARCHITECTURE_ERROR"


def _architecture_error_message(error: str) -> str:
    code = _architecture_error_code(error)
    if code == "ARCHITECTURE_SOURCE_NOT_FOUND":
        return "No architecture source was found in the codebase snapshot"
    if code == "ARCHITECTURE_MODEL_NOT_BUILT":
        return "Architecture Model has not been built"
    if code == "CODE_ARCHITECTURE_NOT_BUILT":
        return "Code-derived Architecture Model has not been built"
    if code == "INVENTORY_NOT_FOUND":
        return "Public surface inventory has not been built"
    if code == "SYMBOL_INDEX_NOT_FOUND":
        return "Python symbol index has not been built"
    return error or "Architecture request failed"
