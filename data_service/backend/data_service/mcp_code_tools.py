"""MCP tool schemas and handlers for V2 codebase assets."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from .code_assets.registry import CodebaseRegistry
from .code_assets.snapshot import CodebaseSnapshotService, public_snapshot


CODE_TOOL_NAMES = {
    "knowledge_codebase_archive",
    "knowledge_codebase_describe",
    "knowledge_codebase_import",
    "knowledge_codebase_list",
    "knowledge_codebase_snapshot",
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
    {
        "name": "knowledge_codebase_list",
        "description": "List V2 codebase assets for a managed workspace",
        "inputSchema": {
            "type": "object",
            "properties": {
                "workspace_id": {"type": "string"},
                "include_archived": {"type": "boolean", "default": False},
                "limit": {"type": "integer", "default": 100},
            },
            "required": ["workspace_id"],
        },
    },
    {
        "name": "knowledge_codebase_snapshot",
        "description": "Generate a deterministic repo snapshot for an imported V2 codebase asset",
        "inputSchema": {
            "type": "object",
            "properties": {
                "workspace_id": {"type": "string"},
                "codebase_id": {"type": "string"},
                "scan_policy": {"type": "object"},
                "include_git": {"type": "boolean", "default": True},
            },
            "required": ["workspace_id", "codebase_id"],
        },
    },
    {
        "name": "knowledge_codebase_describe",
        "description": "Describe one V2 codebase asset",
        "inputSchema": {
            "type": "object",
            "properties": {
                "workspace_id": {"type": "string"},
                "codebase_id": {"type": "string"},
            },
            "required": ["workspace_id", "codebase_id"],
        },
    },
    {
        "name": "knowledge_codebase_archive",
        "description": "Archive one V2 codebase asset",
        "inputSchema": {
            "type": "object",
            "properties": {
                "workspace_id": {"type": "string"},
                "codebase_id": {"type": "string"},
                "reason": {"type": "string"},
            },
            "required": ["workspace_id", "codebase_id"],
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
    if name not in CODE_TOOL_NAMES:
        raise ValueError(f"Unknown code tool: {name}")

    workspace_path = resolve_workspace(arguments.get("workspace_id"), None)
    meta = ensure_workspace_meta(workspace_path)
    workspace_id = str(meta["workspace_id"])
    if meta.get("status") == "archived" and name in {"knowledge_codebase_import", "knowledge_codebase_archive"}:
        return blocked(
            workspace_id=workspace_id,
            message="Workspace is archived and cannot modify codebases",
            next_actions=["knowledge_workspace_describe"],
            code="workspace_archived",
        )

    registry = CodebaseRegistry(workspace_path, workspace_id=workspace_id)
    if name == "knowledge_codebase_list":
        try:
            limit = int(arguments.get("limit") if arguments.get("limit") is not None else 100)
        except (TypeError, ValueError):
            return blocked(
                workspace_id=workspace_id,
                message="limit must be an integer",
                next_actions=["knowledge_codebase_list"],
                code="invalid_limit",
            )
        limit = max(1, min(limit, 500))
        items = [
            asset.public_dict()
            for asset in registry.list_codebases(
                include_archived=bool(arguments.get("include_archived", False)),
                limit=limit,
            )
        ]
        return envelope(workspace_id=workspace_id, data={"items": items})

    if name == "knowledge_codebase_snapshot":
        codebase_id = str(arguments.get("codebase_id") or "").strip()
        if not codebase_id:
            return blocked(
                workspace_id=workspace_id,
                message="codebase_id is required",
                next_actions=["knowledge_codebase_list"],
                code="invalid_codebase_id",
            )
        scan_policy = arguments.get("scan_policy") or {}
        if not isinstance(scan_policy, dict):
            return blocked(
                workspace_id=workspace_id,
                message="scan_policy must be an object",
                next_actions=["knowledge_codebase_snapshot"],
                code="invalid_scan_policy",
            )
        service = CodebaseSnapshotService(workspace_path, workspace_id=workspace_id)
        try:
            result = service.create_snapshot(
                codebase_id,
                scan_policy=scan_policy,
                include_git=bool(arguments.get("include_git", True)),
            )
        except FileNotFoundError:
            return blocked(
                workspace_id=workspace_id,
                message="Unknown codebase_id",
                next_actions=["knowledge_codebase_list"],
                code="codebase_not_found",
            )
        except ValueError as exc:
            return blocked(
                workspace_id=workspace_id,
                message=_snapshot_error_message(str(exc)),
                next_actions=["knowledge_codebase_describe"],
                code=str(exc),
            )
        snapshot = public_snapshot(result["snapshot"])
        return envelope(
            workspace_id=workspace_id,
            artifact_refs=snapshot["artifact_refs"],
            next_actions=["knowledge_project_inventory", "knowledge_code_symbol_search"],
            data={"snapshot": snapshot},
        )

    if name == "knowledge_codebase_describe":
        codebase_id = str(arguments.get("codebase_id") or "").strip()
        if not codebase_id:
            return blocked(
                workspace_id=workspace_id,
                message="codebase_id is required",
                next_actions=["knowledge_codebase_list"],
                code="invalid_codebase_id",
            )
        try:
            asset = registry.describe(codebase_id)
        except FileNotFoundError:
            return blocked(
                workspace_id=workspace_id,
                message="Unknown codebase_id",
                next_actions=["knowledge_codebase_list"],
                code="codebase_not_found",
            )
        except ValueError as exc:
            return _blocked_from_error(blocked, envelope, workspace_id=workspace_id, error=str(exc))
        return envelope(workspace_id=workspace_id, data={"codebase": asset.public_dict()})

    if name == "knowledge_codebase_archive":
        codebase_id = str(arguments.get("codebase_id") or "").strip()
        if not codebase_id:
            return blocked(
                workspace_id=workspace_id,
                message="codebase_id is required",
                next_actions=["knowledge_codebase_list"],
                code="invalid_codebase_id",
            )
        try:
            asset = registry.archive(codebase_id, reason=str(arguments.get("reason") or ""))
        except FileNotFoundError:
            return blocked(
                workspace_id=workspace_id,
                message="Unknown codebase_id",
                next_actions=["knowledge_codebase_list"],
                code="codebase_not_found",
            )
        except ValueError as exc:
            return _blocked_from_error(blocked, envelope, workspace_id=workspace_id, error=str(exc))
        return envelope(workspace_id=workspace_id, data={"codebase": asset.public_dict()})

    path = str(arguments.get("path") or "").strip()
    if not path:
        return blocked(
            workspace_id=workspace_id,
            message="path is required",
            next_actions=["knowledge_codebase_import"],
            code="invalid_codebase_path",
        )

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
    if error == "CODEBASE_PATH_NOT_ALLOWED":
        return "path_not_allowed"
    if error in {"CODEBASE_PATH_NOT_FOUND", "CODEBASE_PATH_NOT_DIRECTORY", "CODEBASE_ID_CONFLICT"}:
        return error
    if "codebase_id" in error.lower():
        return "INVALID_CODEBASE_ID"
    return "CODEBASE_IMPORT_FAILED"


def _error_message(code: str, error: str) -> str:
    if code == "path_not_allowed":
        return "Codebase path is outside allowed roots"
    if code == "CODEBASE_PATH_NOT_FOUND":
        return "Codebase path does not exist"
    if code == "CODEBASE_PATH_NOT_DIRECTORY":
        return "Codebase path is not a directory"
    if code == "CODEBASE_ID_CONFLICT":
        return "codebase_id already exists for a different root path"
    if code == "INVALID_CODEBASE_ID":
        return error
    return error or "Codebase import failed"


def _snapshot_error_message(code: str) -> str:
    if code == "CODEBASE_NOT_ACTIVE":
        return "Codebase is not active"
    return code or "Codebase snapshot failed"
