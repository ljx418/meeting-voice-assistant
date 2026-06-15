"""V2.42 relationship chain builder.

The output is a reading aid for agents, not a full call graph or runtime path.
"""

from __future__ import annotations

import hashlib
from collections import Counter
from pathlib import PurePosixPath
from typing import Any

from data_service.mcp_common import now, read_json, write_json

from ..artifacts import (
    architecture_forbidden_edge_scan_v242_path,
    architecture_relationship_chain_summary_v242_path,
    architecture_relationship_chains_v242_path,
    read_jsonl,
    write_jsonl,
)


SCHEMA_VERSION = "v2.42_relationship_chain"
ALLOWED_EDGE_TYPES = {
    "capability_has_entrypoint",
    "entrypoint_handled_by_symbol",
    "symbol_references_symbol",
    "module_imports_module",
    "module_referenced_by_test",
    "module_uses_config",
    "claim_constrains_capability",
    "candidate_hint",
}
FORBIDDEN_EDGE_TYPES = {
    "runtime_call",
    "runtime_calls",
    "data_flow",
    "control_flow",
    "production_topology",
    "production_runtime_topology",
    "type_inferred_dependency",
}


def build_relationship_chains_v3(
    *,
    workspace,
    workspace_id: str,
    codebase_id: str,
    snapshot_id: str,
    surfaces: list[dict[str, Any]],
    symbols: list[dict[str, Any]],
    files: list[dict[str, Any]],
    language_symbols: list[dict[str, Any]],
    language_references: list[dict[str, Any]],
    workflow_candidates: list[dict[str, Any]],
    runtime_candidates: list[dict[str, Any]],
    entrypoint_candidates: list[dict[str, Any]],
    doc_claims: list[dict[str, Any]] | None,
    artifact_refs: list[dict[str, str]],
) -> dict[str, Any]:
    chains: list[dict[str, Any]] = []
    blockers: list[dict[str, Any]] = []
    symbol_by_path = _symbols_by_path([*symbols, *language_symbols])
    refs_by_path = _refs_by_path(language_references)
    tests_by_stem = _tests_by_stem(files)

    for surface in sorted(surfaces, key=lambda item: str(item.get("surface_id") or "")):
        chain = _surface_chain(workspace_id, codebase_id, snapshot_id, surface, symbol_by_path, refs_by_path, tests_by_stem, doc_claims or [])
        if chain:
            chains.append(chain)

    if len(chains) < 10:
        for candidate in [*entrypoint_candidates, *workflow_candidates, *runtime_candidates]:
            if len(chains) >= 10:
                break
            chain = _candidate_chain(workspace_id, codebase_id, snapshot_id, candidate, refs_by_path, tests_by_stem)
            if chain:
                chains.append(chain)

    chains = _dedupe_chains(chains)
    if not chains:
        blockers.append({"code": "RELATIONSHIP_CHAIN_NOT_ENOUGH_EVIDENCE", "reason": "No surface or candidate evidence could be converted into a reviewable chain."})

    forbidden_scan = _forbidden_edge_scan(workspace_id, codebase_id, snapshot_id, chains)
    summary = _summary(workspace_id, codebase_id, snapshot_id, chains, blockers, forbidden_scan, artifact_refs)
    write_jsonl(architecture_relationship_chains_v242_path(workspace, codebase_id), chains)
    write_json(architecture_relationship_chain_summary_v242_path(workspace, codebase_id), summary)
    write_json(architecture_forbidden_edge_scan_v242_path(workspace, codebase_id), forbidden_scan)
    return {
        "schema_version": SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "chains": chains,
        "summary": summary,
        "forbidden_edge_scan": forbidden_scan,
        "artifact_refs": artifact_refs,
        "created_at": summary["created_at"],
    }


def read_relationship_chains_v3(workspace, codebase_id: str, artifact_refs: list[dict[str, str]]) -> dict[str, Any]:
    chains = read_jsonl(architecture_relationship_chains_v242_path(workspace, codebase_id))
    summary = read_json(architecture_relationship_chain_summary_v242_path(workspace, codebase_id), {})
    forbidden_scan = read_json(architecture_forbidden_edge_scan_v242_path(workspace, codebase_id), {})
    if not summary:
        raise FileNotFoundError("ARCHITECTURE_RELATIONSHIP_CHAINS_V3_NOT_BUILT")
    return {
        "schema_version": SCHEMA_VERSION,
        "workspace_id": summary.get("workspace_id"),
        "codebase_id": codebase_id,
        "snapshot_id": summary.get("snapshot_id"),
        "chains": chains,
        "summary": summary,
        "forbidden_edge_scan": forbidden_scan,
        "artifact_refs": artifact_refs,
    }


def public_relationship_chains_v3_payload(payload: dict[str, Any], *, limit: int = 80) -> dict[str, Any]:
    chains = list(payload.get("chains") or [])
    return {
        "schema_version": payload.get("schema_version", SCHEMA_VERSION),
        "workspace_id": payload.get("workspace_id"),
        "codebase_id": payload.get("codebase_id"),
        "snapshot_id": payload.get("snapshot_id"),
        "summary": payload.get("summary") or {},
        "forbidden_edge_scan": payload.get("forbidden_edge_scan") or {},
        "chains": {"total": len(chains), "sample": chains[:limit], "truncated": len(chains) > limit},
        "artifact_refs": payload.get("artifact_refs") or [],
    }


def _surface_chain(workspace_id: str, codebase_id: str, snapshot_id: str, surface: dict[str, Any], symbol_by_path: dict[str, list[dict[str, Any]]], refs_by_path: dict[str, list[dict[str, Any]]], tests_by_stem: dict[str, list[str]], doc_claims: list[dict[str, Any]]) -> dict[str, Any] | None:
    source_file = str(surface.get("source_file") or surface.get("path") or "")
    if not source_file:
        return None
    surface_id = str(surface.get("surface_id") or _stable_id("surface", source_file, str(surface.get("line_range"))))
    capability_id = str(surface.get("capability_id") or surface.get("name") or surface_id)
    nodes = [_node("capability", f"capability:{capability_id}", capability_id), _node("entrypoint", f"surface:{surface_id}", surface_id, path=source_file, line_range=surface.get("line_range"))]
    edges = [_edge("capability_has_entrypoint", nodes[0]["node_id"], nodes[1]["node_id"], surface, "deterministic", 0.9)]
    handler = _best_symbol(source_file, surface, symbol_by_path)
    if handler:
        handler_id = f"symbol:{handler.get('fact_id') or handler.get('symbol_id') or handler.get('qualified_name') or handler.get('name')}"
        nodes.append(_node("handler", handler_id, str(handler.get("qualified_name") or handler.get("name") or handler_id), path=source_file, line_range=handler.get("line_range")))
        edges.append(_edge("entrypoint_handled_by_symbol", nodes[1]["node_id"], handler_id, handler, "deterministic", 0.88))
    else:
        nodes.append(_node("module", f"module:{source_file}", PurePosixPath(source_file).stem, path=source_file, line_range=surface.get("line_range")))
        edges.append(_edge("candidate_hint", nodes[1]["node_id"], f"module:{source_file}", surface, "heuristic", 0.62, needs_review=[{"code": "HANDLER_SYMBOL_NOT_RESOLVED", "reason": "Entrypoint line evidence did not resolve to a handler symbol."}]))
    _append_reference_nodes(nodes, edges, refs_by_path.get(source_file, [])[:3])
    _append_test_nodes(nodes, edges, source_file, tests_by_stem)
    _append_doc_claim_nodes(nodes, edges, capability_id, doc_claims)
    return _chain(workspace_id, codebase_id, snapshot_id, "capability_chain", capability_id, nodes, edges)


def _candidate_chain(workspace_id: str, codebase_id: str, snapshot_id: str, candidate: dict[str, Any], refs_by_path: dict[str, list[dict[str, Any]]], tests_by_stem: dict[str, list[str]]) -> dict[str, Any] | None:
    path = str(candidate.get("path") or "")
    if not path:
        return None
    label = str(candidate.get("label") or candidate.get("candidate_type") or path)
    nodes = [_node("entrypoint_candidate", f"candidate:{candidate.get('candidate_id')}", label, path=path, line_range=candidate.get("line_range"))]
    edges: list[dict[str, Any]] = []
    module_id = f"module:{path}"
    nodes.append(_node("module", module_id, PurePosixPath(path).stem, path=path, line_range=candidate.get("line_range")))
    reviews = list(candidate.get("needs_review") or [])
    reviews.append({"code": "CANDIDATE_REQUIRES_REVIEW", "reason": "Candidate chain is a reading hint, not a runtime topology claim."})
    edges.append(_edge("candidate_hint", nodes[0]["node_id"], module_id, candidate, "heuristic", min(0.72, float(candidate.get("confidence") or 0.5)), needs_review=reviews))
    _append_reference_nodes(nodes, edges, refs_by_path.get(path, [])[:3])
    _append_test_nodes(nodes, edges, path, tests_by_stem)
    return _chain(workspace_id, codebase_id, snapshot_id, "candidate_chain", label, nodes, edges)


def _append_reference_nodes(nodes: list[dict[str, Any]], edges: list[dict[str, Any]], refs: list[dict[str, Any]]) -> None:
    source_id = nodes[-1]["node_id"]
    for ref in refs:
        target = str(ref.get("target") or ref.get("name") or "")
        if not target:
            continue
        node_id = f"reference:{target}"
        nodes.append(_node("dependency_reference", node_id, target, path=ref.get("path"), line_range=ref.get("line_range")))
        edges.append(_edge("symbol_references_symbol", source_id, node_id, ref, "heuristic" if ref.get("needs_review") else "deterministic", float(ref.get("confidence") or 0.7), needs_review=list(ref.get("needs_review") or [])))


def _append_test_nodes(nodes: list[dict[str, Any]], edges: list[dict[str, Any]], source_file: str, tests_by_stem: dict[str, list[str]]) -> None:
    stem = PurePosixPath(source_file).stem.replace("_service", "").replace("_adapter", "")
    for test in tests_by_stem.get(stem, [])[:2]:
        node_id = f"test:{test}"
        nodes.append(_node("test", node_id, PurePosixPath(test).name, path=test))
        edges.append(_edge("module_referenced_by_test", f"module:{source_file}", node_id, {"path": test}, "heuristic", 0.68, needs_review=[{"code": "TEST_REFERENCE_HEURISTIC", "reason": "Test linkage is filename-derived."}]))


def _append_doc_claim_nodes(nodes: list[dict[str, Any]], edges: list[dict[str, Any]], capability_id: str, doc_claims: list[dict[str, Any]]) -> None:
    normalized = capability_id.lower().replace("_", " ")
    for claim in doc_claims[:200]:
        label = str(claim.get("label") or claim.get("text") or "")
        if not label or normalized not in label.lower():
            continue
        node_id = f"doc_claim:{claim.get('claim_id') or _stable_id('claim', label)}"
        nodes.append(_node("doc_claim", node_id, label[:120], path=claim.get("source_path"), line_range=claim.get("line_range")))
        edges.append(_edge("claim_constrains_capability", node_id, f"capability:{capability_id}", claim, "heuristic", 0.62, needs_review=[{"code": "DOC_CLAIM_TEXT_MATCH", "reason": "Doc claim linkage is text-derived and reviewable."}]))
        break


def _chain(workspace_id: str, codebase_id: str, snapshot_id: str, chain_type: str, label: str, nodes: list[dict[str, Any]], edges: list[dict[str, Any]]) -> dict[str, Any]:
    accepted = bool(edges) and all(edge["edge_type"] in ALLOWED_EDGE_TYPES for edge in edges) and all(edge["evidence_refs"] for edge in edges if edge["determinism"] == "deterministic")
    needs_review = [review for edge in edges for review in edge.get("needs_review", [])]
    status = "accepted" if accepted and not any(edge["edge_type"] in FORBIDDEN_EDGE_TYPES for edge in edges) else "needs_review"
    if not edges:
        needs_review.append({"code": "CHAIN_HAS_NO_EDGES", "reason": "Chain has no relationship edges."})
    return {
        "schema_version": SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "chain_id": _stable_id("chain-v3", codebase_id, snapshot_id, chain_type, label, ",".join(node["node_id"] for node in nodes[:5])),
        "chain_type": chain_type,
        "label": label,
        "status": status,
        "nodes": _dedupe_nodes(nodes),
        "edges": edges,
        "evidence_refs": _compact_evidence(edges),
        "confidence": round(sum(float(edge.get("confidence") or 0) for edge in edges) / max(1, len(edges)), 3),
        "completeness_score": _completeness(nodes, edges),
        "needs_review": needs_review,
        "created_at": now(),
    }


def _node(kind: str, node_id: str, label: str, *, path: Any = None, line_range: Any = None) -> dict[str, Any]:
    return {"node_id": node_id, "node_type": kind, "label": label, "path": path, "line_range": line_range}


def _edge(edge_type: str, source_id: str, target_id: str, source: dict[str, Any], determinism: str, confidence: float, *, needs_review: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    path = source.get("path") or source.get("source_file")
    line_range = source.get("line_range")
    evidence_refs = list(source.get("evidence_refs") or [])
    if not evidence_refs and path:
        evidence_refs = [{"type": "file_line", "path": path, "line_range": line_range}]
    review = list(needs_review or [])
    if determinism == "heuristic" and not review:
        review.append({"code": "HEURISTIC_EDGE", "reason": "Edge is a reading hint, not a runtime claim."})
    return {
        "edge_id": _stable_id("edge-v3", edge_type, source_id, target_id, str(path), str(line_range)),
        "edge_type": edge_type,
        "source_id": source_id,
        "target_id": target_id,
        "determinism": determinism,
        "confidence": confidence,
        "source_extractor": source.get("extractor") or source.get("provider") or "relationship_chain_v3",
        "evidence_refs": evidence_refs,
        "needs_review": review,
    }


def _summary(workspace_id: str, codebase_id: str, snapshot_id: str, chains: list[dict[str, Any]], blockers: list[dict[str, Any]], forbidden_scan: dict[str, Any], artifact_refs: list[dict[str, str]]) -> dict[str, Any]:
    statuses = Counter(chain["status"] for chain in chains)
    edge_types = Counter(edge["edge_type"] for chain in chains for edge in chain.get("edges", []))
    heuristic_edge_count = sum(1 for chain in chains for edge in chain.get("edges", []) if edge.get("determinism") == "heuristic")
    heuristic_without_review = sum(1 for chain in chains for edge in chain.get("edges", []) if edge.get("determinism") == "heuristic" and not edge.get("needs_review"))
    return {
        "schema_version": SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "chain_count": len(chains),
        "accepted_chain_count": statuses.get("accepted", 0),
        "needs_review_chain_count": statuses.get("needs_review", 0),
        "edge_type_counts": dict(sorted(edge_types.items())),
        "forbidden_edge_count": forbidden_scan["forbidden_edge_count"],
        "unsupported_edge_count": forbidden_scan["unsupported_edge_count"],
        "heuristic_edge_count": heuristic_edge_count,
        "heuristic_without_review": heuristic_without_review,
        "blockers": blockers,
        "artifact_refs": artifact_refs,
        "created_at": now(),
    }


def _forbidden_edge_scan(workspace_id: str, codebase_id: str, snapshot_id: str, chains: list[dict[str, Any]]) -> dict[str, Any]:
    forbidden = []
    unsupported = []
    for chain in chains:
        for edge in chain.get("edges", []):
            if edge.get("edge_type") in FORBIDDEN_EDGE_TYPES:
                forbidden.append({"chain_id": chain.get("chain_id"), "edge_id": edge.get("edge_id"), "edge_type": edge.get("edge_type")})
            if edge.get("edge_type") not in ALLOWED_EDGE_TYPES:
                unsupported.append({"chain_id": chain.get("chain_id"), "edge_id": edge.get("edge_id"), "edge_type": edge.get("edge_type")})
    return {
        "schema_version": SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "forbidden_edge_count": len(forbidden),
        "unsupported_edge_count": len(unsupported),
        "forbidden_edges": forbidden,
        "unsupported_edges": unsupported,
        "allowed_edge_types": sorted(ALLOWED_EDGE_TYPES),
        "forbidden_edge_types": sorted(FORBIDDEN_EDGE_TYPES),
        "created_at": now(),
    }


def _symbols_by_path(symbols: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    by_path: dict[str, list[dict[str, Any]]] = {}
    for symbol in symbols:
        path = str(symbol.get("path") or symbol.get("source_file") or "")
        if path:
            by_path.setdefault(path, []).append(symbol)
    return by_path


def _refs_by_path(refs: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    by_path: dict[str, list[dict[str, Any]]] = {}
    for ref in refs:
        path = str(ref.get("path") or "")
        if path:
            by_path.setdefault(path, []).append(ref)
    return by_path


def _tests_by_stem(files: list[dict[str, Any]]) -> dict[str, list[str]]:
    tests: dict[str, list[str]] = {}
    for item in files:
        path = str(item.get("path") or "")
        if "test" not in path.lower():
            continue
        stem = PurePosixPath(path).stem.replace("test_", "").replace("_test", "")
        if stem:
            tests.setdefault(stem, []).append(path)
    return tests


def _best_symbol(source_file: str, surface: dict[str, Any], symbol_by_path: dict[str, list[dict[str, Any]]]) -> dict[str, Any] | None:
    candidates = symbol_by_path.get(source_file, [])
    if not candidates:
        return None
    line_range = surface.get("line_range") or []
    if isinstance(line_range, list) and len(line_range) == 2:
        for symbol in candidates:
            raw = symbol.get("line_range") or []
            if isinstance(raw, list) and len(raw) == 2 and int(raw[0]) <= int(line_range[0]) <= int(raw[1]):
                return symbol
    return candidates[0]


def _compact_evidence(edges: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen = set()
    refs = []
    for edge in edges:
        for ref in edge.get("evidence_refs", []):
            key = repr(sorted(ref.items())) if isinstance(ref, dict) else repr(ref)
            if key in seen:
                continue
            seen.add(key)
            refs.append(ref)
            if len(refs) >= 12:
                return refs
    return refs


def _completeness(nodes: list[dict[str, Any]], edges: list[dict[str, Any]]) -> float:
    types = {node.get("node_type") for node in nodes}
    score = 0.2
    for required in ("entrypoint", "entrypoint_candidate", "handler", "module", "dependency_reference", "test", "doc_claim"):
        if required in types:
            score += 0.13
    if edges:
        score += 0.15
    return round(min(1.0, score), 3)


def _dedupe_nodes(nodes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen = set()
    out = []
    for node in nodes:
        node_id = node.get("node_id")
        if node_id in seen:
            continue
        seen.add(node_id)
        out.append(node)
    return out


def _dedupe_chains(chains: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen = set()
    out = []
    for chain in chains:
        chain_id = chain.get("chain_id")
        if not chain_id or chain_id in seen:
            continue
        seen.add(chain_id)
        out.append(chain)
    return out


def _stable_id(*parts: Any) -> str:
    return hashlib.sha256("::".join(str(part) for part in parts).encode("utf-8")).hexdigest()[:24]
