"""Stable V2 read envelopes for codebase asset APIs."""

from __future__ import annotations

from typing import Any


V2_ENVELOPE_SCHEMA_VERSION = "v2.0"


def v2_success_envelope(
    *,
    workspace_id: str,
    codebase_id: str | None = None,
    snapshot_id: str | None = None,
    data: dict[str, Any] | None = None,
    artifact_refs: list[dict[str, Any]] | None = None,
    warnings: list[Any] | None = None,
    unresolved: list[Any] | None = None,
    next_actions: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "ok": True,
        "schema_version": V2_ENVELOPE_SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "data": dict(data or {}),
        "artifact_refs": normalize_artifact_refs(artifact_refs),
        "warnings": normalize_list(warnings),
        "unresolved": normalize_list(unresolved),
        "next_actions": sorted(set(str(item) for item in list(next_actions or []) if str(item))),
    }


def v2_error_envelope(
    *,
    workspace_id: str,
    codebase_id: str | None = None,
    snapshot_id: str | None = None,
    code: str,
    message: str,
    retryable: bool = False,
    data: dict[str, Any] | None = None,
    artifact_refs: list[dict[str, Any]] | None = None,
    warnings: list[Any] | None = None,
    unresolved: list[Any] | None = None,
    next_actions: list[str] | None = None,
) -> dict[str, Any]:
    payload = v2_success_envelope(
        workspace_id=workspace_id,
        codebase_id=codebase_id,
        snapshot_id=snapshot_id,
        data=data,
        artifact_refs=artifact_refs,
        warnings=warnings or [message],
        unresolved=unresolved,
        next_actions=next_actions,
    )
    payload["ok"] = False
    payload["error"] = {
        "code": normalize_error_code(code),
        "message": message,
        "retryable": bool(retryable),
    }
    return payload


def normalize_artifact_refs(refs: list[dict[str, Any]] | None) -> list[dict[str, Any]]:
    normalized = []
    for ref in list(refs or []):
        item = dict(ref)
        normalized.append(item)
    return sorted(normalized, key=lambda item: (str(item.get("type") or ""), str(item.get("artifact_ref") or ""), str(item)))


def normalize_list(items: list[Any] | None) -> list[Any]:
    values = list(items or [])
    if all(not isinstance(item, (dict, list)) for item in values):
        return sorted(set(values), key=lambda item: str(item))
    return values


def normalize_error_code(code: str) -> str:
    value = str(code or "ERROR").strip()
    if not value:
        return "ERROR"
    return value.upper()
