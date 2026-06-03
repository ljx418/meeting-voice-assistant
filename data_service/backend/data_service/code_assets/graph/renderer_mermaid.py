"""Mermaid renderer for V2.1 Code Graph."""

from __future__ import annotations

import re
from typing import Any


def render_mermaid(nodes: list[dict[str, Any]], edges: list[dict[str, Any]], *, max_edges: int = 80) -> str:
    node_index = {item["node_id"]: item for item in nodes}
    lines = ["flowchart TD"]
    used_nodes = set()
    for edge in edges[:max_edges]:
        if edge["from_id"] not in node_index or edge["to_id"] not in node_index:
            continue
        used_nodes.add(edge["from_id"])
        used_nodes.add(edge["to_id"])
    for node_id in sorted(used_nodes):
        item = node_index[node_id]
        lines.append(f"  {safe_id(node_id)}[{_label(item)}]")
    for edge in edges[:max_edges]:
        if edge["from_id"] in used_nodes and edge["to_id"] in used_nodes:
            lines.append(f"  {safe_id(edge['from_id'])} -->|{edge['relation']}| {safe_id(edge['to_id'])}")
    return "\n".join(lines) + "\n"


def safe_id(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_]", "_", value)


def _label(node: dict[str, Any]) -> str:
    label = str(node.get("label") or node.get("node_type") or "node")
    label = label.replace("[", "(").replace("]", ")").replace("|", "/")
    if "/" in label:
        label = label.split("/")[-1]
    return label[:80]
