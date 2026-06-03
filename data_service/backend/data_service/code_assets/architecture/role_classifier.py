"""Deterministic role classification for V2.4 code-derived architecture."""

from __future__ import annotations

from collections import OrderedDict
from pathlib import Path
from typing import Any

from .code_model import code_architecture_role, evidence_from_path


def classify_code_roles(
    *,
    workspace_id: str,
    codebase_id: str,
    snapshot_id: str,
    files: list[dict[str, Any]],
    surfaces: list[dict[str, Any]],
    symbols: list[dict[str, Any]],
    source_artifact_refs: list[dict[str, str]],
) -> list[dict[str, Any]]:
    roles: list[dict[str, Any]] = []
    for surface in surfaces:
        role = _role_from_surface(
            workspace_id=workspace_id,
            codebase_id=codebase_id,
            snapshot_id=snapshot_id,
            surface=surface,
            source_artifact_refs=source_artifact_refs,
        )
        if role:
            roles.append(role)
    for symbol in symbols:
        if symbol.get("kind") != "module":
            continue
        role = _role_from_symbol(
            workspace_id=workspace_id,
            codebase_id=codebase_id,
            snapshot_id=snapshot_id,
            symbol=symbol,
            source_artifact_refs=source_artifact_refs,
        )
        if role:
            roles.append(role)
    for record in files:
        role = _role_from_file(
            workspace_id=workspace_id,
            codebase_id=codebase_id,
            snapshot_id=snapshot_id,
            record=record,
            source_artifact_refs=source_artifact_refs,
        )
        if role:
            roles.append(role)
    return _dedupe_roles(roles)


def _role_from_surface(*, workspace_id: str, codebase_id: str, snapshot_id: str, surface: dict[str, Any], source_artifact_refs: list[dict[str, str]]) -> dict[str, Any] | None:
    surface_type = str(surface.get("surface_type") or "")
    mapping = {
        "http_api": ("api_router", "http_surface"),
        "mcp_tool": ("mcp_tooling", "mcp_surface"),
        "cli_command": ("cli_tooling", "cli_surface"),
        "frontend_page": ("frontend", "frontend_surface"),
    }
    if surface_type not in mapping:
        return None
    role_type, signal = mapping[surface_type]
    path = _surface_path(surface)
    evidence = _surface_evidence(surface, path)
    name = str(surface.get("name") or surface.get("path") or surface.get("tool_name") or surface.get("command") or surface.get("surface_id"))
    return code_architecture_role(
        workspace_id=workspace_id,
        codebase_id=codebase_id,
        snapshot_id=snapshot_id,
        role_type=role_type,
        target_type="surface",
        target_id=str(surface.get("surface_id") or name),
        name=name,
        path=path,
        signals=[signal, surface_type],
        evidence=evidence,
        confidence=0.95 if evidence else 0.7,
        needs_review=[] if evidence else [{"reason": "surface_missing_evidence"}],
        source_artifact_refs=source_artifact_refs,
    )


def _role_from_symbol(*, workspace_id: str, codebase_id: str, snapshot_id: str, symbol: dict[str, Any], source_artifact_refs: list[dict[str, str]]) -> dict[str, Any] | None:
    path = str(symbol.get("path") or "")
    if not path:
        return None
    role_type, confidence, signals = _classify_path(path)
    if role_type == "unknown":
        return None
    line_range = symbol.get("line_range") if isinstance(symbol.get("line_range"), list) else None
    return code_architecture_role(
        workspace_id=workspace_id,
        codebase_id=codebase_id,
        snapshot_id=snapshot_id,
        role_type=role_type,
        target_type="symbol",
        target_id=str(symbol.get("symbol_id") or symbol.get("qualified_name") or path),
        name=str(symbol.get("qualified_name") or symbol.get("name") or path),
        path=path,
        signals=signals,
        evidence=evidence_from_path(path, line_range=line_range, source="symbol_index"),
        confidence=confidence,
        needs_review=[],
        source_artifact_refs=source_artifact_refs,
    )


def _role_from_file(*, workspace_id: str, codebase_id: str, snapshot_id: str, record: dict[str, Any], source_artifact_refs: list[dict[str, str]]) -> dict[str, Any] | None:
    if not record.get("included"):
        return None
    path = str(record.get("path") or "")
    if not path:
        return None
    role_type, confidence, signals = _classify_path(path)
    if role_type == "unknown":
        if not _is_relevant_unknown(path):
            return None
        return code_architecture_role(
            workspace_id=workspace_id,
            codebase_id=codebase_id,
            snapshot_id=snapshot_id,
            role_type="unknown",
            target_type="file",
            target_id=f"file:{path}",
            name=Path(path).name,
            path=path,
            signals=["unclassified_relevant_file"],
            evidence=evidence_from_path(path, source="snapshot_file_manifest"),
            confidence=0.25,
            needs_review=[{"reason": "role_not_classified"}],
            source_artifact_refs=source_artifact_refs,
        )
    return code_architecture_role(
        workspace_id=workspace_id,
        codebase_id=codebase_id,
        snapshot_id=snapshot_id,
        role_type=role_type,
        target_type="file",
        target_id=f"file:{path}",
        name=Path(path).name,
        path=path,
        signals=signals,
        evidence=evidence_from_path(path, source="snapshot_file_manifest"),
        confidence=confidence,
        needs_review=[],
        source_artifact_refs=source_artifact_refs,
    )


def _classify_path(path: str) -> tuple[str, float, list[str]]:
    lower = path.lower()
    if lower.startswith("frontend/") or "/frontend/" in lower or lower.endswith((".vue", ".tsx", ".jsx")):
        return "frontend", 0.9, ["frontend_path"]
    if lower.startswith("docs/") or lower.endswith((".md", ".drawio", ".mmd")):
        return "docs", 0.85, ["docs_path"]
    if lower.startswith("backend/tests/") or lower.startswith("tests/") or "/test_" in lower or lower.endswith("_test.py"):
        return "test", 0.9, ["test_path"]
    if lower.startswith("scripts/") or "/scripts/" in lower:
        return "script", 0.85, ["script_path"]
    if "backend/app/api/" in lower or lower.startswith("backend/app/api/"):
        return "api_router", 0.9, ["backend_api_path"]
    if "mcp_" in lower or lower.endswith("/mcp.py"):
        return "mcp_tooling", 0.9, ["mcp_module_path"]
    if "cli_" in lower or lower.endswith("__main__.py"):
        return "cli_tooling", 0.9, ["cli_module_path"]
    if "quality" in lower or "governance" in lower:
        return "governance", 0.85, ["governance_name"]
    if "artifact" in lower or "persistence" in lower or "registry" in lower or "snapshot" in lower:
        return "artifact_store", 0.85, ["artifact_persistence_name"]
    if "provider" in lower:
        return "provider", 0.8, ["provider_name"]
    if "policy" in lower:
        return "policy", 0.8, ["policy_name"]
    if "runtime" in lower:
        return "runtime", 0.8, ["runtime_name"]
    if any(token in lower for token in ("devwiki", "graph", "context", "overview", "inventory", "symbols", "trace", "architecture")):
        return "service", 0.8, ["project_intelligence_service_name"]
    if lower.startswith("backend/data_service/"):
        return "service", 0.7, ["backend_data_service_path"]
    return "unknown", 0.2, []


def _surface_path(surface: dict[str, Any]) -> str | None:
    for key in ("source_file", "path"):
        value = surface.get(key)
        if isinstance(value, str) and value:
            return value
    evidence = surface.get("evidence")
    if isinstance(evidence, list):
        for item in evidence:
            if isinstance(item, dict) and isinstance(item.get("path"), str):
                return item["path"]
    return None


def _surface_evidence(surface: dict[str, Any], path: str | None) -> list[dict[str, Any]]:
    existing = surface.get("evidence")
    if isinstance(existing, list) and existing:
        return [dict(item) for item in existing if isinstance(item, dict)]
    if path:
        line_range = surface.get("line_range") if isinstance(surface.get("line_range"), list) else None
        return evidence_from_path(path, line_range=line_range, source="public_surface_inventory")
    return []


def _is_relevant_unknown(path: str) -> bool:
    return path.endswith((".py", ".ts", ".tsx", ".vue", ".md", ".toml", ".json", ".yaml", ".yml"))


def _dedupe_roles(roles: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: OrderedDict[str, dict[str, Any]] = OrderedDict()
    for role in roles:
        key = str(role.get("role_id"))
        if key not in seen or float(role.get("confidence") or 0) > float(seen[key].get("confidence") or 0):
            seen[key] = role
    return list(seen.values())
