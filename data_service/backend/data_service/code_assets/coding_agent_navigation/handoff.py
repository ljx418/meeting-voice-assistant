"""Build V2.35 coding-agent handoff payloads."""

from __future__ import annotations

import hashlib
from typing import Any

from data_service.mcp_common import now

from .impact_persistence import impact_artifact_refs
from .reading_pack_persistence import reading_pack_artifact_refs


SCHEMA_VERSION = "v2.35"
SUPPORTED_AGENTS = {"copilot", "codex", "claude_code", "generic"}


def stable_id(prefix: str, *parts: Any) -> str:
    body = "\n".join(str(part) for part in parts if part is not None)
    return f"{prefix}_{hashlib.sha256(body.encode('utf-8')).hexdigest()[:16]}"


def build_handoff_payload(
    *,
    workspace_id: str,
    codebase_id: str,
    target_agent: str,
    reading_pack: dict[str, Any],
    token_ledger: dict[str, Any],
    impact: dict[str, Any],
    test_selection: dict[str, Any],
) -> dict[str, Any]:
    normalized_agent = target_agent if target_agent in SUPPORTED_AGENTS else "generic"
    task_id = str(reading_pack.get("task_id") or impact.get("task_id") or "")
    snapshot_id = str(reading_pack.get("snapshot_id") or impact.get("snapshot_id") or "")
    pack_id = str(reading_pack.get("pack_id") or "")
    handoff_id = stable_id("handoff", codebase_id, snapshot_id, task_id, pack_id, normalized_agent)
    impact_refs = impact_artifact_refs(codebase_id, task_id) if task_id else []
    reading_refs = reading_pack_artifact_refs(codebase_id, pack_id) if pack_id else []
    evidence_refs = sorted(
        set(
            list(reading_pack.get("evidence_refs") or [])
            + list(impact.get("evidence_refs") or [])
            + [ref for item in test_selection.get("suggested_tests") or [] for ref in list(item.get("evidence_refs") or [])]
        )
    )
    recommended_commands = _recommended_commands(test_selection, evidence_refs)
    guardrails = _guardrails(reading_pack, impact)
    acceptance_checks = _acceptance_checks(test_selection, evidence_refs)
    for row in recommended_commands + guardrails + acceptance_checks:
        if not row.get("evidence_refs"):
            row.setdefault("needs_review", []).append("handoff item has no retained evidence")
    refs = reading_refs + impact_refs + [{"type": "agent_handoff", "artifact_ref": f"coding-agent://{codebase_id}/task_navigation/handoff/{handoff_id}.json"}]
    blockers = list(reading_pack.get("blockers") or []) + list(impact.get("blockers") or [])
    warnings = []
    if not evidence_refs:
        blocker = {
            "code": "HANDOFF_EVIDENCE_UNAVAILABLE",
            "message": "Handoff has no retained evidence refs; downstream agent must review reading pack and blockers before editing.",
            "retryable": False,
        }
        blockers.append(blocker)
        warnings.append("HANDOFF_EVIDENCE_UNAVAILABLE")
    return {
        "schema_version": SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "created_at": now(),
        "handoff_id": handoff_id,
        "task_id": task_id,
        "task": reading_pack.get("task"),
        "target_agent": normalized_agent,
        "reading_pack_ref": reading_refs[0]["artifact_ref"] if reading_refs else None,
        "impact_ref": impact_refs[0]["artifact_ref"] if impact_refs else None,
        "token_budget": {
            "max_tokens": token_ledger.get("max_tokens"),
            "included_tokens": token_ledger.get("included_tokens"),
            "omitted_tokens": token_ledger.get("omitted_tokens"),
            "omitted_count": len(token_ledger.get("omitted_items") or []),
        },
        "recommended_commands": recommended_commands,
        "guardrails": guardrails,
        "acceptance_checks": acceptance_checks,
        "evidence_refs": evidence_refs,
        "needs_review": sorted(set(list(reading_pack.get("needs_review") or []) + list(impact.get("needs_review") or []))),
        "blockers": blockers,
        "artifact_refs": refs,
        "warnings": warnings,
    }


def public_handoff_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return dict(payload)


def _recommended_commands(test_selection: dict[str, Any], evidence_refs: list[str]) -> list[dict[str, Any]]:
    commands = []
    tests = test_selection.get("suggested_tests") or []
    pytest_paths = [str(item.get("path") or "") for item in tests if str(item.get("path") or "").endswith(".py")]
    if pytest_paths:
        commands.append(
            {
                "command_id": "pytest_suggested",
                "command": "PYTHONPATH=backend /usr/bin/python3 -m pytest " + " ".join(pytest_paths[:8]) + " -q",
                "purpose": "Validate impacted Python tests selected from deterministic task impact.",
                "evidence_refs": evidence_refs[:5],
                "needs_review": [],
            }
        )
    commands.append(
        {
            "command_id": "git_diff_check",
            "command": "git diff --check -- <changed-files>",
            "purpose": "Check whitespace and patch formatting after edits.",
            "evidence_refs": [],
            "needs_review": ["changed files are not known until the downstream agent edits code"],
        }
    )
    return commands


def _guardrails(reading_pack: dict[str, Any], impact: dict[str, Any]) -> list[dict[str, Any]]:
    evidence = list(reading_pack.get("evidence_refs") or impact.get("evidence_refs") or [])[:5]
    return [
        {
            "guardrail_id": "read_required_first",
            "rule": "Read required_reads before editing.",
            "evidence_refs": evidence,
            "needs_review": [],
        },
        {
            "guardrail_id": "do_not_treat_heuristics_as_runtime",
            "rule": "Do not treat static relationship hints as runtime call graph evidence.",
            "evidence_refs": [],
            "needs_review": ["semantic limit must be checked in relationship artifacts"],
        },
        {
            "guardrail_id": "respect_blockers",
            "rule": "If blockers are present, keep the task in review until evidence improves.",
            "evidence_refs": [],
            "needs_review": ["blockers require downstream review"],
        },
    ]


def _acceptance_checks(test_selection: dict[str, Any], evidence_refs: list[str]) -> list[dict[str, Any]]:
    checks = [
        {
            "check_id": "run_suggested_tests",
            "description": "Run suggested tests or justify why they are not applicable.",
            "evidence_refs": evidence_refs[:5],
            "needs_review": [],
        },
        {
            "check_id": "update_public_contract_if_surface_changes",
            "description": "If public HTTP/MCP/CLI surface changes, update contract tests and public surface guard.",
            "evidence_refs": evidence_refs[:5],
            "needs_review": [],
        },
    ]
    if not test_selection.get("suggested_tests"):
        checks[0]["needs_review"].append("no suggested tests were selected")
    return checks
