"""Boundary inference for V2.4 code-derived architecture."""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Any

from .code_model import code_architecture_boundary


def infer_boundaries(
    *,
    workspace_id: str,
    codebase_id: str,
    snapshot_id: str,
    roles: list[dict[str, Any]],
    source_artifact_refs: list[dict[str, str]],
) -> list[dict[str, Any]]:
    boundaries: list[dict[str, Any]] = []
    by_package: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for role in roles:
        path = str(role.get("path") or "")
        package = _package_name(path)
        if package:
            by_package[package].append(role)
    for package, members_roles in sorted(by_package.items()):
        if len(members_roles) < 2:
            continue
        boundaries.append(_boundary(workspace_id, codebase_id, snapshot_id, "package", package, members_roles, ["path_package"], source_artifact_refs))

    special = [
        ("public_surface_boundary", "public interface", {"api_router", "mcp_tooling", "cli_tooling", "frontend"}, "public_surface_roles"),
        ("governance_boundary", "governance", {"governance", "policy"}, "governance_roles"),
        ("storage_boundary", "artifact and storage", {"artifact_store", "storage"}, "artifact_storage_roles"),
        ("adapter_boundary", "adapter and provider", {"provider", "runtime"}, "adapter_provider_roles"),
    ]
    for boundary_type, name, role_types, signal in special:
        matches = [role for role in roles if role.get("role_type") in role_types and float(role.get("confidence") or 0) >= 0.8]
        if matches:
            boundaries.append(_boundary(workspace_id, codebase_id, snapshot_id, boundary_type, name, matches, [signal], source_artifact_refs))
    return boundaries


def _boundary(workspace_id: str, codebase_id: str, snapshot_id: str, boundary_type: str, name: str, roles: list[dict[str, Any]], signals: list[str], source_artifact_refs: list[dict[str, str]]) -> dict[str, Any]:
    members = [
        {
            "role_id": role.get("role_id"),
            "role_type": role.get("role_type"),
            "target_type": role.get("target_type"),
            "target_id": role.get("target_id"),
            "name": role.get("name"),
            "path": role.get("path"),
        }
        for role in roles[:200]
    ]
    evidence = []
    seen = set()
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
                break
        if len(evidence) >= 20:
            break
    return code_architecture_boundary(
        workspace_id=workspace_id,
        codebase_id=codebase_id,
        snapshot_id=snapshot_id,
        boundary_type=boundary_type,
        name=name,
        members=members,
        signals=[*signals, f"roles:{len(roles)}"],
        evidence=evidence,
        confidence=0.85 if evidence else 0.55,
        needs_review=[] if evidence else [{"reason": "boundary_missing_evidence"}],
        source_artifact_refs=source_artifact_refs,
    )


def _package_name(path: str) -> str | None:
    if not path:
        return None
    parts = Path(path).parts
    if len(parts) >= 4 and parts[0] == "backend" and parts[1] == "data_service":
        return "/".join(parts[:4]) if parts[2] == "code_assets" and len(parts) >= 4 else "/".join(parts[:3])
    if len(parts) >= 3 and parts[0] == "backend" and parts[1] == "app":
        return "/".join(parts[:3])
    if len(parts) >= 2 and parts[0] in {"frontend", "docs", "tests", "backend"}:
        return "/".join(parts[:2])
    return parts[0] if parts else None
