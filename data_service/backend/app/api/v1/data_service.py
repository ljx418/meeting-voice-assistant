"""HTTP API for the local knowledge governance service."""

from __future__ import annotations

import hashlib
import json
import os
import re
import threading
import time
import traceback
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from app.api.v1.auth import api_key_header, verify_api_key
from app.config import config
from data_service import DataService, GraphExecutionOwner, QueryMode
from data_service.distill_contract import run_distill_contract
from data_service.mcp_common import blocked as _contract_blocked
from data_service.mcp_common import envelope as _contract_envelope
from data_service.query_contract import run_query_contract
from data_service.quality_contract import (
    low_signal_audit_payload,
    quality_correction_plan_payload,
    quality_correction_rule_review_payload,
    quality_correction_rules_build_payload,
    quality_correction_rules_payload,
    quality_feedback_list_payload,
    record_quality_feedback_payload,
)
from data_service.security import validate_source_paths, validate_workspace_path
from data_service.session_service import SessionKnowledgeService
from data_service.source_trace_contract import source_trace_payload


async def verify_knowledge_access(api_key: Optional[str] = Depends(api_key_header)) -> str:
    configured = os.getenv("DATA_SERVICE_REQUIRE_API_KEY")
    if configured is None:
        require_api_key = bool((getattr(config.api, "api_key", "") or "").strip()) and not (
            getattr(config.jwt, "dev_mode", False) and getattr(config.jwt, "dev_bypass_auth", False)
        )
    else:
        require_api_key = configured.lower() not in {"0", "false", "no", "off"}
    if require_api_key:
        return await verify_api_key(api_key)
    return getattr(config.jwt, "dev_user_id", None) or "local-dev"


router = APIRouter(prefix="/knowledge", tags=["Knowledge"], dependencies=[Depends(verify_knowledge_access)])
target_router = APIRouter(prefix="/workspaces", tags=["Knowledge Target"], dependencies=[Depends(verify_knowledge_access)])
_MAX_SOURCE_FILES = 100
_MAX_SOURCE_FILE_BYTES = 10 * 1024 * 1024
_BUILD_MODES = {"full", "incremental", "graph_only", "llmwiki_only"}
_TERMINAL_OPERATION_STATUSES = {"completed", "failed", "blocked", "cancelled"}
_BUILD_WORKERS: set[str] = set()
_BUILD_WORKERS_LOCK = threading.Lock()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _slug(value: object) -> str:
    text = re.sub(r"[^A-Za-z0-9._-]+", "-", str(value or "").strip().lower()).strip("-")
    return text[:48] or "workspace"


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


def _workspace_root() -> Path:
    configured = os.getenv("DATA_SERVICE_WORKSPACE_ROOT", "").strip()
    root = Path(configured).expanduser() if configured else Path.cwd()
    resolved = validate_workspace_path(root)
    resolved.mkdir(parents=True, exist_ok=True)
    return resolved


def _workspace_meta_path(workspace: Path) -> Path:
    return workspace / ".data_service_workspace.json"


def _sources_manifest_path(workspace: Path) -> Path:
    return workspace / "lifecycle" / "sources.json"


def _directory_scan_path(workspace: Path) -> Path:
    return workspace / "lifecycle" / "directory_scan.json"


def _operations_dir(workspace: Path) -> Path:
    return workspace / "lifecycle" / "operations"


def _operation_path(workspace: Path, operation_id: str) -> Path:
    return _operations_dir(workspace) / f"{operation_id}.json"


def _ensure_workspace_meta(workspace: Path, *, name: str | None = None, owner: str | None = None, tags: list[str] | None = None, bound_paths: list[str] | None = None) -> dict:
    workspace.mkdir(parents=True, exist_ok=True)
    DataService(workspace).ensure_layout()
    meta_path = _workspace_meta_path(workspace)
    existing = _read_json(meta_path, {})
    now = _now()
    meta = {
        "workspace_id": existing.get("workspace_id") or workspace.name,
        "name": name or existing.get("name") or workspace.name,
        "workspace_path": str(workspace),
        "owner": owner if owner is not None else existing.get("owner"),
        "tags": list(tags if tags is not None else existing.get("tags", [])),
        "status": existing.get("status", "active"),
        "bound_paths": list(bound_paths if bound_paths is not None else existing.get("bound_paths", [])),
        "created_at": existing.get("created_at", now),
        "updated_at": now,
    }
    _write_json(meta_path, meta)
    return meta


def _resolve_workspace_path(*, workspace: str | None = None, workspace_id: str | None = None) -> Path:
    if workspace:
        return validate_workspace_path(workspace)
    if workspace_id:
        root = _workspace_root()
        candidate = validate_workspace_path(root / workspace_id)
        try:
            candidate.relative_to(root)
        except ValueError as exc:
            raise ValueError("workspace_id is outside DATA_SERVICE_WORKSPACE_ROOT") from exc
        return candidate
    raise ValueError("workspace or workspace_id is required")


def _envelope(*, workspace_id: str, operation_id: str | None = None, status: str = "ok", warnings: list[str] | None = None, artifact_refs: list[Any] | None = None, next_actions: list[str] | None = None, data: dict | None = None) -> dict:
    return _contract_envelope(
        workspace_id=workspace_id,
        operation_id=operation_id,
        status=status,
        warnings=warnings,
        artifact_refs=artifact_refs,
        next_actions=next_actions,
        data=data,
    )


def _blocked(*, workspace_id: str, message: str, operation_id: str | None = None, next_actions: list[str] | None = None, data: dict | None = None) -> dict:
    return _contract_blocked(
        workspace_id=workspace_id,
        operation_id=operation_id,
        message=message,
        next_actions=next_actions,
        data=data,
    )


def _collect_source_files(paths: list[str], *, workspace: Path) -> list[Path]:
    validated = [Path(item) for item in validate_source_paths(paths, workspace=workspace)]
    files: list[Path] = []
    for path in validated:
        if path.is_dir():
            for candidate in sorted(path.rglob("*")):
                if candidate.is_file():
                    files.append(candidate)
                    if len(files) >= _MAX_SOURCE_FILES:
                        return files
        elif path.is_file():
            files.append(path)
        else:
            raise ValueError(f"Source path does not exist: {path}")
        if len(files) >= _MAX_SOURCE_FILES:
            return files
    return files


def _should_scan_file(path: Path) -> bool:
    if not path.is_file():
        return False
    if any(part.startswith(".") for part in path.parts):
        return False
    return path.suffix.lower() in DataService.SUPPORTED_SOURCE_SUFFIXES


def _file_fingerprint(path: Path) -> dict:
    stat = path.stat()
    payload = {
        "path": str(path),
        "name": path.name,
        "size_bytes": stat.st_size,
        "modified_at": datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat().replace("+00:00", "Z"),
        "mtime_ns": stat.st_mtime_ns,
        "sha256": None,
    }
    if stat.st_size <= _MAX_SOURCE_FILE_BYTES:
        payload["sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
    return payload


def _known_source_paths(workspace: Path) -> set[str]:
    known: set[str] = set()
    manifest = _read_json(_sources_manifest_path(workspace), {"items": []})
    for item in manifest.get("items", []):
        for key in ("path", "original_path"):
            value = str(item.get(key) or "").strip()
            if value:
                known.add(str(Path(value).expanduser().resolve()))
    service = DataService(workspace)
    distill_manifest = _read_json(service.layout.distill_manifest, {})
    for item in distill_manifest.get("sources", []):
        value = str(item.get("path") or "").strip()
        if value:
            known.add(str(Path(value).expanduser().resolve()))
    return known


def _scan_directories(workspace: Path, paths: list[str], *, persist: bool = True, limit: int = 500) -> dict:
    validated = [Path(item) for item in validate_source_paths(paths, workspace=workspace)]
    previous = _read_json(_directory_scan_path(workspace), {"files": {}})
    previous_files = previous.get("files", {}) or {}
    known_paths = _known_source_paths(workspace)
    current_files: dict[str, dict] = {}
    unreadable: list[dict] = []
    supported_suffixes = sorted(DataService.SUPPORTED_SOURCE_SUFFIXES)

    for root in validated:
        candidates = [root] if root.is_file() else sorted(root.rglob("*"))
        for candidate in candidates:
            if len(current_files) >= limit:
                break
            try:
                resolved = candidate.expanduser().resolve()
                if not _should_scan_file(resolved):
                    continue
                current_files[str(resolved)] = _file_fingerprint(resolved)
            except OSError as exc:
                unreadable.append({"path": str(candidate), "reason": str(exc)})
        if len(current_files) >= limit:
            break

    new_files: list[dict] = []
    modified_files: list[dict] = []
    unchanged_files: list[dict] = []
    for path, fingerprint in current_files.items():
        before = previous_files.get(path)
        if before:
            if before.get("sha256") != fingerprint.get("sha256") or before.get("size_bytes") != fingerprint.get("size_bytes") or before.get("mtime_ns") != fingerprint.get("mtime_ns"):
                modified_files.append({**fingerprint, "previous": before})
            else:
                unchanged_files.append(fingerprint)
        elif path in known_paths:
            unchanged_files.append({**fingerprint, "known_without_scan_baseline": True})
        else:
            new_files.append(fingerprint)

    deleted_files = [
        before
        for path, before in previous_files.items()
        if path not in current_files
    ]
    payload = {
        "workspace": str(workspace),
        "scanned_at": _now(),
        "roots": [str(path) for path in validated],
        "supported_suffixes": supported_suffixes,
        "limit": limit,
        "truncated": len(current_files) >= limit,
        "summary": {
            "current_file_count": len(current_files),
            "new_count": len(new_files),
            "modified_count": len(modified_files),
            "deleted_count": len(deleted_files),
            "unchanged_count": len(unchanged_files),
            "unreadable_count": len(unreadable),
            "pending_count": len(new_files) + len(modified_files) + len(deleted_files) + len(unreadable),
        },
        "changes": {
            "new": new_files[:100],
            "modified": modified_files[:100],
            "deleted": deleted_files[:100],
            "unreadable": unreadable[:100],
        },
        "files": current_files,
    }
    if persist:
        _write_json(_directory_scan_path(workspace), payload)
    return payload


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
        "started_at": operation.get("started_at"),
        "completed_at": operation.get("completed_at"),
        "created_at": operation.get("created_at"),
        "updated_at": operation.get("updated_at"),
        "error": operation.get("error"),
        "retryable": operation.get("retryable", True),
        "artifacts": operation.get("artifacts", []),
        "results": operation.get("results", []),
    }


def _operation_envelope(workspace_id: str, operation_id: str, operation: dict, *, warnings: list[str] | None = None, next_actions: list[str] | None = None) -> dict:
    status = operation.get("status", "queued")
    if next_actions is None:
        next_actions = ["knowledge_build_status"]
        if status not in _TERMINAL_OPERATION_STATUSES:
            next_actions.append("knowledge_build_cancel")
        if status in {"failed", "blocked"} and operation.get("retryable", True):
            next_actions.append("knowledge_build_start")
    return _envelope(
        workspace_id=workspace_id,
        operation_id=operation_id,
        status=status,
        warnings=warnings,
        artifact_refs=operation.get("artifacts", []),
        next_actions=next_actions,
        data=_operation_payload(operation),
    )


def _operation_cancel_requested(workspace: Path, operation_id: str) -> bool:
    operation = _read_json(_operation_path(workspace, operation_id), {})
    return bool(operation.get("cancel_requested")) or operation.get("status") == "cancelled"


class _BuildCancelled(Exception):
    pass


def _raise_if_cancelled(workspace: Path, operation_id: str) -> None:
    if _operation_cancel_requested(workspace, operation_id):
        _update_operation(
            workspace,
            operation_id,
            status="cancelled",
            stage="cancelled",
            completed_at=_now(),
            retryable=False,
            error=None,
        )
        raise _BuildCancelled()


def _operation_source_paths(workspace: Path, operation: dict) -> list[str]:
    explicit_paths = [str(item) for item in operation.get("paths", []) if str(item).strip()]
    if explicit_paths:
        return validate_source_paths(explicit_paths, workspace=workspace)
    imported_paths = _active_source_paths(workspace)
    if imported_paths:
        workspace_resolved = workspace.resolve()
        safe_imported_paths = []
        for item in imported_paths:
            resolved = Path(item).expanduser().resolve()
            try:
                resolved.relative_to(workspace_resolved)
            except ValueError as exc:
                raise ValueError(f"Imported source path is outside workspace: {resolved}") from exc
            safe_imported_paths.append(str(resolved))
        return safe_imported_paths
    meta = _read_json(_workspace_meta_path(workspace), {})
    bound_paths = [str(item) for item in meta.get("bound_paths", []) if str(item).strip()]
    if bound_paths:
        return validate_source_paths(bound_paths, workspace=workspace)
    return []


def _run_build_operation(workspace: Path, operation_id: str) -> None:
    operation = _read_json(_operation_path(workspace, operation_id), {})
    mode = operation.get("mode", "full")
    try:
        _update_operation(workspace, operation_id, status="running", stage="source_import", progress=0.05, started_at=operation.get("started_at") or _now())
        _raise_if_cancelled(workspace, operation_id)
        source_paths = _operation_source_paths(workspace, operation)
        if not source_paths:
            _update_operation(
                workspace,
                operation_id,
                status="blocked",
                stage="failed",
                progress=0.0,
                completed_at=_now(),
                error={"message": "No source paths available for this workspace", "stage": "source_import"},
                retryable=True,
            )
            return

        include_llmwiki = mode in {"full", "incremental", "llmwiki_only"}
        include_graphrag = mode in {"full", "incremental", "graph_only"}
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
        _update_operation(workspace, operation_id, stage="llmwiki" if include_llmwiki else "graphrag", progress=0.45)
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
            completed_at=_now(),
            retryable=False,
            artifacts=artifacts,
            results=[{"engine": result.engine, "status": result.status, "meta": result.meta} for result in results],
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
            completed_at=_now(),
            error={"message": str(exc), "type": exc.__class__.__name__, "traceback": traceback.format_exc(limit=6)},
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
            completed_at=_now(),
            error={"message": "HTTP server stopped while this build was running", "type": "server_interrupted"},
            retryable=True,
        )


def _workspace_worker_key(workspace: Path) -> str:
    return str(workspace.resolve())


def _next_queued_operation(workspace: Path) -> dict | None:
    operation_files = sorted(_operations_dir(workspace).glob("*.json"), key=lambda item: (_read_json(item, {}).get("created_at", ""), item.name))
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
                _update_operation(workspace, operation_id, status="cancelled", stage="cancelled", completed_at=_now(), retryable=False, error=None)
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


def _read_source_items(workspace: Path, *, limit: int, status: str | None = None) -> list[dict]:
    manifest = _read_json(_sources_manifest_path(workspace), {"items": []})
    items: list[dict] = []
    seen: set[str] = set()
    for item in manifest.get("items", []):
        item_status = str(item.get("status", "active"))
        if status and item_status != status:
            continue
        source_id = str(item.get("source_id") or item.get("sha256") or item.get("path") or "")
        seen.add(source_id)
        items.append(
            {
                "source_id": source_id,
                "sha256": item.get("sha256"),
                "title": item.get("title") or source_id,
                "status": item_status,
                "ingest_status": item.get("ingest_status") or "pending",
                "low_signal": item.get("low_signal", {}),
                "path": item.get("path"),
                "original_path": item.get("original_path"),
                "imported_at": item.get("imported_at"),
                "ingest_updated_at": item.get("ingest_updated_at"),
            }
        )
        if len(items) >= limit:
            return items

    service = DataService(workspace)
    distill_manifest = _read_json(service.layout.distill_manifest, {})
    for item in distill_manifest.get("sources", []):
        source_id = str(item.get("source_id") or "")
        if not source_id or source_id in seen:
            continue
        low_signal = item.get("profile", {}).get("low_signal") or item.get("low_signal") or {}
        item_status = "indexed"
        if status and status != item_status:
            continue
        items.append(
            {
                "source_id": source_id,
                "sha256": None,
                "title": item.get("title") or source_id,
                "status": "active",
                "ingest_status": item_status,
                "low_signal": low_signal,
                "path": item.get("path"),
                "original_path": item.get("path"),
                "unit_count": item.get("unit_count"),
                "source_weight": item.get("source_weight"),
                "source_density_score": item.get("source_density_score"),
            }
        )
        if len(items) >= limit:
            return items
    return items


def _service_for_workspace(workspace: str) -> DataService:
    try:
        return DataService(validate_workspace_path(workspace))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


def _service_for_workspace_id(workspace_id: str) -> DataService:
    try:
        return DataService(_resolve_workspace_path(workspace_id=workspace_id))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


class WorkspaceCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=128)
    root: Optional[str] = Field(default=None, description="Optional workspace root. Defaults to DATA_SERVICE_WORKSPACE_ROOT")
    owner: str = Field(default="", max_length=128)
    tags: List[str] = Field(default_factory=list)
    bound_paths: List[str] = Field(default_factory=list, description="Optional read-only source directories for directory-as-knowledge mode")


class WorkspaceListRequest(BaseModel):
    root: Optional[str] = Field(default=None)
    owner: str = Field(default="", max_length=128)
    tag: str = Field(default="", max_length=128)
    limit: int = Field(default=50, ge=1, le=200)


class WorkspaceDescribeRequest(BaseModel):
    workspace: Optional[str] = Field(default=None)
    workspace_id: Optional[str] = Field(default=None)


class SourceImportRequest(BaseModel):
    workspace: str = Field(..., description="Target workspace directory")
    paths: List[str] = Field(default_factory=list, description="Files or directories to copy into the managed source area")
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SourceListRequest(BaseModel):
    workspace: str = Field(..., description="Target workspace directory")
    limit: int = Field(default=100, ge=1, le=500)
    status: Optional[str] = Field(default=None)


class SourceRemoveRequest(BaseModel):
    workspace: str = Field(..., description="Target workspace directory")
    source_id: str = Field(..., min_length=1, max_length=128)
    reason: str = Field(default="", max_length=512)


class BuildStartRequest(BaseModel):
    workspace: Optional[str] = Field(default=None, description="Target workspace directory")
    workspace_id: Optional[str] = Field(default=None, description="Target workspace id under DATA_SERVICE_WORKSPACE_ROOT")
    mode: str = Field(default="full", description="Build mode: full, incremental, graph_only, llmwiki_only")
    paths: List[str] = Field(default_factory=list, description="Optional source paths for directory-as-knowledge refresh")


class BuildStatusRequest(BaseModel):
    workspace: Optional[str] = Field(default=None)
    workspace_id: Optional[str] = Field(default=None)
    operation_id: str = Field(..., min_length=1, max_length=128)


class BuildCancelRequest(BaseModel):
    workspace: Optional[str] = Field(default=None)
    workspace_id: Optional[str] = Field(default=None)
    operation_id: str = Field(..., min_length=1, max_length=128)
    reason: str = Field(default="", max_length=512)


class IngestRequest(BaseModel):
    workspace: str = Field(..., description="Target workspace directory")
    paths: List[str] = Field(..., description="Source file or directory paths to ingest")
    graphrag_execution_owner: GraphExecutionOwner = Field(
        default=GraphExecutionOwner.APP_GRAPHRAG,
        description="Who executes GraphRAG indexing: data_service or app.graphrag",
    )


class QueryRequest(BaseModel):
    workspace: str = Field(..., description="Target workspace directory")
    query: str = Field(..., description="Query text")
    mode: QueryMode = Field(default=QueryMode.HYBRID, description="Query mode: llmwiki, graphrag, hybrid")
    top_k: int = Field(default=8, ge=1, le=50)


class WorkspaceScopedQueryRequest(BaseModel):
    query: str = Field(..., description="Query text")
    mode: QueryMode = Field(default=QueryMode.HYBRID, description="Query mode: llmwiki, graphrag, hybrid")
    top_k: int = Field(default=8, ge=1, le=50)


class SummaryRequest(BaseModel):
    workspace: str = Field(..., description="Target workspace directory")


class GraphRequest(BaseModel):
    workspace: Optional[str] = Field(default=None, description="Target workspace directory")
    workspace_id: Optional[str] = Field(default=None, description="Target workspace id under DATA_SERVICE_WORKSPACE_ROOT")
    scope: str = Field(default="workspace", description="Graph scope: workspace or session")
    session_id: Optional[str] = Field(default=None, description="Session id when scope=session")
    max_nodes: int = Field(default=120, ge=10, le=500)


class DistillRequest(BaseModel):
    workspace: str = Field(..., description="Target workspace directory")
    source_id: Optional[str] = Field(default=None, description="Optional source_id to inspect")
    limit: int = Field(default=20, ge=1, le=200)
    kind: Optional[str] = Field(default=None, description="Optional unit kind filter")
    typed_unit_type: Optional[str] = Field(default=None, description="Optional typed unit type filter")
    min_importance: float = Field(default=0.0, ge=0.0, description="Minimum unit importance")
    llm_enriched_only: bool = Field(default=False, description="Only return llm-enriched units")
    authority: Optional[str] = Field(default=None, description="Optional authority filter")
    min_source_weight: float = Field(default=0.0, ge=0.0, description="Minimum source_weight")
    min_source_density: float = Field(default=0.0, ge=0.0, description="Minimum source_density_score")


class WorkspaceScopedDistillRequest(BaseModel):
    source_id: Optional[str] = Field(default=None, description="Optional source_id to inspect")
    limit: int = Field(default=20, ge=1, le=200)
    kind: Optional[str] = Field(default=None, description="Optional unit kind filter")
    typed_unit_type: Optional[str] = Field(default=None, description="Optional typed unit type filter")
    min_importance: float = Field(default=0.0, ge=0.0, description="Minimum unit importance")
    llm_enriched_only: bool = Field(default=False, description="Only return llm-enriched units")
    authority: Optional[str] = Field(default=None, description="Optional authority filter")
    min_source_weight: float = Field(default=0.0, ge=0.0, description="Minimum source_weight")
    min_source_density: float = Field(default=0.0, ge=0.0, description="Minimum source_density_score")


class SourceTraceRequest(BaseModel):
    workspace: str = Field(..., description="Target workspace directory")
    source_id: str = Field(..., min_length=1, max_length=256)
    limit: int = Field(default=12, ge=1, le=50)


class LowSignalAuditRequest(BaseModel):
    workspace: str = Field(..., description="Target workspace directory")
    limit: int = Field(default=30, ge=1, le=100)


class DirectoryScanRequest(BaseModel):
    workspace: str = Field(..., description="Target workspace directory")
    paths: List[str] = Field(default_factory=list, description="Optional directories/files to scan. Defaults to workspace bound_paths")
    persist: bool = Field(default=True, description="Persist scan snapshot for later change detection")
    limit: int = Field(default=500, ge=1, le=2000)


class PageRequest(BaseModel):
    workspace: str = Field(..., description="Target workspace directory")
    slug: str = Field(..., description="LLMWiki page slug")


class ResetRequest(BaseModel):
    workspace: str = Field(..., description="Target workspace directory")
    confirmation: str = Field(..., description="Must equal 'Delete' to confirm reset")


class GraphRAGExecuteRequest(BaseModel):
    workspace: str = Field(..., description="Target workspace directory")


class QualityFeedbackRequest(BaseModel):
    workspace: str = Field(..., description="Target workspace directory")
    target_type: str = Field(..., min_length=1, max_length=64, description="Target class, for example page/source/entity/query")
    target_id: str = Field(..., min_length=1, max_length=512, description="Stable target id or slug")
    action: str = Field(..., min_length=1, max_length=64, description="Feedback action, for example needs_review/rename_suggest/mark_noise")
    label: str = Field(default="", max_length=256, description="Human-readable target label")
    suggested_value: str = Field(default="", max_length=1024, description="Optional correction or replacement value")
    reason: str = Field(default="", max_length=4096, description="Operator note")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Optional context copied from the UI")


class QualityFeedbackListRequest(BaseModel):
    workspace: str = Field(..., description="Target workspace directory")
    limit: int = Field(default=100, ge=1, le=500)
    target_type: Optional[str] = Field(default=None, description="Optional target type filter")
    target_id: Optional[str] = Field(default=None, description="Optional target id filter")


class QualityCorrectionRulesRequest(BaseModel):
    workspace: str = Field(..., description="Target workspace directory")
    limit: int = Field(default=100, ge=1, le=500)
    status: Optional[str] = Field(default=None, description="Optional rule status filter")


class QualityCorrectionRulesBuildRequest(BaseModel):
    workspace: str = Field(..., description="Target workspace directory")


class QualityCorrectionRuleReviewRequest(BaseModel):
    workspace: str = Field(..., description="Target workspace directory")
    rule_id: str = Field(..., min_length=1, max_length=128, description="Correction rule id")
    status: str = Field(..., description="New review status: draft, approved, rejected, archived, revoked")
    reviewer: str = Field(default="", max_length=128, description="Optional reviewer name")
    note: str = Field(default="", max_length=2048, description="Optional review note")


class QualityCorrectionPlanRequest(BaseModel):
    workspace: str = Field(..., description="Target workspace directory")


@router.post("/workspaces/create")
async def create_workspace(request: WorkspaceCreateRequest) -> dict:
    try:
        root = validate_workspace_path(request.root) if request.root else _workspace_root()
        bound_paths = validate_source_paths(request.bound_paths, workspace=root) if request.bound_paths else []
        workspace = validate_workspace_path(root / _slug(request.name))
        meta = _ensure_workspace_meta(
            workspace,
            name=request.name,
            owner=request.owner or None,
            tags=[str(tag) for tag in request.tags[:20]],
            bound_paths=bound_paths,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return _envelope(
        workspace_id=meta["workspace_id"],
        artifact_refs=[{"type": "workspace", "path": meta["workspace_path"]}],
        next_actions=["knowledge_source_import", "knowledge_workspace_describe"],
        data={"workspace": meta},
    )


@router.post("/workspaces/list")
async def list_workspaces(request: WorkspaceListRequest) -> dict:
    try:
        root = validate_workspace_path(request.root) if request.root else _workspace_root()
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    root.mkdir(parents=True, exist_ok=True)
    items = []
    for meta_path in sorted(root.glob("*/.data_service_workspace.json"), key=lambda item: item.stat().st_mtime, reverse=True):
        meta = _read_json(meta_path, {})
        if request.owner and meta.get("owner") != request.owner:
            continue
        if request.tag and request.tag not in meta.get("tags", []):
            continue
        items.append(
            {
                "workspace_id": meta.get("workspace_id") or meta_path.parent.name,
                "name": meta.get("name") or meta_path.parent.name,
                "workspace_path": meta.get("workspace_path") or str(meta_path.parent),
                "status": meta.get("status", "active"),
                "updated_at": meta.get("updated_at"),
                "created_at": meta.get("created_at"),
                "tags": meta.get("tags", []),
                "bound_paths": meta.get("bound_paths", []),
            }
        )
        if len(items) >= request.limit:
            break
    return _envelope(workspace_id="root", data={"items": items}, next_actions=["knowledge_workspace_describe", "knowledge_workspace_create"])


@router.post("/workspaces/describe")
async def describe_workspace(request: WorkspaceDescribeRequest) -> dict:
    try:
        workspace = _resolve_workspace_path(workspace=request.workspace, workspace_id=request.workspace_id)
        meta = _ensure_workspace_meta(workspace)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    service = DataService(workspace)
    service.ensure_layout()
    bundle = service.read_summary_bundle()
    sources = _read_source_items(workspace, limit=500)
    return _envelope(
        workspace_id=meta["workspace_id"],
        artifact_refs=[{"type": "workspace", "path": meta["workspace_path"]}],
        next_actions=["knowledge_source_list", "knowledge_build_start", "knowledge_query"],
        data={
            "workspace": meta,
            "source_summary": {
                "source_count": len(sources),
                "indexed_count": sum(1 for item in sources if item.get("ingest_status") in {"indexed", "built"}),
                "failed_count": sum(1 for item in sources if item.get("ingest_status") == "failed"),
                "low_signal_count": sum(1 for item in sources if bool(item.get("low_signal"))),
            },
            "summary": bundle.get("summary_json", {}),
            "engines": {
                "llmwiki": {"page_count": len(bundle.get("llmwiki_pages", []))},
                "graphrag": bundle.get("graph_stats", {}),
            },
            "quality": bundle.get("quality", {}),
        },
    )


@router.post("/sources/import")
async def import_sources(request: SourceImportRequest) -> dict:
    service = _service_for_workspace(request.workspace)
    meta = _ensure_workspace_meta(service.workspace)
    if meta.get("status") == "archived":
        return _envelope(workspace_id=meta["workspace_id"], status="blocked", warnings=["Workspace is archived and cannot import sources"], next_actions=["knowledge_workspace_describe"])
    try:
        files = _collect_source_files(request.paths, workspace=service.workspace)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if not files:
        raise HTTPException(status_code=400, detail="No source files found")

    manifest_path = _sources_manifest_path(service.workspace)
    manifest = _read_json(manifest_path, {"items": []})
    existing_by_sha = {item.get("sha256"): item for item in manifest.get("items", []) if item.get("sha256")}
    imported_dir = service.workspace / "sources" / "imported"
    imported_dir.mkdir(parents=True, exist_ok=True)
    imported: list[dict] = []
    for source_path in files:
        if source_path.stat().st_size > _MAX_SOURCE_FILE_BYTES:
            raise HTTPException(status_code=400, detail=f"source file is larger than {_MAX_SOURCE_FILE_BYTES} bytes: {source_path}")
        content = source_path.read_bytes()
        sha256 = hashlib.sha256(content).hexdigest()
        duplicate = existing_by_sha.get(sha256)
        if duplicate:
            duplicate_payload = dict(duplicate)
            duplicate_payload["status"] = "duplicate"
            imported.append(duplicate_payload)
            continue
        source_id = f"src_{sha256[:16]}"
        target = imported_dir / f"{source_id}{source_path.suffix or '.txt'}"
        target.write_bytes(content)
        record = {
            "source_id": source_id,
            "sha256": sha256,
            "title": source_path.stem,
            "status": "active",
            "path": str(target),
            "original_path": str(source_path),
            "metadata": dict(request.metadata or {}),
            "imported_at": _now(),
            "low_signal": {},
            "ingest_status": "pending",
        }
        manifest.setdefault("items", []).append(record)
        existing_by_sha[sha256] = record
        imported.append(record)
    _write_json(manifest_path, manifest)
    return _envelope(
        workspace_id=meta["workspace_id"],
        artifact_refs=[{"type": "source", "source_id": item.get("source_id")} for item in imported],
        next_actions=["knowledge_source_list", "knowledge_build_start"],
        data={"sources": imported},
    )


@router.post("/sources/list")
async def list_sources(request: SourceListRequest) -> dict:
    service = _service_for_workspace(request.workspace)
    meta = _ensure_workspace_meta(service.workspace)
    items = _read_source_items(service.workspace, limit=request.limit, status=request.status)
    return _envelope(workspace_id=meta["workspace_id"], data={"items": items})


@router.post("/sources/remove")
async def remove_source(request: SourceRemoveRequest) -> dict:
    service = _service_for_workspace(request.workspace)
    meta = _ensure_workspace_meta(service.workspace)
    if meta.get("status") == "archived":
        return _envelope(workspace_id=meta["workspace_id"], status="blocked", warnings=["Workspace is archived and cannot remove sources"], next_actions=["knowledge_workspace_describe"])
    manifest_path = _sources_manifest_path(service.workspace)
    manifest = _read_json(manifest_path, {"items": []})
    updated = None
    for item in manifest.get("items", []):
        if item.get("source_id") == request.source_id:
            item["status"] = "removed"
            item["removed_at"] = _now()
            item["remove_reason"] = request.reason
            updated = item
            break
    if updated is None:
        raise HTTPException(status_code=404, detail=f"Unknown source_id: {request.source_id}")
    _write_json(manifest_path, manifest)
    return _envelope(
        workspace_id=meta["workspace_id"],
        artifact_refs=[{"type": "source", "source_id": request.source_id}],
        next_actions=["knowledge_source_list"],
        data={"source": updated},
    )


@router.post("/build/start")
async def start_build(request: BuildStartRequest) -> dict:
    try:
        workspace = _resolve_workspace_path(workspace=request.workspace, workspace_id=request.workspace_id)
        meta = _ensure_workspace_meta(workspace)
        if meta.get("status") == "archived":
            return _envelope(
                workspace_id=meta["workspace_id"],
                status="blocked",
                warnings=["Workspace is archived and cannot start builds"],
                next_actions=["knowledge_workspace_describe"],
            )
        mode = request.mode or "full"
        if mode not in _BUILD_MODES:
            raise ValueError(f"mode must be one of: {', '.join(sorted(_BUILD_MODES))}")
        source_paths = validate_source_paths(request.paths, workspace=workspace) if request.paths else []
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    operation_id = f"op_{uuid.uuid4().hex[:12]}"
    operation = {
        "operation_id": operation_id,
        "workspace_id": meta["workspace_id"],
        "mode": mode,
        "paths": source_paths,
        "status": "queued",
        "stage": "queued",
        "progress": 0.0,
        "error": None,
        "retryable": True,
        "artifacts": [],
        "created_at": _now(),
        "updated_at": _now(),
    }
    _write_json(_operation_path(workspace, operation_id), operation)
    _ensure_build_worker(workspace)
    return _envelope(
        workspace_id=meta["workspace_id"],
        operation_id=operation_id,
        status="queued",
        artifact_refs=[{"type": "operation", "operation_id": operation_id}],
        next_actions=["knowledge_build_status", "knowledge_build_cancel"],
        data=_operation_payload(operation),
    )


@router.post("/build/status")
async def build_status(request: BuildStatusRequest) -> dict:
    try:
        workspace = _resolve_workspace_path(workspace=request.workspace, workspace_id=request.workspace_id)
        meta = _ensure_workspace_meta(workspace)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    operation = _read_json(_operation_path(workspace, request.operation_id), None)
    if not operation:
        return _blocked(
            workspace_id=meta["workspace_id"],
            operation_id=request.operation_id,
            message=f"Unknown operation_id: {request.operation_id}",
            next_actions=["knowledge_build_start"],
        )
    if operation.get("status") == "queued":
        _ensure_build_worker(workspace)
    return _operation_envelope(meta["workspace_id"], request.operation_id, operation)


@router.post("/build/cancel")
async def cancel_build(request: BuildCancelRequest) -> dict:
    try:
        workspace = _resolve_workspace_path(workspace=request.workspace, workspace_id=request.workspace_id)
        meta = _ensure_workspace_meta(workspace)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    operation_path = _operation_path(workspace, request.operation_id)
    operation = _read_json(operation_path, None)
    if not operation:
        return _blocked(
            workspace_id=meta["workspace_id"],
            operation_id=request.operation_id,
            message=f"Unknown operation_id: {request.operation_id}",
            next_actions=["knowledge_build_start"],
        )
    warnings = []
    if operation.get("status") in _TERMINAL_OPERATION_STATUSES:
        warnings.append(f"Operation is already {operation.get('status')} and cannot be cancelled")
    else:
        if operation.get("status") == "queued":
            operation["status"] = "cancelled"
            operation["stage"] = "cancelled"
            operation["completed_at"] = _now()
            operation["retryable"] = False
        else:
            operation["cancel_requested"] = True
        operation["cancel_reason"] = request.reason
        operation["updated_at"] = _now()
        _write_json(operation_path, operation)
    return _operation_envelope(meta["workspace_id"], request.operation_id, operation, warnings=warnings)


@router.post("/ingest")
async def ingest_knowledge(request: IngestRequest) -> dict:
    service = _service_for_workspace(request.workspace)
    try:
        source_paths = validate_source_paths(request.paths, workspace=service.workspace)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    plan = service.build_ingest_plan(
        source_paths,
        graphrag_execution_owner=request.graphrag_execution_owner,
    )
    service.write_summary_files(plan)
    results = service.run_default_pipeline_and_refresh_summary(plan)
    return {
        "workspace": str(service.workspace),
        "summary": str(service.layout.summary_md),
        "results": [
            {"engine": result.engine, "status": result.status, "meta": result.meta}
            for result in results
        ],
    }


@router.post("/query")
async def query_knowledge(request: QueryRequest) -> dict:
    service = _service_for_workspace(request.workspace)
    return run_query_contract(service, request.query, mode=request.mode, top_k=request.top_k)


@router.post("/summary")
async def read_summary(request: SummaryRequest) -> dict:
    service = _service_for_workspace(request.workspace)
    return service.read_summary_bundle()


@router.post("/graph")
async def read_graph(request: GraphRequest) -> dict:
    if request.scope == "session":
        if not request.session_id:
            raise HTTPException(status_code=400, detail="session_id is required when scope=session")
        try:
            workspace = _resolve_workspace_path(workspace=request.workspace, workspace_id=request.workspace_id)
            service = SessionKnowledgeService(workspace, workspace_id=request.workspace_id or workspace.name)
            return service.graph_snapshot(
                scope="session",
                session_id=request.session_id,
                max_nodes=request.max_nodes,
                include_communities=True,
                include_source_refs=True,
            )
        except ValueError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
    if not request.workspace:
        raise HTTPException(status_code=400, detail="workspace is required when scope=workspace")
    service = _service_for_workspace(request.workspace)
    return service.get_graph_snapshot(max_nodes=request.max_nodes)


@router.post("/distill")
async def read_distill(request: DistillRequest) -> dict:
    service = _service_for_workspace(request.workspace)
    payload = run_distill_contract(
        service,
        source_id=request.source_id,
        limit=request.limit,
        kind=request.kind,
        typed_unit_type=request.typed_unit_type,
        min_importance=request.min_importance,
        llm_enriched_only=request.llm_enriched_only,
        authority=request.authority,
        min_source_weight=request.min_source_weight,
        min_source_density=request.min_source_density,
    )
    if request.source_id and payload["source"] is None:
        raise HTTPException(status_code=404, detail=f"Unknown source_id: {request.source_id}")
    return payload


@router.post("/source/trace")
async def read_source_trace(request: SourceTraceRequest) -> dict:
    service = _service_for_workspace(request.workspace)
    try:
        return source_trace_payload(service, request.source_id, limit=request.limit)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=f"Unknown source_id: {request.source_id}") from exc


@target_router.post("/{workspace_id}/query")
async def query_workspace(workspace_id: str, request: WorkspaceScopedQueryRequest) -> dict:
    service = _service_for_workspace_id(workspace_id)
    return run_query_contract(service, request.query, mode=request.mode, top_k=request.top_k)


@target_router.post("/{workspace_id}/distill")
async def read_workspace_distill(workspace_id: str, request: WorkspaceScopedDistillRequest) -> dict:
    service = _service_for_workspace_id(workspace_id)
    payload = run_distill_contract(
        service,
        source_id=request.source_id,
        limit=request.limit,
        kind=request.kind,
        typed_unit_type=request.typed_unit_type,
        min_importance=request.min_importance,
        llm_enriched_only=request.llm_enriched_only,
        authority=request.authority,
        min_source_weight=request.min_source_weight,
        min_source_density=request.min_source_density,
    )
    if request.source_id and payload["source"] is None:
        raise HTTPException(status_code=404, detail=f"Unknown source_id: {request.source_id}")
    return payload


@target_router.get("/{workspace_id}/sources/{source_id}/trace")
async def read_workspace_source_trace(
    workspace_id: str,
    source_id: str,
    limit: int = Query(default=12, ge=1, le=50),
) -> dict:
    service = _service_for_workspace_id(workspace_id)
    try:
        return source_trace_payload(service, source_id, limit=limit)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=f"Unknown source_id: {source_id}") from exc


@router.post("/quality/low-signal-audit")
async def read_low_signal_audit(request: LowSignalAuditRequest) -> dict:
    service = _service_for_workspace(request.workspace)
    return low_signal_audit_payload(service, limit=request.limit)


@router.post("/directories/scan")
async def scan_directories(request: DirectoryScanRequest) -> dict:
    service = _service_for_workspace(request.workspace)
    meta = _ensure_workspace_meta(service.workspace)
    paths = request.paths or list(meta.get("bound_paths", []) or [])
    if not paths:
        return _envelope(
            workspace_id=meta["workspace_id"],
            status="blocked",
            warnings=["No bound paths configured for directory scan"],
            next_actions=["knowledge_workspace_describe", "knowledge_workspace_create"],
            data={"summary": {"pending_count": 0}, "changes": {"new": [], "modified": [], "deleted": [], "unreadable": []}},
        )
    try:
        scan = _scan_directories(service.workspace, paths, persist=request.persist, limit=request.limit)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return _envelope(
        workspace_id=meta["workspace_id"],
        status="ok",
        artifact_refs=[{"type": "directory_scan", "path": str(_directory_scan_path(service.workspace))}],
        next_actions=["knowledge_build_start"] if scan["summary"]["pending_count"] else ["knowledge_source_list"],
        data=scan,
    )


@router.post("/boundary")
async def read_boundary(request: SummaryRequest) -> dict:
    service = _service_for_workspace(request.workspace)
    return service.read_boundary_audit()


@router.post("/graphrag/execute")
async def execute_graphrag(request: GraphRAGExecuteRequest) -> dict:
    service = _service_for_workspace(request.workspace)
    return service.run_graphrag_execution_request()


@router.post("/quality/feedback")
async def record_quality_feedback(request: QualityFeedbackRequest) -> dict:
    service = _service_for_workspace(request.workspace)
    try:
        return record_quality_feedback_payload(
            service,
            target_type=request.target_type,
            target_id=request.target_id,
            action=request.action,
            label=request.label,
            suggested_value=request.suggested_value,
            reason=request.reason,
            metadata=request.metadata,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/quality/feedback/list")
async def list_quality_feedback(request: QualityFeedbackListRequest) -> dict:
    service = _service_for_workspace(request.workspace)
    return quality_feedback_list_payload(
        service,
        limit=request.limit,
        target_type=request.target_type,
        target_id=request.target_id,
    )


@router.post("/quality/corrections")
async def list_quality_corrections(request: QualityCorrectionRulesRequest) -> dict:
    service = _service_for_workspace(request.workspace)
    return quality_correction_rules_payload(service, limit=request.limit, status=request.status)


@router.post("/quality/corrections/build")
async def build_quality_corrections(request: QualityCorrectionRulesBuildRequest) -> dict:
    service = _service_for_workspace(request.workspace)
    return quality_correction_rules_build_payload(service)


@router.post("/quality/corrections/review")
async def review_quality_correction(request: QualityCorrectionRuleReviewRequest) -> dict:
    service = _service_for_workspace(request.workspace)
    try:
        return quality_correction_rule_review_payload(
            service,
            rule_id=request.rule_id,
            status=request.status,
            reviewer=request.reviewer,
            note=request.note,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/quality/corrections/plan")
async def build_quality_correction_plan(request: QualityCorrectionPlanRequest) -> dict:
    service = _service_for_workspace(request.workspace)
    return quality_correction_plan_payload(service)


@router.post("/page")
async def read_page(request: PageRequest) -> dict:
    service = _service_for_workspace(request.workspace)
    return service.read_llmwiki_page(request.slug)


@router.post("/reset")
async def reset_workspace(request: ResetRequest) -> dict:
    service = _service_for_workspace(request.workspace)
    try:
        return service.reset_workspace(request.confirmation)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
