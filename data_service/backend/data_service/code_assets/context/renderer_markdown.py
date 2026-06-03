"""Markdown renderer for V2 agent context packs."""

from __future__ import annotations

from typing import Any


def render_markdown(pack: dict[str, Any]) -> str:
    lines = [
        "# Agent Context Pack",
        "",
        "## 1. Task Interpretation",
        _jsonish(pack.get("task_interpretation")),
        "",
        "## 2. Project Summary",
        str((pack.get("project_summary") or {}).get("project_one_liner") or ""),
        "",
        "## 3. Relevant Capabilities",
        *_bullets(pack.get("relevant_capabilities"), "capability_id"),
        "",
        "## 4. Relevant Public Surface",
        *_bullets(pack.get("relevant_public_surface"), "surface_id"),
        "",
        "## 5. Relevant Files",
        *_bullets(pack.get("relevant_files"), "path"),
        "",
        "## 6. Relevant Symbols",
        *_bullets(pack.get("relevant_symbols"), "qualified_name"),
        "",
        "## 7. Implementation Guidance",
        *_claim_bullets(pack.get("implementation_guidance")),
        "",
        "## 8. Risks and Compatibility Notes",
        *_claim_bullets(pack.get("risks")),
        "",
        "## 9. Suggested Tests",
        *_claim_bullets(pack.get("suggested_tests")),
        "",
        "## 10. Recommended Next Steps",
        *_claim_bullets(pack.get("recommended_next_steps")),
        "",
        "## 11. Evidence",
        *_evidence_bullets(pack.get("evidence")),
    ]
    if pack.get("omitted_items"):
        lines.extend(["", "## 12. Omitted Items", *_claim_bullets(pack.get("omitted_items"))])
    return "\n".join(lines).strip() + "\n"


def _bullets(items: Any, key: str) -> list[str]:
    rows = items if isinstance(items, list) else []
    if not rows:
        return ["- needs_review"]
    return [f"- `{item.get(key) or item.get('summary') or item}`" for item in rows[:20]]


def _claim_bullets(items: Any) -> list[str]:
    rows = items if isinstance(items, list) else []
    if not rows:
        return ["- needs_review"]
    result = []
    for item in rows[:20]:
        suffix = " (needs_review)" if item.get("needs_review") else ""
        result.append(f"- {item.get('summary') or item.get('risk_id') or item}{suffix}")
    return result


def _evidence_bullets(items: Any) -> list[str]:
    rows = items if isinstance(items, list) else []
    if not rows:
        return ["- needs_review"]
    result = []
    for item in rows[:40]:
        location = item.get("source_file") or item.get("artifact") or item.get("evidence_id")
        line = ""
        if item.get("start_line") and item.get("end_line"):
            line = f":{item.get('start_line')}-{item.get('end_line')}"
        result.append(f"- `{location}{line}`")
    return result


def _jsonish(value: Any) -> str:
    if isinstance(value, dict):
        return "\n".join(f"- `{key}`: {item}" for key, item in value.items())
    return str(value or "")
