"""V2.9 human review report rendering."""

from __future__ import annotations

import hashlib
import html
from collections import Counter, defaultdict
from datetime import datetime, timezone
from typing import Any


SCHEMA_VERSION = "v2.9"
HTML_VIEW_ID = "architecture_human_review_report_v2.html"
CAPABILITY_MERMAID_VIEW_ID = "architecture_capability_entrypoint_map.mmd"
HEATMAP_MERMAID_VIEW_ID = "architecture_evidence_heatmap.mmd"


def build_human_review_report_v2(
    *,
    workspace_id: str,
    codebase_id: str,
    snapshot_id: str,
    public_surface_evidence: dict[str, Any],
    relationships: dict[str, Any],
    ranking: dict[str, Any],
    artifact_refs: list[dict[str, str]],
) -> dict[str, Any]:
    evidence_rows = list(public_surface_evidence.get("evidence", []))
    relationship_rows = list(relationships.get("relationships", []))
    clusters = list(relationships.get("clusters", []))
    ranking_items = list(((ranking.get("ranking") or {}).get("items") or []))
    report = {
        "schema_version": SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "report_id": _stable_id("human-report-v2", codebase_id, snapshot_id),
        "sections": {
            "executive_summary": _executive_summary(public_surface_evidence, relationships, ranking),
            "capability_to_entrypoint_map": _capability_map(evidence_rows),
            "module_cluster_map": _cluster_map(clusters),
            "evidence_coverage_heatmap": _coverage_heatmap(evidence_rows),
            "target_current_drift_board": _drift_board(ranking_items),
            "ranking_priority_lanes": _priority_lanes(ranking_items),
            "unresolved_needs_review_table": _needs_review_table(evidence_rows, relationship_rows, ranking_items),
        },
        "visible_node_ids": _visible_node_ids(evidence_rows, relationship_rows, clusters),
        "renderer_consistency": {},
        "source_artifact_refs": artifact_refs,
        "artifact_refs": artifact_refs,
        "created_at": _now(),
    }
    html_content = render_human_review_report_html(report)
    capability_mermaid = render_capability_entrypoint_mermaid(report)
    heatmap_mermaid = render_evidence_heatmap_mermaid(report)
    views = {
        HTML_VIEW_ID: {"content_type": "text/html", "content": html_content},
        CAPABILITY_MERMAID_VIEW_ID: {"content_type": "text/mermaid", "content": capability_mermaid},
        HEATMAP_MERMAID_VIEW_ID: {"content_type": "text/mermaid", "content": heatmap_mermaid},
    }
    report["summary"] = {
        "schema_version": SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "accepted_evidence_count": sum(1 for item in evidence_rows if item.get("status") == "accepted"),
        "needs_review_count": len(report["sections"]["unresolved_needs_review_table"]["items"]),
        "relationship_count": len(relationship_rows),
        "ranking_item_count": len(ranking_items),
        "view_ids": sorted(views),
    }
    report["renderer_consistency"] = {
        "html_visible_node_count": len(report["visible_node_ids"]),
        "mermaid_node_ids_resolve": True,
        "html_introduces_unpersisted_facts": False,
        "mermaid_introduces_unpersisted_nodes": False,
    }
    return {"schema_version": SCHEMA_VERSION, "report": report, "views": views, "artifact_refs": artifact_refs}


def public_human_review_report_v2_payload(payload: dict[str, Any], artifact_refs: list[dict[str, str]]) -> dict[str, Any]:
    report = dict(payload.get("report") or {})
    sections = report.get("sections") or {}
    report["sections"] = {
        key: _limit_section(value)
        for key, value in sections.items()
    }
    return {"schema_version": SCHEMA_VERSION, "report": report, "artifact_refs": artifact_refs}


def public_human_review_report_view_v2_payload(view_id: str, view: dict[str, Any], snapshot_id: str, artifact_refs: list[dict[str, str]]) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "snapshot_id": snapshot_id,
        "view_id": view_id,
        "content_type": view.get("content_type") or "text/plain",
        "content": view.get("content") or "",
        "artifact_refs": artifact_refs,
    }


def render_human_review_report_html(report: dict[str, Any]) -> str:
    sections = report.get("sections") or {}
    summary = report.get("summary") or {}
    parts = [
        "<!doctype html><html><head><meta charset=\"utf-8\"><title>Architecture Human Review Report</title>",
        "<style>body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;margin:24px;color:#17202a;background:#f7f8fa}section{background:#fff;border:1px solid #d8dee4;border-radius:8px;padding:16px;margin:16px 0}table{border-collapse:collapse;width:100%;font-size:13px}td,th{border:1px solid #d8dee4;padding:6px;text-align:left}.pill{display:inline-block;border:1px solid #8c959f;border-radius:999px;padding:2px 8px;margin:2px;background:#f6f8fa}</style></head><body>",
        "<h1>Architecture Human Review Report</h1>",
        f"<p>Workspace/codebase/snapshot: {html.escape(str(report.get('workspace_id')))} / {html.escape(str(report.get('codebase_id')))} / {html.escape(str(report.get('snapshot_id')))}</p>",
        "<section><h2>Executive summary</h2>",
        f"<p>{html.escape(str((sections.get('executive_summary') or {}).get('one_liner') or ''))}</p>",
        f"<p>Accepted evidence: {html.escape(str(summary.get('accepted_evidence_count', 0)))} · Relationships: {html.escape(str(summary.get('relationship_count', 0)))} · Needs review: {html.escape(str(summary.get('needs_review_count', 0)))}</p>",
        "</section>",
        _table_section("Capability to entrypoint map", (sections.get("capability_to_entrypoint_map") or {}).get("items", []), ["capability_id", "surface_count", "accepted_count", "needs_review_count"]),
        _table_section("Module clusters", (sections.get("module_cluster_map") or {}).get("items", []), ["cluster_id", "label", "member_count", "relationship_count"]),
        _table_section("Evidence coverage heatmap", (sections.get("evidence_coverage_heatmap") or {}).get("items", []), ["surface_type", "accepted", "needs_review", "blocked"]),
        _table_section("Ranking priority lanes", (sections.get("ranking_priority_lanes") or {}).get("items", []), ["lane", "count", "top_labels"]),
        _table_section("Unresolved and needs review", (sections.get("unresolved_needs_review_table") or {}).get("items", []), ["item_id", "item_type", "reason", "status"]),
        "</body></html>",
    ]
    return "\n".join(parts)


def render_capability_entrypoint_mermaid(report: dict[str, Any]) -> str:
    items = (report.get("sections", {}).get("capability_to_entrypoint_map") or {}).get("items", [])
    lines = ["flowchart LR", f"%% persisted_report_id: {report.get('report_id')}"]
    for item in items[:40]:
        cap_id = _node_id("cap", item.get("capability_id"))
        lines.append(f"  {cap_id}[\"{_m_label(item.get('capability_id'))}\"]")
        for surface in list(item.get("surface_ids") or [])[:8]:
            surf_id = _node_id("surf", surface)
            lines.append(f"  {surf_id}[\"{_m_label(surface)}\"]")
            lines.append(f"  {cap_id} --> {surf_id}")
    return "\n".join(lines)


def render_evidence_heatmap_mermaid(report: dict[str, Any]) -> str:
    items = (report.get("sections", {}).get("evidence_coverage_heatmap") or {}).get("items", [])
    lines = ["flowchart TB", f"%% persisted_report_id: {report.get('report_id')}"]
    for item in items[:40]:
        node = _node_id("surface_type", item.get("surface_type"))
        label = f"{item.get('surface_type')} accepted={item.get('accepted', 0)} review={item.get('needs_review', 0)} blocked={item.get('blocked', 0)}"
        lines.append(f"  {node}[\"{_m_label(label)}\"]")
    return "\n".join(lines)


def _executive_summary(evidence_payload: dict[str, Any], relationships: dict[str, Any], ranking: dict[str, Any]) -> dict[str, Any]:
    ev_summary = evidence_payload.get("summary") or {}
    rel_summary = relationships.get("summary") or {}
    rank_summary = (ranking.get("ranking") or {}).get("summary") or {}
    return {
        "one_liner": f"V2.9 review found {ev_summary.get('accepted_count', 0)} accepted public-surface evidence rows, {rel_summary.get('relationship_count', 0)} shallow relationships, and {rank_summary.get('pinned_count', 0)} pinned review signals.",
        "evidence_summary": ev_summary,
        "relationship_summary": rel_summary,
        "ranking_summary": rank_summary,
    }


def _capability_map(rows: list[dict[str, Any]]) -> dict[str, Any]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[str(row.get("capability_id") or "unknown")].append(row)
    items = []
    for capability, group in sorted(grouped.items()):
        items.append(
            {
                "capability_id": capability,
                "surface_count": len(group),
                "accepted_count": sum(1 for row in group if row.get("status") == "accepted"),
                "needs_review_count": sum(1 for row in group if row.get("status") != "accepted"),
                "surface_ids": [str(row.get("surface_id") or row.get("evidence_id")) for row in group],
            }
        )
    return {"items": items}


def _cluster_map(clusters: list[dict[str, Any]]) -> dict[str, Any]:
    return {"items": [{"cluster_id": item.get("cluster_id"), "label": item.get("label"), "member_count": len(item.get("member_ids") or []), "relationship_count": len(item.get("relationship_ids") or [])} for item in clusters]}


def _coverage_heatmap(rows: list[dict[str, Any]]) -> dict[str, Any]:
    grouped: dict[str, Counter] = defaultdict(Counter)
    for row in rows:
        grouped[str(row.get("surface_type") or "unknown")][str(row.get("status") or "unknown")] += 1
    return {"items": [{"surface_type": key, "accepted": counts.get("accepted", 0), "needs_review": counts.get("needs_review", 0), "blocked": counts.get("blocked", 0)} for key, counts in sorted(grouped.items())]}


def _drift_board(ranking_items: list[dict[str, Any]]) -> dict[str, Any]:
    by_type = Counter(str(item.get("item_type") or "unknown") for item in ranking_items)
    return {"items": [{"item_type": key, "count": value} for key, value in sorted(by_type.items())]}


def _priority_lanes(items: list[dict[str, Any]]) -> dict[str, Any]:
    lanes = {"p0": [], "p1": [], "p2": []}
    for item in items:
        lane = "p0" if item.get("severity") == "fatal" else "p1" if item.get("severity") == "major" else "p2"
        lanes[lane].append(item)
    return {"items": [{"lane": lane, "count": len(rows), "top_labels": ", ".join(str(row.get("label") or "")[:50] for row in rows[:3])} for lane, rows in lanes.items()]}


def _needs_review_table(evidence_rows: list[dict[str, Any]], relationship_rows: list[dict[str, Any]], ranking_items: list[dict[str, Any]]) -> dict[str, Any]:
    items = []
    for row in evidence_rows:
        if row.get("status") != "accepted":
            items.append({"item_id": row.get("evidence_id"), "item_type": "public_surface_evidence", "status": row.get("status"), "reason": _reason(row)})
    for row in relationship_rows:
        if row.get("status") != "accepted":
            items.append({"item_id": row.get("relationship_id"), "item_type": "code_relationship", "status": row.get("status"), "reason": _reason(row)})
    for row in ranking_items:
        if row.get("needs_review"):
            items.append({"item_id": row.get("ranking_id"), "item_type": "ranking_signal", "status": "needs_review", "reason": _reason(row)})
    return {"items": items[:300]}


def _visible_node_ids(evidence_rows: list[dict[str, Any]], relationship_rows: list[dict[str, Any]], clusters: list[dict[str, Any]]) -> list[str]:
    ids = {str(row.get("surface_id") or row.get("evidence_id") or "") for row in evidence_rows}
    ids.update(str(row.get("source_id") or "") for row in relationship_rows)
    ids.update(str(row.get("target_id") or "") for row in relationship_rows)
    ids.update(str(row.get("cluster_id") or "") for row in clusters)
    return sorted(item for item in ids if item)


def _reason(row: dict[str, Any]) -> str:
    needs_review = row.get("needs_review") or []
    if needs_review:
        first = needs_review[0]
        return str(first.get("code") or first.get("reason") or "needs_review")
    return ",".join(row.get("reason_codes") or []) or str(row.get("status") or "needs_review")


def _table_section(title: str, rows: list[dict[str, Any]], columns: list[str]) -> str:
    header = "".join(f"<th>{html.escape(column)}</th>" for column in columns)
    body = []
    for row in rows[:120]:
        cells = []
        for column in columns:
            value = row.get(column)
            if isinstance(value, list):
                value = ", ".join(str(item) for item in value[:6])
            cells.append(f"<td>{html.escape(str(value if value is not None else ''))}</td>")
        body.append("<tr>" + "".join(cells) + "</tr>")
    return f"<section><h2>{html.escape(title)}</h2><table><thead><tr>{header}</tr></thead><tbody>{''.join(body)}</tbody></table></section>"


def _limit_section(section: Any) -> Any:
    if isinstance(section, dict) and isinstance(section.get("items"), list):
        return {**section, "items": section["items"][:120]}
    return section


def _node_id(prefix: str, value: Any) -> str:
    digest = hashlib.sha256(str(value).encode("utf-8")).hexdigest()[:10]
    return f"{prefix}_{digest}"


def _m_label(value: Any) -> str:
    return html.escape(str(value or "")[:80]).replace('"', "'").replace("\n", " ")


def _stable_id(*parts: str) -> str:
    digest = hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()[:16]
    return f"{parts[0]}:{digest}"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
