"""Surface-to-symbol mapping and evidence trace artifacts for V2 codebase assets."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from data_service.mcp_common import now, read_json, write_json

from .artifacts import (
    evidence_path,
    inventory_surfaces_path,
    mapping_summary_path,
    mappings_path,
    read_jsonl,
    symbol_summary_path,
    symbols_path,
    trace_index_path,
    write_jsonl,
)
from .inventory import CodebaseInventoryService
from .registry import CodebaseRegistry
from .snapshot import CodebaseSnapshotService
from .symbols import CodebaseSymbolIndexService


TRACE_SCHEMA_VERSION = "v2.0"
SUCCESS_MAPPING_CONFIDENCE_MIN = 0.80
GOLDEN_CAPABILITIES = {
    "agent_context_pack",
    "source_import",
    "query",
    "build",
    "quality",
    "graph",
    "source_trace",
    "codebase_import",
    "project_overview",
}
MCP_HANDLER_BY_PREFIX = {
    "knowledge_codebase_": "backend.data_service.mcp_code_tools.handle_code_tool",
    "knowledge_devwiki_": "backend.data_service.mcp_code_devwiki_tools.handle_devwiki_tool",
    "knowledge_code_graph_": "backend.data_service.mcp_code_graph_tools.handle_graph_tool",
    "knowledge_code_quality_": "backend.data_service.mcp_code_quality_tools.handle_quality_tool",
    "knowledge_project_": "backend.data_service.mcp_code_tools.handle_code_tool",
    "knowledge_code_": "backend.data_service.mcp_code_tools.handle_code_tool",
    "knowledge_public_surface_trace": "backend.data_service.mcp_code_tools.handle_code_tool",
    "knowledge_source_": "backend.data_service.mcp_source_tools.handle_source_tool",
    "knowledge_build_": "backend.data_service.mcp_build_tools.handle_build_tool",
    "knowledge_quality_": "backend.data_service.mcp_quality_tools.handle_quality_tool",
    "knowledge_graph_": "backend.data_service.mcp_session_tools.handle_session_tool",
    "knowledge_query": "backend.data_service.mcp_core_tools.handle_core_tool",
    "knowledge_ingest": "backend.data_service.mcp_core_tools.handle_core_tool",
}
CLI_SYMBOL_BY_PREFIX = {
    "knowledge code ": "backend.data_service.cli_code.run_code_command",
    "knowledge source ": "backend.data_service.__main__.main",
    "knowledge build ": "backend.data_service.__main__.main",
    "knowledge query": "backend.data_service.__main__.main",
    "knowledge quality ": "backend.data_service.__main__.main",
    "knowledge graph ": "backend.data_service.__main__.main",
    "knowledge trace ": "backend.data_service.__main__.main",
}


class CodebaseTraceService:
    def __init__(self, workspace: Path, *, workspace_id: str) -> None:
        self.workspace = workspace
        self.workspace_id = workspace_id
        self.registry = CodebaseRegistry(workspace, workspace_id=workspace_id)
        self.snapshots = CodebaseSnapshotService(workspace, workspace_id=workspace_id)
        self.inventory = CodebaseInventoryService(workspace, workspace_id=workspace_id)
        self.symbols = CodebaseSymbolIndexService(workspace, workspace_id=workspace_id)

    def build_trace(self, codebase_id: str, *, snapshot_id: str | None = None) -> dict[str, Any]:
        asset = self.registry.describe(codebase_id)
        if asset.status != "active":
            raise ValueError("CODEBASE_NOT_ACTIVE")
        resolved_snapshot_id = snapshot_id or self._latest_snapshot_id(codebase_id)
        self.snapshots.read_snapshot(codebase_id, resolved_snapshot_id)
        surfaces = self._read_required_surfaces(codebase_id, resolved_snapshot_id)
        symbol_items = self._read_required_symbols(codebase_id, resolved_snapshot_id)
        root = Path(asset.root_path).expanduser().resolve()

        symbols_by_file_name = _symbols_by_file_name(symbol_items)
        symbols_by_qualified_name = {str(item.get("qualified_name")): item for item in symbol_items}
        evidence_rows: list[dict[str, Any]] = []
        mappings: list[dict[str, Any]] = []

        for surface in surfaces:
            surface_evidence = _surface_evidence(
                self.workspace_id,
                codebase_id,
                resolved_snapshot_id,
                surface,
                root,
            )
            if surface_evidence:
                evidence_rows.append(surface_evidence)
                mappings.append(
                    _mapping(
                        self.workspace_id,
                        codebase_id,
                        resolved_snapshot_id,
                        from_type=str(surface.get("surface_type") or "surface"),
                        from_id=str(surface.get("surface_id")),
                        to_type="evidence",
                        to_id=str(surface_evidence["evidence_id"]),
                        relation="EVIDENCED_BY",
                        capability_id=str(surface.get("capability_id") or "unresolved"),
                        confidence=float(surface_evidence.get("confidence") or 0.9),
                        evidence_ids=[str(surface_evidence["evidence_id"])],
                    )
                )
            symbol = _symbol_for_surface(surface, symbols_by_file_name, symbols_by_qualified_name)
            if symbol:
                symbol_evidence = _symbol_evidence(
                    self.workspace_id,
                    codebase_id,
                    resolved_snapshot_id,
                    surface,
                    symbol,
                    root,
                )
                if symbol_evidence:
                    evidence_rows.append(symbol_evidence)
                evidence_ids = [str(row["evidence_id"]) for row in [surface_evidence, symbol_evidence] if row]
                mappings.append(
                    _mapping(
                        self.workspace_id,
                        codebase_id,
                        resolved_snapshot_id,
                        from_type=str(surface.get("surface_type") or "surface"),
                        from_id=str(surface.get("surface_id")),
                        to_type="symbol",
                        to_id=str(symbol.get("symbol_id")),
                        relation="HANDLED_BY",
                        capability_id=str(surface.get("capability_id") or "unresolved"),
                        confidence=_symbol_mapping_confidence(surface, symbol),
                        evidence_ids=evidence_ids,
                    )
                )
            else:
                mappings.append(
                    _mapping(
                        self.workspace_id,
                        codebase_id,
                        resolved_snapshot_id,
                        from_type=str(surface.get("surface_type") or "surface"),
                        from_id=str(surface.get("surface_id")),
                        to_type="symbol",
                        to_id=None,
                        relation="UNRESOLVED",
                        capability_id=str(surface.get("capability_id") or "unresolved"),
                        confidence=0.0,
                        evidence_ids=[str(surface_evidence["evidence_id"])] if surface_evidence else [],
                        unresolved_reason=_unresolved_reason(surface),
                    )
                )

        evidence_rows = _dedupe_by_key(evidence_rows, "evidence_id")
        mappings = _dedupe_by_key(mappings, "mapping_id")
        trace_index = _build_trace_index(self.workspace_id, codebase_id, resolved_snapshot_id, surfaces, symbol_items, mappings, evidence_rows)
        summary = _build_summary(self.workspace_id, codebase_id, resolved_snapshot_id, surfaces, mappings, evidence_rows)
        refs = trace_artifact_refs(codebase_id, resolved_snapshot_id)
        summary["artifact_refs"] = refs
        trace_index["artifact_refs"] = refs

        write_jsonl(mappings_path(self.workspace, codebase_id, resolved_snapshot_id), mappings)
        write_jsonl(evidence_path(self.workspace, codebase_id, resolved_snapshot_id), evidence_rows)
        write_json(mapping_summary_path(self.workspace, codebase_id, resolved_snapshot_id), summary)
        write_json(trace_index_path(self.workspace, codebase_id, resolved_snapshot_id), trace_index)
        return {"summary": summary, "mappings": mappings, "evidence": evidence_rows, "trace_index": trace_index}

    def read_trace(self, codebase_id: str, *, snapshot_id: str | None = None) -> dict[str, Any]:
        resolved_snapshot_id = snapshot_id or self._latest_snapshot_id(codebase_id)
        self.registry.describe(codebase_id)
        summary = read_json(mapping_summary_path(self.workspace, codebase_id, resolved_snapshot_id), None)
        if not summary:
            raise FileNotFoundError("TRACE_NOT_FOUND")
        return {
            "summary": summary,
            "mappings": read_jsonl(mappings_path(self.workspace, codebase_id, resolved_snapshot_id)),
            "evidence": read_jsonl(evidence_path(self.workspace, codebase_id, resolved_snapshot_id)),
            "trace_index": read_json(trace_index_path(self.workspace, codebase_id, resolved_snapshot_id), {}),
            "surfaces": read_jsonl(inventory_surfaces_path(self.workspace, codebase_id, resolved_snapshot_id)),
            "symbols": read_jsonl(symbols_path(self.workspace, codebase_id, resolved_snapshot_id)),
        }

    def trace_surface(self, codebase_id: str, surface_id: str, *, snapshot_id: str | None = None) -> dict[str, Any]:
        trace = self.read_trace(codebase_id, snapshot_id=snapshot_id)
        index = trace["trace_index"].get("by_surface", {}).get(surface_id)
        if not index:
            raise FileNotFoundError("TRACE_SURFACE_NOT_FOUND")
        return _select_trace(trace, surface_ids={surface_id}, mapping_ids=set(index.get("mapping_ids") or []), evidence_ids=set(index.get("evidence_ids") or []))

    def trace_capability(self, codebase_id: str, capability_id: str, *, snapshot_id: str | None = None) -> dict[str, Any]:
        trace = self.read_trace(codebase_id, snapshot_id=snapshot_id)
        index = trace["trace_index"].get("by_capability", {}).get(capability_id)
        if not index:
            raise FileNotFoundError("TRACE_CAPABILITY_NOT_FOUND")
        return _select_trace(
            trace,
            surface_ids=set(index.get("surface_ids") or []),
            symbol_ids=set(index.get("symbol_ids") or []),
            mapping_ids=set(index.get("mapping_ids") or []),
            evidence_ids=set(index.get("evidence_ids") or []),
        )

    def read_evidence(self, codebase_id: str, *, snapshot_id: str | None = None, limit: int = 50) -> list[dict[str, Any]]:
        evidence = self.read_trace(codebase_id, snapshot_id=snapshot_id)["evidence"]
        return evidence[: max(1, min(int(limit or 50), 500))]

    def _latest_snapshot_id(self, codebase_id: str) -> str:
        snapshots = self.snapshots.list_snapshots(codebase_id, limit=1)
        if not snapshots:
            raise FileNotFoundError("SNAPSHOT_NOT_FOUND")
        return str(snapshots[0]["snapshot_id"])

    def _read_required_surfaces(self, codebase_id: str, snapshot_id: str) -> list[dict[str, Any]]:
        if not inventory_surfaces_path(self.workspace, codebase_id, snapshot_id).exists():
            raise FileNotFoundError("NO_INVENTORY")
        return self.inventory.read_surfaces(codebase_id, snapshot_id=snapshot_id)

    def _read_required_symbols(self, codebase_id: str, snapshot_id: str) -> list[dict[str, Any]]:
        if not symbol_summary_path(self.workspace, codebase_id, snapshot_id).exists():
            raise FileNotFoundError("NO_SYMBOL_INDEX")
        return self.symbols.read_symbol_index(codebase_id, snapshot_id=snapshot_id)["symbols"]


def trace_artifact_refs(codebase_id: str, snapshot_id: str) -> list[dict[str, str]]:
    return [
        {"type": "mappings", "artifact_ref": f"mappings://{codebase_id}/{snapshot_id}"},
        {"type": "evidence", "artifact_ref": f"evidence://{codebase_id}/{snapshot_id}"},
        {"type": "mapping_summary", "artifact_ref": f"mapping-summary://{codebase_id}/{snapshot_id}"},
        {"type": "trace_index", "artifact_ref": f"trace-index://{codebase_id}/{snapshot_id}"},
    ]


def public_trace_payload(trace: dict[str, Any]) -> dict[str, Any]:
    summary = trace["summary"]
    return {
        "schema_version": summary.get("schema_version"),
        "workspace_id": summary.get("workspace_id"),
        "codebase_id": summary.get("codebase_id"),
        "snapshot_id": summary.get("snapshot_id"),
        "summary": summary,
        "mappings": [public_mapping_payload(item) for item in trace["mappings"]],
        "evidence": [public_evidence_payload(item) for item in trace["evidence"]],
        "trace_index": trace["trace_index"],
    }


def public_trace_selection_payload(selection: dict[str, Any]) -> dict[str, Any]:
    return {
        "snapshot_id": selection.get("snapshot_id"),
        "surfaces": selection.get("surfaces", []),
        "symbols": [_public_symbol_ref(item) for item in selection.get("symbols", [])],
        "mappings": [public_mapping_payload(item) for item in selection.get("mappings", [])],
        "evidence": [public_evidence_payload(item) for item in selection.get("evidence", [])],
    }


def public_mapping_payload(mapping: dict[str, Any]) -> dict[str, Any]:
    return dict(mapping)


def public_evidence_payload(evidence: dict[str, Any]) -> dict[str, Any]:
    payload = dict(evidence)
    payload["source_file"] = payload.pop("path", None)
    return payload


def _public_symbol_ref(symbol: dict[str, Any]) -> dict[str, Any]:
    payload = {
        "symbol_id": symbol.get("symbol_id"),
        "kind": symbol.get("kind"),
        "name": symbol.get("name"),
        "qualified_name": symbol.get("qualified_name"),
        "source_file": symbol.get("path") or symbol.get("source_file"),
        "line_range": symbol.get("line_range"),
    }
    return payload


def _symbols_by_file_name(symbols: list[dict[str, Any]]) -> dict[tuple[str, str], list[dict[str, Any]]]:
    index: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for symbol in symbols:
        key = (str(symbol.get("path") or ""), str(symbol.get("name") or ""))
        index.setdefault(key, []).append(symbol)
    return index


def _surface_evidence(
    workspace_id: str,
    codebase_id: str,
    snapshot_id: str,
    surface: dict[str, Any],
    root: Path,
) -> dict[str, Any] | None:
    source_file = str(surface.get("source_file") or "")
    line_range = _line_range(surface.get("line_range"))
    if not source_file or not line_range:
        return None
    if not _line_range_valid(root / source_file, line_range):
        return None
    return _evidence(
        workspace_id,
        codebase_id,
        snapshot_id,
        path=source_file,
        line_range=line_range,
        symbol_id=None,
        surface_id=str(surface.get("surface_id")),
        capability_id=str(surface.get("capability_id") or "unresolved"),
        confidence=max(0.8, min(float(surface.get("confidence") or 0.9), 1.0)),
        snippet=_snippet(root / source_file, line_range),
    )


def _symbol_evidence(
    workspace_id: str,
    codebase_id: str,
    snapshot_id: str,
    surface: dict[str, Any],
    symbol: dict[str, Any],
    root: Path,
) -> dict[str, Any] | None:
    source_file = str(symbol.get("path") or "")
    line_range = _line_range(symbol.get("line_range"))
    if not source_file or not line_range:
        return None
    if not _line_range_valid(root / source_file, line_range):
        return None
    return _evidence(
        workspace_id,
        codebase_id,
        snapshot_id,
        path=source_file,
        line_range=line_range,
        symbol_id=str(symbol.get("symbol_id")),
        surface_id=str(surface.get("surface_id")),
        capability_id=str(surface.get("capability_id") or "unresolved"),
        confidence=_symbol_mapping_confidence(surface, symbol),
        snippet=_snippet(root / source_file, line_range),
    )


def _symbol_for_surface(
    surface: dict[str, Any],
    symbols_by_file_name: dict[tuple[str, str], list[dict[str, Any]]],
    symbols_by_qualified_name: dict[str, dict[str, Any]],
) -> dict[str, Any] | None:
    surface_type = str(surface.get("surface_type") or "")
    source_file = str(surface.get("source_file") or "")
    if surface_type == "http_api":
        handler = str(surface.get("handler") or "")
        if not handler:
            return None
        matches = symbols_by_file_name.get((source_file, handler), [])
        return _single_symbol(matches)
    if surface_type == "mcp_tool":
        return symbols_by_qualified_name.get(_mcp_handler_qualified_name(str(surface.get("tool_name") or "")))
    if surface_type == "cli_command":
        return symbols_by_qualified_name.get(_cli_handler_qualified_name(str(surface.get("command") or "")))
    return None


def _mcp_handler_qualified_name(tool_name: str) -> str:
    for prefix, qualified_name in MCP_HANDLER_BY_PREFIX.items():
        if tool_name == prefix or tool_name.startswith(prefix):
            return qualified_name
    return "backend.data_service.mcp_core_tools.handle_core_tool"


def _cli_handler_qualified_name(command: str) -> str:
    for prefix, qualified_name in CLI_SYMBOL_BY_PREFIX.items():
        if command == prefix.rstrip() or command.startswith(prefix):
            return qualified_name
    return "backend.data_service.__main__.main"


def _single_symbol(matches: list[dict[str, Any]]) -> dict[str, Any] | None:
    function_like = [item for item in matches if item.get("kind") in {"function", "method"}]
    if len(function_like) == 1:
        return function_like[0]
    return None


def _symbol_mapping_confidence(surface: dict[str, Any], symbol: dict[str, Any]) -> float:
    if surface.get("surface_type") == "http_api" and surface.get("source_file") == symbol.get("path"):
        return 1.0
    if surface.get("surface_type") in {"mcp_tool", "cli_command"}:
        return 0.95
    return 0.8


def _unresolved_reason(surface: dict[str, Any]) -> str:
    surface_type = str(surface.get("surface_type") or "")
    if surface_type == "http_api":
        return "NO_HANDLER_SYMBOL"
    if surface_type == "mcp_tool":
        return "NO_TOOL_HANDLER"
    if surface_type == "cli_command":
        return "NO_CLI_HANDLER"
    return "OUT_OF_SCOPE_SURFACE_TYPE"


def _mapping(
    workspace_id: str,
    codebase_id: str,
    snapshot_id: str,
    *,
    from_type: str,
    from_id: str,
    to_type: str,
    to_id: str | None,
    relation: str,
    capability_id: str,
    confidence: float,
    evidence_ids: list[str],
    unresolved_reason: str | None = None,
) -> dict[str, Any]:
    is_success = confidence >= SUCCESS_MAPPING_CONFIDENCE_MIN and unresolved_reason is None and to_id is not None
    if not is_success and unresolved_reason is None:
        unresolved_reason = "LOW_CONFIDENCE"
    mapping_id = _stable_id("map", snapshot_id, from_type, from_id, to_type, to_id or "unresolved", relation, capability_id)
    return {
        "schema_version": TRACE_SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "mapping_id": mapping_id,
        "from_type": from_type,
        "from_id": from_id,
        "to_type": to_type,
        "to_id": to_id,
        "relation": relation,
        "capability_id": capability_id,
        "confidence": round(float(confidence), 4),
        "extractor": "deterministic_surface_symbol_mapper",
        "evidence_ids": sorted(set(evidence_ids)),
        "unresolved_reason": unresolved_reason,
    }


def _evidence(
    workspace_id: str,
    codebase_id: str,
    snapshot_id: str,
    *,
    path: str,
    line_range: list[int],
    symbol_id: str | None,
    surface_id: str | None,
    capability_id: str,
    confidence: float,
    snippet: str | None,
) -> dict[str, Any]:
    evidence_id = _stable_id("ev", snapshot_id, path, line_range[0], line_range[1], symbol_id or "", surface_id or "", capability_id)
    return {
        "schema_version": TRACE_SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "evidence_id": evidence_id,
        "path": path,
        "start_line": line_range[0],
        "end_line": line_range[1],
        "symbol_id": symbol_id,
        "surface_id": surface_id,
        "capability_id": capability_id,
        "extractor": "deterministic_surface_symbol_mapper",
        "confidence": round(float(confidence), 4),
        "snippet": snippet,
    }


def _build_trace_index(
    workspace_id: str,
    codebase_id: str,
    snapshot_id: str,
    surfaces: list[dict[str, Any]],
    symbols: list[dict[str, Any]],
    mappings: list[dict[str, Any]],
    evidence_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    surfaces_by_id = {str(item.get("surface_id")): item for item in surfaces}
    symbols_by_id = {str(item.get("symbol_id")): item for item in symbols}
    evidence_by_id = {str(item.get("evidence_id")): item for item in evidence_rows}
    by_surface: dict[str, dict[str, Any]] = {}
    by_capability: dict[str, dict[str, Any]] = {}
    by_symbol: dict[str, dict[str, Any]] = {}

    for mapping in mappings:
        surface_id = str(mapping.get("from_id") or "")
        capability_id = str(mapping.get("capability_id") or "unresolved")
        symbol_id = str(mapping.get("to_id") or "") if mapping.get("to_type") == "symbol" else ""
        evidence_ids = [item for item in mapping.get("evidence_ids") or [] if item in evidence_by_id]
        by_surface.setdefault(surface_id, {"mapping_ids": [], "evidence_ids": [], "symbol_ids": [], "capability_id": capability_id})
        by_surface[surface_id]["mapping_ids"].append(mapping["mapping_id"])
        by_surface[surface_id]["evidence_ids"].extend(evidence_ids)
        if symbol_id in symbols_by_id:
            by_surface[surface_id]["symbol_ids"].append(symbol_id)

        by_capability.setdefault(capability_id, {"surface_ids": [], "symbol_ids": [], "mapping_ids": [], "evidence_ids": []})
        if surface_id in surfaces_by_id:
            by_capability[capability_id]["surface_ids"].append(surface_id)
        if symbol_id in symbols_by_id:
            by_capability[capability_id]["symbol_ids"].append(symbol_id)
            by_symbol.setdefault(symbol_id, {"surface_ids": [], "capability_ids": [], "mapping_ids": [], "evidence_ids": []})
            by_symbol[symbol_id]["surface_ids"].append(surface_id)
            by_symbol[symbol_id]["capability_ids"].append(capability_id)
            by_symbol[symbol_id]["mapping_ids"].append(mapping["mapping_id"])
            by_symbol[symbol_id]["evidence_ids"].extend(evidence_ids)
        by_capability[capability_id]["mapping_ids"].append(mapping["mapping_id"])
        by_capability[capability_id]["evidence_ids"].extend(evidence_ids)

    return {
        "schema_version": TRACE_SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "created_at": now(),
        "by_surface": _dedupe_nested_lists(by_surface),
        "by_capability": _dedupe_nested_lists(by_capability),
        "by_symbol": _dedupe_nested_lists(by_symbol),
    }


def _build_summary(
    workspace_id: str,
    codebase_id: str,
    snapshot_id: str,
    surfaces: list[dict[str, Any]],
    mappings: list[dict[str, Any]],
    evidence_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    successful = [item for item in mappings if item.get("unresolved_reason") is None and float(item.get("confidence") or 0) >= SUCCESS_MAPPING_CONFIDENCE_MIN]
    successful_surface_ids = {str(item.get("from_id")) for item in successful}
    coverage_by_surface_type: dict[str, dict[str, Any]] = {}
    for surface_type in sorted({str(item.get("surface_type")) for item in surfaces}):
        total_ids = {str(item.get("surface_id")) for item in surfaces if item.get("surface_type") == surface_type}
        mapped_ids = total_ids & successful_surface_ids
        coverage_by_surface_type[surface_type] = {
            "total": len(total_ids),
            "mapped": len(mapped_ids),
            "ratio": round(len(mapped_ids) / len(total_ids), 4) if total_ids else 0.0,
        }

    evidence_by_capability: dict[str, dict[str, Any]] = {}
    for capability_id in sorted({str(item.get("capability_id") or "unresolved") for item in surfaces} | GOLDEN_CAPABILITIES):
        surface_ids = {str(item.get("surface_id")) for item in surfaces if item.get("capability_id") == capability_id}
        evidence_ids = {str(item.get("evidence_id")) for item in evidence_rows if item.get("capability_id") == capability_id}
        evidence_by_capability[capability_id] = {
            "surface_count": len(surface_ids),
            "evidence_count": len(evidence_ids),
            "covered": bool(evidence_ids),
            "needs_review": not bool(evidence_ids) and capability_id in GOLDEN_CAPABILITIES,
        }

    unresolved_reason_counts: dict[str, int] = {}
    for mapping in mappings:
        reason = mapping.get("unresolved_reason")
        if reason:
            unresolved_reason_counts[str(reason)] = unresolved_reason_counts.get(str(reason), 0) + 1

    golden_checks = {
        capability_id: {
            "passed": evidence_by_capability.get(capability_id, {}).get("covered", False),
            "evidence_count": evidence_by_capability.get(capability_id, {}).get("evidence_count", 0),
            "surface_count": evidence_by_capability.get(capability_id, {}).get("surface_count", 0),
        }
        for capability_id in sorted(GOLDEN_CAPABILITIES)
    }
    return {
        "schema_version": TRACE_SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "created_at": now(),
        "surface_count": len(surfaces),
        "mapping_count": len(mappings),
        "mapped_surface_count": len(successful_surface_ids),
        "unresolved_mapping_count": len([item for item in mappings if item.get("unresolved_reason")]),
        "evidence_count": len(evidence_rows),
        "mapping_coverage_by_surface_type": coverage_by_surface_type,
        "evidence_coverage_by_capability": evidence_by_capability,
        "success_mapping_confidence_min": SUCCESS_MAPPING_CONFIDENCE_MIN,
        "unresolved_reason_counts": unresolved_reason_counts,
        "golden_checks": golden_checks,
    }


def _select_trace(
    trace: dict[str, Any],
    *,
    surface_ids: set[str] | None = None,
    symbol_ids: set[str] | None = None,
    mapping_ids: set[str] | None = None,
    evidence_ids: set[str] | None = None,
) -> dict[str, Any]:
    surface_ids = surface_ids or set()
    symbol_ids = symbol_ids or set()
    mapping_ids = mapping_ids or set()
    evidence_ids = evidence_ids or set()
    mappings = [item for item in trace["mappings"] if item.get("mapping_id") in mapping_ids or item.get("from_id") in surface_ids]
    for mapping in mappings:
        if mapping.get("to_type") == "symbol" and mapping.get("to_id"):
            symbol_ids.add(str(mapping["to_id"]))
        evidence_ids.update(str(item) for item in mapping.get("evidence_ids") or [])
    return {
        "snapshot_id": trace["summary"].get("snapshot_id"),
        "surfaces": [item for item in trace["surfaces"] if item.get("surface_id") in surface_ids],
        "symbols": [item for item in trace["symbols"] if item.get("symbol_id") in symbol_ids],
        "mappings": mappings,
        "evidence": [item for item in trace["evidence"] if item.get("evidence_id") in evidence_ids],
    }


def _dedupe_by_key(rows: list[dict[str, Any]], key: str) -> list[dict[str, Any]]:
    by_key: dict[str, dict[str, Any]] = {}
    for row in rows:
        by_key.setdefault(str(row.get(key)), row)
    return [by_key[item] for item in sorted(by_key)]


def _dedupe_nested_lists(index: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for key, payload in sorted(index.items()):
        result[key] = {}
        for item_key, value in payload.items():
            if isinstance(value, list):
                result[key][item_key] = sorted(set(str(item) for item in value if str(item)))
            else:
                result[key][item_key] = value
    return result


def _line_range(value: Any) -> list[int] | None:
    if not isinstance(value, list) or len(value) != 2:
        return None
    try:
        start = int(value[0])
        end = int(value[1])
    except (TypeError, ValueError):
        return None
    if start < 1 or end < start:
        return None
    return [start, end]


def _line_range_valid(path: Path, line_range: list[int]) -> bool:
    if not path.is_file():
        return False
    try:
        line_count = len(path.read_text(encoding="utf-8").splitlines())
    except UnicodeDecodeError:
        return False
    return 1 <= line_range[0] <= line_count and 1 <= line_range[1] <= line_count


def _snippet(path: Path, line_range: list[int]) -> str | None:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except UnicodeDecodeError:
        return None
    selected = lines[line_range[0] - 1 : min(line_range[1], line_range[0] + 4)]
    text = "\n".join(selected).strip()
    return text[:500] if text else None


def _stable_id(prefix: str, *parts: Any) -> str:
    digest = hashlib.sha256(":".join(str(part) for part in parts).encode("utf-8")).hexdigest()[:16]
    return f"{prefix}_{digest}"
