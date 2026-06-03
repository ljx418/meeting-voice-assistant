"""V2.4 code-derived architecture model helpers."""

from __future__ import annotations

from typing import Any

from .model import stable_id


CODE_ARCHITECTURE_SCHEMA_VERSION = "v2.4"

ROLE_TYPES = {
    "api_router",
    "mcp_tooling",
    "cli_tooling",
    "frontend",
    "service",
    "domain",
    "runtime",
    "provider",
    "storage",
    "policy",
    "governance",
    "build_pipeline",
    "artifact_store",
    "test",
    "script",
    "docs",
    "unknown",
}

LAYER_TYPES = {
    "interface",
    "application",
    "domain",
    "infrastructure",
    "governance",
    "runtime",
    "artifact",
    "test",
    "docs",
    "unknown",
}

BOUNDARY_TYPES = {
    "package",
    "bounded_context_candidate",
    "adapter_boundary",
    "governance_boundary",
    "storage_boundary",
    "public_surface_boundary",
}

PATTERN_TYPES = {
    "fastapi_router",
    "mcp_registry",
    "cli_command_group",
    "provider_adapter",
    "artifact_store",
    "pipeline",
    "quality_gate",
    "context_pack",
    "devwiki",
    "code_graph",
    "architecture_alignment",
}


def evidence_from_path(path: str, *, line_range: list[int] | None = None, source: str = "code_architecture_inference") -> list[dict[str, Any]]:
    evidence: dict[str, Any] = {"path": path, "source": source}
    if line_range:
        evidence["line_range"] = list(line_range)
    return [evidence]


def code_architecture_role(
    *,
    workspace_id: str,
    codebase_id: str,
    snapshot_id: str,
    role_type: str,
    target_type: str,
    target_id: str,
    name: str,
    path: str | None,
    signals: list[str],
    evidence: list[dict[str, Any]],
    confidence: float,
    needs_review: list[dict[str, Any]] | None = None,
    source_artifact_refs: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    if role_type not in ROLE_TYPES:
        raise ValueError(f"UNSUPPORTED_CODE_ARCHITECTURE_ROLE:{role_type}")
    return {
        "schema_version": CODE_ARCHITECTURE_SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "role_id": stable_id("coderole", snapshot_id, role_type, target_type, target_id),
        "role_type": role_type,
        "target_type": target_type,
        "target_id": target_id,
        "name": name,
        "path": path,
        "signals": list(signals),
        "evidence": list(evidence),
        "confidence": float(confidence),
        "needs_review": list(needs_review or []),
        "source_artifact_refs": list(source_artifact_refs or []),
    }


def code_architecture_layer(
    *,
    workspace_id: str,
    codebase_id: str,
    snapshot_id: str,
    layer_type: str,
    members: list[dict[str, Any]],
    signals: list[str],
    evidence: list[dict[str, Any]],
    confidence: float,
    needs_review: list[dict[str, Any]] | None = None,
    source_artifact_refs: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    if layer_type not in LAYER_TYPES:
        raise ValueError(f"UNSUPPORTED_CODE_ARCHITECTURE_LAYER:{layer_type}")
    return {
        "schema_version": CODE_ARCHITECTURE_SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "layer_id": stable_id("codelayer", snapshot_id, layer_type),
        "layer_type": layer_type,
        "members": list(members),
        "signals": list(signals),
        "evidence": list(evidence),
        "confidence": float(confidence),
        "needs_review": list(needs_review or []),
        "source_artifact_refs": list(source_artifact_refs or []),
    }


def code_architecture_boundary(
    *,
    workspace_id: str,
    codebase_id: str,
    snapshot_id: str,
    boundary_type: str,
    name: str,
    members: list[dict[str, Any]],
    signals: list[str],
    evidence: list[dict[str, Any]],
    confidence: float,
    needs_review: list[dict[str, Any]] | None = None,
    source_artifact_refs: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    if boundary_type not in BOUNDARY_TYPES:
        raise ValueError(f"UNSUPPORTED_CODE_ARCHITECTURE_BOUNDARY:{boundary_type}")
    return {
        "schema_version": CODE_ARCHITECTURE_SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "boundary_id": stable_id("codeboundary", snapshot_id, boundary_type, name),
        "boundary_type": boundary_type,
        "name": name,
        "members": list(members),
        "signals": list(signals),
        "evidence": list(evidence),
        "confidence": float(confidence),
        "needs_review": list(needs_review or []),
        "source_artifact_refs": list(source_artifact_refs or []),
    }


def architecture_pattern_candidate(
    *,
    workspace_id: str,
    codebase_id: str,
    snapshot_id: str,
    pattern_type: str,
    name: str,
    targets: list[dict[str, Any]],
    signals: list[str],
    evidence: list[dict[str, Any]],
    confidence: float,
    needs_review: list[dict[str, Any]] | None = None,
    source_artifact_refs: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    if pattern_type not in PATTERN_TYPES:
        raise ValueError(f"UNSUPPORTED_ARCHITECTURE_PATTERN:{pattern_type}")
    return {
        "schema_version": CODE_ARCHITECTURE_SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "pattern_id": stable_id("codepattern", snapshot_id, pattern_type, name),
        "pattern_type": pattern_type,
        "name": name,
        "targets": list(targets),
        "signals": list(signals),
        "evidence": list(evidence),
        "confidence": float(confidence),
        "needs_review": list(needs_review or []),
        "source_artifact_refs": list(source_artifact_refs or []),
    }
