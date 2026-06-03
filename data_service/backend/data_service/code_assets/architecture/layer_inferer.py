"""Layer inference for V2.4 code-derived architecture roles."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from .code_model import code_architecture_layer


ROLE_TO_LAYER = {
    "api_router": "interface",
    "mcp_tooling": "interface",
    "cli_tooling": "interface",
    "frontend": "interface",
    "service": "application",
    "domain": "domain",
    "provider": "infrastructure",
    "storage": "infrastructure",
    "policy": "governance",
    "governance": "governance",
    "runtime": "runtime",
    "build_pipeline": "runtime",
    "artifact_store": "artifact",
    "test": "test",
    "script": "test",
    "docs": "docs",
    "unknown": "unknown",
}


def infer_layers(
    *,
    workspace_id: str,
    codebase_id: str,
    snapshot_id: str,
    roles: list[dict[str, Any]],
    source_artifact_refs: list[dict[str, str]],
) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for role in roles:
        grouped[ROLE_TO_LAYER.get(str(role.get("role_type")), "unknown")].append(role)
    layers: list[dict[str, Any]] = []
    for layer_type in sorted(grouped):
        members = [
            {
                "role_id": role.get("role_id"),
                "role_type": role.get("role_type"),
                "target_type": role.get("target_type"),
                "target_id": role.get("target_id"),
                "name": role.get("name"),
                "path": role.get("path"),
            }
            for role in grouped[layer_type]
        ]
        evidence = _first_evidence(grouped[layer_type])
        needs_review = []
        confidence_values = [float(role.get("confidence") or 0) for role in grouped[layer_type]]
        confidence = min(0.95, sum(confidence_values) / max(1, len(confidence_values)))
        if layer_type == "unknown":
            needs_review.append({"reason": "layer_contains_unknown_roles"})
            confidence = min(confidence, 0.3)
        layers.append(
            code_architecture_layer(
                workspace_id=workspace_id,
                codebase_id=codebase_id,
                snapshot_id=snapshot_id,
                layer_type=layer_type,
                members=members,
                signals=[f"roles:{len(members)}", f"layer:{layer_type}"],
                evidence=evidence,
                confidence=confidence,
                needs_review=needs_review,
                source_artifact_refs=source_artifact_refs,
            )
        )
    return layers


def _first_evidence(roles: list[dict[str, Any]]) -> list[dict[str, Any]]:
    evidence: list[dict[str, Any]] = []
    seen: set[str] = set()
    for role in roles:
        for item in role.get("evidence") or []:
            if not isinstance(item, dict):
                continue
            key = f"{item.get('path')}:{item.get('line_range')}"
            if key in seen:
                continue
            seen.add(key)
            evidence.append(dict(item))
            if len(evidence) >= 20:
                return evidence
    return evidence
