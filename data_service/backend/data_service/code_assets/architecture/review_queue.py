"""V2.6 architecture review queue builder."""

from __future__ import annotations

import hashlib
from typing import Any

from data_service.mcp_common import now


SCHEMA_VERSION = "v2.6"


def build_review_queue(
    *,
    workspace_id: str,
    codebase_id: str,
    snapshot_id: str | None,
    taxonomy: dict[str, Any],
    collections: dict[str, list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    queue: list[dict[str, Any]] = []
    thresholds = taxonomy.get("confidence_thresholds") if isinstance(taxonomy.get("confidence_thresholds"), dict) else {}
    accepted_min = float(thresholds.get("accepted_min") or 0.8)
    major_below = float(thresholds.get("major_below") or 0.5)
    for target_type, items in collections.items():
        for item in items:
            item_id = _target_id(item)
            if not item_id:
                continue
            confidence = _confidence(item)
            reasons: list[str] = []
            if item.get("needs_review") or confidence < accepted_min:
                reasons.append("low_confidence" if confidence < accepted_min else "unsupported_semantic_claim")
            if not item.get("evidence"):
                reasons.append("missing_evidence")
            redaction = item.get("redaction")
            if isinstance(redaction, dict) and redaction.get("redaction_count"):
                reasons.append("redacted_sensitive_value")
            if _is_unknown_type(item):
                reasons.append("unknown_config_type")
            for reason in sorted(set(reasons)):
                queue.append(_queue_item(workspace_id, codebase_id, snapshot_id, target_type, item_id, reason, confidence, major_below, item))
    return _dedupe(queue)


def public_review_queue_payload(items: list[dict[str, Any]], *, limit: int = 50) -> dict[str, Any]:
    counts: dict[str, int] = {}
    severities: dict[str, int] = {}
    for item in items:
        reason = str(item.get("reason") or "unknown")
        severity = str(item.get("severity") or "unknown")
        counts[reason] = counts.get(reason, 0) + 1
        severities[severity] = severities.get(severity, 0) + 1
    capped = max(1, min(limit, 50))
    return {
        "total": len(items),
        "reason_counts": dict(sorted(counts.items())),
        "severity_counts": dict(sorted(severities.items())),
        "sample": items[:capped],
        "truncated": len(items) > capped,
    }


def _queue_item(workspace_id: str, codebase_id: str, snapshot_id: str | None, target_type: str, target_id: str, reason: str, confidence: float, major_below: float, item: dict[str, Any]) -> dict[str, Any]:
    severity = "major" if reason in {"missing_evidence", "unsupported_semantic_claim"} or confidence < major_below else "minor"
    return {
        "schema_version": SCHEMA_VERSION,
        "review_id": _stable_id(target_type, target_id, reason),
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id or item.get("snapshot_id"),
        "target_type": target_type,
        "target_id": target_id,
        "reason": reason,
        "severity": severity,
        "confidence": confidence,
        "signals": list(item.get("signals") or [target_type]),
        "evidence": list(item.get("evidence") or []),
        "recommended_action": _recommended_action(reason),
        "created_at": now(),
    }


def _recommended_action(reason: str) -> str:
    if reason == "missing_evidence":
        return "add or verify source evidence before using as accepted architecture fact"
    if reason == "redacted_sensitive_value":
        return "review redacted configuration value without exposing the secret"
    if reason == "unknown_config_type":
        return "classify the configuration type or keep it as needs_review"
    return "review before using as accepted architecture fact"


def _target_id(item: dict[str, Any]) -> str:
    for key in ("role_id", "layer_id", "boundary_id", "pattern_id", "fact_id", "item_id", "deployment_id", "schema_id"):
        if item.get(key):
            return str(item[key])
    return ""


def _confidence(item: dict[str, Any]) -> float:
    try:
        return float(item.get("confidence") or 0)
    except (TypeError, ValueError):
        return 0.0


def _is_unknown_type(item: dict[str, Any]) -> bool:
    for key in ("role_type", "layer_type", "boundary_type", "pattern_type", "fact_type", "item_type", "deployment_type", "schema_type"):
        value = str(item.get(key) or "")
        if value.startswith("unknown") or value.endswith("_hint"):
            return True
    return False


def _stable_id(target_type: str, target_id: str, reason: str) -> str:
    digest = hashlib.sha256(f"{target_type}:{target_id}:{reason}".encode("utf-8")).hexdigest()[:16]
    return f"review:{digest}"


def _dedupe(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    deduped: dict[str, dict[str, Any]] = {}
    for item in items:
        review_id = str(item.get("review_id") or "")
        if review_id and review_id not in deduped:
            deduped[review_id] = item
    return [deduped[key] for key in sorted(deduped)]
