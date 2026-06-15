"""Code proof graph builder for V2.27 Phase 93."""

from __future__ import annotations

import hashlib
from collections import Counter
from pathlib import Path
from typing import Any

from data_service.mcp_common import now, read_json, write_json

from ..artifacts import read_jsonl, write_jsonl
from .paths import (
    architecture_intent_claim_artifact_refs,
    architecture_intent_diagram_claims_path,
    architecture_intent_evidence_bundles_path,
    architecture_intent_proof_edges_path,
    architecture_intent_proof_graph_artifact_refs,
    architecture_intent_proof_graph_summary_path,
    architecture_intent_proof_nodes_path,
    architecture_intent_source_artifact_refs,
    architecture_intent_sources_path,
)


SCHEMA_VERSION = "v2.25"
FORBIDDEN_EDGE_TYPES = {"runtime_calls", "data_flow", "control_flow", "type_inferred_dependency", "runtime_observed"}


def build_code_proof_graph(*, workspace: Path, workspace_id: str, codebase_id: str, snapshot_id: str) -> dict[str, Any]:
    created_at = now()
    sources = read_jsonl(architecture_intent_sources_path(workspace, codebase_id))
    claims = read_jsonl(architecture_intent_diagram_claims_path(workspace, codebase_id))
    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []
    bundles: list[dict[str, Any]] = []

    source_node_by_id: dict[str, str] = {}
    for source in sources:
        node_type = node_type_for_source(str(source.get("source_type") or ""))
        node = make_node(
            workspace_id=workspace_id,
            codebase_id=codebase_id,
            snapshot_id=snapshot_id,
            node_type=node_type,
            label=str(source.get("path") or ""),
            source_refs=[str(source.get("source_id") or "")],
            evidence_refs=list(source.get("evidence") or []),
            confidence=float(source.get("confidence") or 0.6),
            semantic_limit="descriptor_only" if node_type == "runtime_descriptor" else "source_fact",
            created_at=created_at,
        )
        nodes.append(node)
        source_node_by_id[str(source.get("source_id") or "")] = node["node_id"]

    for claim in claims:
        claim_node = make_node(
            workspace_id=workspace_id,
            codebase_id=codebase_id,
            snapshot_id=snapshot_id,
            node_type="document_claim",
            label=str(claim.get("label") or ""),
            source_refs=[str(claim.get("claim_id") or "")],
            evidence_refs=list(claim.get("evidence") or []),
            confidence=float(claim.get("confidence") or 0.6),
            semantic_limit="document_claim_only",
            created_at=created_at,
        )
        nodes.append(claim_node)
        source_node = source_node_by_id.get(str(claim.get("source_id") or ""))
        if source_node:
            edge = make_edge(
                workspace_id=workspace_id,
                codebase_id=codebase_id,
                snapshot_id=snapshot_id,
                edge_type="documented_by",
                source_node_id=claim_node["node_id"],
                target_node_id=source_node,
                evidence_refs=list(claim.get("evidence") or []),
                confidence=min(float(claim.get("confidence") or 0.6), 0.9),
                semantic_limit="not_runtime_call",
                created_at=created_at,
            )
            edges.append(edge)
            bundles.append(make_bundle(workspace_id, codebase_id, snapshot_id, claim_node, edge, created_at))

    # Add conservative source fact edges to make config/test/runtime semantics explicit.
    for source_id, node_id in source_node_by_id.items():
        source = next((item for item in sources if str(item.get("source_id") or "") == source_id), {})
        node_type = node_type_for_source(str(source.get("source_type") or ""))
        edge_type = {
            "code_file": "defined_by",
            "config_fact": "configured_by",
            "test_fact": "tested_by",
            "runtime_descriptor": "described_by",
            "architecture_source": "documented_by",
        }.get(node_type, "documented_by")
        edges.append(
            make_edge(
                workspace_id=workspace_id,
                codebase_id=codebase_id,
                snapshot_id=snapshot_id,
                edge_type=edge_type,
                source_node_id=node_id,
                target_node_id=node_id,
                evidence_refs=list(source.get("evidence") or []),
                confidence=float(source.get("confidence") or 0.6),
                semantic_limit="descriptor_only" if node_type == "runtime_descriptor" else "source_fact",
                created_at=created_at,
            )
        )

    nodes = sorted(_dedupe(nodes, "node_id"), key=lambda item: (item["node_type"], item["label"]))
    edges = sorted(_dedupe(edges, "edge_id"), key=lambda item: (item["edge_type"], item["source_node_id"], item["target_node_id"]))
    bundles = sorted(_dedupe(bundles, "bundle_id"), key=lambda item: item["bundle_id"])
    forbidden_edges = [edge for edge in edges if edge.get("edge_type") in FORBIDDEN_EDGE_TYPES or edge.get("semantic_limit") == "runtime_observed"]
    summary = build_summary(workspace_id, codebase_id, snapshot_id, nodes, edges, bundles, forbidden_edges, created_at)

    write_jsonl(architecture_intent_proof_nodes_path(workspace, codebase_id), nodes)
    write_jsonl(architecture_intent_proof_edges_path(workspace, codebase_id), edges)
    write_jsonl(architecture_intent_evidence_bundles_path(workspace, codebase_id), bundles)
    write_json(architecture_intent_proof_graph_summary_path(workspace, codebase_id), summary)
    return {
        "schema_version": SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "nodes": nodes,
        "edges": edges,
        "evidence_bundles": bundles,
        "summary": summary,
        "artifact_refs": architecture_intent_proof_graph_artifact_refs(codebase_id),
    }


def read_code_proof_graph(*, workspace: Path, codebase_id: str) -> dict[str, Any]:
    summary = read_json(architecture_intent_proof_graph_summary_path(workspace, codebase_id), {})
    return {
        "schema_version": summary.get("schema_version", SCHEMA_VERSION),
        "workspace_id": summary.get("workspace_id"),
        "codebase_id": codebase_id,
        "snapshot_id": summary.get("snapshot_id"),
        "nodes": read_jsonl(architecture_intent_proof_nodes_path(workspace, codebase_id)),
        "edges": read_jsonl(architecture_intent_proof_edges_path(workspace, codebase_id)),
        "evidence_bundles": read_jsonl(architecture_intent_evidence_bundles_path(workspace, codebase_id)),
        "summary": summary,
        "artifact_refs": architecture_intent_proof_graph_artifact_refs(codebase_id),
    }


def node_type_for_source(source_type: str) -> str:
    if source_type == "code":
        return "code_file"
    if source_type == "config":
        return "config_fact"
    if source_type == "test":
        return "test_fact"
    if source_type == "runtime_descriptor":
        return "runtime_descriptor"
    return "architecture_source"


def make_node(
    *,
    workspace_id: str,
    codebase_id: str,
    snapshot_id: str,
    node_type: str,
    label: str,
    source_refs: list[str],
    evidence_refs: list[dict[str, Any]],
    confidence: float,
    semantic_limit: str,
    created_at: str,
) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "node_id": stable_id("proofnode", snapshot_id, node_type, label, source_refs),
        "node_type": node_type,
        "label": label[:500],
        "source_refs": source_refs,
        "evidence_refs": evidence_refs,
        "confidence": round(confidence, 3),
        "semantic_limit": semantic_limit,
        "created_at": created_at,
    }


def make_edge(
    *,
    workspace_id: str,
    codebase_id: str,
    snapshot_id: str,
    edge_type: str,
    source_node_id: str,
    target_node_id: str,
    evidence_refs: list[dict[str, Any]],
    confidence: float,
    semantic_limit: str,
    created_at: str,
) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "edge_id": stable_id("proofedge", snapshot_id, edge_type, source_node_id, target_node_id, evidence_refs),
        "edge_type": edge_type,
        "source_node_id": source_node_id,
        "target_node_id": target_node_id,
        "evidence_refs": evidence_refs,
        "confidence": round(confidence, 3),
        "semantic_limit": semantic_limit,
        "needs_review": [] if edge_type not in FORBIDDEN_EDGE_TYPES and semantic_limit != "runtime_observed" else [{"code": "FORBIDDEN_PROOF_EDGE", "reason": "Forbidden semantic edge detected."}],
        "created_at": created_at,
    }


def make_bundle(workspace_id: str, codebase_id: str, snapshot_id: str, node: dict[str, Any], edge: dict[str, Any], created_at: str) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "bundle_id": stable_id("evidencebundle", snapshot_id, node.get("node_id"), edge.get("edge_id")),
        "subject_node_id": node.get("node_id"),
        "edge_ids": [edge.get("edge_id")],
        "evidence_refs": edge.get("evidence_refs", []),
        "confidence": min(float(node.get("confidence") or 0.0), float(edge.get("confidence") or 0.0)),
        "created_at": created_at,
    }


def build_summary(
    workspace_id: str,
    codebase_id: str,
    snapshot_id: str,
    nodes: list[dict[str, Any]],
    edges: list[dict[str, Any]],
    bundles: list[dict[str, Any]],
    forbidden_edges: list[dict[str, Any]],
    created_at: str,
) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "created_at": created_at,
        "proof_node_count": len(nodes),
        "proof_edge_count": len(edges),
        "evidence_bundle_count": len(bundles),
        "node_type_counts": dict(sorted(Counter(str(row.get("node_type")) for row in nodes).items())),
        "edge_type_counts": dict(sorted(Counter(str(row.get("edge_type")) for row in edges).items())),
        "forbidden_edge_count": len(forbidden_edges),
        "artifact_refs": [
            *architecture_intent_source_artifact_refs(codebase_id),
            *architecture_intent_claim_artifact_refs(codebase_id),
            *architecture_intent_proof_graph_artifact_refs(codebase_id),
        ],
    }


def stable_id(prefix: str, *parts: Any) -> str:
    raw = "\x1f".join(str(part) for part in parts)
    return f"{prefix}_{hashlib.sha256(raw.encode('utf-8')).hexdigest()[:16]}"


def _dedupe(rows: list[dict[str, Any]], key: str) -> list[dict[str, Any]]:
    seen: set[str] = set()
    result: list[dict[str, Any]] = []
    for row in rows:
        value = str(row.get(key) or "")
        if not value or value in seen:
            continue
        seen.add(value)
        result.append(row)
    return result
