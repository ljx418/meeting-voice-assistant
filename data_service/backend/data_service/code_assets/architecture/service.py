"""Service layer for V2.3 Architecture Abstraction."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from data_service.mcp_common import read_json

from ..artifacts import architecture_view_path, code_graph_json_path, inventory_surfaces_path, read_jsonl, snapshot_files_path, symbols_path
from ..registry import CodebaseRegistry
from ..snapshot import CodebaseSnapshotService
from .aligner import align_architecture_model
from .boundary_inferer import infer_boundaries
from .code_model_builder import build_code_derived_model
from .drift import build_design_code_drift
from .findings import build_findings
from .layer_inferer import infer_layers
from .model_builder import build_architecture_model
from .pattern_detector import detect_patterns
from .persistence import architecture_artifact_refs, code_architecture_artifact_refs, read_architecture_bundle, read_architecture_view, read_code_architecture_roles_layers, write_architecture_bundle, write_code_architecture_roles_layers
from .role_classifier import classify_code_roles
from .renderer import render_code_architecture_html, render_code_architecture_mermaid, render_html, render_mermaid
from .sources import discover_architecture_sources
from ..quality.persistence import read_plan


class ArchitectureService:
    def __init__(self, workspace: Path, *, workspace_id: str) -> None:
        self.workspace = Path(workspace)
        self.workspace_id = workspace_id
        self.registry = CodebaseRegistry(workspace, workspace_id=workspace_id)
        self.snapshots = CodebaseSnapshotService(workspace, workspace_id=workspace_id)

    def build_architecture(self, codebase_id: str, *, snapshot_id: str | None = None) -> dict[str, Any]:
        asset = self.registry.describe(codebase_id)
        if asset.status != "active":
            raise ValueError("CODEBASE_NOT_ACTIVE")
        resolved_snapshot_id = snapshot_id or self._latest_snapshot_id(codebase_id)
        self.snapshots.read_snapshot(codebase_id, resolved_snapshot_id)
        sources, parsed = discover_architecture_sources(workspace=self.workspace, workspace_id=self.workspace_id, codebase_id=codebase_id, snapshot_id=resolved_snapshot_id, root=Path(asset.root_path).expanduser().resolve())
        if not sources:
            raise FileNotFoundError("ARCHITECTURE_SOURCE_NOT_FOUND")
        model = build_architecture_model(workspace_id=self.workspace_id, codebase_id=codebase_id, snapshot_id=resolved_snapshot_id, sources=sources, parsed_sources=parsed)
        graph = read_json(code_graph_json_path(self.workspace, codebase_id), None)
        alignment = align_architecture_model(workspace_id=self.workspace_id, codebase_id=codebase_id, snapshot_id=resolved_snapshot_id, design_nodes=model["design_nodes"], graph=graph)
        findings = build_findings(workspace_id=self.workspace_id, codebase_id=codebase_id, snapshot_id=resolved_snapshot_id, design_nodes=model["design_nodes"], alignment=alignment)
        summary = dict(model["summary"])
        summary.update(
            {
                "match_count": alignment["summary"]["match_count"],
                "unmatched_design_count": alignment["summary"]["unmatched_design_count"],
                "finding_count": len(findings),
                "artifact_refs": architecture_artifact_refs(codebase_id),
            }
        )
        bundle = {
            "sources": sources,
            "design_nodes": model["design_nodes"],
            "design_edges": model["design_edges"],
            "model": model,
            "alignment": alignment,
            "findings": findings,
            "summary": summary,
            "artifact_refs": architecture_artifact_refs(codebase_id),
        }
        write_architecture_bundle(self.workspace, codebase_id, bundle, render_mermaid(model, alignment), render_html(model, alignment, findings))
        return bundle

    def read_architecture(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        bundle = read_architecture_bundle(self.workspace, codebase_id)
        bundle["artifact_refs"] = architecture_artifact_refs(codebase_id)
        return bundle

    def read_view(self, codebase_id: str, view_id: str) -> dict[str, Any]:
        bundle = self.read_architecture(codebase_id)
        content = read_architecture_view(self.workspace, codebase_id, view_id)
        return {"snapshot_id": bundle["model"]["snapshot_id"], "view_id": view_id, "content": content}

    def build_code_architecture(self, codebase_id: str, *, snapshot_id: str | None = None) -> dict[str, Any]:
        asset = self.registry.describe(codebase_id)
        if asset.status != "active":
            raise ValueError("CODEBASE_NOT_ACTIVE")
        resolved_snapshot_id = snapshot_id or self._latest_snapshot_id(codebase_id)
        self.snapshots.read_snapshot(codebase_id, resolved_snapshot_id)
        files = read_jsonl(snapshot_files_path(self.workspace, codebase_id, resolved_snapshot_id))
        surfaces = read_jsonl(inventory_surfaces_path(self.workspace, codebase_id, resolved_snapshot_id))
        symbols = read_jsonl(symbols_path(self.workspace, codebase_id, resolved_snapshot_id))
        if not surfaces:
            raise FileNotFoundError("INVENTORY_NOT_FOUND")
        if not symbols:
            raise FileNotFoundError("SYMBOL_INDEX_NOT_FOUND")
        refs = code_architecture_artifact_refs(codebase_id)
        source_refs = [
            {"type": "snapshot_files", "artifact_ref": f"snapshot-files://{codebase_id}/{resolved_snapshot_id}"},
            {"type": "inventory_surfaces", "artifact_ref": f"inventory-surfaces://{codebase_id}/{resolved_snapshot_id}"},
            {"type": "symbols", "artifact_ref": f"symbols://{codebase_id}/{resolved_snapshot_id}"},
        ]
        roles = classify_code_roles(
            workspace_id=self.workspace_id,
            codebase_id=codebase_id,
            snapshot_id=resolved_snapshot_id,
            files=files,
            surfaces=surfaces,
            symbols=symbols,
            source_artifact_refs=source_refs,
        )
        layers = infer_layers(workspace_id=self.workspace_id, codebase_id=codebase_id, snapshot_id=resolved_snapshot_id, roles=roles, source_artifact_refs=source_refs)
        boundaries = infer_boundaries(workspace_id=self.workspace_id, codebase_id=codebase_id, snapshot_id=resolved_snapshot_id, roles=roles, source_artifact_refs=source_refs)
        patterns = detect_patterns(workspace_id=self.workspace_id, codebase_id=codebase_id, snapshot_id=resolved_snapshot_id, roles=roles, source_artifact_refs=source_refs)
        summary = _code_architecture_summary(self.workspace_id, codebase_id, resolved_snapshot_id, roles, layers, boundaries, patterns)
        code_model = build_code_derived_model(workspace_id=self.workspace_id, codebase_id=codebase_id, snapshot_id=resolved_snapshot_id, roles=roles, layers=layers, boundaries=boundaries, patterns=patterns, summary=summary, source_artifact_refs=source_refs)
        drift = build_design_code_drift(workspace_id=self.workspace_id, codebase_id=codebase_id, snapshot_id=resolved_snapshot_id, design_nodes=_read_design_nodes_if_available(self.workspace, codebase_id), code_model=code_model)
        summary["drift_count"] = len(drift)
        code_model["summary"] = summary
        write_code_architecture_roles_layers(self.workspace, codebase_id, roles, layers, boundaries, patterns, code_model, drift)
        _write_code_architecture_views(self.workspace, codebase_id, code_model, drift)
        return {
            "schema_version": "v2.4",
            "workspace_id": self.workspace_id,
            "codebase_id": codebase_id,
            "snapshot_id": resolved_snapshot_id,
            "roles": roles,
            "layers": layers,
            "boundaries": boundaries,
            "patterns": patterns,
            "code_model": code_model,
            "drift": drift,
            "summary": summary,
            "artifact_refs": refs,
        }

    def read_code_architecture(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        payload = read_code_architecture_roles_layers(self.workspace, codebase_id)
        snapshot_id = _snapshot_id_from_roles_layers(payload)
        result = {
            "schema_version": "v2.4",
            "workspace_id": self.workspace_id,
            "codebase_id": codebase_id,
            "snapshot_id": snapshot_id,
            "roles": payload["roles"],
            "layers": payload["layers"],
            "boundaries": payload.get("boundaries", []),
            "patterns": payload.get("patterns", []),
            "code_model": payload.get("code_model", {}),
            "drift": payload.get("drift", []),
            "summary": _summary_from_payload_or_build(self.workspace_id, codebase_id, snapshot_id, payload),
            "artifact_refs": code_architecture_artifact_refs(codebase_id),
        }
        return _apply_quality_plan_to_architecture_payload(self.workspace, codebase_id, result)

    def read_code_view(self, codebase_id: str, view_id: str) -> dict[str, Any]:
        payload = self.read_code_architecture(codebase_id)
        normalized = _normalize_code_view_id(view_id)
        content = read_architecture_view(self.workspace, codebase_id, normalized)
        return {"snapshot_id": payload["snapshot_id"], "view_id": normalized, "content": content}

    def _latest_snapshot_id(self, codebase_id: str) -> str:
        snapshots = self.snapshots.list_snapshots(codebase_id, limit=1)
        if not snapshots:
            raise FileNotFoundError("SNAPSHOT_NOT_FOUND")
        return str(snapshots[0]["snapshot_id"])


def public_architecture_payload(bundle: dict[str, Any]) -> dict[str, Any]:
    return {
        "summary": bundle.get("summary", {}),
        "sources": bundle.get("sources", []),
        "model": {
            "schema_version": bundle.get("model", {}).get("schema_version"),
            "workspace_id": bundle.get("model", {}).get("workspace_id"),
            "codebase_id": bundle.get("model", {}).get("codebase_id"),
            "snapshot_id": bundle.get("model", {}).get("snapshot_id"),
            "design_nodes": bundle.get("design_nodes", []),
            "design_edges": bundle.get("design_edges", []),
        },
        "alignment": bundle.get("alignment", {}),
        "findings": bundle.get("findings", []),
    }


def public_code_architecture_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": payload.get("schema_version"),
        "workspace_id": payload.get("workspace_id"),
        "codebase_id": payload.get("codebase_id"),
        "snapshot_id": payload.get("snapshot_id"),
        "summary": payload.get("summary", {}),
        "roles": payload.get("roles", []),
        "layers": payload.get("layers", []),
        "boundaries": payload.get("boundaries", []),
        "patterns": payload.get("patterns", []),
        "code_model": payload.get("code_model", {}),
        "drift": payload.get("drift", []),
        "artifact_refs": payload.get("artifact_refs", []),
    }


def _snapshot_id_from_roles_layers(payload: dict[str, Any]) -> str | None:
    for collection in (payload.get("roles") or [], payload.get("layers") or []):
        for item in collection:
            if isinstance(item, dict) and item.get("snapshot_id"):
                return str(item["snapshot_id"])
    return None


def _code_architecture_summary(
    workspace_id: str,
    codebase_id: str,
    snapshot_id: str | None,
    roles: list[dict[str, Any]],
    layers: list[dict[str, Any]],
    boundaries: list[dict[str, Any]] | None = None,
    patterns: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    role_counts: dict[str, int] = {}
    layer_counts: dict[str, int] = {}
    boundary_counts: dict[str, int] = {}
    pattern_counts: dict[str, int] = {}
    high_confidence_without_evidence = 0
    needs_review_count = 0
    for role in roles:
        role_type = str(role.get("role_type") or "unknown")
        role_counts[role_type] = role_counts.get(role_type, 0) + 1
        if float(role.get("confidence") or 0) >= 0.8 and not role.get("evidence"):
            high_confidence_without_evidence += 1
        if role.get("needs_review"):
            needs_review_count += 1
    for layer in layers:
        layer_type = str(layer.get("layer_type") or "unknown")
        layer_counts[layer_type] = layer_counts.get(layer_type, 0) + 1
        if layer.get("needs_review"):
            needs_review_count += 1
    for boundary in boundaries or []:
        boundary_type = str(boundary.get("boundary_type") or "unknown")
        boundary_counts[boundary_type] = boundary_counts.get(boundary_type, 0) + 1
        if float(boundary.get("confidence") or 0) >= 0.8 and not boundary.get("evidence"):
            high_confidence_without_evidence += 1
        if boundary.get("needs_review"):
            needs_review_count += 1
    for pattern in patterns or []:
        pattern_type = str(pattern.get("pattern_type") or "unknown")
        pattern_counts[pattern_type] = pattern_counts.get(pattern_type, 0) + 1
        if float(pattern.get("confidence") or 0) >= 0.8 and not pattern.get("evidence"):
            high_confidence_without_evidence += 1
        if pattern.get("needs_review"):
            needs_review_count += 1
    return {
        "schema_version": "v2.4",
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "role_count": len(roles),
        "layer_count": len(layers),
        "boundary_count": len(boundaries or []),
        "pattern_count": len(patterns or []),
        "role_counts": role_counts,
        "layer_counts": layer_counts,
        "boundary_counts": boundary_counts,
        "pattern_counts": pattern_counts,
        "needs_review_count": needs_review_count,
        "high_confidence_without_evidence": high_confidence_without_evidence,
    }


def _read_design_nodes_if_available(workspace: Path, codebase_id: str) -> list[dict[str, Any]]:
    try:
        return read_architecture_bundle(workspace, codebase_id).get("design_nodes", [])
    except FileNotFoundError:
        return []


def _summary_from_payload_or_build(workspace_id: str, codebase_id: str, snapshot_id: str | None, payload: dict[str, Any]) -> dict[str, Any]:
    code_model = payload.get("code_model") or {}
    summary = code_model.get("summary")
    if isinstance(summary, dict) and summary:
        return summary
    built = _code_architecture_summary(workspace_id, codebase_id, snapshot_id, payload["roles"], payload["layers"], payload.get("boundaries", []), payload.get("patterns", []))
    built["drift_count"] = len(payload.get("drift", []))
    return built


def _apply_quality_plan_to_architecture_payload(workspace: Path, codebase_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    plan = read_plan(workspace, codebase_id)
    overlays = plan.get("read_time_overlays") if isinstance(plan, dict) else None
    if not overlays:
        return payload
    by_target: dict[tuple[str, str], dict[str, Any]] = {}
    for overlay in overlays:
        if isinstance(overlay, dict):
            by_target[(str(overlay.get("target_type") or ""), str(overlay.get("target_id") or ""))] = overlay
    collection_specs = [
        ("roles", "architecture_role", "role_id"),
        ("layers", "architecture_layer", "layer_id"),
        ("boundaries", "architecture_boundary", "boundary_id"),
        ("patterns", "architecture_pattern", "pattern_id"),
        ("drift", "architecture_drift_finding", "finding_id"),
    ]
    for collection_name, target_type, id_key in collection_specs:
        updated = []
        for item in payload.get(collection_name, []) or []:
            if not isinstance(item, dict):
                updated.append(item)
                continue
            overlay = by_target.get((target_type, str(item.get(id_key) or "")))
            if overlay:
                item = dict(item)
                item["applied_rules"] = list(overlay.get("applied_rules") or [])
                item["governed_by"] = list(overlay.get("governed_by") or [])
            updated.append(item)
        payload[collection_name] = updated
    return payload


def _write_code_architecture_views(workspace: Path, codebase_id: str, code_model: dict[str, Any], drift: list[dict[str, Any]]) -> None:
    mmd = architecture_view_path(workspace, codebase_id, "code_derived_architecture.mmd")
    html_path = architecture_view_path(workspace, codebase_id, "code_derived_architecture.html")
    mmd.parent.mkdir(parents=True, exist_ok=True)
    mmd.write_text(render_code_architecture_mermaid(code_model, drift), encoding="utf-8")
    html_path.write_text(render_code_architecture_html(code_model, drift), encoding="utf-8")


def _normalize_code_view_id(view_id: str) -> str:
    requested = str(view_id or "code_derived_architecture.html")
    if requested in {"html", "code", "code.html"}:
        return "code_derived_architecture.html"
    if requested in {"mmd", "mermaid", "code.mmd"}:
        return "code_derived_architecture.mmd"
    if requested in {"code_derived_architecture.html", "code_derived_architecture.mmd"}:
        return requested
    raise FileNotFoundError("ARCHITECTURE_VIEW_NOT_FOUND")
