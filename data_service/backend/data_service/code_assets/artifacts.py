"""Artifact paths for V2 codebase assets."""

from __future__ import annotations

import hashlib
import json
import os
import threading
from pathlib import Path
from typing import Any

from data_service.mcp_common import read_json, write_json


def codebase_assets_dir(workspace: Path) -> Path:
    return workspace / "assets" / "codebase"


def codebase_index_path(workspace: Path) -> Path:
    return codebase_assets_dir(workspace) / "index.json"


def codebase_dir(workspace: Path, codebase_id: str) -> Path:
    return codebase_assets_dir(workspace) / codebase_id


def codebase_json_path(workspace: Path, codebase_id: str) -> Path:
    return codebase_dir(workspace, codebase_id) / "codebase.json"


def snapshots_dir(workspace: Path, codebase_id: str) -> Path:
    return codebase_dir(workspace, codebase_id) / "snapshots"


def snapshot_dir(workspace: Path, codebase_id: str, snapshot_id: str) -> Path:
    return snapshots_dir(workspace, codebase_id) / snapshot_id


def snapshot_json_path(workspace: Path, codebase_id: str, snapshot_id: str) -> Path:
    return snapshot_dir(workspace, codebase_id, snapshot_id) / "snapshot.json"


def snapshot_files_path(workspace: Path, codebase_id: str, snapshot_id: str) -> Path:
    return snapshot_dir(workspace, codebase_id, snapshot_id) / "files.jsonl"


def snapshot_stats_path(workspace: Path, codebase_id: str, snapshot_id: str) -> Path:
    return snapshot_dir(workspace, codebase_id, snapshot_id) / "stats.json"


def snapshot_warnings_path(workspace: Path, codebase_id: str, snapshot_id: str) -> Path:
    return snapshot_dir(workspace, codebase_id, snapshot_id) / "warnings.jsonl"


def inventory_surfaces_path(workspace: Path, codebase_id: str, snapshot_id: str) -> Path:
    return snapshot_dir(workspace, codebase_id, snapshot_id) / "surfaces.jsonl"


def inventory_capabilities_path(workspace: Path, codebase_id: str, snapshot_id: str) -> Path:
    return snapshot_dir(workspace, codebase_id, snapshot_id) / "capabilities.jsonl"


def inventory_alignment_path(workspace: Path, codebase_id: str, snapshot_id: str) -> Path:
    return snapshot_dir(workspace, codebase_id, snapshot_id) / "alignment_matrix.json"


def inventory_summary_path(workspace: Path, codebase_id: str, snapshot_id: str) -> Path:
    return snapshot_dir(workspace, codebase_id, snapshot_id) / "inventory_summary.json"


def symbols_path(workspace: Path, codebase_id: str, snapshot_id: str) -> Path:
    return snapshot_dir(workspace, codebase_id, snapshot_id) / "symbols.jsonl"


def imports_path(workspace: Path, codebase_id: str, snapshot_id: str) -> Path:
    return snapshot_dir(workspace, codebase_id, snapshot_id) / "imports.jsonl"


def symbol_summary_path(workspace: Path, codebase_id: str, snapshot_id: str) -> Path:
    return snapshot_dir(workspace, codebase_id, snapshot_id) / "symbol_summary.json"


def mappings_path(workspace: Path, codebase_id: str, snapshot_id: str) -> Path:
    return snapshot_dir(workspace, codebase_id, snapshot_id) / "mappings.jsonl"


def evidence_path(workspace: Path, codebase_id: str, snapshot_id: str) -> Path:
    return snapshot_dir(workspace, codebase_id, snapshot_id) / "evidence.jsonl"


def mapping_summary_path(workspace: Path, codebase_id: str, snapshot_id: str) -> Path:
    return snapshot_dir(workspace, codebase_id, snapshot_id) / "mapping_summary.json"


def trace_index_path(workspace: Path, codebase_id: str, snapshot_id: str) -> Path:
    return snapshot_dir(workspace, codebase_id, snapshot_id) / "trace_index.json"


def overview_path(workspace: Path, codebase_id: str) -> Path:
    return codebase_dir(workspace, codebase_id) / "overview.json"


def agent_context_dir(workspace: Path, codebase_id: str) -> Path:
    return codebase_dir(workspace, codebase_id) / "agent_context"


def agent_context_path(workspace: Path, codebase_id: str, pack_id: str) -> Path:
    return agent_context_dir(workspace, codebase_id) / f"{pack_id}.json"


def devwiki_dir(workspace: Path, codebase_id: str) -> Path:
    return codebase_dir(workspace, codebase_id) / "devwiki"


def devwiki_index_path(workspace: Path, codebase_id: str) -> Path:
    return devwiki_dir(workspace, codebase_id) / "index.json"


def devwiki_pages_dir(workspace: Path, codebase_id: str) -> Path:
    return devwiki_dir(workspace, codebase_id) / "pages"


def devwiki_page_json_path(workspace: Path, codebase_id: str, page_slug: str) -> Path:
    return devwiki_pages_dir(workspace, codebase_id) / f"{page_slug}.json"


def devwiki_page_markdown_path(workspace: Path, codebase_id: str, page_slug: str) -> Path:
    return devwiki_pages_dir(workspace, codebase_id) / f"{page_slug}.md"


def code_graph_dir(workspace: Path, codebase_id: str) -> Path:
    return codebase_dir(workspace, codebase_id) / "graph"


def code_graph_json_path(workspace: Path, codebase_id: str) -> Path:
    return code_graph_dir(workspace, codebase_id) / "graph.json"


def code_graph_nodes_path(workspace: Path, codebase_id: str) -> Path:
    return code_graph_dir(workspace, codebase_id) / "nodes.jsonl"


def code_graph_edges_path(workspace: Path, codebase_id: str) -> Path:
    return code_graph_dir(workspace, codebase_id) / "edges.jsonl"


def code_graph_summary_path(workspace: Path, codebase_id: str) -> Path:
    return code_graph_dir(workspace, codebase_id) / "summary.json"


def code_graph_mermaid_dir(workspace: Path, codebase_id: str) -> Path:
    return code_graph_dir(workspace, codebase_id) / "mermaid"


def code_graph_mermaid_path(workspace: Path, codebase_id: str, name: str = "project") -> Path:
    return code_graph_mermaid_dir(workspace, codebase_id) / f"{name}.mmd"


def code_quality_dir(workspace: Path, codebase_id: str) -> Path:
    return codebase_dir(workspace, codebase_id) / "quality"


def code_quality_feedback_path(workspace: Path, codebase_id: str) -> Path:
    return code_quality_dir(workspace, codebase_id) / "feedback.jsonl"


def code_quality_rules_path(workspace: Path, codebase_id: str) -> Path:
    return code_quality_dir(workspace, codebase_id) / "rules.jsonl"


def code_quality_reviews_path(workspace: Path, codebase_id: str) -> Path:
    return code_quality_dir(workspace, codebase_id) / "reviews.jsonl"


def code_quality_plan_path(workspace: Path, codebase_id: str) -> Path:
    return code_quality_dir(workspace, codebase_id) / "plan.json"


def code_quality_summary_path(workspace: Path, codebase_id: str) -> Path:
    return code_quality_dir(workspace, codebase_id) / "summary.json"


def architecture_dir(workspace: Path, codebase_id: str) -> Path:
    return codebase_dir(workspace, codebase_id) / "architecture"


def architecture_sources_path(workspace: Path, codebase_id: str) -> Path:
    return architecture_dir(workspace, codebase_id) / "sources.jsonl"


def architecture_design_nodes_path(workspace: Path, codebase_id: str) -> Path:
    return architecture_dir(workspace, codebase_id) / "design_nodes.jsonl"


def architecture_design_edges_path(workspace: Path, codebase_id: str) -> Path:
    return architecture_dir(workspace, codebase_id) / "design_edges.jsonl"


def architecture_model_path(workspace: Path, codebase_id: str) -> Path:
    return architecture_dir(workspace, codebase_id) / "model.json"


def architecture_alignment_path(workspace: Path, codebase_id: str) -> Path:
    return architecture_dir(workspace, codebase_id) / "alignment.json"


def architecture_findings_path(workspace: Path, codebase_id: str) -> Path:
    return architecture_dir(workspace, codebase_id) / "findings.jsonl"


def architecture_summary_path(workspace: Path, codebase_id: str) -> Path:
    return architecture_dir(workspace, codebase_id) / "summary.json"


def architecture_scale_profile_path(workspace: Path, codebase_id: str) -> Path:
    return architecture_dir(workspace, codebase_id) / "architecture_scale_profile.json"


def architecture_language_facts_path(workspace: Path, codebase_id: str) -> Path:
    return architecture_dir(workspace, codebase_id) / "language_facts.jsonl"


def architecture_config_inventory_path(workspace: Path, codebase_id: str) -> Path:
    return architecture_dir(workspace, codebase_id) / "config_inventory.jsonl"


def architecture_deployment_inventory_path(workspace: Path, codebase_id: str) -> Path:
    return architecture_dir(workspace, codebase_id) / "deployment_inventory.jsonl"


def architecture_schema_inventory_path(workspace: Path, codebase_id: str) -> Path:
    return architecture_dir(workspace, codebase_id) / "schema_inventory.jsonl"


def architecture_taxonomy_path(workspace: Path, codebase_id: str) -> Path:
    return architecture_dir(workspace, codebase_id) / "architecture_taxonomy.json"


def architecture_taxonomy_override_path(workspace: Path, codebase_id: str) -> Path:
    return architecture_dir(workspace, codebase_id) / "architecture_taxonomy_override.json"


def architecture_review_queue_path(workspace: Path, codebase_id: str) -> Path:
    return architecture_dir(workspace, codebase_id) / "architecture_review_queue.jsonl"


def architecture_code_roles_path(workspace: Path, codebase_id: str) -> Path:
    return architecture_dir(workspace, codebase_id) / "code_roles.jsonl"


def architecture_code_layers_path(workspace: Path, codebase_id: str) -> Path:
    return architecture_dir(workspace, codebase_id) / "code_layers.jsonl"


def architecture_code_boundaries_path(workspace: Path, codebase_id: str) -> Path:
    return architecture_dir(workspace, codebase_id) / "code_boundaries.jsonl"


def architecture_pattern_candidates_path(workspace: Path, codebase_id: str) -> Path:
    return architecture_dir(workspace, codebase_id) / "pattern_candidates.jsonl"


def architecture_code_derived_model_path(workspace: Path, codebase_id: str) -> Path:
    return architecture_dir(workspace, codebase_id) / "code_derived_model.json"


def architecture_design_code_drift_path(workspace: Path, codebase_id: str) -> Path:
    return architecture_dir(workspace, codebase_id) / "design_code_drift.jsonl"


def architecture_views_dir(workspace: Path, codebase_id: str) -> Path:
    return architecture_dir(workspace, codebase_id) / "views"


def architecture_view_path(workspace: Path, codebase_id: str, view_id: str) -> Path:
    suffix = "html" if view_id.endswith(".html") else "mmd"
    name = view_id.rsplit(".", 1)[0]
    return architecture_views_dir(workspace, codebase_id) / f"{name}.{suffix}"


def architecture_docs_dir(workspace: Path, codebase_id: str) -> Path:
    return architecture_dir(workspace, codebase_id) / "docs"


def architecture_docs_path(workspace: Path, codebase_id: str) -> Path:
    return architecture_docs_dir(workspace, codebase_id) / "architecture_docs.jsonl"


def architecture_doc_sources_path(workspace: Path, codebase_id: str) -> Path:
    return architecture_docs_dir(workspace, codebase_id) / "architecture_doc_sources.jsonl"


def architecture_doc_claims_path(workspace: Path, codebase_id: str) -> Path:
    return architecture_docs_dir(workspace, codebase_id) / "architecture_doc_claims.jsonl"


def architecture_doc_relations_path(workspace: Path, codebase_id: str) -> Path:
    return architecture_docs_dir(workspace, codebase_id) / "architecture_doc_relations.jsonl"


def architecture_doc_quality_findings_path(workspace: Path, codebase_id: str) -> Path:
    return architecture_docs_dir(workspace, codebase_id) / "architecture_doc_quality_findings.jsonl"


def architecture_doc_quality_summary_path(workspace: Path, codebase_id: str) -> Path:
    return architecture_docs_dir(workspace, codebase_id) / "architecture_doc_quality_summary.json"


def architecture_doc_code_alignment_path(workspace: Path, codebase_id: str) -> Path:
    return architecture_docs_dir(workspace, codebase_id) / "architecture_doc_code_alignment.jsonl"


def architecture_doc_code_drift_v2_path(workspace: Path, codebase_id: str) -> Path:
    return architecture_docs_dir(workspace, codebase_id) / "architecture_doc_code_drift_v2.jsonl"


def architecture_reconstructed_model_path(workspace: Path, codebase_id: str) -> Path:
    return architecture_docs_dir(workspace, codebase_id) / "architecture_reconstructed_model.json"


def architecture_doc_views_dir(workspace: Path, codebase_id: str) -> Path:
    return architecture_docs_dir(workspace, codebase_id) / "views"


def architecture_doc_view_path(workspace: Path, codebase_id: str, view_id: str) -> Path:
    suffix = "html" if view_id.endswith(".html") else "mmd"
    name = view_id.rsplit(".", 1)[0]
    return architecture_doc_views_dir(workspace, codebase_id) / f"{name}.{suffix}"


def architecture_v28_dir(workspace: Path, codebase_id: str) -> Path:
    return architecture_dir(workspace, codebase_id) / "v2_8"


def architecture_reading_dashboard_path(workspace: Path, codebase_id: str) -> Path:
    return architecture_v28_dir(workspace, codebase_id) / "architecture_reading_dashboard.json"


def architecture_v28_views_dir(workspace: Path, codebase_id: str) -> Path:
    return architecture_v28_dir(workspace, codebase_id) / "views"


def architecture_v28_view_path(workspace: Path, codebase_id: str, view_id: str) -> Path:
    suffix = "html" if view_id.endswith(".html") else "mmd"
    name = view_id.rsplit(".", 1)[0]
    return architecture_v28_views_dir(workspace, codebase_id) / f"{name}.{suffix}"


def architecture_graph_summary_v28_path(workspace: Path, codebase_id: str) -> Path:
    return architecture_v28_dir(workspace, codebase_id) / "architecture_graph_summary.json"


def architecture_graph_clusters_v28_path(workspace: Path, codebase_id: str) -> Path:
    return architecture_v28_dir(workspace, codebase_id) / "architecture_graph_clusters.json"


def architecture_graph_views_v28_dir(workspace: Path, codebase_id: str) -> Path:
    return architecture_v28_dir(workspace, codebase_id) / "architecture_graph_views"


def architecture_graph_view_v28_path(workspace: Path, codebase_id: str, view_id: str) -> Path:
    safe = view_id.strip().replace("/", "_") or "system_overview"
    return architecture_graph_views_v28_dir(workspace, codebase_id) / f"{safe}.json"


def architecture_code_fact_chains_v28_path(workspace: Path, codebase_id: str) -> Path:
    return architecture_v28_dir(workspace, codebase_id) / "architecture_code_fact_chains.jsonl"


def architecture_runtime_boundaries_v28_path(workspace: Path, codebase_id: str) -> Path:
    return architecture_v28_dir(workspace, codebase_id) / "architecture_runtime_boundaries.jsonl"


def architecture_signal_ranking_v28_path(workspace: Path, codebase_id: str) -> Path:
    return architecture_v28_dir(workspace, codebase_id) / "architecture_signal_ranking.json"


def architecture_review_queue_v2_v28_path(workspace: Path, codebase_id: str) -> Path:
    return architecture_v28_dir(workspace, codebase_id) / "architecture_review_queue_v2.json"


def architecture_intent_evidence_v28_path(workspace: Path, codebase_id: str) -> Path:
    return architecture_v28_dir(workspace, codebase_id) / "architecture_intent_evidence.jsonl"


def architecture_context_pack_v28_dir(workspace: Path, codebase_id: str) -> Path:
    return architecture_v28_dir(workspace, codebase_id) / "architecture_context_pack_v2"


def architecture_context_pack_v28_path(workspace: Path, codebase_id: str, pack_id: str) -> Path:
    safe = pack_id.strip().replace("/", "_") or "architecture_context_pack"
    return architecture_context_pack_v28_dir(workspace, codebase_id) / f"{safe}.json"


def architecture_v29_dir(workspace: Path, codebase_id: str) -> Path:
    return architecture_dir(workspace, codebase_id) / "v2_9"


def architecture_public_surface_evidence_v29_path(workspace: Path, codebase_id: str) -> Path:
    return architecture_v29_dir(workspace, codebase_id) / "architecture_public_surface_evidence_v2.jsonl"


def architecture_code_relationships_v29_path(workspace: Path, codebase_id: str) -> Path:
    return architecture_v29_dir(workspace, codebase_id) / "architecture_code_relationships_v2.jsonl"


def architecture_module_clusters_v29_path(workspace: Path, codebase_id: str) -> Path:
    return architecture_v29_dir(workspace, codebase_id) / "architecture_module_clusters_v2.json"


def architecture_signal_ranking_v29_path(workspace: Path, codebase_id: str) -> Path:
    return architecture_v29_dir(workspace, codebase_id) / "architecture_signal_ranking_v2.json"


def architecture_review_queue_v29_path(workspace: Path, codebase_id: str) -> Path:
    return architecture_v29_dir(workspace, codebase_id) / "architecture_review_queue_v3.json"


def architecture_human_review_report_v29_path(workspace: Path, codebase_id: str) -> Path:
    return architecture_v29_dir(workspace, codebase_id) / "architecture_human_review_report_v2.json"


def architecture_v29_views_dir(workspace: Path, codebase_id: str) -> Path:
    return architecture_v29_dir(workspace, codebase_id) / "views"


def architecture_v29_view_path(workspace: Path, codebase_id: str, view_id: str) -> Path:
    suffix = "html" if view_id.endswith(".html") else "mmd"
    name = view_id.rsplit(".", 1)[0].strip().replace("/", "_") or "architecture_human_review_report_v2"
    return architecture_v29_views_dir(workspace, codebase_id) / f"{name}.{suffix}"


def architecture_context_pack_v29_dir(workspace: Path, codebase_id: str) -> Path:
    return architecture_v29_dir(workspace, codebase_id) / "architecture_context_pack_v3"


def architecture_v242_dir(workspace: Path, codebase_id: str) -> Path:
    return architecture_dir(workspace, codebase_id) / "v2_42"


def architecture_relationship_chains_v242_path(workspace: Path, codebase_id: str) -> Path:
    return architecture_v242_dir(workspace, codebase_id) / "relationship_chains_v3.jsonl"


def architecture_relationship_chain_summary_v242_path(workspace: Path, codebase_id: str) -> Path:
    return architecture_v242_dir(workspace, codebase_id) / "relationship_chain_summary.json"


def architecture_forbidden_edge_scan_v242_path(workspace: Path, codebase_id: str) -> Path:
    return architecture_v242_dir(workspace, codebase_id) / "forbidden_edge_scan.json"


def architecture_v243_dir(workspace: Path, codebase_id: str) -> Path:
    return architecture_dir(workspace, codebase_id) / "v2_43"


def architecture_document_semantic_claims_v243_path(workspace: Path, codebase_id: str) -> Path:
    return architecture_v243_dir(workspace, codebase_id) / "document_semantic_claims.jsonl"


def architecture_document_semantic_relations_v243_path(workspace: Path, codebase_id: str) -> Path:
    return architecture_v243_dir(workspace, codebase_id) / "document_semantic_relations.jsonl"


def architecture_document_semantic_summary_v243_path(workspace: Path, codebase_id: str) -> Path:
    return architecture_v243_dir(workspace, codebase_id) / "document_semantic_summary.json"


def architecture_v244_dir(workspace: Path, codebase_id: str) -> Path:
    return architecture_dir(workspace, codebase_id) / "v2_44"


def architecture_token_budget_ledger_v244_path(workspace: Path, codebase_id: str) -> Path:
    return architecture_v244_dir(workspace, codebase_id) / "token_budget_ledger.json"


def architecture_context_cache_index_v244_path(workspace: Path, codebase_id: str) -> Path:
    return architecture_v244_dir(workspace, codebase_id) / "context_cache_index.json"


def architecture_context_pack_optimized_v244_dir(workspace: Path, codebase_id: str) -> Path:
    return architecture_v244_dir(workspace, codebase_id) / "context_pack_optimized"


def architecture_context_pack_optimized_v244_path(workspace: Path, codebase_id: str, pack_id: str) -> Path:
    return architecture_context_pack_optimized_v244_dir(workspace, codebase_id) / f"{pack_id}.json"


def architecture_context_pack_optimized_markdown_v244_path(workspace: Path, codebase_id: str, pack_id: str) -> Path:
    return architecture_context_pack_optimized_v244_dir(workspace, codebase_id) / f"{pack_id}.md"


def architecture_v245_dir(workspace: Path, codebase_id: str) -> Path:
    return architecture_dir(workspace, codebase_id) / "v2_45"


def architecture_project_profiles_v245_dir(workspace: Path, codebase_id: str) -> Path:
    return architecture_v245_dir(workspace, codebase_id) / "project_profiles"


def architecture_project_profile_v245_path(workspace: Path, codebase_id: str, profile_id: str) -> Path:
    safe_id = profile_id.replace("/", "_").replace(":", "_")
    return architecture_project_profiles_v245_dir(workspace, codebase_id) / f"{safe_id}.json"


def architecture_taxonomy_registry_v245_path(workspace: Path, codebase_id: str) -> Path:
    return architecture_v245_dir(workspace, codebase_id) / "taxonomy_registry.json"


def architecture_real_repo_regression_matrix_v245_path(workspace: Path, codebase_id: str) -> Path:
    return architecture_v245_dir(workspace, codebase_id) / "real_repo_regression_matrix.json"


def architecture_no_hardcode_audit_v245_path(workspace: Path, codebase_id: str) -> Path:
    return architecture_v245_dir(workspace, codebase_id) / "no_hardcode_audit.json"


def architecture_closure_audit_report_v245_path(workspace: Path, codebase_id: str) -> Path:
    return architecture_v245_dir(workspace, codebase_id) / "closure_audit_report.md"


def architecture_context_pack_v29_path(workspace: Path, codebase_id: str, pack_id: str) -> Path:
    safe = pack_id.strip().replace("/", "_") or "architecture_context_pack"
    return architecture_context_pack_v29_dir(workspace, codebase_id) / f"{safe}.json"


def architecture_v210_dir(workspace: Path, codebase_id: str) -> Path:
    return architecture_dir(workspace, codebase_id) / "v2_10"


def architecture_pattern_adapter_registry_v210_path(workspace: Path, codebase_id: str) -> Path:
    return architecture_v210_dir(workspace, codebase_id) / "pattern_adapter_registry.json"


def architecture_adapter_attempts_v210_path(workspace: Path, codebase_id: str) -> Path:
    return architecture_v210_dir(workspace, codebase_id) / "adapter_attempts.jsonl"


def architecture_ast_bindings_v210_path(workspace: Path, codebase_id: str) -> Path:
    return architecture_v210_dir(workspace, codebase_id) / "adapter_matches.jsonl"


def architecture_definition_lookups_v210_path(workspace: Path, codebase_id: str) -> Path:
    return architecture_v210_dir(workspace, codebase_id) / "definition_lookup_results.jsonl"


def architecture_doc_code_evidence_v3_v210_path(workspace: Path, codebase_id: str) -> Path:
    return architecture_v210_dir(workspace, codebase_id) / "doc_code_evidence_v3.jsonl"


def architecture_manifest_candidates_v210_path(workspace: Path, codebase_id: str) -> Path:
    return architecture_v210_dir(workspace, codebase_id) / "manifest_candidates.jsonl"


def architecture_runtime_candidates_v210_path(workspace: Path, codebase_id: str) -> Path:
    return architecture_v210_dir(workspace, codebase_id) / "runtime_introspection_candidates.jsonl"


def architecture_accepted_pattern_evidence_v210_path(workspace: Path, codebase_id: str) -> Path:
    return architecture_v210_dir(workspace, codebase_id) / "accepted_pattern_evidence.jsonl"


def architecture_pattern_blockers_v210_path(workspace: Path, codebase_id: str) -> Path:
    return architecture_v210_dir(workspace, codebase_id) / "pattern_blockers.jsonl"


def architecture_pattern_evidence_summary_v210_path(workspace: Path, codebase_id: str) -> Path:
    return architecture_v210_dir(workspace, codebase_id) / "pattern_evidence_summary.json"


def architecture_v210_views_dir(workspace: Path, codebase_id: str) -> Path:
    return architecture_v210_dir(workspace, codebase_id) / "views"


def architecture_v210_view_path(workspace: Path, codebase_id: str, view_id: str) -> Path:
    suffix = "html" if view_id.endswith(".html") else "mmd"
    aliases = {
        "pattern_evidence_report.html": "architecture_pattern_evidence_report.html",
        "pattern_evidence_map.mmd": "architecture_pattern_adapter_map.mmd",
    }
    view_id = aliases.get(view_id, view_id)
    name = view_id.rsplit(".", 1)[0].strip().replace("/", "_") or "architecture_pattern_evidence_report"
    return architecture_v210_views_dir(workspace, codebase_id) / f"{name}.{suffix}"


def root_path_hash(root_path: Path | str) -> str:
    return hashlib.sha256(str(Path(root_path).expanduser().resolve()).encode("utf-8")).hexdigest()


def read_index(workspace: Path) -> dict[str, Any]:
    return read_json(codebase_index_path(workspace), {"schema_version": "v2.0", "items": []})


def write_index(workspace: Path, index: dict[str, Any]) -> None:
    write_json(codebase_index_path(workspace), index)


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_name(f".{path.name}.{os.getpid()}.{threading.get_ident()}.tmp")
    tmp_path.write_text("".join(f"{json.dumps(row, ensure_ascii=False)}\n" for row in rows), encoding="utf-8")
    os.replace(tmp_path, path)


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows
