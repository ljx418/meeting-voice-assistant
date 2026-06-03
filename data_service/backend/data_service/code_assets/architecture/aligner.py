"""Design-code alignment for V2.3 architecture models."""

from __future__ import annotations

import re
from collections import Counter
from typing import Any

from .model import ARCHITECTURE_SCHEMA_VERSION, stable_id


MATCH_NODE_TYPES = {"Capability", "HTTPRoute", "MCPTool", "CLICommand", "FrontendPage", "Module", "Class", "Function", "File", "DevWikiPage"}


def align_architecture_model(*, workspace_id: str, codebase_id: str, snapshot_id: str, design_nodes: list[dict[str, Any]], graph: dict[str, Any] | None) -> dict[str, Any]:
    graph_nodes = [node for node in (graph or {}).get("nodes", []) if node.get("node_type") in MATCH_NODE_TYPES]
    index = _token_index(graph_nodes)
    matches = []
    unmatched_design = []
    matched_graph_ids = set()
    for design in design_nodes:
        candidate = _best_match(design, graph_nodes, index)
        if candidate:
            graph_node, score = candidate
            matched_graph_ids.add(graph_node["node_id"])
            matches.append(
                {
                    "alignment_id": stable_id("archalign", snapshot_id, design["node_id"], graph_node["node_id"]),
                    "design_node_id": design["node_id"],
                    "design_label": design["label"],
                    "design_node_type": design["node_type"],
                    "code_node_id": graph_node["node_id"],
                    "code_label": graph_node.get("label"),
                    "code_node_type": graph_node.get("node_type"),
                    "confidence": score,
                    "evidence": design.get("evidence", []),
                    "needs_review": [] if score >= 0.75 else [{"code": "LOW_CONFIDENCE_MAPPING", "reason": "Textual match requires review."}],
                }
            )
        elif design.get("node_type") not in {"System", "Milestone", "ForbiddenClaim"}:
            unmatched_design.append({"design_node_id": design["node_id"], "label": design["label"], "node_type": design["node_type"], "needs_review": [{"code": "DESIGN_NOT_FOUND_IN_CODE", "reason": "No matching Code Graph node was found."}]})
    code_only = [node for node in graph_nodes if node["node_id"] not in matched_graph_ids][:100]
    summary = {
        "schema_version": ARCHITECTURE_SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "match_count": len(matches),
        "unmatched_design_count": len(unmatched_design),
        "code_only_sample_count": len(code_only),
        "match_counts_by_design_type": dict(sorted(Counter(item["design_node_type"] for item in matches).items())),
    }
    return {"schema_version": ARCHITECTURE_SCHEMA_VERSION, "workspace_id": workspace_id, "codebase_id": codebase_id, "snapshot_id": snapshot_id, "summary": summary, "matches": matches, "unmatched_design": unmatched_design, "code_only_sample": _public_code_nodes(code_only)}


def _best_match(design: dict[str, Any], graph_nodes: list[dict[str, Any]], index: dict[str, set[int]]) -> tuple[dict[str, Any], float] | None:
    tokens = _tokens(str(design.get("label") or ""))
    if not tokens:
        return None
    candidate_indexes: set[int] = set()
    for token in tokens:
        candidate_indexes.update(index.get(token, set()))
    if not candidate_indexes:
        return None
    best: tuple[dict[str, Any], float] | None = None
    for idx in candidate_indexes:
        node = graph_nodes[idx]
        haystack = " ".join([str(node.get("label") or ""), str(node.get("natural_id") or ""), str(node.get("data", {}).get("path") or "")])
        node_tokens = _tokens(haystack)
        if not node_tokens:
            continue
        overlap = len(tokens & node_tokens)
        if overlap == 0:
            continue
        score = min(0.95, overlap / max(len(tokens), 1))
        if score >= 0.45 and (best is None or score > best[1]):
            best = (node, score)
    return best


def _token_index(graph_nodes: list[dict[str, Any]]) -> dict[str, set[int]]:
    index: dict[str, set[int]] = {}
    for idx, node in enumerate(graph_nodes):
        haystack = " ".join([str(node.get("label") or ""), str(node.get("natural_id") or ""), str(node.get("data", {}).get("path") or "")])
        for token in _tokens(haystack):
            index.setdefault(token, set()).add(idx)
    return index


def _tokens(value: str) -> set[str]:
    raw = re.findall(r"[A-Za-z][A-Za-z0-9_]{2,}|[\u4e00-\u9fff]{2,}", value.lower())
    stop = {"the", "and", "for", "with", "current", "target", "complete", "phase", "plane"}
    return {item for item in raw if item not in stop}


def _public_code_nodes(nodes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [{"node_id": node.get("node_id"), "node_type": node.get("node_type"), "label": node.get("label"), "natural_id": node.get("natural_id")} for node in nodes]
