"""Human-readable V2.16 workbench view model."""

from __future__ import annotations

import hashlib
import html
from typing import Any

from data_service.mcp_common import now

from .persistence import workbench_v2_artifact_refs


SCHEMA_VERSION = "v2.16"


def build_workbench_v2_payload(
    *,
    workspace_id: str,
    codebase_id: str,
    snapshot_id: str,
    provider_registry: dict[str, Any],
    semantic_index: dict[str, Any],
    runtime_profiles: dict[str, Any],
    workbench: dict[str, Any],
) -> dict[str, Any]:
    provider_nodes = [
        {"node_id": _node_id("provider", provider["provider_id"]), "kind": "provider", "label": provider["provider_id"], "status": provider.get("status")}
        for provider in provider_registry.get("providers", [])
    ]
    section_ids = ["provider_matrix", "semantic_coverage", "runtime_profiles", "risk_lanes", "blocker_board"]
    blockers = _blockers(provider_registry, semantic_index, runtime_profiles, workbench)
    risk_lanes = list(workbench.get("risk_lanes") or [])[:50]
    nodes = provider_nodes + [
        {"node_id": "section_provider_matrix", "kind": "section", "label": "Provider Matrix"},
        {"node_id": "section_semantic_coverage", "kind": "section", "label": "Semantic Coverage"},
        {"node_id": "section_runtime_profiles", "kind": "section", "label": "Runtime Profiles"},
        {"node_id": "section_blocker_board", "kind": "section", "label": "Blocker Board"},
    ]
    payload = {
        "schema_version": SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "workbench_id": _stable_id("workbenchv2", codebase_id, snapshot_id, len(provider_nodes), len(blockers), len(risk_lanes)),
        "source_phase": "V2.16 Phase 79",
        "summary": {
            "provider_count": provider_registry.get("summary", {}).get("provider_count", 0),
            "available_provider_count": provider_registry.get("summary", {}).get("available_count", 0),
            "semantic_fact_count": semantic_index.get("index", {}).get("summary", {}).get("provider_fact_count", 0),
            "runtime_profile_count": runtime_profiles.get("summary", {}).get("profile_count", 0),
            "risk_lane_count": len(risk_lanes),
            "blocker_count": len(blockers),
        },
        "sections": [
            {"section_id": section_id, "title": section_id.replace("_", " ").title(), "visible": True}
            for section_id in section_ids
        ],
        "provider_matrix": provider_registry.get("providers", []),
        "semantic_coverage": semantic_index.get("index", {}).get("summary", {}),
        "runtime_profiles": runtime_profiles.get("profiles", []),
        "risk_lanes": risk_lanes,
        "blocker_board": blockers,
        "graph": {
            "nodes": nodes,
            "edges": _edges(provider_nodes),
        },
        "warnings": [],
        "unresolved": blockers,
        "artifact_refs": workbench_v2_artifact_refs(codebase_id),
        "created_at": now(),
    }
    return payload


def render_workbench_v2_html(payload: dict[str, Any]) -> str:
    summary = payload.get("summary", {})
    sections = "\n".join(f"<li>{html.escape(section['title'])}</li>" for section in payload.get("sections", []))
    providers = "\n".join(
        "<tr><td>{}</td><td>{}</td><td>{}</td></tr>".format(
            html.escape(str(provider.get("provider_id"))),
            html.escape(str(provider.get("status"))),
            html.escape(str(provider.get("reason_code") or provider.get("reason") or "")),
        )
        for provider in payload.get("provider_matrix", [])
    )
    blockers = "\n".join(
        "<li><strong>{}</strong>: {}</li>".format(html.escape(str(item.get("code") or item.get("provider_id") or "blocker")), html.escape(str(item.get("message") or item.get("reason") or item)))
        for item in payload.get("blocker_board", [])
    )
    return f"""<!doctype html>
<html lang="zh-CN">
<head><meta charset="utf-8"><title>V2.16 Workbench v2</title>
<style>body{{font-family:-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif;margin:24px;line-height:1.5}}table{{border-collapse:collapse;width:100%}}td,th{{border:1px solid #ddd;padding:6px}}.metric{{display:inline-block;margin:6px 12px 6px 0;padding:8px;border:1px solid #ddd;border-radius:6px}}</style></head>
<body>
<h1>V2.16 Coding Agent 审查台</h1>
<div class="metric">Provider: {summary.get('provider_count', 0)}</div>
<div class="metric">可用 Provider: {summary.get('available_provider_count', 0)}</div>
<div class="metric">语义事实: {summary.get('semantic_fact_count', 0)}</div>
<div class="metric">Runtime Profile: {summary.get('runtime_profile_count', 0)}</div>
<div class="metric">Blocker: {summary.get('blocker_count', 0)}</div>
<h2>审查区块</h2><ul>{sections}</ul>
<h2>Provider Matrix</h2><table><tr><th>Provider</th><th>Status</th><th>Reason</th></tr>{providers}</table>
<h2>Blocker Board</h2><ul>{blockers}</ul>
</body></html>"""


def render_workbench_v2_mermaid(payload: dict[str, Any]) -> str:
    lines = ["flowchart TD"]
    node_ids = {node["node_id"] for node in payload.get("graph", {}).get("nodes", [])}
    for node in payload.get("graph", {}).get("nodes", []):
        lines.append(f"  {node['node_id']}[\"{_label(node.get('label'))}\"]")
    for edge in payload.get("graph", {}).get("edges", []):
        if edge["from"] in node_ids and edge["to"] in node_ids:
            lines.append(f"  {edge['from']} --> {edge['to']}")
    return "\n".join(lines) + "\n"


def public_workbench_v2_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return dict(payload)


def _blockers(provider_registry: dict[str, Any], semantic_index: dict[str, Any], runtime_profiles: dict[str, Any], workbench: dict[str, Any]) -> list[dict[str, Any]]:
    blockers: list[dict[str, Any]] = []
    blockers.extend(provider_registry.get("unresolved", []))
    blockers.extend(semantic_index.get("index", {}).get("provider_blockers", []))
    blockers.extend(runtime_profiles.get("warnings", []))
    blockers.extend(workbench.get("blockers", []))
    return blockers[:100]


def _edges(provider_nodes: list[dict[str, Any]]) -> list[dict[str, str]]:
    edges = []
    for node in provider_nodes:
        edges.append({"from": "section_provider_matrix", "to": node["node_id"], "type": "lists_provider"})
    return edges


def _node_id(prefix: str, raw: str) -> str:
    return f"{prefix}_{hashlib.sha256(raw.encode('utf-8')).hexdigest()[:12]}"


def _stable_id(prefix: str, *parts: Any) -> str:
    return f"{prefix}_{hashlib.sha256('|'.join(str(part) for part in parts).encode('utf-8')).hexdigest()[:20]}"


def _label(value: Any) -> str:
    return str(value or "").replace('"', "'").replace("\n", " ")[:80]
