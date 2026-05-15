"""Stable Session lifecycle contract for target HTTP surfaces."""

from __future__ import annotations

from typing import Any, Callable

from .mcp_common import blocked as contract_blocked
from .mcp_common import bounded_int
from .mcp_common import envelope as contract_envelope

_INTERNAL_PATH_KEYS = {
    "workspace_path",
    "root_path",
    "filesystem_path",
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
}


def create_session_payload(
    session_service: Any,
    *,
    workspace_id: str,
    external_id: str | None = None,
    session_type: str = "generic",
    title: str = "",
    ephemeral: bool = False,
    ttl_seconds: int | None = None,
    metadata: dict[str, Any] | None = None,
    envelope: Callable[..., dict[str, Any]] = contract_envelope,
) -> dict[str, Any]:
    result = session_service.create_session(
        external_id=external_id,
        session_type=session_type,
        title=title,
        ephemeral=ephemeral,
        ttl_seconds=ttl_seconds,
        metadata=dict(metadata or {}),
    )
    session = _project_session(result["session"], workspace_id=workspace_id)
    return envelope(
        workspace_id=workspace_id,
        artifact_refs=[_session_artifact_ref(session["session_id"])],
        next_actions=["knowledge_session_get", "knowledge_session_close"],
        data={"session": session, "created": bool(result.get("created"))},
    )


def list_sessions_payload(
    session_service: Any,
    *,
    workspace_id: str,
    status: str | None = None,
    session_type: str | None = None,
    include_deleted: bool = False,
    limit: object = 20,
    envelope: Callable[..., dict[str, Any]] = contract_envelope,
) -> dict[str, Any]:
    normalized_limit = bounded_int(limit, default=20, minimum=1, maximum=100, field="limit")
    items = [
        _project_session(session, workspace_id=workspace_id)
        for session in session_service.list_sessions(
            status=status,
            session_type=session_type,
            include_disposed=include_deleted,
            limit=normalized_limit,
        )
    ]
    return envelope(
        workspace_id=workspace_id,
        next_actions=["knowledge_session_get", "knowledge_session_create"],
        data={"items": items, "limit": normalized_limit, "include_deleted": include_deleted},
    )


def get_session_payload(
    session_service: Any,
    *,
    workspace_id: str,
    session_id: str,
    envelope: Callable[..., dict[str, Any]] = contract_envelope,
    blocked: Callable[..., dict[str, Any]] = contract_blocked,
) -> dict[str, Any]:
    session = session_service.get_session(session_id=session_id)
    if not session:
        return _unknown_session(blocked, workspace_id=workspace_id, session_id=session_id)
    projected = _project_session(session, workspace_id=workspace_id)
    return envelope(
        workspace_id=workspace_id,
        artifact_refs=[_session_artifact_ref(projected["session_id"])],
        next_actions=["knowledge_session_close", "knowledge_session_delete"],
        data={"session": projected},
    )


def close_session_payload(
    session_service: Any,
    *,
    workspace_id: str,
    session_id: str,
    envelope: Callable[..., dict[str, Any]] = contract_envelope,
    blocked: Callable[..., dict[str, Any]] = contract_blocked,
) -> dict[str, Any]:
    try:
        session = session_service.close_session(session_id)
    except (KeyError, ValueError):
        return _unknown_session(blocked, workspace_id=workspace_id, session_id=session_id)
    projected = _project_session(session, workspace_id=workspace_id)
    return envelope(
        workspace_id=workspace_id,
        status=projected.get("status") or "closed",
        artifact_refs=[_session_artifact_ref(projected["session_id"])],
        next_actions=["knowledge_session_get", "knowledge_session_delete"],
        data={"session": projected},
    )


def delete_session_payload(
    session_service: Any,
    *,
    workspace_id: str,
    session_id: str,
    envelope: Callable[..., dict[str, Any]] = contract_envelope,
    blocked: Callable[..., dict[str, Any]] = contract_blocked,
) -> dict[str, Any]:
    try:
        session = session_service.delete_session(session_id)
    except (KeyError, ValueError):
        return _unknown_session(blocked, workspace_id=workspace_id, session_id=session_id)
    projected = _project_session(session, workspace_id=workspace_id)
    return envelope(
        workspace_id=workspace_id,
        status=projected.get("status") or "disposed",
        artifact_refs=[_session_artifact_ref(projected["session_id"])],
        next_actions=["knowledge_session_list"],
        data={"session": projected},
    )


def _unknown_session(
    blocked: Callable[..., dict[str, Any]],
    *,
    workspace_id: str,
    session_id: str,
) -> dict[str, Any]:
    return blocked(
        workspace_id=workspace_id,
        message=f"Unknown session_id: {session_id}",
        code="unknown_session",
        next_actions=["knowledge_session_create", "knowledge_session_list"],
    )


def _project_session(session: dict[str, Any], *, workspace_id: str) -> dict[str, Any]:
    session_id = str(session.get("session_id") or "")
    return {
        "workspace_id": workspace_id,
        "session_id": session_id,
        "external_id": session.get("external_id"),
        "session_type": session.get("session_type") or "generic",
        "title": session.get("title") or session_id,
        "status": session.get("status") or "active",
        "ephemeral": bool(session.get("ephemeral", False)),
        "ttl_seconds": session.get("ttl_seconds"),
        "expires_at": session.get("expires_at"),
        "metadata": _stable_metadata(session.get("metadata") or {}),
        "artifact_ref": f"session://{session_id}" if session_id else None,
        "created_at": session.get("created_at"),
        "updated_at": session.get("updated_at"),
        "closed_at": session.get("closed_at"),
        "deleted_at": session.get("deleted_at"),
        "removed_at": session.get("deleted_at"),
    }


def _session_artifact_ref(session_id: str) -> dict[str, Any]:
    return {"type": "session", "session_id": session_id, "artifact_ref": f"session://{session_id}"}


def _stable_metadata(value: Any) -> Any:
    if isinstance(value, list):
        return [_stable_metadata(item) for item in value]
    if isinstance(value, dict):
        return {key: _stable_metadata(item) for key, item in value.items() if key not in _INTERNAL_PATH_KEYS}
    return value
