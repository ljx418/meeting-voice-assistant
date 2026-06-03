"""Deterministic ranking for V2 agent context packs."""

from __future__ import annotations

from typing import Any


def keywords(text: str | None) -> set[str]:
    raw = (text or "").lower()
    tokens = []
    current = []
    for char in raw:
        if char.isalnum() or char in {"_", "-"}:
            current.append(char)
        elif current:
            tokens.append("".join(current))
            current = []
    if current:
        tokens.append("".join(current))
    return {token for token in tokens if len(token) >= 3}


def score_text(value: str | None, task_keywords: set[str]) -> int:
    haystack = (value or "").lower()
    return sum(1 for token in task_keywords if token in haystack)


def rank_items(items: list[dict[str, Any]], *, task_keywords: set[str], focus_values: set[str] | None = None) -> list[dict[str, Any]]:
    focus_values = focus_values or set()

    def score(item: dict[str, Any]) -> tuple[int, int, int, str]:
        joined = " ".join(str(value) for value in item.values() if isinstance(value, (str, int, float)))
        focus_score = sum(1 for value in focus_values if value and value in joined)
        keyword_score = score_text(joined, task_keywords)
        evidence_score = len(item.get("evidence") or item.get("evidence_ids") or [])
        return (-focus_score, -keyword_score, -evidence_score, joined)

    return sorted(items, key=score)
