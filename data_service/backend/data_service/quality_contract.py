"""Shared quality contract helpers for HTTP and future CLI/MCP entrypoints."""

from __future__ import annotations

import hashlib
import json
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .service import DataService


LOW_SIGNAL_AUDIT_LIMIT_MIN = 1
LOW_SIGNAL_AUDIT_LIMIT_MAX = 100
LOW_SIGNAL_AUDIT_LIMIT_DEFAULT = 30
QUALITY_RULE_LIMIT_MIN = 1
QUALITY_RULE_LIMIT_MAX = 100
QUALITY_RULE_LIMIT_DEFAULT = 50
_SAFE_TITLE_DERIVED_KINDS = {"question", "note", "fact_candidate", "risk"}
_QUALITY_RULE_DRAFT_STATUSES = {"draft", "proposed", "pending_review"}
_QUALITY_RULE_TERMINAL_STATUSES = {"approved", "rejected", "archived", "revoked", "active", "applied"}
_QUALITY_REVIEW_ALLOWED_STATUSES = {"draft", "approved", "rejected", "archived", "revoked"}
_QUALITY_REVIEW_BLOCKED_CURRENT_STATUSES = {"active", "applied"}
_QUALITY_ACTION_TO_RULE_TYPE = {
    "rename_suggest": "rename",
    "merge_suggest": "merge",
    "mark_noise": "suppress",
    "needs_review": "review",
}
_QUALITY_RULE_TYPE_TO_ACTION = {
    "rename": "rename_suggest",
    "merge": "merge_suggest",
    "suppress": "mark_noise",
    "review": "needs_review",
}
_FORBIDDEN_CONTRACT_KEYS = {
    "workspace_path",
    "root_path",
    "filesystem_path",
    "session_storage_path",
    "source_path",
    "original_path",
    "local_path",
    "artifact_physical_path",
    "graphrag_cache_path",
    "cache_path",
    "physical_path",
    "internal_path",
    "debug_paths",
    "feedback_path",
    "rules_path",
    "plan_path",
    "path",
    "paths",
}
_PATH_LIKE_MARKERS = (".json", ".jsonl", ".parquet", ".md", "/workspace/", "/quality/", "/graphrag/", "/llmwiki/")
_QUALITY_METADATA_MAX_BYTES = 8192
_QUALITY_METADATA_MAX_DEPTH = 8


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return default


def normalize_low_signal_audit_limit(value: object, *, default: int = LOW_SIGNAL_AUDIT_LIMIT_DEFAULT) -> int:
    try:
        parsed = int(value if value is not None else default)
    except (TypeError, ValueError) as exc:
        raise ValueError("limit must be an integer") from exc
    if parsed < LOW_SIGNAL_AUDIT_LIMIT_MIN or parsed > LOW_SIGNAL_AUDIT_LIMIT_MAX:
        raise ValueError(f"limit must be between {LOW_SIGNAL_AUDIT_LIMIT_MIN} and {LOW_SIGNAL_AUDIT_LIMIT_MAX}")
    return parsed


def normalize_quality_rule_limit(value: object, *, default: int = QUALITY_RULE_LIMIT_DEFAULT) -> int:
    try:
        parsed = int(value if value is not None else default)
    except (TypeError, ValueError) as exc:
        raise ValueError("limit must be an integer") from exc
    if parsed < QUALITY_RULE_LIMIT_MIN or parsed > QUALITY_RULE_LIMIT_MAX:
        raise ValueError(f"limit must be between {QUALITY_RULE_LIMIT_MIN} and {QUALITY_RULE_LIMIT_MAX}")
    return parsed


def record_quality_feedback_payload(
    service: DataService,
    *,
    target_type: str,
    target_id: str,
    action: str,
    label: str = "",
    suggested_value: str = "",
    reason: str = "",
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    record = service.record_quality_feedback(
        target_type=target_type,
        target_id=target_id,
        action=action,
        label=label,
        suggested_value=suggested_value,
        reason=reason,
        metadata=metadata or {},
    )
    return {
        "workspace": str(service.workspace),
        "feedback": record,
        "summary": service.read_quality_feedback(limit=20)["summary"],
    }


def _sanitize_quality_contract_value(value: Any) -> Any:
    if isinstance(value, dict):
        sanitized: dict[str, Any] = {}
        for key, item in value.items():
            key_text = str(key)
            key_lower = key_text.lower()
            if key_lower in _FORBIDDEN_CONTRACT_KEYS or key_lower.endswith("_path") or key_lower.endswith("_paths"):
                continue
            sanitized[key_text] = _sanitize_quality_contract_value(item)
        return sanitized
    if isinstance(value, list):
        return [_sanitize_quality_contract_value(item) for item in value]
    if isinstance(value, str):
        text = value.strip()
        lower = text.lower()
        if text.startswith("/") or text.startswith("~") or ".." in text or any(marker in lower for marker in _PATH_LIKE_MARKERS):
            return "[redacted]"
        return value
    return value


def _validate_quality_metadata(value: dict[str, Any]) -> dict[str, Any]:
    def depth(item: Any) -> int:
        if isinstance(item, dict):
            return 1 + max((depth(child) for child in item.values()), default=0)
        if isinstance(item, list):
            return 1 + max((depth(child) for child in item), default=0)
        return 0

    if depth(value) > _QUALITY_METADATA_MAX_DEPTH:
        raise ValueError("metadata is too deeply nested")
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True)
    if len(encoded.encode("utf-8")) > _QUALITY_METADATA_MAX_BYTES:
        raise ValueError("metadata is too large")
    return _sanitize_quality_contract_value(value)


def _validate_quality_target_id(target_id: str) -> str:
    normalized = str(target_id or "").strip()
    if not normalized:
        raise ValueError("target_id is required")
    lower = normalized.lower()
    if normalized.startswith(("/", "~")) or "\\" in normalized or ".." in normalized or any(marker in lower for marker in _PATH_LIKE_MARKERS):
        raise ValueError("target_id must be a stable non-path identifier")
    return normalized


def _quality_rules_artifact_ref(workspace_id: str) -> str:
    return f"quality-correction-rules://{workspace_id}"


def _quality_plan_artifact_ref(workspace_id: str) -> str:
    return f"quality-correction-plan://{workspace_id}"


def _stable_quality_rule(rule: dict[str, Any]) -> dict[str, Any]:
    rule_type = str(rule.get("rule_type") or "").strip()
    return {
        "rule_id": str(rule.get("rule_id") or "").strip(),
        "target_type": str(rule.get("target_type") or "").strip(),
        "target_id": str(rule.get("target_id") or "").strip(),
        "action": _QUALITY_RULE_TYPE_TO_ACTION.get(rule_type, rule_type),
        "label": str(rule.get("current_label") or rule.get("label") or "").strip(),
        "suggested_value": str(rule.get("proposed_value") or rule.get("suggested_value") or "").strip(),
        "reason": str(rule.get("reason") or "").strip(),
        "status": str(rule.get("status") or "draft").strip(),
        "created_at": str(rule.get("created_at") or "").strip(),
        "updated_at": str(rule.get("updated_at") or "").strip(),
        "reviewed_at": str(rule.get("reviewed_at") or "").strip(),
        "reviewer": str(rule.get("reviewer") or "").strip(),
        "note": str(rule.get("review_note") or rule.get("note") or "").strip(),
        "metadata": _sanitize_quality_contract_value(rule.get("metadata") or {}),
    }


def _read_quality_rules_payload_without_build(service: DataService) -> dict[str, Any]:
    service.ensure_layout()
    payload = _read_json(service.layout.quality_correction_rules_json, {})
    if not isinstance(payload, dict):
        payload = {}
    rules = list(payload.get("rules", []) or [])
    return {
        "schema_version": str(payload.get("schema_version") or "1.0"),
        "generated_at": str(payload.get("generated_at") or ""),
        "updated_at": str(payload.get("updated_at") or ""),
        "rules": [dict(rule) for rule in rules if isinstance(rule, dict)],
    }


def _write_quality_rules_payload(service: DataService, payload: dict[str, Any]) -> None:
    service.ensure_layout()
    payload["summary"] = service._build_correction_rules_summary(list(payload.get("rules", []) or []))
    service._write_quality_correction_rules_payload(payload)


def _read_quality_plan_payload_without_build(service: DataService) -> dict[str, Any]:
    service.ensure_layout()
    payload = _read_json(service.layout.quality_correction_plan_json, {})
    return payload if isinstance(payload, dict) else {}


def _stable_quality_plan_action(action: dict[str, Any]) -> dict[str, Any]:
    rule_id = str(action.get("source_rule_id") or action.get("rule_id") or "").strip()
    target_type = str(action.get("target_type") or "").strip()
    target_id = str(action.get("target_id") or "").strip()
    action_name = str(action.get("action") or "").strip()
    label = str(action.get("current_label") or action.get("label") or "").strip()
    proposed_value = str(action.get("proposed_value") or action.get("suggested_value") or "").strip()
    summary_parts = [part for part in [action_name, target_type, target_id] if part]
    if proposed_value:
        summary_parts.append(f"to {proposed_value}")
    existing_summary = str(action.get("summary") or "").strip()
    return {
        "action_id": str(action.get("action_id") or f"action_{rule_id}" if rule_id else "").strip(),
        "rule_id": rule_id,
        "target_type": target_type,
        "target_id": target_id,
        "action": action_name,
        "label": label,
        "summary": existing_summary or " ".join(summary_parts),
        "status": str(action.get("status") or "planned").strip(),
    }


def _quality_plan_id(*, included_rule_ids: list[str], actions: list[dict[str, Any]], excluded_rule_counts: dict[str, int]) -> str:
    signature = {
        "included_rule_ids": sorted(included_rule_ids),
        "actions": actions,
        "excluded_rule_counts": dict(sorted(excluded_rule_counts.items())),
    }
    digest = hashlib.sha256(json.dumps(signature, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()
    return f"qplan_{digest[:16]}"


def _stable_quality_plan_payload(payload: dict[str, Any], *, workspace_id: str) -> dict[str, Any]:
    raw_actions = [item for item in list(payload.get("actions", []) or []) if isinstance(item, dict)]
    actions = [_stable_quality_plan_action(action) for action in raw_actions]
    included_rule_ids = [
        str(item).strip()
        for item in list(payload.get("included_rule_ids", []) or [action.get("rule_id") for action in actions])
        if str(item or "").strip()
    ]
    excluded_rule_counts = {
        str(key): int(value)
        for key, value in dict(payload.get("excluded_rule_counts") or {}).items()
        if isinstance(value, int) or str(value).isdigit()
    }
    plan_id = str(payload.get("plan_id") or "").strip() or _quality_plan_id(
        included_rule_ids=included_rule_ids,
        actions=actions,
        excluded_rule_counts=excluded_rule_counts,
    )
    artifact_ref = _quality_plan_artifact_ref(workspace_id)
    return {
        "workspace_id": workspace_id,
        "plan_id": plan_id,
        "status": str(payload.get("status") or "planned").strip(),
        "rule_count": int(payload.get("rule_count") or len(included_rule_ids)),
        "action_count": int(payload.get("action_count") or len(actions)),
        "included_rule_ids": included_rule_ids,
        "excluded_rule_counts": excluded_rule_counts,
        "rules_summary": _sanitize_quality_contract_value(payload.get("rules_summary") or {}),
        "actions": actions,
        "summary": _sanitize_quality_contract_value(payload.get("summary") or {}),
        "artifact_ref": artifact_ref,
        "created_at": str(payload.get("created_at") or payload.get("generated_at") or "").strip(),
        "updated_at": str(payload.get("updated_at") or payload.get("generated_at") or "").strip(),
    }


def _new_quality_rule_from_request(
    *,
    target_type: str,
    target_id: str,
    action: str,
    label: str,
    suggested_value: str,
    reason: str,
    metadata: dict[str, Any],
) -> dict[str, Any]:
    normalized_target_type = str(target_type or "").strip()
    normalized_target_id = _validate_quality_target_id(target_id)
    normalized_action = str(action or "").strip()
    if not normalized_target_type:
        raise ValueError("target_type is required")
    if normalized_action not in _QUALITY_ACTION_TO_RULE_TYPE:
        raise ValueError(f"Unsupported action: {normalized_action}")
    rule_type = _QUALITY_ACTION_TO_RULE_TYPE[normalized_action]
    normalized_label = str(label or "").strip()
    normalized_suggested_value = str(suggested_value or "").strip()
    normalized_reason = str(reason or "").strip()
    if rule_type in {"rename", "merge"} and not normalized_suggested_value:
        raise ValueError("suggested_value is required for rename_suggest and merge_suggest")
    now = _now()
    return {
        "rule_id": f"rule_manual_{uuid.uuid4().hex[:12]}",
        "rule_type": rule_type,
        "status": "draft",
        "target_type": normalized_target_type,
        "target_id": normalized_target_id,
        "current_label": normalized_label,
        "proposed_value": normalized_suggested_value,
        "reason": normalized_reason,
        "source_feedback_id": "",
        "created_at": now,
        "updated_at": now,
        "metadata": _validate_quality_metadata(metadata or {}),
    }


def target_quality_correction_rules_list_payload(
    service: DataService,
    *,
    workspace_id: str,
    limit: int = QUALITY_RULE_LIMIT_DEFAULT,
    status: str | None = None,
    envelope,
) -> dict[str, Any]:
    normalized_limit = normalize_quality_rule_limit(limit)
    payload = _read_quality_rules_payload_without_build(service)
    status_filter = str(status or "").strip()
    if status_filter and status_filter not in _QUALITY_RULE_DRAFT_STATUSES | _QUALITY_RULE_TERMINAL_STATUSES:
        raise ValueError(f"Unsupported status: {status_filter}")
    rules = list(payload.get("rules", []) or [])
    filtered = [rule for rule in rules if not status_filter or str(rule.get("status") or "").strip() == status_filter]
    visible = filtered[:normalized_limit]
    artifact_ref = _quality_rules_artifact_ref(workspace_id) if rules else None
    artifact_refs = [{"type": "quality_correction_rules", "artifact_ref": artifact_ref}] if artifact_ref else []
    return envelope(
        workspace_id=workspace_id,
        status="ok",
        artifact_refs=artifact_refs,
        next_actions=["knowledge_correction_rules"],
        data={
            "workspace_id": workspace_id,
            "rules": [_stable_quality_rule(rule) for rule in visible],
            "count": len(visible),
            "total_count": len(rules),
            "filtered_count": len(filtered),
            "limit": normalized_limit,
            "truncated": len(filtered) > normalized_limit,
            "artifact_ref": artifact_ref,
            "summary": _sanitize_quality_contract_value(service._build_correction_rules_summary(rules)),
        },
    )


def target_quality_correction_rule_write_payload(
    service: DataService,
    *,
    workspace_id: str,
    rule_id: str = "",
    target_type: str,
    target_id: str,
    action: str,
    label: str = "",
    suggested_value: str = "",
    reason: str = "",
    metadata: dict[str, Any] | None = None,
    envelope,
) -> dict[str, Any]:
    payload = _read_quality_rules_payload_without_build(service)
    rules = list(payload.get("rules", []) or [])
    now = _now()
    normalized_rule_id = str(rule_id or "").strip()
    candidate = _new_quality_rule_from_request(
        target_type=target_type,
        target_id=target_id,
        action=action,
        label=label,
        suggested_value=suggested_value,
        reason=reason,
        metadata=metadata or {},
    )
    operation = "created"
    matched_rule: dict[str, Any] | None = None
    if normalized_rule_id:
        for index, existing in enumerate(rules):
            if str(existing.get("rule_id") or "").strip() != normalized_rule_id:
                continue
            status = str(existing.get("status") or "draft").strip()
            if status in _QUALITY_RULE_TERMINAL_STATUSES:
                raise ValueError("terminal correction rules cannot be updated in E2")
            if status not in _QUALITY_RULE_DRAFT_STATUSES:
                raise ValueError("correction rule status cannot be updated in E2")
            candidate["rule_id"] = normalized_rule_id
            candidate["status"] = status or "draft"
            candidate["created_at"] = str(existing.get("created_at") or now)
            candidate["updated_at"] = now
            candidate["source_feedback_id"] = str(existing.get("source_feedback_id") or "")
            rules[index] = candidate
            matched_rule = candidate
            operation = "updated"
            break
        if matched_rule is None:
            raise ValueError("Unknown correction rule")
    else:
        rules.append(candidate)
        matched_rule = candidate

    payload = {
        "schema_version": str(payload.get("schema_version") or "1.0"),
        "workspace": str(service.workspace),
        "generated_at": str(payload.get("generated_at") or now),
        "updated_at": now,
        "source_feedback_count": int(payload.get("source_feedback_count") or 0),
        "rules": rules,
    }
    _write_quality_rules_payload(service, payload)
    artifact_ref = _quality_rules_artifact_ref(workspace_id)
    return envelope(
        workspace_id=workspace_id,
        status="ok",
        artifact_refs=[{"type": "quality_correction_rules", "artifact_ref": artifact_ref}],
        next_actions=["knowledge_correction_rules"],
        data={
            "workspace_id": workspace_id,
            "operation": operation,
            "rule": _stable_quality_rule(matched_rule or {}),
            "rule_id": str((matched_rule or {}).get("rule_id") or ""),
            "artifact_ref": artifact_ref,
            "summary": _sanitize_quality_contract_value(service._build_correction_rules_summary(rules)),
        },
    )


def target_quality_correction_rule_review_payload(
    service: DataService,
    *,
    workspace_id: str,
    rule_id: str,
    status: str,
    reviewer: str = "",
    note: str = "",
    envelope,
) -> dict[str, Any]:
    """Review one correction rule without building or updating correction plans."""
    payload = _read_quality_rules_payload_without_build(service)
    rules = list(payload.get("rules", []) or [])
    normalized_rule_id = str(rule_id or "").strip()
    normalized_status = str(status or "").strip()
    normalized_reviewer = str(reviewer or "").strip()
    normalized_note = str(note or "").strip()
    if not normalized_rule_id:
        raise ValueError("rule_id is required")
    if normalized_status not in _QUALITY_REVIEW_ALLOWED_STATUSES:
        raise ValueError(f"Unsupported review status: {normalized_status}")
    if len(normalized_reviewer) > 256:
        raise ValueError("reviewer must be 256 characters or fewer")
    if len(normalized_note) > 4096:
        raise ValueError("note must be 4096 characters or fewer")

    matched_rule: dict[str, Any] | None = None
    now = _now()
    for rule in rules:
        if str(rule.get("rule_id") or "").strip() != normalized_rule_id:
            continue
        current_status = str(rule.get("status") or "draft").strip()
        if current_status in _QUALITY_REVIEW_BLOCKED_CURRENT_STATUSES:
            raise ValueError("active/applied correction rules cannot be reviewed in E3")
        rule["status"] = normalized_status
        rule["reviewed_at"] = now
        rule["reviewer"] = normalized_reviewer
        rule["review_note"] = normalized_note
        rule["updated_at"] = now
        matched_rule = rule
        break
    if matched_rule is None:
        raise ValueError("Unknown correction rule")

    payload = {
        "schema_version": str(payload.get("schema_version") or "1.0"),
        "workspace": str(service.workspace),
        "generated_at": str(payload.get("generated_at") or now),
        "updated_at": now,
        "source_feedback_count": int(payload.get("source_feedback_count") or 0),
        "rules": rules,
    }
    _write_quality_rules_payload(service, payload)
    artifact_ref = _quality_rules_artifact_ref(workspace_id)
    return envelope(
        workspace_id=workspace_id,
        status="ok",
        artifact_refs=[{"type": "quality_correction_rules", "artifact_ref": artifact_ref}],
        next_actions=["knowledge_correction_rules"],
        data={
            "workspace_id": workspace_id,
            "rule_id": normalized_rule_id,
            "status": normalized_status,
            "reviewer": normalized_reviewer,
            "reviewed_at": now,
            "note": normalized_note,
            "rule": _stable_quality_rule(matched_rule),
            "summary": _sanitize_quality_contract_value(service._build_correction_rules_summary(rules)),
            "artifact_ref": artifact_ref,
        },
    )


def target_quality_correction_plan_read_payload(
    service: DataService,
    *,
    workspace_id: str,
    envelope,
    blocked,
) -> dict[str, Any]:
    """Read an existing correction plan without generating or activating anything."""
    payload = _read_quality_plan_payload_without_build(service)
    if not payload:
        return blocked(
            workspace_id=workspace_id,
            message="Quality correction plan artifact is not available",
            code="quality_correction_plan_no_artifact",
            next_actions=["knowledge_correction_plan"],
        )
    artifact_ref = _quality_plan_artifact_ref(workspace_id)
    stable = _stable_quality_plan_payload(payload, workspace_id=workspace_id)
    return envelope(
        workspace_id=workspace_id,
        status="ok",
        artifact_refs=[{"type": "quality_correction_plan", "artifact_ref": artifact_ref}],
        next_actions=["knowledge_correction_plan"],
        data=stable,
    )


def target_quality_correction_plan_generate_payload(
    service: DataService,
    *,
    workspace_id: str,
    envelope,
) -> dict[str, Any]:
    """Generate a correction plan artifact without applying corrections or rebuilding quality state."""
    service.ensure_layout()
    rules_payload = _read_quality_rules_payload_without_build(service)
    rules = list(rules_payload.get("rules", []) or [])
    approved_rules = [rule for rule in rules if str(rule.get("status") or "draft").strip() == "approved"]
    excluded_rule_counts: dict[str, int] = {}
    for rule in rules:
        status = str(rule.get("status") or "draft").strip()
        if status != "approved":
            excluded_rule_counts[status] = excluded_rule_counts.get(status, 0) + 1

    raw_actions: list[dict[str, Any]] = []
    approved_without_action = 0
    for rule in approved_rules:
        action = service._correction_rule_to_plan_action(rule)
        if not action:
            approved_without_action += 1
            continue
        raw_actions.append(action)
    if approved_without_action:
        excluded_rule_counts["approved_without_action"] = approved_without_action

    actions = [_stable_quality_plan_action(action) for action in raw_actions]
    included_rule_ids = [action["rule_id"] for action in actions if action.get("rule_id")]
    plan_id = _quality_plan_id(
        included_rule_ids=included_rule_ids,
        actions=actions,
        excluded_rule_counts=excluded_rule_counts,
    )
    now = _now()
    existing = _read_quality_plan_payload_without_build(service)
    previous_plan_id = str(existing.get("plan_id") or "").strip()
    artifact_ref = _quality_plan_artifact_ref(workspace_id)
    payload = {
        "schema_version": "1.0",
        "workspace_id": workspace_id,
        "plan_id": plan_id,
        "status": "planned",
        "created_at": now,
        "generated_at": now,
        "updated_at": now,
        "rule_count": len(included_rule_ids),
        "source_rule_count": len(approved_rules),
        "action_count": len(actions),
        "included_rule_ids": included_rule_ids,
        "excluded_rule_counts": dict(sorted(excluded_rule_counts.items())),
        "rules_summary": {
            "approved_rule_count": len(approved_rules),
            "included_rule_count": len(included_rule_ids),
            "excluded_rule_counts": dict(sorted(excluded_rule_counts.items())),
        },
        "actions": actions,
        "summary": service._build_correction_plan_summary(actions),
        "artifact_ref": artifact_ref,
        "notes": [
            "Only approved correction rules are included.",
            "This artifact is generated in plan-only mode.",
            "No correction is executed and read-time governance is not activated.",
        ],
    }
    service.layout.quality_correction_plan_json.parent.mkdir(parents=True, exist_ok=True)
    service.layout.quality_correction_plan_json.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    stable = _stable_quality_plan_payload(payload, workspace_id=workspace_id)
    stable["replaced_existing"] = bool(existing)
    stable["previous_plan_id"] = previous_plan_id
    return envelope(
        workspace_id=workspace_id,
        status="ok",
        artifact_refs=[{"type": "quality_correction_plan", "artifact_ref": artifact_ref}],
        next_actions=["knowledge_correction_plan"],
        data=stable,
    )


def target_quality_correction_rules_build_payload(
    service: DataService,
    *,
    workspace_id: str,
    envelope,
) -> dict[str, Any]:
    """Build correction-rules artifact only; never generate or mutate correction plans."""
    existing_plan = _read_quality_plan_payload_without_build(service)
    payload = service.build_quality_correction_rules()
    rules = [rule for rule in list(payload.get("rules", []) or []) if isinstance(rule, dict)]
    normalized_limit = QUALITY_RULE_LIMIT_DEFAULT
    visible_rules = rules[:normalized_limit]
    artifact_ref = _quality_rules_artifact_ref(workspace_id)
    warnings: list[str] = []
    next_actions = ["knowledge_correction_rules"]
    if existing_plan:
        warnings.append("correction_plan_may_be_stale")
        next_actions.append("knowledge_correction_plan")
    return envelope(
        workspace_id=workspace_id,
        status="ok",
        artifact_refs=[{"type": "quality_correction_rules", "artifact_ref": artifact_ref}],
        warnings=warnings,
        next_actions=next_actions,
        data={
            "workspace_id": workspace_id,
            "status": "built",
            "count": len(rules),
            "total_count": len(rules),
            "source_feedback_count": int(payload.get("source_feedback_count") or 0),
            "rules": [_stable_quality_rule(rule) for rule in visible_rules],
            "limit": normalized_limit,
            "truncated": len(rules) > normalized_limit,
            "artifact_ref": artifact_ref,
            "summary": _sanitize_quality_contract_value(
                payload.get("summary") or service._build_correction_rules_summary(rules)
            ),
        },
    )


def target_quality_feedback_payload(
    service: DataService,
    *,
    workspace_id: str,
    target_type: str,
    target_id: str,
    action: str,
    label: str = "",
    suggested_value: str = "",
    reason: str = "",
    metadata: dict[str, Any] | None = None,
    envelope,
) -> dict[str, Any]:
    """Record quality feedback and project the result as a stable target HTTP contract."""
    normalized_target_id = _validate_quality_target_id(target_id)
    result = record_quality_feedback_payload(
        service,
        target_type=target_type,
        target_id=normalized_target_id,
        action=action,
        label=label,
        suggested_value=suggested_value,
        reason=reason,
        metadata=_sanitize_quality_contract_value(metadata or {}),
    )
    feedback = dict(result.get("feedback") or {})
    feedback_id = str(feedback.get("feedback_id") or "")
    artifact_ref = f"quality-feedback://{feedback_id}" if feedback_id else None
    stable_feedback = {
        "workspace_id": workspace_id,
        "feedback_id": feedback_id,
        "target_type": feedback.get("target_type"),
        "target_id": feedback.get("target_id"),
        "action": feedback.get("action"),
        "label": feedback.get("label", ""),
        "suggested_value": feedback.get("suggested_value", ""),
        "reason": feedback.get("reason", ""),
        "metadata": _sanitize_quality_contract_value(feedback.get("metadata") or {}),
        "status": "recorded",
        "created_at": feedback.get("created_at"),
        "artifact_ref": artifact_ref,
    }
    artifact_refs = [{"type": "quality_feedback", "feedback_id": feedback_id, "artifact_ref": artifact_ref}] if artifact_ref else []
    return envelope(
        workspace_id=workspace_id,
        status="ok",
        artifact_refs=artifact_refs,
        next_actions=["knowledge_quality_feedback_list", "knowledge_correction_rules"],
        data={
            "workspace_id": workspace_id,
            "feedback": stable_feedback,
            "summary": _sanitize_quality_contract_value(result.get("summary") or {}),
        },
    )


def quality_feedback_list_payload(
    service: DataService,
    *,
    limit: int = 100,
    target_type: str | None = None,
    target_id: str | None = None,
) -> dict[str, Any]:
    return service.read_quality_feedback(
        limit=limit,
        target_type=target_type,
        target_id=target_id,
    )


def quality_correction_rules_payload(
    service: DataService,
    *,
    limit: int = 100,
    status: str | None = None,
) -> dict[str, Any]:
    return service.read_quality_correction_rules(limit=limit, status=status)


def quality_summary_payload(service: DataService) -> dict[str, Any]:
    bundle = service.read_summary_bundle()
    return {
        "workspace": str(service.workspace),
        "quality": bundle.get("quality", {}),
        "quality_feedback": bundle.get("quality_feedback", []),
        "quality_correction_rules": bundle.get("quality_correction_rules", []),
        "quality_correction_plan": bundle.get("quality_correction_plan", {}),
    }


def quality_correction_plan_preview_payload(service: DataService, *, rebuild: bool = False) -> dict[str, Any]:
    if rebuild:
        return service.build_quality_correction_plan()
    return service.read_quality_correction_plan(build_if_missing=False)


def quality_correction_rules_build_payload(service: DataService) -> dict[str, Any]:
    return service.build_quality_correction_rules()


def quality_correction_rule_review_payload(
    service: DataService,
    *,
    rule_id: str,
    status: str,
    reviewer: str = "",
    note: str = "",
) -> dict[str, Any]:
    return service.review_quality_correction_rule(
        rule_id=rule_id,
        status=status,
        reviewer=reviewer,
        note=note,
    )


def quality_correction_plan_payload(service: DataService) -> dict[str, Any]:
    return service.build_quality_correction_plan()


def _markdown_title(path: Path) -> str:
    try:
        for line in path.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if stripped.startswith("#"):
                return stripped.lstrip("#").strip()
    except OSError:
        pass
    return path.stem


def _source_low_signal(source: dict[str, Any]) -> dict[str, Any]:
    return dict(source.get("profile", {}).get("low_signal") or source.get("low_signal") or {})


def _title_like_terms(title: str) -> set[str]:
    text = str(title or "").strip()
    if not text:
        return set()
    terms = {text}
    stem = Path(text).stem
    if stem:
        terms.add(stem)
    without_uuid = re.sub(r"^[0-9a-fA-F-]{12,}[-_\\s]+", "", stem).strip()
    if without_uuid and len(without_uuid) >= 8:
        terms.add(without_uuid)
    return {term for term in terms if len(term) >= 8}


def low_signal_audit_payload(service: DataService, *, limit: object = LOW_SIGNAL_AUDIT_LIMIT_DEFAULT) -> dict[str, Any]:
    normalized_limit = normalize_low_signal_audit_limit(limit)
    service.ensure_layout()
    summary_bundle = service.read_summary_bundle()
    distill_bundle = service.read_distill_bundle(limit=200)
    distill_quality = dict(summary_bundle.get("quality", {}).get("distill", {}) or {})
    sources = list(distill_bundle.get("sources", []) or [])
    low_signal_sources = [source for source in sources if _source_low_signal(source)]
    low_signal_terms: dict[str, set[str]] = {
        str(source.get("source_id") or ""): _title_like_terms(str(source.get("title") or ""))
        for source in low_signal_sources
    }

    title_derived_conclusion_count = 0
    disallowed_title_derived_count = 0
    title_derived_kind_counts: dict[str, int] = {}
    title_derived_samples: list[dict[str, Any]] = []
    disallowed_samples: list[dict[str, Any]] = []
    scanned_source_count = 0

    if service.layout.distill_sources_dir.exists():
        for source_path in sorted(service.layout.distill_sources_dir.glob("*.json")):
            source_record = _read_json(source_path, {})
            if not source_record:
                continue
            scanned_source_count += 1
            for unit in source_record.get("units", []) or []:
                if not bool(unit.get("is_title_derived", False)):
                    continue
                kind = str(unit.get("kind") or "unknown")
                title_derived_kind_counts[kind] = title_derived_kind_counts.get(kind, 0) + 1
                sample = {
                    "source_id": source_record.get("source_id") or source_path.stem,
                    "source_title": source_record.get("title") or source_path.stem,
                    "unit_id": unit.get("unit_id"),
                    "kind": kind,
                    "text": str(unit.get("text") or unit.get("normalized_text") or "")[:220],
                }
                if len(title_derived_samples) < normalized_limit:
                    title_derived_samples.append(sample)
                if kind == "conclusion":
                    title_derived_conclusion_count += 1
                if kind not in _SAFE_TITLE_DERIVED_KINDS:
                    disallowed_title_derived_count += 1
                    if len(disallowed_samples) < normalized_limit:
                        disallowed_samples.append(sample)

    llmwiki_title_leaks: list[dict[str, Any]] = []
    if service.layout.llmwiki_pages_dir.exists() and low_signal_terms:
        for page_path in sorted(service.layout.llmwiki_pages_dir.glob("*.md")):
            page_title = _markdown_title(page_path)
            haystack = f"{page_path.stem}\n{page_title}"
            for source_id, terms in low_signal_terms.items():
                matched = next((term for term in terms if len(term) >= 18 and term in haystack), "")
                if matched:
                    source = next((item for item in low_signal_sources if str(item.get("source_id") or "") == source_id), {})
                    llmwiki_title_leaks.append(
                        {
                            "source_id": source_id,
                            "source_title": source.get("title"),
                            "page_slug": page_path.stem,
                            "page_title": page_title,
                            "matched_term": matched,
                        }
                    )
                    break
            if len(llmwiki_title_leaks) >= normalized_limit:
                break

    graph_snapshot = service.get_graph_snapshot(max_nodes=160)
    graph_quality = dict(graph_snapshot.get("quality_diagnostics", {}) or {})
    top_communities = list(graph_quality.get("top_communities", []) or graph_snapshot.get("communities", []) or [])
    graph_title_leaks: list[dict[str, Any]] = []
    for community in top_communities[:50]:
        label = str(community.get("title") or community.get("label") or community.get("name") or community.get("id") or "")
        if len(label) >= 36:
            graph_title_leaks.append({"community_id": community.get("id") or community.get("target_id"), "title": label, "reason": "long_community_title"})
            continue
        for source_id, terms in low_signal_terms.items():
            matched = next((term for term in terms if len(term) >= 18 and term in label), "")
            if matched:
                graph_title_leaks.append(
                    {
                        "community_id": community.get("id") or community.get("target_id"),
                        "title": label,
                        "source_id": source_id,
                        "matched_term": matched,
                        "reason": "low_signal_title_leak",
                    }
                )
                break
        if len(graph_title_leaks) >= normalized_limit:
            break

    checks = [
        {
            "check_id": "zero_unit_count",
            "label": "zero unit source",
            "status": "passed" if int(distill_quality.get("zero_unit_count", 0) or 0) == 0 else "failed",
            "actual": int(distill_quality.get("zero_unit_count", 0) or 0),
            "expected": 0,
        },
        {
            "check_id": "title_derived_conclusion_count",
            "label": "标题派生 conclusion",
            "status": "passed" if title_derived_conclusion_count == 0 else "failed",
            "actual": title_derived_conclusion_count,
            "expected": 0,
        },
        {
            "check_id": "disallowed_title_derived_kind_count",
            "label": "标题派生强语义 unit",
            "status": "passed" if disallowed_title_derived_count == 0 else "failed",
            "actual": disallowed_title_derived_count,
            "expected": 0,
            "allowed_kinds": sorted(_SAFE_TITLE_DERIVED_KINDS),
        },
        {
            "check_id": "llmwiki_low_signal_title_leak_count",
            "label": "LLMWiki 长标题泄漏",
            "status": "passed" if not llmwiki_title_leaks else "warning",
            "actual": len(llmwiki_title_leaks),
            "expected": 0,
        },
        {
            "check_id": "graphrag_low_signal_title_leak_count",
            "label": "GraphRAG 头部社区长标题泄漏",
            "status": "passed" if not graph_title_leaks else "warning",
            "actual": len(graph_title_leaks),
            "expected": 0,
        },
    ]
    failed_count = sum(1 for check in checks if check["status"] == "failed")
    warning_count = sum(1 for check in checks if check["status"] == "warning")
    overall_status = "failed" if failed_count else ("warning" if warning_count else "passed")
    recommendations = []
    if title_derived_conclusion_count or disallowed_title_derived_count:
        recommendations.append("收紧 title fallback：标题派生内容只允许 question / note / fact_candidate / risk。")
    if llmwiki_title_leaks:
        recommendations.append("抽查 LLMWiki 页面标题，将低信号 source 的原始长标题保留到 source trace，不作为 topic 标题。")
    if graph_title_leaks:
        recommendations.append("抽查 GraphRAG top communities，把长标题或功能尾缀主题降权、合并或标记为噪音。")
    if not recommendations:
        recommendations.append("当前低信号 source 审计未发现阻塞项，继续用真实知识库定期回归。")

    return {
        "workspace": str(service.workspace),
        "audited_at": _now(),
        "overall_status": overall_status,
        "checks": checks,
        "metrics": {
            "source_count": len(sources),
            "scanned_source_count": scanned_source_count,
            "low_signal_source_count": len(low_signal_sources),
            "zero_unit_count": int(distill_quality.get("zero_unit_count", 0) or 0),
            "title_fallback_source_count": int(distill_quality.get("title_fallback_source_count", 0) or 0),
            "title_fallback_source_counts": dict(distill_quality.get("title_fallback_source_counts", {}) or {}),
            "title_derived_unit_count": sum(title_derived_kind_counts.values()),
            "title_derived_kind_counts": dict(sorted(title_derived_kind_counts.items())),
            "title_derived_conclusion_count": title_derived_conclusion_count,
            "disallowed_title_derived_count": disallowed_title_derived_count,
            "llmwiki_title_leak_count": len(llmwiki_title_leaks),
            "graphrag_title_leak_count": len(graph_title_leaks),
        },
        "samples": {
            "title_derived": title_derived_samples,
            "disallowed_title_derived": disallowed_samples,
            "llmwiki_title_leaks": llmwiki_title_leaks,
            "graphrag_title_leaks": graph_title_leaks,
        },
        "recommendations": recommendations,
    }
