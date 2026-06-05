"""V2.6 architecture scale profile builder."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from data_service.mcp_common import now, read_json

from ..artifacts import (
    architecture_alignment_path,
    architecture_code_boundaries_path,
    architecture_code_derived_model_path,
    architecture_code_layers_path,
    architecture_code_roles_path,
    architecture_config_inventory_path,
    architecture_design_code_drift_path,
    architecture_deployment_inventory_path,
    architecture_findings_path,
    architecture_language_facts_path,
    architecture_model_path,
    architecture_pattern_candidates_path,
    architecture_scale_profile_path,
    architecture_schema_inventory_path,
    architecture_sources_path,
    architecture_summary_path,
    code_graph_json_path,
    codebase_json_path,
    devwiki_index_path,
    evidence_path,
    imports_path,
    inventory_capabilities_path,
    inventory_surfaces_path,
    mappings_path,
    overview_path,
    read_jsonl,
    snapshot_files_path,
    snapshot_json_path,
    symbols_path,
)


SCHEMA_VERSION = "v2.6"
SUMMARY_MODE_FILE_COUNT = 5000
SUMMARY_MODE_LOC_TOTAL = 100000
SUMMARY_MODE_ARTIFACT_BYTES = 1_048_576


def build_architecture_scale_profile(
    *,
    workspace: Path,
    workspace_id: str,
    codebase_id: str,
    snapshot_id: str,
    snapshot: dict[str, Any],
    files: list[dict[str, Any]],
) -> dict[str, Any]:
    artifact_paths = _artifact_paths(workspace, codebase_id, snapshot_id)
    artifact_sizes = _artifact_sizes(artifact_paths)
    warning_counts = _warning_counts(workspace, codebase_id, snapshot_id)
    confidence_distribution = _confidence_distribution(workspace, codebase_id)
    needs_review_count = confidence_distribution["needs_review"]
    stats = snapshot.get("stats") if isinstance(snapshot.get("stats"), dict) else {}
    file_count = int(stats.get("file_count") or len([item for item in files if item.get("included")]))
    loc_total = int(stats.get("loc_total") or sum(int(item.get("loc") or 0) for item in files if item.get("included")))
    language_distribution = dict(stats.get("languages") or _language_distribution(files))
    skipped_paths = [
        {"path": item.get("path"), "skip_reason": item.get("skip_reason")}
        for item in files
        if item.get("skip_reason")
    ][:100]
    largest_artifact_bytes = max(artifact_sizes.values(), default=0)
    summary_mode_required = (
        file_count >= SUMMARY_MODE_FILE_COUNT
        or loc_total >= SUMMARY_MODE_LOC_TOTAL
        or largest_artifact_bytes >= SUMMARY_MODE_ARTIFACT_BYTES
    )
    profile = {
        "schema_version": SCHEMA_VERSION,
        "profile_id": f"scale:{workspace_id}:{codebase_id}:{snapshot_id}",
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "file_count": file_count,
        "loc_total": loc_total,
        "language_distribution": language_distribution,
        "artifact_sizes": artifact_sizes,
        "build_durations": {},
        "warning_counts": warning_counts,
        "skipped_paths": skipped_paths,
        "confidence_distribution": confidence_distribution,
        "needs_review_count": needs_review_count,
        "summary_mode_required": summary_mode_required,
        "thresholds": {
            "summary_mode_file_count": SUMMARY_MODE_FILE_COUNT,
            "summary_mode_loc_total": SUMMARY_MODE_LOC_TOTAL,
            "summary_mode_artifact_bytes": SUMMARY_MODE_ARTIFACT_BYTES,
        },
        "source_artifact_refs": _source_artifact_refs(codebase_id, snapshot_id),
        "artifact_refs": architecture_scale_artifact_refs(codebase_id),
        "artifact_hashes": _artifact_hashes(artifact_paths),
        "warnings": [],
        "redaction": {"applied": True, "redaction_count": 0},
        "created_at": now(),
    }
    return profile


def public_scale_profile_payload(profile: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": profile.get("schema_version"),
        "profile_id": profile.get("profile_id"),
        "workspace_id": profile.get("workspace_id"),
        "codebase_id": profile.get("codebase_id"),
        "snapshot_id": profile.get("snapshot_id"),
        "file_count": profile.get("file_count", 0),
        "loc_total": profile.get("loc_total", 0),
        "language_distribution": profile.get("language_distribution", {}),
        "artifact_sizes": profile.get("artifact_sizes", {}),
        "warning_counts": profile.get("warning_counts", {}),
        "skipped_path_count": len(profile.get("skipped_paths") or []),
        "skipped_paths_sample": list(profile.get("skipped_paths") or [])[:20],
        "confidence_distribution": profile.get("confidence_distribution", {}),
        "needs_review_count": profile.get("needs_review_count", 0),
        "summary_mode_required": bool(profile.get("summary_mode_required")),
        "thresholds": profile.get("thresholds", {}),
        "source_artifact_refs": profile.get("source_artifact_refs", []),
        "artifact_refs": architecture_scale_artifact_refs(str(profile.get("codebase_id") or "")),
        "warnings": profile.get("warnings", []),
        "redaction": profile.get("redaction", {"applied": True, "redaction_count": 0}),
        "truncated": bool(profile.get("summary_mode_required")),
    }


def architecture_scale_artifact_refs(codebase_id: str) -> list[dict[str, str]]:
    return [{"type": "architecture_scale_profile", "artifact_ref": f"architecture://{codebase_id}/architecture_scale_profile.json"}]


def read_scale_profile(workspace: Path, codebase_id: str) -> dict[str, Any]:
    payload = read_json(architecture_scale_profile_path(workspace, codebase_id), None)
    if not payload:
        raise FileNotFoundError("ARCHITECTURE_SCALE_PROFILE_NOT_BUILT")
    return payload


def _artifact_paths(workspace: Path, codebase_id: str, snapshot_id: str) -> dict[str, Path]:
    return {
        "codebase": codebase_json_path(workspace, codebase_id),
        "snapshot": snapshot_json_path(workspace, codebase_id, snapshot_id),
        "snapshot_files": snapshot_files_path(workspace, codebase_id, snapshot_id),
        "inventory_surfaces": inventory_surfaces_path(workspace, codebase_id, snapshot_id),
        "inventory_capabilities": inventory_capabilities_path(workspace, codebase_id, snapshot_id),
        "symbols": symbols_path(workspace, codebase_id, snapshot_id),
        "imports": imports_path(workspace, codebase_id, snapshot_id),
        "evidence": evidence_path(workspace, codebase_id, snapshot_id),
        "mappings": mappings_path(workspace, codebase_id, snapshot_id),
        "overview": overview_path(workspace, codebase_id),
        "devwiki_index": devwiki_index_path(workspace, codebase_id),
        "graph": code_graph_json_path(workspace, codebase_id),
        "architecture_sources": architecture_sources_path(workspace, codebase_id),
        "architecture_model": architecture_model_path(workspace, codebase_id),
        "architecture_alignment": architecture_alignment_path(workspace, codebase_id),
        "architecture_findings": architecture_findings_path(workspace, codebase_id),
        "architecture_summary": architecture_summary_path(workspace, codebase_id),
        "code_architecture_roles": architecture_code_roles_path(workspace, codebase_id),
        "code_architecture_layers": architecture_code_layers_path(workspace, codebase_id),
        "code_architecture_boundaries": architecture_code_boundaries_path(workspace, codebase_id),
        "architecture_pattern_candidates": architecture_pattern_candidates_path(workspace, codebase_id),
        "code_derived_architecture_model": architecture_code_derived_model_path(workspace, codebase_id),
        "design_code_drift": architecture_design_code_drift_path(workspace, codebase_id),
        "architecture_language_facts": architecture_language_facts_path(workspace, codebase_id),
        "architecture_config_inventory": architecture_config_inventory_path(workspace, codebase_id),
        "architecture_deployment_inventory": architecture_deployment_inventory_path(workspace, codebase_id),
        "architecture_schema_inventory": architecture_schema_inventory_path(workspace, codebase_id),
    }


def _artifact_sizes(paths: dict[str, Path]) -> dict[str, int]:
    return {name: path.stat().st_size for name, path in sorted(paths.items()) if path.exists() and path.is_file()}


def _artifact_hashes(paths: dict[str, Path]) -> dict[str, str]:
    hashes: dict[str, str] = {}
    for name, path in sorted(paths.items()):
        if path.exists() and path.is_file():
            hashes[name] = hashlib.sha256(path.read_bytes()).hexdigest()
        else:
            hashes[name] = "missing_before"
    return hashes


def _warning_counts(workspace: Path, codebase_id: str, snapshot_id: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for item in read_jsonl(snapshot_files_path(workspace, codebase_id, snapshot_id)):
        reason = item.get("skip_reason")
        if reason:
            counts[str(reason)] = counts.get(str(reason), 0) + 1
    return dict(sorted(counts.items()))


def _confidence_distribution(workspace: Path, codebase_id: str) -> dict[str, int]:
    values: list[float] = []
    needs_review = 0
    for path in (
        architecture_code_roles_path(workspace, codebase_id),
        architecture_code_layers_path(workspace, codebase_id),
        architecture_code_boundaries_path(workspace, codebase_id),
        architecture_pattern_candidates_path(workspace, codebase_id),
    ):
        for item in read_jsonl(path):
            try:
                values.append(float(item.get("confidence") or 0))
            except (TypeError, ValueError):
                values.append(0)
            if item.get("needs_review"):
                needs_review += 1
    high = sum(1 for value in values if value >= 0.8)
    medium = sum(1 for value in values if 0.5 <= value < 0.8)
    low = sum(1 for value in values if value < 0.5)
    return {"high": high, "medium": medium, "low": low, "needs_review": needs_review}


def _language_distribution(files: list[dict[str, Any]]) -> dict[str, dict[str, int]]:
    languages: dict[str, dict[str, int]] = {}
    for item in files:
        if not item.get("included"):
            continue
        language = str(item.get("language") or "unknown")
        bucket = languages.setdefault(language, {"files": 0, "loc": 0, "bytes": 0})
        bucket["files"] += 1
        bucket["loc"] += int(item.get("loc") or 0)
        bucket["bytes"] += int(item.get("size_bytes") or 0)
    return dict(sorted(languages.items()))


def _source_artifact_refs(codebase_id: str, snapshot_id: str) -> list[dict[str, str]]:
    return [
        {"type": "snapshot", "artifact_ref": f"snapshot://{codebase_id}/{snapshot_id}"},
        {"type": "snapshot_files", "artifact_ref": f"snapshot-files://{codebase_id}/{snapshot_id}"},
        {"type": "code_derived_architecture", "artifact_ref": f"architecture://{codebase_id}/code_derived_model.json"},
    ]
