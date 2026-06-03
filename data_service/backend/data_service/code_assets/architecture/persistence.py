"""Persistence helpers for V2.3 architecture artifacts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from data_service.mcp_common import read_json, write_json

from ..artifacts import (
    architecture_alignment_path,
    architecture_code_layers_path,
    architecture_code_boundaries_path,
    architecture_code_derived_model_path,
    architecture_code_roles_path,
    architecture_design_code_drift_path,
    architecture_pattern_candidates_path,
    architecture_design_edges_path,
    architecture_design_nodes_path,
    architecture_findings_path,
    architecture_model_path,
    architecture_sources_path,
    architecture_summary_path,
    architecture_view_path,
    read_jsonl,
    write_jsonl,
)


def architecture_artifact_refs(codebase_id: str) -> list[dict[str, str]]:
    return [
        {"type": "architecture_sources", "artifact_ref": f"architecture://{codebase_id}/sources"},
        {"type": "architecture_model", "artifact_ref": f"architecture://{codebase_id}/model"},
        {"type": "architecture_alignment", "artifact_ref": f"architecture://{codebase_id}/alignment"},
        {"type": "architecture_findings", "artifact_ref": f"architecture://{codebase_id}/findings"},
        {"type": "architecture_summary", "artifact_ref": f"architecture://{codebase_id}/summary"},
        {"type": "architecture_view_mermaid", "artifact_ref": f"architecture://{codebase_id}/views/architecture.mmd"},
        {"type": "architecture_view_html", "artifact_ref": f"architecture://{codebase_id}/views/architecture.html"},
    ]


def code_architecture_artifact_refs(codebase_id: str) -> list[dict[str, str]]:
    return [
        {"type": "code_architecture_roles", "artifact_ref": f"architecture://{codebase_id}/code_roles.jsonl"},
        {"type": "code_architecture_layers", "artifact_ref": f"architecture://{codebase_id}/code_layers.jsonl"},
        {"type": "code_architecture_boundaries", "artifact_ref": f"architecture://{codebase_id}/code_boundaries.jsonl"},
        {"type": "architecture_pattern_candidates", "artifact_ref": f"architecture://{codebase_id}/pattern_candidates.jsonl"},
        {"type": "code_derived_architecture_model", "artifact_ref": f"architecture://{codebase_id}/code_derived_model.json"},
        {"type": "design_code_drift", "artifact_ref": f"architecture://{codebase_id}/design_code_drift.jsonl"},
    ]


def write_architecture_bundle(workspace: Path, codebase_id: str, bundle: dict[str, Any], mermaid: str, html: str) -> None:
    write_jsonl(architecture_sources_path(workspace, codebase_id), bundle["sources"])
    write_jsonl(architecture_design_nodes_path(workspace, codebase_id), bundle["design_nodes"])
    write_jsonl(architecture_design_edges_path(workspace, codebase_id), bundle["design_edges"])
    write_json(architecture_model_path(workspace, codebase_id), bundle["model"])
    write_json(architecture_alignment_path(workspace, codebase_id), bundle["alignment"])
    write_jsonl(architecture_findings_path(workspace, codebase_id), bundle["findings"])
    write_json(architecture_summary_path(workspace, codebase_id), bundle["summary"])
    mmd = architecture_view_path(workspace, codebase_id, "architecture.mmd")
    page = architecture_view_path(workspace, codebase_id, "architecture.html")
    mmd.parent.mkdir(parents=True, exist_ok=True)
    mmd.write_text(mermaid, encoding="utf-8")
    page.write_text(html, encoding="utf-8")


def write_code_architecture_roles_layers(
    workspace: Path,
    codebase_id: str,
    roles: list[dict[str, Any]],
    layers: list[dict[str, Any]],
    boundaries: list[dict[str, Any]] | None = None,
    patterns: list[dict[str, Any]] | None = None,
    code_model: dict[str, Any] | None = None,
    drift: list[dict[str, Any]] | None = None,
) -> None:
    write_jsonl(architecture_code_roles_path(workspace, codebase_id), roles)
    write_jsonl(architecture_code_layers_path(workspace, codebase_id), layers)
    if boundaries is not None:
        write_jsonl(architecture_code_boundaries_path(workspace, codebase_id), boundaries)
    if patterns is not None:
        write_jsonl(architecture_pattern_candidates_path(workspace, codebase_id), patterns)
    if code_model is not None:
        write_json(architecture_code_derived_model_path(workspace, codebase_id), code_model)
    if drift is not None:
        write_jsonl(architecture_design_code_drift_path(workspace, codebase_id), drift)


def read_architecture_bundle(workspace: Path, codebase_id: str) -> dict[str, Any]:
    model = read_json(architecture_model_path(workspace, codebase_id), None)
    if not model:
        raise FileNotFoundError("ARCHITECTURE_MODEL_NOT_BUILT")
    return {
        "sources": read_jsonl(architecture_sources_path(workspace, codebase_id)),
        "design_nodes": read_jsonl(architecture_design_nodes_path(workspace, codebase_id)),
        "design_edges": read_jsonl(architecture_design_edges_path(workspace, codebase_id)),
        "model": model,
        "alignment": read_json(architecture_alignment_path(workspace, codebase_id), {}),
        "findings": read_jsonl(architecture_findings_path(workspace, codebase_id)),
        "summary": read_json(architecture_summary_path(workspace, codebase_id), {}),
    }


def read_code_architecture_roles_layers(workspace: Path, codebase_id: str) -> dict[str, Any]:
    roles = read_jsonl(architecture_code_roles_path(workspace, codebase_id))
    layers = read_jsonl(architecture_code_layers_path(workspace, codebase_id))
    if not roles and not layers:
        raise FileNotFoundError("CODE_ARCHITECTURE_NOT_BUILT")
    return {
        "roles": roles,
        "layers": layers,
        "boundaries": read_jsonl(architecture_code_boundaries_path(workspace, codebase_id)),
        "patterns": read_jsonl(architecture_pattern_candidates_path(workspace, codebase_id)),
        "code_model": read_json(architecture_code_derived_model_path(workspace, codebase_id), {}),
        "drift": read_jsonl(architecture_design_code_drift_path(workspace, codebase_id)),
    }


def read_architecture_view(workspace: Path, codebase_id: str, view_id: str) -> str:
    path = architecture_view_path(workspace, codebase_id, view_id)
    if not path.exists():
        raise FileNotFoundError("ARCHITECTURE_VIEW_NOT_FOUND")
    return path.read_text(encoding="utf-8")
