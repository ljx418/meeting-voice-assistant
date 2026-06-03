"""Neighbor reader for V2.1 Code Graph."""

from __future__ import annotations

from typing import Any


def neighbors(graph: dict[str, Any], node_id: str, *, depth: int = 1, limit: int = 100) -> dict[str, Any]:
    node_index = {item["node_id"]: item for item in graph.get("nodes", [])}
    if node_id not in node_index:
        raise FileNotFoundError("GRAPH_NODE_NOT_FOUND")
    edges = list(graph.get("edges", []))
    frontier = {node_id}
    seen_nodes = {node_id}
    selected_edges = []
    for _ in range(max(1, min(depth, 3))):
        next_frontier = set()
        for edge in edges:
            if edge["from_id"] in frontier or edge["to_id"] in frontier:
                selected_edges.append(edge)
                next_frontier.add(edge["from_id"])
                next_frontier.add(edge["to_id"])
        frontier = next_frontier - seen_nodes
        seen_nodes |= next_frontier
        if len(selected_edges) >= limit:
            break
    selected_edges = selected_edges[:limit]
    selected_node_ids = {node_id}
    for edge in selected_edges:
        selected_node_ids.add(edge["from_id"])
        selected_node_ids.add(edge["to_id"])
    return {
        "center": node_index[node_id],
        "nodes": [node_index[item] for item in sorted(selected_node_ids) if item in node_index],
        "edges": selected_edges,
        "unresolved": [],
    }
