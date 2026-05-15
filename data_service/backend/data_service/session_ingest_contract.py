"""Stable Session ingest contract for target HTTP surfaces."""

from __future__ import annotations

import json
from typing import Any, Callable

from .mcp_common import blocked as contract_blocked
from .mcp_common import envelope as contract_envelope

_MAX_CONTENT_BYTES = 2 * 1024 * 1024
_MAX_RECORDS = 1000
_MAX_METADATA_BYTES = 16 * 1024
_MAX_METADATA_DEPTH = 8
_ALLOWED_CONTENT_FORMATS = {"text", "markdown", "turns", "json"}
_INTERNAL_PATH_KEYS = {
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
}


def ingest_session_payload(
    session_service: Any,
    *,
    workspace_id: str,
    session_id: str,
    source_type: str = "structured",
    content_format: str = "text",
    title: str = "",
    records: list[Any] | None = None,
    content: Any = None,
    metadata: dict[str, Any] | None = None,
    related_source_ids: list[str] | None = None,
    source_refs: list[str] | None = None,
    auto_link: bool = False,
    allow_closed_write: bool = False,
    envelope: Callable[..., dict[str, Any]] = contract_envelope,
    blocked: Callable[..., dict[str, Any]] = contract_blocked,
) -> dict[str, Any]:
    """Ingest session-scoped content and return a stable non-path payload."""

    try:
        normalized = _normalize_request(
            source_type=source_type,
            content_format=content_format,
            records=records,
            content=content,
            metadata=metadata,
        )
    except ValueError as exc:
        return blocked(
            workspace_id=workspace_id,
            message=str(exc),
            code="invalid_session_ingest_request",
            next_actions=["knowledge_session_get"],
        )

    related_ids = _normalize_string_list(related_source_ids) + _normalize_string_list(source_refs)
    related_ids = list(dict.fromkeys(related_ids))

    try:
        result = session_service.ingest(
            session_id=session_id,
            source_type=normalized["source_type"],
            content_format=normalized["content_format"],
            title=title,
            records=normalized["records"],
            content=normalized["content"],
            metadata=normalized["metadata"],
            related_source_ids=related_ids,
            related_paths=[],
            auto_link=bool(auto_link),
            allow_closed_write=bool(allow_closed_write),
        )
    except (KeyError, ValueError) as exc:
        return _blocked_from_ingest_error(blocked, workspace_id=workspace_id, session_id=session_id, error=str(exc))

    source = _project_session_source(result.get("source") or {}, workspace_id=workspace_id, session_id=session_id)
    artifact_refs = [_session_source_artifact_ref(session_id=session_id, source_id=source["source_id"])]
    return envelope(
        workspace_id=workspace_id,
        artifact_refs=artifact_refs,
        next_actions=["knowledge_session_build_start"],
        data={"source": source},
    )


def _normalize_request(
    *,
    source_type: str,
    content_format: str,
    records: list[Any] | None,
    content: Any,
    metadata: dict[str, Any] | None,
) -> dict[str, Any]:
    normalized_source_type = str(source_type or "").strip()
    if not normalized_source_type:
        raise ValueError("source_type is required")
    normalized_format = str(content_format or "text").strip()
    if normalized_format not in _ALLOWED_CONTENT_FORMATS:
        raise ValueError("content_format must be one of: json, markdown, text, turns")

    has_records = bool(records)
    has_content = content is not None and (not isinstance(content, str) or bool(content.strip()))
    if has_records and has_content:
        raise ValueError("content and records are mutually exclusive for target HTTP session ingest")
    if not has_records and not has_content:
        raise ValueError("content or records is required")
    if records is not None and len(records) > _MAX_RECORDS:
        raise ValueError(f"records exceeds maximum item count {_MAX_RECORDS}")
    if records is not None and any(not isinstance(item, dict) for item in records):
        raise ValueError("records must be a list of objects")

    _assert_json_size("content", content, _MAX_CONTENT_BYTES)
    _assert_json_size("records", records, _MAX_CONTENT_BYTES)
    _assert_json_size("metadata", metadata or {}, _MAX_METADATA_BYTES)
    _assert_metadata_depth(metadata or {}, depth=0)

    return {
        "source_type": normalized_source_type,
        "content_format": normalized_format,
        "records": records,
        "content": content,
        "metadata": _stable_metadata(metadata or {}),
    }


def _assert_json_size(field: str, value: Any, limit: int) -> None:
    if value is None:
        return
    size = len(json.dumps(value, ensure_ascii=False).encode("utf-8"))
    if size > limit:
        raise ValueError(f"{field} exceeds maximum size {limit} bytes")


def _assert_metadata_depth(value: Any, *, depth: int) -> None:
    if depth > _MAX_METADATA_DEPTH:
        raise ValueError(f"metadata exceeds maximum depth {_MAX_METADATA_DEPTH}")
    if isinstance(value, dict):
        for item in value.values():
            _assert_metadata_depth(item, depth=depth + 1)
    elif isinstance(value, list):
        for item in value:
            _assert_metadata_depth(item, depth=depth + 1)


def _normalize_string_list(value: list[str] | None) -> list[str]:
    return [str(item).strip() for item in value or [] if str(item).strip()]


def _blocked_from_ingest_error(
    blocked: Callable[..., dict[str, Any]],
    *,
    workspace_id: str,
    session_id: str,
    error: str,
) -> dict[str, Any]:
    lower = error.lower()
    if "unknown session" in lower:
        code = "unknown_session_id"
    elif "closed" in lower:
        code = "session_closed"
    elif "disposed" in lower or "deleted" in lower:
        code = "session_disposed"
    else:
        code = "session_ingest_blocked"
    return blocked(
        workspace_id=workspace_id,
        message=error or f"Session ingest blocked for session_id: {session_id}",
        code=code,
        next_actions=["knowledge_session_get", "knowledge_session_list"],
    )


def _project_session_source(source: dict[str, Any], *, workspace_id: str, session_id: str) -> dict[str, Any]:
    source_id = str(source.get("source_id") or "")
    artifact_ref = f"session-source://{session_id}/{source_id}" if source_id else None
    return {
        "workspace_id": workspace_id,
        "session_id": session_id,
        "source_id": source_id,
        "session_source_id": source_id,
        "source_scope": "session",
        "source_type": source.get("source_type") or "structured",
        "content_format": source.get("content_format") or "text",
        "title": source.get("title") or source_id,
        "record_count": int(source.get("record_count") or 0),
        "status": "ingested",
        "artifact_ref": artifact_ref,
        "created_at": source.get("created_at"),
        "updated_at": source.get("updated_at") or source.get("created_at"),
        "metadata": _stable_metadata(source.get("metadata") or {}),
        "related_source_ids": _normalize_string_list(source.get("related_source_ids") or []),
        "auto_link": bool(source.get("auto_link", False)),
    }


def _session_source_artifact_ref(*, session_id: str, source_id: str) -> dict[str, Any]:
    return {
        "type": "session_source",
        "session_id": session_id,
        "source_id": source_id,
        "artifact_ref": f"session-source://{session_id}/{source_id}",
    }


def _stable_metadata(value: Any) -> Any:
    if isinstance(value, list):
        return [_stable_metadata(item) for item in value]
    if isinstance(value, dict):
        return {
            key: _stable_metadata(item)
            for key, item in value.items()
            if str(key) not in _INTERNAL_PATH_KEYS and not str(key).endswith("_path")
        }
    return value
