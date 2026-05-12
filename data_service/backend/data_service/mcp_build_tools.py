"""Workspace build MCP tool schemas and handlers."""

from __future__ import annotations

import uuid
from pathlib import Path
from typing import Any, Callable


BUILD_MODES = ["full", "incremental", "graph_only", "llmwiki_only"]
TERMINAL_OPERATION_STATUSES = {"completed", "failed", "blocked", "cancelled"}

BUILD_TOOL_NAMES = {
    "knowledge_build_start",
    "knowledge_build_status",
    "knowledge_build_cancel",
}

BUILD_TOOL_SPECS = [
    {
        "name": "knowledge_build_start",
        "description": "Start a non-blocking managed workspace build operation",
        "inputSchema": {
            "type": "object",
            "properties": {
                "workspace_id": {"type": "string"},
                "mode": {"type": "string", "enum": BUILD_MODES},
            },
            "required": ["workspace_id"],
        },
    },
    {
        "name": "knowledge_build_status",
        "description": "Poll a managed workspace build operation",
        "inputSchema": {
            "type": "object",
            "properties": {
                "workspace_id": {"type": "string"},
                "operation_id": {"type": "string"},
            },
            "required": ["workspace_id", "operation_id"],
        },
    },
    {
        "name": "knowledge_build_cancel",
        "description": "Cancel a managed workspace build operation",
        "inputSchema": {
            "type": "object",
            "properties": {
                "workspace_id": {"type": "string"},
                "operation_id": {"type": "string"},
                "reason": {"type": "string"},
            },
            "required": ["workspace_id", "operation_id"],
        },
    },
]


def handle_build_tool(
    name: str,
    arguments: dict[str, Any],
    *,
    blocked: Callable[..., dict[str, Any]],
    ensure_build_worker: Callable[[Path], None],
    ensure_workspace_meta: Callable[..., dict[str, Any]],
    envelope: Callable[..., dict[str, Any]],
    now: Callable[[], str],
    operation_envelope: Callable[..., dict[str, Any]],
    operation_path: Callable[[Path, str], Path],
    read_json: Callable[[Path, Any], Any],
    resolve_workspace: Callable[[str | None, str | None], Path],
    write_json: Callable[[Path, Any], None],
) -> dict[str, Any]:
    if name == "knowledge_build_start":
        workspace_path = resolve_workspace(arguments.get("workspace_id"), None)
        meta = ensure_workspace_meta(workspace_path)
        if meta.get("status") == "archived":
            return envelope(
                workspace_id=meta["workspace_id"],
                status="blocked",
                warnings=["Workspace is archived and cannot start builds"],
                next_actions=["knowledge_workspace_describe"],
            )
        mode = str(arguments.get("mode") or "full")
        if mode not in BUILD_MODES:
            raise ValueError(f"mode must be one of: {', '.join(BUILD_MODES)}")
        operation_id = f"op_{uuid.uuid4().hex[:12]}"
        operation = {
            "operation_id": operation_id,
            "workspace_id": meta["workspace_id"],
            "mode": mode,
            "status": "queued",
            "stage": "queued",
            "progress": 0.0,
            "error": None,
            "retryable": True,
            "artifacts": [],
            "created_at": now(),
            "updated_at": now(),
        }
        write_json(operation_path(workspace_path, operation_id), operation)
        ensure_build_worker(workspace_path)
        return envelope(
            workspace_id=meta["workspace_id"],
            operation_id=operation_id,
            status="queued",
            artifact_refs=[{"type": "operation", "operation_id": operation_id}],
            next_actions=["knowledge_build_status"],
            data={"mode": mode, "stage": "queued", "progress": 0.0},
        )

    if name == "knowledge_build_status":
        workspace_path = resolve_workspace(arguments.get("workspace_id"), None)
        meta = ensure_workspace_meta(workspace_path)
        operation_id = str(arguments.get("operation_id") or "").strip()
        operation = read_json(operation_path(workspace_path, operation_id), None)
        if not operation:
            return blocked(
                workspace_id=meta["workspace_id"],
                operation_id=operation_id,
                message=f"Unknown operation_id: {operation_id}",
                next_actions=["knowledge_build_start"],
            )
        return operation_envelope(meta["workspace_id"], operation_id, operation)

    if name == "knowledge_build_cancel":
        workspace_path = resolve_workspace(arguments.get("workspace_id"), None)
        meta = ensure_workspace_meta(workspace_path)
        operation_id = str(arguments.get("operation_id") or "").strip()
        op_path = operation_path(workspace_path, operation_id)
        operation = read_json(op_path, None)
        if not operation:
            return blocked(
                workspace_id=meta["workspace_id"],
                operation_id=operation_id,
                message=f"Unknown operation_id: {operation_id}",
                next_actions=["knowledge_build_start"],
            )
        warnings = []
        if operation.get("status") in TERMINAL_OPERATION_STATUSES:
            warnings.append(f"Operation is already {operation.get('status')} and cannot be cancelled")
        else:
            if operation.get("status") == "queued":
                operation["status"] = "cancelled"
                operation["stage"] = "cancelled"
                operation["retryable"] = False
            else:
                operation["status"] = "cancelled"
                operation["stage"] = "cancelled"
                operation["retryable"] = False
                operation["cancel_requested"] = True
            operation["progress"] = operation.get("progress", 0.0)
            operation["cancel_reason"] = str(arguments.get("reason") or "")
            operation["updated_at"] = now()
            write_json(op_path, operation)
        return operation_envelope(meta["workspace_id"], operation_id, operation, warnings=warnings)

    raise ValueError(f"Unknown build MCP tool: {name}")
