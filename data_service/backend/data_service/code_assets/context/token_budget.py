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
]


def apply_token_budget(pack: dict[str, Any], *, max_tokens: int) -> dict[str, Any]:
    budget = max(256, int(max_tokens or 16000))
    result = dict(pack)
    result["omitted_items"] = list(result.get("omitted_items") or [])
    while token_estimate(result) > budget:
        changed = False
        for key in TRUNCATABLE_LISTS:
            rows = list(result.get(key) or [])
            if len(rows) <= 1:
                continue
            omitted = rows.pop()
            result[key] = rows
            result["omitted_items"].append(
                {
                    "summary": f"Omitted one `{key}` item because max_tokens={budget}",
                    "item_ref": omitted.get("symbol_id") or omitted.get("surface_id") or omitted.get("path") or omitted.get("summary"),
                    "reason": "TOKEN_BUDGET",
                    "needs_review": bool(omitted.get("needs_review")),
                    "evidence": omitted.get("evidence", []),
                }
            )
            changed = True
            if token_estimate(result) <= budget:
                break
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
