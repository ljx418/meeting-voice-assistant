"""Build V2.34 module reading packs and token ledgers."""

from __future__ import annotations

import hashlib
from typing import Any

from data_service.mcp_common import now


SCHEMA_VERSION = "v2.34"


def stable_id(prefix: str, *parts: Any) -> str:
    body = "\n".join(str(part) for part in parts if part is not None)
    return f"{prefix}_{hashlib.sha256(body.encode('utf-8')).hexdigest()[:16]}"


def build_reading_pack_payload(
    *,
    workspace_id: str,
    codebase_id: str,
    task_query: dict[str, Any],
    impact: dict[str, Any],
    test_selection: dict[str, Any],
    max_tokens: int = 12000,
    role: str = "coding_agent",
) -> tuple[dict[str, Any], str, dict[str, Any]]:
    task_id = str(task_query.get("task_id") or impact.get("task_id") or stable_id("task", task_query.get("task")))
    snapshot_id = str(task_query.get("snapshot_id") or impact.get("snapshot_id") or "")
    candidates = []
    candidates.extend(_read_items(impact.get("impacted_surfaces") or [], "surface", priority=100))
    candidates.extend(_read_items(impact.get("impacted_symbols") or [], "symbol", priority=90))
    candidates.extend(_read_items(impact.get("impacted_files") or [], "file", priority=80))
    candidates.extend(_read_items(impact.get("impacted_tests") or [], "test", priority=75))
    candidates.extend(_read_items(impact.get("impacted_docs") or [], "doc", priority=60))
    candidates.extend(_test_items(test_selection.get("suggested_tests") or [], priority=70))
    candidates = _dedupe_reads(candidates)
    naive_tokens = sum(item["estimated_tokens"] for item in candidates)
    included, omitted = _apply_budget(candidates, max_tokens=max_tokens)
    required_reads = [item for item in included if item["priority"] >= 80]
    optional_reads = [item for item in included if item["priority"] < 80]
    skip_reads = [{"item_ref": item["item_ref"], "path": item.get("path"), "reason": item["omitted_reason"]} for item in omitted]
    recommended_next_steps = _next_steps(task_query, impact, test_selection)
    for step in recommended_next_steps:
        if not step.get("evidence_refs"):
            step.setdefault("needs_review", []).append("recommendation has no retained evidence")
    included_tokens = sum(item["estimated_tokens"] for item in included)
    omitted_tokens = sum(item["estimated_tokens"] for item in omitted)
    evidence_floor_tokens = min(included_tokens, max(200, int(max_tokens * 0.1))) if included else 0
    pack_id = stable_id("readpack", codebase_id, snapshot_id, task_id, role, max_tokens)
    cache_key = stable_id("readcache", codebase_id, snapshot_id, task_id, role, max_tokens, [item.get("item_ref") for item in included])
    ledger = {
        "schema_version": SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "pack_id": pack_id,
        "cache_key": cache_key,
        "task_id": task_id,
        "max_tokens": max_tokens,
        "estimated_tokens": naive_tokens,
        "included_tokens": included_tokens,
        "omitted_tokens": omitted_tokens,
        "evidence_floor_tokens": evidence_floor_tokens,
        "compression_ratio": round(included_tokens / naive_tokens, 4) if naive_tokens else 1.0,
        "omitted_items": [{"item_ref": item["item_ref"], "reason": item["omitted_reason"], "estimated_tokens": item["estimated_tokens"]} for item in omitted],
    }
    pack = {
        "schema_version": SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "created_at": now(),
        "pack_id": pack_id,
        "task_id": task_id,
        "task": task_query.get("task"),
        "role": role,
        "required_reads": required_reads,
        "optional_reads": optional_reads,
        "skip_reads": skip_reads,
        "reuse_patterns": _reuse_patterns(included),
        "recommended_next_steps": recommended_next_steps,
        "token_ledger": ledger,
        "source_artifact_refs": list(impact.get("source_artifact_refs") or []) + list(impact.get("artifact_refs") or []),
        "evidence_refs": sorted({ref for item in included for ref in list(item.get("evidence_refs") or [])}),
        "warnings": [],
        "needs_review": sorted({review for item in included for review in list(item.get("needs_review") or [])}),
        "blockers": list(impact.get("blockers") or []),
    }
    if included_tokens > max_tokens:
        blocker = {"code": "TOKEN_BUDGET_TOO_SMALL", "message": "Token budget is too small to include the minimum evidence floor.", "retryable": False}
        pack["blockers"].append(blocker)
        ledger.setdefault("blockers", []).append(blocker)
    markdown = render_reading_pack_markdown(pack)
    return pack, markdown, ledger


def render_reading_pack_markdown(pack: dict[str, Any]) -> str:
    ledger = pack.get("token_ledger") or {}
    lines = [
        f"# Module Reading Pack: {pack.get('task') or pack.get('task_id')}",
        "",
        f"- pack_id: `{pack.get('pack_id')}`",
        f"- task_id: `{pack.get('task_id')}`",
        f"- role: `{pack.get('role')}`",
        f"- token budget: {ledger.get('included_tokens', 0)} / {ledger.get('max_tokens', 0)}",
        f"- omitted tokens: {ledger.get('omitted_tokens', 0)}",
        "",
        "## Required Reads",
    ]
    lines.extend(_render_reads(pack.get("required_reads") or []))
    lines.extend(["", "## Optional Reads"])
    lines.extend(_render_reads(pack.get("optional_reads") or []))
    lines.extend(["", "## Recommended Next Steps"])
    for step in pack.get("recommended_next_steps") or []:
        suffix = " needs_review" if step.get("needs_review") else ""
        lines.append(f"- {step.get('action')}: {step.get('reason')}{suffix}")
    lines.extend(["", "## Omitted Items"])
    for item in ledger.get("omitted_items") or []:
        lines.append(f"- `{item.get('item_ref')}`: {item.get('reason')}")
    lines.extend(["", "## Blockers"])
    for blocker in pack.get("blockers") or []:
        lines.append(f"- {blocker.get('code')}: {blocker.get('message')}")
    return "\n".join(lines).strip() + "\n"


def public_reading_pack_payload(pack: dict[str, Any]) -> dict[str, Any]:
    return dict(pack)


def _read_items(items: list[dict[str, Any]], kind: str, *, priority: int) -> list[dict[str, Any]]:
    result = []
    for item in items:
        ref = item.get("impact_ref") or {}
        path = str(ref.get("path") or item.get("path") or "")
        ref_id = str(ref.get("ref_id") or item.get("relationship_id") or stable_id(kind, path))
        if not path and kind in {"file", "doc", "test"}:
            continue
        evidence_refs = list(item.get("evidence_refs") or [])
        needs_review = list(item.get("needs_review") or [])
        result.append(
            {
                "item_ref": stable_id("read", kind, ref_id, path),
                "read_type": kind,
                "ref_id": ref_id,
                "path": path,
                "reason": item.get("impact_type") or item.get("relationship_type") or "impact",
                "priority": priority + (10 if evidence_refs else 0),
                "estimated_tokens": _estimate_tokens(path, ref_id, item),
                "evidence_refs": evidence_refs,
                "needs_review": needs_review if needs_review or evidence_refs else ["read item has no direct evidence"],
            }
        )
    return result


def _test_items(items: list[dict[str, Any]], *, priority: int) -> list[dict[str, Any]]:
    result = []
    for item in items:
        path = str(item.get("path") or "")
        if not path:
            continue
        result.append(
            {
                "item_ref": stable_id("read", "test", item.get("test_ref"), path),
                "read_type": "test",
                "ref_id": item.get("test_ref"),
                "path": path,
                "reason": item.get("reason") or "suggested test",
                "priority": priority + (10 if item.get("evidence_refs") else 0),
                "estimated_tokens": _estimate_tokens(path, item.get("test_ref"), item),
                "evidence_refs": list(item.get("evidence_refs") or []),
                "needs_review": list(item.get("needs_review") or []),
            }
        )
    return result


def _apply_budget(items: list[dict[str, Any]], *, max_tokens: int) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    sorted_items = sorted(items, key=lambda item: (-int(item.get("priority") or 0), int(item.get("estimated_tokens") or 0), str(item.get("path") or "")))
    included = []
    omitted = []
    used = 0
    for item in sorted_items:
        cost = int(item["estimated_tokens"])
        if used + cost <= max_tokens or not included:
            included.append(item)
            used += cost
        else:
            copy = dict(item)
            copy["omitted_reason"] = "over_budget"
            omitted.append(copy)
    return included, omitted


def _dedupe_reads(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_key: dict[str, dict[str, Any]] = {}
    for item in items:
        key = str(item.get("path") or item.get("ref_id") or item.get("item_ref"))
        existing = by_key.get(key)
        if not existing or int(item.get("priority") or 0) > int(existing.get("priority") or 0):
            by_key[key] = item
        elif existing:
            existing["needs_review"] = sorted(set(list(existing.get("needs_review") or []) + ["duplicate merged"]))
    return list(by_key.values())


def _estimate_tokens(*values: Any) -> int:
    chars = sum(len(str(value)) for value in values if value is not None)
    return max(80, int(chars / 4) + 40)


def _next_steps(task_query: dict[str, Any], impact: dict[str, Any], test_selection: dict[str, Any]) -> list[dict[str, Any]]:
    evidence = list(impact.get("evidence_refs") or test_selection.get("evidence_refs") or [])[:5]
    return [
        {"action": "read_required_files", "reason": "Start from required_reads before editing.", "evidence_refs": evidence, "needs_review": []},
        {"action": "inspect_suggested_tests", "reason": "Use suggested_tests to choose validation scope.", "evidence_refs": evidence, "needs_review": []},
        {"action": "respect_blockers", "reason": "Do not treat blockers as accepted runtime facts.", "evidence_refs": [], "needs_review": ["blocker handling requires human or later-phase review"]},
    ]


def _reuse_patterns(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    patterns = []
    for item in items[:10]:
        if item.get("read_type") in {"surface", "symbol", "test"}:
            patterns.append({"pattern_id": stable_id("reuse", item.get("item_ref")), "source_ref": item.get("ref_id"), "path": item.get("path"), "reason": item.get("reason"), "evidence_refs": item.get("evidence_refs", []), "needs_review": item.get("needs_review", [])})
    return patterns[:10]


def _render_reads(items: list[dict[str, Any]]) -> list[str]:
    if not items:
        return ["- none"]
    return [f"- `{item.get('path') or item.get('ref_id')}` ({item.get('read_type')}): {item.get('reason')}" for item in items[:50]]
