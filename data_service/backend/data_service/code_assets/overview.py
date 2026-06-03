"""Project overview artifacts for V2 codebase assets."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from data_service.mcp_common import now, read_json, write_json

from .artifacts import overview_path, read_jsonl, snapshot_files_path
from .inventory import CodebaseInventoryService, inventory_artifact_refs
from .registry import CodebaseRegistry
from .snapshot import CodebaseSnapshotService, public_snapshot
from .symbols import CodebaseSymbolIndexService, symbol_artifact_refs
from .trace import CodebaseTraceService, public_evidence_payload, trace_artifact_refs


OVERVIEW_SCHEMA_VERSION = "v2.0"


class CodebaseOverviewService:
    def __init__(self, workspace: Path, *, workspace_id: str) -> None:
        self.workspace = workspace
        self.workspace_id = workspace_id
        self.registry = CodebaseRegistry(workspace, workspace_id=workspace_id)
        self.snapshots = CodebaseSnapshotService(workspace, workspace_id=workspace_id)
        self.inventory = CodebaseInventoryService(workspace, workspace_id=workspace_id)
        self.symbols = CodebaseSymbolIndexService(workspace, workspace_id=workspace_id)
        self.trace = CodebaseTraceService(workspace, workspace_id=workspace_id)

    def build_overview(self, codebase_id: str, *, snapshot_id: str | None = None) -> dict[str, Any]:
        asset = self.registry.describe(codebase_id)
        if asset.status != "active":
            raise ValueError("CODEBASE_NOT_ACTIVE")
        resolved_snapshot_id = snapshot_id or self._latest_snapshot_id(codebase_id)
        snapshot = self.snapshots.read_snapshot(codebase_id, resolved_snapshot_id)
        inventory = self.inventory.read_inventory(codebase_id, snapshot_id=resolved_snapshot_id)
        symbol_index = self.symbols.read_symbol_index(codebase_id, snapshot_id=resolved_snapshot_id)
        trace = self.trace.read_trace(codebase_id, snapshot_id=resolved_snapshot_id)
        files = read_jsonl(snapshot_files_path(self.workspace, codebase_id, resolved_snapshot_id))

        snapshot_public = public_snapshot(snapshot)
        summary = inventory["summary"]
        symbol_summary = symbol_index["summary"]
        trace_summary = trace["summary"]
        evidence = _overview_evidence(codebase_id, resolved_snapshot_id, snapshot_public, inventory, symbol_index, trace)
        needs_review = _needs_review(summary, symbol_summary, trace_summary)
        core_modules = _core_modules(symbol_index["symbols"], symbol_index["imports"], trace["evidence"])
        entrypoints = _entrypoints(snapshot_public.get("important_paths") or {}, files)
        public_surface_summary = _public_surface_summary(summary, inventory["alignment_matrix"], inventory["capabilities"])
        known_risks = _known_risks(summary, symbol_summary, trace_summary, needs_review)
        overview = {
            "schema_version": OVERVIEW_SCHEMA_VERSION,
            "workspace_id": self.workspace_id,
            "codebase_id": codebase_id,
            "snapshot_id": resolved_snapshot_id,
            "created_at": now(),
            "project_one_liner": _one_liner(asset.name, snapshot_public, summary),
            "entrypoints": entrypoints,
            "public_surface_summary": public_surface_summary,
            "language_stats": snapshot_public.get("stats") or {},
            "important_paths": snapshot_public.get("important_paths") or {},
            "core_modules": core_modules,
            "storage_summary": _storage_summary(codebase_id, resolved_snapshot_id),
            "known_risks": known_risks,
            "evidence": evidence,
            "needs_review": needs_review,
            "confidence": _confidence(needs_review),
            "artifact_refs": overview_artifact_refs(codebase_id),
            "source_artifact_refs": [
                *(snapshot_public.get("artifact_refs") or []),
                *inventory_artifact_refs(codebase_id, resolved_snapshot_id),
                *symbol_artifact_refs(codebase_id, resolved_snapshot_id),
                *trace_artifact_refs(codebase_id, resolved_snapshot_id),
            ],
        }
        write_json(overview_path(self.workspace, codebase_id), overview)
        return overview

    def read_overview(self, codebase_id: str, *, snapshot_id: str | None = None, build_if_missing: bool = True) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        payload = read_json(overview_path(self.workspace, codebase_id), None)
        if payload and (snapshot_id is None or payload.get("snapshot_id") == snapshot_id):
            return payload
        if build_if_missing:
            return self.build_overview(codebase_id, snapshot_id=snapshot_id)
        raise FileNotFoundError("OVERVIEW_NOT_FOUND")

    def _latest_snapshot_id(self, codebase_id: str) -> str:
        snapshots = self.snapshots.list_snapshots(codebase_id, limit=1)
        if not snapshots:
            raise FileNotFoundError("SNAPSHOT_NOT_FOUND")
        return str(snapshots[0]["snapshot_id"])


def overview_artifact_refs(codebase_id: str) -> list[dict[str, str]]:
    return [{"type": "project_overview", "artifact_ref": f"overview://{codebase_id}"}]


def public_overview_payload(overview: dict[str, Any]) -> dict[str, Any]:
    payload = dict(overview)
    payload["evidence"] = [public_evidence_payload(item) if "path" in item else item for item in payload.get("evidence", [])]
    return payload


def _one_liner(name: str, snapshot: dict[str, Any], inventory_summary: dict[str, Any]) -> str:
    stats = snapshot.get("stats") or {}
    languages = stats.get("languages") or {}
    main_language = max(languages.items(), key=lambda item: int(item[1].get("loc") or 0))[0] if languages else "multi-language"
    surface_count = int(inventory_summary.get("surface_count") or 0)
    return f"{name} is a local project intelligence codebase with {surface_count} public surfaces and {main_language} as its largest detected language."


def _entrypoints(important_paths: dict[str, list[str]], files: list[dict[str, Any]]) -> list[dict[str, Any]]:
    file_index = {str(item.get("path")): item for item in files}
    entries = []
    for path in important_paths.get("entrypoints", [])[:20]:
        record = file_index.get(path, {})
        entries.append(
            {
                "path": path,
                "language": record.get("language"),
                "loc": record.get("loc"),
                "evidence": [_path_evidence(path, "snapshot_entrypoint_detector")],
            }
        )
    return entries


def _public_surface_summary(summary: dict[str, Any], alignment: dict[str, Any], capabilities: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "surface_count": summary.get("surface_count", 0),
        "surface_counts": summary.get("surface_counts", {}),
        "capability_count": summary.get("capability_count", 0),
        "alignment_capability_count": summary.get("alignment_capability_count", 0),
        "unresolved_count": summary.get("unresolved_count", 0),
        "unresolved_ratio": summary.get("unresolved_ratio", 0),
        "top_capabilities": [
            {
                "capability_id": item.get("capability_id"),
                "surface_count": item.get("surface_count"),
                "surface_types": item.get("surface_types"),
            }
            for item in capabilities[:12]
        ],
        "alignment_matrix_summary": {
            "capabilities": len((alignment.get("capabilities") or {})) if isinstance(alignment, dict) else 0,
        },
        "evidence": [_artifact_evidence("inventory_summary", "inventory_summary.json")],
    }


def _core_modules(symbols: list[dict[str, Any]], imports: list[dict[str, Any]], evidence_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    import_degree: dict[str, int] = {}
    for item in imports:
        for key in ("from_module", "to_module"):
            module = str(item.get(key) or "")
            if module:
                import_degree[module] = import_degree.get(module, 0) + 1
    evidence_by_file = {str(item.get("path") or item.get("source_file") or ""): item for item in evidence_rows}
    modules = [item for item in symbols if item.get("kind") == "module"]
    ranked = sorted(
        modules,
        key=lambda item: (-import_degree.get(str(item.get("qualified_name")), 0), str(item.get("path") or "")),
    )
    result = []
    for module in ranked[:12]:
        path = str(module.get("path") or module.get("source_file") or "")
        evidence = evidence_by_file.get(path)
        result.append(
            {
                "symbol_id": module.get("symbol_id"),
                "qualified_name": module.get("qualified_name"),
                "source_file": path,
                "import_degree": import_degree.get(str(module.get("qualified_name")), 0),
                "evidence": [public_evidence_payload(evidence)] if evidence else [_path_evidence(path, "python_symbol_index")],
            }
        )
    return result


def _storage_summary(codebase_id: str, snapshot_id: str) -> dict[str, Any]:
    return {
        "codebase_artifact_root": f"workspace/assets/codebase/{codebase_id}",
        "snapshot_artifact_root": f"workspace/assets/codebase/{codebase_id}/snapshots/{snapshot_id}",
        "overview_artifact": f"workspace/assets/codebase/{codebase_id}/overview.json",
        "agent_context_root": f"workspace/assets/codebase/{codebase_id}/agent_context",
        "evidence": [_artifact_evidence("artifact_layout", "workspace/assets/codebase/{codebase_id}")],
    }


def _known_risks(summary: dict[str, Any], symbol_summary: dict[str, Any], trace_summary: dict[str, Any], needs_review: list[dict[str, Any]]) -> list[dict[str, Any]]:
    risks: list[dict[str, Any]] = []
    if int(summary.get("unresolved_count") or 0) > 0:
        risks.append(
            {
                "risk_id": "unresolved_public_surfaces",
                "summary": "Some public surfaces could not be assigned to a normalized capability.",
                "evidence": [_artifact_evidence("inventory_summary", "inventory_summary.json")],
            }
        )
    if int(trace_summary.get("unresolved_mapping_count") or 0) > 0:
        risks.append(
            {
                "risk_id": "unresolved_surface_mappings",
                "summary": "Some public surfaces could not be mapped to concrete symbols with high confidence.",
                "evidence": [_artifact_evidence("mapping_summary", "mapping_summary.json")],
            }
        )
    if int(symbol_summary.get("syntax_error_count") or 0) > 0:
        risks.append(
            {
                "risk_id": "syntax_error_symbols",
                "summary": "Some Python files could not be parsed for symbols.",
                "evidence": [_artifact_evidence("symbol_summary", "symbol_summary.json")],
            }
        )
    for item in needs_review[:5]:
        risks.append({"risk_id": item.get("code"), "summary": item.get("reason"), "needs_review": True, "evidence": item.get("evidence", [])})
    return risks


def _overview_evidence(
    codebase_id: str,
    snapshot_id: str,
    snapshot: dict[str, Any],
    inventory: dict[str, Any],
    symbol_index: dict[str, Any],
    trace: dict[str, Any],
) -> list[dict[str, Any]]:
    evidence: list[dict[str, Any]] = [
        _artifact_evidence("snapshot", f"workspace/assets/codebase/{codebase_id}/snapshots/{snapshot_id}/snapshot.json"),
        _artifact_evidence("inventory_summary", f"workspace/assets/codebase/{codebase_id}/snapshots/{snapshot_id}/inventory_summary.json"),
        _artifact_evidence("symbol_summary", f"workspace/assets/codebase/{codebase_id}/snapshots/{snapshot_id}/symbol_summary.json"),
        _artifact_evidence("mapping_summary", f"workspace/assets/codebase/{codebase_id}/snapshots/{snapshot_id}/mapping_summary.json"),
    ]
    for path in (snapshot.get("important_paths") or {}).get("entrypoints", [])[:8]:
        evidence.append(_path_evidence(path, "snapshot_entrypoint_detector"))
    for row in trace.get("evidence", [])[:20]:
        evidence.append(public_evidence_payload(row))
    return _dedupe_evidence(evidence)


def _needs_review(summary: dict[str, Any], symbol_summary: dict[str, Any], trace_summary: dict[str, Any]) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    if float(summary.get("unresolved_ratio") or 0) > 0:
        items.append(
            {
                "code": "UNRESOLVED_CAPABILITIES",
                "reason": "Inventory has public surfaces that need capability review.",
                "evidence": [_artifact_evidence("inventory_summary", "inventory_summary.json")],
            }
        )
    if int(trace_summary.get("unresolved_mapping_count") or 0) > 0:
        items.append(
            {
                "code": "UNRESOLVED_MAPPINGS",
                "reason": "Trace has surface-to-symbol mappings that need review.",
                "evidence": [_artifact_evidence("mapping_summary", "mapping_summary.json")],
            }
        )
    if int(symbol_summary.get("syntax_error_count") or 0) > 0:
        items.append(
            {
                "code": "SYMBOL_PARSE_WARNINGS",
                "reason": "Symbol extraction reported parse warnings.",
                "evidence": [_artifact_evidence("symbol_summary", "symbol_summary.json")],
            }
        )
    return items


def _confidence(needs_review: list[dict[str, Any]]) -> float:
    return max(0.5, round(0.92 - (0.05 * len(needs_review)), 2))


def _artifact_evidence(kind: str, artifact: str) -> dict[str, Any]:
    return {
        "evidence_id": f"artifact:{kind}",
        "kind": "artifact",
        "artifact": artifact,
        "extractor": "project_overview",
        "confidence": 1.0,
    }


def _path_evidence(path: str, extractor: str) -> dict[str, Any]:
    return {
        "evidence_id": f"path:{path}",
        "kind": "path",
        "source_file": path,
        "extractor": extractor,
        "confidence": 1.0,
    }


def _dedupe_evidence(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen = set()
    result = []
    for item in items:
        key = str(item.get("evidence_id") or item.get("artifact") or item.get("source_file"))
        if key in seen:
            continue
        seen.add(key)
        result.append(item)
    return result
