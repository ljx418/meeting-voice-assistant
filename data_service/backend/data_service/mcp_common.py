"""Shared MCP helper functions for data_service."""

from __future__ import annotations

import json
import os
import re
import threading
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PUBLIC_PROVIDER_ERROR_CODES = {
    "PROVIDER_NOT_CONFIGURED",
    "PROVIDER_UNSUPPORTED",
    "PROVIDER_MISSING_CREDENTIAL",
    "PROVIDER_AUTH_FAILED",
    "PROVIDER_TIMEOUT",
    "PROVIDER_QUOTA_EXCEEDED",
    "PROVIDER_UNAVAILABLE",
    "PROVIDER_BAD_RESPONSE",
    "PROVIDER_EXECUTION_FAILED",
    "PROVIDER_OUTPUT_INVALID",
    "EXPORTER_NOT_CONFIGURED",
    "EXPORTER_UNSUPPORTED",
    "PDF_RASTERIZER_UNAVAILABLE",
}


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def bounded_int(value: object, *, default: int, minimum: int, maximum: int, field: str) -> int:
    try:
        parsed = int(value if value is not None else default)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field} must be an integer") from exc
    if parsed < minimum or parsed > maximum:
        raise ValueError(f"{field} must be between {minimum} and {maximum}")
    return parsed


def slug(value: object) -> str:
    text = re.sub(r"[^A-Za-z0-9._-]+", "-", str(value or "").strip().lower()).strip("-")
    return text[:48] or "workspace"


def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return default


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_name(f".{path.name}.{os.getpid()}.{threading.get_ident()}.tmp")
    tmp_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp_path, path)


def envelope(
    *,
    workspace_id: str,
    status: str = "ok",
    operation_id: str | None = None,
    warnings: list[str] | None = None,
    artifact_refs: list[Any] | None = None,
    next_actions: list[str] | None = None,
    data: dict | None = None,
) -> dict[str, Any]:
    payload_data = dict(data or {})
    payload_warnings = list(warnings or [])
    if status in {"blocked", "failed", "disposed"}:
        payload_data.setdefault(
            "error",
            _normalize_error(
                payload_data.get("error"),
                fallback_message=payload_warnings[0] if payload_warnings else status,
                fallback_code=status,
                retryable=False,
            ),
        )
    return {
        "workspace_id": workspace_id,
        "operation_id": operation_id,
        "status": status,
        "warnings": payload_warnings,
        "artifact_refs": [_artifact_ref(item) for item in list(artifact_refs or [])],
        "next_actions": list(next_actions or []),
        "data": _sanitize_external_payload(payload_data),
    }


def blocked(
    *,
    workspace_id: str,
    message: str,
    operation_id: str | None = None,
    next_actions: list[str] | None = None,
    data: dict | None = None,
    code: str = "blocked",
) -> dict[str, Any]:
    payload = dict(data or {})
    payload["error"] = _normalize_error(
        payload.get("error"),
        fallback_message=message,
        fallback_code=code,
        retryable=False,
    )
    return envelope(
        workspace_id=workspace_id,
        operation_id=operation_id,
        status="blocked",
        warnings=[message],
        next_actions=next_actions,
        data=payload,
    )


_PATH_KEYS = {
    "path",
    "paths",
    "workspace_path",
    "original_path",
    "distill_path",
    "rules_path",
    "feedback_path",
    "units_path",
    "db_path",
    "request_path",
    "root",
    "bound_paths",
    "roots",
    "files",
}


def _artifact_ref(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        payload = dict(value)
        raw_path = payload.pop("path", None)
        raw_ref = payload.get("artifact_ref") or payload.get("source_id") or payload.get("operation_id") or payload.get("session_id")
        if raw_path and "artifact_ref" not in payload:
            payload["artifact_ref"] = _opaque_ref(raw_path)
            payload.setdefault("debug_path", str(raw_path))
        elif raw_ref and "artifact_ref" not in payload:
            payload["artifact_ref"] = str(raw_ref)
        return payload
    return {"type": "artifact", "artifact_ref": _opaque_ref(value), "debug_path": str(value)}


def _opaque_ref(value: Any) -> str:
    digest = hashlib.sha256(str(value).encode("utf-8")).hexdigest()[:16]
    return f"artifact://{digest}"


def _sanitize_external_payload(value: Any) -> Any:
    if isinstance(value, list):
        return [_sanitize_external_payload(item) for item in value]
    if not isinstance(value, dict):
        return value

    result: dict[str, Any] = {}
    debug_paths: dict[str, Any] = {}
    for key, item in value.items():
        if key == "debug_paths":
            debug_paths.update(dict(item or {}))
            continue
        if key == "v2" and isinstance(item, dict):
            result[key] = _sanitize_v2_payload(item)
            continue
        if key == "artifact_refs":
            result[key] = [_artifact_ref(ref) for ref in list(item or [])]
            continue
        if key == "artifacts":
            result["artifact_refs"] = [_artifact_ref(ref) for ref in list(item or [])]
            debug_paths[key] = list(item or [])
            continue
        if key == "workspace" and isinstance(item, str):
            debug_paths[key] = item
            continue
        if key == "error":
            result[key] = _normalize_error(item)
            continue
        if key == "files" and not isinstance(item, (dict, list, tuple)):
            result[key] = _sanitize_external_payload(item)
            continue
        if key in _PATH_KEYS:
            debug_paths[key] = item
            if key not in {"path", "paths", "workspace_path", "workspace", "original_path", "root"}:
                result[f"{key}_ref"] = _opaque_ref(item)
            continue
        result[key] = _sanitize_external_payload(item)
    if debug_paths:
        result["debug_paths"] = debug_paths
    return result


def _sanitize_v2_payload(value: dict[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, item in value.items():
        if key == "error" and isinstance(item, dict):
            result[key] = {
                "code": str(item.get("code") or "ERROR"),
                "message": str(item.get("message") or ""),
                "retryable": bool(item.get("retryable", False)),
            }
            continue
        result[key] = _sanitize_external_payload(item)
    return result


def _normalize_error(
    error: Any,
    *,
    fallback_message: str = "",
    fallback_code: str = "error",
    retryable: bool = False,
) -> dict[str, Any]:
    if isinstance(error, dict):
        payload = dict(error)
    elif error:
        payload = {"message": str(error)}
    else:
        payload = {}
    message = str(payload.get("message") or fallback_message or fallback_code)
    code = str(payload.get("code") or payload.get("type") or _infer_error_code(message, fallback_code=fallback_code))
    payload["code"] = code if code in PUBLIC_PROVIDER_ERROR_CODES else _slug_code(code)
    payload["message"] = message
    payload["retryable"] = bool(payload.get("retryable", retryable))
    payload.pop("type", None)
    return payload


def _slug_code(value: str) -> str:
    text = re.sub(r"[^a-zA-Z0-9_]+", "_", str(value or "error")).strip("_").lower()
    return text or "error"


def _infer_error_code(message: str, *, fallback_code: str) -> str:
    lowered = str(message or "").lower()
    if "unknown source_id" in lowered:
        return "unknown_source_id"
    if "unknown operation_id" in lowered:
        return "unknown_operation_id"
    if "unknown session" in lowered or "unknown session_id" in lowered:
        return "unknown_session_id"
    if "archived" in lowered:
        return "workspace_archived"
    if "outside allowed roots" in lowered:
        return "source_path_outside_allowed_roots"
    if "outside data_service_workspace_root" in lowered:
        return "workspace_id_outside_root"
    if "outside workspace" in lowered:
        return "path_outside_workspace"
    if "larger than" in lowered:
        return "payload_too_large"
    if "closed" in lowered:
        return "session_closed"
    if "disposed" in lowered:
        return "session_disposed"
    return fallback_code or "error"
