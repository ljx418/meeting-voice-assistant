"""MCP server for the local knowledge governance service.

The server name remains `data_service` for compatibility with existing MCP
clients. The service boundary is MCP-first and workspace-scoped.
"""

from __future__ import annotations

import json
import os
import hashlib
import re
import shutil
import threading
import time
import traceback
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, List

try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Resource, TextContent, TextResourceContents, Tool
    _MCP_IMPORT_ERROR = None
except ModuleNotFoundError as exc:  # pragma: no cover - environment dependent
    Server = None  # type: ignore[assignment]
    stdio_server = None  # type: ignore[assignment]
    Resource = TextContent = TextResourceContents = Tool = object  # type: ignore[assignment]
    _MCP_IMPORT_ERROR = exc

from .models import QueryMode
from .service import DataService
from .security import validate_source_paths, validate_workspace_path
from .session_service import (
    SESSION_BUILD_MODES,
    SESSION_TERMINAL_STATUSES,
    SessionKnowledgeService,
    normalize_workspace_arg,
)


if Server is None:  # pragma: no cover - environment dependent
    raise RuntimeError("The `mcp` package is required to run data_service.mcp_stdio") from _MCP_IMPORT_ERROR

server = Server("data_service")
_workspace = validate_workspace_path(os.getenv("DATA_SERVICE_WORKSPACE", Path.cwd()))
_RULE_STATUSES = ["draft", "approved", "rejected", "archived", "revoked"]
_BUILD_MODES = ["full", "incremental", "graph_only", "llmwiki_only"]
_SESSION_BUILD_MODES = sorted(SESSION_BUILD_MODES)
_SOURCE_STATUSES = ["active", "removed", "duplicate", "blocked"]
_MAX_IMPORT_FILES = 50
_MAX_IMPORT_FILE_BYTES = 10 * 1024 * 1024
_MAX_IMPORT_TEXT_BYTES = 2 * 1024 * 1024
_TERMINAL_OPERATION_STATUSES = {"completed", "failed", "blocked", "cancelled"}
_V2_TOOL_MAP = {
    "knowledge_ingest_v2": "knowledge_ingest",
    "knowledge_query_v2": "knowledge_query",
    "knowledge_quality_summary_v2": "knowledge_quality_summary",
    "knowledge_correction_plan_v2": "knowledge_correction_plan",
    "knowledge_quality_feedback_v2": "knowledge_quality_feedback",
    "knowledge_correction_rules_v2": "knowledge_correction_rules",
    "knowledge_review_correction_rule_v2": "knowledge_review_correction_rule",
}
_BUILD_WORKERS: set[str] = set()
_BUILD_WORKERS_LOCK = threading.Lock()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _bounded_int(value: object, *, default: int, minimum: int, maximum: int, field: str) -> int:
    try:
        parsed = int(value if value is not None else default)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field} must be an integer") from exc
    if parsed < minimum or parsed > maximum:
        raise ValueError(f"{field} must be between {minimum} and {maximum}")
    return parsed


def _slug(value: object) -> str:
    text = re.sub(r"[^A-Za-z0-9._-]+", "-", str(value or "").strip().lower()).strip("-")
    return text[:48] or "workspace"


def _workspace_root() -> Path:
    configured = os.getenv("DATA_SERVICE_WORKSPACE_ROOT", "").strip()
    root = Path(configured).expanduser() if configured else _workspace.parent
    resolved = validate_workspace_path(root)
    resolved.mkdir(parents=True, exist_ok=True)
    return resolved


def _workspace_meta_path(workspace: Path) -> Path:
    return workspace / ".data_service_workspace.json"


def _lifecycle_dir(workspace: Path) -> Path:
    return workspace / "lifecycle"


def _sources_manifest_path(workspace: Path) -> Path:
    return _lifecycle_dir(workspace) / "sources.json"


def _operations_dir(workspace: Path) -> Path:
    return _lifecycle_dir(workspace) / "operations"


def _operation_path(workspace: Path, operation_id: str) -> Path:
    return _operations_dir(workspace) / f"{operation_id}.json"


def _read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return default


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _active_source_paths(workspace: Path) -> list[str]:
    manifest = _read_json(_sources_manifest_path(workspace), {"items": []})
    paths: list[str] = []
    for item in manifest.get("items", []):
        if item.get("status", "active") != "active":
            continue
        path = item.get("path")
        if path:
            paths.append(str(path))
    return paths


def _update_source_ingest_status(workspace: Path, status: str) -> None:
    manifest_path = _sources_manifest_path(workspace)
    manifest = _read_json(manifest_path, {"items": []})
    changed = False
    for item in manifest.get("items", []):
        if item.get("status", "active") == "active":
            item["ingest_status"] = status
            item["ingest_updated_at"] = _now()
            changed = True
    if changed:
        _write_json(manifest_path, manifest)


def _update_operation(workspace: Path, operation_id: str, **updates: Any) -> dict:
    operation_path = _operation_path(workspace, operation_id)
    operation = _read_json(operation_path, {})
    operation.update(updates)
    operation["updated_at"] = _now()
    _write_json(operation_path, operation)
    return operation


def _operation_payload(operation: dict) -> dict:
    return {
        "mode": operation.get("mode"),
        "stage": operation.get("stage"),
        "progress": operation.get("progress", 0.0),
        "error": operation.get("error"),
        "retryable": operation.get("retryable", True),
        "artifacts": operation.get("artifacts", []),
    }


def _operation_envelope(
    workspace_id: str,
    operation_id: str,
    operation: dict,
    *,
    warnings: list[str] | None = None,
    next_actions: list[str] | None = None,
) -> dict:
    status = operation.get("status", "queued")
    if next_actions is None:
        next_actions = ["knowledge_build_status"]
        if status not in _TERMINAL_OPERATION_STATUSES:
            next_actions.append("knowledge_build_cancel")
    return _envelope(
        workspace_id=workspace_id,
        operation_id=operation_id,
        status=status,
        warnings=warnings,
        artifact_refs=operation.get("artifacts", []),
        next_actions=next_actions,
        data=_operation_payload(operation),
    )


def _blocked(
    *,
    workspace_id: str,
    message: str,
    operation_id: str | None = None,
    next_actions: list[str] | None = None,
    data: dict | None = None,
) -> dict:
    return _envelope(
        workspace_id=workspace_id,
        operation_id=operation_id,
        status="blocked",
        warnings=[message],
        next_actions=next_actions,
        data=data or {"error": {"message": message, "retryable": False}},
    )


def _operation_cancel_requested(workspace: Path, operation_id: str) -> bool:
    operation = _read_json(_operation_path(workspace, operation_id), {})
    return bool(operation.get("cancel_requested")) or operation.get("status") == "cancelled"


def _raise_if_cancelled(workspace: Path, operation_id: str) -> None:
    if _operation_cancel_requested(workspace, operation_id):
        _update_operation(
            workspace,
            operation_id,
            status="cancelled",
            stage="cancelled",
            retryable=False,
            error=None,
        )
        raise _BuildCancelled()


class _BuildCancelled(Exception):
    """Internal sentinel used to stop a build at stage boundaries."""


def _run_build_operation(workspace: Path, operation_id: str) -> None:
    operation = _read_json(_operation_path(workspace, operation_id), {})
    mode = operation.get("mode", "full")
    try:
        _update_operation(workspace, operation_id, status="running", stage="source_import", progress=0.05)
        _raise_if_cancelled(workspace, operation_id)
        source_paths = _active_source_paths(workspace)
        if not source_paths:
            _update_operation(
                workspace,
                operation_id,
                status="blocked",
                stage="failed",
                progress=0.0,
                error={"message": "No active sources imported for workspace", "stage": "source_import"},
                retryable=True,
            )
            return

        include_llmwiki = mode in ("full", "incremental", "llmwiki_only")
        include_graphrag = mode in ("full", "incremental", "graph_only")
        service = DataService(workspace)
        plan = service.build_ingest_plan(
            source_paths,
            include_llmwiki=include_llmwiki,
            include_graphrag=include_graphrag,
        )
        service.write_summary_files(plan)
        _update_operation(workspace, operation_id, stage="distill", progress=0.25)
        _raise_if_cancelled(workspace, operation_id)
        units = service.build_distilled_units(plan)
        artifacts: list[str] = []
        if include_llmwiki:
            _update_operation(workspace, operation_id, stage="llmwiki", progress=0.45)
        elif include_graphrag:
            _update_operation(workspace, operation_id, stage="graphrag", progress=0.45)
        _raise_if_cancelled(workspace, operation_id)
        results = service.run_default_pipeline(plan, distilled_units=units)
        service.write_summary_files(plan)
        for result in results:
            artifacts.extend(str(item) for item in result.artifacts)
        _update_operation(workspace, operation_id, stage="quality_plan", progress=0.9, artifacts=artifacts)
        _update_source_ingest_status(workspace, "built")
        _update_operation(
            workspace,
            operation_id,
            status="completed",
            stage="completed",
            progress=1.0,
            retryable=False,
            artifacts=artifacts,
            results=[
                {"engine": result.engine, "status": result.status, "meta": result.meta}
                for result in results
            ],
        )
    except _BuildCancelled:
        return
    except Exception as exc:  # pragma: no cover - defensive operation recording
        _update_source_ingest_status(workspace, "failed")
        _update_operation(
            workspace,
            operation_id,
            status="failed",
            stage="failed",
            error={
                "message": str(exc),
                "type": exc.__class__.__name__,
                "traceback": traceback.format_exc(limit=6),
            },
            retryable=True,
        )


def _mark_interrupted_running_operations(workspace: Path) -> None:
    for operation_file in _operations_dir(workspace).glob("*.json"):
        operation = _read_json(operation_file, {})
        if operation.get("status") != "running":
            continue
        _update_operation(
            workspace,
            str(operation.get("operation_id") or operation_file.stem),
            status="failed",
            stage="failed",
            error={
                "message": "MCP server stopped while this build was running",
                "type": "server_interrupted",
            },
            retryable=True,
        )


def _workspace_worker_key(workspace: Path) -> str:
    return str(workspace.resolve())


def _next_queued_operation(workspace: Path) -> dict | None:
    operation_files = sorted(
        _operations_dir(workspace).glob("*.json"),
        key=lambda item: (_read_json(item, {}).get("created_at", ""), item.name),
    )
    for operation_file in operation_files:
        operation = _read_json(operation_file, {})
        if operation.get("status") == "queued":
            return operation
    return None


def _run_build_queue(workspace: Path) -> None:
    try:
        while True:
            operation = _next_queued_operation(workspace)
            if not operation:
                return
            operation_id = str(operation.get("operation_id") or "")
            if not operation_id:
                return
            if operation.get("cancel_requested"):
                _update_operation(
                    workspace,
                    operation_id,
                    status="cancelled",
                    stage="cancelled",
                    retryable=False,
                    error=None,
                )
                continue
            _run_build_operation(workspace, operation_id)
            time.sleep(0.01)
    finally:
        with _BUILD_WORKERS_LOCK:
            _BUILD_WORKERS.discard(_workspace_worker_key(workspace))
        if _next_queued_operation(workspace):
            _ensure_build_worker(workspace)


def _ensure_build_worker(workspace: Path) -> None:
    key = _workspace_worker_key(workspace)
    with _BUILD_WORKERS_LOCK:
        if key in _BUILD_WORKERS:
            return
        _BUILD_WORKERS.add(key)
    _mark_interrupted_running_operations(workspace)
    threading.Thread(target=_run_build_queue, args=(workspace,), daemon=True).start()


def _workspace_id_for_path(path: Path) -> str:
    meta = _read_json(_workspace_meta_path(path), {})
    if meta.get("workspace_id"):
        return str(meta["workspace_id"])
    return path.name


def _resolve_workspace(identifier: str | None = None, workspace: str | None = None) -> Path:
    if workspace:
        return validate_workspace_path(workspace)
    if identifier:
        root = _workspace_root()
        candidate = validate_workspace_path(root / str(identifier))
        try:
            candidate.relative_to(root)
        except ValueError as exc:
            raise ValueError("workspace_id is outside DATA_SERVICE_WORKSPACE_ROOT") from exc
        return candidate
    raise ValueError("workspace_id or workspace is required")


def _ensure_workspace_meta(workspace: Path, *, name: str | None = None, owner: str | None = None, tags: list[str] | None = None) -> dict:
    workspace.mkdir(parents=True, exist_ok=True)
    service = DataService(workspace)
    service.ensure_layout()
    meta_path = _workspace_meta_path(workspace)
    existing = _read_json(meta_path, {})
    now = _now()
    meta = {
        "workspace_id": existing.get("workspace_id") or _workspace_id_for_path(workspace),
        "name": name or existing.get("name") or workspace.name,
        "workspace_path": str(workspace),
        "owner": owner if owner is not None else existing.get("owner"),
        "tags": list(tags if tags is not None else existing.get("tags", [])),
        "status": existing.get("status", "active"),
        "created_at": existing.get("created_at", now),
        "updated_at": now,
    }
    _write_json(meta_path, meta)
    return meta


def _envelope(
    *,
    workspace_id: str,
    status: str = "ok",
    operation_id: str | None = None,
    warnings: list[str] | None = None,
    artifact_refs: list[Any] | None = None,
    next_actions: list[str] | None = None,
    data: dict | None = None,
) -> dict:
    return {
        "workspace_id": workspace_id,
        "operation_id": operation_id,
        "status": status,
        "warnings": list(warnings or []),
        "artifact_refs": list(artifact_refs or []),
        "next_actions": list(next_actions or []),
        "data": data or {},
    }


def _service(workspace: str | None = None, workspace_id: str | None = None) -> DataService:
    if workspace or workspace_id:
        return DataService(_resolve_workspace(workspace_id, workspace))
    return DataService(_workspace)


def _session_service(service: DataService) -> SessionKnowledgeService:
    return SessionKnowledgeService(service.workspace, workspace_id=_workspace_id_for_service(service))


def _session_operation_payload(operation: dict) -> dict:
    return {
        "mode": operation.get("mode"),
        "stage": operation.get("stage"),
        "progress": operation.get("progress", 0.0),
        "error": operation.get("error"),
        "retryable": operation.get("retryable", True),
        "artifacts": operation.get("artifacts", []),
        "results": operation.get("results", {}),
    }


def _session_operation_envelope(
    workspace_id: str,
    session_id: str,
    operation_id: str,
    operation: dict,
    *,
    warnings: list[str] | None = None,
) -> dict:
    status = operation.get("status", "queued")
    next_actions = ["knowledge_session_build_status"]
    if status not in SESSION_TERMINAL_STATUSES:
        next_actions.append("knowledge_session_build_cancel")
    return _envelope(
        workspace_id=workspace_id,
        operation_id=operation_id,
        status=status,
        warnings=warnings,
        artifact_refs=operation.get("artifacts", []),
        next_actions=next_actions,
        data={"session_id": session_id, **_session_operation_payload(operation)},
    )


def _json_content(payload: dict) -> List[TextContent]:
    return [TextContent(type="text", text=json.dumps(payload, ensure_ascii=False, indent=2))]


def _workspace_id_for_service(service: DataService) -> str:
    return _workspace_id_for_path(service.workspace)


def _is_workspace_archived(workspace: Path) -> bool:
    meta = _read_json(_workspace_meta_path(workspace), {})
    return meta.get("status") == "archived"


def _layout_payload(service: DataService) -> dict:
    layout = service.layout
    return {
        "workspace": str(layout.workspace),
        "row_manifest": str(layout.row_manifest),
        "llmwiki": {
            "raw": str(layout.raw_dir),
            "readable": str(layout.readable_dir),
            "normalized": str(layout.normalized_dir),
            "pages": str(layout.llmwiki_pages_dir),
            "state": str(layout.llmwiki_state_dir),
        },
        "graphrag": {
            "input": str(layout.graphrag_input_dir),
            "cache": str(layout.graphrag_cache_dir),
            "state": str(layout.graphrag_state_dir),
        },
        "summary": str(layout.summary_dir),
        "quality": str(layout.quality_dir),
    }


@server.list_resources()
async def list_resources() -> List[Resource]:
    return [
        Resource(
            uri="data_service://summary",
            name="Workspace Summary",
            description="Current data_service summary for the active workspace",
            mimeType="text/markdown",
        ),
        Resource(
            uri="data_service://layout",
            name="Workspace Layout",
            description="Artifact layout for row, llmwiki, graphrag, and summary layers",
            mimeType="application/json",
        ),
    ]


@server.read_resource()
async def read_resource(uri: str) -> TextResourceContents:
    service = _service()
    if uri == "data_service://summary":
        plan = service.build_ingest_plan([])
        service.write_summary_files(plan)
        return TextResourceContents(uri=uri, mimeType="text/markdown", text=service.layout.summary_md.read_text(encoding="utf-8"))
    if uri == "data_service://layout":
        payload = _layout_payload(service)
        return TextResourceContents(uri=uri, mimeType="application/json", text=json.dumps(payload, ensure_ascii=False, indent=2))
    raise ValueError(f"Unknown resource: {uri}")


@server.list_tools()
async def list_tools() -> List[Tool]:
    return [
        Tool(
            name="knowledge_ingest",
            description="Ingest files once and fan out to llmwiki and graphrag",
            inputSchema={
                "type": "object",
                "properties": {
                    "paths": {"type": "array", "items": {"type": "string"}},
                    "workspace": {"type": "string"},
                    "workspace_id": {"type": "string"},
                },
                "required": ["paths"],
            },
        ),
        Tool(
            name="knowledge_query",
            description="Query llmwiki, graphrag, or hybrid mode",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "mode": {"type": "string", "enum": [mode.value for mode in QueryMode]},
                    "top_k": {"type": "integer", "default": 8},
                    "workspace": {"type": "string"},
                    "workspace_id": {"type": "string"},
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="knowledge_quality_summary",
            description="Read quality governance summary, recent feedback, correction rules, and approved correction plan",
            inputSchema={
                "type": "object",
                "properties": {
                    "workspace": {"type": "string"},
                    "workspace_id": {"type": "string"},
                },
            },
        ),
        Tool(
            name="knowledge_correction_plan",
            description="Read or rebuild the approved quality correction plan with action impact scopes",
            inputSchema={
                "type": "object",
                "properties": {
                    "workspace": {"type": "string"},
                    "workspace_id": {"type": "string"},
                    "rebuild": {"type": "boolean", "default": False},
                },
            },
        ),
        Tool(
            name="knowledge_quality_feedback",
            description="Submit controlled quality feedback without mutating source data",
            inputSchema={
                "type": "object",
                "properties": {
                    "workspace": {"type": "string"},
                    "workspace_id": {"type": "string"},
                    "target_type": {"type": "string"},
                    "target_id": {"type": "string"},
                    "action": {"type": "string"},
                    "label": {"type": "string"},
                    "suggested_value": {"type": "string"},
                    "reason": {"type": "string"},
                    "metadata": {"type": "object"},
                },
                "required": ["target_type", "target_id", "action"],
            },
        ),
        Tool(
            name="knowledge_correction_rules",
            description="List quality correction rules, optionally filtered by review status",
            inputSchema={
                "type": "object",
                "properties": {
                    "workspace": {"type": "string"},
                    "workspace_id": {"type": "string"},
                    "limit": {"type": "integer", "default": 100},
                    "status": {"type": "string", "enum": _RULE_STATUSES},
                },
            },
        ),
        Tool(
            name="knowledge_review_correction_rule",
            description="Review one quality correction rule and refresh the approved correction plan",
            inputSchema={
                "type": "object",
                "properties": {
                    "workspace": {"type": "string"},
                    "workspace_id": {"type": "string"},
                    "rule_id": {"type": "string"},
                    "status": {"type": "string", "enum": _RULE_STATUSES},
                    "reviewer": {"type": "string"},
                    "note": {"type": "string"},
                },
                "required": ["rule_id", "status"],
            },
        ),
        Tool(
            name="knowledge_ingest_v2",
            description="Envelope-wrapped knowledge_ingest for external MCP clients",
            inputSchema={
                "type": "object",
                "properties": {
                    "paths": {"type": "array", "items": {"type": "string"}},
                    "workspace": {"type": "string"},
                    "workspace_id": {"type": "string"},
                },
                "required": ["paths"],
            },
        ),
        Tool(
            name="knowledge_query_v2",
            description="Envelope-wrapped knowledge_query for external MCP clients",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "mode": {"type": "string", "enum": [mode.value for mode in QueryMode]},
                    "top_k": {"type": "integer", "default": 8},
                    "workspace": {"type": "string"},
                    "workspace_id": {"type": "string"},
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="knowledge_quality_summary_v2",
            description="Envelope-wrapped knowledge_quality_summary for external MCP clients",
            inputSchema={
                "type": "object",
                "properties": {
                    "workspace": {"type": "string"},
                    "workspace_id": {"type": "string"},
                },
            },
        ),
        Tool(
            name="knowledge_correction_plan_v2",
            description="Envelope-wrapped knowledge_correction_plan for external MCP clients",
            inputSchema={
                "type": "object",
                "properties": {
                    "workspace": {"type": "string"},
                    "workspace_id": {"type": "string"},
                    "rebuild": {"type": "boolean", "default": False},
                },
            },
        ),
        Tool(
            name="knowledge_quality_feedback_v2",
            description="Envelope-wrapped knowledge_quality_feedback for external MCP clients",
            inputSchema={
                "type": "object",
                "properties": {
                    "workspace": {"type": "string"},
                    "workspace_id": {"type": "string"},
                    "target_type": {"type": "string"},
                    "target_id": {"type": "string"},
                    "action": {"type": "string"},
                    "label": {"type": "string"},
                    "suggested_value": {"type": "string"},
                    "reason": {"type": "string"},
                    "metadata": {"type": "object"},
                },
                "required": ["target_type", "target_id", "action"],
            },
        ),
        Tool(
            name="knowledge_correction_rules_v2",
            description="Envelope-wrapped knowledge_correction_rules for external MCP clients",
            inputSchema={
                "type": "object",
                "properties": {
                    "workspace": {"type": "string"},
                    "workspace_id": {"type": "string"},
                    "limit": {"type": "integer", "default": 100},
                    "status": {"type": "string", "enum": _RULE_STATUSES},
                },
            },
        ),
        Tool(
            name="knowledge_review_correction_rule_v2",
            description="Envelope-wrapped knowledge_review_correction_rule for external MCP clients",
            inputSchema={
                "type": "object",
                "properties": {
                    "workspace": {"type": "string"},
                    "workspace_id": {"type": "string"},
                    "rule_id": {"type": "string"},
                    "status": {"type": "string", "enum": _RULE_STATUSES},
                    "reviewer": {"type": "string"},
                    "note": {"type": "string"},
                },
                "required": ["rule_id", "status"],
            },
        ),
        Tool(
            name="knowledge_workspace_create",
            description="Create or register a managed knowledge workspace",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "root": {"type": "string"},
                    "owner": {"type": "string"},
                    "tags": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["name"],
            },
        ),
        Tool(
            name="knowledge_workspace_list",
            description="List managed knowledge workspaces under DATA_SERVICE_WORKSPACE_ROOT",
            inputSchema={
                "type": "object",
                "properties": {
                    "owner": {"type": "string"},
                    "tag": {"type": "string"},
                    "limit": {"type": "integer", "default": 50},
                },
            },
        ),
        Tool(
            name="knowledge_workspace_describe",
            description="Describe one managed knowledge workspace",
            inputSchema={
                "type": "object",
                "properties": {
                    "workspace_id": {"type": "string"},
                    "workspace": {"type": "string"},
                },
            },
        ),
        Tool(
            name="knowledge_workspace_archive",
            description="Archive a managed knowledge workspace without deleting data",
            inputSchema={
                "type": "object",
                "properties": {
                    "workspace_id": {"type": "string"},
                    "reason": {"type": "string"},
                },
                "required": ["workspace_id"],
            },
        ),
        Tool(
            name="knowledge_source_import",
            description="Import files or text payloads into a managed workspace source area",
            inputSchema={
                "type": "object",
                "properties": {
                    "workspace_id": {"type": "string"},
                    "paths": {"type": "array", "items": {"type": "string"}},
                    "texts": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "title": {"type": "string"},
                                "content": {"type": "string"},
                                "metadata": {"type": "object"},
                            },
                        },
                    },
                    "metadata": {"type": "object"},
                },
                "required": ["workspace_id"],
            },
        ),
        Tool(
            name="knowledge_source_list",
            description="List imported sources for a managed workspace",
            inputSchema={
                "type": "object",
                "properties": {
                    "workspace_id": {"type": "string"},
                    "status": {"type": "string", "enum": _SOURCE_STATUSES},
                    "limit": {"type": "integer", "default": 100},
                },
                "required": ["workspace_id"],
            },
        ),
        Tool(
            name="knowledge_source_remove",
            description="Soft-remove one imported source from a managed workspace",
            inputSchema={
                "type": "object",
                "properties": {
                    "workspace_id": {"type": "string"},
                    "source_id": {"type": "string"},
                    "reason": {"type": "string"},
                },
                "required": ["workspace_id", "source_id"],
            },
        ),
        Tool(
            name="knowledge_build_start",
            description="Start a non-blocking managed workspace build operation",
            inputSchema={
                "type": "object",
                "properties": {
                    "workspace_id": {"type": "string"},
                    "mode": {"type": "string", "enum": _BUILD_MODES},
                },
                "required": ["workspace_id"],
            },
        ),
        Tool(
            name="knowledge_build_status",
            description="Poll a managed workspace build operation",
            inputSchema={
                "type": "object",
                "properties": {
                    "workspace_id": {"type": "string"},
                    "operation_id": {"type": "string"},
                },
                "required": ["workspace_id", "operation_id"],
            },
        ),
        Tool(
            name="knowledge_build_cancel",
            description="Cancel a managed workspace build operation",
            inputSchema={
                "type": "object",
                "properties": {
                    "workspace_id": {"type": "string"},
                    "operation_id": {"type": "string"},
                    "reason": {"type": "string"},
                },
                "required": ["workspace_id", "operation_id"],
            },
        ),
        Tool(
            name="knowledge_session_create",
            description="Create or reuse a scoped knowledge session inside a workspace",
            inputSchema={
                "type": "object",
                "properties": {
                    "workspace": {"type": "string"},
                    "workspace_id": {"type": "string"},
                    "external_id": {"type": "string"},
                    "session_type": {"type": "string"},
                    "title": {"type": "string"},
                    "ephemeral": {"type": "boolean", "default": False},
                    "ttl_seconds": {"type": "integer"},
                    "metadata": {"type": "object"},
                },
            },
        ),
        Tool(
            name="knowledge_session_get",
            description="Inspect one scoped knowledge session",
            inputSchema={
                "type": "object",
                "properties": {
                    "workspace": {"type": "string"},
                    "workspace_id": {"type": "string"},
                    "session_id": {"type": "string"},
                    "external_id": {"type": "string"},
                },
            },
        ),
        Tool(
            name="knowledge_session_list",
            description="List scoped knowledge sessions in a workspace",
            inputSchema={
                "type": "object",
                "properties": {
                    "workspace": {"type": "string"},
                    "workspace_id": {"type": "string"},
                    "status": {"type": "string"},
                    "session_type": {"type": "string"},
                    "include_disposed": {"type": "boolean", "default": False},
                    "limit": {"type": "integer", "default": 100},
                },
            },
        ),
        Tool(
            name="knowledge_session_close",
            description="Close or reopen a scoped knowledge session",
            inputSchema={
                "type": "object",
                "properties": {
                    "workspace": {"type": "string"},
                    "workspace_id": {"type": "string"},
                    "session_id": {"type": "string"},
                    "reopen": {"type": "boolean", "default": False},
                },
                "required": ["session_id"],
            },
        ),
        Tool(
            name="knowledge_session_delete",
            description="Dispose a session and remove session-scoped graph, sources, communities, summaries, and caches",
            inputSchema={
                "type": "object",
                "properties": {
                    "workspace": {"type": "string"},
                    "workspace_id": {"type": "string"},
                    "session_id": {"type": "string"},
                },
                "required": ["session_id"],
            },
        ),
        Tool(
            name="knowledge_session_ingest",
            description="Ingest structured records into a scoped session",
            inputSchema={
                "type": "object",
                "properties": {
                    "workspace": {"type": "string"},
                    "workspace_id": {"type": "string"},
                    "session_id": {"type": "string"},
                    "source_type": {"type": "string"},
                    "content_format": {"type": "string", "enum": ["text", "markdown", "turns", "json"]},
                    "title": {"type": "string"},
                    "records": {"type": "array", "items": {"type": "object"}},
                    "content": {},
                    "metadata": {"type": "object"},
                    "related_source_ids": {"type": "array", "items": {"type": "string"}},
                    "related_paths": {"type": "array", "items": {"type": "string"}},
                    "auto_link": {"type": "boolean", "default": False},
                    "allow_closed_write": {"type": "boolean", "default": False},
                },
                "required": ["session_id"],
            },
        ),
        Tool(
            name="knowledge_session_build_start",
            description="Start a session-scoped distill/graph/community build",
            inputSchema={
                "type": "object",
                "properties": {
                    "workspace": {"type": "string"},
                    "workspace_id": {"type": "string"},
                    "session_id": {"type": "string"},
                    "mode": {"type": "string", "enum": _SESSION_BUILD_MODES},
                    "sync": {"type": "boolean", "default": False},
                    "wait": {"type": "boolean", "default": False},
                },
                "required": ["session_id"],
            },
        ),
        Tool(
            name="knowledge_session_build_status",
            description="Poll a session-scoped build operation",
            inputSchema={
                "type": "object",
                "properties": {
                    "workspace": {"type": "string"},
                    "workspace_id": {"type": "string"},
                    "session_id": {"type": "string"},
                    "operation_id": {"type": "string"},
                },
                "required": ["session_id", "operation_id"],
            },
        ),
        Tool(
            name="knowledge_session_build_cancel",
            description="Cancel a session-scoped build operation",
            inputSchema={
                "type": "object",
                "properties": {
                    "workspace": {"type": "string"},
                    "workspace_id": {"type": "string"},
                    "session_id": {"type": "string"},
                    "operation_id": {"type": "string"},
                    "reason": {"type": "string"},
                },
                "required": ["session_id", "operation_id"],
            },
        ),
        Tool(
            name="knowledge_graph_snapshot",
            description="Read a workspace or session graph snapshot",
            inputSchema={
                "type": "object",
                "properties": {
                    "workspace": {"type": "string"},
                    "workspace_id": {"type": "string"},
                    "scope": {"type": "string", "enum": ["workspace", "session"], "default": "workspace"},
                    "session_id": {"type": "string"},
                    "max_nodes": {"type": "integer", "default": 200},
                    "include_communities": {"type": "boolean", "default": True},
                    "include_source_refs": {"type": "boolean", "default": True},
                    "node_types": {"type": "array", "items": {"type": "string"}},
                },
            },
        ),
        Tool(
            name="knowledge_graph_neighbors",
            description="Read session graph neighbors for a node",
            inputSchema={
                "type": "object",
                "properties": {
                    "workspace": {"type": "string"},
                    "workspace_id": {"type": "string"},
                    "session_id": {"type": "string"},
                    "node_id": {"type": "string"},
                    "depth": {"type": "integer", "default": 1},
                    "max_nodes": {"type": "integer", "default": 80},
                },
                "required": ["session_id", "node_id"],
            },
        ),
        Tool(
            name="knowledge_community_summary",
            description="Read session community summaries",
            inputSchema={
                "type": "object",
                "properties": {
                    "workspace": {"type": "string"},
                    "workspace_id": {"type": "string"},
                    "session_id": {"type": "string"},
                    "community_id": {"type": "string"},
                    "limit": {"type": "integer", "default": 20},
                },
                "required": ["session_id"],
            },
        ),
        Tool(
            name="knowledge_session_query",
            description="Query a scoped session graph and optionally include workspace context",
            inputSchema={
                "type": "object",
                "properties": {
                    "workspace": {"type": "string"},
                    "workspace_id": {"type": "string"},
                    "session_id": {"type": "string"},
                    "query": {"type": "string"},
                    "top_k": {"type": "integer", "default": 8},
                    "include_workspace_context": {"type": "boolean", "default": False},
                },
                "required": ["session_id", "query"],
            },
        ),
        Tool(
            name="knowledge_actor_summary",
            description="Summarize one actor inside a scoped session",
            inputSchema={
                "type": "object",
                "properties": {
                    "workspace": {"type": "string"},
                    "workspace_id": {"type": "string"},
                    "scope": {"type": "string", "enum": ["session"], "default": "session"},
                    "session_id": {"type": "string"},
                    "actor_id": {"type": "string"},
                    "include_units": {"type": "boolean", "default": True},
                    "unit_types": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["session_id", "actor_id"],
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> List[TextContent]:
    arguments = arguments or {}
    service = _service(normalize_workspace_arg(arguments.get("workspace")), arguments.get("workspace_id"))

    if name in _V2_TOOL_MAP:
        legacy_name = _V2_TOOL_MAP[name]
        if legacy_name in {"knowledge_ingest", "knowledge_quality_feedback", "knowledge_review_correction_rule"} and _is_workspace_archived(service.workspace):
            return _json_content(
                _blocked(
                    workspace_id=_workspace_id_for_service(service),
                    message="Workspace is archived and cannot be modified",
                    next_actions=["knowledge_workspace_describe"],
                )
            )
        try:
            legacy_content = await call_tool(legacy_name, arguments)
            legacy_payload = json.loads(legacy_content[0].text)
        except ValueError as exc:
            return _json_content(
                _blocked(
                    workspace_id=_workspace_id_for_service(service),
                    message=str(exc),
                    next_actions=[],
                )
            )
        return _json_content(
            _envelope(
                workspace_id=_workspace_id_for_service(service),
                artifact_refs=[{"type": "workspace", "path": str(service.workspace)}],
                next_actions=[],
                data=legacy_payload,
            )
        )

    if name.startswith("knowledge_session_") or name in {
        "knowledge_graph_snapshot",
        "knowledge_graph_neighbors",
        "knowledge_community_summary",
        "knowledge_actor_summary",
    }:
        session_service = _session_service(service)
        workspace_id = _workspace_id_for_service(service)

        def blocked_from_error(exc: Exception, *, session_id: str | None = None) -> List[TextContent]:
            return _json_content(
                _blocked(
                    workspace_id=workspace_id,
                    message=str(exc),
                    next_actions=["knowledge_session_get", "knowledge_session_list"],
                    data={
                        "error": {
                            "code": exc.__class__.__name__,
                            "message": str(exc),
                            "retryable": False,
                            **({"session_id": session_id} if session_id else {}),
                        }
                    },
                )
            )

        try:
            if name == "knowledge_session_create":
                result = session_service.create_session(
                    external_id=arguments.get("external_id"),
                    session_type=str(arguments.get("session_type") or "generic"),
                    title=str(arguments.get("title") or ""),
                    ephemeral=bool(arguments.get("ephemeral", False)),
                    ttl_seconds=arguments.get("ttl_seconds"),
                    metadata=dict(arguments.get("metadata") or {}),
                )
                return _json_content(
                    _envelope(
                        workspace_id=workspace_id,
                        status="ok",
                        artifact_refs=[{"type": "session", "session_id": result["session"]["session_id"]}],
                        next_actions=["knowledge_session_ingest", "knowledge_session_build_start"],
                        data=result,
                    )
                )

            if name == "knowledge_session_get":
                session = session_service.get_session(
                    session_id=arguments.get("session_id"),
                    external_id=arguments.get("external_id"),
                )
                if not session:
                    return _json_content(
                        _blocked(
                            workspace_id=workspace_id,
                            message="Unknown session",
                            next_actions=["knowledge_session_create", "knowledge_session_list"],
                        )
                    )
                return _json_content(_envelope(workspace_id=workspace_id, data={"session": session}))

            if name == "knowledge_session_list":
                items = session_service.list_sessions(
                    status=arguments.get("status"),
                    session_type=arguments.get("session_type"),
                    include_disposed=bool(arguments.get("include_disposed", False)),
                    limit=_bounded_int(arguments.get("limit"), default=100, minimum=1, maximum=500, field="limit"),
                )
                return _json_content(_envelope(workspace_id=workspace_id, data={"items": items}))

            if name == "knowledge_session_close":
                session_id = str(arguments.get("session_id") or "")
                session = session_service.close_session(session_id, reopen=bool(arguments.get("reopen", False)))
                return _json_content(
                    _envelope(
                        workspace_id=workspace_id,
                        status=session.get("status", "closed"),
                        artifact_refs=[{"type": "session", "session_id": session_id}],
                        next_actions=["knowledge_session_get", "knowledge_session_delete"],
                        data={"session": session},
                    )
                )

            if name == "knowledge_session_delete":
                session_id = str(arguments.get("session_id") or "")
                session = session_service.delete_session(session_id)
                return _json_content(
                    _envelope(
                        workspace_id=workspace_id,
                        status="disposed",
                        artifact_refs=[{"type": "session", "session_id": session_id}],
                        next_actions=["knowledge_session_list"],
                        data={"session": session},
                    )
                )

            if name == "knowledge_session_ingest":
                session_id = str(arguments.get("session_id") or "")
                result = session_service.ingest(
                    session_id=session_id,
                    source_type=str(arguments.get("source_type") or "structured"),
                    content_format=str(arguments.get("content_format") or "text"),
                    title=str(arguments.get("title") or ""),
                    records=list(arguments.get("records") or []),
                    content=arguments.get("content"),
                    metadata=dict(arguments.get("metadata") or {}),
                    related_source_ids=[str(item) for item in (arguments.get("related_source_ids") or [])],
                    related_paths=[str(item) for item in (arguments.get("related_paths") or [])],
                    auto_link=bool(arguments.get("auto_link", False)),
                    allow_closed_write=bool(arguments.get("allow_closed_write", False)),
                )
                source = result["source"]
                return _json_content(
                    _envelope(
                        workspace_id=workspace_id,
                        artifact_refs=[{"type": "session_source", "session_id": session_id, "source_id": source["source_id"]}],
                        next_actions=["knowledge_session_build_start"],
                        data={
                            "session_id": session_id,
                            "source": {
                                "source_id": source["source_id"],
                                "title": source["title"],
                                "source_type": source["source_type"],
                                "content_format": source["content_format"],
                                "record_count": source["record_count"],
                            },
                        },
                    )
                )

            if name == "knowledge_session_build_start":
                session_id = str(arguments.get("session_id") or "")
                operation = session_service.start_build(
                    session_id=session_id,
                    mode=str(arguments.get("mode") or "full"),
                )
                operation_id = operation["operation_id"]
                if bool(arguments.get("sync", False) or arguments.get("wait", False)):
                    session_service.run_build(session_id, operation_id)
                    operation = session_service.get_operation(session_id, operation_id) or operation
                else:
                    threading.Thread(target=session_service.run_build, args=(session_id, operation_id), daemon=True).start()
                return _json_content(_session_operation_envelope(workspace_id, session_id, operation_id, operation))

            if name == "knowledge_session_build_status":
                session_id = str(arguments.get("session_id") or "")
                operation_id = str(arguments.get("operation_id") or "")
                operation = session_service.get_operation(session_id, operation_id)
                if not operation:
                    return _json_content(
                        _blocked(
                            workspace_id=workspace_id,
                            operation_id=operation_id,
                            message=f"Unknown operation_id: {operation_id}",
                            next_actions=["knowledge_session_build_start"],
                        )
                    )
                return _json_content(_session_operation_envelope(workspace_id, session_id, operation_id, operation))

            if name == "knowledge_session_build_cancel":
                session_id = str(arguments.get("session_id") or "")
                operation_id = str(arguments.get("operation_id") or "")
                operation = session_service.cancel_operation(
                    session_id,
                    operation_id,
                    reason=str(arguments.get("reason") or ""),
                )
                return _json_content(_session_operation_envelope(workspace_id, session_id, operation_id, operation))

            if name == "knowledge_graph_snapshot":
                scope = str(arguments.get("scope") or "workspace")
                max_nodes = _bounded_int(arguments.get("max_nodes"), default=200, minimum=1, maximum=1000, field="max_nodes")
                if scope == "session":
                    payload = session_service.graph_snapshot(
                        scope="session",
                        session_id=arguments.get("session_id"),
                        max_nodes=max_nodes,
                        include_communities=bool(arguments.get("include_communities", True)),
                        include_source_refs=bool(arguments.get("include_source_refs", True)),
                        node_types=list(arguments.get("node_types") or []),
                    )
                    return _json_content(_envelope(workspace_id=workspace_id, status=payload.get("status", "ok"), data=payload))
                snapshot = service.get_graph_snapshot(max_nodes=max_nodes)
                return _json_content(_envelope(workspace_id=workspace_id, data={**snapshot, "scope": "workspace"}))

            if name == "knowledge_graph_neighbors":
                session_id = str(arguments.get("session_id") or "")
                payload = session_service.graph_neighbors(
                    session_id=session_id,
                    node_id=str(arguments.get("node_id") or ""),
                    depth=_bounded_int(arguments.get("depth"), default=1, minimum=1, maximum=3, field="depth"),
                    max_nodes=_bounded_int(arguments.get("max_nodes"), default=80, minimum=1, maximum=500, field="max_nodes"),
                )
                return _json_content(_envelope(workspace_id=workspace_id, status=payload.get("status", "ok"), data=payload))

            if name == "knowledge_community_summary":
                session_id = str(arguments.get("session_id") or "")
                payload = session_service.community_summary(
                    session_id=session_id,
                    community_id=arguments.get("community_id"),
                    limit=_bounded_int(arguments.get("limit"), default=20, minimum=1, maximum=200, field="limit"),
                )
                return _json_content(_envelope(workspace_id=workspace_id, status=payload.get("status", "ok"), data=payload))

            if name == "knowledge_session_query":
                session_id = str(arguments.get("session_id") or "")
                include_workspace_context = bool(arguments.get("include_workspace_context", False))
                workspace_context = None
                if include_workspace_context:
                    workspace_result = service.query(
                        str(arguments.get("query") or ""),
                        mode=QueryMode.HYBRID,
                        top_k=_bounded_int(arguments.get("top_k"), default=8, minimum=1, maximum=50, field="top_k"),
                    )
                    workspace_context = {
                        "answer": workspace_result.answer,
                        "hits": [
                            {
                                "title": hit.title,
                                "snippet": hit.snippet,
                                "source": hit.source,
                                "score": hit.score,
                                "meta": hit.meta,
                            }
                            for hit in workspace_result.hits
                        ],
                    }
                payload = session_service.query_session(
                    session_id=session_id,
                    query=str(arguments.get("query") or ""),
                    top_k=_bounded_int(arguments.get("top_k"), default=8, minimum=1, maximum=50, field="top_k"),
                    include_workspace_context=include_workspace_context,
                    workspace_context=workspace_context,
                )
                return _json_content(_envelope(workspace_id=workspace_id, status=payload.get("status", "ok"), data=payload))

            if name == "knowledge_actor_summary":
                session_id = str(arguments.get("session_id") or "")
                payload = session_service.actor_summary(
                    session_id=session_id,
                    actor_id=str(arguments.get("actor_id") or ""),
                    include_units=bool(arguments.get("include_units", True)),
                    unit_types=list(arguments.get("unit_types") or []),
                )
                return _json_content(_envelope(workspace_id=workspace_id, status=payload.get("status", "ok"), data=payload))
        except ValueError as exc:
            return blocked_from_error(exc, session_id=arguments.get("session_id"))

    if name == "knowledge_ingest":
        paths = validate_source_paths(arguments.get("paths") or [], workspace=service.workspace)
        plan = service.build_ingest_plan(paths)
        service.write_summary_files(plan)
        results = service.run_default_pipeline(plan)
        payload = {
            "workspace": str(service.workspace),
            "results": [
                {"engine": result.engine, "status": result.status, "meta": result.meta}
                for result in results
            ],
        }
        return _json_content(payload)

    if name == "knowledge_query":
        response = service.query(
            arguments.get("query", ""),
            mode=QueryMode(arguments.get("mode", QueryMode.HYBRID.value)),
            top_k=_bounded_int(arguments.get("top_k"), default=8, minimum=1, maximum=50, field="top_k"),
        )
        payload = {
            "mode": response.mode.value,
            "query": response.query,
            "answer": response.answer,
            "hits": [
                {
                    "title": hit.title,
                    "snippet": hit.snippet,
                    "source": hit.source,
                    "score": hit.score,
                    "meta": hit.meta,
                }
                for hit in response.hits
            ],
            "engine_payloads": response.engine_payloads,
        }
        return _json_content(payload)

    if name == "knowledge_quality_summary":
        bundle = service.read_summary_bundle()
        payload = {
            "workspace": str(service.workspace),
            "quality": bundle.get("quality", {}),
            "quality_feedback": bundle.get("quality_feedback", []),
            "quality_correction_rules": bundle.get("quality_correction_rules", []),
            "quality_correction_plan": bundle.get("quality_correction_plan", {}),
        }
        return _json_content(payload)

    if name == "knowledge_correction_plan":
        payload = (
            service.build_quality_correction_plan()
            if bool(arguments.get("rebuild", False))
            else service.read_quality_correction_plan(build_if_missing=False)
        )
        return _json_content(payload)

    if name == "knowledge_quality_feedback":
        payload = service.record_quality_feedback(
            target_type=arguments.get("target_type", ""),
            target_id=arguments.get("target_id", ""),
            action=arguments.get("action", ""),
            label=arguments.get("label", ""),
            suggested_value=arguments.get("suggested_value", ""),
            reason=arguments.get("reason", ""),
            metadata=arguments.get("metadata") or {},
        )
        return _json_content(payload)

    if name == "knowledge_correction_rules":
        payload = service.read_quality_correction_rules(
            limit=_bounded_int(arguments.get("limit"), default=100, minimum=1, maximum=500, field="limit"),
            status=arguments.get("status"),
        )
        return _json_content(payload)

    if name == "knowledge_review_correction_rule":
        payload = service.review_quality_correction_rule(
            rule_id=arguments.get("rule_id", ""),
            status=arguments.get("status", ""),
            reviewer=arguments.get("reviewer", ""),
            note=arguments.get("note", ""),
        )
        return _json_content(payload)

    if name == "knowledge_workspace_create":
        workspace_name = str(arguments.get("name") or "").strip()
        if not workspace_name:
            raise ValueError("name is required")
        tags = [str(tag) for tag in (arguments.get("tags") or [])][:20]
        root_arg = str(arguments.get("root") or "").strip()
        root = validate_workspace_path(root_arg) if root_arg else _workspace_root()
        workspace_id = _slug(workspace_name)
        workspace_path = validate_workspace_path(root / workspace_id)
        meta = _ensure_workspace_meta(
            workspace_path,
            name=workspace_name,
            owner=str(arguments.get("owner") or "") or None,
            tags=tags,
        )
        payload = _envelope(
            workspace_id=meta["workspace_id"],
            artifact_refs=[{"type": "workspace", "path": meta["workspace_path"]}],
            next_actions=["knowledge_source_import", "knowledge_workspace_describe"],
            data={
                "workspace_path": meta["workspace_path"],
                "capabilities": {
                    "ingest": True,
                    "query": True,
                    "quality_feedback": True,
                    "build": True,
                },
            },
        )
        return _json_content(payload)

    if name == "knowledge_workspace_list":
        root = _workspace_root()
        limit = _bounded_int(arguments.get("limit"), default=50, minimum=1, maximum=200, field="limit")
        owner = str(arguments.get("owner") or "").strip()
        tag = str(arguments.get("tag") or "").strip()
        items = []
        for meta_path in sorted(root.glob("*/.data_service_workspace.json"), key=lambda item: item.stat().st_mtime, reverse=True):
            meta = _read_json(meta_path, {})
            if owner and meta.get("owner") != owner:
                continue
            if tag and tag not in meta.get("tags", []):
                continue
            items.append(
                {
                    "workspace_id": meta.get("workspace_id") or meta_path.parent.name,
                    "name": meta.get("name") or meta_path.parent.name,
                    "workspace_path": meta.get("workspace_path") or str(meta_path.parent),
                    "status": meta.get("status", "active"),
                    "updated_at": meta.get("updated_at"),
                    "tags": meta.get("tags", []),
                }
            )
            if len(items) >= limit:
                break
        payload = _envelope(
            workspace_id="root",
            data={"items": items},
            next_actions=["knowledge_workspace_describe", "knowledge_workspace_create"],
        )
        return _json_content(payload)

    if name == "knowledge_workspace_describe":
        workspace_path = _resolve_workspace(arguments.get("workspace_id"), arguments.get("workspace"))
        meta = _ensure_workspace_meta(workspace_path)
        target_service = DataService(workspace_path)
        target_service.ensure_layout()
        bundle = target_service.read_summary_bundle()
        latest_build = None
        operations = sorted(_operations_dir(workspace_path).glob("*.json"), key=lambda item: item.stat().st_mtime, reverse=True)
        if operations:
            latest_build = _read_json(operations[0], None)
        payload = _envelope(
            workspace_id=meta["workspace_id"],
            artifact_refs=[{"type": "workspace", "path": meta["workspace_path"]}],
            next_actions=["knowledge_source_list", "knowledge_build_start", "knowledge_query"],
            data={
                "layout": _layout_payload(target_service),
                "summary": bundle.get("summary_json", {}),
                "engines": {
                    "llmwiki": {"page_count": len(bundle.get("llmwiki_pages", []))},
                    "graphrag": bundle.get("graph_stats", {}),
                },
                "latest_build": latest_build,
                "quality": bundle.get("quality", {}),
            },
        )
        return _json_content(payload)

    if name == "knowledge_workspace_archive":
        workspace_path = _resolve_workspace(arguments.get("workspace_id"))
        meta = _ensure_workspace_meta(workspace_path)
        meta["status"] = "archived"
        meta["archived_at"] = _now()
        meta["archive_reason"] = str(arguments.get("reason") or "")
        meta["updated_at"] = meta["archived_at"]
        _write_json(_workspace_meta_path(workspace_path), meta)
        payload = _envelope(
            workspace_id=meta["workspace_id"],
            artifact_refs=[{"type": "workspace", "path": meta["workspace_path"]}],
            next_actions=["knowledge_workspace_list"],
            data={"workspace": meta},
        )
        return _json_content(payload)

    if name == "knowledge_source_import":
        workspace_path = _resolve_workspace(arguments.get("workspace_id"))
        meta = _ensure_workspace_meta(workspace_path)
        if meta.get("status") == "archived":
            return _json_content(
                _envelope(
                    workspace_id=meta["workspace_id"],
                    status="blocked",
                    warnings=["Workspace is archived and cannot import sources"],
                    next_actions=["knowledge_workspace_describe"],
                )
            )
        paths = list(arguments.get("paths") or [])
        texts = list(arguments.get("texts") or [])
        if len(paths) + len(texts) > _MAX_IMPORT_FILES:
            return _json_content(
                _blocked(
                    workspace_id=meta["workspace_id"],
                    message=f"source import count must be between 0 and {_MAX_IMPORT_FILES}",
                    next_actions=["knowledge_source_import"],
                )
            )
        try:
            validated_paths = validate_source_paths(paths, workspace=workspace_path)
        except ValueError as exc:
            return _json_content(
                _blocked(
                    workspace_id=meta["workspace_id"],
                    message=str(exc),
                    next_actions=["knowledge_source_import"],
                )
            )
        manifest = _read_json(_sources_manifest_path(workspace_path), {"items": []})
        existing_by_sha = {item.get("sha256"): item for item in manifest.get("items", []) if item.get("sha256")}
        imported_dir = workspace_path / "sources" / "imported"
        imported_dir.mkdir(parents=True, exist_ok=True)
        sources = []

        def add_source(*, title: str, content: bytes, suffix: str, original_path: str | None, metadata: dict) -> dict:
            if len(content) > _MAX_IMPORT_FILE_BYTES:
                raise ValueError(f"source is larger than {_MAX_IMPORT_FILE_BYTES} bytes")
            sha256 = hashlib.sha256(content).hexdigest()
            duplicate = existing_by_sha.get(sha256)
            if duplicate:
                result = dict(duplicate)
                result["status"] = "duplicate"
                return result
            source_id = f"src_{sha256[:16]}"
            filename = f"{source_id}{suffix if suffix else '.txt'}"
            target = imported_dir / filename
            target.write_bytes(content)
            record = {
                "source_id": source_id,
                "sha256": sha256,
                "title": title or source_id,
                "status": "active",
                "path": str(target),
                "original_path": original_path,
                "metadata": metadata,
                "imported_at": _now(),
                "low_signal": {},
                "ingest_status": "pending",
            }
            manifest.setdefault("items", []).append(record)
            existing_by_sha[sha256] = record
            return record

        for raw_path in validated_paths:
            source_path = Path(raw_path)
            if not source_path.is_file():
                return _json_content(
                    _blocked(
                        workspace_id=meta["workspace_id"],
                        message=f"Source path is not a file: {source_path}",
                        next_actions=["knowledge_source_import"],
                    )
                )
            if source_path.stat().st_size > _MAX_IMPORT_FILE_BYTES:
                return _json_content(
                    _blocked(
                        workspace_id=meta["workspace_id"],
                        message=f"source file is larger than {_MAX_IMPORT_FILE_BYTES} bytes",
                        next_actions=["knowledge_source_import"],
                    )
                )
            record = add_source(
                title=source_path.stem,
                content=source_path.read_bytes(),
                suffix=source_path.suffix,
                original_path=str(source_path),
                metadata=dict(arguments.get("metadata") or {}),
            )
            sources.append(record)

        for text_record in texts:
            title = str((text_record or {}).get("title") or "text-source").strip()
            content_text = str((text_record or {}).get("content") or "")
            content = content_text.encode("utf-8")
            if len(content) > _MAX_IMPORT_TEXT_BYTES:
                return _json_content(
                    _blocked(
                        workspace_id=meta["workspace_id"],
                        message=f"text source is larger than {_MAX_IMPORT_TEXT_BYTES} bytes",
                        next_actions=["knowledge_source_import"],
                    )
                )
            record = add_source(
                title=title,
                content=content,
                suffix=".md",
                original_path=None,
                metadata={**dict(arguments.get("metadata") or {}), **dict((text_record or {}).get("metadata") or {})},
            )
            sources.append(record)

        _write_json(_sources_manifest_path(workspace_path), manifest)
        payload_sources = [
            {
                "source_id": item["source_id"],
                "sha256": item["sha256"],
                "title": item["title"],
                "status": "duplicate" if item.get("status") == "duplicate" else "imported",
                "path": item.get("path"),
            }
            for item in sources
        ]
        payload = _envelope(
            workspace_id=meta["workspace_id"],
            artifact_refs=[{"type": "source", "source_id": item["source_id"]} for item in payload_sources],
            next_actions=["knowledge_build_start", "knowledge_source_list"],
            data={"sources": payload_sources},
        )
        return _json_content(payload)

    if name == "knowledge_source_list":
        workspace_path = _resolve_workspace(arguments.get("workspace_id"))
        meta = _ensure_workspace_meta(workspace_path)
        limit = _bounded_int(arguments.get("limit"), default=100, minimum=1, maximum=500, field="limit")
        status_filter = arguments.get("status")
        manifest = _read_json(_sources_manifest_path(workspace_path), {"items": []})
        items = []
        for item in manifest.get("items", []):
            status = item.get("status", "active")
            if status_filter and status != status_filter:
                continue
            items.append(
                {
                    "source_id": item.get("source_id"),
                    "sha256": item.get("sha256"),
                    "title": item.get("title"),
                    "status": status,
                    "low_signal": item.get("low_signal", {}),
                    "ingest_status": item.get("ingest_status"),
                }
            )
            if len(items) >= limit:
                break
        return _json_content(_envelope(workspace_id=meta["workspace_id"], data={"items": items}))

    if name == "knowledge_source_remove":
        workspace_path = _resolve_workspace(arguments.get("workspace_id"))
        meta = _ensure_workspace_meta(workspace_path)
        if meta.get("status") == "archived":
            return _json_content(
                _envelope(
                    workspace_id=meta["workspace_id"],
                    status="blocked",
                    warnings=["Workspace is archived and cannot remove sources"],
                    next_actions=["knowledge_workspace_describe"],
                )
            )
        source_id = str(arguments.get("source_id") or "").strip()
        manifest = _read_json(_sources_manifest_path(workspace_path), {"items": []})
        updated = None
        for item in manifest.get("items", []):
            if item.get("source_id") == source_id:
                item["status"] = "removed"
                item["removed_at"] = _now()
                item["remove_reason"] = str(arguments.get("reason") or "")
                updated = item
                break
        if updated is None:
            return _json_content(
                _blocked(
                    workspace_id=meta["workspace_id"],
                    message=f"Unknown source_id: {source_id}",
                    next_actions=["knowledge_source_list"],
                )
            )
        _write_json(_sources_manifest_path(workspace_path), manifest)
        return _json_content(
            _envelope(
                workspace_id=meta["workspace_id"],
                artifact_refs=[{"type": "source", "source_id": source_id}],
                next_actions=["knowledge_source_list"],
                data={"source": updated},
            )
        )

    if name == "knowledge_build_start":
        workspace_path = _resolve_workspace(arguments.get("workspace_id"))
        meta = _ensure_workspace_meta(workspace_path)
        if meta.get("status") == "archived":
            return _json_content(
                _envelope(
                    workspace_id=meta["workspace_id"],
                    status="blocked",
                    warnings=["Workspace is archived and cannot start builds"],
                    next_actions=["knowledge_workspace_describe"],
                )
            )
        mode = str(arguments.get("mode") or "full")
        if mode not in _BUILD_MODES:
            raise ValueError(f"mode must be one of: {', '.join(_BUILD_MODES)}")
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
            "created_at": _now(),
            "updated_at": _now(),
        }
        _write_json(_operation_path(workspace_path, operation_id), operation)
        _ensure_build_worker(workspace_path)
        return _json_content(
            _envelope(
                workspace_id=meta["workspace_id"],
                operation_id=operation_id,
                status="queued",
                artifact_refs=[{"type": "operation", "operation_id": operation_id}],
                next_actions=["knowledge_build_status"],
                data={"mode": mode, "stage": "queued", "progress": 0.0},
            )
        )

    if name == "knowledge_build_status":
        workspace_path = _resolve_workspace(arguments.get("workspace_id"))
        meta = _ensure_workspace_meta(workspace_path)
        operation_id = str(arguments.get("operation_id") or "").strip()
        operation_path = _operation_path(workspace_path, operation_id)
        operation = _read_json(operation_path, None)
        if not operation:
            return _json_content(
                _blocked(
                    workspace_id=meta["workspace_id"],
                    operation_id=operation_id,
                    message=f"Unknown operation_id: {operation_id}",
                    next_actions=["knowledge_build_start"],
                )
            )
        return _json_content(_operation_envelope(meta["workspace_id"], operation_id, operation))

    if name == "knowledge_build_cancel":
        workspace_path = _resolve_workspace(arguments.get("workspace_id"))
        meta = _ensure_workspace_meta(workspace_path)
        operation_id = str(arguments.get("operation_id") or "").strip()
        operation_path = _operation_path(workspace_path, operation_id)
        operation = _read_json(operation_path, None)
        if not operation:
            return _json_content(
                _blocked(
                    workspace_id=meta["workspace_id"],
                    operation_id=operation_id,
                    message=f"Unknown operation_id: {operation_id}",
                    next_actions=["knowledge_build_start"],
                )
            )
        warnings = []
        if operation.get("status") in _TERMINAL_OPERATION_STATUSES:
            warnings.append(f"Operation is already {operation.get('status')} and cannot be cancelled")
        else:
            if operation.get("status") == "queued":
                operation["status"] = "cancelled"
                operation["stage"] = "cancelled"
                operation["retryable"] = False
            else:
                operation["cancel_requested"] = True
            operation["progress"] = operation.get("progress", 0.0)
            operation["cancel_reason"] = str(arguments.get("reason") or "")
            operation["updated_at"] = _now()
            _write_json(operation_path, operation)
        return _json_content(_operation_envelope(meta["workspace_id"], operation_id, operation, warnings=warnings))

    raise ValueError(f"Unknown tool: {name}")


async def main() -> None:
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
