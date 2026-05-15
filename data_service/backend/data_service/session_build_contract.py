"""Stable session-scoped build contract for target HTTP surfaces."""

from __future__ import annotations

import hashlib
import threading
from typing import Any, Callable

from .mcp_common import blocked as contract_blocked
from .mcp_common import envelope as contract_envelope
from .session_service import SESSION_BUILD_MODES, SESSION_TERMINAL_STATUSES

_INTERNAL_KEYS = {
    "workspace_path",
    "root_path",
    "filesystem_path",
    "session_storage_path",
    "artifact_physical_path",
    "graphrag_cache_path",
    "cache_path",
    "physical_path",
    "internal_path",
    "debug_paths",
    "db_path",
    "path",
    "paths",
    "local_path",
    "source_path",
    "original_path",
    "traceback",
}


def start_session_build_payload(
    session_service: Any,
    *,
    workspace_id: str,
    session_id: str,
    mode: str = "full",
    envelope: Callable[..., dict[str, Any]] = contract_envelope,
    blocked: Callable[..., dict[str, Any]] = contract_blocked,
) -> dict[str, Any]:
    normalized_session_id = str(session_id or "").strip()
    normalized_mode = str(mode or "full").strip()
    if normalized_mode not in SESSION_BUILD_MODES:
        return blocked(
            workspace_id=workspace_id,
            message="mode must be one of: communities, distill, full, graph",
            code="invalid_session_build_request",
            next_actions=["knowledge_session_get"],
        )
    try:
        session = session_service.get_session(session_id=normalized_session_id)
        if not session:
            return _unknown_session(blocked, workspace_id=workspace_id, session_id=normalized_session_id)
        operation = session_service.start_build(session_id=normalized_session_id, mode=normalized_mode)
    except (KeyError, ValueError) as exc:
        return _blocked_from_error(blocked, workspace_id=workspace_id, session_id=normalized_session_id, error=str(exc))

    operation_id = str(operation.get("operation_id") or "")
    threading.Thread(target=session_service.run_build, args=(normalized_session_id, operation_id), daemon=True).start()
    return _operation_envelope(envelope, workspace_id, normalized_session_id, operation_id, operation)


def read_session_build_payload(
    session_service: Any,
    *,
    workspace_id: str,
    session_id: str,
    operation_id: str,
    envelope: Callable[..., dict[str, Any]] = contract_envelope,
    blocked: Callable[..., dict[str, Any]] = contract_blocked,
) -> dict[str, Any]:
    normalized_session_id = str(session_id or "").strip()
    normalized_operation_id = str(operation_id or "").strip()
    session = session_service.get_session(session_id=normalized_session_id)
    if not session:
        return _unknown_session(blocked, workspace_id=workspace_id, session_id=normalized_session_id, operation_id=normalized_operation_id)
    operation = session_service.get_operation(normalized_session_id, normalized_operation_id)
    if not operation:
        return _unknown_operation(blocked, workspace_id=workspace_id, session_id=normalized_session_id, operation_id=normalized_operation_id)
    if operation.get("workspace_id") != workspace_id or operation.get("session_id") != normalized_session_id:
        return _unknown_operation(blocked, workspace_id=workspace_id, session_id=normalized_session_id, operation_id=normalized_operation_id)
    return _operation_envelope(envelope, workspace_id, normalized_session_id, normalized_operation_id, operation)


def cancel_session_build_payload(
    session_service: Any,
    *,
    workspace_id: str,
    session_id: str,
    operation_id: str,
    reason: str = "",
    envelope: Callable[..., dict[str, Any]] = contract_envelope,
    blocked: Callable[..., dict[str, Any]] = contract_blocked,
) -> dict[str, Any]:
    normalized_session_id = str(session_id or "").strip()
    normalized_operation_id = str(operation_id or "").strip()
    session = session_service.get_session(session_id=normalized_session_id)
    if not session:
        return _unknown_session(blocked, workspace_id=workspace_id, session_id=normalized_session_id, operation_id=normalized_operation_id)
    before = session_service.get_operation(normalized_session_id, normalized_operation_id)
    if not before or before.get("workspace_id") != workspace_id or before.get("session_id") != normalized_session_id:
        return _unknown_operation(blocked, workspace_id=workspace_id, session_id=normalized_session_id, operation_id=normalized_operation_id)
    operation = session_service.cancel_operation(normalized_session_id, normalized_operation_id, reason=str(reason or ""))
    warnings = []
    if before.get("status") in SESSION_TERMINAL_STATUSES:
        warnings.append(f"Operation is already {before.get('status')} and cannot be cancelled")
    return _operation_envelope(envelope, workspace_id, normalized_session_id, normalized_operation_id, operation, warnings=warnings)


def _operation_envelope(
    envelope: Callable[..., dict[str, Any]],
    workspace_id: str,
    session_id: str,
    operation_id: str,
    operation: dict[str, Any],
    *,
    warnings: list[str] | None = None,
) -> dict[str, Any]:
    status = str(operation.get("status") or "queued")
    next_actions = ["knowledge_session_build_status"]
    if status not in SESSION_TERMINAL_STATUSES:
        next_actions.append("knowledge_session_build_cancel")
    elif status in {"failed", "blocked"} and operation.get("retryable", True):
        next_actions.append("knowledge_session_build_start")
    return envelope(
        workspace_id=workspace_id,
        operation_id=operation_id,
        status=status,
        warnings=warnings,
        artifact_refs=_artifact_refs(session_id=session_id, operation=operation),
        next_actions=next_actions,
        data=_operation_payload(workspace_id=workspace_id, session_id=session_id, operation=operation),
    )


def _operation_payload(*, workspace_id: str, session_id: str, operation: dict[str, Any]) -> dict[str, Any]:
    return {
        "workspace_id": workspace_id,
        "session_id": session_id,
        "operation_id": operation.get("operation_id"),
        "mode": operation.get("mode"),
        "status": operation.get("status", "queued"),
        "stage": operation.get("stage"),
        "progress": operation.get("progress", 0.0),
        "created_at": operation.get("created_at"),
        "updated_at": operation.get("updated_at"),
        "started_at": operation.get("started_at"),
        "completed_at": operation.get("completed_at"),
        "artifact_ref": f"session-build://{session_id}/{operation.get('operation_id')}",
        "artifact_refs": _artifact_refs(session_id=session_id, operation=operation),
        "warnings": [],
        "next_actions": [],
        "error": _stable_value(operation.get("error")),
        "retryable": operation.get("retryable", True),
        "results": _stable_value(operation.get("results") or {}),
        "artifacts": _artifact_refs(session_id=session_id, operation=operation),
    }


def _artifact_refs(*, session_id: str, operation: dict[str, Any]) -> list[dict[str, Any]]:
    operation_id = str(operation.get("operation_id") or "")
    refs = [
        {
            "type": "session_build_operation",
            "session_id": session_id,
            "operation_id": operation_id,
            "artifact_ref": f"session-build://{session_id}/{operation_id}",
        }
    ]
    for item in operation.get("artifacts", []) or []:
        digest = hashlib.sha256(str(item or "").encode("utf-8")).hexdigest()[:16]
        refs.append(
            {
                "type": "session_build_artifact",
                "session_id": session_id,
                "operation_id": operation_id,
                "artifact_ref": f"session-artifact://{session_id}/{digest}",
            }
        )
    return refs


def _stable_value(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: _stable_value(item)
            for key, item in value.items()
            if str(key) not in _INTERNAL_KEYS and not _looks_like_path_key(str(key))
        }
    if isinstance(value, list):
        return [_stable_value(item) for item in value]
    return value


def _looks_like_path_key(key: str) -> bool:
    lowered = key.lower()
    return lowered.endswith("_path") or lowered.endswith("_paths") or "physical" in lowered or "cache" in lowered


def _unknown_session(
    blocked: Callable[..., dict[str, Any]],
    *,
    workspace_id: str,
    session_id: str,
    operation_id: str | None = None,
) -> dict[str, Any]:
    return blocked(
        workspace_id=workspace_id,
        operation_id=operation_id,
        message=f"Unknown session_id: {session_id}",
        code="unknown_session_id",
        next_actions=["knowledge_session_list"],
    )


def _unknown_operation(
    blocked: Callable[..., dict[str, Any]],
    *,
    workspace_id: str,
    session_id: str,
    operation_id: str,
) -> dict[str, Any]:
    return blocked(
        workspace_id=workspace_id,
        operation_id=operation_id,
        message=f"Unknown operation_id: {operation_id}",
        code="unknown_operation_id",
        next_actions=["knowledge_session_build_start"],
        data={"session_id": session_id},
    )


def _blocked_from_error(
    blocked: Callable[..., dict[str, Any]],
    *,
    workspace_id: str,
    session_id: str,
    error: str,
) -> dict[str, Any]:
    lower = error.lower()
    if "unknown session" in lower:
        code = "unknown_session_id"
    elif "disposed" in lower or "deleted" in lower:
        code = "session_disposed"
    elif "mode" in lower:
        code = "invalid_session_build_request"
    else:
        code = "session_build_blocked"
    return blocked(
        workspace_id=workspace_id,
        message=error or f"Session build blocked for session_id: {session_id}",
        code=code,
        next_actions=["knowledge_session_get", "knowledge_session_ingest"],
    )
