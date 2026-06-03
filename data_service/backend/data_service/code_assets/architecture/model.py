"""Model helpers for V2.3 Architecture Abstraction."""

from __future__ import annotations

import hashlib
from typing import Any


ARCHITECTURE_SCHEMA_VERSION = "v2.3"
SUPPORTED_ARCH_RELATIONS = {
    "CONTAINS",
    "DEPENDS_ON",
    "EXPOSES",
    "ADAPTS_TO",
    "PRODUCES",
    "CONSUMES",
    "GOVERNED_BY",
    "DOCUMENTS",
    "IMPLEMENTS",
    "VERIFIED_BY",
    "CONFLICTS_WITH",
}


def stable_id(prefix: str, *parts: object) -> str:
    raw = "|".join(str(part or "") for part in parts)
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:20]
    return f"{prefix}_{digest}"


def architecture_source(*, workspace_id: str, codebase_id: str, snapshot_id: str, path: str, source_type: str, parser: str, evidence: list[dict[str, Any]], confidence: float = 1.0) -> dict[str, Any]:
    return {
        "schema_version": ARCHITECTURE_SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "source_id": stable_id("archsrc", snapshot_id, path, source_type),
        "path": path,
        "source_type": source_type,
        "parser": parser,
        "evidence": evidence,
        "confidence": float(confidence),
    }


def architecture_node(*, workspace_id: str, codebase_id: str, snapshot_id: str, natural_id: str, node_type: str, label: str, source_id: str, source_path: str, status: str = "unknown", evidence: list[dict[str, Any]] | None = None, needs_review: list[dict[str, Any]] | None = None, confidence: float = 0.8, data: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        "schema_version": ARCHITECTURE_SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "node_id": stable_id("archnode", snapshot_id, node_type, natural_id),
        "natural_id": natural_id,
        "node_type": node_type,
        "label": label,
        "status": status,
        "source_id": source_id,
        "source_path": source_path,
        "evidence": list(evidence or []),
        "needs_review": list(needs_review or []),
        "confidence": float(confidence),
        "data": dict(data or {}),
    }


def architecture_edge(*, workspace_id: str, codebase_id: str, snapshot_id: str, relation: str, from_id: str, to_id: str, source_id: str, evidence: list[dict[str, Any]] | None = None, needs_review: list[dict[str, Any]] | None = None, confidence: float = 0.8, data: dict[str, Any] | None = None) -> dict[str, Any]:
    if relation not in SUPPORTED_ARCH_RELATIONS:
        raise ValueError(f"UNSUPPORTED_ARCH_RELATION:{relation}")
    return {
        "schema_version": ARCHITECTURE_SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "edge_id": stable_id("archedge", snapshot_id, relation, from_id, to_id, source_id),
        "relation": relation,
        "from_id": from_id,
        "to_id": to_id,
        "source_id": source_id,
        "evidence": list(evidence or []),
        "needs_review": list(needs_review or []),
        "confidence": float(confidence),
        "data": dict(data or {}),
    }
