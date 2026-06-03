"""Aggregate code-derived architecture model for V2.4."""

from __future__ import annotations

from typing import Any


def build_code_derived_model(
    *,
    workspace_id: str,
    codebase_id: str,
    snapshot_id: str,
    roles: list[dict[str, Any]],
    layers: list[dict[str, Any]],
    boundaries: list[dict[str, Any]],
    patterns: list[dict[str, Any]],
    summary: dict[str, Any],
    source_artifact_refs: list[dict[str, str]],
) -> dict[str, Any]:
    return {
        "schema_version": "v2.4",
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "model_id": f"code_derived_architecture:{codebase_id}:{snapshot_id}",
        "roles": roles,
        "layers": layers,
        "boundaries": boundaries,
        "patterns": patterns,
        "summary": summary,
        "source_artifact_refs": list(source_artifact_refs),
    }
