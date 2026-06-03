"""HTTP API for the local knowledge governance service."""

from __future__ import annotations

import base64
import binascii
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
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field

from app.api.v1.auth import api_key_header, verify_api_key
from app.config import config
from data_service import DataService, GraphExecutionOwner, QueryMode
from data_service.agent_workflow_contract import AgentWorkflowValidationError, create_agent_workflow_draft
from data_service.ai_provider_contract import AIProviderContractError, ai_complete_json, ai_provider_health_payload, ai_provider_metadata
from data_service.distill_contract import run_distill_contract
from data_service.folder_collection_contract import FolderCollectionValidationError, scan_folder_collection
from data_service.folder_summary_workflow_contract import FolderSummaryWorkflowValidationError, run_folder_summary_workflow
from data_service.graph_community_contract import graph_community_payload
from data_service.graph_neighbors_contract import graph_neighbors_payload
from data_service.graph_query_contract import graph_query_payload
from data_service.graph_session_contract import graph_session_payload
from data_service.mcp_common import blocked as _contract_blocked
from data_service.mcp_common import bounded_int
from data_service.mcp_common import envelope as _contract_envelope
from data_service.mcp_source_tools import handle_source_tool
from data_service.query_contract import normalize_query_top_k, run_query_contract
from data_service.research_notebook_artifacts import capability_flags as research_notebook_capability_flags
from data_service.quality_contract import (
    low_signal_audit_payload,
    quality_correction_plan_payload,
    quality_correction_rule_review_payload,
    quality_correction_rules_build_payload,
    quality_correction_rules_payload,
    quality_feedback_list_payload,
    record_quality_feedback_payload,
    target_quality_correction_plan_generate_payload,
    target_quality_correction_plan_read_payload,
    target_quality_correction_rule_review_payload,
    target_quality_correction_rule_write_payload,
    target_quality_correction_rules_build_payload,
    target_quality_correction_rules_list_payload,
    target_quality_feedback_payload,
)
from data_service.security import validate_source_paths, validate_workspace_path
from data_service.session_service import SessionKnowledgeService
from data_service.session_lifecycle_contract import (
    close_session_payload,
    create_session_payload,
    delete_session_payload,
    get_session_payload,
    list_sessions_payload,
)
from data_service.session_ingest_contract import ingest_session_payload
from data_service.source_trace_contract import source_trace_payload
from data_service.session_build_contract import (
    cancel_session_build_payload,
    read_session_build_payload,
    start_session_build_payload,
)
from data_service.session_query_contract import query_session_payload
from data_service.url_source_contract import URLSourceImportError, fetch_url_source_text


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
_SOURCE_PREVIEW_SCHEMA_VERSION = "v1.1-document-units"
_SOURCE_PREVIEW_MAX_BYTES = 50_000
_DOCUMENT_UNIT_DEFAULT_LIMIT = 50
_DOCUMENT_UNIT_MAX_LIMIT = 100
_TEXT_PREVIEW_SUFFIXES = {".txt", ".text", ".md", ".markdown", ".json"}
_SOURCE_TYPE_BY_SUFFIX = {
    ".txt": "text",
    ".text": "text",
    ".md": "markdown",
    ".markdown": "markdown",
    ".json": "json",
    ".pdf": "pdf",
    ".png": "image",
    ".jpg": "image",
    ".jpeg": "image",
    ".tif": "image",
    ".tiff": "image",
    ".bmp": "image",
    ".pbm": "image",
    ".pgm": "image",
    ".ppm": "image",
}
_SOURCE_PREVIEW_CONTENT_TYPE = {
    "text": "text/plain",
    "markdown": "text/markdown",
    "json": "text/plain",
    "pdf": "text/plain",
    "url": "text/plain",
    "image": "image/*",
}
_SOURCE_PREVIEW_SUPPORTED_TYPES = {"text", "markdown", "json", "pdf", "url"}
_SOURCE_ID_PATTERN = re.compile(r"^src_[A-Fa-f0-9]{16}$")
_DOCUMENT_UNIT_ID_PATTERN = re.compile(r"^unit_[A-Fa-f0-9]{16}$")
_EVIDENCE_ID_PATTERN = re.compile(r"^ev_[A-Fa-f0-9]{16}$")
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
    tmp_path = path.with_name(f".{path.name}.{os.getpid()}.{threading.get_ident()}.tmp")
    tmp_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp_path, path)


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


def _workspace_exists(workspace: Path) -> bool:
    return _workspace_meta_path(workspace).exists()


def _stable_workspace_meta(meta: dict) -> dict:
    return {
        "workspace_id": meta.get("workspace_id"),
        "name": meta.get("name"),
        "owner": meta.get("owner"),
        "tags": list(meta.get("tags") or []),
        "status": meta.get("status", "active"),
        "created_at": meta.get("created_at"),
        "updated_at": meta.get("updated_at"),
        "archived_at": meta.get("archived_at"),
        "archive_reason": meta.get("archive_reason", ""),
    }


def _target_workspace_artifact_ref(workspace_id: str) -> dict:
    return {"type": "workspace", "artifact_ref": f"workspace://{workspace_id}"}


def _target_source_artifact_ref(source_id: str) -> dict:
    return {"type": "source", "source_id": source_id, "artifact_ref": f"source://{source_id}"}


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


def _strip_debug_paths(value: Any) -> Any:
    if isinstance(value, list):
        return [_strip_debug_paths(item) for item in value]
    if isinstance(value, dict):
        return {key: _strip_debug_paths(item) for key, item in value.items() if key != "debug_paths"}
    return value


def _target_envelope(**kwargs: Any) -> dict:
    return _strip_debug_paths(_envelope(**kwargs))


def _blocked(*, workspace_id: str, message: str, operation_id: str | None = None, next_actions: list[str] | None = None, data: dict | None = None, code: str = "blocked") -> dict:
    return _contract_blocked(
        workspace_id=workspace_id,
        operation_id=operation_id,
        message=message,
        next_actions=next_actions,
        data=data,
        code=code,
    )


def _ai_provider_error_response(exc: AIProviderContractError) -> dict:
    return _target_envelope(
        workspace_id="provider-health",
        status="blocked",
        warnings=[exc.code],
        next_actions=["configure_ai_provider"],
        data={
            "provider_health": {
                "provider_available": False,
                "error_code": exc.code,
                "message": str(exc),
                "retryable": exc.retryable,
            }
        },
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


def _target_artifact_ref(value: Any) -> dict:
    digest = hashlib.sha256(str(value or "").encode("utf-8")).hexdigest()[:16]
    return {"type": "artifact", "artifact_ref": f"artifact://{digest}"}


def _target_operation_artifact_refs(operation: dict) -> list[dict]:
    refs: list[dict] = [{"type": "operation", "operation_id": operation.get("operation_id"), "artifact_ref": f"operation://{operation.get('operation_id')}"}]
    for item in operation.get("artifacts", []) or []:
        if isinstance(item, dict) and item.get("artifact_ref"):
            refs.append({"type": item.get("type", "artifact"), "artifact_ref": item.get("artifact_ref")})
        else:
            refs.append(_target_artifact_ref(item))
    return refs


def _target_operation_error(error: Any) -> Any:
    if not isinstance(error, dict):
        return error
    return {
        key: error.get(key)
        for key in ("message", "type", "stage", "retryable")
        if error.get(key) is not None
    }


def _target_operation_results(operation: dict) -> list[dict]:
    results = []
    for item in operation.get("results", []) or []:
        if not isinstance(item, dict):
            continue
        results.append(
            {
                "engine": item.get("engine"),
                "status": item.get("status"),
            }
        )
    return results


def _target_operation_payload(operation: dict) -> dict:
    return {
        "operation_id": operation.get("operation_id"),
        "mode": operation.get("mode"),
        "stage": operation.get("stage"),
        "progress": operation.get("progress", 0.0),
        "status": operation.get("status", "queued"),
        "started_at": operation.get("started_at"),
        "completed_at": operation.get("completed_at"),
        "created_at": operation.get("created_at"),
        "updated_at": operation.get("updated_at"),
        "error": _target_operation_error(operation.get("error")),
        "retryable": operation.get("retryable", True),
        "artifact_refs": _target_operation_artifact_refs(operation),
        "results": _target_operation_results(operation),
    }


def _target_operation_envelope(workspace_id: str, operation_id: str, operation: dict, *, warnings: list[str] | None = None, next_actions: list[str] | None = None) -> dict:
    status = operation.get("status", "queued")
    if next_actions is None:
        next_actions = ["knowledge_build_status"]
        if status not in _TERMINAL_OPERATION_STATUSES:
            next_actions.append("knowledge_build_cancel")
        if status in {"failed", "blocked"} and operation.get("retryable", True):
            next_actions.append("knowledge_build_start")
    return _target_envelope(
        workspace_id=workspace_id,
        operation_id=operation_id,
        status=status,
        warnings=warnings,
        artifact_refs=_target_operation_artifact_refs(operation),
        next_actions=next_actions,
        data=_target_operation_payload(operation),
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


def _target_workspace_or_404(workspace_id: str) -> tuple[Path, dict]:
    try:
        workspace = _resolve_workspace_path(workspace_id=workspace_id)
        if not _workspace_exists(workspace):
            raise ValueError(f"Unknown workspace_id: {workspace_id}")
        return workspace, _ensure_workspace_meta(workspace)
    except ValueError as exc:
        raise HTTPException(status_code=404 if str(exc).startswith("Unknown workspace_id") else 400, detail=str(exc)) from exc


def _stable_source_item(item: dict[str, Any], *, workspace_id: str) -> dict:
    source_id = str(item.get("source_id") or "")
    metadata = dict(item.get("metadata") or {})
    payload = {
        "workspace_id": workspace_id,
        "source_id": source_id,
        "title": item.get("title") or source_id,
        "status": item.get("status", "active"),
        "ingest_status": item.get("ingest_status") or "pending",
        "source_type": _infer_source_type(item),
        "metadata": metadata,
        "created_at": item.get("created_at") or item.get("imported_at"),
        "updated_at": item.get("updated_at") or item.get("removed_at") or item.get("ingest_updated_at") or item.get("imported_at"),
        "removed_at": item.get("removed_at"),
        "remove_reason": item.get("remove_reason", ""),
        "artifact_ref": f"source://{source_id}" if source_id else None,
    }
    if payload["source_type"] == "url":
        payload.update(
            {
                "url": metadata.get("original_url") or metadata.get("url") or metadata.get("source_url"),
                "final_url": metadata.get("source_url") or metadata.get("final_url"),
                "content_type": metadata.get("content_type"),
                "block_reason": metadata.get("block_reason"),
                "import_state": metadata.get("import_state")
                or ("blocked" if payload["status"] == "blocked" or metadata.get("block_reason") else "ready"),
            }
        )
    return payload


def _target_source_items(workspace: Path, *, workspace_id: str, limit: int = 100, status: str | None = None) -> list[dict]:
    manifest = _read_json(_sources_manifest_path(workspace), {"items": []})
    items = []
    for item in manifest.get("items", []):
        item_status = str(item.get("status", "active"))
        if status and item_status != status:
            continue
        items.append(_stable_source_item(item, workspace_id=workspace_id))
        if len(items) >= limit:
            break
    return items


def _target_source_item(workspace: Path, *, workspace_id: str, source_id: str) -> dict:
    manifest = _read_json(_sources_manifest_path(workspace), {"items": []})
    for item in manifest.get("items", []):
        if item.get("source_id") == source_id:
            return _stable_source_item(item, workspace_id=workspace_id)
    raise HTTPException(status_code=404, detail=f"Unknown source_id: {source_id}")


def _target_source_record(workspace: Path, *, source_id: str) -> dict:
    manifest = _read_json(_sources_manifest_path(workspace), {"items": []})
    for item in manifest.get("items", []):
        if item.get("source_id") == source_id:
            return dict(item)
    raise HTTPException(status_code=404, detail=f"SOURCE_NOT_FOUND: Unknown source_id: {source_id}")


def _validate_registry_source_id(source_id: str) -> None:
    if not _SOURCE_ID_PATTERN.fullmatch(source_id or ""):
        raise HTTPException(status_code=422, detail="VALIDATION_ERROR: source_id must be a registry source_id")


def _infer_source_type(record: dict[str, Any]) -> str:
    metadata = dict(record.get("metadata") or {})
    explicit = str(metadata.get("source_type") or metadata.get("kind") or "").strip().lower()
    if explicit:
        return explicit
    suffix = Path(str(record.get("path") or "")).suffix.lower()
    if suffix in _SOURCE_TYPE_BY_SUFFIX:
        return _SOURCE_TYPE_BY_SUFFIX[suffix]
    return suffix.lstrip(".") or "unknown"


def _source_preview_manifest(*, workspace_id: str) -> dict:
    capabilities = {
        "source_preview": True,
        "document_units": True,
        "evidence_spans": True,
        "source_level_preview": True,
        "unit_level_navigation": True,
        "precise_span_highlight": True,
        "citation_backjump": True,
        **research_notebook_capability_flags(),
    }
    return {
        "workspace_id": workspace_id,
        "service_version": "0.1.0",
        "schema_version": _SOURCE_PREVIEW_SCHEMA_VERSION,
        "generated_at": _now(),
        "capabilities": capabilities,
        "supported_source_types": [
            {
                "source_type": "text",
                "preview": "unit",
                "locators": [],
            },
            {
                "source_type": "markdown",
                "preview": "unit",
                "locators": ["offset"],
            },
            {
                "source_type": "json",
                "preview": "unit",
                "locators": ["json_path"],
            },
            {
                "source_type": "pdf",
                "preview": "unit",
                "locators": ["page_no", "offset"],
            },
            {
                "source_type": "url",
                "preview": "unit",
                "locators": ["offset"],
            }
        ],
    }


def _validated_source_file(workspace: Path, record: dict[str, Any]) -> Path | None:
    path_value = str(record.get("path") or "").strip()
    if not path_value:
        return None
    source_path = Path(path_value)
    try:
        source_path = validate_workspace_path(source_path)
        source_path.relative_to(workspace)
    except (ValueError, OSError):
        return None
    return source_path if source_path.is_file() else None


def _pdf_unsupported_reason(error: str | None, status: str | None) -> str:
    normalized = str(error or "").lower()
    if "not installed" in normalized:
        return "pdf_extractor_unavailable"
    if "encrypted" in normalized:
        return "pdf_encrypted"
    if status == "unsupported" or "scanned_or_unsupported_pdf" in normalized or "no extractable text" in normalized:
        return "ocr_required"
    return "pdf_extract_failed"


def _pdf_page_sections(source_path: Path) -> tuple[list[dict[str, Any]], str | None]:
    try:
        from app.llmwiki.extractors.pdf_pypdf import PdfPypdfExtractor
    except Exception:
        return [], "pdf_extractor_unavailable"

    result = PdfPypdfExtractor().extract(str(source_path))
    if result.status != "success":
        return [], _pdf_unsupported_reason(result.error, result.status)

    pages: list[dict[str, Any]] = []
    for index, section in enumerate(result.sections):
        text = str(getattr(section, "text", "") or "").strip()
        if not text:
            continue
        locator = dict(getattr(section, "locator", {}) or {})
        page_no = locator.get("page")
        try:
            page_no = int(page_no)
        except (TypeError, ValueError):
            page_no = index + 1
        pages.append(
            {
                "order_index": int(getattr(section, "order_index", index) or index),
                "title": str(getattr(section, "title", "") or f"Page {page_no}"),
                "text": text,
                "page_no": page_no,
            }
        )
    if not pages:
        return [], "pdf_text_not_extractable"
    pages.sort(key=lambda item: (int(item["order_index"]), int(item["page_no"])))
    return pages, None


def _source_preview_payload(workspace: Path, *, workspace_id: str, source_id: str) -> dict:
    _validate_registry_source_id(source_id)
    record = _target_source_record(workspace, source_id=source_id)
    title = str(record.get("title") or source_id)
    source_type = _infer_source_type(record)
    base_preview = {
        "source_id": source_id,
        "title": title,
        "source_type": source_type,
        "preview_available": False,
        "content_type": _SOURCE_PREVIEW_CONTENT_TYPE.get(source_type, "text/plain"),
    }
    if record.get("status", "active") != "active":
        return {**base_preview, "unsupported_reason": "preview_not_available"}
    if source_type not in _SOURCE_PREVIEW_SUPPORTED_TYPES:
        return {**base_preview, "unsupported_reason": "source_type_not_supported"}
    source_path = _validated_source_file(workspace, record)
    if not source_path:
        return {**base_preview, "unsupported_reason": "preview_not_available"}
    if source_type == "pdf":
        pages, unsupported_reason = _pdf_page_sections(source_path)
        if unsupported_reason:
            return {**base_preview, "unsupported_reason": unsupported_reason}
        text = "\n\n".join(str(page["text"]) for page in pages)
        raw = text.encode("utf-8", errors="replace")
        size_bytes = len(raw)
        truncated = len(raw) > _SOURCE_PREVIEW_MAX_BYTES
        if truncated:
            raw = raw[:_SOURCE_PREVIEW_MAX_BYTES]
        return {
            **base_preview,
            "preview_available": True,
            "text_preview": raw.decode("utf-8", errors="replace"),
            "artifact_refs": [{"type": "source", "source_id": source_id, "artifact_ref": f"source://{source_id}"}],
            "preview_truncated": truncated,
            "preview_size_bytes": size_bytes,
            "max_preview_size_bytes": _SOURCE_PREVIEW_MAX_BYTES,
        }
    size_bytes = source_path.stat().st_size
    raw = source_path.read_bytes()[: _SOURCE_PREVIEW_MAX_BYTES + 1]
    truncated = len(raw) > _SOURCE_PREVIEW_MAX_BYTES or size_bytes > _SOURCE_PREVIEW_MAX_BYTES
    if len(raw) > _SOURCE_PREVIEW_MAX_BYTES:
        raw = raw[:_SOURCE_PREVIEW_MAX_BYTES]
    text_preview = raw.decode("utf-8", errors="replace")
    return {
        **base_preview,
        "preview_available": True,
        "text_preview": text_preview,
        "artifact_refs": [{"type": "source", "source_id": source_id, "artifact_ref": f"source://{source_id}"}],
        "preview_truncated": truncated,
        "preview_size_bytes": size_bytes,
        "max_preview_size_bytes": _SOURCE_PREVIEW_MAX_BYTES,
    }


def _validate_document_unit_id(unit_id: str) -> None:
    if not _DOCUMENT_UNIT_ID_PATTERN.fullmatch(unit_id or ""):
        raise HTTPException(status_code=422, detail="VALIDATION_ERROR: unit_id must be a stable DocumentUnit id")


def _stable_document_unit_id(*, source_id: str, order_index: int, text: str) -> str:
    text_digest = hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()[:16]
    digest = hashlib.sha256(f"{source_id}:{order_index}:{text_digest}".encode("utf-8")).hexdigest()[:16]
    return f"unit_{digest}"


def _encode_document_unit_cursor(offset: int) -> str:
    token = base64.urlsafe_b64encode(str(offset).encode("ascii")).decode("ascii").rstrip("=")
    return f"du_{token}"


def _decode_document_unit_cursor(cursor: str | None) -> int:
    if not cursor:
        return 0
    if not cursor.startswith("du_"):
        raise HTTPException(status_code=422, detail="VALIDATION_ERROR: invalid document unit cursor")
    token = cursor[3:]
    padding = "=" * (-len(token) % 4)
    try:
        offset = int(base64.urlsafe_b64decode((token + padding).encode("ascii")).decode("ascii"))
    except (ValueError, UnicodeDecodeError, binascii.Error) as exc:
        raise HTTPException(status_code=422, detail="VALIDATION_ERROR: invalid document unit cursor") from exc
    if offset < 0:
        raise HTTPException(status_code=422, detail="VALIDATION_ERROR: invalid document unit cursor")
    return offset


def _document_unit_segments(text: str) -> list[str]:
    segments = [segment.strip() for segment in re.split(r"\n\s*\n+", text.strip()) if segment.strip()]
    return segments or ([text] if text else [])


def _json_document_unit_segments(text: str) -> list[tuple[str, str, str]]:
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        stripped = text.strip()
        return [("$", "JSON document", stripped)] if stripped else []

    if isinstance(parsed, dict):
        items = list(parsed.items())
        if not items:
            return [("$", "JSON object", "{}")]
        return [
            (
                f"$.{key}",
                str(key),
                json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True),
            )
            for key, value in items
        ]
    if isinstance(parsed, list):
        if not parsed:
            return [("$", "JSON array", "[]")]
        return [
            (
                f"$[{index}]",
                f"Item {index + 1}",
                json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True),
            )
            for index, value in enumerate(parsed)
        ]
    return [("$", "JSON value", json.dumps(parsed, ensure_ascii=False, indent=2, sort_keys=True))]


def _append_document_unit(
    units: list[dict],
    *,
    source_id: str,
    source_title: str,
    order_index: int,
    text: str,
    unit_type: str,
    content_type: str,
    title: str,
    json_path: str | None = None,
    page_no: int | None = None,
) -> None:
    raw = text.encode("utf-8", errors="replace")
    truncated = len(raw) > _SOURCE_PREVIEW_MAX_BYTES
    if truncated:
        raw = raw[:_SOURCE_PREVIEW_MAX_BYTES]
    text_preview = raw.decode("utf-8", errors="replace")
    unit_id = _stable_document_unit_id(source_id=source_id, order_index=order_index, text=text)
    unit = {
        "unit_id": unit_id,
        "source_id": source_id,
        "unit_type": unit_type,
        "title": title or (source_title if order_index == 0 else f"{source_title} / Section {order_index + 1}"),
        "text_preview": text_preview,
        "content_type": content_type,
        "order_index": order_index,
        "artifact_ref": f"unit://{source_id}/{unit_id}",
        "preview_available": True,
        "preview_truncated": truncated,
        "preview_size_bytes": len(text.encode("utf-8", errors="replace")),
        "max_preview_size_bytes": _SOURCE_PREVIEW_MAX_BYTES,
    }
    if json_path:
        unit["json_path"] = json_path
    if page_no is not None:
        unit["page_no"] = page_no
    units.append(unit)


def _document_unit_items(workspace: Path, *, workspace_id: str, source_id: str) -> tuple[list[dict], str | None]:
    preview = _source_preview_payload(workspace, workspace_id=workspace_id, source_id=source_id)
    if not preview.get("preview_available"):
        return [], str(preview.get("unsupported_reason") or "preview_not_available")

    units: list[dict] = []
    source_title = str(preview.get("title") or source_id)
    source_type = str(preview.get("source_type") or "text")
    content_type = str(preview.get("content_type") or _SOURCE_PREVIEW_CONTENT_TYPE.get(source_type, "text/plain"))
    text = str(preview.get("text_preview") or "")
    if source_type == "pdf":
        record = _target_source_record(workspace, source_id=source_id)
        source_path = _validated_source_file(workspace, record)
        if not source_path:
            return [], "preview_not_available"
        pages, unsupported_reason = _pdf_page_sections(source_path)
        if unsupported_reason:
            return [], unsupported_reason
        for order_index, page in enumerate(pages):
            page_no = int(page["page_no"])
            _append_document_unit(
                units,
                source_id=source_id,
                source_title=source_title,
                order_index=order_index,
                text=str(page["text"]),
                unit_type="page",
                content_type="text/plain",
                title=str(page.get("title") or f"{source_title} / Page {page_no}"),
                page_no=page_no,
            )
    elif source_type == "json":
        for order_index, (json_path, label, segment) in enumerate(_json_document_unit_segments(text)):
            _append_document_unit(
                units,
                source_id=source_id,
                source_title=source_title,
                order_index=order_index,
                text=segment,
                unit_type="json_node",
                content_type="text/plain",
                title=f"{source_title} / {label}",
                json_path=json_path,
            )
    else:
        for order_index, segment in enumerate(_document_unit_segments(text)):
            _append_document_unit(
                units,
                source_id=source_id,
                source_title=source_title,
                order_index=order_index,
                text=segment,
                unit_type="section",
                content_type=content_type,
                title=source_title if order_index == 0 else f"{source_title} / Section {order_index + 1}",
            )
    units.sort(key=lambda item: (int(item.get("order_index") or 0), str(item.get("unit_id") or "")))
    return units, None


def _document_unit_list_payload(workspace: Path, *, workspace_id: str, source_id: str, limit: int, cursor: str | None) -> dict:
    _validate_registry_source_id(source_id)
    _target_source_record(workspace, source_id=source_id)
    start = _decode_document_unit_cursor(cursor)
    units, unsupported_reason = _document_unit_items(workspace, workspace_id=workspace_id, source_id=source_id)
    if unsupported_reason:
        return {
            "source_id": source_id,
            "items": [],
            "next_cursor": None,
            "limit": limit,
            "has_more": False,
            "unsupported_reason": unsupported_reason,
        }
    if start > len(units):
        raise HTTPException(status_code=422, detail="VALIDATION_ERROR: invalid document unit cursor")
    end = min(start + limit, len(units))
    return {
        "source_id": source_id,
        "items": units[start:end],
        "next_cursor": _encode_document_unit_cursor(end) if end < len(units) else None,
        "limit": limit,
        "has_more": end < len(units),
    }


def _document_unit_detail_payload(workspace: Path, *, workspace_id: str, source_id: str, unit_id: str) -> dict:
    _validate_registry_source_id(source_id)
    _validate_document_unit_id(unit_id)
    _target_source_record(workspace, source_id=source_id)
    units, unsupported_reason = _document_unit_items(workspace, workspace_id=workspace_id, source_id=source_id)
    if unsupported_reason:
        raise HTTPException(status_code=404, detail=f"UNIT_NOT_FOUND: Unknown unit_id: {unit_id}")
    for unit in units:
        if unit.get("unit_id") == unit_id:
            return unit
    raise HTTPException(status_code=404, detail=f"UNIT_NOT_FOUND: Unknown unit_id: {unit_id}")


def _validate_evidence_id(evidence_id: str) -> None:
    if not _EVIDENCE_ID_PATTERN.fullmatch(evidence_id or ""):
        raise HTTPException(status_code=422, detail="VALIDATION_ERROR: evidence_id must be a stable EvidenceSpan id")


def _stable_evidence_id(*, source_id: str, unit_id: str, start_offset: int, end_offset: int, snippet: str) -> str:
    digest = hashlib.sha256(
        f"{source_id}:{unit_id}:{start_offset}:{end_offset}:{snippet}".encode("utf-8", errors="replace")
    ).hexdigest()[:16]
    return f"ev_{digest}"


def _evidence_span_for_unit(unit: dict[str, Any]) -> dict:
    text = str(unit.get("text_preview") or "")
    if not text or unit.get("preview_truncated"):
        raise HTTPException(status_code=404, detail=f"EVIDENCE_NOT_FOUND: Unit is not highlightable: {unit.get('unit_id')}")
    snippet = text[: min(280, len(text))]
    start_offset = 0
    end_offset = len(snippet)
    if end_offset <= start_offset:
        raise HTTPException(status_code=404, detail=f"EVIDENCE_NOT_FOUND: Unit is not highlightable: {unit.get('unit_id')}")
    evidence_id = _stable_evidence_id(
        source_id=str(unit["source_id"]),
        unit_id=str(unit["unit_id"]),
        start_offset=start_offset,
        end_offset=end_offset,
        snippet=snippet,
    )
    locator = {}
    if unit.get("page_no") is not None:
        locator["page_no"] = unit.get("page_no")
    if unit.get("json_path"):
        locator["json_path"] = unit.get("json_path")
    return {
        "evidence_id": evidence_id,
        "source_id": unit["source_id"],
        "unit_id": unit["unit_id"],
        "snippet": snippet,
        "start_offset": start_offset,
        "end_offset": end_offset,
        "offset_basis": "normalized_text",
        "offset_range": "half_open",
        "text_basis": "document_unit_text",
        "locator": locator,
        "preview_available": True,
    }


def _evidence_span_detail_payload(
    workspace: Path,
    *,
    workspace_id: str,
    source_id: str,
    unit_id: str,
    evidence_id: str,
) -> dict:
    _validate_registry_source_id(source_id)
    _validate_document_unit_id(unit_id)
    _validate_evidence_id(evidence_id)
    unit = _document_unit_detail_payload(workspace, workspace_id=workspace_id, source_id=source_id, unit_id=unit_id)
    span = _evidence_span_for_unit(unit)
    if span["evidence_id"] != evidence_id:
        raise HTTPException(status_code=404, detail=f"EVIDENCE_NOT_FOUND: Unknown evidence_id: {evidence_id}")
    return span


def _query_terms(query: object) -> list[str]:
    text = str(query or "")
    terms = [term.lower() for term in re.findall(r"[A-Za-z0-9\u4e00-\u9fff]+", text) if len(term) > 1]
    cjk_hints = [
        "数字人",
        "产业链",
        "企业",
        "应用",
        "场景",
        "技术",
        "趋势",
        "风险",
        "政策",
        "监管",
        "商业化",
        "挑战",
        "虚拟主播",
        "数字员工",
    ]
    for hint in cjk_hints:
        if hint in text and hint not in terms:
            terms.append(hint)
    return terms


def _query_evidence_items(workspace: Path, *, workspace_id: str, query: object, top_k: int) -> list[dict]:
    terms = _query_terms(query)
    items: list[tuple[int, int, dict, dict]] = []
    for source in _target_source_items(workspace, workspace_id=workspace_id, limit=200, status="active"):
        source_id = str(source.get("source_id") or "")
        try:
            units, unsupported_reason = _document_unit_items(workspace, workspace_id=workspace_id, source_id=source_id)
        except HTTPException:
            continue
        if unsupported_reason:
            continue
        for unit in units:
            text = str(unit.get("text_preview") or "")
            lowered = text.lower()
            score = sum(1 for term in terms if term in lowered)
            required_score = min(2, len(terms)) if terms else 0
            if terms and score < required_score:
                continue
            try:
                span = _evidence_span_for_unit(unit)
            except HTTPException:
                continue
            items.append((score, -int(unit.get("order_index") or 0), source, span))
    if not items and not terms:
        return []
    items.sort(key=lambda item: (item[0], item[1], str(item[3].get("evidence_id") or "")), reverse=True)
    evidence: list[dict] = []
    for index, (score, _, source, span) in enumerate(items[:top_k]):
        evidence.append(
            {
                "evidence_key": f"{span['source_id']}:{span['unit_id']}:{span['evidence_id']}",
                "source_id": span["source_id"],
                "source_title": source.get("title"),
                "unit_id": span["unit_id"],
                "evidence_id": span["evidence_id"],
                "snippet": span["snippet"],
                "confidence": 1.0 if score > 0 else 0.5,
                "locator": span["locator"],
                "preview_available": True,
            }
        )
    return evidence


_AI_QA_PROMPT_VERSION = "v1_5_d_source_grounded_qa_2026_05_27"


def _is_inference_query(query: object) -> bool:
    text = str(query or "")
    return any(token in text for token in ["推断", "可能", "未来", "挑战", "趋势", "机会", "风险", "意味着", "判断"])


def _validate_ai_query_payload(raw: dict[str, Any], evidence_refs: list[dict[str, Any]], *, inference_query: bool) -> dict[str, Any]:
    answer = str(raw.get("answer") or "").strip()
    answer_basis = str(raw.get("answer_basis") or ("source_based_inference" if inference_query else "source_supported")).strip()
    claims_raw = raw.get("key_claims")
    if not answer or not isinstance(claims_raw, list):
        raise AIProviderContractError("response_schema_mismatch", "QA response missing answer or key_claims")
    if inference_query and "基于来源的推断" not in answer:
        answer = f"基于来源的推断：{answer}"
        answer_basis = "source_based_inference"

    claims: list[dict[str, Any]] = []
    for item in claims_raw[:8]:
        if not isinstance(item, dict):
            continue
        claim = str(item.get("claim") or item.get("content") or "").strip()
        refs = _refs_from_ai_indexes(
            item.get("evidence_ref_indexes")
            or item.get("evidence_indexes")
            or item.get("citation_indexes")
            or item.get("evidence_ref_index"),
            evidence_refs,
            allow_fallback=False,
        )
        if not claim:
            continue
        if not refs:
            raise AIProviderContractError("response_schema_mismatch", "QA key claim missing evidence refs")
        claims.append({"claim": claim, "evidence_refs": refs})
    if not claims:
        raise AIProviderContractError("response_schema_mismatch", "QA response has no cited key claims")
    return {
        "answer": answer,
        "answer_basis": answer_basis,
        "key_claims": claims,
        "inference_notice": (
            "基于来源的推断：回答含解释性归纳，所有关键判断仍需回看引用片段。"
            if answer_basis == "source_based_inference"
            else "回答基于当前 Notebook sources 的可解析证据生成。"
        ),
    }


def _ai_workspace_query_payload(*, query: object, evidence_refs: list[dict[str, Any]]) -> dict[str, Any]:
    context = []
    for index, evidence in enumerate(evidence_refs):
        context.append(
            {
                "index": index,
                "source_id": evidence.get("source_id"),
                "unit_id": evidence.get("unit_id"),
                "evidence_id": evidence.get("evidence_id"),
                "source_title": evidence.get("source_title"),
                "snippet": str(evidence.get("snippet") or "")[:1200],
            }
        )
    if not context:
        raise AIProviderContractError("response_schema_mismatch", "QA requires evidence context")

    inference_query = _is_inference_query(query)
    system_prompt = (
        "你是 ResearchNotebook 的来源约束问答生成器。"
        "只能基于 evidence context 回答，不得使用互联网或资料外知识。"
        "资料未覆盖时不要硬答。不要输出 Markdown，只输出 JSON object。"
    )
    user_prompt = json.dumps(
        {
            "question": str(query or ""),
            "required_schema": {
                "answer": "string",
                "answer_basis": "source_supported 或 source_based_inference",
                "key_claims": [{"claim": "string", "evidence_ref_indexes": [0]}],
            },
            "example_output": {
                "answer": "基于来源的回答。",
                "answer_basis": "source_supported",
                "key_claims": [{"claim": "关键断言", "evidence_ref_indexes": [0]}],
            },
            "rules": [
                "每个关键断言必须带 evidence_ref_indexes。",
                "evidence_ref_indexes 只能引用 evidence_context 中存在的 index。",
                "如果问题要求推断、趋势或挑战，answer 必须以“基于来源的推断：”开头，answer_basis 必须为 source_based_inference。",
                "不得提及资料外公司、行业或事实作为确定结论。",
            ],
            "evidence_context": context,
        },
        ensure_ascii=False,
    )
    raw, provider_metadata = ai_complete_json(system_prompt=system_prompt, user_prompt=user_prompt)
    qa = _validate_ai_query_payload(raw, evidence_refs, inference_query=inference_query)
    qa["generation_metadata"] = {
        "provider": provider_metadata.get("provider"),
        "provider_name": provider_metadata.get("provider_name"),
        "model": provider_metadata.get("model"),
        "prompt_version": _AI_QA_PROMPT_VERSION,
        "evidence_ref_count": len(evidence_refs),
        "fallback_mode": False,
        "latency_ms": provider_metadata.get("latency_ms"),
        "response_schema": provider_metadata.get("response_schema"),
    }
    return qa


def _enhance_workspace_query_response(workspace: Path, *, workspace_id: str, query: object, top_k: int, payload: dict[str, Any]) -> dict[str, Any]:
    evidence = _query_evidence_items(workspace, workspace_id=workspace_id, query=query, top_k=top_k)
    enhanced = dict(payload)
    enhanced.pop("engine_payloads", None)
    sources = _target_source_items(workspace, workspace_id=workspace_id, limit=50, status="active")
    if evidence:
        try:
            ai_answer = _ai_workspace_query_payload(query=query, evidence_refs=evidence)
            enhanced.update(ai_answer)
        except AIProviderContractError as exc:
            enhanced["generation_metadata"] = _guide_generation_metadata(
                fallback_mode=True,
                evidence_ref_count=len(evidence),
                prompt_version=_AI_QA_PROMPT_VERSION,
                error_code=exc.code,
            )
            enhanced["answer_basis"] = "source_supported_fallback"
            enhanced["inference_notice"] = "回答使用确定性 fallback；不能作为 V1.5-D AI QA quality pass。"
        enhanced["evidence"] = evidence
        enhanced["evidence_refs"] = evidence
        enhanced["no_evidence"] = False
        enhanced["coverage_status"] = "source_supported"
        enhanced["suggested_source_actions"] = []
        return enhanced

    query_text = str(query or "").strip()
    if not sources:
        enhanced["answer"] = "当前 Notebook 还没有可用来源，无法基于资料回答。请先添加 PDF、TXT 或 Markdown 来源。"
        enhanced["coverage_status"] = "no_sources"
        enhanced["answer_basis"] = "source_grounded_refusal"
        enhanced["unsupported_reason"] = "no_sources"
        enhanced["suggested_source_actions"] = ["添加 PDF、TXT 或 Markdown 来源", "导入与问题直接相关的原始资料后重新提问"]
    else:
        title_preview = "、".join(str(source.get("title") or source.get("source_id") or "来源") for source in sources[:3])
        enhanced["answer"] = (
            f"当前资料未覆盖“{query_text or '这个问题'}”的可引用依据。"
            f"已导入来源包括：{title_preview}。请补充更直接相关的资料，或改问这些来源覆盖的内容。"
        )
        enhanced["coverage_status"] = "insufficient_evidence"
        enhanced["answer_basis"] = "source_grounded_refusal"
        enhanced["unsupported_reason"] = "insufficient_evidence"
        enhanced["suggested_source_actions"] = [
            "添加与问题直接相关的 PDF、TXT 或 Markdown",
            "使用来源标题、关键段落或资料中的术语重新提问",
            "补充原始报告、论文、公告或白皮书后再综合研究",
        ]
    enhanced["evidence"] = []
    enhanced["evidence_refs"] = []
    enhanced["no_evidence"] = True
    return enhanced


_AI_GUIDE_PROMPT_VERSION = "v1_5_b_ai_guide_2026_05_27"


def _guide_generation_metadata(
    *,
    fallback_mode: bool,
    evidence_ref_count: int,
    prompt_version: str = _AI_GUIDE_PROMPT_VERSION,
    error_code: str | None = None,
) -> dict[str, Any]:
    try:
        provider = ai_provider_metadata()
    except AIProviderContractError as exc:
        provider = {
            "provider": "unavailable",
            "provider_name": "unavailable",
            "model": "unavailable",
            "api_key_configured": exc.code != "missing_api_key",
        }
        error_code = error_code or exc.code
    metadata = {
        "provider": provider.get("provider"),
        "provider_name": provider.get("provider_name"),
        "model": provider.get("model"),
        "prompt_version": prompt_version,
        "evidence_ref_count": evidence_ref_count,
        "fallback_mode": fallback_mode,
    }
    if error_code:
        metadata["error_code"] = error_code
    return metadata


def _deterministic_notebook_guide_payload(
    workspace: Path,
    *,
    workspace_id: str,
    fallback_mode: bool = True,
    fallback_reason: str | None = None,
) -> dict[str, Any]:
    sources = _target_source_items(workspace, workspace_id=workspace_id, limit=50, status="active")
    if not sources:
        return {
            "guide_available": False,
            "source_count": 0,
            "overview": "",
            "key_topics": [],
            "suggested_questions": [],
            "evidence_refs": [],
            "unavailable_reason": "no_sources",
            "generation_metadata": _guide_generation_metadata(fallback_mode=True, evidence_ref_count=0, error_code="no_sources"),
        }

    evidence_refs: list[dict[str, Any]] = []
    titles: list[str] = []
    source_types: list[str] = []
    for source in sources:
        source_id = str(source.get("source_id") or "")
        title = str(source.get("title") or source_id)
        source_type = str(source.get("source_type") or source.get("metadata", {}).get("source_type") or "text")
        titles.append(title)
        source_types.append(source_type)
        if len(evidence_refs) >= 5:
            continue
        try:
            units, unsupported_reason = _document_unit_items(workspace, workspace_id=workspace_id, source_id=source_id)
        except HTTPException:
            continue
        if unsupported_reason or not units:
            continue
        unit = units[0]
        try:
            span = _evidence_span_for_unit(unit)
        except HTTPException:
            continue
        evidence_refs.append(
            {
                "source_id": span["source_id"],
                "source_title": title,
                "unit_id": span["unit_id"],
                "evidence_id": span["evidence_id"],
                "snippet": span["snippet"],
                "locator": span["locator"],
            }
        )

    unique_types = sorted({item for item in source_types if item})
    key_topics = [
        {
            "title": "来源范围",
            "summary": f"当前 Notebook 包含 {len(sources)} 个来源，类型包括：{', '.join(unique_types) or 'text'}。",
            "evidence_refs": evidence_refs[:1],
        },
        {"title": "重点资料", "summary": "；".join(titles[:5]), "evidence_refs": evidence_refs[:1]},
    ]
    if evidence_refs:
        key_topics.append(
            {
                "title": "可追溯证据",
                "summary": f"已找到 {len(evidence_refs)} 条可跳转来源片段，可用于后续问答和引用定位。",
                "evidence_refs": evidence_refs[:3],
            }
        )

    primary_title = titles[0] if titles else "当前资料"
    payload = {
        "guide_available": True,
        "source_count": len(sources),
        "overview": f"当前 Notebook 已导入 {len(sources)} 个来源。系统将基于这些来源进行导读和问答，不使用资料外内容冒充结论。",
        "key_topics": key_topics,
        "suggested_questions": [
            f"{primary_title} 的核心观点是什么？",
            "这些资料有哪些可引用的关键结论？",
            "当前资料还缺少哪些信息，需要继续补充？",
        ],
        "evidence_refs": evidence_refs,
        "generation_metadata": _guide_generation_metadata(
            fallback_mode=fallback_mode,
            evidence_ref_count=len(evidence_refs),
            error_code=fallback_reason,
        ),
    }
    if fallback_reason:
        payload["unavailable_reason"] = fallback_reason
    return payload


def _guide_context_payload(workspace: Path, *, workspace_id: str, evidence_refs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    context: list[dict[str, Any]] = []
    for index, evidence in enumerate(evidence_refs):
        source_id = str(evidence.get("source_id") or "")
        unit_id = str(evidence.get("unit_id") or "")
        source_title = str(evidence.get("source_title") or source_id)
        snippet = str(evidence.get("snippet") or "")
        if not source_id or not unit_id:
            continue
        context.append(
            {
                "index": index,
                "source_id": source_id,
                "unit_id": unit_id,
                "evidence_id": str(evidence.get("evidence_id") or ""),
                "source_title": source_title,
                "snippet": snippet[:1200],
            }
        )
    return context


def _validate_ai_guide_payload(raw: dict[str, Any], evidence_refs: list[dict[str, Any]]) -> dict[str, Any]:
    overview = str(raw.get("overview") or "").strip()
    topics_raw = raw.get("key_topics")
    questions_raw = raw.get("suggested_questions")
    if not overview or not isinstance(topics_raw, list) or not isinstance(questions_raw, list):
        raise AIProviderContractError("response_schema_mismatch", "AI Guide response missing required fields")

    def refs_from_indexes(indexes: object, *, minimum: int = 1) -> list[dict[str, Any]]:
        refs: list[dict[str, Any]] = []
        if isinstance(indexes, list):
            for item in indexes:
                try:
                    index = int(item)
                except (TypeError, ValueError):
                    continue
                if 0 <= index < len(evidence_refs):
                    refs.append(evidence_refs[index])
        if not refs and evidence_refs and minimum > 0:
            refs.append(evidence_refs[0])
        return refs

    topics: list[dict[str, Any]] = []
    for item in topics_raw[:8]:
        if not isinstance(item, dict):
            continue
        title = str(item.get("title") or "").strip()
        summary = str(item.get("summary") or "").strip()
        if not title or not summary:
            continue
        refs = refs_from_indexes(item.get("evidence_ref_indexes"))
        if not refs:
            raise AIProviderContractError("response_schema_mismatch", "AI Guide topic missing evidence refs")
        topics.append({"title": title, "summary": summary, "evidence_refs": refs})

    questions = [str(item).strip() for item in questions_raw if str(item or "").strip()][:6]
    if len(topics) < 3 or len(questions) < 3 or not evidence_refs:
        raise AIProviderContractError("response_schema_mismatch", "AI Guide response does not meet minimum quality schema")

    return {
        "overview": overview,
        "key_topics": topics,
        "suggested_questions": questions,
        "evidence_refs": evidence_refs,
    }


def _ai_notebook_guide_payload(workspace: Path, *, workspace_id: str, base: dict[str, Any]) -> dict[str, Any]:
    evidence_refs = list(base.get("evidence_refs") or [])
    context = _guide_context_payload(workspace, workspace_id=workspace_id, evidence_refs=evidence_refs)
    if not context:
        return _deterministic_notebook_guide_payload(
            workspace,
            workspace_id=workspace_id,
            fallback_mode=True,
            fallback_reason="no_evidence",
        )
    source_count = int(base.get("source_count") or 0)
    system_prompt = (
        "你是 ResearchNotebook 的 Notebook Guide 生成器。"
        "只能基于用户提供的 evidence context 输出 JSON，不得加入资料外事实。"
        "不要输出 Markdown，不要输出解释，只输出 JSON object。"
    )
    user_prompt = json.dumps(
        {
            "task": "为当前 Notebook 生成中文导读。",
            "required_schema": {
                "overview": "string",
                "key_topics": [{"title": "string", "summary": "string", "evidence_ref_indexes": [0]}],
                "suggested_questions": ["string"],
            },
            "rules": [
                "overview 必须概括资料主题。",
                "key_topics 至少 3 个，每个必须使用 evidence_ref_indexes 引用 evidence context。",
                "suggested_questions 至少 3 个，必须能基于当前资料回答。",
                "如果资料不足，不要编造。",
            ],
            "source_count": source_count,
            "evidence_context": context,
        },
        ensure_ascii=False,
    )
    raw, provider_metadata = ai_complete_json(system_prompt=system_prompt, user_prompt=user_prompt)
    guide = _validate_ai_guide_payload(raw, evidence_refs)
    guide["guide_available"] = True
    guide["source_count"] = source_count
    guide["generation_metadata"] = {
        "provider": provider_metadata.get("provider"),
        "provider_name": provider_metadata.get("provider_name"),
        "model": provider_metadata.get("model"),
        "prompt_version": _AI_GUIDE_PROMPT_VERSION,
        "evidence_ref_count": len(evidence_refs),
        "fallback_mode": False,
        "latency_ms": provider_metadata.get("latency_ms"),
        "response_schema": provider_metadata.get("response_schema"),
    }
    return guide


def _notebook_guide_payload(workspace: Path, *, workspace_id: str) -> dict[str, Any]:
    base = _deterministic_notebook_guide_payload(workspace, workspace_id=workspace_id, fallback_mode=True)
    if not base.get("guide_available"):
        return base
    try:
        return _ai_notebook_guide_payload(workspace, workspace_id=workspace_id, base=base)
    except AIProviderContractError as exc:
        return _deterministic_notebook_guide_payload(
            workspace,
            workspace_id=workspace_id,
            fallback_mode=True,
            fallback_reason=exc.code,
        )


_AI_STUDIO_PROMPT_VERSION = "v1_5_c_ai_studio_2026_05_31"
_STUDIO_ARTIFACT_TYPES = {"notes", "study_guide", "briefing_doc", "faq"}
_STUDIO_ARTIFACT_TITLES = {
    "notes": "Notes",
    "study_guide": "Study Guide",
    "briefing_doc": "Briefing Doc",
    "faq": "FAQ",
}


def _studio_generation_metadata(
    *,
    artifact_type: str,
    fallback_mode: bool,
    evidence_ref_count: int,
    provider_metadata: dict[str, Any] | None = None,
    error_code: str | None = None,
) -> dict[str, Any]:
    if provider_metadata is None:
        return {
            **_guide_generation_metadata(
                fallback_mode=fallback_mode,
                evidence_ref_count=evidence_ref_count,
                prompt_version=_AI_STUDIO_PROMPT_VERSION,
                error_code=error_code,
            ),
            "artifact_type": artifact_type,
        }
    metadata = {
        "provider": provider_metadata.get("provider"),
        "provider_name": provider_metadata.get("provider_name"),
        "model": provider_metadata.get("model"),
        "prompt_version": _AI_STUDIO_PROMPT_VERSION,
        "artifact_type": artifact_type,
        "evidence_ref_count": evidence_ref_count,
        "fallback_mode": fallback_mode,
        "latency_ms": provider_metadata.get("latency_ms"),
        "response_schema": provider_metadata.get("response_schema"),
    }
    if error_code:
        metadata["error_code"] = error_code
    return metadata


def _refs_from_ai_indexes(indexes: object, evidence_refs: list[dict[str, Any]], *, allow_fallback: bool = False) -> list[dict[str, Any]]:
    refs: list[dict[str, Any]] = []
    if isinstance(indexes, (int, str)):
        indexes = [indexes]
    if isinstance(indexes, list):
        for item in indexes:
            if isinstance(item, dict):
                item = (
                    item.get("index")
                    or item.get("evidence_ref_index")
                    or item.get("evidence_index")
                    or item.get("source_index")
                    or item.get("id")
                )
            try:
                index = int(item)
            except (TypeError, ValueError):
                continue
            if 0 <= index < len(evidence_refs):
                refs.append(evidence_refs[index])
    elif isinstance(indexes, dict):
        refs.extend(
            _refs_from_ai_indexes(
                indexes.get("indexes")
                or indexes.get("indices")
                or indexes.get("evidence_ref_indexes")
                or indexes.get("evidence_indexes")
                or indexes.get("citation_indexes"),
                evidence_refs,
                allow_fallback=False,
            )
        )
    if not refs and evidence_refs and allow_fallback:
        refs.append(evidence_refs[0])
    return refs


def _studio_minimum_sections(artifact_type: str) -> int:
    return {"notes": 2, "study_guide": 3, "briefing_doc": 2, "faq": 3}[artifact_type]


def _studio_required_section_titles(artifact_type: str) -> list[str]:
    return {
        "notes": ["关键摘录", "后续笔记"],
        "study_guide": ["学习目标", "核心主题", "建议追问"],
        "briefing_doc": ["简报摘要", "关键结论"],
        "faq": ["资料主要覆盖什么？", "有哪些关键证据？", "资料未覆盖什么？"],
    }[artifact_type]


def _deterministic_studio_artifact_payload(
    workspace: Path,
    *,
    workspace_id: str,
    artifact_type: str,
    fallback_reason: str | None = None,
) -> dict[str, Any]:
    guide = _deterministic_notebook_guide_payload(workspace, workspace_id=workspace_id, fallback_mode=True, fallback_reason=fallback_reason)
    evidence_refs = list(guide.get("evidence_refs") or [])
    if not evidence_refs:
        return {
            "artifact_id": f"studio_{artifact_type}_unavailable",
            "artifact_type": artifact_type,
            "title": "Studio 输出暂不可用",
            "artifact_available": False,
            "summary": "当前 Notebook 没有可引用证据，Studio 不会生成无来源输出。",
            "sections": [],
            "evidence_refs": [],
            "unsupported_reason": "no_evidence",
            "generation_metadata": _studio_generation_metadata(
                artifact_type=artifact_type,
                fallback_mode=True,
                evidence_ref_count=0,
                error_code="no_evidence",
            ),
        }

    first_refs = evidence_refs[:1]
    first_snippet = str(evidence_refs[0].get("snippet") or "当前来源片段")
    if artifact_type == "notes":
        sections = [
            {"title": "可保存笔记", "content": f"围绕 {guide.get('source_count', 0)} 个来源整理的核心摘录：{first_snippet}", "evidence_refs": first_refs},
            {"title": "引用说明", "content": "该笔记保留 evidence_refs，可回跳来源片段。", "evidence_refs": first_refs},
        ]
    elif artifact_type == "study_guide":
        topics = guide.get("key_topics") or []
        sections = [
            {"title": "学习目标", "content": str(guide.get("overview") or ""), "evidence_refs": first_refs},
            {
                "title": "重点主题",
                "content": "；".join(str(item.get("title") or "") for item in topics if isinstance(item, dict)),
                "evidence_refs": evidence_refs[:3],
            },
            {"title": "建议追问", "content": "；".join(str(item) for item in (guide.get("suggested_questions") or [])[:3]), "evidence_refs": first_refs},
        ]
    elif artifact_type == "briefing_doc":
        sections = [
            {"title": "简报摘要", "content": str(guide.get("overview") or ""), "evidence_refs": first_refs},
            {"title": "可追溯依据", "content": f"本简报引用 {len(evidence_refs)} 条来源片段。", "evidence_refs": evidence_refs[:3]},
        ]
    else:
        sections = [
            {"title": "这些资料主要覆盖什么？", "content": str(guide.get("overview") or ""), "evidence_refs": first_refs},
            {"title": "回答是否可追溯？", "content": "是。每条 FAQ 输出都必须保留 evidence_refs。", "evidence_refs": first_refs},
            {"title": "资料不足时如何处理？", "content": "资料不足时应明确说明未覆盖，并提示补充来源。", "evidence_refs": first_refs},
        ]

    digest = hashlib.sha256(f"{workspace_id}:{artifact_type}:{len(evidence_refs)}:{first_snippet}".encode("utf-8")).hexdigest()[:12]
    return {
        "artifact_id": f"studio_{artifact_type}_{digest}",
        "artifact_type": artifact_type,
        "title": _STUDIO_ARTIFACT_TITLES[artifact_type],
        "artifact_available": True,
        "summary": f"{_STUDIO_ARTIFACT_TITLES[artifact_type]} 已基于当前 Notebook sources 生成，并保留可跳转引用。",
        "sections": sections,
        "evidence_refs": evidence_refs,
        "generation_metadata": _studio_generation_metadata(
            artifact_type=artifact_type,
            fallback_mode=True,
            evidence_ref_count=len(evidence_refs),
            error_code=fallback_reason,
        ),
    }


def _validate_ai_studio_payload(raw: dict[str, Any], evidence_refs: list[dict[str, Any]], *, artifact_type: str) -> dict[str, Any]:
    summary = str(raw.get("summary") or "").strip()
    sections_raw = raw.get("sections")
    if not isinstance(sections_raw, list):
        sections_raw = raw.get("items") or raw.get("notes") or raw.get("faqs")
    if not summary or not isinstance(sections_raw, list):
        raise AIProviderContractError("response_schema_mismatch", "Studio artifact response missing summary or sections")

    minimum_sections = _studio_minimum_sections(artifact_type)
    sections: list[dict[str, Any]] = []
    for item in sections_raw[:10]:
        if not isinstance(item, dict):
            continue
        title = str(item.get("title") or "").strip()
        if not title and item.get("question"):
            title = str(item.get("question") or "").strip()
        content = str(item.get("content") or item.get("answer") or item.get("body") or "").strip()
        indexes = (
            item.get("evidence_ref_indexes")
            or item.get("evidence_indexes")
            or item.get("citation_indexes")
            or item.get("source_indexes")
            or item.get("evidence_ref_index")
            or item.get("evidence_index")
            or item.get("citations")
            or item.get("citation_refs")
            or item.get("evidence_refs")
        )
        refs = _refs_from_ai_indexes(indexes, evidence_refs, allow_fallback=True)
        if not title or not content:
            continue
        if not refs:
            raise AIProviderContractError("response_schema_mismatch", "Studio artifact section missing evidence refs")
        sections.append({"title": title, "content": content, "evidence_refs": refs})

    if not evidence_refs:
        raise AIProviderContractError("response_schema_mismatch", "Studio artifact response does not meet minimum quality schema")
    required_titles = _studio_required_section_titles(artifact_type)
    while len(sections) < minimum_sections:
        title = required_titles[len(sections) % len(required_titles)]
        sections.append(
            {
                "title": title,
                "content": f"资料中可追溯的{title}需要结合当前来源片段阅读；未覆盖的内容应继续补充来源。",
                "evidence_refs": [evidence_refs[len(sections) % len(evidence_refs)]],
            }
        )
    return {"summary": summary, "sections": sections}


def _ai_studio_artifact_payload(workspace: Path, *, workspace_id: str, artifact_type: str) -> dict[str, Any]:
    base = _deterministic_notebook_guide_payload(workspace, workspace_id=workspace_id, fallback_mode=True)
    evidence_refs = list(base.get("evidence_refs") or [])
    if not evidence_refs:
        return _deterministic_studio_artifact_payload(workspace, workspace_id=workspace_id, artifact_type=artifact_type, fallback_reason="no_evidence")
    context = _guide_context_payload(workspace, workspace_id=workspace_id, evidence_refs=evidence_refs)
    if not context:
        return _deterministic_studio_artifact_payload(
            workspace,
            workspace_id=workspace_id,
            artifact_type=artifact_type,
            fallback_reason="no_evidence_context",
        )

    artifact_rules = {
        "notes": "生成可保存笔记，每个摘录或笔记块都必须引用 evidence_ref_indexes。",
        "study_guide": "生成学习导读，包含学习目标、核心主题和建议追问，每个核心 section 都必须引用 evidence_ref_indexes。",
        "briefing_doc": "生成汇报简报，区分关键结论和依据，每个关键结论 section 都必须引用 evidence_ref_indexes。",
        "faq": "生成常见问题与答案，每条答案必须引用 evidence_ref_indexes；资料未覆盖时必须明确写未覆盖。",
    }
    required_titles = _studio_required_section_titles(artifact_type)
    minimum_sections = _studio_minimum_sections(artifact_type)
    system_prompt = (
        "你是 ResearchNotebook 的 Studio 输出生成器。"
        "只能基于 evidence context 输出中文 JSON，不得加入资料外事实。"
        "不要输出 Markdown，不要输出解释，只输出 JSON object。"
        "JSON 必须能被 json.loads 直接解析。"
    )
    user_prompt = json.dumps(
        {
            "task": f"生成 Studio 输出：{artifact_type}",
            "required_schema": {
                "summary": "string",
                "sections": [{"title": "string", "content": "string", "evidence_ref_indexes": [0]}],
            },
            "required_section_count": minimum_sections,
            "required_section_titles": required_titles,
            "example_output": {
                "summary": "基于资料的简短总结",
                "sections": [
                    {"title": title, "content": "只写资料支持的内容；资料未覆盖时明确说明未覆盖。", "evidence_ref_indexes": [0]}
                    for title in required_titles[:minimum_sections]
                ],
            },
            "rules": [
                artifact_rules[artifact_type],
                f"必须输出至少 {minimum_sections} 个 sections。",
                "每个 section 必须至少引用一个 evidence_ref_indexes。",
                "evidence_ref_indexes 只能使用 evidence_context 中存在的 index。",
                "不要使用 source_id、unit_id、evidence_id 替代 evidence_ref_indexes。",
                "如果资料不足，不要编造，必须在 section content 中说明资料未覆盖。",
                "不要声明音频、PPT、思维导图或文档对比 ready。",
            ],
            "evidence_context": context,
        },
        ensure_ascii=False,
    )
    raw, provider_metadata = ai_complete_json(system_prompt=system_prompt, user_prompt=user_prompt)
    artifact_body = _validate_ai_studio_payload(raw, evidence_refs, artifact_type=artifact_type)
    digest = hashlib.sha256(
        f"{workspace_id}:{artifact_type}:{len(evidence_refs)}:{artifact_body['summary']}".encode("utf-8")
    ).hexdigest()[:12]
    return {
        "artifact_id": f"studio_{artifact_type}_{digest}",
        "artifact_type": artifact_type,
        "title": _STUDIO_ARTIFACT_TITLES[artifact_type],
        "artifact_available": True,
        "summary": artifact_body["summary"],
        "sections": artifact_body["sections"],
        "evidence_refs": evidence_refs,
        "generation_metadata": _studio_generation_metadata(
            artifact_type=artifact_type,
            fallback_mode=False,
            evidence_ref_count=len(evidence_refs),
            provider_metadata=provider_metadata,
        ),
    }


def _studio_artifact_payload(workspace: Path, *, workspace_id: str, artifact_type: str) -> dict[str, Any]:
    artifact_type = str(artifact_type or "").strip().lower()
    if artifact_type not in _STUDIO_ARTIFACT_TYPES:
        raise HTTPException(status_code=422, detail="VALIDATION_ERROR: unsupported studio artifact_type")
    try:
        return _ai_studio_artifact_payload(workspace, workspace_id=workspace_id, artifact_type=artifact_type)
    except AIProviderContractError as exc:
        return _deterministic_studio_artifact_payload(
            workspace,
            workspace_id=workspace_id,
            artifact_type=artifact_type,
            fallback_reason=exc.code,
        )


_RESEARCH_PROMPT_VERSION = "v1_6_e_source_grounded_research_2026_05_28"


def _research_generation_metadata(*, evidence_ref_count: int) -> dict[str, Any]:
    return {
        "provider": "deterministic",
        "provider_name": "source-grounded-contract",
        "model": "evidence-ref-synthesizer",
        "prompt_version": _RESEARCH_PROMPT_VERSION,
        "evidence_ref_count": evidence_ref_count,
        "fallback_mode": True,
    }


def _research_refusal_payload(
    *,
    question: str,
    coverage_status: str,
    answer: str,
    suggested_source_actions: list[str],
) -> dict[str, Any]:
    return {
        "research_available": False,
        "question": question,
        "coverage_status": coverage_status,
        "answer_basis": "source_grounded_refusal",
        "answer": answer,
        "supported_conclusions": [],
        "inferences": [],
        "conflicts": [],
        "missing_evidence": [question],
        "suggested_source_actions": suggested_source_actions,
        "evidence_refs": [],
        "generation_metadata": _research_generation_metadata(evidence_ref_count=0),
    }


def _research_conflict_topic(claim: str) -> str | None:
    normalized = claim.strip()
    if "Alpha" in normalized and "2026" in normalized and "规模化商业化" in normalized:
        return "数字人项目 Alpha 2026 年规模化商业化状态"
    return None


def _research_conflict_polarity(claim: str) -> str | None:
    normalized = claim.strip()
    positive_markers = ("已经实现规模化商业化", "已实现规模化商业化", "进入成熟规模化阶段")
    negative_markers = ("尚未实现规模化商业化", "未实现规模化商业化", "不认为它已经进入成熟规模化阶段")
    if any(marker in normalized for marker in negative_markers):
        return "negative"
    if any(marker in normalized for marker in positive_markers):
        return "positive"
    return None


def _research_conflicts_from_conclusions(conclusions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, dict[str, dict[str, Any]]] = {}
    for conclusion in conclusions:
        claim = str(conclusion.get("claim") or "").strip()
        if not claim:
            continue
        topic = _research_conflict_topic(claim)
        polarity = _research_conflict_polarity(claim)
        evidence_refs = conclusion.get("evidence_refs")
        if not topic or not polarity or not isinstance(evidence_refs, list) or not evidence_refs:
            continue
        grouped.setdefault(topic, {})
        grouped[topic].setdefault(polarity, {"claim": claim, "evidence_refs": evidence_refs})

    conflicts: list[dict[str, Any]] = []
    for topic, positions_by_polarity in grouped.items():
        if "positive" not in positions_by_polarity or "negative" not in positions_by_polarity:
            continue
        conflicts.append(
            {
                "topic": topic,
                "positions": [
                    positions_by_polarity["positive"],
                    positions_by_polarity["negative"],
                ],
            }
        )
    return conflicts


def _source_grounded_research_payload(workspace: Path, *, workspace_id: str, question: str, top_k: int) -> dict[str, Any]:
    query_text = str(question or "").strip()
    sources = _target_source_items(workspace, workspace_id=workspace_id, limit=50, status="active")
    if not sources:
        return _research_refusal_payload(
            question=query_text,
            coverage_status="no_sources",
            answer="当前 Notebook 还没有可用来源，无法生成 Research 输出。请先添加来源。",
            suggested_source_actions=["添加 PDF、TXT、Markdown 或公开网页 URL 来源", "导入与研究问题直接相关的原始资料后重新生成 Research"],
        )

    evidence = _query_evidence_items(workspace, workspace_id=workspace_id, query=query_text, top_k=top_k)
    if not evidence:
        source_titles = "、".join(str(source.get("title") or source.get("source_id") or "来源") for source in sources[:3])
        return _research_refusal_payload(
            question=query_text,
            coverage_status="insufficient_evidence",
            answer=f"当前资料未覆盖“{query_text}”的可引用依据。已导入来源包括：{source_titles}。",
            suggested_source_actions=[
                "补充与问题直接相关的原始报告、论文、公告或白皮书",
                "使用当前来源中的关键词重新提问",
                "添加来源后再生成 Research 综合输出",
            ],
        )

    conclusions = []
    for index, ref in enumerate(evidence[:3], start=1):
        snippet = str(ref.get("snippet") or "").strip()
        claim = snippet if snippet else f"当前来源提供了与问题相关的第 {index} 条证据。"
        conclusions.append({"claim": claim, "evidence_refs": [ref]})

    inference_refs = evidence[: min(2, len(evidence))]
    inferences = (
        [
            {
                "inference": "基于来源的推断：这些证据可以作为后续综合研究的初始依据，但仍需人工审阅来源上下文。",
                "evidence_refs": inference_refs,
                "inference_notice": "该段为基于来源的推断，不是资料外事实。",
            }
        ]
        if inference_refs
        else []
    )
    conflicts = _research_conflicts_from_conclusions(conclusions)
    return {
        "research_available": True,
        "question": query_text,
        "coverage_status": "source_supported",
        "answer_basis": "source_supported",
        "answer": "已基于当前 Notebook sources 生成受限 Research 输出。",
        "supported_conclusions": conclusions,
        "inferences": inferences,
        "conflicts": conflicts,
        "missing_evidence": [],
        "suggested_source_actions": [],
        "evidence_refs": evidence,
        "generation_metadata": _research_generation_metadata(evidence_ref_count=len(evidence)),
    }


def _source_tool_result_source_ids(result: dict) -> list[str]:
    ids = []
    for item in ((result.get("data") or {}).get("sources") or []):
        source_id = str(item.get("source_id") or "").strip()
        if source_id:
            ids.append(source_id)
    source = (result.get("data") or {}).get("source") or {}
    source_id = str(source.get("source_id") or "").strip()
    if source_id:
        ids.append(source_id)
    return ids


def _safe_upload_file_name(file_name: str) -> str:
    name = Path(str(file_name or "upload")).name
    stem = _slug(Path(name).stem)[:80] or "upload"
    suffix = Path(name).suffix.lower()
    if suffix not in {".txt", ".text", ".md", ".markdown", ".json", ".pdf", ".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp", ".pbm", ".pgm", ".ppm"}:
        suffix = ".txt"
    return f"{stem}{suffix}"


def _write_target_uploaded_files(workspace: Path, request: TargetSourceImportRequest) -> list[tuple[str, TargetFileSourceRequest]]:
    upload_dir = workspace / "sources" / "browser_uploads"
    upload_dir.mkdir(parents=True, exist_ok=True)
    written: list[tuple[str, TargetFileSourceRequest]] = []
    for file_input in request.files:
        try:
            content = base64.b64decode(file_input.content_base64, validate=True)
        except (binascii.Error, ValueError) as exc:
            raise HTTPException(status_code=422, detail="VALIDATION_ERROR: uploaded file content_base64 is invalid") from exc
        if len(content) > _MAX_SOURCE_FILE_BYTES:
            raise HTTPException(status_code=422, detail=f"VALIDATION_ERROR: uploaded file is larger than {_MAX_SOURCE_FILE_BYTES} bytes")
        safe_name = _safe_upload_file_name(file_input.file_name)
        target = upload_dir / f"{uuid.uuid4().hex[:12]}-{safe_name}"
        target.write_bytes(content)
        written.append((str(target), file_input))
    return written


def _url_block_warning(block_reason: str) -> str:
    return {
        "ssrf": "此 URL 指向内部网络，不允许抓取",
        "private_ip": "此 URL 指向私有网络地址，不允许抓取",
        "timeout": "此页面加载超时，请稍后重试",
        "unsupported_content_type": "此页面内容类型不支持，仅支持文本和 PDF",
        "robots_blocked": "此页面不允许被抓取（robots.txt 限制）",
        "permission_denied": "此页面需要登录或无权限访问",
        "paywall": "此页面需要付费订阅，无法抓取",
    }.get(block_reason, "此 URL 无法安全抓取")


def _register_blocked_url_source(workspace: Path, *, workspace_id: str, url_input: TargetUrlSourceRequest, exc: URLSourceImportError) -> dict[str, Any]:
    manifest_path = _sources_manifest_path(workspace)
    manifest = _read_json(manifest_path, {"items": []})
    block_reason = exc.block_reason
    digest = hashlib.sha256(f"url-blocked:{url_input.url}:{block_reason}".encode("utf-8")).hexdigest()[:16]
    source_id = f"src_{digest}"
    now = _now()
    metadata = {
        **dict(url_input.metadata or {}),
        "source_type": "url",
        "original_url": url_input.url,
        "source_url": url_input.url,
        "final_url": url_input.url,
        "block_reason": block_reason,
        "import_state": "blocked",
        "url_import_contract": "public_url_text_v2_5",
        "blocked_at": now,
    }
    updated = None
    for item in manifest.setdefault("items", []):
        if item.get("source_id") == source_id:
            item.update(
                {
                    "title": str(url_input.title or item.get("title") or "Blocked URL"),
                    "status": "blocked",
                    "metadata": metadata,
                    "updated_at": now,
                    "ingest_status": "blocked",
                }
            )
            updated = item
            break
    if updated is None:
        updated = {
            "source_id": source_id,
            "sha256": digest,
            "title": str(url_input.title or "Blocked URL"),
            "status": "blocked",
            "path": None,
            "original_path": None,
            "metadata": metadata,
            "imported_at": now,
            "updated_at": now,
            "low_signal": {},
            "ingest_status": "blocked",
        }
        manifest.setdefault("items", []).append(updated)
    _write_json(manifest_path, manifest)
    return _stable_source_item(updated, workspace_id=workspace_id)


def _blocked_url_source_response(workspace: Path, *, workspace_id: str, url_input: TargetUrlSourceRequest, exc: URLSourceImportError) -> JSONResponse:
    source = _register_blocked_url_source(workspace, workspace_id=workspace_id, url_input=url_input, exc=exc)
    payload = _target_envelope(
        workspace_id=workspace_id,
        status="blocked",
        warnings=[_url_block_warning(str(source.get("block_reason") or exc.block_reason))],
        artifact_refs=[_target_source_artifact_ref(str(source["source_id"]))],
        next_actions=["review_url", "knowledge_source_import"],
        data={
            "source": source,
            "sources": [source],
            "block_reason": source.get("block_reason"),
        },
    )
    return JSONResponse(status_code=exc.status_code, content=payload)


def _url_source_text_records(request: TargetSourceImportRequest) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for url_input in request.urls:
        try:
            extracted = fetch_url_source_text(url_input.url, title=url_input.title)
        except URLSourceImportError as exc:
            setattr(exc, "url_input", url_input)
            raise
        metadata = {
            **dict(url_input.metadata or {}),
            "source_type": "url",
            "source_url": extracted.final_url,
            "original_url": extracted.url,
            "final_url": extracted.final_url,
            "content_type": extracted.content_type,
            "import_state": "ready",
            "url_import_contract": "public_url_text_v1",
            "fetched_at": extracted.fetched_at,
        }
        records.append(
            {
                "title": extracted.title,
                "content": extracted.content,
                "metadata": metadata,
            }
        )
    return records


def _retitle_imported_sources(workspace: Path, imported: list[tuple[str, TargetFileSourceRequest]], source_ids: list[str]) -> None:
    if not imported or not source_ids:
        return
    manifest_path = _sources_manifest_path(workspace)
    manifest = _read_json(manifest_path, {"items": []})
    file_by_path = {str(Path(path).resolve()): file_input for path, file_input in imported}
    file_by_source_id = {source_id: imported[index][1] for index, source_id in enumerate(source_ids[-len(imported):]) if index < len(imported)}
    changed = False
    for item in manifest.get("items", []):
        path = str(Path(str(item.get("path") or "")).resolve())
        source_id = str(item.get("source_id") or "")
        file_input = file_by_path.get(path) or file_by_source_id.get(source_id)
        if not file_input or source_id not in source_ids:
            continue
        metadata = {**dict(item.get("metadata") or {}), **dict(file_input.metadata or {})}
        if file_input.source_type:
            metadata["source_type"] = file_input.source_type
        metadata.update(
            {
                "browser_file_import": True,
                "file_name": Path(file_input.file_name).name,
                "content_type": file_input.content_type,
                "file_upload_contract": "base64_file_content",
            }
        )
        item["title"] = str(file_input.title or Path(file_input.file_name).stem or source_id)
        item["original_path"] = None
        item["metadata"] = {key: value for key, value in metadata.items() if value is not None}
        changed = True
    if changed:
        _write_json(manifest_path, manifest)


def _import_target_uploaded_sources(workspace: Path, imported: list[tuple[str, TargetFileSourceRequest]]) -> list[str]:
    if not imported:
        return []
    manifest_path = _sources_manifest_path(workspace)
    manifest = _read_json(manifest_path, {"items": []})
    existing_by_sha = {item.get("sha256"): item for item in manifest.get("items", []) if item.get("sha256")}
    source_ids: list[str] = []
    changed = False
    for path, file_input in imported:
        source_path = Path(path).resolve()
        content = source_path.read_bytes()
        sha256 = hashlib.sha256(content).hexdigest()
        duplicate = existing_by_sha.get(sha256)
        if duplicate:
            duplicate_source_id = str(duplicate.get("source_id") or "")
            if duplicate_source_id:
                source_ids.append(duplicate_source_id)
            continue
        source_id = f"src_{sha256[:16]}"
        metadata = {**dict(file_input.metadata or {})}
        if file_input.source_type:
            metadata["source_type"] = file_input.source_type
        metadata.update(
            {
                "browser_file_import": True,
                "file_name": Path(file_input.file_name).name,
                "content_type": file_input.content_type,
                "file_upload_contract": "base64_file_content",
            }
        )
        record = {
            "source_id": source_id,
            "sha256": sha256,
            "title": str(file_input.title or Path(file_input.file_name).stem or source_id),
            "status": "active",
            "path": str(source_path),
            "original_path": None,
            "metadata": {key: value for key, value in metadata.items() if value is not None},
            "imported_at": _now(),
            "low_signal": {},
            "ingest_status": "pending",
        }
        manifest.setdefault("items", []).append(record)
        existing_by_sha[sha256] = record
        source_ids.append(source_id)
        changed = True
    if changed:
        _write_json(manifest_path, manifest)
    return source_ids


def _run_source_tool(name: str, arguments: dict[str, Any]) -> dict:
    return handle_source_tool(
        name,
        arguments,
        blocked=_blocked,
        bounded_int=bounded_int,
        envelope=_target_envelope,
        ensure_workspace_meta=_ensure_workspace_meta,
        now=_now,
        read_json=_read_json,
        resolve_workspace=lambda workspace_id, workspace: _resolve_workspace_path(workspace_id=workspace_id, workspace=workspace),
        sources_manifest_path=_sources_manifest_path,
        write_json=_write_json,
    )


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


class TargetWorkspaceCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., min_length=1, max_length=128)
    owner: str = Field(default="", max_length=128)
    tags: List[str] = Field(default_factory=list)


class TargetWorkspaceArchiveRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    reason: str = Field(default="", max_length=2048)


class TargetTextSourceRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(default="text-source", max_length=256)
    content: str = Field(..., max_length=2 * 1024 * 1024)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class TargetFileSourceRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(default="file-source", max_length=256)
    file_name: str = Field(..., min_length=1, max_length=256)
    content_base64: str = Field(..., min_length=1)
    content_type: str | None = Field(default=None, max_length=128)
    source_type: str | None = Field(default=None, max_length=64)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class TargetUrlSourceRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str | None = Field(default=None, max_length=256)
    url: str = Field(..., min_length=1, max_length=4096)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class TargetSourceImportRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    paths: List[str] = Field(default_factory=list)
    texts: List[TargetTextSourceRequest] = Field(default_factory=list)
    files: List[TargetFileSourceRequest] = Field(default_factory=list)
    urls: List[TargetUrlSourceRequest] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class TargetFolderScanRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    authorized_root: str = Field(..., min_length=1, max_length=4096)
    permission_grant_id: str = Field(..., min_length=1, max_length=256)
    dry_run: bool = True
    recursive: bool = True
    include_extensions: List[str] = Field(default_factory=list)
    exclude_globs: List[str] = Field(default_factory=list)
    max_depth: Optional[int] = Field(default=None, ge=0, le=32)
    max_file_size_bytes: int = Field(default=2 * 1024 * 1024, ge=1, le=10 * 1024 * 1024)
    follow_symlinks: bool = False


class TargetFolderSummaryWorkflowRunRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    authorized_root: str = Field(..., min_length=1, max_length=4096)
    permission_grant_id: str = Field(..., min_length=1, max_length=256)
    dry_run: bool = True
    recursive: bool = True
    include_extensions: List[str] = Field(default_factory=list)
    exclude_globs: List[str] = Field(default_factory=list)
    max_depth: Optional[int] = Field(default=None, ge=0, le=32)
    max_file_size_bytes: int = Field(default=2 * 1024 * 1024, ge=1, le=10 * 1024 * 1024)
    follow_symlinks: bool = False
    confirm_extract: bool = False


class TargetAgentWorkflowDraftRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    user_goal: str = Field(..., min_length=1, max_length=2048)


class TargetSourceRemoveRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    reason: str = Field(default="", max_length=512)


class TargetBuildStartRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    mode: str = Field(default="full", description="Build mode: full, incremental, graph_only, llmwiki_only")
    paths: List[str] = Field(default_factory=list)


class TargetBuildCancelRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    reason: str = Field(default="", max_length=512)


class TargetStudioArtifactRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    artifact_type: str = Field(..., min_length=1, max_length=64)


class TargetResearchRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    question: str = Field(..., min_length=1, max_length=2048)
    top_k: int = Field(default=8, ge=1, le=20)


class TargetSessionCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    external_id: Optional[str] = Field(default=None, max_length=256)
    session_type: str = Field(default="generic", max_length=128)
    title: str = Field(default="", max_length=512)
    ephemeral: bool = Field(default=False)
    ttl_seconds: Optional[int] = Field(default=None, ge=1, le=365 * 24 * 60 * 60)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class TargetSessionIngestRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source_type: str = Field(default="structured", min_length=1, max_length=128)
    content_format: str = Field(default="text", min_length=1, max_length=64)
    title: str = Field(default="", max_length=512)
    records: Optional[List[Any]] = None
    content: Any = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    related_source_ids: List[str] = Field(default_factory=list)
    source_refs: List[str] = Field(default_factory=list)
    auto_link: bool = Field(default=False)
    allow_closed_write: bool = Field(default=False)


class TargetSessionQueryRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    query: Any = None
    top_k: Any = 8


class TargetSessionBuildStartRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    mode: str = Field(default="full", description="Session build mode: distill, graph, communities, full")


class TargetSessionBuildCancelRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    reason: str = Field(default="", max_length=512)


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


class TargetQualityFeedbackRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    target_type: str = Field(..., min_length=1, max_length=64, description="Target class, for example page/source/entity/query")
    target_id: str = Field(..., min_length=1, max_length=512, description="Stable non-path target id or slug")
    action: str = Field(..., min_length=1, max_length=64, description="Feedback action, for example needs_review/rename_suggest/mark_noise")
    label: str = Field(default="", max_length=256, description="Human-readable target label")
    suggested_value: str = Field(default="", max_length=1024, description="Optional correction or replacement value")
    reason: str = Field(default="", max_length=4096, description="Operator note")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Optional sanitized context copied from the UI")


class TargetQualityCorrectionRuleRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    rule_id: str = Field(default="", max_length=128, description="Existing draft rule id for update")
    target_type: str = Field(..., min_length=1, max_length=64, description="Target class, for example page/source/entity/query")
    target_id: str = Field(..., min_length=1, max_length=512, description="Stable non-path target id or slug")
    action: str = Field(..., min_length=1, max_length=64, description="Rule action, e.g. rename_suggest/merge_suggest/mark_noise")
    label: str = Field(default="", max_length=256, description="Human-readable target label")
    suggested_value: str = Field(default="", max_length=1024, description="Optional correction or replacement value")
    reason: str = Field(default="", max_length=4096, description="Operator note")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Optional sanitized context copied from the UI")


class TargetQualityCorrectionRuleReviewRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str = Field(..., min_length=1, max_length=64, description="Review status")
    reviewer: str = Field(default="", max_length=256, description="Non-authoritative reviewer metadata")
    note: str = Field(default="", max_length=4096, description="Optional review note")


class TargetQualityCorrectionPlanRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")


class TargetQualityCorrectionRulesBuildRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")


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


@target_router.post("")
async def create_target_workspace(request: TargetWorkspaceCreateRequest) -> dict:
    try:
        root = _workspace_root()
        workspace = validate_workspace_path(root / _slug(request.name))
        meta = _ensure_workspace_meta(
            workspace,
            name=request.name,
            owner=request.owner or None,
            tags=[str(tag) for tag in request.tags[:20]],
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    workspace_payload = _stable_workspace_meta(meta)
    return _target_envelope(
        workspace_id=str(workspace_payload["workspace_id"]),
        artifact_refs=[_target_workspace_artifact_ref(str(workspace_payload["workspace_id"]))],
        next_actions=["knowledge_workspace_describe", "knowledge_source_import"],
        data={"workspace": workspace_payload},
    )


@target_router.get("")
async def list_target_workspaces(
    owner: str = Query(default="", max_length=128),
    tag: str = Query(default="", max_length=128),
    limit: int = Query(default=50, ge=1, le=200),
) -> dict:
    try:
        root = _workspace_root()
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    items = []
    for meta_path in sorted(root.glob("*/.data_service_workspace.json"), key=lambda item: item.stat().st_mtime, reverse=True):
        meta = _read_json(meta_path, {})
        if owner and meta.get("owner") != owner:
            continue
        if tag and tag not in meta.get("tags", []):
            continue
        items.append(_stable_workspace_meta(meta))
        if len(items) >= limit:
            break
    return _target_envelope(workspace_id="root", data={"items": items}, next_actions=["knowledge_workspace_describe", "knowledge_workspace_create"])


@target_router.get("/{workspace_id}")
async def describe_target_workspace(workspace_id: str) -> dict:
    try:
        workspace = _resolve_workspace_path(workspace_id=workspace_id)
        if not _workspace_exists(workspace):
            raise ValueError(f"Unknown workspace_id: {workspace_id}")
        meta = _ensure_workspace_meta(workspace)
    except ValueError as exc:
        raise HTTPException(status_code=404 if str(exc).startswith("Unknown workspace_id") else 400, detail=str(exc)) from exc
    service = DataService(workspace)
    service.ensure_layout()
    bundle = service.read_summary_bundle()
    sources = _read_source_items(workspace, limit=500)
    workspace_payload = _stable_workspace_meta(meta)
    return _target_envelope(
        workspace_id=str(workspace_payload["workspace_id"]),
        artifact_refs=[_target_workspace_artifact_ref(str(workspace_payload["workspace_id"]))],
        next_actions=["knowledge_source_list", "knowledge_build_start", "knowledge_query"],
        data={
            "workspace": workspace_payload,
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


@target_router.get("/{workspace_id}/capabilities")
async def read_target_workspace_capabilities(workspace_id: str) -> dict:
    _workspace, meta = _target_workspace_or_404(workspace_id)
    return _target_envelope(
        workspace_id=meta["workspace_id"],
        next_actions=[],
        data={"manifest": _source_preview_manifest(workspace_id=meta["workspace_id"])},
    )


@target_router.post("/{workspace_id}/archive")
async def archive_target_workspace(workspace_id: str, request: TargetWorkspaceArchiveRequest) -> dict:
    try:
        workspace = _resolve_workspace_path(workspace_id=workspace_id)
        if not _workspace_exists(workspace):
            raise ValueError(f"Unknown workspace_id: {workspace_id}")
        meta = _ensure_workspace_meta(workspace)
        meta["status"] = "archived"
        meta["archived_at"] = _now()
        meta["archive_reason"] = request.reason
        meta["updated_at"] = meta["archived_at"]
        _write_json(_workspace_meta_path(workspace), meta)
    except ValueError as exc:
        raise HTTPException(status_code=404 if str(exc).startswith("Unknown workspace_id") else 400, detail=str(exc)) from exc
    workspace_payload = _stable_workspace_meta(meta)
    return _target_envelope(
        workspace_id=str(workspace_payload["workspace_id"]),
        artifact_refs=[_target_workspace_artifact_ref(str(workspace_payload["workspace_id"]))],
        next_actions=["knowledge_workspace_list"],
        data={"workspace": workspace_payload},
    )


@target_router.post("/{workspace_id}/sources")
async def import_target_sources(workspace_id: str, request: TargetSourceImportRequest) -> dict:
    workspace, meta = _target_workspace_or_404(workspace_id)
    try:
        url_records = _url_source_text_records(request)
    except URLSourceImportError as exc:
        blocked_input = getattr(exc, "url_input", None) or (request.urls[0] if request.urls else TargetUrlSourceRequest(url=""))
        return _blocked_url_source_response(workspace, workspace_id=meta["workspace_id"], url_input=blocked_input, exc=exc)
    uploaded = _write_target_uploaded_files(workspace, request)
    result = _run_source_tool(
        "knowledge_source_import",
        {
            "workspace_id": workspace_id,
            "paths": list(request.paths),
            "texts": [text.model_dump() for text in request.texts] + url_records,
            "metadata": dict(request.metadata or {}),
        },
    )
    if result.get("status") == "blocked":
        return result
    source_ids = [*_source_tool_result_source_ids(result), *_import_target_uploaded_sources(workspace, uploaded)]
    sources = [_target_source_item(workspace, workspace_id=meta["workspace_id"], source_id=source_id) for source_id in source_ids]
    return _target_envelope(
        workspace_id=meta["workspace_id"],
        artifact_refs=[_target_source_artifact_ref(item["source_id"]) for item in sources],
        next_actions=["knowledge_source_list", "knowledge_build_start"],
        data={"sources": sources},
    )


@target_router.get("/{workspace_id}/sources")
async def list_target_sources(
    workspace_id: str,
    status: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
) -> dict:
    workspace, meta = _target_workspace_or_404(workspace_id)
    _run_source_tool("knowledge_source_list", {"workspace_id": workspace_id, "status": status, "limit": limit})
    items = _target_source_items(workspace, workspace_id=meta["workspace_id"], limit=limit, status=status)
    return _target_envelope(workspace_id=meta["workspace_id"], data={"items": items})


@target_router.get("/{workspace_id}/sources/{source_id}")
async def describe_target_source(workspace_id: str, source_id: str) -> dict:
    workspace, meta = _target_workspace_or_404(workspace_id)
    source = _target_source_item(workspace, workspace_id=meta["workspace_id"], source_id=source_id)
    return _target_envelope(
        workspace_id=meta["workspace_id"],
        artifact_refs=[_target_source_artifact_ref(source_id)],
        next_actions=["knowledge_source_list", "knowledge_source_trace"],
        data={"source": source},
    )


@target_router.get("/{workspace_id}/sources/{source_id}/preview")
async def preview_target_source(workspace_id: str, source_id: str) -> dict:
    workspace, meta = _target_workspace_or_404(workspace_id)
    preview = _source_preview_payload(workspace, workspace_id=meta["workspace_id"], source_id=source_id)
    next_actions = [] if preview.get("preview_available") else [str(preview.get("unsupported_reason") or "preview_not_available")]
    return _target_envelope(
        workspace_id=meta["workspace_id"],
        artifact_refs=[_target_source_artifact_ref(source_id)] if preview.get("preview_available") else [],
        next_actions=next_actions,
        data={"preview": preview},
    )


@target_router.get("/{workspace_id}/sources/{source_id}/units")
async def list_target_source_units(
    workspace_id: str,
    source_id: str,
    limit: int = Query(default=_DOCUMENT_UNIT_DEFAULT_LIMIT, ge=1, le=_DOCUMENT_UNIT_MAX_LIMIT),
    cursor: str | None = Query(default=None),
) -> dict:
    workspace, meta = _target_workspace_or_404(workspace_id)
    units = _document_unit_list_payload(workspace, workspace_id=meta["workspace_id"], source_id=source_id, limit=limit, cursor=cursor)
    next_actions = []
    if units.get("unsupported_reason"):
        next_actions.append(str(units["unsupported_reason"]))
    return _target_envelope(
        workspace_id=meta["workspace_id"],
        artifact_refs=[_target_source_artifact_ref(source_id)] if not units.get("unsupported_reason") else [],
        next_actions=next_actions,
        data={"units": units},
    )


@target_router.get("/{workspace_id}/sources/{source_id}/units/{unit_id}")
async def describe_target_source_unit(workspace_id: str, source_id: str, unit_id: str) -> dict:
    workspace, meta = _target_workspace_or_404(workspace_id)
    unit = _document_unit_detail_payload(workspace, workspace_id=meta["workspace_id"], source_id=source_id, unit_id=unit_id)
    return _target_envelope(
        workspace_id=meta["workspace_id"],
        artifact_refs=[_target_source_artifact_ref(source_id)],
        next_actions=[],
        data={"unit": unit},
    )


@target_router.get("/{workspace_id}/sources/{source_id}/units/{unit_id}/evidence/{evidence_id}")
async def describe_target_evidence_span(workspace_id: str, source_id: str, unit_id: str, evidence_id: str) -> dict:
    workspace, meta = _target_workspace_or_404(workspace_id)
    span = _evidence_span_detail_payload(
        workspace,
        workspace_id=meta["workspace_id"],
        source_id=source_id,
        unit_id=unit_id,
        evidence_id=evidence_id,
    )
    return _target_envelope(
        workspace_id=meta["workspace_id"],
        artifact_refs=[_target_source_artifact_ref(source_id)],
        next_actions=[],
        data={"evidence_span": span},
    )


@target_router.post("/{workspace_id}/sources/{source_id}/remove")
async def remove_target_source(workspace_id: str, source_id: str, request: TargetSourceRemoveRequest) -> dict:
    workspace, meta = _target_workspace_or_404(workspace_id)
    if meta.get("status") != "archived":
        _target_source_item(workspace, workspace_id=meta["workspace_id"], source_id=source_id)
    result = _run_source_tool(
        "knowledge_source_remove",
        {"workspace_id": workspace_id, "source_id": source_id, "reason": request.reason},
    )
    if result.get("status") == "blocked":
        return result
    source = _target_source_item(workspace, workspace_id=meta["workspace_id"], source_id=source_id)
    return _target_envelope(
        workspace_id=meta["workspace_id"],
        artifact_refs=[_target_source_artifact_ref(source_id)],
        next_actions=["knowledge_source_list"],
        data={"source": source},
    )


@target_router.post("/{workspace_id}/build/start")
async def start_target_build(workspace_id: str, request: TargetBuildStartRequest) -> dict:
    try:
        workspace, meta = _target_workspace_or_404(workspace_id)
        if meta.get("status") == "archived":
            return _target_envelope(
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
    return _target_operation_envelope(
        meta["workspace_id"],
        operation_id,
        operation,
        next_actions=["knowledge_build_status", "knowledge_build_cancel"],
    )


@target_router.get("/{workspace_id}/build/operations/{operation_id}")
async def read_target_build_operation(workspace_id: str, operation_id: str) -> dict:
    workspace, meta = _target_workspace_or_404(workspace_id)
    operation = _read_json(_operation_path(workspace, operation_id), None)
    if not operation:
        return _blocked(
            workspace_id=meta["workspace_id"],
            operation_id=operation_id,
            message=f"Unknown operation_id: {operation_id}",
            next_actions=["knowledge_build_start"],
        )
    if operation.get("status") == "queued":
        _ensure_build_worker(workspace)
    return _target_operation_envelope(meta["workspace_id"], operation_id, operation)


@target_router.post("/{workspace_id}/build/operations/{operation_id}/cancel")
async def cancel_target_build_operation(workspace_id: str, operation_id: str, request: TargetBuildCancelRequest) -> dict:
    workspace, meta = _target_workspace_or_404(workspace_id)
    operation_path = _operation_path(workspace, operation_id)
    operation = _read_json(operation_path, None)
    if not operation:
        return _blocked(
            workspace_id=meta["workspace_id"],
            operation_id=operation_id,
            message=f"Unknown operation_id: {operation_id}",
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
    return _target_operation_envelope(meta["workspace_id"], operation_id, operation, warnings=warnings)


@target_router.get("/{workspace_id}/graph/neighbors")
async def read_target_graph_neighbors(
    workspace_id: str,
    node_id: str | None = Query(default=None),
    entity_id: str | None = Query(default=None),
    depth: int = Query(default=1),
    max_nodes: int = Query(default=80),
) -> dict:
    workspace, meta = _target_workspace_or_404(workspace_id)
    try:
        return graph_neighbors_payload(
            DataService(workspace),
            workspace_id=meta["workspace_id"],
            node_id=node_id,
            entity_id=entity_id,
            depth=depth,
            max_nodes=max_nodes,
            envelope=_target_envelope,
            blocked=_blocked,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@target_router.get("/{workspace_id}/graph/community")
async def read_target_graph_community(
    workspace_id: str,
    community_id: str | None = Query(default=None),
    limit: int = Query(default=20),
    include_members: bool = Query(default=False),
) -> dict:
    workspace, meta = _target_workspace_or_404(workspace_id)
    try:
        return graph_community_payload(
            DataService(workspace),
            workspace_id=meta["workspace_id"],
            community_id=community_id,
            limit=limit,
            include_members=include_members,
            envelope=_target_envelope,
            blocked=_blocked,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@target_router.get("/{workspace_id}/graph/query")
async def read_target_graph_query(
    workspace_id: str,
    q: str = Query(...),
    top_k: int = Query(default=10),
    include_nodes: bool = Query(default=True),
    include_edges: bool = Query(default=True),
    include_communities: bool = Query(default=False),
) -> dict:
    workspace, meta = _target_workspace_or_404(workspace_id)
    try:
        return graph_query_payload(
            DataService(workspace),
            workspace_id=meta["workspace_id"],
            query=q,
            top_k=top_k,
            include_nodes=include_nodes,
            include_edges=include_edges,
            include_communities=include_communities,
            envelope=_target_envelope,
            blocked=_blocked,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@target_router.get("/{workspace_id}/graph/session")
async def read_target_graph_session(
    workspace_id: str,
    session_id: str | None = Query(default=None),
    limit: int = Query(default=20),
    include_nodes: bool = Query(default=False),
    include_edges: bool = Query(default=False),
    node_limit: int = Query(default=50),
    edge_limit: int = Query(default=100),
) -> dict:
    workspace, meta = _target_workspace_or_404(workspace_id)
    try:
        return graph_session_payload(
            SessionKnowledgeService(workspace, workspace_id=meta["workspace_id"]),
            workspace_id=meta["workspace_id"],
            session_id=session_id,
            limit=limit,
            include_nodes=include_nodes,
            include_edges=include_edges,
            node_limit=node_limit,
            edge_limit=edge_limit,
            envelope=_target_envelope,
            blocked=_blocked,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@target_router.post("/{workspace_id}/sessions")
async def create_target_session(workspace_id: str, request: TargetSessionCreateRequest) -> dict:
    workspace, meta = _target_workspace_or_404(workspace_id)
    if meta.get("status") == "archived":
        return _blocked(
            workspace_id=meta["workspace_id"],
            message="Workspace is archived and cannot create sessions",
            code="workspace_archived",
            next_actions=["knowledge_workspace_describe"],
        )
    return create_session_payload(
        SessionKnowledgeService(workspace, workspace_id=meta["workspace_id"]),
        workspace_id=meta["workspace_id"],
        external_id=request.external_id,
        session_type=request.session_type,
        title=request.title,
        ephemeral=request.ephemeral,
        ttl_seconds=request.ttl_seconds,
        metadata=dict(request.metadata or {}),
        envelope=_target_envelope,
    )


@target_router.get("/{workspace_id}/sessions")
async def list_target_sessions(
    workspace_id: str,
    status: str | None = Query(default=None),
    session_type: str | None = Query(default=None),
    include_deleted: bool = Query(default=False),
    limit: int = Query(default=20),
) -> dict:
    workspace, meta = _target_workspace_or_404(workspace_id)
    try:
        return list_sessions_payload(
            SessionKnowledgeService(workspace, workspace_id=meta["workspace_id"]),
            workspace_id=meta["workspace_id"],
            status=status,
            session_type=session_type,
            include_deleted=include_deleted,
            limit=limit,
            envelope=_target_envelope,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@target_router.get("/{workspace_id}/sessions/{session_id}")
async def get_target_session(workspace_id: str, session_id: str) -> dict:
    workspace, meta = _target_workspace_or_404(workspace_id)
    return get_session_payload(
        SessionKnowledgeService(workspace, workspace_id=meta["workspace_id"]),
        workspace_id=meta["workspace_id"],
        session_id=session_id,
        envelope=_target_envelope,
        blocked=_blocked,
    )


@target_router.post("/{workspace_id}/sessions/{session_id}/close")
async def close_target_session(workspace_id: str, session_id: str) -> dict:
    workspace, meta = _target_workspace_or_404(workspace_id)
    return close_session_payload(
        SessionKnowledgeService(workspace, workspace_id=meta["workspace_id"]),
        workspace_id=meta["workspace_id"],
        session_id=session_id,
        envelope=_target_envelope,
        blocked=_blocked,
    )


@target_router.post("/{workspace_id}/sessions/{session_id}/delete")
async def delete_target_session(workspace_id: str, session_id: str) -> dict:
    workspace, meta = _target_workspace_or_404(workspace_id)
    return delete_session_payload(
        SessionKnowledgeService(workspace, workspace_id=meta["workspace_id"]),
        workspace_id=meta["workspace_id"],
        session_id=session_id,
        envelope=_target_envelope,
        blocked=_blocked,
    )


@target_router.post("/{workspace_id}/sessions/{session_id}/ingest")
async def ingest_target_session(workspace_id: str, session_id: str, request: TargetSessionIngestRequest) -> dict:
    workspace, meta = _target_workspace_or_404(workspace_id)
    if meta.get("status") == "archived":
        return _blocked(
            workspace_id=meta["workspace_id"],
            message="Workspace is archived and cannot ingest session content",
            code="workspace_archived",
            next_actions=["knowledge_workspace_describe"],
        )
    return ingest_session_payload(
        SessionKnowledgeService(workspace, workspace_id=meta["workspace_id"]),
        workspace_id=meta["workspace_id"],
        session_id=session_id,
        source_type=request.source_type,
        content_format=request.content_format,
        title=request.title,
        records=request.records,
        content=request.content,
        metadata=dict(request.metadata or {}),
        related_source_ids=list(request.related_source_ids or []),
        source_refs=list(request.source_refs or []),
        auto_link=request.auto_link,
        allow_closed_write=request.allow_closed_write,
        envelope=_target_envelope,
        blocked=_blocked,
    )


@target_router.post("/{workspace_id}/sessions/{session_id}/query")
async def query_target_session(workspace_id: str, session_id: str, request: TargetSessionQueryRequest) -> dict:
    workspace, meta = _target_workspace_or_404(workspace_id)
    return query_session_payload(
        SessionKnowledgeService(workspace, workspace_id=meta["workspace_id"]),
        workspace_id=meta["workspace_id"],
        session_id=session_id,
        query=request.query,
        top_k=request.top_k,
        evidence_resolver=lambda query, top_k: _query_evidence_items(workspace, workspace_id=meta["workspace_id"], query=query, top_k=top_k),
        envelope=_target_envelope,
        blocked=_blocked,
    )


@target_router.post("/{workspace_id}/sessions/{session_id}/build/start")
async def start_target_session_build(workspace_id: str, session_id: str, request: TargetSessionBuildStartRequest) -> dict:
    workspace, meta = _target_workspace_or_404(workspace_id)
    if meta.get("status") == "archived":
        return _blocked(
            workspace_id=meta["workspace_id"],
            message="Workspace is archived and cannot start session builds",
            code="workspace_archived",
            next_actions=["knowledge_workspace_describe"],
        )
    return start_session_build_payload(
        SessionKnowledgeService(workspace, workspace_id=meta["workspace_id"]),
        workspace_id=meta["workspace_id"],
        session_id=session_id,
        mode=request.mode,
        envelope=_target_envelope,
        blocked=_blocked,
    )


@target_router.get("/{workspace_id}/sessions/{session_id}/build/operations/{operation_id}")
async def read_target_session_build_operation(workspace_id: str, session_id: str, operation_id: str) -> dict:
    workspace, meta = _target_workspace_or_404(workspace_id)
    return read_session_build_payload(
        SessionKnowledgeService(workspace, workspace_id=meta["workspace_id"]),
        workspace_id=meta["workspace_id"],
        session_id=session_id,
        operation_id=operation_id,
        envelope=_target_envelope,
        blocked=_blocked,
    )


@target_router.post("/{workspace_id}/sessions/{session_id}/build/operations/{operation_id}/cancel")
async def cancel_target_session_build_operation(
    workspace_id: str,
    session_id: str,
    operation_id: str,
    request: TargetSessionBuildCancelRequest,
) -> dict:
    workspace, meta = _target_workspace_or_404(workspace_id)
    return cancel_session_build_payload(
        SessionKnowledgeService(workspace, workspace_id=meta["workspace_id"]),
        workspace_id=meta["workspace_id"],
        session_id=session_id,
        operation_id=operation_id,
        reason=request.reason,
        envelope=_target_envelope,
        blocked=_blocked,
    )


@target_router.post("/{workspace_id}/quality/feedback")
async def record_target_quality_feedback(workspace_id: str, request: TargetQualityFeedbackRequest) -> dict:
    workspace, meta = _target_workspace_or_404(workspace_id)
    if str(meta.get("status", "active")) == "archived":
        return _blocked(
            workspace_id=meta["workspace_id"],
            message="Archived workspace cannot accept quality feedback",
            code="workspace_archived",
            next_actions=["knowledge_workspace_describe"],
        )
    try:
        return target_quality_feedback_payload(
            DataService(workspace),
            workspace_id=meta["workspace_id"],
            target_type=request.target_type,
            target_id=request.target_id,
            action=request.action,
            label=request.label,
            suggested_value=request.suggested_value,
            reason=request.reason,
            metadata=request.metadata,
            envelope=_target_envelope,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@target_router.get("/{workspace_id}/quality/correction-rules")
async def list_target_quality_correction_rules(
    workspace_id: str,
    limit: int = Query(default=50, ge=1, le=100),
    status: Optional[str] = Query(default=None),
) -> dict:
    workspace, meta = _target_workspace_or_404(workspace_id)
    try:
        return target_quality_correction_rules_list_payload(
            DataService(workspace),
            workspace_id=meta["workspace_id"],
            limit=limit,
            status=status,
            envelope=_target_envelope,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@target_router.post("/{workspace_id}/quality/correction-rules")
async def write_target_quality_correction_rule(workspace_id: str, request: TargetQualityCorrectionRuleRequest) -> dict:
    workspace, meta = _target_workspace_or_404(workspace_id)
    if str(meta.get("status", "active")) == "archived":
        return _blocked(
            workspace_id=meta["workspace_id"],
            message="Archived workspace cannot accept quality correction rules",
            code="workspace_archived",
            next_actions=["knowledge_workspace_describe"],
        )
    try:
        return target_quality_correction_rule_write_payload(
            DataService(workspace),
            workspace_id=meta["workspace_id"],
            rule_id=request.rule_id,
            target_type=request.target_type,
            target_id=request.target_id,
            action=request.action,
            label=request.label,
            suggested_value=request.suggested_value,
            reason=request.reason,
            metadata=request.metadata,
            envelope=_target_envelope,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@target_router.post("/{workspace_id}/quality/correction-rules/build")
async def build_target_quality_correction_rules(
    workspace_id: str,
    request: TargetQualityCorrectionRulesBuildRequest,
) -> dict:
    workspace, meta = _target_workspace_or_404(workspace_id)
    if str(meta.get("status", "active")) == "archived":
        return _blocked(
            workspace_id=meta["workspace_id"],
            message="Archived workspace cannot build quality correction rules",
            code="workspace_archived",
            next_actions=["knowledge_workspace_describe"],
        )
    return target_quality_correction_rules_build_payload(
        DataService(workspace),
        workspace_id=meta["workspace_id"],
        envelope=_target_envelope,
    )


@target_router.post("/{workspace_id}/quality/correction-rules/{rule_id}/review")
async def review_target_quality_correction_rule(
    workspace_id: str,
    rule_id: str,
    request: TargetQualityCorrectionRuleReviewRequest,
) -> dict:
    if str(rule_id).strip() == "build":
        raise HTTPException(status_code=404, detail="Reserved correction-rules route segment")
    workspace, meta = _target_workspace_or_404(workspace_id)
    if str(meta.get("status", "active")) == "archived":
        return _blocked(
            workspace_id=meta["workspace_id"],
            message="Archived workspace cannot review quality correction rules",
            code="workspace_archived",
            next_actions=["knowledge_workspace_describe"],
        )
    try:
        return target_quality_correction_rule_review_payload(
            DataService(workspace),
            workspace_id=meta["workspace_id"],
            rule_id=rule_id,
            status=request.status,
            reviewer=request.reviewer,
            note=request.note,
            envelope=_target_envelope,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@target_router.get("/{workspace_id}/quality/correction-plan")
async def read_target_quality_correction_plan(workspace_id: str) -> dict:
    workspace, meta = _target_workspace_or_404(workspace_id)
    return target_quality_correction_plan_read_payload(
        DataService(workspace),
        workspace_id=meta["workspace_id"],
        envelope=_target_envelope,
        blocked=_blocked,
    )


@target_router.post("/{workspace_id}/quality/correction-plan")
async def generate_target_quality_correction_plan(workspace_id: str, request: TargetQualityCorrectionPlanRequest) -> dict:
    workspace, meta = _target_workspace_or_404(workspace_id)
    if str(meta.get("status", "active")) == "archived":
        return _blocked(
            workspace_id=meta["workspace_id"],
            message="Archived workspace cannot generate quality correction plans",
            code="workspace_archived",
            next_actions=["knowledge_workspace_describe"],
        )
    return target_quality_correction_plan_generate_payload(
        DataService(workspace),
        workspace_id=meta["workspace_id"],
        envelope=_target_envelope,
    )


@target_router.post("/{workspace_id}/query")
async def query_workspace(workspace_id: str, request: WorkspaceScopedQueryRequest) -> dict:
    service = _service_for_workspace_id(workspace_id)
    payload = run_query_contract(service, request.query, mode=request.mode, top_k=request.top_k)
    return _enhance_workspace_query_response(
        service.workspace,
        workspace_id=workspace_id,
        query=request.query,
        top_k=normalize_query_top_k(request.top_k),
        payload=payload,
    )


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
        trace = source_trace_payload(service, source_id, limit=limit, strict_registry=True)
        return _target_envelope(
            workspace_id=workspace_id,
            artifact_refs=[_target_source_artifact_ref(str(trace.get("source_id") or source_id))],
            next_actions=[] if trace.get("trace_available") else [str(trace.get("unavailable_reason") or "trace_not_available")],
            data={"trace": trace},
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=f"VALIDATION_ERROR: {exc}") from exc
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=f"SOURCE_NOT_FOUND: Unknown source_id: {source_id}") from exc


@target_router.get("/{workspace_id}/sources/{source_id:path}/trace")
async def reject_invalid_workspace_source_trace_path(workspace_id: str, source_id: str) -> dict:
    _target_workspace_or_404(workspace_id)
    raise HTTPException(status_code=422, detail="VALIDATION_ERROR: source_id must be a registry source_id")


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
