"""Deterministic Code Graph builder."""

from __future__ import annotations

from typing import Any

from .model import GRAPH_SCHEMA_VERSION, SUPPORTED_RELATIONS, UNSUPPORTED_RELATIONS, edge, node


def build_graph_model(
    *,
    workspace_id: str,
    codebase_id: str,
    snapshot_id: str,
    snapshot: dict[str, Any],
    files: list[dict[str, Any]],
    inventory: dict[str, Any],
    symbols: dict[str, Any],
    trace: dict[str, Any],
    devwiki: dict[str, Any],
    created_at: str,
) -> dict[str, Any]:
    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []
    ids: dict[tuple[str, str], str] = {}

    def add_node(item: dict[str, Any]) -> str:
        key = (item["node_type"], item["natural_id"])
        if key in ids:
            return ids[key]
        ids[key] = item["node_id"]
        nodes.append(item)
        return item["node_id"]

    codebase_node = add_node(node("Codebase", codebase_id, label=codebase_id, snapshot_id=snapshot_id, data={"codebase_id": codebase_id}))
    snapshot_node = add_node(node("Snapshot", snapshot_id, label=snapshot_id, snapshot_id=snapshot_id, data={"stats": snapshot.get("stats", {})}))
    edges.append(_edge("GENERATED_FROM", snapshot_node, codebase_node, snapshot_id=snapshot_id, extractor="snapshot"))

    file_node_by_path: dict[str, str] = {}
    folder_node_by_path: dict[str, str] = {}
    for record in files:
        if not record.get("included"):
            continue
        path = str(record.get("path") or "")
        if not path:
            continue
        parts = path.split("/")
        parent = codebase_node
        current = ""
        for folder in parts[:-1]:
            current = f"{current}/{folder}".strip("/")
            folder_id = folder_node_by_path.get(current)
            if not folder_id:
                folder_id = add_node(node("Folder", current, label=current, snapshot_id=snapshot_id, data={"path": current}))
                folder_node_by_path[current] = folder_id
                edges.append(_edge("CONTAINS", parent, folder_id, snapshot_id=snapshot_id, extractor="snapshot_file_tree"))
            parent = folder_id
        file_id = add_node(node("File", path, label=path, snapshot_id=snapshot_id, data={"path": path, "language": record.get("language"), "loc": record.get("loc")}))
        file_node_by_path[path] = file_id
        edges.append(_edge("CONTAINS", parent, file_id, snapshot_id=snapshot_id, extractor="snapshot_file_tree"))

    symbol_node_by_id: dict[str, str] = {}
    for item in symbols.get("symbols", []):
        symbol_id = str(item.get("symbol_id") or "")
        if not symbol_id:
            continue
        kind = str(item.get("kind") or "symbol")
        node_type = {"module": "Module", "class": "Class", "function": "Function", "method": "Method"}.get(kind, "Symbol")
        graph_id = add_node(
            node(
                node_type,
                symbol_id,
                label=str(item.get("qualified_name") or item.get("name") or symbol_id),
                snapshot_id=snapshot_id,
                data={k: item.get(k) for k in ("symbol_id", "qualified_name", "name", "path", "line_range", "signature")},
            )
        )
        symbol_node_by_id[symbol_id] = graph_id
        file_id = file_node_by_path.get(str(item.get("path") or ""))
        if file_id:
            edges.append(_edge("DEFINES", file_id, graph_id, snapshot_id=snapshot_id, extractor="python_symbol_index", evidence=_path_evidence(item)))

    module_node_by_name = {str(item.get("data", {}).get("qualified_name") or item.get("label")): item["node_id"] for item in nodes if item.get("node_type") == "Module"}
    for item in symbols.get("imports", []):
        from_id = module_node_by_name.get(str(item.get("from_module") or ""))
        to_id = module_node_by_name.get(str(item.get("to_module") or ""))
        if from_id and to_id:
            edges.append(_edge("IMPORTS", from_id, to_id, snapshot_id=snapshot_id, extractor="python_import_ast", evidence=_path_evidence(item), confidence=0.9))

    capability_node_by_id: dict[str, str] = {}
    for item in inventory.get("capabilities", []):
        capability_id = str(item.get("capability_id") or "")
        if not capability_id:
            continue
        capability_node_by_id[capability_id] = add_node(
            node("Capability", capability_id, label=capability_id, snapshot_id=snapshot_id, data={"capability_id": capability_id, "surface_count": item.get("surface_count")})
        )

    surface_node_by_id: dict[str, str] = {}
    for item in inventory.get("surfaces", []):
        surface_id = str(item.get("surface_id") or "")
        if not surface_id:
            continue
        surface_type = str(item.get("surface_type") or "surface")
        node_type = {"http_api": "HTTPRoute", "mcp_tool": "MCPTool", "cli_command": "CLICommand", "frontend_page": "FrontendPage"}.get(surface_type, "PublicSurface")
        graph_id = add_node(node(node_type, surface_id, label=str(item.get("name") or surface_id), snapshot_id=snapshot_id, data=dict(item)))
        surface_node_by_id[surface_id] = graph_id
        file_id = file_node_by_path.get(str(item.get("source_file") or ""))
        relation = {"http_api": "EXPOSES_ROUTE", "mcp_tool": "REGISTERS_MCP_TOOL", "cli_command": "EXPOSES_CLI_COMMAND"}.get(surface_type, "GENERATED_FROM")
        if file_id:
            edges.append(_edge(relation, file_id, graph_id, snapshot_id=snapshot_id, extractor=str(item.get("extractor") or "inventory"), evidence=_surface_evidence(item)))
        capability_id = str(item.get("capability_id") or "")
        capability_node = capability_node_by_id.get(capability_id)
        if capability_node:
            edges.append(_edge("IMPLEMENTS_CAPABILITY", graph_id, capability_node, snapshot_id=snapshot_id, extractor="inventory_capability_normalizer", evidence=_surface_evidence(item), confidence=0.9))

    evidence_node_by_id: dict[str, str] = {}
    for item in trace.get("evidence", []):
        evidence_id = str(item.get("evidence_id") or "")
        if not evidence_id:
            continue
        graph_id = add_node(node("EvidenceSpan", evidence_id, label=evidence_id, snapshot_id=snapshot_id, data=dict(item)))
        evidence_node_by_id[evidence_id] = graph_id
        surface_node = surface_node_by_id.get(str(item.get("surface_id") or ""))
        symbol_node = symbol_node_by_id.get(str(item.get("symbol_id") or ""))
        if surface_node:
            edges.append(_edge("EVIDENCED_BY", surface_node, graph_id, snapshot_id=snapshot_id, extractor="evidence_trace", evidence=[item]))
        if symbol_node:
            edges.append(_edge("EVIDENCED_BY", symbol_node, graph_id, snapshot_id=snapshot_id, extractor="evidence_trace", evidence=[item]))

    for item in trace.get("mappings", []):
        if item.get("to_type") == "symbol":
            surface_node = surface_node_by_id.get(str(item.get("from_id") or ""))
            symbol_node = symbol_node_by_id.get(str(item.get("to_id") or ""))
            if surface_node and symbol_node:
                edges.append(_edge("HANDLED_BY", surface_node, symbol_node, snapshot_id=snapshot_id, extractor="surface_symbol_mapping", evidence=_mapping_evidence(item, evidence_node_by_id), confidence=float(item.get("confidence") or 0.8)))

    for page in devwiki.get("pages", []):
        page_id = str(page.get("page_id") or "")
        page_node = add_node(node("DevWikiPage", page_id, label=str(page.get("title") or page_id), snapshot_id=snapshot_id, data={"page_id": page_id, "slug": page.get("slug"), "stale": page.get("stale")}))
        for ref in page.get("source_artifact_refs", []):
            edges.append(_edge("GENERATED_FROM", page_node, snapshot_node, snapshot_id=snapshot_id, extractor="devwiki_source_artifact_refs", evidence=[{"type": ref.get("type"), "artifact_ref": ref.get("artifact_ref")}], confidence=0.75))
            break
        for ev in page.get("evidence", [])[:20]:
            evidence_id = str(ev.get("evidence_id") or "")
            evidence_node = evidence_node_by_id.get(evidence_id)
            if evidence_node:
                edges.append(_edge("EVIDENCED_BY", page_node, evidence_node, snapshot_id=snapshot_id, extractor="devwiki_evidence", evidence=[ev], confidence=0.9))
        for capability_id, capability_node in capability_node_by_id.items():
            if capability_id in str(page.get("slug") or "") or capability_id in str(page.get("title") or "").lower():
                edges.append(_edge("DOCUMENTED_BY", capability_node, page_node, snapshot_id=snapshot_id, extractor="devwiki_slug_match", evidence=_artifact_evidence(page), confidence=0.8))

    edges = _dedupe_edges(edges)
    summary = _summary(workspace_id, codebase_id, snapshot_id, nodes, edges, created_at)
    return {
        "schema_version": GRAPH_SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "created_at": created_at,
        "updated_at": created_at,
        "nodes": nodes,
        "edges": edges,
        "summary": summary,
        "source_artifact_refs": _source_refs(snapshot, inventory, symbols, trace, devwiki),
    }


def _edge(relation: str, from_id: str, to_id: str, *, snapshot_id: str, extractor: str, evidence: list[dict[str, Any]] | None = None, needs_review: list[dict[str, Any]] | None = None, confidence: float = 1.0) -> dict[str, Any]:
    if not evidence and not needs_review:
        needs_review = [{"code": "EDGE_EVIDENCE_REVIEW", "reason": "Edge was derived from deterministic artifact structure without a line-level evidence span."}]
    return edge(relation, from_id, to_id, snapshot_id=snapshot_id, extractor=extractor, evidence=evidence, needs_review=needs_review, confidence=confidence)


def _path_evidence(item: dict[str, Any]) -> list[dict[str, Any]]:
    path = item.get("path") or item.get("source_file")
    if not path:
        return []
    return [{"type": "source_file", "path": path, "line_range": item.get("line_range"), "extractor": "code_graph_builder"}]


def _surface_evidence(item: dict[str, Any]) -> list[dict[str, Any]]:
    return _path_evidence(item)


def _mapping_evidence(mapping: dict[str, Any], evidence_node_by_id: dict[str, str]) -> list[dict[str, Any]]:
    return [{"type": "evidence_id", "evidence_id": evidence_id} for evidence_id in mapping.get("evidence_ids", []) if evidence_id in evidence_node_by_id]


def _artifact_evidence(page: dict[str, Any]) -> list[dict[str, Any]]:
    return [{"type": ref.get("type"), "artifact_ref": ref.get("artifact_ref")} for ref in page.get("artifact_refs", [])]


def _summary(workspace_id: str, codebase_id: str, snapshot_id: str, nodes: list[dict[str, Any]], edges: list[dict[str, Any]], created_at: str) -> dict[str, Any]:
    node_counts = _counts(nodes, "node_type")
    edge_counts = _counts(edges, "relation")
    unsupported_count = sum(1 for item in edges if item.get("relation") in UNSUPPORTED_RELATIONS or item.get("relation") not in SUPPORTED_RELATIONS)
    return {
        "schema_version": GRAPH_SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "created_at": created_at,
        "node_count": len(nodes),
        "edge_count": len(edges),
        "node_counts": node_counts,
        "edge_coverage_by_type": edge_counts,
        "unsupported_edge_count": unsupported_count,
    }


def _counts(items: list[dict[str, Any]], field: str) -> dict[str, int]:
    result: dict[str, int] = {}
    for item in items:
        key = str(item.get(field) or "unknown")
        result[key] = result.get(key, 0) + 1
    return dict(sorted(result.items()))


def _source_refs(*payloads: dict[str, Any]) -> list[dict[str, Any]]:
    seen = set()
    refs = []
    for payload in payloads:
        for ref in payload.get("artifact_refs", []) + payload.get("source_artifact_refs", []):
            key = (str(ref.get("type")), str(ref.get("artifact_ref")))
            if key in seen:
                continue
            seen.add(key)
            refs.append(dict(ref))
    return refs


def _dedupe_edges(edges: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen = set()
    result = []
    for item in edges:
        key = item["edge_id"]
        if key in seen:
            continue
        seen.add(key)
        result.append(item)
    return result
