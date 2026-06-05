"""Evidence-preserving token budget enforcement for V2 context packs."""

from __future__ import annotations

from typing import Any

from .model import token_estimate


TRUNCATABLE_LISTS = [
    "relevant_symbols",
    "relevant_public_surface",
    "relevant_files",
    "relevant_capabilities",
    "suggested_tests",
    "risks",
    "implementation_guidance",
    "recommended_next_steps",
    "evidence",
]

MIN_ITEMS = {
    "relevant_symbols": 1,
    "relevant_public_surface": 1,
    "relevant_files": 1,
    "relevant_capabilities": 1,
    "suggested_tests": 1,
    "risks": 1,
    "implementation_guidance": 1,
    "recommended_next_steps": 1,
    "evidence": 1,
}

MAX_OMITTED_ITEMS = 24


def apply_token_budget(pack: dict[str, Any], *, max_tokens: int) -> dict[str, Any]:
    budget = max(256, int(max_tokens or 16000))
    result = dict(pack)
    result["omitted_items"] = list(result.get("omitted_items") or [])
    while token_estimate(result) > budget:
        changed = False
        for key in TRUNCATABLE_LISTS:
            rows = list(result.get(key) or [])
            if len(rows) <= MIN_ITEMS.get(key, 0):
                continue
            omitted = rows.pop()
            result[key] = rows
            result["omitted_items"].append(
                {
                    "summary": f"Omitted one `{key}` item because max_tokens={budget}",
                    "item_ref": omitted.get("evidence_id") or omitted.get("symbol_id") or omitted.get("surface_id") or omitted.get("path") or omitted.get("summary"),
                    "reason": "TOKEN_BUDGET",
                    "needs_review": bool(omitted.get("needs_review")),
                    "evidence": [],
                }
            )
            changed = True
            if token_estimate(result) <= budget:
                break
        if token_estimate(result) <= budget:
            break
        if len(result.get("omitted_items") or []) > MAX_OMITTED_ITEMS:
            result["omitted_items"] = _compact_omitted_items(result["omitted_items"])
            changed = True
            if token_estimate(result) <= budget:
                break
        if not changed:
            architecture_summary = result.get("architecture_summary")
            if isinstance(architecture_summary, dict):
                result.pop("architecture_summary", None)
                result["omitted_items"].append(
                    {
                        "summary": f"Omitted architecture_summary because max_tokens={budget}",
                        "item_ref": "architecture_summary",
                        "reason": "TOKEN_BUDGET",
                        "needs_review": bool(architecture_summary.get("needs_review", True)),
                        "evidence": architecture_summary.get("artifact_refs", []),
                    }
                )
                if token_estimate(result) <= budget:
                    break
                changed = True
        if not changed:
            result["omitted_items"].append(
                {
                    "summary": "Token budget is too small to include all evidence-backed sections.",
                    "reason": "TOKEN_BUDGET_MINIMUM_REACHED",
                    "needs_review": True,
                    "evidence": [],
                }
            )
            break
    result["token_estimate"] = token_estimate(result)
    return result


def _compact_omitted_items(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if len(items) <= MAX_OMITTED_ITEMS:
        return items
    priority = [item for item in items if item.get("item_ref") == "architecture_summary"]
    keep = items[: MAX_OMITTED_ITEMS - 1]
    for item in priority:
        if item not in keep:
            keep.insert(0, item)
            keep = keep[: MAX_OMITTED_ITEMS - 1]
    omitted_count = len(items) - len(keep)
    keep.append(
        {
            "summary": f"Compacted {omitted_count} additional omitted items because of token budget.",
            "item_ref": "omitted_items.compacted",
            "reason": "TOKEN_BUDGET_COMPACTED",
            "needs_review": True,
            "evidence": [],
        }
    )
    return keep
