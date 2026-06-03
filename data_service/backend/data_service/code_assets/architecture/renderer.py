"""Architecture model renderers for V2.3."""

from __future__ import annotations

import html
import re
from collections import Counter
from typing import Any


def render_mermaid(model: dict[str, Any], alignment: dict[str, Any]) -> str:
    lines = ["flowchart TD"]
    nodes = model.get("design_nodes", [])[:80]
    node_ids = {item["node_id"] for item in nodes}
    for item in nodes:
        lines.append(f"  {safe_id(item['node_id'])}[\"{_label(item)}\"]")
    for edge in model.get("design_edges", [])[:120]:
        if edge.get("from_id") in node_ids and edge.get("to_id") in node_ids:
            lines.append(f"  {safe_id(edge['from_id'])} -->|{edge.get('relation')}| {safe_id(edge['to_id'])}")
    for match in alignment.get("matches", [])[:20]:
        if match.get("design_node_id") in node_ids:
            code_id = safe_id(str(match["code_node_id"]))
            lines.append(f"  {code_id}((\"{html.escape(str(match.get('code_node_type')))}\"))")
            lines.append(f"  {safe_id(match['design_node_id'])} -. mapped .-> {code_id}")
    return "\n".join(lines) + "\n"


def render_html(model: dict[str, Any], alignment: dict[str, Any], findings: list[dict[str, Any]]) -> str:
    summary = model.get("summary", {})
    node_counts = Counter(item.get("node_type") for item in model.get("design_nodes", []))
    finding_counts = Counter(item.get("finding_type") for item in findings)
    rows = "".join(f"<tr><td>{html.escape(str(k))}</td><td>{v}</td></tr>" for k, v in sorted(node_counts.items()))
    finding_rows = "".join(f"<tr><td>{html.escape(str(k))}</td><td>{v}</td></tr>" for k, v in sorted(finding_counts.items()))
    match_rows = "".join(
        f"<tr><td>{html.escape(str(m.get('design_label')))}</td><td>{html.escape(str(m.get('code_label')))}</td><td>{float(m.get('confidence') or 0):.2f}</td></tr>"
        for m in alignment.get("matches", [])[:50]
    )
    return f"""<!doctype html>
<html lang=\"zh-CN\"><head><meta charset=\"utf-8\"><title>Architecture Abstraction</title>
<style>body{{font-family:-apple-system,BlinkMacSystemFont,Segoe UI,Arial,sans-serif;margin:24px;line-height:1.5;color:#17212b}}section{{border:1px solid #d9dee5;border-radius:8px;padding:18px;margin:14px 0}}table{{border-collapse:collapse;width:100%}}td,th{{border-bottom:1px solid #e5e7eb;padding:8px;text-align:left}}code{{background:#eef2f7;padding:2px 4px;border-radius:4px}}</style></head>
<body><h1>V2.3 Architecture Abstraction</h1>
<section><h2>Summary</h2><p>sources={summary.get('source_count')}, design_nodes={summary.get('design_node_count')}, design_edges={summary.get('design_edge_count')}, matches={alignment.get('summary', {}).get('match_count')}, findings={len(findings)}</p></section>
<section><h2>Design Node Types</h2><table><tbody>{rows}</tbody></table></section>
<section><h2>Findings</h2><table><tbody>{finding_rows}</tbody></table></section>
<section><h2>Design-Code Matches</h2><table><thead><tr><th>Design</th><th>Code</th><th>Confidence</th></tr></thead><tbody>{match_rows}</tbody></table></section>
</body></html>"""


def render_code_architecture_mermaid(code_model: dict[str, Any], drift: list[dict[str, Any]]) -> str:
    lines = ["flowchart TD"]
    layers = code_model.get("layers", [])[:20]
    patterns = code_model.get("patterns", [])[:40]
    roles = code_model.get("roles", [])[:80]
    for layer in layers:
        lines.append(f"  {safe_id(str(layer.get('layer_id')))}[\"Layer: {html.escape(str(layer.get('layer_type')))}\"]")
    for role in roles:
        role_id = safe_id(str(role.get("role_id")))
        lines.append(f"  {role_id}[\"{html.escape(str(role.get('role_type')))}: {html.escape(str(role.get('name'))[:50])}\"]")
        layer_id = _role_layer_id(role, layers)
        if layer_id:
            lines.append(f"  {safe_id(layer_id)} --> {role_id}")
    for pattern in patterns:
        pattern_id = safe_id(str(pattern.get("pattern_id")))
        lines.append(f"  {pattern_id}((\"Pattern: {html.escape(str(pattern.get('pattern_type')))}\"))")
        for target in (pattern.get("targets") or [])[:5]:
            if target.get("role_id"):
                lines.append(f"  {pattern_id} -. uses .-> {safe_id(str(target['role_id']))}")
    for finding in drift[:30]:
        finding_id = safe_id(str(finding.get("finding_id")))
        lines.append(f"  {finding_id}{{\"{html.escape(str(finding.get('finding_type')))}\"}}")
        code_ref = finding.get("code_ref") or {}
        if code_ref.get("id"):
            lines.append(f"  {finding_id} -. drift .-> {safe_id(str(code_ref['id']))}")
    return "\n".join(lines) + "\n"


def render_code_architecture_html(code_model: dict[str, Any], drift: list[dict[str, Any]]) -> str:
    summary = code_model.get("summary", {})
    role_counts = summary.get("role_counts", {})
    layer_counts = summary.get("layer_counts", {})
    pattern_counts = summary.get("pattern_counts", {})
    boundary_counts = summary.get("boundary_counts", {})
    drift_counts = Counter(item.get("finding_type") for item in drift)
    role_rows = _count_rows(role_counts)
    layer_rows = _count_rows(layer_counts)
    boundary_rows = _count_rows(boundary_counts)
    pattern_rows = _count_rows(pattern_counts)
    drift_rows = _count_rows(drift_counts)
    return f"""<!doctype html>
<html lang=\"zh-CN\"><head><meta charset=\"utf-8\"><title>Code-Derived Architecture</title>
<style>body{{font-family:-apple-system,BlinkMacSystemFont,Segoe UI,Arial,sans-serif;margin:24px;line-height:1.5;color:#17212b}}section{{border:1px solid #d9dee5;border-radius:8px;padding:18px;margin:14px 0}}table{{border-collapse:collapse;width:100%}}td,th{{border-bottom:1px solid #e5e7eb;padding:8px;text-align:left}}.grid{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px}}</style></head>
<body><h1>V2.4 Code-Derived Architecture</h1>
<section><h2>Summary</h2><p>roles={summary.get('role_count')}, layers={summary.get('layer_count')}, boundaries={summary.get('boundary_count')}, patterns={summary.get('pattern_count')}, drift={summary.get('drift_count')}, needs_review={summary.get('needs_review_count')}</p></section>
<div class=\"grid\">
<section><h2>Roles</h2><table><tbody>{role_rows}</tbody></table></section>
<section><h2>Layers</h2><table><tbody>{layer_rows}</tbody></table></section>
<section><h2>Boundaries</h2><table><tbody>{boundary_rows}</tbody></table></section>
<section><h2>Patterns</h2><table><tbody>{pattern_rows}</tbody></table></section>
</div>
<section><h2>Design-Code Drift</h2><table><tbody>{drift_rows}</tbody></table></section>
</body></html>"""


def safe_id(value: str) -> str:
    return "A" + re.sub(r"[^A-Za-z0-9_]", "_", value)


def _label(item: dict[str, Any]) -> str:
    return html.escape(f"{item.get('node_type')}: {item.get('label')}"[:90])


def _role_layer_id(role: dict[str, Any], layers: list[dict[str, Any]]) -> str | None:
    role_id = role.get("role_id")
    for layer in layers:
        for member in layer.get("members") or []:
            if member.get("role_id") == role_id:
                return str(layer.get("layer_id"))
    return None


def _count_rows(counts: Any) -> str:
    if not isinstance(counts, dict) or not counts:
        return "<tr><td>none</td><td>0</td></tr>"
    return "".join(f"<tr><td>{html.escape(str(k))}</td><td>{v}</td></tr>" for k, v in sorted(counts.items()))
