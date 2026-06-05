"""V2.8 deterministic architecture graph aggregation."""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from typing import Any


VIEW_IDS = {
    "system_overview",
    "layer_view",
    "capability_view",
    "public_surface_view",
    "doc_code_drift_view",
    "evidence_view",
}
CLUSTER_PRIORITY = ["layer", "capability", "public_surface", "folder_module", "document_authority", "confidence_band", "severity"]


def build_architecture_graph_aggregation(*, workspace_id: str, codebase_id: str, reconstructed_model: dict[str, Any], artifact_refs: list[dict[str, Any]]) -> dict[str, Any]:
    nodes = [_aggregate_node(node) for node in _source_nodes(reconstructed_model)]
    node_lookup = {node["source_node_id"]: node for node in nodes}
    clusters = _clusters(nodes)
    edges = _cluster_edges(reconstructed_model.get("edges", []), node_lookup)
    views = {view_id: _view(view_id, nodes, edges, clusters, reconstructed_model, artifact_refs) for view_id in sorted(VIEW_IDS)}
    summary = {
        "schema_version": "v2.8",
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": reconstructed_model.get("snapshot_id"),
        "graph_summary_id": _stable_id("graph-summary", codebase_id, str(reconstructed_model.get("snapshot_id") or "")),
        "node_count": len(nodes),
        "edge_count": len(edges),
        "cluster_count": len(clusters),
        "view_ids": sorted(VIEW_IDS),
        "filter_options": {
            "confidence_band": ["high", "medium", "low", "review"],
            "severity": ["fatal", "major", "minor", "info"],
            "accepted_only": [True, False],
            "unmatched_claims": [True, False],
            "public_surface_only": [True, False],
            "source_kind": ["document_claim", "code_fact", "alignment", "quality_finding", "explicit_inference"],
        },
        "coverage": {
            "nodes_with_source_refs": sum(1 for node in nodes if node["source_artifact_refs"] or node["evidence_refs"]),
            "nodes_needing_review": sum(1 for node in nodes if node["needs_review"]),
            "cluster_edges_with_source_edge_ids": sum(1 for edge in edges if edge["source_edge_ids"]),
        },
        "unsupported_edge_count": 0,
        "source_artifact_refs": reconstructed_model.get("source_artifact_refs", []),
        "artifact_refs": artifact_refs,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    return {"summary": summary, "clusters": {"schema_version": "v2.8", "clusters": clusters, "cluster_edges": edges}, "views": views}


def public_architecture_graph_aggregation_payload(payload: dict[str, Any], artifact_refs: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "schema_version": "v2.8",
        "summary": payload.get("summary", {}),
        "clusters": payload.get("clusters", {}).get("clusters", [])[:120],
        "cluster_edges": payload.get("clusters", {}).get("cluster_edges", [])[:180],
        "artifact_refs": artifact_refs,
    }


def _source_nodes(model: dict[str, Any]) -> list[dict[str, Any]]:
    nodes = [*model.get("target_nodes", []), *model.get("current_nodes", []), *model.get("diff_nodes", [])]
    return sorted(nodes, key=lambda item: str(item.get("node_id") or ""))


def _aggregate_node(node: dict[str, Any]) -> dict[str, Any]:
    memberships = _memberships(node)
    primary = sorted(memberships, key=lambda item: CLUSTER_PRIORITY.index(item["cluster_type"]) if item["cluster_type"] in CLUSTER_PRIORITY else 99)[0]
    source_refs = node.get("source_refs") or []
    needs_review = list(node.get("needs_review") or [])
    if str(node.get("source_kind")) == "alignment" and str(node.get("label", "")).lower().find("weak") >= 0:
        needs_review.append({"code": "WEAK_ALIGNMENT_EDGE_BLOCKED", "reason": "Weak alignment remains review-only in V2.8 graph views."})
    return {
        "node_id": f"aggnode:{_stable_id(str(node.get('node_id') or 'node'))}",
        "source_node_id": str(node.get("node_id") or ""),
        "node_type": node.get("node_type") or "node",
        "label": node.get("label") or node.get("node_id"),
        "section": node.get("section"),
        "source_kind": node.get("source_kind"),
        "primary_cluster_id": primary["cluster_id"],
        "cluster_memberships": memberships,
        "source_artifact_refs": source_refs,
        "evidence_refs": source_refs,
        "confidence": float(node.get("confidence") or 0),
        "needs_review": needs_review,
    }


def _memberships(node: dict[str, Any]) -> list[dict[str, str]]:
    label = str(node.get("label") or node.get("node_id") or "unknown")
    section = str(node.get("section") or "unknown")
    source_kind = str(node.get("source_kind") or "unknown")
    confidence = float(node.get("confidence") or 0)
    severity = _severity(node)
    keys: list[tuple[str, str]] = []
    if section == "current_from_code":
        keys.append(("layer", "current_code"))
    if "capability" in label.lower() or "knowledge_" in label.lower():
        keys.append(("capability", _bucket(label)))
    if any(token in label for token in ("GET ", "POST ", "MCP", "CLI", "knowledge_")):
        keys.append(("public_surface", _bucket(label)))
    keys.append(("document_authority", source_kind))
    keys.append(("confidence_band", _confidence_band(confidence)))
    if severity:
        keys.append(("severity", severity))
    if not keys:
        keys.append(("folder_module", "unknown"))
    return [{"cluster_id": _cluster_id(kind, key), "cluster_type": kind, "primary_key": key} for kind, key in keys]


def _clusters(nodes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, dict[str, Any]] = {}
    for node in nodes:
        for membership in node["cluster_memberships"]:
            cluster_id = membership["cluster_id"]
            cluster = grouped.setdefault(
                cluster_id,
                {
                    "cluster_id": cluster_id,
                    "cluster_type": membership["cluster_type"],
                    "label": membership["primary_key"],
                    "primary_key": membership["primary_key"],
                    "member_node_ids": [],
                    "source_artifact_refs": [],
                    "expansion_refs": [],
                    "confidence": 1.0,
                    "needs_review": [],
                },
            )
            cluster["member_node_ids"].append(node["node_id"])
            cluster["source_artifact_refs"].extend(node["source_artifact_refs"])
            cluster["expansion_refs"].append({"type": "architecture_graph_node", "node_id": node["node_id"], "source_node_id": node["source_node_id"]})
            cluster["confidence"] = min(float(cluster["confidence"]), float(node["confidence"]))
            cluster["needs_review"].extend(node["needs_review"])
    result = []
    for cluster in grouped.values():
        source_refs = _dedupe_refs(cluster["source_artifact_refs"])
        cluster["source_artifact_refs"] = source_refs
        cluster["member_node_ids"] = sorted(set(cluster["member_node_ids"]))
        cluster["member_count"] = len(cluster["member_node_ids"])
        cluster["edge_count"] = 0
        cluster["needs_review"] = cluster["needs_review"][:20]
        result.append(cluster)
    return sorted(result, key=lambda item: (CLUSTER_PRIORITY.index(item["cluster_type"]) if item["cluster_type"] in CLUSTER_PRIORITY else 99, item["cluster_id"]))


def _cluster_edges(source_edges: list[dict[str, Any]], node_lookup: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str, str], dict[str, Any]] = {}
    for index, edge in enumerate(source_edges):
        source = node_lookup.get(str(edge.get("from_node_id") or ""))
        target = node_lookup.get(str(edge.get("to_node_id") or ""))
        if not source or not target:
            continue
        edge_type = str(edge.get("edge_type") or "RELATES_TO")
        if "WEAK" in edge_type.upper() or "TOKEN" in edge_type.upper():
            continue
        key = (source["primary_cluster_id"], target["primary_cluster_id"], edge_type)
        item = grouped.setdefault(
            key,
            {
                "cluster_edge_id": f"cluster_edge:{_stable_id(*key)}",
                "from_cluster_id": key[0],
                "to_cluster_id": key[1],
                "edge_type": edge_type,
                "source_edge_ids": [],
                "evidence_refs": [],
                "confidence": 1.0,
                "needs_review": [],
            },
        )
        item["source_edge_ids"].append(str(edge.get("edge_id") or f"edge:{index}"))
        item["evidence_refs"].extend(edge.get("source_refs") or edge.get("evidence_refs") or [])
        item["confidence"] = min(float(item["confidence"]), float(edge.get("confidence") or 0.8))
    return sorted(grouped.values(), key=lambda item: item["cluster_edge_id"])


def _view(view_id: str, nodes: list[dict[str, Any]], edges: list[dict[str, Any]], clusters: list[dict[str, Any]], model: dict[str, Any], artifact_refs: list[dict[str, Any]]) -> dict[str, Any]:
    filtered_nodes = _filter_nodes(view_id, nodes)
    node_clusters = {node["primary_cluster_id"] for node in filtered_nodes}
    filtered_clusters = [cluster for cluster in clusters if cluster["cluster_id"] in node_clusters]
    filtered_edges = [edge for edge in edges if edge["from_cluster_id"] in node_clusters and edge["to_cluster_id"] in node_clusters]
    return {
        "schema_version": "v2.8",
        "workspace_id": model.get("workspace_id"),
        "codebase_id": model.get("codebase_id"),
        "snapshot_id": model.get("snapshot_id"),
        "view_id": view_id,
        "view_type": "clustered_architecture_graph",
        "filters": {"view_id": view_id},
        "nodes": filtered_nodes[:240],
        "edges": filtered_edges[:240],
        "clusters": filtered_clusters[:160],
        "summary": {"node_count": len(filtered_nodes), "edge_count": len(filtered_edges), "cluster_count": len(filtered_clusters)},
        "source_artifact_refs": model.get("source_artifact_refs", []),
        "artifact_refs": artifact_refs,
        "warnings": [] if filtered_nodes else [{"code": "EMPTY_VIEW", "message": f"No graph nodes matched {view_id}."}],
        "unresolved": [],
    }


def _filter_nodes(view_id: str, nodes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if view_id == "system_overview":
        return nodes
    if view_id == "layer_view":
        return [node for node in nodes if any(item["cluster_type"] == "layer" for item in node["cluster_memberships"])]
    if view_id == "capability_view":
        return [node for node in nodes if any(item["cluster_type"] == "capability" for item in node["cluster_memberships"])]
    if view_id == "public_surface_view":
        return [node for node in nodes if any(item["cluster_type"] == "public_surface" for item in node["cluster_memberships"])]
    if view_id == "doc_code_drift_view":
        return [node for node in nodes if node.get("section") == "gap_and_drift" or node.get("needs_review")]
    if view_id == "evidence_view":
        return [node for node in nodes if node.get("evidence_refs")]
    raise FileNotFoundError("ARCHITECTURE_GRAPH_VIEW_NOT_FOUND")


def _cluster_id(kind: str, key: str) -> str:
    return f"cluster:{kind}:{_stable_id(key)}"


def _stable_id(*parts: str) -> str:
    return hashlib.sha256(":".join(parts).encode("utf-8")).hexdigest()[:16]


def _bucket(label: str) -> str:
    clean = "".join(ch.lower() if ch.isalnum() else "_" for ch in label)[:60].strip("_")
    return clean or "unknown"


def _confidence_band(value: float) -> str:
    if value >= 0.8:
        return "high"
    if value >= 0.5:
        return "medium"
    if value > 0:
        return "low"
    return "review"


def _severity(node: dict[str, Any]) -> str | None:
    label = str(node.get("label") or "").lower()
    for severity in ("fatal", "major", "minor", "info"):
        if severity in label:
            return severity
    if node.get("needs_review"):
        return "major"
    return None


def _dedupe_refs(items: list[Any]) -> list[Any]:
    seen = set()
    result = []
    for item in items:
        key = repr(item)
        if key in seen:
            continue
        seen.add(key)
        result.append(item)
    return result[:80]
