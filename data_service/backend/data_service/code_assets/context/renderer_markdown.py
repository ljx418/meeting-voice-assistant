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
        "## 3. Architecture Summary",
        *_architecture_summary(pack.get("architecture_summary")),
        "",
        "## 4. Relevant Capabilities",
        *_bullets(pack.get("relevant_capabilities"), "capability_id"),
        "",
        "## 5. Relevant Public Surface",
        *_bullets(pack.get("relevant_public_surface"), "surface_id"),
        "",
        "## 6. Relevant Files",
        *_bullets(pack.get("relevant_files"), "path"),
        "",
        "## 7. Relevant Symbols",
        *_bullets(pack.get("relevant_symbols"), "qualified_name"),
        "",
        "## 8. Implementation Guidance",
        *_claim_bullets(pack.get("implementation_guidance")),
        "",
        "## 9. Risks and Compatibility Notes",
        *_claim_bullets(pack.get("risks")),
        "",
        "## 10. Suggested Tests",
        *_claim_bullets(pack.get("suggested_tests")),
        "",
        "## 11. Recommended Next Steps",
        *_claim_bullets(pack.get("recommended_next_steps")),
        "",
        "## 12. Evidence",
        *_evidence_bullets(pack.get("evidence")),
    ]
    if pack.get("omitted_items"):
        lines.extend(["", "## 13. Omitted Items", *_claim_bullets(pack.get("omitted_items"))])
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


def _architecture_summary(value: Any) -> list[str]:
    if not isinstance(value, dict):
        return ["- needs_review"]
    summary = value.get("summary") if isinstance(value.get("summary"), dict) else {}
    rows = [
        f"- files={summary.get('file_count', 0)}, loc={summary.get('loc_total', 0)}, summary_mode={summary.get('summary_mode_required', False)}",
        f"- language_facts={summary.get('language_fact_count', 0)}, config={summary.get('config_count', 0)}, deployment={summary.get('deployment_count', 0)}, schema={summary.get('schema_count', 0)}",
        f"- review_queue={summary.get('review_queue_count', 0)}",
    ]
    if value.get("needs_review"):
        rows.append("- review queue requires human review before treating low-confidence facts as accepted")
    return rows


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
