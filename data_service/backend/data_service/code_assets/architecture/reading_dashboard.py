"""V2.8 human-readable architecture dashboard views."""

from __future__ import annotations

import hashlib
import html
import re
from datetime import datetime, timezone
from typing import Any


HTML_VIEW_ID = "architecture_reading_dashboard.html"
MERMAID_VIEW_ID = "architecture_relationship_summary.mmd"
REQUIRED_CHART_IDS = [
    "architecture_overview",
    "capability_map",
    "doc_code_drift_map",
    "quality_severity",
    "evidence_coverage",
    "hotspot_table",
]


def build_architecture_reading_dashboard(
    *,
    workspace_id: str,
    codebase_id: str,
    reconstructed_model: dict[str, Any],
    quality: dict[str, Any],
    alignment: dict[str, Any],
    artifact_refs: list[dict[str, Any]],
) -> dict[str, Any]:
    snapshot_id = str(reconstructed_model.get("snapshot_id") or "")
    nodes = [
        *reconstructed_model.get("target_nodes", []),
        *reconstructed_model.get("current_nodes", []),
        *reconstructed_model.get("diff_nodes", []),
    ]
    edges = reconstructed_model.get("edges", [])
    findings = quality.get("findings", [])
    alignments = alignment.get("alignments", [])
    drift = alignment.get("drift", [])
    chart_inputs = _chart_inputs(reconstructed_model, findings, alignments, drift)
    dashboard = {
        "schema_version": "v2.8",
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "dashboard_id": _stable_id("reading-dashboard", codebase_id, snapshot_id),
        "summary": {
            "target_node_count": len(reconstructed_model.get("target_nodes", [])),
            "current_node_count": len(reconstructed_model.get("current_nodes", [])),
            "diff_node_count": len(reconstructed_model.get("diff_nodes", [])),
            "edge_count": len(edges),
            "quality_finding_count": len(findings),
            "alignment_count": len(alignments),
            "drift_count": len(drift),
            "chart_count": len(REQUIRED_CHART_IDS),
            "hotspot_count": len(chart_inputs["hotspots"]),
            "view_ids": [HTML_VIEW_ID, MERMAID_VIEW_ID],
        },
        "first_screen": {
            "title": "Architecture Reading Dashboard",
            "one_liner": _one_liner(reconstructed_model, findings, drift),
            "navigation": [
                {"chart_id": chart_id, "label": _label(chart_id)}
                for chart_id in REQUIRED_CHART_IDS
            ],
        },
        "charts": chart_inputs["charts"],
        "hotspots": chart_inputs["hotspots"],
        "source_artifact_refs": reconstructed_model.get("source_artifact_refs", []),
        "artifact_refs": artifact_refs,
        "warnings": _warnings(reconstructed_model, findings, drift),
        "unresolved": _unresolved(reconstructed_model),
        "redaction": {"absolute_paths_redacted": True, "script_tags_escaped": True},
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    return _redact_payload(dashboard)


def render_architecture_reading_dashboard_html(dashboard: dict[str, Any]) -> str:
    summary = dashboard.get("summary", {})
    charts = {str(chart.get("chart_id")): chart for chart in dashboard.get("charts", [])}
    body = [
        "<!doctype html>",
        '<html lang="zh-CN">',
        "<head>",
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        "<title>Architecture Reading Dashboard</title>",
        "<style>",
        "body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;margin:0;color:#17202a;background:#f6f7f9}",
        "main{max-width:1240px;margin:0 auto;padding:24px}",
        ".hero{background:white;border-bottom:1px solid #d8dee7;padding:22px 24px}",
        ".meta{color:#5f6b7a;font-size:12px}",
        ".grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px}",
        ".card,.chart{background:white;border:1px solid #d8dee7;border-radius:8px;padding:14px}",
        ".chart{margin:14px 0}",
        ".bar{height:12px;border-radius:6px;background:#e8edf3;overflow:hidden}",
        ".bar span{display:block;height:100%;background:#2563eb}",
        ".row{display:grid;grid-template-columns:minmax(140px,1fr) 2fr 64px;gap:10px;align-items:center;margin:8px 0}",
        ".badge{display:inline-block;border-radius:12px;background:#eef2f7;padding:2px 8px;margin:2px;font-size:12px}",
        ".warn{background:#fff7ed;border-color:#fed7aa}",
        ".bad{background:#fef2f2;border-color:#fecaca}",
        "table{border-collapse:collapse;width:100%;font-size:13px}",
        "th,td{border-bottom:1px solid #e5eaf0;text-align:left;padding:8px;vertical-align:top}",
        "svg{max-width:100%;height:auto}",
        "</style>",
        "</head>",
        "<body>",
        '<header class="hero">',
        "<h1>Architecture Reading Dashboard</h1>",
        f"<p>{_h(dashboard.get('first_screen', {}).get('one_liner'))}</p>",
        f"<p class=\"meta\">workspace={_h(dashboard.get('workspace_id'))} codebase={_h(dashboard.get('codebase_id'))} snapshot={_h(dashboard.get('snapshot_id'))}</p>",
        "</header>",
        "<main>",
        '<section class="grid" aria-label="summary cards">',
    ]
    for key in ("target_node_count", "current_node_count", "diff_node_count", "edge_count", "quality_finding_count", "alignment_count", "drift_count", "hotspot_count"):
        body.append(f'<div class="card"><strong>{_h(key)}</strong><br>{_h(summary.get(key, 0))}</div>')
    body.append("</section>")
    body.append(_overview_chart(charts.get("architecture_overview", {})))
    body.append(_capability_chart(charts.get("capability_map", {})))
    body.append(_drift_chart(charts.get("doc_code_drift_map", {})))
    body.append(_quality_chart(charts.get("quality_severity", {})))
    body.append(_evidence_chart(charts.get("evidence_coverage", {})))
    body.append(_hotspot_table(dashboard.get("hotspots", [])))
    warnings = dashboard.get("warnings", [])
    unresolved = dashboard.get("unresolved", [])
    body.append('<section class="chart warn"><h2>Warnings and Unresolved</h2>')
    body.append(f'<p class="meta">warnings={_h(len(warnings))} unresolved={_h(len(unresolved))}</p>')
    for item in warnings[:8]:
        body.append(f'<span class="badge">{_h(item.get("code"))}: {_h(item.get("message"))}</span>')
    for item in unresolved[:8]:
        body.append(f'<span class="badge">{_h(item.get("reason"))}: {_h(item.get("node_id"))}</span>')
    body.append("</section>")
    body.extend(["</main>", "</body>", "</html>"])
    return "\n".join(body)


def render_architecture_relationship_summary_mermaid(dashboard: dict[str, Any]) -> str:
    overview = next((chart for chart in dashboard.get("charts", []) if chart.get("chart_id") == "architecture_overview"), {})
    values = overview.get("values", {})
    lines = ["flowchart LR"]
    node_labels = {
        "target": f"Target docs\\n{values.get('target_nodes', 0)}",
        "current": f"Current code\\n{values.get('current_nodes', 0)}",
        "diff": f"Drift\\n{values.get('diff_nodes', 0)}",
        "quality": f"Quality findings\\n{values.get('quality_findings', 0)}",
        "evidence": f"Evidence coverage\\n{_evidence_percent(dashboard)}%",
    }
    for node_id, label in node_labels.items():
        lines.append(f'  {node_id}["{_mermaid_label(label)}"]')
    lines.extend(
        [
            '  target -- "documents claims" --> current',
            '  current -- "code facts" --> diff',
            '  diff -- "needs review" --> quality',
            '  quality -- "trace" --> evidence',
            "%% persisted_dashboard_id",
            f"%% dashboard={_mermaid_label(str(dashboard.get('dashboard_id') or ''))}",
        ]
    )
    return "\n".join(lines) + "\n"


def public_architecture_reading_dashboard_payload(payload: dict[str, Any], artifact_refs: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "schema_version": payload.get("schema_version", "v2.8"),
        "workspace_id": payload.get("workspace_id"),
        "codebase_id": payload.get("codebase_id"),
        "snapshot_id": payload.get("snapshot_id"),
        "dashboard_id": payload.get("dashboard_id"),
        "summary": payload.get("summary", {}),
        "first_screen": payload.get("first_screen", {}),
        "charts": payload.get("charts", []),
        "hotspots": payload.get("hotspots", [])[:60],
        "source_artifact_refs": payload.get("source_artifact_refs", []),
        "warnings": payload.get("warnings", []),
        "unresolved": payload.get("unresolved", []),
        "redaction": payload.get("redaction", {}),
        "artifact_refs": artifact_refs,
    }


def _chart_inputs(reconstructed: dict[str, Any], findings: list[dict[str, Any]], alignments: list[dict[str, Any]], drift: list[dict[str, Any]]) -> dict[str, Any]:
    target = reconstructed.get("target_nodes", [])
    current = reconstructed.get("current_nodes", [])
    diff = reconstructed.get("diff_nodes", [])
    evidence_counts = {
        "with_source_refs": sum(1 for node in [*target, *current, *diff] if node.get("source_refs")),
        "without_source_refs": sum(1 for node in [*target, *current, *diff] if not node.get("source_refs")),
    }
    quality_counts: dict[str, int] = {}
    for finding in findings:
        severity = str(finding.get("severity") or "unknown")
        quality_counts[severity] = quality_counts.get(severity, 0) + 1
    drift_counts: dict[str, int] = {}
    for item in drift:
        kind = str(item.get("drift_type") or item.get("finding_type") or "drift")
        drift_counts[kind] = drift_counts.get(kind, 0) + 1
    capability_counts: dict[str, int] = {}
    for item in alignments:
        label = str(item.get("claim_type") or item.get("match_strategy") or item.get("status") or "alignment")
        capability_counts[label] = capability_counts.get(label, 0) + 1
    charts = [
        {"chart_id": "architecture_overview", "title": "Architecture Overview", "values": {"target_nodes": len(target), "current_nodes": len(current), "diff_nodes": len(diff), "edges": len(reconstructed.get("edges", [])), "quality_findings": len(findings)}},
        {"chart_id": "capability_map", "title": "Capability and Alignment Map", "values": _top_counts(capability_counts, limit=12)},
        {"chart_id": "doc_code_drift_map", "title": "Document-Code Drift Map", "values": _top_counts(drift_counts, limit=12)},
        {"chart_id": "quality_severity", "title": "Quality Severity", "values": _top_counts(quality_counts, limit=12)},
        {"chart_id": "evidence_coverage", "title": "Evidence Coverage", "values": evidence_counts},
        {"chart_id": "hotspot_table", "title": "Hotspots", "values": {"items": len(_hotspots(diff, findings, alignments))}},
    ]
    return {"charts": charts, "hotspots": _hotspots(diff, findings, alignments)}


def _hotspots(drift: list[dict[str, Any]], findings: list[dict[str, Any]], alignments: list[dict[str, Any]]) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for index, finding in enumerate(findings[:30]):
        items.append(
            {
                "hotspot_id": f"quality:{finding.get('finding_id') or index}",
                "kind": "quality_finding",
                "label": finding.get("message") or finding.get("finding_type") or "quality finding",
                "severity": finding.get("severity") or "unknown",
                "source_refs": finding.get("evidence") or finding.get("source_refs") or [],
                "needs_review": finding.get("needs_review") or [],
            }
        )
    for index, item in enumerate(drift[:30]):
        items.append(
            {
                "hotspot_id": f"drift:{item.get('drift_id') or index}",
                "kind": "doc_code_drift",
                "label": item.get("message") or item.get("drift_type") or "drift",
                "severity": item.get("severity") or "medium",
                "source_refs": item.get("evidence") or item.get("source_refs") or [],
                "needs_review": item.get("needs_review") or [],
            }
        )
    weak = [item for item in alignments if str(item.get("match_status") or item.get("status") or "").lower() in {"weak_match", "needs_review", "unmatched"}]
    for index, item in enumerate(weak[:20]):
        items.append(
            {
                "hotspot_id": f"alignment:{item.get('alignment_id') or index}",
                "kind": "weak_alignment",
                "label": item.get("claim_label") or item.get("matched_label") or item.get("match_strategy") or "weak alignment",
                "severity": "medium",
                "source_refs": item.get("evidence") or item.get("source_refs") or [],
                "needs_review": item.get("needs_review") or ["weak_or_unmatched_alignment"],
            }
        )
    return _redact_payload(items[:80])


def _overview_chart(chart: dict[str, Any]) -> str:
    values = chart.get("values", {})
    total = max(sum(int(values.get(key, 0)) for key in ("target_nodes", "current_nodes", "diff_nodes")), 1)
    rows = []
    for key, color in (("target_nodes", "#2563eb"), ("current_nodes", "#16a34a"), ("diff_nodes", "#ea580c")):
        value = int(values.get(key, 0))
        rows.append(_bar_row(key, value, total, color))
    return f'<section class="chart" id="architecture_overview"><h2>Architecture Overview</h2>{"".join(rows)}</section>'


def _capability_chart(chart: dict[str, Any]) -> str:
    return _count_chart("capability_map", "Capability and Alignment Map", chart.get("values", {}), "#4f46e5")


def _drift_chart(chart: dict[str, Any]) -> str:
    return _count_chart("doc_code_drift_map", "Document-Code Drift Map", chart.get("values", {}), "#ea580c")


def _quality_chart(chart: dict[str, Any]) -> str:
    return _count_chart("quality_severity", "Quality Severity", chart.get("values", {}), "#dc2626")


def _evidence_chart(chart: dict[str, Any]) -> str:
    values = chart.get("values", {})
    total = max(int(values.get("with_source_refs", 0)) + int(values.get("without_source_refs", 0)), 1)
    rows = [
        _bar_row("with_source_refs", int(values.get("with_source_refs", 0)), total, "#16a34a"),
        _bar_row("without_source_refs", int(values.get("without_source_refs", 0)), total, "#dc2626"),
    ]
    return f'<section class="chart" id="evidence_coverage"><h2>Evidence Coverage</h2>{"".join(rows)}</section>'


def _count_chart(chart_id: str, title: str, values: dict[str, int], color: str) -> str:
    total = max(sum(int(value) for value in values.values()), 1)
    rows = [_bar_row(key, int(value), total, color) for key, value in values.items()]
    if not rows:
        rows = ['<p class="meta">No values available.</p>']
    return f'<section class="chart" id="{_h(chart_id)}"><h2>{_h(title)}</h2>{"".join(rows)}</section>'


def _bar_row(label: str, value: int, total: int, color: str) -> str:
    pct = min(100, round((value / total) * 100, 2)) if total else 0
    return (
        '<div class="row">'
        f"<span>{_h(label)}</span>"
        f'<div class="bar"><span style="width:{pct}%;background:{_h(color)}"></span></div>'
        f"<strong>{_h(value)}</strong>"
        "</div>"
    )


def _hotspot_table(hotspots: list[dict[str, Any]]) -> str:
    rows = []
    for item in hotspots[:40]:
        css = "bad" if str(item.get("severity")).lower() in {"fatal", "major", "high"} else ""
        rows.append(
            f'<tr class="{css}"><td>{_h(item.get("kind"))}</td><td>{_h(item.get("severity"))}</td>'
            f'<td>{_h(item.get("label"))}</td><td>{_h(len(item.get("source_refs") or []))}</td><td>{_h(len(item.get("needs_review") or []))}</td></tr>'
        )
    if not rows:
        rows.append('<tr><td colspan="5" class="meta">No hotspots found.</td></tr>')
    return (
        '<section class="chart" id="hotspot_table"><h2>Hotspot Table</h2>'
        "<table><thead><tr><th>Kind</th><th>Severity</th><th>Label</th><th>Evidence</th><th>Needs Review</th></tr></thead>"
        f"<tbody>{''.join(rows)}</tbody></table></section>"
    )


def _one_liner(reconstructed: dict[str, Any], findings: list[dict[str, Any]], drift: list[dict[str, Any]]) -> str:
    summary = reconstructed.get("summary", {})
    return (
        f"目标文档节点 {summary.get('target_node_count', 0)} 个，代码当前节点 {summary.get('current_node_count', 0)} 个，"
        f"差异节点 {summary.get('diff_node_count', 0)} 个；当前质量发现 {len(findings)} 项，文档-代码 drift {len(drift)} 项。"
    )


def _warnings(reconstructed: dict[str, Any], findings: list[dict[str, Any]], drift: list[dict[str, Any]]) -> list[dict[str, str]]:
    warnings: list[dict[str, str]] = []
    if not reconstructed.get("target_nodes"):
        warnings.append({"code": "NO_TARGET_ARCHITECTURE_NODES", "message": "No target architecture document nodes are available."})
    if not reconstructed.get("current_nodes"):
        warnings.append({"code": "NO_CURRENT_CODE_NODES", "message": "No current architecture code nodes are available."})
    if findings:
        warnings.append({"code": "QUALITY_FINDINGS_PRESENT", "message": f"{len(findings)} document quality findings require review."})
    if drift:
        warnings.append({"code": "DOC_CODE_DRIFT_PRESENT", "message": f"{len(drift)} document-code drift items require review."})
    return warnings


def _unresolved(reconstructed: dict[str, Any]) -> list[dict[str, str]]:
    unresolved: list[dict[str, str]] = []
    for node in [*reconstructed.get("target_nodes", []), *reconstructed.get("current_nodes", []), *reconstructed.get("diff_nodes", [])]:
        if not node.get("source_refs"):
            unresolved.append({"node_id": str(node.get("node_id") or ""), "reason": "missing_source_refs"})
    return unresolved[:80]


def _evidence_percent(dashboard: dict[str, Any]) -> int:
    chart = next((item for item in dashboard.get("charts", []) if item.get("chart_id") == "evidence_coverage"), {})
    values = chart.get("values", {})
    with_refs = int(values.get("with_source_refs", 0))
    total = with_refs + int(values.get("without_source_refs", 0))
    return int((with_refs / total) * 100) if total else 0


def _top_counts(values: dict[str, int], *, limit: int) -> dict[str, int]:
    return dict(sorted(values.items(), key=lambda item: (-item[1], item[0]))[:limit])


def _label(chart_id: str) -> str:
    return chart_id.replace("_", " ").title()


def _stable_id(*parts: str) -> str:
    digest = hashlib.sha256(":".join(parts).encode("utf-8")).hexdigest()[:16]
    return f"v28_{digest}"


def _redact_payload(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _redact_payload(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_redact_payload(item) for item in value]
    if isinstance(value, str):
        text = re.sub(r"/Users/[^\\s\"'<>]+", "[REDACTED_PATH]", value)
        text = re.sub(r"/private/(tmp|var)/[^\\s\"'<>]+", "[REDACTED_PATH]", text)
        return text
    return value


def _h(value: Any) -> str:
    return html.escape(str(value), quote=True)


def _mermaid_label(value: str) -> str:
    safe = _redact_payload(value)
    safe = re.sub(r"[\[\]{}<>|`]", " ", str(safe))
    return safe.replace('"', "'")[:80]
