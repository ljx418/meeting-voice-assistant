"""V2.7 document-code architecture reconstruction views."""

from __future__ import annotations

import hashlib
import html
import re
from datetime import datetime, timezone
from typing import Any


HTML_VIEW_ID = "document_code_architecture_report.html"
MERMAID_VIEW_ID = "document_code_architecture_diff.mmd"
MAX_TARGET_NODES = 180
MAX_CURRENT_NODES = 180
MAX_DIFF_NODES = 220


def build_reconstructed_architecture_model(
    *,
    workspace_id: str,
    codebase_id: str,
    snapshot_id: str,
    documents: list[dict[str, Any]],
    claims: list[dict[str, Any]],
    relations: list[dict[str, Any]],
    quality_findings: list[dict[str, Any]],
    alignments: list[dict[str, Any]],
    drift: list[dict[str, Any]],
    code_architecture: dict[str, Any] | None = None,
    taxonomy: dict[str, Any] | None = None,
) -> dict[str, Any]:
    target_nodes = _target_nodes(claims)
    current_nodes = _current_nodes(alignments, drift, code_architecture or {})
    diff_nodes = _diff_nodes(drift, quality_findings)
    all_nodes = [*target_nodes, *current_nodes, *diff_nodes]
    edges = _edges(target_nodes, current_nodes, diff_nodes, alignments, drift, relations)
    model = {
        "schema_version": "v2.7",
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "model_id": _stable_id("reconstructed", codebase_id, snapshot_id),
        "sections": {
            "target_from_documents": [item["node_id"] for item in target_nodes],
            "current_from_code": [item["node_id"] for item in current_nodes],
            "gap_and_drift": [item["node_id"] for item in diff_nodes],
        },
        "target_nodes": target_nodes,
        "current_nodes": current_nodes,
        "diff_nodes": diff_nodes,
        "edges": edges,
        "summary": {
            "document_count": len(documents),
            "claim_count": len(claims),
            "relation_count": len(relations),
            "quality_finding_count": len(quality_findings),
            "alignment_count": len(alignments),
            "drift_count": len(drift),
            "target_node_count": len(target_nodes),
            "current_node_count": len(current_nodes),
            "diff_node_count": len(diff_nodes),
            "edge_count": len(edges),
            "target_truncated": len(claims) > MAX_TARGET_NODES,
            "current_truncated": _estimated_current_source_count(alignments, drift, code_architecture or {}) > MAX_CURRENT_NODES,
            "diff_truncated": len(drift) + len(quality_findings) > MAX_DIFF_NODES,
            "rendered_node_ids": [item["node_id"] for item in all_nodes],
            "source_kind_counts": _source_kind_counts(all_nodes),
            "taxonomy_version": (taxonomy or {}).get("schema_version"),
        },
        "source_artifact_refs": [
            {"type": "architecture_docs", "artifact_ref": f"architecture-docs://{codebase_id}/architecture_docs.jsonl"},
            {"type": "architecture_doc_claims", "artifact_ref": f"architecture-docs://{codebase_id}/architecture_doc_claims.jsonl"},
            {"type": "architecture_doc_quality_findings", "artifact_ref": f"architecture-docs://{codebase_id}/architecture_doc_quality_findings.jsonl"},
            {"type": "architecture_doc_code_alignment", "artifact_ref": f"architecture-docs://{codebase_id}/architecture_doc_code_alignment.jsonl"},
            {"type": "architecture_doc_code_drift_v2", "artifact_ref": f"architecture-docs://{codebase_id}/architecture_doc_code_drift_v2.jsonl"},
        ],
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    return _redact_model(model)


def render_reconstructed_architecture_html(model: dict[str, Any]) -> str:
    summary = model.get("summary", {})
    target = model.get("target_nodes", [])
    current = model.get("current_nodes", [])
    diff = model.get("diff_nodes", [])
    sections = [
        ("Target Architecture from Documents", target, "target"),
        ("Current Architecture from Code", current, "current"),
        ("Gaps and Drift", diff, "diff"),
    ]
    body: list[str] = [
        "<!doctype html>",
        '<html lang="en">',
        "<head>",
        '<meta charset="utf-8">',
        "<title>Document-Code Architecture Report</title>",
        "<style>",
        "body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;margin:24px;color:#17202a;background:#f7f8fa}",
        "main{max-width:1160px;margin:0 auto}",
        "section{background:white;border:1px solid #d7dde5;border-radius:8px;margin:16px 0;padding:16px}",
        ".grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px}",
        ".card{border:1px solid #e1e6ee;border-radius:6px;padding:10px;background:#fbfcfe}",
        ".meta{color:#5f6b7a;font-size:12px}",
        ".badge{display:inline-block;border-radius:12px;background:#edf2f7;padding:2px 8px;margin:2px;font-size:12px}",
        ".legend{display:flex;gap:10px;flex-wrap:wrap;margin:8px 0 12px}",
        ".legend span{display:inline-flex;align-items:center;gap:6px;color:#3f4b5b;font-size:12px}",
        ".dot{width:10px;height:10px;border-radius:50%;display:inline-block}",
        ".diagram-wrap{overflow:auto;border:1px solid #d7dde5;border-radius:8px;background:#fbfcfe;padding:10px}",
        ".diagram-title{font-size:13px;font-weight:600;fill:#17202a}",
        ".diagram-label{font-size:11px;fill:#17202a}",
        ".diagram-meta{font-size:10px;fill:#5f6b7a}",
        ".diagram-node{stroke:#24364b;stroke-width:1.2}",
        ".diagram-edge{stroke:#62748a;stroke-width:1.2;fill:none;marker-end:url(#arrow)}",
        ".diagram-edge.drift{stroke:#b54708;stroke-dasharray:5 4}",
        "</style>",
        "</head><body><main>",
        "<h1>Document-Code Architecture Report</h1>",
        f"<p class=\"meta\">workspace={_h(model.get('workspace_id'))} codebase={_h(model.get('codebase_id'))} snapshot={_h(model.get('snapshot_id'))}</p>",
        "<section><h2>Summary</h2><div class=\"grid\">",
    ]
    for key in ("document_count", "claim_count", "alignment_count", "drift_count", "target_node_count", "current_node_count", "diff_node_count", "edge_count"):
        body.append(f"<div class=\"card\"><strong>{_h(key)}</strong><br>{_h(summary.get(key, 0))}</div>")
    body.append("</div></section>")
    body.append(_relationship_overview_svg(model))
    for title, nodes, section_name in sections:
        body.append(f"<section data-section=\"{_h(section_name)}\"><h2>{_h(title)}</h2>")
        if not nodes:
            body.append("<p class=\"meta\">No persisted nodes for this section.</p>")
        else:
            body.append("<div class=\"grid\">")
            for node in nodes[:80]:
                body.append(_node_card(node))
            body.append("</div>")
            if len(nodes) > 80:
                body.append(f"<p class=\"meta\">Rendered first 80 of {_h(len(nodes))} persisted nodes.</p>")
        body.append("</section>")
    body.extend(["</main></body></html>"])
    return "\n".join(body)


def _relationship_overview_svg(model: dict[str, Any]) -> str:
    target_nodes = _select_overview_nodes(model.get("target_nodes", []), limit=7)
    current_nodes = _select_overview_nodes(model.get("current_nodes", []), limit=7)
    diff_nodes = _select_overview_nodes(model.get("diff_nodes", []), limit=7)
    selected = [*target_nodes, *current_nodes, *diff_nodes]
    selected_ids = {str(item.get("node_id")) for item in selected}
    if not selected:
        return (
            '<section data-section="relationship_overview">'
            "<h2>Architecture Relationship Overview</h2>"
            '<p class="meta">No persisted nodes are available for an overview diagram.</p>'
            "</section>"
        )

    positions: dict[str, tuple[int, int]] = {}
    rows = max(len(target_nodes), len(current_nodes), len(diff_nodes), 1)
    height = max(360, 84 + rows * 58)
    columns = [
        ("Target Architecture from Documents", target_nodes, 170, "#dbeafe"),
        ("Current Architecture from Code", current_nodes, 520, "#dcfce7"),
        ("Gaps and Drift", diff_nodes, 870, "#ffedd5"),
    ]
    svg: list[str] = [
        '<section data-section="relationship_overview">',
        "<h2>Architecture Relationship Overview</h2>",
        '<p class="meta">Key persisted nodes and relationships. Document-derived target facts, code-derived current facts, and drift findings are intentionally separated.</p>',
        '<div class="legend">',
        '<span><i class="dot" style="background:#dbeafe;border:1px solid #2563eb"></i>document target claim</span>',
        '<span><i class="dot" style="background:#dcfce7;border:1px solid #16a34a"></i>code fact</span>',
        '<span><i class="dot" style="background:#ffedd5;border:1px solid #ea580c"></i>gap / drift / quality finding</span>',
        "</div>",
        '<div class="diagram-wrap">',
        f'<svg role="img" aria-label="Architecture relationship overview" width="1080" height="{height}" viewBox="0 0 1080 {height}" xmlns="http://www.w3.org/2000/svg">',
        "<defs>",
        '<marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="3.5" orient="auto"><path d="M0,0 L8,3.5 L0,7 Z" fill="#62748a"/></marker>',
        "</defs>",
    ]
    for title, nodes, x, fill in columns:
        svg.append(f'<text class="diagram-title" x="{x - 118}" y="26">{_h(title)}</text>')
        for index, node in enumerate(nodes):
            y = 62 + index * 58
            positions[str(node.get("node_id"))] = (x, y)
            svg.append(
                f'<g data-node-id="{_h(node.get("node_id"))}">'
                f'<rect class="diagram-node" x="{x - 125}" y="{y - 20}" width="250" height="42" rx="7" fill="{fill}"/>'
                f'<text class="diagram-label" x="{x - 116}" y="{y - 3}">{_h(_truncate_label(str(node.get("label") or node.get("node_id")), 34))}</text>'
                f'<text class="diagram-meta" x="{x - 116}" y="{y + 13}">{_h(str(node.get("node_type") or "node"))} | confidence={_h(node.get("confidence"))}</text>'
                "</g>"
            )
    rendered_edges = 0
    for edge in model.get("edges", []):
        source_id = str(edge.get("from_node_id"))
        target_id = str(edge.get("to_node_id"))
        if source_id not in selected_ids or target_id not in selected_ids:
            continue
        source = positions.get(source_id)
        target = positions.get(target_id)
        if not source or not target:
            continue
        edge_type = str(edge.get("edge_type") or "RELATES_TO")
        css = "diagram-edge drift" if "DRIFT" in edge_type or "QUALITY" in edge_type else "diagram-edge"
        x1 = source[0] + (128 if source[0] <= target[0] else -128)
        x2 = target[0] - (128 if source[0] <= target[0] else -128)
        y1 = source[1]
        y2 = target[1]
        mid_x = (x1 + x2) // 2
        svg.append(f'<path class="{css}" d="M{x1},{y1} C{mid_x},{y1} {mid_x},{y2} {x2},{y2}"/>')
        if rendered_edges < 18:
            svg.append(f'<text class="diagram-meta" x="{mid_x - 44}" y="{(y1 + y2) // 2 - 4}">{_h(_truncate_label(edge_type, 22))}</text>')
        rendered_edges += 1
        if rendered_edges >= 36:
            break
    svg.extend(
        [
            "</svg>",
            "</div>",
            f'<p class="meta">Rendered {len(selected)} key nodes and {rendered_edges} persisted relationships. Full model nodes remain available in the detailed sections below.</p>',
            "</section>",
        ]
    )
    return "\n".join(svg)


def render_reconstructed_architecture_mermaid(model: dict[str, Any]) -> str:
    nodes = [*model.get("target_nodes", []), *model.get("current_nodes", []), *model.get("diff_nodes", [])]
    node_lookup = {str(node.get("node_id")): node for node in nodes}
    rendered = nodes[:160]
    id_map = {str(node.get("node_id")): f"n{index}" for index, node in enumerate(rendered)}
    lines = ["flowchart LR"]
    for node in rendered:
        raw_id = str(node.get("node_id"))
        mermaid_id = id_map[raw_id]
        label = _mermaid_label(str(node.get("label") or raw_id))
        shape = _shape_for_section(str(node.get("section") or ""))
        lines.append(f"  {mermaid_id}{shape[0]}\"{label}\"{shape[1]}")
    for edge in model.get("edges", [])[:220]:
        source = id_map.get(str(edge.get("from_node_id")))
        target = id_map.get(str(edge.get("to_node_id")))
        if not source or not target:
            continue
        label = _mermaid_label(str(edge.get("edge_type") or "relates_to"))
        lines.append(f"  {source} -- \"{label}\" --> {target}")
    lines.append("%% persisted_node_ids")
    for raw_id, mermaid_id in id_map.items():
        if raw_id in node_lookup:
            lines.append(f"%% {mermaid_id}={_mermaid_label(raw_id)}")
    return "\n".join(lines) + "\n"


def public_reconstructed_architecture_payload(payload: dict[str, Any], artifact_refs: list[dict[str, Any]]) -> dict[str, Any]:
    target_nodes = payload.get("target_nodes", [])[:100]
    current_nodes = payload.get("current_nodes", [])[:100]
    diff_nodes = payload.get("diff_nodes", [])[:120]
    node_ids = {item["node_id"] for item in [*target_nodes, *current_nodes, *diff_nodes]}
    edges = [
        item
        for item in payload.get("edges", [])
        if item.get("from_node_id") in node_ids and item.get("to_node_id") in node_ids
    ][:160]
    summary = dict(payload.get("summary", {}))
    summary["rendered_node_ids"] = [item["node_id"] for item in [*target_nodes, *current_nodes, *diff_nodes]]
    return {
        "schema_version": payload.get("schema_version", "v2.7"),
        "workspace_id": payload.get("workspace_id"),
        "codebase_id": payload.get("codebase_id"),
        "snapshot_id": payload.get("snapshot_id"),
        "model_id": payload.get("model_id"),
        "sections": payload.get("sections", {}),
        "summary": summary,
        "target_nodes": target_nodes,
        "current_nodes": current_nodes,
        "diff_nodes": diff_nodes,
        "edges": edges,
        "source_artifact_refs": payload.get("source_artifact_refs", []),
        "artifact_refs": artifact_refs,
    }


def _target_nodes(claims: list[dict[str, Any]]) -> list[dict[str, Any]]:
    ordered = sorted(claims, key=lambda item: (_claim_priority(item), str(item.get("claim_id") or "")))
    nodes: list[dict[str, Any]] = []
    for claim in ordered[:MAX_TARGET_NODES]:
        claim_id = str(claim.get("claim_id") or _stable_id("claim", claim.get("label")))
        nodes.append(
            _node(
                node_id=f"target:{claim_id}",
                node_type=str(claim.get("claim_type") or "document_claim"),
                label=str(claim.get("label") or claim_id),
                section="target_from_documents",
                source_kind="document_claim",
                source_refs=[{"type": "architecture_doc_claim", "claim_id": claim_id, "doc_id": claim.get("doc_id"), "path": claim.get("repo_path") or claim.get("source_path")}],
                confidence=float(claim.get("confidence") or 0.5),
                needs_review=list(claim.get("needs_review") or []),
            )
        )
    return nodes


def _current_nodes(alignments: list[dict[str, Any]], drift: list[dict[str, Any]], code_architecture: dict[str, Any]) -> list[dict[str, Any]]:
    nodes: dict[str, dict[str, Any]] = {}
    for item in alignments:
        if item.get("status") != "matched":
            continue
        for ref in item.get("code_refs") or []:
            key = _code_ref_key(ref)
            if key not in nodes:
                nodes[key] = _node(
                    node_id=f"current:{_stable_id(key)}",
                    node_type=str(ref.get("type") or "code_fact"),
                    label=str(ref.get("label") or ref.get("path") or ref.get("symbol_id") or ref.get("surface_id") or key),
                    section="current_from_code",
                    source_kind="code_fact",
                    source_refs=[{"type": "code_ref", **{k: v for k, v in ref.items() if v is not None}}, {"type": "architecture_doc_code_alignment", "alignment_id": item.get("alignment_id")}],
                    confidence=float(item.get("confidence") or 0.8),
                    needs_review=[],
                )
            if len(nodes) >= MAX_CURRENT_NODES:
                break
        if len(nodes) >= MAX_CURRENT_NODES:
            break
    for item in drift:
        if item.get("drift_type") != "code_not_documented" or len(nodes) >= MAX_CURRENT_NODES:
            continue
        for ref in item.get("code_refs") or item.get("code_evidence") or []:
            key = _code_ref_key(ref)
            nodes.setdefault(
                key,
                _node(
                    node_id=f"current:{_stable_id(key)}",
                    node_type=str(ref.get("type") or "code_fact"),
                    label=str(ref.get("label") or ref.get("path") or ref.get("symbol_id") or ref.get("surface_id") or key),
                    section="current_from_code",
                    source_kind="code_fact",
                    source_refs=[{"type": "code_ref", **{k: v for k, v in ref.items() if v is not None}}, {"type": "architecture_doc_code_drift", "drift_id": item.get("drift_id")}],
                    confidence=float(item.get("confidence") or 0.7),
                    needs_review=["code_not_documented"],
                ),
            )
    for collection_name in ("roles", "layers", "boundaries", "patterns"):
        for item in code_architecture.get(collection_name, []) or []:
            if len(nodes) >= MAX_CURRENT_NODES:
                break
            key = str(item.get("role_id") or item.get("layer_id") or item.get("boundary_id") or item.get("pattern_id") or item.get("path") or "")
            if not key:
                continue
            nodes.setdefault(
                key,
                _node(
                    node_id=f"current:{_stable_id(collection_name, key)}",
                    node_type=collection_name.rstrip("s"),
                    label=str(item.get("label") or item.get("name") or item.get("path") or key),
                    section="current_from_code",
                    source_kind="code_fact",
                    source_refs=[{"type": f"code_architecture_{collection_name}", "id": key}],
                    confidence=float(item.get("confidence") or 0.65),
                    needs_review=list(item.get("needs_review") or []),
                ),
            )
    return list(nodes.values())[:MAX_CURRENT_NODES]


def _diff_nodes(drift: list[dict[str, Any]], quality_findings: list[dict[str, Any]]) -> list[dict[str, Any]]:
    nodes: list[dict[str, Any]] = []
    for item in drift[:MAX_DIFF_NODES]:
        drift_id = str(item.get("drift_id") or _stable_id("drift", item.get("target_id"), item.get("drift_type")))
        nodes.append(
            _node(
                node_id=f"diff:{drift_id}",
                node_type=str(item.get("drift_type") or "drift"),
                label=str(item.get("message") or item.get("drift_type") or drift_id),
                section="gap_and_drift",
                source_kind="alignment",
                source_refs=[{"type": "architecture_doc_code_drift", "drift_id": drift_id, "target_id": item.get("target_id")}],
                confidence=float(item.get("confidence") or 0.6),
                needs_review=list(item.get("needs_review") or ["review_required"]),
            )
        )
    remaining = MAX_DIFF_NODES - len(nodes)
    for item in quality_findings[: max(0, remaining)]:
        finding_id = str(item.get("finding_id") or _stable_id("finding", item.get("target_id"), item.get("finding_type")))
        nodes.append(
            _node(
                node_id=f"diff:{finding_id}",
                node_type=str(item.get("finding_type") or "quality_finding"),
                label=str(item.get("message") or item.get("finding_type") or finding_id),
                section="gap_and_drift",
                source_kind="quality_finding",
                source_refs=[{"type": "architecture_doc_quality_finding", "finding_id": finding_id, "target_id": item.get("target_id")}],
                confidence=float(item.get("confidence") or 0.6),
                needs_review=list(item.get("needs_review") or ["review_required"]),
            )
        )
    return nodes


def _edges(target_nodes: list[dict[str, Any]], current_nodes: list[dict[str, Any]], diff_nodes: list[dict[str, Any]], alignments: list[dict[str, Any]], drift: list[dict[str, Any]], relations: list[dict[str, Any]]) -> list[dict[str, Any]]:
    target_by_claim = {str(ref.get("claim_id")): node["node_id"] for node in target_nodes for ref in node.get("source_refs", []) if ref.get("claim_id")}
    current_by_key = {}
    for node in current_nodes:
        for ref in node.get("source_refs", []):
            if ref.get("type") == "code_ref":
                current_by_key[_code_ref_key(ref)] = node["node_id"]
    diff_by_id = {}
    for node in diff_nodes:
        for ref in node.get("source_refs", []):
            if ref.get("drift_id"):
                diff_by_id[str(ref["drift_id"])] = node["node_id"]
            if ref.get("finding_id"):
                diff_by_id[str(ref["finding_id"])] = node["node_id"]
    edges: list[dict[str, Any]] = []
    for item in alignments:
        if item.get("status") != "matched":
            continue
        source = target_by_claim.get(str(item.get("claim_id") or item.get("target_id") or ""))
        if not source:
            continue
        for ref in item.get("code_refs") or []:
            target = current_by_key.get(_code_ref_key(ref))
            if target:
                edges.append(_edge(source, target, "MATCHED_BY_CODE", item.get("alignment_id"), item.get("confidence", 0.8)))
    for item in drift:
        drift_id = str(item.get("drift_id") or "")
        diff_node = diff_by_id.get(drift_id)
        if not diff_node:
            continue
        claim_id = str(item.get("claim_id") or item.get("target_id") or "")
        source = target_by_claim.get(claim_id)
        if source:
            edges.append(_edge(source, diff_node, "HAS_DRIFT", drift_id, item.get("confidence", 0.6)))
        for ref in item.get("code_refs") or item.get("code_evidence") or []:
            current = current_by_key.get(_code_ref_key(ref))
            if current:
                edges.append(_edge(current, diff_node, "HAS_DRIFT", drift_id, item.get("confidence", 0.6)))
    for relation in relations[:120]:
        source = target_by_claim.get(str(relation.get("from_claim_id") or ""))
        target = target_by_claim.get(str(relation.get("to_claim_id") or ""))
        if source and target:
            edges.append(_edge(source, target, str(relation.get("relation_type") or "DOCUMENT_RELATION"), relation.get("relation_id"), relation.get("confidence", 0.6)))
    seen: set[tuple[str, str, str]] = set()
    unique: list[dict[str, Any]] = []
    for edge in edges:
        key = (edge["from_node_id"], edge["to_node_id"], edge["edge_type"])
        if key not in seen:
            seen.add(key)
            unique.append(edge)
    return unique[:360]


def _node(*, node_id: str, node_type: str, label: str, section: str, source_kind: str, source_refs: list[dict[str, Any]], confidence: float, needs_review: list[Any]) -> dict[str, Any]:
    return {
        "node_id": _safe_node_id(node_id),
        "node_type": _redact_text(node_type),
        "label": _redact_text(label),
        "section": section,
        "source_kind": source_kind,
        "source_refs": _redact_model(source_refs),
        "confidence": round(max(0.0, min(1.0, confidence)), 3),
        "needs_review": [_redact_text(str(item)) for item in needs_review],
    }


def _edge(from_node_id: str, to_node_id: str, edge_type: str, evidence_id: Any, confidence: Any) -> dict[str, Any]:
    return {
        "edge_id": _stable_id("edge", from_node_id, to_node_id, edge_type, evidence_id),
        "from_node_id": from_node_id,
        "to_node_id": to_node_id,
        "edge_type": _redact_text(edge_type),
        "source_kind": "alignment" if edge_type in {"MATCHED_BY_CODE", "HAS_DRIFT"} else "document_claim",
        "source_refs": [{"type": "source_artifact", "id": evidence_id}] if evidence_id else [],
        "confidence": round(max(0.0, min(1.0, float(confidence or 0.6))), 3),
    }


def _node_card(node: dict[str, Any]) -> str:
    needs = "".join(f"<span class=\"badge\">{_h(item)}</span>" for item in node.get("needs_review", [])[:3])
    return (
        f"<div class=\"card\" data-node-id=\"{_h(node.get('node_id'))}\">"
        f"<strong>{_h(node.get('label'))}</strong>"
        f"<p class=\"meta\">{_h(node.get('node_type'))} | {_h(node.get('source_kind'))} | confidence={_h(node.get('confidence'))}</p>"
        f"{needs}"
        "</div>"
    )


def _select_overview_nodes(nodes: list[dict[str, Any]], *, limit: int) -> list[dict[str, Any]]:
    def score(node: dict[str, Any]) -> tuple[int, float, str]:
        needs_review = 1 if node.get("needs_review") else 0
        node_type = str(node.get("node_type") or "")
        priority = 0 if node_type in {"component", "layer", "plane", "public_interface", "adapter", "storage", "governance_boundary"} else 1
        if node.get("section") == "gap_and_drift":
            priority = 0 if needs_review else priority
        return (priority, -float(node.get("confidence") or 0.0), str(node.get("node_id") or ""))

    return sorted(nodes, key=score)[:limit]


def _truncate_label(value: str, limit: int) -> str:
    clean = " ".join(_redact_text(value).split())
    if len(clean) <= limit:
        return clean
    return clean[: max(0, limit - 1)].rstrip() + "…"


def _claim_priority(item: dict[str, Any]) -> tuple[int, int]:
    claim_type = str(item.get("claim_type") or "")
    block = str(item.get("source_block_type") or "")
    priority = 5
    if claim_type in {"component", "layer", "plane", "public_interface", "governance_boundary", "storage", "adapter"}:
        priority = 0
    elif block in {"heading", "interface_list", "table_row"}:
        priority = 1
    elif claim_type in {"acceptance_gate", "non_goal", "forbidden_claim"}:
        priority = 2
    return priority, 1 if item.get("needs_review") else 0


def _code_ref_key(ref: dict[str, Any]) -> str:
    return str(ref.get("surface_id") or ref.get("symbol_id") or ref.get("path") or ref.get("id") or ref.get("label") or ref)


def _safe_node_id(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9:_.-]+", "_", value)[:180]


def _stable_id(*parts: Any) -> str:
    return hashlib.sha256("|".join(str(part) for part in parts).encode("utf-8")).hexdigest()[:20]


def _h(value: Any) -> str:
    return html.escape(str(value), quote=True)


def _mermaid_label(value: str) -> str:
    clean = _redact_text(value).replace("\n", " ").replace("\r", " ")
    clean = clean.replace('"', "'").replace("[", "(").replace("]", ")").replace("{", "(").replace("}", ")")
    clean = clean.replace("<", "(").replace(">", ")")
    return clean[:90]


def _shape_for_section(section: str) -> tuple[str, str]:
    if section == "target_from_documents":
        return ("[", "]")
    if section == "current_from_code":
        return ("(", ")")
    return ("{{", "}}")


_ABS_PATH_RE = re.compile(r"(/Users/[^\\s\"'<>]+|/private/[^\\s\"'<>]+|/tmp/[^\\s\"'<>]+|/Volumes/[^\\s\"'<>]+)")


def _redact_text(value: str) -> str:
    return _ABS_PATH_RE.sub("[REDACTED_LOCAL_PATH]", value)


def _redact_model(value: Any) -> Any:
    if isinstance(value, str):
        return _redact_text(value)
    if isinstance(value, list):
        return [_redact_model(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _redact_model(item) for key, item in value.items()}
    return value


def _source_kind_counts(nodes: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for node in nodes:
        kind = str(node.get("source_kind") or "unknown")
        counts[kind] = counts.get(kind, 0) + 1
    return dict(sorted(counts.items()))


def _estimated_current_source_count(alignments: list[dict[str, Any]], drift: list[dict[str, Any]], code_architecture: dict[str, Any]) -> int:
    return sum(len(item.get("code_refs") or []) for item in alignments) + sum(len(item.get("code_refs") or item.get("code_evidence") or []) for item in drift) + sum(len(code_architecture.get(name, []) or []) for name in ("roles", "layers", "boundaries", "patterns"))
