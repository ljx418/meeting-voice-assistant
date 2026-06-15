"""Service layer for V2.3 Architecture Abstraction."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from data_service.mcp_common import read_json

from ..artifacts import architecture_view_path, code_graph_json_path, evidence_path, imports_path, inventory_surfaces_path, read_jsonl, snapshot_files_path, symbols_path
from ..registry import CodebaseRegistry
from ..snapshot import CodebaseSnapshotService
from .aligner import align_architecture_model
from .boundary_inferer import infer_boundaries
from .code_fact_chains import build_code_fact_chains, public_code_fact_chain_payload
from .code_relationships_v2 import build_code_relationships_v2, public_code_relationships_v2_payload as public_code_relationships_v2_payload_impl
from .context_pack_v3 import build_architecture_context_pack_v3, public_architecture_context_pack_v3_payload as public_architecture_context_pack_v3_payload_impl
from .context_pack_v2 import build_architecture_context_pack_v2, public_architecture_context_pack_v2_payload as public_architecture_context_pack_v2_payload_impl
from .code_model_builder import build_code_derived_model
from .doc_claim_extractor import build_document_claims, public_document_claims_payload
from .doc_code_alignment import build_document_code_alignment, public_document_code_alignment_payload
from .doc_quality import build_document_quality, public_document_quality_payload
from .doc_registry import build_document_registry, public_document_registry_payload
from .document_semantics_v3 import build_document_semantics_v3, public_document_semantics_v3_payload, read_document_semantics_v3
from .drift import build_design_code_drift
from .findings import build_findings
from .inventory_extractors import build_architecture_inventory, public_inventory_payload
from .language_provider_v2 import build_language_provider_artifacts, public_language_provider_payload, read_language_provider_artifacts
from .large_project_views import HTML_VIEW_ID, MERMAID_VIEW_ID, build_architecture_summary, render_key_boundaries_mermaid, render_large_project_html
from .layer_inferer import infer_layers
from .model_builder import build_architecture_model
from .pattern_detector import detect_patterns
from .pattern_evidence_v2 import build_pattern_evidence_v2, public_pattern_blockers_payload as public_pattern_blockers_payload_impl, public_pattern_evidence_payload as public_pattern_evidence_payload_impl, public_pattern_view_payload as public_pattern_view_payload_impl
from .profile_taxonomy_regression import build_profile_taxonomy_regression, public_profile_taxonomy_regression_payload, read_profile_taxonomy_regression
from .graph_aggregation import build_architecture_graph_aggregation, public_architecture_graph_aggregation_payload
from .human_review_report_v2 import HTML_VIEW_ID as HUMAN_REPORT_HTML_VIEW_ID, build_human_review_report_v2, public_human_review_report_v2_payload as public_human_review_report_v2_payload_impl, public_human_review_report_view_v2_payload as public_human_review_report_view_v2_payload_impl
from .persistence import architecture_artifact_refs, architecture_code_fact_chain_artifact_refs, architecture_context_pack_v2_artifact_refs, architecture_context_pack_v3_artifact_refs, architecture_doc_claim_artifact_refs, architecture_doc_code_alignment_artifact_refs, architecture_doc_quality_artifact_refs, architecture_doc_registry_artifact_refs, architecture_document_semantics_v243_artifact_refs, architecture_graph_v28_artifact_refs, architecture_human_report_v29_artifact_refs, architecture_intent_evidence_artifact_refs, architecture_inventory_artifact_refs, architecture_pattern_evidence_v210_artifact_refs, architecture_public_surface_evidence_v29_artifact_refs, architecture_reading_dashboard_artifact_refs, architecture_reconstructed_artifact_refs, architecture_relationship_chains_v242_artifact_refs, architecture_relationships_v29_artifact_refs, architecture_scale_artifact_refs, architecture_signal_ranking_artifact_refs, architecture_signal_ranking_v29_artifact_refs, architecture_taxonomy_artifact_refs, code_architecture_artifact_refs, read_architecture_bundle, read_architecture_code_fact_chains, read_architecture_config_inventory, read_architecture_context_pack_v2, read_architecture_context_pack_v3, read_architecture_deployment_inventory, read_architecture_doc_claims, read_architecture_doc_code_alignment, read_architecture_doc_quality, read_architecture_doc_registry, read_architecture_doc_view, read_architecture_graph_v28, read_architecture_graph_view_v28, read_architecture_human_report_v29, read_architecture_human_report_view_v29, read_architecture_intent_evidence, read_architecture_inventory, read_architecture_language_facts, read_architecture_pattern_evidence_v210, read_architecture_pattern_evidence_v210_view, read_architecture_public_surface_evidence_v29, read_architecture_reading_dashboard, read_architecture_reconstructed_model, read_architecture_relationships_v29, read_architecture_review_queue, read_architecture_scale_profile, read_architecture_schema_inventory, read_architecture_signal_ranking, read_architecture_signal_ranking_v29, read_architecture_taxonomy, read_architecture_v28_view, read_architecture_view, read_code_architecture_roles_layers, write_architecture_bundle, write_architecture_code_fact_chains, write_architecture_context_pack_v2, write_architecture_context_pack_v3, write_architecture_doc_claims, write_architecture_doc_code_alignment, write_architecture_doc_quality, write_architecture_doc_registry, write_architecture_graph_v28, write_architecture_human_report_v29, write_architecture_intent_evidence, write_architecture_inventory, write_architecture_pattern_evidence_v210, write_architecture_public_surface_evidence_v29, write_architecture_reading_dashboard, write_architecture_reconstructed_model, write_architecture_relationships_v29, write_architecture_review_queue, write_architecture_scale_profile, write_architecture_signal_ranking, write_architecture_signal_ranking_v29, write_architecture_taxonomy, write_code_architecture_roles_layers
from .ranking_intent import build_intent_evidence, build_signal_ranking, public_intent_evidence_payload, public_signal_ranking_payload
from .ranking_calibration_v2 import build_ranking_calibration_v2, public_ranking_calibration_v2_payload as public_ranking_calibration_v2_payload_impl
from .reading_dashboard import HTML_VIEW_ID as READING_DASHBOARD_HTML_VIEW_ID, MERMAID_VIEW_ID as READING_DASHBOARD_MERMAID_VIEW_ID, build_architecture_reading_dashboard, public_architecture_reading_dashboard_payload, render_architecture_reading_dashboard_html, render_architecture_relationship_summary_mermaid
from .relationship_chains_v3 import build_relationship_chains_v3, public_relationship_chains_v3_payload, read_relationship_chains_v3
from .reconstruction import HTML_VIEW_ID as RECONSTRUCTED_HTML_VIEW_ID, MERMAID_VIEW_ID as RECONSTRUCTED_MERMAID_VIEW_ID, build_reconstructed_architecture_model, public_reconstructed_architecture_payload, render_reconstructed_architecture_html, render_reconstructed_architecture_mermaid
from .review_queue import build_review_queue, public_review_queue_payload
from .role_classifier import classify_code_roles
from .renderer import render_code_architecture_html, render_code_architecture_mermaid, render_html, render_mermaid
from .scale_profile import build_architecture_scale_profile, public_scale_profile_payload, read_scale_shard_page
from .surface_evidence_v2 import build_public_surface_evidence_v2, public_public_surface_evidence_v2_payload as public_public_surface_evidence_v2_payload_impl
from .sources import discover_architecture_sources
from .taxonomy import build_default_taxonomy
from .token_context_cache import build_optimized_context_pack, public_optimized_context_pack_payload
from .workflow_runtime_v2 import build_workflow_runtime_candidates, public_workflow_runtime_payload, read_workflow_runtime_candidates
from .persistence import architecture_context_pack_optimized_v244_artifact_refs, read_architecture_context_pack_optimized_v244, write_architecture_context_pack_optimized_v244
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

    def build_scale_profile(self, codebase_id: str, *, snapshot_id: str | None = None, budget: dict[str, Any] | None = None) -> dict[str, Any]:
        asset = self.registry.describe(codebase_id)
        if asset.status != "active":
            raise ValueError("CODEBASE_NOT_ACTIVE")
        resolved_snapshot_id = snapshot_id or self._latest_snapshot_id(codebase_id)
        snapshot = self.snapshots.read_snapshot(codebase_id, resolved_snapshot_id)
        files = read_jsonl(snapshot_files_path(self.workspace, codebase_id, resolved_snapshot_id))
        if not files:
            raise FileNotFoundError("SNAPSHOT_FILES_NOT_FOUND")
        profile = build_architecture_scale_profile(
            workspace=self.workspace,
            workspace_id=self.workspace_id,
            codebase_id=codebase_id,
            snapshot_id=resolved_snapshot_id,
            snapshot=snapshot,
            files=files,
            budget=budget,
        )
        write_architecture_scale_profile(self.workspace, codebase_id, profile)
        return profile

    def read_scale_profile(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        return read_architecture_scale_profile(self.workspace, codebase_id)

    def read_scale_shard(self, codebase_id: str, *, shard: str = "files", page: int = 1, page_size: int = 100) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        return read_scale_shard_page(self.workspace, codebase_id, shard=shard, page=page, page_size=page_size)

    def build_inventory(self, codebase_id: str, *, snapshot_id: str | None = None) -> dict[str, Any]:
        asset = self.registry.describe(codebase_id)
        if asset.status != "active":
            raise ValueError("CODEBASE_NOT_ACTIVE")
        resolved_snapshot_id = snapshot_id or self._latest_snapshot_id(codebase_id)
        self.snapshots.read_snapshot(codebase_id, resolved_snapshot_id)
        files = read_jsonl(snapshot_files_path(self.workspace, codebase_id, resolved_snapshot_id))
        if not files:
            raise FileNotFoundError("SNAPSHOT_FILES_NOT_FOUND")
        source_refs = [
            {"type": "snapshot_files", "artifact_ref": f"snapshot-files://{codebase_id}/{resolved_snapshot_id}"},
            {"type": "architecture_scale_profile", "artifact_ref": f"architecture://{codebase_id}/architecture_scale_profile.json"},
        ]
        payload = build_architecture_inventory(
            workspace_id=self.workspace_id,
            codebase_id=codebase_id,
            snapshot_id=resolved_snapshot_id,
            root=Path(asset.root_path).expanduser().resolve(),
            files=files,
            source_artifact_refs=source_refs,
        )
        write_architecture_inventory(self.workspace, codebase_id, **payload)
        return {
            "schema_version": "v2.6",
            "workspace_id": self.workspace_id,
            "codebase_id": codebase_id,
            "snapshot_id": resolved_snapshot_id,
            **payload,
            "artifact_refs": architecture_inventory_artifact_refs(codebase_id),
        }

    def read_inventory(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        payload = read_architecture_inventory(self.workspace, codebase_id)
        snapshot_id = _snapshot_id_from_inventory(payload)
        return {
            "schema_version": "v2.6",
            "workspace_id": self.workspace_id,
            "codebase_id": codebase_id,
            "snapshot_id": snapshot_id,
            **payload,
            "artifact_refs": architecture_inventory_artifact_refs(codebase_id),
        }

    def read_language_facts(self, codebase_id: str) -> list[dict[str, Any]]:
        self.registry.describe(codebase_id)
        return read_architecture_language_facts(self.workspace, codebase_id)

    def build_language_provider_facts(self, codebase_id: str, *, snapshot_id: str | None = None) -> dict[str, Any]:
        asset = self.registry.describe(codebase_id)
        if asset.status != "active":
            raise ValueError("CODEBASE_NOT_ACTIVE")
        resolved_snapshot_id = snapshot_id or self._latest_snapshot_id(codebase_id)
        self.snapshots.read_snapshot(codebase_id, resolved_snapshot_id)
        files = read_jsonl(snapshot_files_path(self.workspace, codebase_id, resolved_snapshot_id))
        if not files:
            raise FileNotFoundError("SNAPSHOT_FILES_NOT_FOUND")
        return build_language_provider_artifacts(
            workspace=self.workspace,
            workspace_id=self.workspace_id,
            codebase_id=codebase_id,
            snapshot_id=resolved_snapshot_id,
            root=Path(asset.root_path).expanduser().resolve(),
            files=files,
        )

    def read_language_provider_facts(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        payload = read_language_provider_artifacts(self.workspace, codebase_id)
        payload["workspace_id"] = self.workspace_id
        return payload

    def build_workflow_runtime_candidates(self, codebase_id: str, *, snapshot_id: str | None = None) -> dict[str, Any]:
        asset = self.registry.describe(codebase_id)
        if asset.status != "active":
            raise ValueError("CODEBASE_NOT_ACTIVE")
        resolved_snapshot_id = snapshot_id or self._latest_snapshot_id(codebase_id)
        self.snapshots.read_snapshot(codebase_id, resolved_snapshot_id)
        files = read_jsonl(snapshot_files_path(self.workspace, codebase_id, resolved_snapshot_id))
        if not files:
            raise FileNotFoundError("SNAPSHOT_FILES_NOT_FOUND")
        return build_workflow_runtime_candidates(
            workspace=self.workspace,
            workspace_id=self.workspace_id,
            codebase_id=codebase_id,
            snapshot_id=resolved_snapshot_id,
            root=Path(asset.root_path).expanduser().resolve(),
            files=files,
        )

    def read_workflow_runtime_candidates(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        payload = read_workflow_runtime_candidates(self.workspace, codebase_id)
        payload["workspace_id"] = self.workspace_id
        return payload

    def read_config_inventory(self, codebase_id: str) -> list[dict[str, Any]]:
        self.registry.describe(codebase_id)
        return read_architecture_config_inventory(self.workspace, codebase_id)

    def read_deployment_inventory(self, codebase_id: str) -> list[dict[str, Any]]:
        self.registry.describe(codebase_id)
        return read_architecture_deployment_inventory(self.workspace, codebase_id)

    def read_schema_inventory(self, codebase_id: str) -> list[dict[str, Any]]:
        self.registry.describe(codebase_id)
        return read_architecture_schema_inventory(self.workspace, codebase_id)

    def build_taxonomy(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        taxonomy = build_default_taxonomy(workspace=self.workspace, workspace_id=self.workspace_id, codebase_id=codebase_id)
        write_architecture_taxonomy(self.workspace, codebase_id, taxonomy)
        return taxonomy

    def read_taxonomy(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        return read_architecture_taxonomy(self.workspace, codebase_id)

    def build_review_queue(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        try:
            taxonomy = self.read_taxonomy(codebase_id)
        except FileNotFoundError:
            taxonomy = self.build_taxonomy(codebase_id)
        collections = _review_collections(self.workspace, codebase_id)
        snapshot_id = _snapshot_id_from_review_collections(collections)
        queue = build_review_queue(
            workspace_id=self.workspace_id,
            codebase_id=codebase_id,
            snapshot_id=snapshot_id,
            taxonomy=taxonomy,
            collections=collections,
        )
        write_architecture_review_queue(self.workspace, codebase_id, queue)
        return {
            "schema_version": "v2.6",
            "workspace_id": self.workspace_id,
            "codebase_id": codebase_id,
            "snapshot_id": snapshot_id,
            "taxonomy": taxonomy,
            "review_queue": queue,
            "summary": public_review_queue_payload(queue),
            "artifact_refs": architecture_taxonomy_artifact_refs(codebase_id),
        }

    def read_review_queue(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        queue = read_architecture_review_queue(self.workspace, codebase_id)
        try:
            taxonomy = self.read_taxonomy(codebase_id)
        except FileNotFoundError:
            taxonomy = {}
        return {
            "schema_version": "v2.6",
            "workspace_id": self.workspace_id,
            "codebase_id": codebase_id,
            "snapshot_id": _snapshot_id_from_items(queue),
            "taxonomy": taxonomy,
            "review_queue": queue,
            "summary": public_review_queue_payload(queue),
            "artifact_refs": architecture_taxonomy_artifact_refs(codebase_id),
        }

    def build_large_project_views(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        payload = self._large_project_payload(codebase_id)
        html = render_large_project_html(payload)
        mermaid, persisted_ids = render_key_boundaries_mermaid(payload)
        _write_architecture_views(self.workspace, codebase_id, html, mermaid)
        return {
            "schema_version": "v2.6",
            "workspace_id": self.workspace_id,
            "codebase_id": codebase_id,
            "snapshot_id": payload.get("snapshot_id"),
            "view_ids": [HTML_VIEW_ID, MERMAID_VIEW_ID],
            "mermaid_persisted_ids": sorted(persisted_ids),
            "artifact_refs": _large_project_view_refs(codebase_id),
        }

    def read_large_project_view(self, codebase_id: str, view_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        normalized = _normalize_large_project_view_id(view_id)
        content = read_architecture_view(self.workspace, codebase_id, normalized)
        content_type = "text/html" if normalized.endswith(".html") else "text/mermaid"
        snapshot_id = None
        try:
            snapshot_id = self.read_scale_profile(codebase_id).get("snapshot_id")
        except FileNotFoundError:
            pass
        return {"schema_version": "v2.6", "snapshot_id": snapshot_id, "view_id": normalized, "content_type": content_type, "content": content, "artifact_refs": _large_project_view_refs(codebase_id)}

    def build_document_registry(self, codebase_id: str, *, snapshot_id: str | None = None) -> dict[str, Any]:
        asset = self.registry.describe(codebase_id)
        if asset.status != "active":
            raise ValueError("CODEBASE_NOT_ACTIVE")
        resolved_snapshot_id = snapshot_id or self._latest_snapshot_id(codebase_id)
        self.snapshots.read_snapshot(codebase_id, resolved_snapshot_id)
        files = read_jsonl(snapshot_files_path(self.workspace, codebase_id, resolved_snapshot_id))
        if not files:
            raise FileNotFoundError("SNAPSHOT_FILES_NOT_FOUND")
        payload = build_document_registry(
            workspace_id=self.workspace_id,
            codebase_id=codebase_id,
            snapshot_id=resolved_snapshot_id,
            root=Path(asset.root_path).expanduser().resolve(),
            files=files,
        )
        if not payload["documents"]:
            raise FileNotFoundError("ARCHITECTURE_DOC_SOURCE_NOT_FOUND")
        write_architecture_doc_registry(self.workspace, codebase_id, payload["documents"], payload["sources"])
        payload["artifact_refs"] = architecture_doc_registry_artifact_refs(codebase_id)
        return payload

    def read_document_registry(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        payload = read_architecture_doc_registry(self.workspace, codebase_id)
        documents = payload.get("documents", [])
        snapshot_id = _snapshot_id_from_items(documents)
        summary = _document_registry_summary(self.workspace_id, codebase_id, snapshot_id, documents)
        result = {
            "schema_version": "v2.7",
            "workspace_id": self.workspace_id,
            "codebase_id": codebase_id,
            "snapshot_id": snapshot_id,
            "documents": documents,
            "sources": payload.get("sources", []),
            "summary": summary,
            "artifact_refs": architecture_doc_registry_artifact_refs(codebase_id),
        }
        return _apply_quality_plan_to_v27_payload(self.workspace, codebase_id, result)

    def build_document_claims(self, codebase_id: str) -> dict[str, Any]:
        asset = self.registry.describe(codebase_id)
        if asset.status != "active":
            raise ValueError("CODEBASE_NOT_ACTIVE")
        registry = self.read_document_registry(codebase_id)
        snapshot_id = str(registry.get("snapshot_id") or "")
        if not snapshot_id:
            raise FileNotFoundError("ARCHITECTURE_DOCS_NOT_BUILT")
        payload = build_document_claims(
            workspace_id=self.workspace_id,
            codebase_id=codebase_id,
            snapshot_id=snapshot_id,
            root=Path(asset.root_path).expanduser().resolve(),
            documents=registry.get("documents", []),
            sources=registry.get("sources", []),
        )
        if not payload["claims"]:
            raise FileNotFoundError("ARCHITECTURE_DOC_CLAIMS_NOT_FOUND")
        write_architecture_doc_claims(self.workspace, codebase_id, payload["claims"], payload["relations"])
        payload["artifact_refs"] = architecture_doc_claim_artifact_refs(codebase_id)
        return payload

    def read_document_claims(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        payload = read_architecture_doc_claims(self.workspace, codebase_id)
        claims = payload.get("claims", [])
        snapshot_id = _snapshot_id_from_items(claims)
        summary = _document_claim_summary(self.workspace_id, codebase_id, snapshot_id, claims, payload.get("relations", []))
        result = {
            "schema_version": "v2.7",
            "workspace_id": self.workspace_id,
            "codebase_id": codebase_id,
            "snapshot_id": snapshot_id,
            "claims": claims,
            "relations": payload.get("relations", []),
            "summary": summary,
            "artifact_refs": architecture_doc_claim_artifact_refs(codebase_id),
        }
        return _apply_quality_plan_to_v27_payload(self.workspace, codebase_id, result)

    def build_document_semantics_v3(self, codebase_id: str, *, snapshot_id: str | None = None) -> dict[str, Any]:
        asset = self.registry.describe(codebase_id)
        if asset.status != "active":
            raise ValueError("CODEBASE_NOT_ACTIVE")
        resolved_snapshot_id = snapshot_id or self._latest_snapshot_id(codebase_id)
        self.snapshots.read_snapshot(codebase_id, resolved_snapshot_id)
        try:
            registry = self.read_document_registry(codebase_id)
            if str(registry.get("snapshot_id") or "") != resolved_snapshot_id:
                registry = self.build_document_registry(codebase_id, snapshot_id=resolved_snapshot_id)
        except FileNotFoundError:
            registry = self.build_document_registry(codebase_id, snapshot_id=resolved_snapshot_id)
        documents = list(registry.get("documents") or [])
        if not documents:
            raise FileNotFoundError("ARCHITECTURE_DOC_SOURCE_NOT_FOUND")
        refs = architecture_document_semantics_v243_artifact_refs(codebase_id)
        return build_document_semantics_v3(
            workspace=self.workspace,
            workspace_id=self.workspace_id,
            codebase_id=codebase_id,
            snapshot_id=resolved_snapshot_id,
            root=Path(asset.root_path).expanduser().resolve(),
            documents=documents,
            artifact_refs=refs,
        )

    def read_document_semantics_v3(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        return read_document_semantics_v3(self.workspace, codebase_id, architecture_document_semantics_v243_artifact_refs(codebase_id))

    def build_document_quality(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        registry = self.read_document_registry(codebase_id)
        claim_payload = self.read_document_claims(codebase_id)
        snapshot_id = str(claim_payload.get("snapshot_id") or registry.get("snapshot_id") or "")
        payload = build_document_quality(
            workspace_id=self.workspace_id,
            codebase_id=codebase_id,
            snapshot_id=snapshot_id,
            documents=registry.get("documents", []),
            claims=claim_payload.get("claims", []),
            relations=claim_payload.get("relations", []),
        )
        write_architecture_doc_quality(self.workspace, codebase_id, payload["findings"], payload["summary"])
        payload["artifact_refs"] = architecture_doc_quality_artifact_refs(codebase_id)
        return payload

    def read_document_quality(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        payload = read_architecture_doc_quality(self.workspace, codebase_id)
        snapshot_id = str(payload.get("summary", {}).get("snapshot_id") or "")
        result = {
            "schema_version": "v2.7",
            "workspace_id": self.workspace_id,
            "codebase_id": codebase_id,
            "snapshot_id": snapshot_id,
            "findings": payload.get("findings", []),
            "summary": payload.get("summary", {}),
            "artifact_refs": architecture_doc_quality_artifact_refs(codebase_id),
        }
        return _apply_quality_plan_to_v27_payload(self.workspace, codebase_id, result)

    def build_document_code_alignment(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        claim_payload = self.read_document_claims(codebase_id)
        quality_payload = self.read_document_quality(codebase_id)
        snapshot_id = str(claim_payload.get("snapshot_id") or quality_payload.get("snapshot_id") or "")
        if not snapshot_id:
            raise FileNotFoundError("ARCHITECTURE_DOC_CLAIMS_NOT_BUILT")
        files = read_jsonl(snapshot_files_path(self.workspace, codebase_id, snapshot_id))
        surfaces = read_jsonl(inventory_surfaces_path(self.workspace, codebase_id, snapshot_id))
        symbols = read_jsonl(symbols_path(self.workspace, codebase_id, snapshot_id))
        try:
            code_architecture = self.read_code_architecture(codebase_id)
        except FileNotFoundError:
            code_architecture = {"roles": [], "layers": [], "boundaries": [], "patterns": []}
        try:
            taxonomy = self.read_taxonomy(codebase_id)
        except FileNotFoundError:
            taxonomy = {}
        payload = build_document_code_alignment(
            workspace_id=self.workspace_id,
            codebase_id=codebase_id,
            snapshot_id=snapshot_id,
            claims=claim_payload.get("claims", []),
            quality={"findings": quality_payload.get("findings", []), "summary": quality_payload.get("summary", {})},
            code_facts={
                "files": files,
                "surfaces": surfaces,
                "symbols": symbols,
                "roles": code_architecture.get("roles", []),
                "layers": code_architecture.get("layers", []),
                "boundaries": code_architecture.get("boundaries", []),
                "patterns": code_architecture.get("patterns", []),
                "taxonomy": taxonomy,
            },
        )
        write_architecture_doc_code_alignment(self.workspace, codebase_id, payload["alignments"], payload["drift"])
        payload["artifact_refs"] = architecture_doc_code_alignment_artifact_refs(codebase_id)
        return payload

    def read_document_code_alignment(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        payload = read_architecture_doc_code_alignment(self.workspace, codebase_id)
        alignments = payload.get("alignments", [])
        drift = payload.get("drift", [])
        snapshot_id = _snapshot_id_from_items(alignments) or _snapshot_id_from_items(drift)
        summary = _document_code_alignment_summary(self.workspace_id, codebase_id, snapshot_id, alignments, drift)
        result = {
            "schema_version": "v2.7",
            "workspace_id": self.workspace_id,
            "codebase_id": codebase_id,
            "snapshot_id": snapshot_id,
            "alignments": alignments,
            "drift": drift,
            "summary": summary,
            "artifact_refs": architecture_doc_code_alignment_artifact_refs(codebase_id),
        }
        return _apply_quality_plan_to_v27_payload(self.workspace, codebase_id, result)

    def build_reconstructed_architecture(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        registry = self.read_document_registry(codebase_id)
        claim_payload = self.read_document_claims(codebase_id)
        quality_payload = self.read_document_quality(codebase_id)
        alignment_payload = self.read_document_code_alignment(codebase_id)
        snapshot_id = str(alignment_payload.get("snapshot_id") or claim_payload.get("snapshot_id") or registry.get("snapshot_id") or "")
        if not snapshot_id:
            raise FileNotFoundError("ARCHITECTURE_DOC_ALIGNMENT_NOT_BUILT")
        try:
            code_architecture = self.read_code_architecture(codebase_id)
        except FileNotFoundError:
            code_architecture = {"roles": [], "layers": [], "boundaries": [], "patterns": []}
        try:
            taxonomy = self.read_taxonomy(codebase_id)
        except FileNotFoundError:
            taxonomy = {}
        model = build_reconstructed_architecture_model(
            workspace_id=self.workspace_id,
            codebase_id=codebase_id,
            snapshot_id=snapshot_id,
            documents=registry.get("documents", []),
            claims=claim_payload.get("claims", []),
            relations=claim_payload.get("relations", []),
            quality_findings=quality_payload.get("findings", []),
            alignments=alignment_payload.get("alignments", []),
            drift=alignment_payload.get("drift", []),
            code_architecture=code_architecture,
            taxonomy=taxonomy,
        )
        html = render_reconstructed_architecture_html(model)
        mermaid = render_reconstructed_architecture_mermaid(model)
        write_architecture_reconstructed_model(self.workspace, codebase_id, model, html, mermaid)
        model["artifact_refs"] = architecture_reconstructed_artifact_refs(codebase_id)
        return model

    def read_reconstructed_architecture(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        model = read_architecture_reconstructed_model(self.workspace, codebase_id)
        model["artifact_refs"] = architecture_reconstructed_artifact_refs(codebase_id)
        return _apply_quality_plan_to_v27_payload(self.workspace, codebase_id, model)

    def read_document_architecture_view(self, codebase_id: str, view_id: str) -> dict[str, Any]:
        model = self.read_reconstructed_architecture(codebase_id)
        normalized = _normalize_reconstructed_view_id(view_id)
        content = read_architecture_doc_view(self.workspace, codebase_id, normalized)
        content_type = "text/html" if normalized.endswith(".html") else "text/mermaid"
        applied_rules = _applied_rules_from_reconstructed_model(model)
        return {
            "schema_version": "v2.7",
            "snapshot_id": model.get("snapshot_id"),
            "view_id": normalized,
            "content_type": content_type,
            "content": content,
            "applied_rules": applied_rules,
            "governance_status": "governed" if applied_rules else "ungoverned",
            "artifact_refs": architecture_reconstructed_artifact_refs(codebase_id),
        }

    def build_architecture_reading_dashboard(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        model = self.read_reconstructed_architecture(codebase_id)
        try:
            quality = self.read_document_quality(codebase_id)
        except FileNotFoundError:
            quality = {"findings": [], "summary": {}}
        try:
            alignment = self.read_document_code_alignment(codebase_id)
        except FileNotFoundError:
            alignment = {"alignments": [], "drift": []}
        refs = architecture_reading_dashboard_artifact_refs(codebase_id)
        dashboard = build_architecture_reading_dashboard(
            workspace_id=self.workspace_id,
            codebase_id=codebase_id,
            reconstructed_model=model,
            quality=quality,
            alignment=alignment,
            artifact_refs=refs,
        )
        html = render_architecture_reading_dashboard_html(dashboard)
        mermaid = render_architecture_relationship_summary_mermaid(dashboard)
        write_architecture_reading_dashboard(self.workspace, codebase_id, dashboard, html, mermaid)
        dashboard["artifact_refs"] = refs
        return dashboard

    def read_architecture_reading_dashboard(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        payload = read_architecture_reading_dashboard(self.workspace, codebase_id)
        payload["artifact_refs"] = architecture_reading_dashboard_artifact_refs(codebase_id)
        return payload

    def read_architecture_reading_view(self, codebase_id: str, view_id: str) -> dict[str, Any]:
        dashboard = self.read_architecture_reading_dashboard(codebase_id)
        normalized = _normalize_reading_view_id(view_id)
        content = read_architecture_v28_view(self.workspace, codebase_id, normalized)
        content_type = "text/html" if normalized.endswith(".html") else "text/mermaid"
        return {
            "schema_version": "v2.8",
            "snapshot_id": dashboard.get("snapshot_id"),
            "view_id": normalized,
            "content_type": content_type,
            "content": content,
            "artifact_refs": architecture_reading_dashboard_artifact_refs(codebase_id),
        }

    def build_architecture_graph_summary(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        model = self.read_reconstructed_architecture(codebase_id)
        refs = architecture_graph_v28_artifact_refs(codebase_id)
        payload = build_architecture_graph_aggregation(
            workspace_id=self.workspace_id,
            codebase_id=codebase_id,
            reconstructed_model=model,
            artifact_refs=refs,
        )
        write_architecture_graph_v28(self.workspace, codebase_id, payload["summary"], payload["clusters"], payload["views"])
        return {**payload, "artifact_refs": refs}

    def read_architecture_graph_summary(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        payload = read_architecture_graph_v28(self.workspace, codebase_id)
        refs = architecture_graph_v28_artifact_refs(codebase_id)
        return {**payload, "artifact_refs": refs}

    def read_architecture_graph_view(self, codebase_id: str, view_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        normalized = _normalize_graph_view_id(view_id)
        view = read_architecture_graph_view_v28(self.workspace, codebase_id, normalized)
        view["artifact_refs"] = architecture_graph_v28_artifact_refs(codebase_id)
        return view

    def build_code_fact_chains(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        model = self.read_reconstructed_architecture(codebase_id)
        snapshot_id = str(model.get("snapshot_id") or "")
        if not snapshot_id:
            raise FileNotFoundError("ARCHITECTURE_RECONSTRUCTION_NOT_BUILT")
        surfaces = read_jsonl(inventory_surfaces_path(self.workspace, codebase_id, snapshot_id))
        symbols = read_jsonl(symbols_path(self.workspace, codebase_id, snapshot_id))
        files = read_jsonl(snapshot_files_path(self.workspace, codebase_id, snapshot_id))
        evidence = read_jsonl(evidence_path(self.workspace, codebase_id, snapshot_id))
        if not surfaces:
            raise FileNotFoundError("INVENTORY_NOT_FOUND")
        refs = architecture_code_fact_chain_artifact_refs(codebase_id)
        payload = build_code_fact_chains(
            workspace_id=self.workspace_id,
            codebase_id=codebase_id,
            snapshot_id=snapshot_id,
            surfaces=surfaces,
            symbols=symbols,
            files=files,
            evidence=evidence,
            artifact_refs=refs,
        )
        write_architecture_code_fact_chains(self.workspace, codebase_id, payload["chains"], payload["runtime_boundaries"])
        return payload

    def read_code_fact_chains(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        payload = read_architecture_code_fact_chains(self.workspace, codebase_id)
        snapshot_id = _snapshot_id_from_items(payload.get("chains", [])) or _snapshot_id_from_items(payload.get("runtime_boundaries", []))
        refs = architecture_code_fact_chain_artifact_refs(codebase_id)
        summary = {
            "schema_version": "v2.8",
            "workspace_id": self.workspace_id,
            "codebase_id": codebase_id,
            "snapshot_id": snapshot_id,
            "chain_count": len(payload.get("chains", [])),
            "accepted_chain_count": sum(1 for item in payload.get("chains", []) if item.get("status") == "accepted"),
            "needs_review_chain_count": sum(1 for item in payload.get("chains", []) if item.get("status") != "accepted"),
            "runtime_boundary_count": len(payload.get("runtime_boundaries", [])),
        }
        return {"summary": summary, "chains": payload.get("chains", []), "runtime_boundaries": payload.get("runtime_boundaries", []), "artifact_refs": refs}

    def build_signal_ranking(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        model = self.read_reconstructed_architecture(codebase_id)
        snapshot_id = str(model.get("snapshot_id") or "")
        docs = self.read_document_registry(codebase_id)
        claims = self.read_document_claims(codebase_id)
        try:
            quality = self.read_document_quality(codebase_id)
        except FileNotFoundError:
            quality = {"findings": [], "summary": {}}
        try:
            alignment = self.read_document_code_alignment(codebase_id)
        except FileNotFoundError:
            alignment = {"alignments": [], "drift": []}
        try:
            graph = self.read_architecture_graph_summary(codebase_id)
        except FileNotFoundError:
            graph = {"summary": {}, "clusters": {}}
        try:
            chains = self.read_code_fact_chains(codebase_id)
        except FileNotFoundError:
            chains = {"chains": [], "runtime_boundaries": []}
        refs = architecture_signal_ranking_artifact_refs(codebase_id)
        payload = build_signal_ranking(
            workspace_id=self.workspace_id,
            codebase_id=codebase_id,
            snapshot_id=snapshot_id,
            documents=docs.get("documents", []),
            claims=claims.get("claims", []),
            quality_findings=quality.get("findings", []),
            alignments=alignment.get("alignments", []),
            drift=alignment.get("drift", []),
            graph_summary=graph,
            code_fact_chains=chains,
            artifact_refs=refs,
        )
        write_architecture_signal_ranking(self.workspace, codebase_id, payload["ranking"], payload["review_queue_v2"])
        return payload

    def read_signal_ranking(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        payload = read_architecture_signal_ranking(self.workspace, codebase_id)
        payload["artifact_refs"] = architecture_signal_ranking_artifact_refs(codebase_id)
        return payload

    def build_intent_evidence(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        model = self.read_reconstructed_architecture(codebase_id)
        snapshot_id = str(model.get("snapshot_id") or "")
        docs = self.read_document_registry(codebase_id)
        claims = self.read_document_claims(codebase_id)
        try:
            quality = self.read_document_quality(codebase_id)
        except FileNotFoundError:
            quality = {"findings": [], "summary": {}}
        try:
            alignment = self.read_document_code_alignment(codebase_id)
        except FileNotFoundError:
            alignment = {"alignments": [], "drift": []}
        try:
            chains = self.read_code_fact_chains(codebase_id)
        except FileNotFoundError:
            chains = {"chains": [], "runtime_boundaries": []}
        refs = architecture_intent_evidence_artifact_refs(codebase_id)
        payload = build_intent_evidence(
            workspace_id=self.workspace_id,
            codebase_id=codebase_id,
            snapshot_id=snapshot_id,
            documents=docs.get("documents", []),
            claims=claims.get("claims", []),
            quality_findings=quality.get("findings", []),
            alignments=alignment.get("alignments", []),
            drift=alignment.get("drift", []),
            code_fact_chains=chains,
            artifact_refs=refs,
        )
        write_architecture_intent_evidence(self.workspace, codebase_id, payload["intents"])
        return payload

    def read_intent_evidence(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        intents = read_architecture_intent_evidence(self.workspace, codebase_id)
        snapshot_id = _snapshot_id_from_items(intents)
        refs = architecture_intent_evidence_artifact_refs(codebase_id)
        summary = {
            "schema_version": "v2.8",
            "workspace_id": self.workspace_id,
            "codebase_id": codebase_id,
            "snapshot_id": snapshot_id,
            "intent_count": len(intents),
            "intent_type_counts": _count_by_key(intents, "intent_type"),
            "needs_review_count": sum(1 for item in intents if item.get("needs_review")),
            "pure_code_human_intent_claimed": False,
            "source_artifact_refs": refs,
        }
        return {"summary": summary, "intents": intents, "artifact_refs": refs}

    def create_architecture_context_pack_v2(
        self,
        codebase_id: str,
        *,
        mode: str = "project_brief",
        task: str | None = None,
        max_tokens: int = 12000,
    ) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        dashboard = self.read_architecture_reading_dashboard(codebase_id)
        graph = self.read_architecture_graph_summary(codebase_id)
        ranking = self.read_signal_ranking(codebase_id)
        chains = self.read_code_fact_chains(codebase_id)
        intent = self.read_intent_evidence(codebase_id)
        snapshot_id = str(dashboard.get("snapshot_id") or graph.get("summary", {}).get("snapshot_id") or ranking.get("ranking", {}).get("snapshot_id") or "")
        refs = [
            *architecture_reading_dashboard_artifact_refs(codebase_id),
            *architecture_graph_v28_artifact_refs(codebase_id),
            *architecture_signal_ranking_artifact_refs(codebase_id),
            *architecture_code_fact_chain_artifact_refs(codebase_id),
            *architecture_intent_evidence_artifact_refs(codebase_id),
        ]
        pack = build_architecture_context_pack_v2(
            workspace_id=self.workspace_id,
            codebase_id=codebase_id,
            snapshot_id=snapshot_id,
            mode=mode,
            task=task,
            max_tokens=max_tokens,
            dashboard=dashboard,
            graph=graph,
            ranking=ranking,
            code_fact_chains=chains,
            intent_evidence=intent,
            artifact_refs=refs,
        )
        pack["artifact_refs"] = architecture_context_pack_v2_artifact_refs(codebase_id, pack["pack_id"])
        write_architecture_context_pack_v2(self.workspace, codebase_id, pack["pack_id"], pack)
        return pack

    def read_architecture_context_pack_v2(self, codebase_id: str, pack_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        pack = read_architecture_context_pack_v2(self.workspace, codebase_id, pack_id)
        pack["artifact_refs"] = architecture_context_pack_v2_artifact_refs(codebase_id, pack_id)
        return pack

    def build_public_surface_evidence_v2(self, codebase_id: str, *, snapshot_id: str | None = None) -> dict[str, Any]:
        asset = self.registry.describe(codebase_id)
        if asset.status != "active":
            raise ValueError("CODEBASE_NOT_ACTIVE")
        resolved_snapshot_id = snapshot_id or self._latest_snapshot_id(codebase_id)
        self.snapshots.read_snapshot(codebase_id, resolved_snapshot_id)
        files = read_jsonl(snapshot_files_path(self.workspace, codebase_id, resolved_snapshot_id))
        surfaces = read_jsonl(inventory_surfaces_path(self.workspace, codebase_id, resolved_snapshot_id))
        symbols = read_jsonl(symbols_path(self.workspace, codebase_id, resolved_snapshot_id))
        evidence = read_jsonl(evidence_path(self.workspace, codebase_id, resolved_snapshot_id))
        if not surfaces:
            raise FileNotFoundError("INVENTORY_NOT_FOUND")
        try:
            chains = self.read_code_fact_chains(codebase_id)
        except FileNotFoundError:
            chains = {"chains": [], "runtime_boundaries": []}
        refs = architecture_public_surface_evidence_v29_artifact_refs(codebase_id)
        payload = build_public_surface_evidence_v2(
            workspace_id=self.workspace_id,
            codebase_id=codebase_id,
            snapshot_id=resolved_snapshot_id,
            repo_root=Path(asset.root_path).expanduser().resolve(),
            files=files,
            surfaces=surfaces,
            symbols=symbols,
            evidence=evidence,
            code_fact_chains=chains,
            artifact_refs=refs,
        )
        write_architecture_public_surface_evidence_v29(self.workspace, codebase_id, payload)
        return payload

    def read_public_surface_evidence_v2(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        payload = read_architecture_public_surface_evidence_v29(self.workspace, codebase_id)
        payload["artifact_refs"] = architecture_public_surface_evidence_v29_artifact_refs(codebase_id)
        return payload

    def build_code_relationships_v2(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        evidence_payload = self.read_public_surface_evidence_v2(codebase_id)
        snapshot_id = str(evidence_payload.get("snapshot_id") or evidence_payload.get("summary", {}).get("snapshot_id") or "")
        if not snapshot_id:
            raise FileNotFoundError("ARCHITECTURE_PUBLIC_SURFACE_EVIDENCE_NOT_BUILT")
        symbols = read_jsonl(symbols_path(self.workspace, codebase_id, snapshot_id))
        files = read_jsonl(snapshot_files_path(self.workspace, codebase_id, snapshot_id))
        imports = read_jsonl(imports_path(self.workspace, codebase_id, snapshot_id))
        refs = architecture_relationships_v29_artifact_refs(codebase_id)
        payload = build_code_relationships_v2(
            workspace_id=self.workspace_id,
            codebase_id=codebase_id,
            snapshot_id=snapshot_id,
            public_surface_evidence=evidence_payload,
            symbols=symbols,
            files=files,
            imports=imports,
            artifact_refs=refs,
        )
        write_architecture_relationships_v29(self.workspace, codebase_id, payload)
        return payload

    def read_code_relationships_v2(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        payload = read_architecture_relationships_v29(self.workspace, codebase_id)
        payload["artifact_refs"] = architecture_relationships_v29_artifact_refs(codebase_id)
        return payload

    def build_relationship_chains_v3(self, codebase_id: str, *, snapshot_id: str | None = None) -> dict[str, Any]:
        asset = self.registry.describe(codebase_id)
        if asset.status != "active":
            raise ValueError("CODEBASE_NOT_ACTIVE")
        resolved_snapshot_id = snapshot_id or self._latest_snapshot_id(codebase_id)
        self.snapshots.read_snapshot(codebase_id, resolved_snapshot_id)
        files = read_jsonl(snapshot_files_path(self.workspace, codebase_id, resolved_snapshot_id))
        surfaces = read_jsonl(inventory_surfaces_path(self.workspace, codebase_id, resolved_snapshot_id))
        symbols = read_jsonl(symbols_path(self.workspace, codebase_id, resolved_snapshot_id))
        if not files:
            raise FileNotFoundError("SNAPSHOT_FILES_NOT_FOUND")
        language = self.read_language_provider_facts(codebase_id)
        workflow = self.read_workflow_runtime_candidates(codebase_id)
        try:
            claims = self.read_document_claims(codebase_id).get("claims", [])
        except FileNotFoundError:
            claims = []
        refs = architecture_relationship_chains_v242_artifact_refs(codebase_id)
        return build_relationship_chains_v3(
            workspace=self.workspace,
            workspace_id=self.workspace_id,
            codebase_id=codebase_id,
            snapshot_id=resolved_snapshot_id,
            surfaces=surfaces,
            symbols=symbols,
            files=files,
            language_symbols=list(language.get("symbols") or []),
            language_references=list(language.get("references") or []),
            workflow_candidates=list(workflow.get("workflow_candidates") or []),
            runtime_candidates=list(workflow.get("runtime_candidates") or []),
            entrypoint_candidates=list(workflow.get("entrypoint_candidates") or []),
            doc_claims=list(claims),
            artifact_refs=refs,
        )

    def read_relationship_chains_v3(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        return read_relationship_chains_v3(self.workspace, codebase_id, architecture_relationship_chains_v242_artifact_refs(codebase_id))

    def build_ranking_calibration_v2(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        evidence_payload = self.read_public_surface_evidence_v2(codebase_id)
        relationships = self.read_code_relationships_v2(codebase_id)
        snapshot_id = str(evidence_payload.get("snapshot_id") or relationships.get("snapshot_id") or "")
        try:
            previous = self.read_signal_ranking(codebase_id)
        except FileNotFoundError:
            previous = {}
        refs = architecture_signal_ranking_v29_artifact_refs(codebase_id)
        payload = build_ranking_calibration_v2(
            workspace_id=self.workspace_id,
            codebase_id=codebase_id,
            snapshot_id=snapshot_id,
            public_surface_evidence=evidence_payload,
            relationships=relationships,
            previous_ranking=previous,
            artifact_refs=refs,
        )
        write_architecture_signal_ranking_v29(self.workspace, codebase_id, payload["ranking"], payload["review_queue_v3"])
        return payload

    def read_ranking_calibration_v2(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        payload = read_architecture_signal_ranking_v29(self.workspace, codebase_id)
        payload["artifact_refs"] = architecture_signal_ranking_v29_artifact_refs(codebase_id)
        return payload

    def build_human_review_report_v2(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        evidence_payload = self.read_public_surface_evidence_v2(codebase_id)
        relationships = self.read_code_relationships_v2(codebase_id)
        ranking = self.read_ranking_calibration_v2(codebase_id)
        snapshot_id = str(evidence_payload.get("snapshot_id") or relationships.get("snapshot_id") or "")
        refs = architecture_human_report_v29_artifact_refs(codebase_id)
        payload = build_human_review_report_v2(
            workspace_id=self.workspace_id,
            codebase_id=codebase_id,
            snapshot_id=snapshot_id,
            public_surface_evidence=evidence_payload,
            relationships=relationships,
            ranking=ranking,
            artifact_refs=refs,
        )
        write_architecture_human_report_v29(self.workspace, codebase_id, payload["report"], payload["views"])
        return payload

    def read_human_review_report_v2(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        payload = read_architecture_human_report_v29(self.workspace, codebase_id)
        payload["artifact_refs"] = architecture_human_report_v29_artifact_refs(codebase_id)
        return payload

    def read_human_review_report_view_v2(self, codebase_id: str, view_id: str) -> dict[str, Any]:
        report_payload = self.read_human_review_report_v2(codebase_id)
        view = read_architecture_human_report_view_v29(self.workspace, codebase_id, view_id)
        return {
            "schema_version": "v2.9",
            "codebase_id": codebase_id,
            "snapshot_id": report_payload.get("report", {}).get("snapshot_id"),
            "view_id": view_id,
            "content_type": view.get("content_type") or ("text/html" if view_id == HUMAN_REPORT_HTML_VIEW_ID else "text/mermaid"),
            "content": view.get("content") or "",
            "artifact_refs": architecture_human_report_v29_artifact_refs(codebase_id),
        }

    def create_architecture_context_pack_v3(
        self,
        codebase_id: str,
        *,
        mode: str = "project_brief",
        role: str = "maintainer",
        task: str | None = None,
        max_tokens: int = 12000,
    ) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        evidence_payload = self.read_public_surface_evidence_v2(codebase_id)
        relationships = self.read_code_relationships_v2(codebase_id)
        ranking = self.read_ranking_calibration_v2(codebase_id)
        human_report = self.read_human_review_report_v2(codebase_id)
        snapshot_id = str(evidence_payload.get("snapshot_id") or human_report.get("report", {}).get("snapshot_id") or "")
        refs = [
            *architecture_public_surface_evidence_v29_artifact_refs(codebase_id),
            *architecture_relationships_v29_artifact_refs(codebase_id),
            *architecture_signal_ranking_v29_artifact_refs(codebase_id),
            *architecture_human_report_v29_artifact_refs(codebase_id),
        ]
        pack = build_architecture_context_pack_v3(
            workspace_id=self.workspace_id,
            codebase_id=codebase_id,
            snapshot_id=snapshot_id,
            mode=mode,
            role=role,
            task=task,
            max_tokens=max_tokens,
            public_surface_evidence=evidence_payload,
            relationships=relationships,
            ranking=ranking,
            human_report=human_report,
            artifact_refs=refs,
        )
        pack["artifact_refs"] = architecture_context_pack_v3_artifact_refs(codebase_id, pack["pack_id"])
        write_architecture_context_pack_v3(self.workspace, codebase_id, pack["pack_id"], pack)
        return pack

    def read_architecture_context_pack_v3(self, codebase_id: str, pack_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        pack = read_architecture_context_pack_v3(self.workspace, codebase_id, pack_id)
        pack["artifact_refs"] = architecture_context_pack_v3_artifact_refs(codebase_id, pack_id)
        return pack

    def create_optimized_context_pack_v244(
        self,
        codebase_id: str,
        *,
        mode: str = "project_brief",
        role: str = "maintainer",
        task: str | None = None,
        max_tokens: int = 4000,
    ) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        relationships = read_relationship_chains_v3(self.workspace, codebase_id, architecture_relationship_chains_v242_artifact_refs(codebase_id))
        document_semantics = read_document_semantics_v3(self.workspace, codebase_id, architecture_document_semantics_v243_artifact_refs(codebase_id))
        snapshot_id = str(relationships.get("snapshot_id") or document_semantics.get("snapshot_id") or "")
        refs = [
            *architecture_relationship_chains_v242_artifact_refs(codebase_id),
            *architecture_document_semantics_v243_artifact_refs(codebase_id),
        ]
        built = build_optimized_context_pack(
            workspace=self.workspace,
            workspace_id=self.workspace_id,
            codebase_id=codebase_id,
            snapshot_id=snapshot_id,
            mode=mode,
            role=role,
            task=task,
            max_tokens=max_tokens,
            relationship_payload=relationships,
            document_semantics_payload=document_semantics,
            artifact_refs=refs,
        )
        pack = built["pack"]
        pack["artifact_refs"] = architecture_context_pack_optimized_v244_artifact_refs(codebase_id, str(pack.get("pack_id") or ""))
        write_architecture_context_pack_optimized_v244(self.workspace, codebase_id, str(pack["pack_id"]), pack, str(built["markdown"]), built["ledger"], built["cache_index"])
        return pack

    def read_optimized_context_pack_v244(self, codebase_id: str, pack_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        pack = read_architecture_context_pack_optimized_v244(self.workspace, codebase_id, pack_id)
        pack["artifact_refs"] = architecture_context_pack_optimized_v244_artifact_refs(codebase_id, pack_id)
        return pack

    def build_profile_taxonomy_regression_v245(self, codebase_id: str, *, snapshot_id: str | None = None, regression_projects: list[dict[str, Any]] | None = None) -> dict[str, Any]:
        asset = self.registry.describe(codebase_id)
        if asset.status != "active":
            raise ValueError("CODEBASE_NOT_ACTIVE")
        resolved_snapshot_id = snapshot_id or self._latest_snapshot_id(codebase_id)
        self.snapshots.read_snapshot(codebase_id, resolved_snapshot_id)
        projects = regression_projects or [{"name": Path(asset.root_path).name, "exists": True, "artifact_refs": [], "test_commands": []}]
        return build_profile_taxonomy_regression(
            workspace=self.workspace,
            workspace_id=self.workspace_id,
            codebase_id=codebase_id,
            snapshot_id=resolved_snapshot_id,
            repo_root=Path(asset.root_path),
            project_name=Path(asset.root_path).name,
            regression_projects=projects,
        )

    def read_profile_taxonomy_regression_v245(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        return read_profile_taxonomy_regression(self.workspace, codebase_id)

    def build_pattern_evidence_v2(self, codebase_id: str, *, snapshot_id: str | None = None, runtime_enabled: bool = False) -> dict[str, Any]:
        asset = self.registry.describe(codebase_id)
        if asset.status != "active":
            raise ValueError("CODEBASE_NOT_ACTIVE")
        resolved_snapshot_id = snapshot_id or self._latest_snapshot_id(codebase_id)
        self.snapshots.read_snapshot(codebase_id, resolved_snapshot_id)
        files = read_jsonl(snapshot_files_path(self.workspace, codebase_id, resolved_snapshot_id))
        symbols = read_jsonl(symbols_path(self.workspace, codebase_id, resolved_snapshot_id))
        if not files:
            raise FileNotFoundError("SNAPSHOT_FILES_NOT_FOUND")
        try:
            claims_payload = read_architecture_doc_claims(self.workspace, codebase_id)
            document_claims = list(claims_payload.get("claims", []))
        except FileNotFoundError:
            document_claims = []
        refs = architecture_pattern_evidence_v210_artifact_refs(codebase_id)
        payload = build_pattern_evidence_v2(
            workspace_id=self.workspace_id,
            codebase_id=codebase_id,
            snapshot_id=resolved_snapshot_id,
            repo_root=Path(asset.root_path).expanduser().resolve(),
            files=files,
            symbols=symbols,
            document_claims=document_claims,
            runtime_enabled=runtime_enabled,
            artifact_refs=refs,
        )
        write_architecture_pattern_evidence_v210(self.workspace, codebase_id, payload)
        return payload

    def read_pattern_evidence_v2(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        payload = read_architecture_pattern_evidence_v210(self.workspace, codebase_id)
        payload["artifact_refs"] = architecture_pattern_evidence_v210_artifact_refs(codebase_id)
        return payload

    def read_pattern_evidence_view_v2(self, codebase_id: str, view_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        view = read_architecture_pattern_evidence_v210_view(self.workspace, codebase_id, view_id)
        view["artifact_refs"] = architecture_pattern_evidence_v210_artifact_refs(codebase_id)
        return view

    def build_context_architecture_summary(self, codebase_id: str) -> dict[str, Any] | None:
        try:
            payload = self._large_project_payload(codebase_id)
        except FileNotFoundError:
            return None
        return build_architecture_summary(payload)

    def _large_project_payload(self, codebase_id: str) -> dict[str, Any]:
        scale = self.read_scale_profile(codebase_id)
        try:
            inventory = public_architecture_inventory_payload(self.read_inventory(codebase_id))
        except FileNotFoundError:
            inventory = {"language_facts": {}, "config_inventory": {}, "deployment_inventory": {}, "schema_inventory": {}}
        try:
            taxonomy = self.read_taxonomy(codebase_id)
        except FileNotFoundError:
            taxonomy = {}
        try:
            review = self.read_review_queue(codebase_id)
        except FileNotFoundError:
            review = {"review_queue": [], "summary": public_review_queue_payload([])}
        try:
            code_architecture = self.read_code_architecture(codebase_id)
        except FileNotFoundError:
            code_architecture = {"roles": [], "boundaries": [], "patterns": []}
        refs = [
            *architecture_scale_artifact_refs(codebase_id),
            *architecture_inventory_artifact_refs(codebase_id),
            *architecture_taxonomy_artifact_refs(codebase_id),
            *code_architecture_artifact_refs(codebase_id),
            *_large_project_view_refs(codebase_id),
        ]
        return {
            "workspace_id": self.workspace_id,
            "codebase_id": codebase_id,
            "snapshot_id": scale.get("snapshot_id"),
            "scale_profile": public_architecture_scale_profile_payload(scale),
            "inventory": inventory,
            "taxonomy": taxonomy,
            "review_queue": review,
            "code_architecture": code_architecture,
            "artifact_refs": refs,
        }

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


def public_architecture_scale_profile_payload(profile: dict[str, Any]) -> dict[str, Any]:
    payload = public_scale_profile_payload(profile)
    payload["artifact_refs"] = architecture_scale_artifact_refs(str(profile.get("codebase_id") or ""))
    return payload


def public_architecture_inventory_payload(payload: dict[str, Any]) -> dict[str, Any]:
    codebase_id = str(payload.get("codebase_id") or "")
    return {
        "schema_version": payload.get("schema_version", "v2.6"),
        "workspace_id": payload.get("workspace_id"),
        "codebase_id": codebase_id,
        "snapshot_id": payload.get("snapshot_id"),
        "language_facts": public_inventory_payload(payload.get("language_facts", []), item_key="fact_type"),
        "config_inventory": public_inventory_payload(payload.get("config_inventory", []), item_key="item_type"),
        "deployment_inventory": public_inventory_payload(payload.get("deployment_inventory", []), item_key="deployment_type"),
        "schema_inventory": public_inventory_payload(payload.get("schema_inventory", []), item_key="schema_type"),
        "artifact_refs": architecture_inventory_artifact_refs(codebase_id),
    }


def public_architecture_inventory_list_payload(items: list[dict[str, Any]], *, payload_key: str, item_key: str, codebase_id: str) -> dict[str, Any]:
    return {
        payload_key: public_inventory_payload(items, item_key=item_key),
        "artifact_refs": architecture_inventory_artifact_refs(codebase_id),
    }


def public_architecture_taxonomy_payload(taxonomy: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": taxonomy.get("schema_version", "v2.6"),
        "taxonomy_id": taxonomy.get("taxonomy_id"),
        "workspace_id": taxonomy.get("workspace_id"),
        "codebase_id": taxonomy.get("codebase_id"),
        "role_types": taxonomy.get("role_types", []),
        "layer_types": taxonomy.get("layer_types", []),
        "boundary_types": taxonomy.get("boundary_types", []),
        "pattern_types": taxonomy.get("pattern_types", []),
        "review_reasons": taxonomy.get("review_reasons", []),
        "confidence_thresholds": taxonomy.get("confidence_thresholds", {}),
        "override_source": taxonomy.get("override_source"),
    }


def public_architecture_review_queue_payload(payload: dict[str, Any]) -> dict[str, Any]:
    codebase_id = str(payload.get("codebase_id") or "")
    return {
        "schema_version": payload.get("schema_version", "v2.6"),
        "workspace_id": payload.get("workspace_id"),
        "codebase_id": codebase_id,
        "snapshot_id": payload.get("snapshot_id"),
        "taxonomy": public_architecture_taxonomy_payload(payload.get("taxonomy", {})),
        "review_queue": payload.get("summary", public_review_queue_payload(payload.get("review_queue", []))),
        "artifact_refs": architecture_taxonomy_artifact_refs(codebase_id),
    }


def public_architecture_document_registry_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return public_document_registry_payload(payload, architecture_doc_registry_artifact_refs(str(payload.get("codebase_id") or "")))


def public_architecture_document_claims_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return public_document_claims_payload(payload, architecture_doc_claim_artifact_refs(str(payload.get("codebase_id") or "")))


def public_architecture_document_semantics_v3_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return public_document_semantics_v3_payload(payload)


def public_architecture_document_quality_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return public_document_quality_payload(payload, architecture_doc_quality_artifact_refs(str(payload.get("codebase_id") or "")))


def public_architecture_document_code_alignment_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return public_document_code_alignment_payload(payload, architecture_doc_code_alignment_artifact_refs(str(payload.get("codebase_id") or "")))


def public_architecture_reconstructed_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return public_reconstructed_architecture_payload(payload, architecture_reconstructed_artifact_refs(str(payload.get("codebase_id") or "")))


def public_architecture_reading_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return public_architecture_reading_dashboard_payload(payload, architecture_reading_dashboard_artifact_refs(str(payload.get("codebase_id") or "")))


def public_architecture_graph_summary_payload(payload: dict[str, Any]) -> dict[str, Any]:
    summary = payload.get("summary", {})
    codebase_id = str(summary.get("codebase_id") or "")
    return public_architecture_graph_aggregation_payload(payload, architecture_graph_v28_artifact_refs(codebase_id))


def public_architecture_code_fact_chain_payload(payload: dict[str, Any]) -> dict[str, Any]:
    summary = payload.get("summary", {})
    codebase_id = str(summary.get("codebase_id") or "")
    return public_code_fact_chain_payload(payload, architecture_code_fact_chain_artifact_refs(codebase_id))


def public_architecture_signal_ranking_payload(payload: dict[str, Any]) -> dict[str, Any]:
    ranking = payload.get("ranking", {})
    codebase_id = str(ranking.get("codebase_id") or payload.get("review_queue_v2", {}).get("codebase_id") or "")
    return public_signal_ranking_payload(payload, architecture_signal_ranking_artifact_refs(codebase_id))


def public_architecture_intent_evidence_payload(payload: dict[str, Any]) -> dict[str, Any]:
    summary = payload.get("summary", {})
    codebase_id = str(summary.get("codebase_id") or "")
    return public_intent_evidence_payload(payload, architecture_intent_evidence_artifact_refs(codebase_id))


def public_architecture_context_pack_v2_payload(pack: dict[str, Any]) -> dict[str, Any]:
    return public_architecture_context_pack_v2_payload_impl(pack)


def public_architecture_public_surface_evidence_v2_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return public_public_surface_evidence_v2_payload_impl(payload, architecture_public_surface_evidence_v29_artifact_refs(str(payload.get("codebase_id") or "")))


def public_architecture_code_relationships_v2_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return public_code_relationships_v2_payload_impl(payload, architecture_relationships_v29_artifact_refs(str(payload.get("codebase_id") or "")))


def public_architecture_relationship_chains_v3_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return public_relationship_chains_v3_payload(payload)


def public_architecture_ranking_calibration_v2_payload(payload: dict[str, Any]) -> dict[str, Any]:
    ranking = payload.get("ranking", {})
    codebase_id = str(ranking.get("codebase_id") or payload.get("review_queue_v3", {}).get("codebase_id") or "")
    return public_ranking_calibration_v2_payload_impl(payload, architecture_signal_ranking_v29_artifact_refs(codebase_id))


def public_architecture_human_review_report_v2_payload(payload: dict[str, Any]) -> dict[str, Any]:
    report = payload.get("report", {})
    return public_human_review_report_v2_payload_impl(payload, architecture_human_report_v29_artifact_refs(str(report.get("codebase_id") or "")))


def public_architecture_human_review_report_view_v2_payload(view: dict[str, Any]) -> dict[str, Any]:
    refs = architecture_human_report_v29_artifact_refs(str(view.get("codebase_id") or ""))
    return public_human_review_report_view_v2_payload_impl(str(view.get("view_id") or ""), view, str(view.get("snapshot_id") or ""), refs)


def public_architecture_context_pack_v3_payload(pack: dict[str, Any]) -> dict[str, Any]:
    return public_architecture_context_pack_v3_payload_impl(pack, architecture_context_pack_v3_artifact_refs(str(pack.get("codebase_id") or ""), str(pack.get("pack_id") or "")))


def public_architecture_optimized_context_pack_v244_payload(pack: dict[str, Any]) -> dict[str, Any]:
    return public_optimized_context_pack_payload(pack)


def public_architecture_profile_taxonomy_regression_v245_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return public_profile_taxonomy_regression_payload(payload)


def public_architecture_pattern_evidence_v2_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return public_pattern_evidence_payload_impl(payload, architecture_pattern_evidence_v210_artifact_refs(str(payload.get("codebase_id") or "")))


def public_architecture_pattern_blockers_v2_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return public_pattern_blockers_payload_impl(payload, architecture_pattern_evidence_v210_artifact_refs(str(payload.get("codebase_id") or "")))


def public_architecture_pattern_view_v2_payload(view: dict[str, Any]) -> dict[str, Any]:
    return public_pattern_view_payload_impl(view, architecture_pattern_evidence_v210_artifact_refs(str(view.get("codebase_id") or "")))


def _snapshot_id_from_roles_layers(payload: dict[str, Any]) -> str | None:
    for collection in (payload.get("roles") or [], payload.get("layers") or []):
        for item in collection:
            if isinstance(item, dict) and item.get("snapshot_id"):
                return str(item["snapshot_id"])
    return None


def _snapshot_id_from_inventory(payload: dict[str, list[dict[str, Any]]]) -> str | None:
    for collection in payload.values():
        for item in collection:
            if item.get("snapshot_id"):
                return str(item["snapshot_id"])
    return None


def _snapshot_id_from_items(items: list[dict[str, Any]]) -> str | None:
    for item in items:
        if item.get("snapshot_id"):
            return str(item["snapshot_id"])
    return None


def _count_by_key(items: list[dict[str, Any]], key: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for item in items:
        value = str(item.get(key) or "unknown")
        counts[value] = counts.get(value, 0) + 1
    return dict(sorted(counts.items()))


def _document_registry_summary(workspace_id: str, codebase_id: str, snapshot_id: str | None, documents: list[dict[str, Any]]) -> dict[str, Any]:
    doc_type_counts: dict[str, int] = {}
    authority_role_counts: dict[str, int] = {}
    authority_level_counts: dict[str, int] = {}
    for doc in documents:
        doc_type = str(doc.get("doc_type") or "unknown")
        role = str(doc.get("authority_role") or "unknown")
        level = str(doc.get("authority_level") or "unknown")
        doc_type_counts[doc_type] = doc_type_counts.get(doc_type, 0) + 1
        authority_role_counts[role] = authority_role_counts.get(role, 0) + 1
        authority_level_counts[level] = authority_level_counts.get(level, 0) + 1
    return {
        "schema_version": "v2.7",
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "document_count": len(documents),
        "doc_type_counts": dict(sorted(doc_type_counts.items())),
        "authority_role_counts": dict(sorted(authority_role_counts.items())),
        "authority_level_counts": dict(sorted(authority_level_counts.items())),
        "needs_review_count": sum(1 for item in documents if item.get("needs_review")),
        "stale_hint_count": sum(1 for item in documents if item.get("stale_hint")),
    }


def _document_claim_summary(workspace_id: str, codebase_id: str, snapshot_id: str | None, claims: list[dict[str, Any]], relations: list[dict[str, Any]]) -> dict[str, Any]:
    claim_type_counts: dict[str, int] = {}
    source_block_type_counts: dict[str, int] = {}
    for claim in claims:
        claim_type = str(claim.get("claim_type") or "unknown")
        block_type = str(claim.get("source_block_type") or "unknown")
        claim_type_counts[claim_type] = claim_type_counts.get(claim_type, 0) + 1
        source_block_type_counts[block_type] = source_block_type_counts.get(block_type, 0) + 1
    return {
        "schema_version": "v2.7",
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "claim_count": len(claims),
        "relation_count": len(relations),
        "claim_type_counts": dict(sorted(claim_type_counts.items())),
        "source_block_type_counts": dict(sorted(source_block_type_counts.items())),
        "needs_review_count": sum(1 for item in [*claims, *relations] if item.get("needs_review")),
    }


def _document_code_alignment_summary(workspace_id: str, codebase_id: str, snapshot_id: str | None, alignments: list[dict[str, Any]], drift: list[dict[str, Any]]) -> dict[str, Any]:
    status_counts: dict[str, int] = {}
    strategy_counts: dict[str, int] = {}
    drift_type_counts: dict[str, int] = {}
    for item in alignments:
        status = str(item.get("status") or "unknown")
        strategy = str(item.get("match_strategy") or "unknown")
        status_counts[status] = status_counts.get(status, 0) + 1
        strategy_counts[strategy] = strategy_counts.get(strategy, 0) + 1
    for item in drift:
        drift_type = str(item.get("drift_type") or "unknown")
        drift_type_counts[drift_type] = drift_type_counts.get(drift_type, 0) + 1
    return {
        "schema_version": "v2.7",
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "alignment_count": len(alignments),
        "drift_count": len(drift),
        "matched_count": status_counts.get("matched", 0),
        "weak_match_count": status_counts.get("weak_match", 0),
        "designed_not_found_count": status_counts.get("designed_not_found_in_code", 0),
        "code_not_documented_count": drift_type_counts.get("code_not_documented", 0),
        "status_counts": dict(sorted(status_counts.items())),
        "match_strategy_counts": dict(sorted(strategy_counts.items())),
        "drift_type_counts": dict(sorted(drift_type_counts.items())),
        "accepted_match_confidence_min": 0.8,
        "token_overlap_only_accepted": False,
    }


def _snapshot_id_from_review_collections(collections: dict[str, list[dict[str, Any]]]) -> str | None:
    for items in collections.values():
        snapshot_id = _snapshot_id_from_items(items)
        if snapshot_id:
            return snapshot_id
    return None


def _review_collections(workspace: Path, codebase_id: str) -> dict[str, list[dict[str, Any]]]:
    payload: dict[str, list[dict[str, Any]]] = {}
    try:
        code_architecture = read_code_architecture_roles_layers(workspace, codebase_id)
    except FileNotFoundError:
        code_architecture = {"roles": [], "layers": [], "boundaries": [], "patterns": []}
    payload["role"] = list(code_architecture.get("roles") or [])
    payload["layer"] = list(code_architecture.get("layers") or [])
    payload["boundary"] = list(code_architecture.get("boundaries") or [])
    payload["pattern"] = list(code_architecture.get("patterns") or [])
    try:
        inventory = read_architecture_inventory(workspace, codebase_id)
    except FileNotFoundError:
        inventory = {"language_facts": [], "config_inventory": [], "deployment_inventory": [], "schema_inventory": []}
    payload["language_fact"] = list(inventory.get("language_facts") or [])
    payload["config_item"] = list(inventory.get("config_inventory") or [])
    payload["deployment_item"] = list(inventory.get("deployment_inventory") or [])
    payload["schema_item"] = list(inventory.get("schema_inventory") or [])
    return payload


def _large_project_view_refs(codebase_id: str) -> list[dict[str, str]]:
    return [
        {"type": "architecture_large_project_overview", "artifact_ref": f"architecture://{codebase_id}/views/{HTML_VIEW_ID}"},
        {"type": "architecture_key_boundaries", "artifact_ref": f"architecture://{codebase_id}/views/{MERMAID_VIEW_ID}"},
    ]


def _write_architecture_views(workspace: Path, codebase_id: str, html: str, mermaid: str) -> None:
    html_path = architecture_view_path(workspace, codebase_id, HTML_VIEW_ID)
    mermaid_path = architecture_view_path(workspace, codebase_id, MERMAID_VIEW_ID)
    html_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.write_text(html, encoding="utf-8")
    mermaid_path.write_text(mermaid, encoding="utf-8")


def _normalize_large_project_view_id(view_id: str) -> str:
    value = (view_id or HTML_VIEW_ID).strip()
    if value not in {HTML_VIEW_ID, MERMAID_VIEW_ID}:
        raise FileNotFoundError("ARCHITECTURE_VIEW_NOT_BUILT")
    return value


def _normalize_reconstructed_view_id(view_id: str) -> str:
    value = (view_id or RECONSTRUCTED_HTML_VIEW_ID).strip()
    aliases = {
        "html": RECONSTRUCTED_HTML_VIEW_ID,
        "report": RECONSTRUCTED_HTML_VIEW_ID,
        "document_code_architecture_report": RECONSTRUCTED_HTML_VIEW_ID,
        "mermaid": RECONSTRUCTED_MERMAID_VIEW_ID,
        "mmd": RECONSTRUCTED_MERMAID_VIEW_ID,
        "diff": RECONSTRUCTED_MERMAID_VIEW_ID,
        "document_code_architecture_diff": RECONSTRUCTED_MERMAID_VIEW_ID,
    }
    value = aliases.get(value, value)
    if value not in {RECONSTRUCTED_HTML_VIEW_ID, RECONSTRUCTED_MERMAID_VIEW_ID}:
        raise FileNotFoundError("ARCHITECTURE_DOC_VIEW_NOT_FOUND")
    return value


def _normalize_reading_view_id(view_id: str) -> str:
    value = (view_id or READING_DASHBOARD_HTML_VIEW_ID).strip()
    aliases = {
        "html": READING_DASHBOARD_HTML_VIEW_ID,
        "dashboard": READING_DASHBOARD_HTML_VIEW_ID,
        "architecture_reading_dashboard": READING_DASHBOARD_HTML_VIEW_ID,
        "mermaid": READING_DASHBOARD_MERMAID_VIEW_ID,
        "mmd": READING_DASHBOARD_MERMAID_VIEW_ID,
        "relationships": READING_DASHBOARD_MERMAID_VIEW_ID,
        "architecture_relationship_summary": READING_DASHBOARD_MERMAID_VIEW_ID,
    }
    value = aliases.get(value, value)
    if value not in {READING_DASHBOARD_HTML_VIEW_ID, READING_DASHBOARD_MERMAID_VIEW_ID}:
        raise FileNotFoundError("ARCHITECTURE_V28_VIEW_NOT_FOUND")
    return value


def _normalize_graph_view_id(view_id: str) -> str:
    value = (view_id or "system_overview").strip()
    allowed = {"system_overview", "layer_view", "capability_view", "public_surface_view", "doc_code_drift_view", "evidence_view"}
    if value not in allowed:
        raise FileNotFoundError("ARCHITECTURE_GRAPH_VIEW_NOT_FOUND")
    return value


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


def _apply_quality_plan_to_v27_payload(workspace: Path, codebase_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    plan = read_plan(workspace, codebase_id)
    overlays = plan.get("read_time_overlays") if isinstance(plan, dict) else None
    if not overlays:
        payload["applied_rules"] = []
        payload["governance_status"] = "ungoverned"
        return payload
    by_target: dict[tuple[str, str], dict[str, Any]] = {}
    for overlay in overlays:
        if isinstance(overlay, dict):
            by_target[(str(overlay.get("target_type") or ""), str(overlay.get("target_id") or ""))] = overlay
    specs = [
        ("documents", "architecture_doc", "doc_id"),
        ("claims", "architecture_doc_claim", "claim_id"),
        ("relations", "architecture_doc_relation", "relation_id"),
        ("findings", "architecture_doc_quality_finding", "finding_id"),
        ("alignments", "architecture_doc_code_alignment", "alignment_id"),
        ("target_nodes", "architecture_reconstructed_node", "node_id"),
        ("current_nodes", "architecture_reconstructed_node", "node_id"),
        ("diff_nodes", "architecture_reconstructed_node", "node_id"),
        ("edges", "architecture_reconstructed_edge", "edge_id"),
    ]
    applied_rule_ids: set[str] = set()
    for collection_name, target_type, id_key in specs:
        updated = []
        for item in payload.get(collection_name, []) or []:
            if not isinstance(item, dict):
                updated.append(item)
                continue
            overlay = by_target.get((target_type, str(item.get(id_key) or "")))
            if overlay:
                item = dict(item)
                rules = list(overlay.get("applied_rules") or [])
                item["applied_rules"] = rules
                item["governed_by"] = list(overlay.get("governed_by") or [])
                item["governance_status"] = "governed"
                existing_review = list(item.get("needs_review") or [])
                if "governed_by_rule" not in existing_review:
                    existing_review.append("governed_by_rule")
                item["needs_review"] = existing_review
                applied_rule_ids.update(str(rule_id) for rule_id in rules)
            updated.append(item)
        if collection_name in payload:
            payload[collection_name] = updated
    payload["applied_rules"] = sorted(applied_rule_ids)
    payload["governance_status"] = "governed" if applied_rule_ids else "ungoverned"
    return payload


def _applied_rules_from_reconstructed_model(model: dict[str, Any]) -> list[str]:
    rule_ids: set[str] = set()
    for collection_name in ("target_nodes", "current_nodes", "diff_nodes", "edges"):
        for item in model.get(collection_name, []) or []:
            if isinstance(item, dict):
                rule_ids.update(str(rule_id) for rule_id in item.get("applied_rules") or [])
    return sorted(rule_ids)


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
