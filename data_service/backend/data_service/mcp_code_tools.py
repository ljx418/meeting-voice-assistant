"""MCP tool schemas and handlers for V2 codebase assets."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from .code_assets.registry import CodebaseRegistry


CODE_TOOL_NAMES = {
    "knowledge_codebase_import",
}


CODE_TOOL_SPECS = [
    {
        "name": "knowledge_codebase_import",
        "description": "Import a local repository as a V2 codebase asset",
        "inputSchema": {
            "type": "object",
            "properties": {
                "workspace_id": {"type": "string"},
                "path": {"type": "string"},
                "codebase_id": {"type": "string"},
                "name": {"type": "string"},
                "metadata": {"type": "object"},
                "scan_policy": {"type": "object"},
            },
            "required": ["workspace_id", "path"],
        },
    },
]


def handle_code_tool(
    name: str,
    arguments: dict[str, Any],
    *,
    blocked: Callable[..., dict[str, Any]],
    envelope: Callable[..., dict[str, Any]],
    ensure_workspace_meta: Callable[..., dict[str, Any]],
    resolve_workspace: Callable[[str | None, str | None], Path],
) -> dict[str, Any]:
    if name != "knowledge_codebase_import":
        raise ValueError(f"Unknown code tool: {name}")

    workspace_path = resolve_workspace(arguments.get("workspace_id"), None)
    meta = ensure_workspace_meta(workspace_path)
    workspace_id = str(meta["workspace_id"])
    if meta.get("status") == "archived":
        return blocked(
            workspace_id=workspace_id,
            message="Workspace is archived and cannot import codebases",
            next_actions=["knowledge_workspace_describe"],
            code="workspace_archived",
        )

    path = str(arguments.get("path") or "").strip()
    if not path:
        return blocked(
            workspace_id=workspace_id,
            message="path is required",
            next_actions=["knowledge_codebase_import"],
            code="invalid_codebase_path",
        )

    registry = CodebaseRegistry(workspace_path, workspace_id=workspace_id)
    try:
        result = registry.import_codebase(
            path=path,
            codebase_id=arguments.get("codebase_id"),
            name=arguments.get("name"),
            metadata=dict(arguments.get("metadata") or {}),
            scan_policy=dict(arguments.get("scan_policy") or {}),
        )
    except ValueError as exc:
        return _blocked_from_error(blocked, envelope, workspace_id=workspace_id, error=str(exc))

    asset = result["asset"]
    return envelope(
        workspace_id=workspace_id,
        artifact_refs=[{"type": "codebase", "codebase_id": asset.codebase_id, "artifact_ref": f"codebase://{asset.codebase_id}"}],
        next_actions=["knowledge_codebase_snapshot", "knowledge_project_inventory"],
        data={"codebase": asset.public_dict(), "created": bool(result["created"])},
    )


def _blocked_from_error(
    blocked: Callable[..., dict[str, Any]],
    envelope: Callable[..., dict[str, Any]],
    *,
    workspace_id: str,
    error: str,
) -> dict[str, Any]:
    code = _error_code(error)
    if code == "path_not_allowed":
        return envelope(
            workspace_id=workspace_id,
            status="blocked",
            warnings=[_error_message(code, error)],
            next_actions=["knowledge_codebase_import"],
            data={"error": {"code": code, "message": _error_message(code, error), "retryable": False}},
        )
    return blocked(
        workspace_id=workspace_id,
        message=_error_message(code, error),
        next_actions=["knowledge_codebase_import"],
        code=code,
    )


def _error_code(error: str) -> str:
    if "outside allowed roots" in error.lower():
        return "path_not_allowed"
    if error in {"CODEBASE_PATH_NOT_FOUND", "CODEBASE_PATH_NOT_DIRECTORY", "CODEBASE_ID_CONFLICT"}:
        return error
    if "codebase_id" in error.lower():
        return "INVALID_CODEBASE_ID"
    return "CODEBASE_IMPORT_FAILED"


def _error_message(code: str, error: str) -> str:
    if code == "path_not_allowed":
        return error
    if code == "CODEBASE_PATH_NOT_FOUND":
        return "Codebase path does not exist"
    if code == "CODEBASE_PATH_NOT_DIRECTORY":
        return "Codebase path is not a directory"
    if code == "CODEBASE_ID_CONFLICT":
        return "codebase_id already exists for a different root path"
    if code == "INVALID_CODEBASE_ID":
        return error
    return error or "Codebase import failed"
