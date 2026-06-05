"""V2.6 large-project architecture view rendering."""

from __future__ import annotations

import html
import re
from collections import Counter
from typing import Any


HTML_VIEW_ID = "architecture_large_project_overview.html"
MERMAID_VIEW_ID = "architecture_key_boundaries.mmd"


def render_large_project_html(payload: dict[str, Any]) -> str:
    scale = payload.get("scale_profile") or {}
    inventory = payload.get("inventory") or {}
    taxonomy = payload.get("taxonomy") or {}
    review = payload.get("review_queue") or {}
    code_arch = payload.get("code_architecture") or {}
    role_counts = Counter(item.get("role_type") for item in code_arch.get("roles", []))
    boundary_counts = Counter(item.get("boundary_type") for item in code_arch.get("boundaries", []))
    pattern_counts = Counter(item.get("pattern_type") for item in code_arch.get("patterns", []))
    review_summary = review.get("summary") or {}
    refs = payload.get("artifact_refs") or []
    return f"""<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><title>V2.6 Large Project Architecture Overview</title>
<style>body{{font-family:-apple-system,BlinkMacSystemFont,Segoe UI,Arial,sans-serif;margin:24px;line-height:1.5;color:#17212b}}section{{border:1px solid #d9dee5;border-radius:8px;padding:18px;margin:14px 0}}table{{border-collapse:collapse;width:100%}}td,th{{border-bottom:1px solid #e5e7eb;padding:8px;text-align:left}}code{{background:#eef2f7;padding:2px 4px;border-radius:4px}}.grid{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px}}</style></head>
<body>
<h1>V2.6 Large Project Architecture Overview</h1>
<section><h2>Scale Profile</h2><p>files={int(scale.get('file_count') or 0)}, loc={int(scale.get('loc_total') or 0)}, summary_mode={bool(scale.get('summary_mode_required'))}, needs_review={int(scale.get('needs_review_count') or 0)}</p></section>
<div class="grid">
<section><h2>Language Facts</h2>{_counts_table((inventory.get('language_facts') or {}).get('counts'))}</section>
<section><h2>Config Inventory</h2>{_counts_table((inventory.get('config_inventory') or {}).get('counts'))}</section>
<section><h2>Deployment Inventory</h2>{_counts_table((inventory.get('deployment_inventory') or {}).get('counts'))}</section>
<section><h2>Schema Inventory</h2>{_counts_table((inventory.get('schema_inventory') or {}).get('counts'))}</section>
</div>
<div class="grid">
<section><h2>Roles</h2>{_counts_table(role_counts)}</section>
<section><h2>Boundaries</h2>{_counts_table(boundary_counts)}</section>
<section><h2>Patterns</h2>{_counts_table(pattern_counts)}</section>
<section><h2>Review Queue</h2>{_counts_table(review_summary.get('reason_counts'))}</section>
</div>
<section><h2>Taxonomy</h2><p>roles={_csv(taxonomy.get('role_types'))}</p></section>
<section><h2>Artifact Refs</h2><ul>{''.join(f'<li><code>{html.escape(str(ref.get("artifact_ref")))}</code></li>' for ref in refs)}</ul></section>
</body></html>"""


def render_key_boundaries_mermaid(payload: dict[str, Any]) -> tuple[str, set[str]]:
    code_arch = payload.get("code_architecture") or {}
    review = payload.get("review_queue") or {}
    roles = list(code_arch.get("roles") or [])[:30]
    boundaries = list(code_arch.get("boundaries") or [])[:30]
    patterns = list(code_arch.get("patterns") or [])[:20]
    review_items = list(review.get("review_queue") or [])[:20]
    lines = ["flowchart TD"]
    persisted_ids: set[str] = set()
    rendered_ids: set[str] = set()
    for role in roles:
        role_id = str(role.get("role_id") or "")
        if not role_id:
            continue
        persisted_ids.add(role_id)
        node_id = _safe_id(role_id)
        rendered_ids.add(node_id)
        lines.append(f"  {node_id}[\"role: {_label(role.get('role_type'), role.get('name'))}\"]")
    for boundary in boundaries:
        boundary_id = str(boundary.get("boundary_id") or "")
        if not boundary_id:
            continue
        persisted_ids.add(boundary_id)
        node_id = _safe_id(boundary_id)
        rendered_ids.add(node_id)
        lines.append(f"  {node_id}{{\"boundary: {_label(boundary.get('boundary_type'), boundary.get('name'))}\"}}")
        for member in (boundary.get("members") or [])[:8]:
            role_id = str(member.get("role_id") or "")
            if role_id:
                persisted_ids.add(role_id)
                lines.append(f"  {_safe_id(boundary_id)} --> {_safe_id(role_id)}")
    for pattern in patterns:
        pattern_id = str(pattern.get("pattern_id") or "")
        if not pattern_id:
            continue
        persisted_ids.add(pattern_id)
        node_id = _safe_id(pattern_id)
        rendered_ids.add(node_id)
        lines.append(f"  {node_id}((\"pattern: {_label(pattern.get('pattern_type'), pattern.get('name'))}\"))")
        for target in (pattern.get("targets") or [])[:5]:
            role_id = str(target.get("role_id") or "")
            if role_id:
                persisted_ids.add(role_id)
                lines.append(f"  {node_id} -. uses .-> {_safe_id(role_id)}")
    for item in review_items:
        review_id = str(item.get("review_id") or "")
        target_id = str(item.get("target_id") or "")
        if not review_id:
            continue
        persisted_ids.add(review_id)
        node_id = _safe_id(review_id)
        rendered_ids.add(node_id)
        lines.append(f"  {node_id}:::review[\"review: {_label(item.get('reason'), item.get('severity'))}\"]")
        if target_id:
            persisted_ids.add(target_id)
            lines.append(f"  {node_id} -. reviews .-> {_safe_id(target_id)}")
    lines.append("  classDef review fill:#fff7ed,stroke:#f97316,color:#7c2d12")
    return "\n".join(lines) + "\n", persisted_ids


def build_architecture_summary(payload: dict[str, Any]) -> dict[str, Any]:
    scale = payload.get("scale_profile") or {}
    inventory = payload.get("inventory") or {}
    review = payload.get("review_queue") or {}
    refs = payload.get("artifact_refs") or []
    review_summary = review.get("summary") or {}
    return {
        "schema_version": "v2.6",
        "summary": {
            "file_count": scale.get("file_count", 0),
            "loc_total": scale.get("loc_total", 0),
            "summary_mode_required": bool(scale.get("summary_mode_required")),
            "language_fact_count": (inventory.get("language_facts") or {}).get("total", 0),
            "config_count": (inventory.get("config_inventory") or {}).get("total", 0),
            "deployment_count": (inventory.get("deployment_inventory") or {}).get("total", 0),
            "schema_count": (inventory.get("schema_inventory") or {}).get("total", 0),
            "review_queue_count": review_summary.get("total", 0),
            "review_reason_counts": review_summary.get("reason_counts", {}),
        },
        "guidance": [
            {
                "summary": "Use V2.6 architecture artifacts as summary-first context for large projects.",
                "needs_review": False,
                "evidence": refs,
            },
            {
                "summary": "Review queue items must be checked before treating low-confidence architecture facts as accepted.",
                "needs_review": bool((review_summary.get("total") or 0) > 0),
                "evidence": refs,
            },
        ],
        "artifact_refs": refs,
        "needs_review": bool((review_summary.get("total") or 0) > 0),
    }


def _counts_table(counts: Any) -> str:
    if not isinstance(counts, dict) or not counts:
        return "<table><tbody><tr><td>none</td><td>0</td></tr></tbody></table>"
    rows = "".join(f"<tr><td>{html.escape(str(key))}</td><td>{int(value or 0)}</td></tr>" for key, value in sorted(counts.items()))
    return f"<table><tbody>{rows}</tbody></table>"


def _csv(values: Any) -> str:
    rows = values if isinstance(values, list) else []
    return ", ".join(html.escape(str(item)) for item in rows)


def _safe_id(value: str) -> str:
    return "A" + re.sub(r"[^A-Za-z0-9_]", "_", value)


def _label(kind: Any, name: Any) -> str:
    text = f"{kind or 'unknown'} {name or ''}".strip()
    return html.escape(text[:80])
