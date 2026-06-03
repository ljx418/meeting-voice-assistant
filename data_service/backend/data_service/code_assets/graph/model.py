"""Model helpers for V2.1 Code Graph."""

from __future__ import annotations

import hashlib
from typing import Any


GRAPH_SCHEMA_VERSION = "v2.1"
SUPPORTED_RELATIONS = {
    "CONTAINS",
    "DEFINES",
    "IMPORTS",
    "EXPOSES_ROUTE",
    "REGISTERS_MCP_TOOL",
    "EXPOSES_CLI_COMMAND",
    "HANDLED_BY",
    "IMPLEMENTS_CAPABILITY",
    "DOCUMENTED_BY",
    "EVIDENCED_BY",
    "GENERATED_FROM",
}
UNSUPPORTED_RELATIONS = {"CALLS", "DATA_FLOW", "CONTROL_FLOW", "RUNTIME_TRACE", "TYPE_INFERRED"}


def stable_id(prefix: str, *parts: object) -> str:
    raw = "|".join(str(part or "") for part in parts)
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:20]
    return f"{prefix}_{digest}"


def node(node_type: str, natural_id: str, *, label: str, snapshot_id: str, data: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        "node_id": stable_id("node", snapshot_id, node_type, natural_id),
        "node_type": node_type,
        "natural_id": natural_id,
        "label": label,
        "snapshot_id": snapshot_id,
        "data": dict(data or {}),
    }


def edge(
    relation: str,
    from_id: str,
    to_id: str,
    *,
    snapshot_id: str,
    extractor: str,
    evidence: list[dict[str, Any]] | None = None,
    needs_review: list[dict[str, Any]] | None = None,
    confidence: float = 1.0,
) -> dict[str, Any]:
    if relation not in SUPPORTED_RELATIONS:
        raise ValueError(f"UNSUPPORTED_EDGE_TYPE:{relation}")
    return {
        "edge_id": stable_id("edge", snapshot_id, relation, from_id, to_id),
        "from_id": from_id,
        "to_id": to_id,
        "relation": relation,
        "snapshot_id": snapshot_id,
        "extractor": extractor,
        "confidence": float(confidence),
        "evidence": list(evidence or []),
        "needs_review": list(needs_review or []),
    }
