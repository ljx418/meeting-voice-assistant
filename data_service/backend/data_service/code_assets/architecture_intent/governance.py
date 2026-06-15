"""Read-time governance overlay for architecture intent artifacts."""

from __future__ import annotations

import hashlib
from collections import Counter
from pathlib import Path
from typing import Any

from data_service.mcp_common import now, read_json, write_json

from ..artifacts import read_jsonl, write_jsonl
from .paths import (
    architecture_intent_confirmed_facts_path,
    architecture_intent_governance_artifact_refs,
    architecture_intent_governance_events_path,
    architecture_intent_governance_summary_path,
)
from .source_model import SCHEMA_VERSION, redact_public_text


def confirm_architecture_target(
    *,
    workspace: Path,
    workspace_id: str,
    codebase_id: str,
    snapshot_id: str,
    target_type: str,
    target_id: str,
    note: str = "",
    reviewer: str = "local",
) -> dict[str, Any]:
    return _record_event(
        workspace=workspace,
        workspace_id=workspace_id,
        codebase_id=codebase_id,
        snapshot_id=snapshot_id,
        action="confirm",
        target_type=target_type,
        target_id=target_id,
        note=note,
        reviewer=reviewer,
    )


def revoke_architecture_confirmation(
    *,
    workspace: Path,
    workspace_id: str,
    codebase_id: str,
    snapshot_id: str,
    target_type: str,
    target_id: str,
    note: str = "",
    reviewer: str = "local",
) -> dict[str, Any]:
    return _record_event(
        workspace=workspace,
        workspace_id=workspace_id,
        codebase_id=codebase_id,
        snapshot_id=snapshot_id,
        action="revoke",
        target_type=target_type,
        target_id=target_id,
        note=note,
        reviewer=reviewer,
    )


def read_architecture_governance(*, workspace: Path, codebase_id: str) -> dict[str, Any]:
    summary = read_json(architecture_intent_governance_summary_path(workspace, codebase_id), {})
    return {
        "schema_version": summary.get("schema_version", SCHEMA_VERSION),
        "workspace_id": summary.get("workspace_id"),
        "codebase_id": codebase_id,
        "snapshot_id": summary.get("snapshot_id"),
        "confirmed_facts": read_jsonl(architecture_intent_confirmed_facts_path(workspace, codebase_id)),
        "governance_events": read_jsonl(architecture_intent_governance_events_path(workspace, codebase_id)),
        "summary": summary,
        "artifact_refs": architecture_intent_governance_artifact_refs(codebase_id),
    }


def _record_event(
    *,
    workspace: Path,
    workspace_id: str,
    codebase_id: str,
    snapshot_id: str,
    action: str,
    target_type: str,
    target_id: str,
    note: str,
    reviewer: str,
) -> dict[str, Any]:
    created_at = now()
    events = read_jsonl(architecture_intent_governance_events_path(workspace, codebase_id))
    facts = read_jsonl(architecture_intent_confirmed_facts_path(workspace, codebase_id))
    event = {
        "schema_version": SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "event_id": _stable_id("govevent", snapshot_id, action, target_type, target_id, created_at),
        "action": action,
        "target_type": target_type,
        "target_id": target_id,
        "note": redact_public_text(note),
        "reviewer": redact_public_text(reviewer),
        "created_at": created_at,
    }
    events.append(event)
    if action == "confirm":
        facts = [fact for fact in facts if not (fact.get("target_type") == target_type and fact.get("target_id") == target_id)]
        facts.append(
            {
                "schema_version": SCHEMA_VERSION,
                "workspace_id": workspace_id,
                "codebase_id": codebase_id,
                "snapshot_id": snapshot_id,
                "confirmation_id": _stable_id("confirmed", snapshot_id, target_type, target_id),
                "target_type": target_type,
                "target_id": target_id,
                "status": "confirmed",
                "note": redact_public_text(note),
                "reviewer": redact_public_text(reviewer),
                "source": "read_time_overlay",
                "created_at": created_at,
            }
        )
    elif action == "revoke":
        facts = [fact for fact in facts if not (fact.get("target_type") == target_type and fact.get("target_id") == target_id)]
    write_jsonl(architecture_intent_governance_events_path(workspace, codebase_id), events)
    write_jsonl(architecture_intent_confirmed_facts_path(workspace, codebase_id), facts)
    summary = _summary(workspace_id, codebase_id, snapshot_id, events, facts, created_at)
    write_json(architecture_intent_governance_summary_path(workspace, codebase_id), summary)
    return {"event": event, "confirmed_facts": facts, "summary": summary, "artifact_refs": architecture_intent_governance_artifact_refs(codebase_id)}


def _summary(workspace_id: str, codebase_id: str, snapshot_id: str, events: list[dict[str, Any]], facts: list[dict[str, Any]], created_at: str) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "created_at": created_at,
        "event_count": len(events),
        "confirmed_fact_count": len(facts),
        "event_action_counts": dict(sorted(Counter(str(event.get("action") or "") for event in events).items())),
        "artifact_refs": architecture_intent_governance_artifact_refs(codebase_id),
    }


def _stable_id(prefix: str, *parts: Any) -> str:
    raw = "\x1f".join(str(part) for part in parts)
    return f"{prefix}_{hashlib.sha256(raw.encode('utf-8')).hexdigest()[:16]}"
