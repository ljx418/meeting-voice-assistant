"""V2.8 deterministic code fact chains."""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from typing import Any


RELATION_BY_SURFACE = {
    "http_api": "registered_route",
    "mcp_tool": "registered_mcp_tool",
    "cli_command": "registered_cli_command",
}
CHAIN_BY_SURFACE = {
    "http_api": "http_route_chain",
    "mcp_tool": "mcp_tool_chain",
    "cli_command": "cli_command_chain",
}


def build_code_fact_chains(
    *,
    workspace_id: str,
    codebase_id: str,
    snapshot_id: str,
    surfaces: list[dict[str, Any]],
    symbols: list[dict[str, Any]],
    files: list[dict[str, Any]],
    evidence: list[dict[str, Any]],
    artifact_refs: list[dict[str, Any]],
) -> dict[str, Any]:
    symbol_by_file = _symbols_by_file(symbols)
    evidence_by_file = _evidence_by_file(evidence)
    chains = []
    for surface in sorted(surfaces, key=lambda item: str(item.get("surface_id") or "")):
        chain = _surface_chain(workspace_id, codebase_id, snapshot_id, surface, symbol_by_file, evidence_by_file)
        if chain:
            chains.append(chain)
    chains.extend(_test_reference_chains(workspace_id, codebase_id, snapshot_id, files, evidence_by_file))
    boundaries = _runtime_boundaries(workspace_id, codebase_id, snapshot_id, surfaces, files)
    summary = {
        "schema_version": "v2.8",
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "chain_count": len(chains),
        "accepted_chain_count": sum(1 for item in chains if item["status"] == "accepted"),
        "needs_review_chain_count": sum(1 for item in chains if item["status"] != "accepted"),
        "runtime_boundary_count": len(boundaries),
        "deterministic_relation_types": sorted(set(RELATION_BY_SURFACE.values()) | {"test_references_symbol", "declared_config_boundary"}),
        "inferred_relation_types": ["imports_module", "name_similarity", "folder_proximity", "doc_claim_similarity"],
        "max_traversal_depth": 2,
        "source_artifact_refs": artifact_refs,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    return {"summary": summary, "chains": chains, "runtime_boundaries": boundaries, "artifact_refs": artifact_refs}


def public_code_fact_chain_payload(payload: dict[str, Any], artifact_refs: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "schema_version": "v2.8",
        "summary": payload.get("summary", {}),
        "chains": payload.get("chains", [])[:160],
        "runtime_boundaries": payload.get("runtime_boundaries", [])[:120],
        "artifact_refs": artifact_refs,
    }


def _surface_chain(
    workspace_id: str,
    codebase_id: str,
    snapshot_id: str,
    surface: dict[str, Any],
    symbol_by_file: dict[str, list[dict[str, Any]]],
    evidence_by_file: dict[str, list[dict[str, Any]]],
) -> dict[str, Any] | None:
    surface_type = str(surface.get("surface_type") or "")
    if surface_type not in CHAIN_BY_SURFACE:
        return None
    source_file = str(surface.get("source_file") or "")
    line_range = surface.get("line_range")
    relation_type = RELATION_BY_SURFACE[surface_type]
    status = "accepted" if source_file and _valid_line_range(line_range) else "unresolved"
    needs_review = [] if status == "accepted" else [{"code": "MISSING_SURFACE_LINE_EVIDENCE", "reason": "Surface source file or line range is missing."}]
    steps = [
        _step("entry_surface", surface.get("surface_id"), source_file, line_range, relation_type, surface),
    ]
    handler = _matching_symbol(source_file, surface, symbol_by_file)
    if handler:
        steps.append(_step("handler_symbol", handler.get("symbol_id") or handler.get("qualified_name"), source_file, handler.get("line_range"), "calls_local_service_direct", handler))
    evidence_refs = _compact_refs([surface, *(evidence_by_file.get(source_file) or [])[:3]])
    return {
        "chain_id": _stable_id("chain", str(surface.get("surface_id") or ""), snapshot_id),
        "schema_version": "v2.8",
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "chain_type": CHAIN_BY_SURFACE[surface_type],
        "status": status,
        "entry_ref": {"surface_id": surface.get("surface_id"), "surface_type": surface_type, "capability_id": surface.get("capability_id")},
        "steps": steps,
        "source_files": [source_file] if source_file else [],
        "line_ranges": [line_range] if _valid_line_range(line_range) else [],
        "evidence_refs": evidence_refs,
        "confidence": 0.95 if status == "accepted" else 0.3,
        "needs_review": needs_review,
        "warnings": [],
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


def _test_reference_chains(workspace_id: str, codebase_id: str, snapshot_id: str, files: list[dict[str, Any]], evidence_by_file: dict[str, list[dict[str, Any]]]) -> list[dict[str, Any]]:
    chains = []
    for item in sorted(files, key=lambda row: str(row.get("path") or "")):
        path = str(item.get("path") or "")
        if "/test" not in path and not path.startswith("test") and "_test." not in path:
            continue
        evidence_refs = _compact_refs(evidence_by_file.get(path, []))
        chains.append(
            {
                "chain_id": _stable_id("test-chain", path, snapshot_id),
                "schema_version": "v2.8",
                "workspace_id": workspace_id,
                "codebase_id": codebase_id,
                "snapshot_id": snapshot_id,
                "chain_type": "test_reference_chain",
                "status": "needs_review",
                "entry_ref": {"path": path},
                "steps": [_step("test_file", path, path, None, "test_references_symbol", item)],
                "source_files": [path],
                "line_ranges": [],
                "evidence_refs": evidence_refs,
                "confidence": 0.55,
                "needs_review": [{"code": "TEST_REFERENCE_REQUIRES_SYMBOL_CONFIRMATION", "reason": "Test file relationship is path-based and remains reviewable."}],
                "warnings": [],
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
        )
        if len(chains) >= 80:
            break
    return chains


def _runtime_boundaries(workspace_id: str, codebase_id: str, snapshot_id: str, surfaces: list[dict[str, Any]], files: list[dict[str, Any]]) -> list[dict[str, Any]]:
    boundaries: dict[str, dict[str, Any]] = {}
    for surface in surfaces:
        surface_type = str(surface.get("surface_type") or "")
        boundary_type = {"http_api": "http_server", "mcp_tool": "mcp_stdio", "cli_command": "cli"}.get(surface_type)
        if not boundary_type:
            continue
        boundary = boundaries.setdefault(boundary_type, _boundary(workspace_id, codebase_id, snapshot_id, boundary_type, surface_type))
        boundary["source_refs"].append(_surface_ref(surface))
        boundary["evidence_refs"].append(_surface_ref(surface))
    for item in files:
        path = str(item.get("path") or "")
        boundary_type = None
        if path.endswith(("pyproject.toml", "package.json", ".env.example", "docker-compose.yml")):
            boundary_type = "declared_config_boundary"
        elif "tests/" in path or path.startswith("tests/"):
            boundary_type = "test_runtime"
        if boundary_type:
            boundary = boundaries.setdefault(boundary_type, _boundary(workspace_id, codebase_id, snapshot_id, boundary_type, boundary_type))
            boundary["source_refs"].append({"type": "source_file", "path": path})
            boundary["evidence_refs"].append({"type": "source_file", "path": path})
    return sorted(boundaries.values(), key=lambda item: item["boundary_id"])


def _boundary(workspace_id: str, codebase_id: str, snapshot_id: str, boundary_type: str, label: str) -> dict[str, Any]:
    deterministic = boundary_type in {"http_server", "mcp_stdio", "cli", "declared_config_boundary", "test_runtime"}
    return {
        "boundary_id": _stable_id("runtime-boundary", codebase_id, snapshot_id, boundary_type),
        "schema_version": "v2.8",
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "boundary_type": boundary_type if boundary_type != "declared_config_boundary" else "local_file_storage",
        "label": label,
        "status": "deterministic" if deterministic else "needs_review",
        "source_refs": [],
        "evidence_refs": [],
        "confidence": 0.9 if deterministic else 0.4,
        "needs_review": [] if deterministic else [{"code": "BOUNDARY_INFERRED", "reason": "Runtime boundary lacks explicit deterministic evidence."}],
    }


def _step(kind: str, ref: Any, path: str, line_range: Any, relation_type: str, source: dict[str, Any]) -> dict[str, Any]:
    return {
        "step_id": _stable_id("step", kind, str(ref), str(path), str(line_range)),
        "step_type": kind,
        "ref": ref,
        "relation_type": relation_type,
        "source_file": path,
        "line_range": line_range,
        "evidence_ref": _surface_ref(source),
    }


def _matching_symbol(source_file: str, surface: dict[str, Any], symbol_by_file: dict[str, list[dict[str, Any]]]) -> dict[str, Any] | None:
    handler = str(surface.get("handler") or surface.get("handler_function") or surface.get("tool_name") or "").lower()
    candidates = symbol_by_file.get(source_file, [])
    for symbol in candidates:
        name = str(symbol.get("name") or symbol.get("qualified_name") or "").lower()
        if handler and (handler in name or name in handler):
            return symbol
    return candidates[0] if candidates else None


def _symbols_by_file(symbols: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    result: dict[str, list[dict[str, Any]]] = {}
    for symbol in symbols:
        path = str(symbol.get("path") or symbol.get("source_file") or "")
        if path:
            result.setdefault(path, []).append(symbol)
    return result


def _evidence_by_file(evidence: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    result: dict[str, list[dict[str, Any]]] = {}
    for item in evidence:
        path = str(item.get("path") or item.get("source_file") or "")
        if path:
            result.setdefault(path, []).append(item)
    return result


def _valid_line_range(value: Any) -> bool:
    return isinstance(value, list) and len(value) == 2 and all(isinstance(item, int) and item > 0 for item in value)


def _surface_ref(surface: dict[str, Any]) -> dict[str, Any]:
    return {
        "surface_id": surface.get("surface_id"),
        "path": surface.get("source_file") or surface.get("path"),
        "line_range": surface.get("line_range"),
        "capability_id": surface.get("capability_id"),
    }


def _compact_refs(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    refs = []
    for item in items:
        ref = _surface_ref(item)
        if any(ref.values()):
            refs.append(ref)
    return refs[:8]


def _stable_id(*parts: str) -> str:
    return hashlib.sha256(":".join(parts).encode("utf-8")).hexdigest()[:20]
