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
    architecture_config_inventory_path,
    architecture_design_code_drift_path,
    architecture_deployment_inventory_path,
    architecture_doc_claims_path,
    architecture_doc_code_alignment_path,
    architecture_doc_code_drift_v2_path,
    architecture_doc_quality_findings_path,
    architecture_doc_quality_summary_path,
    architecture_doc_relations_path,
    architecture_doc_sources_path,
    architecture_docs_path,
    architecture_doc_view_path,
    architecture_graph_clusters_v28_path,
    architecture_graph_summary_v28_path,
    architecture_graph_view_v28_path,
    architecture_code_fact_chains_v28_path,
    architecture_context_pack_v28_path,
    architecture_context_pack_v29_path,
    architecture_context_cache_index_v244_path,
    architecture_context_pack_optimized_markdown_v244_path,
    architecture_context_pack_optimized_v244_path,
    architecture_code_relationships_v29_path,
    architecture_token_budget_ledger_v244_path,
    architecture_adapter_attempts_v210_path,
    architecture_accepted_pattern_evidence_v210_path,
    architecture_ast_bindings_v210_path,
    architecture_definition_lookups_v210_path,
    architecture_doc_code_evidence_v3_v210_path,
    architecture_intent_evidence_v28_path,
    architecture_human_review_report_v29_path,
    architecture_manifest_candidates_v210_path,
    architecture_runtime_boundaries_v28_path,
    architecture_runtime_candidates_v210_path,
    architecture_module_clusters_v29_path,
    architecture_pattern_adapter_registry_v210_path,
    architecture_pattern_blockers_v210_path,
    architecture_pattern_evidence_summary_v210_path,
    architecture_public_surface_evidence_v29_path,
    architecture_review_queue_v2_v28_path,
    architecture_review_queue_v29_path,
    architecture_reading_dashboard_path,
    architecture_signal_ranking_v29_path,
    architecture_signal_ranking_v28_path,
    architecture_v29_view_path,
    architecture_v210_view_path,
    architecture_pattern_candidates_path,
    architecture_design_edges_path,
    architecture_design_nodes_path,
    architecture_findings_path,
    architecture_language_facts_path,
    architecture_model_path,
    architecture_scale_profile_path,
    architecture_schema_inventory_path,
    architecture_sources_path,
    architecture_summary_path,
    architecture_taxonomy_path,
    architecture_review_queue_path,
    architecture_reconstructed_model_path,
    architecture_v28_view_path,
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


def architecture_scale_artifact_refs(codebase_id: str) -> list[dict[str, str]]:
    return [
        {"type": "architecture_scale_profile", "artifact_ref": f"architecture://{codebase_id}/architecture_scale_profile.json"},
        {"type": "architecture_scale_budget_report", "artifact_ref": f"architecture://{codebase_id}/scale/scan_budget_report.json"},
        {"type": "architecture_scale_readback_index", "artifact_ref": f"architecture://{codebase_id}/scale/paginated_readback_index.json"},
        {"type": "architecture_scale_file_shard", "artifact_ref": f"architecture://{codebase_id}/scale/scan_shards/files_0001.jsonl"},
        {"type": "architecture_scale_language_shard", "artifact_ref": f"architecture://{codebase_id}/scale/scan_shards/languages_0001.jsonl"},
    ]


def architecture_inventory_artifact_refs(codebase_id: str) -> list[dict[str, str]]:
    return [
        {"type": "architecture_language_facts", "artifact_ref": f"architecture://{codebase_id}/language_facts.jsonl"},
        {"type": "architecture_config_inventory", "artifact_ref": f"architecture://{codebase_id}/config_inventory.jsonl"},
        {"type": "architecture_deployment_inventory", "artifact_ref": f"architecture://{codebase_id}/deployment_inventory.jsonl"},
        {"type": "architecture_schema_inventory", "artifact_ref": f"architecture://{codebase_id}/schema_inventory.jsonl"},
    ]


def architecture_taxonomy_artifact_refs(codebase_id: str) -> list[dict[str, str]]:
    return [
        {"type": "architecture_taxonomy", "artifact_ref": f"architecture://{codebase_id}/architecture_taxonomy.json"},
        {"type": "architecture_review_queue", "artifact_ref": f"architecture://{codebase_id}/architecture_review_queue.jsonl"},
    ]


def architecture_doc_registry_artifact_refs(codebase_id: str) -> list[dict[str, str]]:
    return [
        {"type": "architecture_docs", "artifact_ref": f"architecture-docs://{codebase_id}/architecture_docs.jsonl"},
        {"type": "architecture_doc_sources", "artifact_ref": f"architecture-docs://{codebase_id}/architecture_doc_sources.jsonl"},
    ]


def architecture_doc_claim_artifact_refs(codebase_id: str) -> list[dict[str, str]]:
    return [
        {"type": "architecture_doc_claims", "artifact_ref": f"architecture-docs://{codebase_id}/architecture_doc_claims.jsonl"},
        {"type": "architecture_doc_relations", "artifact_ref": f"architecture-docs://{codebase_id}/architecture_doc_relations.jsonl"},
    ]


def architecture_doc_quality_artifact_refs(codebase_id: str) -> list[dict[str, str]]:
    return [
        {"type": "architecture_doc_quality_findings", "artifact_ref": f"architecture-docs://{codebase_id}/architecture_doc_quality_findings.jsonl"},
        {"type": "architecture_doc_quality_summary", "artifact_ref": f"architecture-docs://{codebase_id}/architecture_doc_quality_summary.json"},
    ]


def architecture_doc_code_alignment_artifact_refs(codebase_id: str) -> list[dict[str, str]]:
    return [
        {"type": "architecture_doc_code_alignment", "artifact_ref": f"architecture-docs://{codebase_id}/architecture_doc_code_alignment.jsonl"},
        {"type": "architecture_doc_code_drift_v2", "artifact_ref": f"architecture-docs://{codebase_id}/architecture_doc_code_drift_v2.jsonl"},
    ]


def architecture_reconstructed_artifact_refs(codebase_id: str) -> list[dict[str, str]]:
    return [
        {"type": "architecture_reconstructed_model", "artifact_ref": f"architecture-docs://{codebase_id}/architecture_reconstructed_model.json"},
        {"type": "architecture_doc_html_report", "artifact_ref": f"architecture-docs://{codebase_id}/views/document_code_architecture_report.html"},
        {"type": "architecture_doc_mermaid_diff", "artifact_ref": f"architecture-docs://{codebase_id}/views/document_code_architecture_diff.mmd"},
    ]


def architecture_reading_dashboard_artifact_refs(codebase_id: str) -> list[dict[str, str]]:
    return [
        {"type": "architecture_reading_dashboard", "artifact_ref": f"architecture-v2-8://{codebase_id}/architecture_reading_dashboard.json"},
        {"type": "architecture_reading_html", "artifact_ref": f"architecture-v2-8://{codebase_id}/views/architecture_reading_dashboard.html"},
        {"type": "architecture_relationship_summary", "artifact_ref": f"architecture-v2-8://{codebase_id}/views/architecture_relationship_summary.mmd"},
    ]


def architecture_graph_v28_artifact_refs(codebase_id: str) -> list[dict[str, str]]:
    return [
        {"type": "architecture_graph_summary", "artifact_ref": f"architecture-v2-8://{codebase_id}/architecture_graph_summary.json"},
        {"type": "architecture_graph_clusters", "artifact_ref": f"architecture-v2-8://{codebase_id}/architecture_graph_clusters.json"},
        {"type": "architecture_graph_views", "artifact_ref": f"architecture-v2-8://{codebase_id}/architecture_graph_views"},
    ]


def architecture_code_fact_chain_artifact_refs(codebase_id: str) -> list[dict[str, str]]:
    return [
        {"type": "architecture_code_fact_chains", "artifact_ref": f"architecture-v2-8://{codebase_id}/architecture_code_fact_chains.jsonl"},
        {"type": "architecture_runtime_boundaries", "artifact_ref": f"architecture-v2-8://{codebase_id}/architecture_runtime_boundaries.jsonl"},
    ]


def architecture_signal_ranking_artifact_refs(codebase_id: str) -> list[dict[str, str]]:
    return [
        {"type": "architecture_signal_ranking", "artifact_ref": f"architecture-v2-8://{codebase_id}/architecture_signal_ranking.json"},
        {"type": "architecture_review_queue_v2", "artifact_ref": f"architecture-v2-8://{codebase_id}/architecture_review_queue_v2.json"},
    ]


def architecture_intent_evidence_artifact_refs(codebase_id: str) -> list[dict[str, str]]:
    return [
        {"type": "architecture_intent_evidence", "artifact_ref": f"architecture-v2-8://{codebase_id}/architecture_intent_evidence.jsonl"},
    ]


def architecture_context_pack_v2_artifact_refs(codebase_id: str, pack_id: str) -> list[dict[str, str]]:
    return [
        {"type": "architecture_context_pack_v2", "artifact_ref": f"architecture-v2-8://{codebase_id}/architecture_context_pack_v2/{pack_id}.json"},
    ]


def architecture_public_surface_evidence_v29_artifact_refs(codebase_id: str) -> list[dict[str, str]]:
    return [{"type": "architecture_public_surface_evidence_v2", "artifact_ref": f"architecture-v2-9://{codebase_id}/architecture_public_surface_evidence_v2.jsonl"}]


def architecture_relationships_v29_artifact_refs(codebase_id: str) -> list[dict[str, str]]:
    return [
        {"type": "architecture_code_relationships_v2", "artifact_ref": f"architecture-v2-9://{codebase_id}/architecture_code_relationships_v2.jsonl"},
        {"type": "architecture_module_clusters_v2", "artifact_ref": f"architecture-v2-9://{codebase_id}/architecture_module_clusters_v2.json"},
    ]


def architecture_relationship_chains_v242_artifact_refs(codebase_id: str) -> list[dict[str, str]]:
    return [
        {"type": "relationship_chains_v3", "artifact_ref": f"architecture-v2-42://{codebase_id}/relationship_chains_v3.jsonl"},
        {"type": "relationship_chain_summary", "artifact_ref": f"architecture-v2-42://{codebase_id}/relationship_chain_summary.json"},
        {"type": "forbidden_edge_scan", "artifact_ref": f"architecture-v2-42://{codebase_id}/forbidden_edge_scan.json"},
    ]


def architecture_document_semantics_v243_artifact_refs(codebase_id: str) -> list[dict[str, str]]:
    return [
        {"type": "document_semantic_claims", "artifact_ref": f"architecture-v2-43://{codebase_id}/document_semantic_claims.jsonl"},
        {"type": "document_semantic_relations", "artifact_ref": f"architecture-v2-43://{codebase_id}/document_semantic_relations.jsonl"},
        {"type": "document_semantic_summary", "artifact_ref": f"architecture-v2-43://{codebase_id}/document_semantic_summary.json"},
    ]


def architecture_context_pack_optimized_v244_artifact_refs(codebase_id: str, pack_id: str | None = None) -> list[dict[str, str]]:
    refs = [
        {"type": "token_budget_ledger", "artifact_ref": f"architecture-v2-44://{codebase_id}/token_budget_ledger.json"},
        {"type": "context_cache_index", "artifact_ref": f"architecture-v2-44://{codebase_id}/context_cache_index.json"},
    ]
    if pack_id:
        refs.extend(
            [
                {"type": "context_pack_optimized_json", "artifact_ref": f"architecture-v2-44://{codebase_id}/context_pack_optimized/{pack_id}.json"},
                {"type": "context_pack_optimized_markdown", "artifact_ref": f"architecture-v2-44://{codebase_id}/context_pack_optimized/{pack_id}.md"},
            ]
        )
    return refs


def architecture_signal_ranking_v29_artifact_refs(codebase_id: str) -> list[dict[str, str]]:
    return [
        {"type": "architecture_signal_ranking_v2", "artifact_ref": f"architecture-v2-9://{codebase_id}/architecture_signal_ranking_v2.json"},
        {"type": "architecture_review_queue_v3", "artifact_ref": f"architecture-v2-9://{codebase_id}/architecture_review_queue_v3.json"},
    ]


def architecture_human_report_v29_artifact_refs(codebase_id: str) -> list[dict[str, str]]:
    return [
        {"type": "architecture_human_review_report_v2", "artifact_ref": f"architecture-v2-9://{codebase_id}/architecture_human_review_report_v2.json"},
        {"type": "architecture_human_review_report_html", "artifact_ref": f"architecture-v2-9://{codebase_id}/views/architecture_human_review_report_v2.html"},
        {"type": "architecture_evidence_heatmap", "artifact_ref": f"architecture-v2-9://{codebase_id}/views/architecture_evidence_heatmap.mmd"},
        {"type": "architecture_capability_entrypoint_map", "artifact_ref": f"architecture-v2-9://{codebase_id}/views/architecture_capability_entrypoint_map.mmd"},
    ]


def architecture_context_pack_v3_artifact_refs(codebase_id: str, pack_id: str) -> list[dict[str, str]]:
    return [{"type": "architecture_context_pack_v3", "artifact_ref": f"architecture-v2-9://{codebase_id}/architecture_context_pack_v3/{pack_id}.json"}]


def architecture_pattern_evidence_v210_artifact_refs(codebase_id: str) -> list[dict[str, str]]:
    return [
        {"type": "pattern_adapter_registry", "artifact_ref": f"architecture-v2-10://{codebase_id}/pattern_adapter_registry.json"},
        {"type": "adapter_attempts", "artifact_ref": f"architecture-v2-10://{codebase_id}/adapter_attempts.jsonl"},
        {"type": "adapter_matches", "artifact_ref": f"architecture-v2-10://{codebase_id}/adapter_matches.jsonl"},
        {"type": "definition_lookup_results", "artifact_ref": f"architecture-v2-10://{codebase_id}/definition_lookup_results.jsonl"},
        {"type": "doc_code_evidence_v3", "artifact_ref": f"architecture-v2-10://{codebase_id}/doc_code_evidence_v3.jsonl"},
        {"type": "manifest_candidates", "artifact_ref": f"architecture-v2-10://{codebase_id}/manifest_candidates.jsonl"},
        {"type": "runtime_introspection_candidates", "artifact_ref": f"architecture-v2-10://{codebase_id}/runtime_introspection_candidates.jsonl"},
        {"type": "accepted_pattern_evidence", "artifact_ref": f"architecture-v2-10://{codebase_id}/accepted_pattern_evidence.jsonl"},
        {"type": "pattern_blockers", "artifact_ref": f"architecture-v2-10://{codebase_id}/pattern_blockers.jsonl"},
        {"type": "pattern_evidence_summary", "artifact_ref": f"architecture-v2-10://{codebase_id}/pattern_evidence_summary.json"},
        {"type": "pattern_evidence_html", "artifact_ref": f"architecture-v2-10://{codebase_id}/views/architecture_pattern_evidence_report.html"},
        {"type": "pattern_evidence_mermaid", "artifact_ref": f"architecture-v2-10://{codebase_id}/views/architecture_pattern_adapter_map.mmd"},
    ]


def architecture_doc_code_alignment_artifact_refs(codebase_id: str) -> list[dict[str, str]]:
    return [
        {"type": "architecture_doc_code_alignment", "artifact_ref": f"architecture-docs://{codebase_id}/architecture_doc_code_alignment.jsonl"},
        {"type": "architecture_doc_code_drift_v2", "artifact_ref": f"architecture-docs://{codebase_id}/architecture_doc_code_drift_v2.jsonl"},
    ]


def write_architecture_scale_profile(workspace: Path, codebase_id: str, profile: dict[str, Any]) -> None:
    write_json(architecture_scale_profile_path(workspace, codebase_id), profile)


def read_architecture_scale_profile(workspace: Path, codebase_id: str) -> dict[str, Any]:
    payload = read_json(architecture_scale_profile_path(workspace, codebase_id), None)
    if not payload:
        raise FileNotFoundError("ARCHITECTURE_SCALE_PROFILE_NOT_BUILT")
    return payload


def write_architecture_inventory(
    workspace: Path,
    codebase_id: str,
    *,
    language_facts: list[dict[str, Any]],
    config_inventory: list[dict[str, Any]],
    deployment_inventory: list[dict[str, Any]],
    schema_inventory: list[dict[str, Any]],
) -> None:
    write_jsonl(architecture_language_facts_path(workspace, codebase_id), language_facts)
    write_jsonl(architecture_config_inventory_path(workspace, codebase_id), config_inventory)
    write_jsonl(architecture_deployment_inventory_path(workspace, codebase_id), deployment_inventory)
    write_jsonl(architecture_schema_inventory_path(workspace, codebase_id), schema_inventory)


def read_architecture_inventory(workspace: Path, codebase_id: str) -> dict[str, list[dict[str, Any]]]:
    language_facts = read_jsonl(architecture_language_facts_path(workspace, codebase_id))
    config_inventory = read_jsonl(architecture_config_inventory_path(workspace, codebase_id))
    deployment_inventory = read_jsonl(architecture_deployment_inventory_path(workspace, codebase_id))
    schema_inventory = read_jsonl(architecture_schema_inventory_path(workspace, codebase_id))
    if not language_facts and not config_inventory and not deployment_inventory and not schema_inventory:
        raise FileNotFoundError("ARCHITECTURE_INVENTORY_NOT_BUILT")
    return {
        "language_facts": language_facts,
        "config_inventory": config_inventory,
        "deployment_inventory": deployment_inventory,
        "schema_inventory": schema_inventory,
    }


def read_architecture_language_facts(workspace: Path, codebase_id: str) -> list[dict[str, Any]]:
    items = read_jsonl(architecture_language_facts_path(workspace, codebase_id))
    if not items:
        raise FileNotFoundError("ARCHITECTURE_LANGUAGE_FACTS_NOT_BUILT")
    return items


def read_architecture_config_inventory(workspace: Path, codebase_id: str) -> list[dict[str, Any]]:
    items = read_jsonl(architecture_config_inventory_path(workspace, codebase_id))
    if not items:
        raise FileNotFoundError("ARCHITECTURE_CONFIG_INVENTORY_NOT_BUILT")
    return items


def read_architecture_deployment_inventory(workspace: Path, codebase_id: str) -> list[dict[str, Any]]:
    items = read_jsonl(architecture_deployment_inventory_path(workspace, codebase_id))
    if not items:
        raise FileNotFoundError("ARCHITECTURE_DEPLOYMENT_INVENTORY_NOT_BUILT")
    return items


def read_architecture_schema_inventory(workspace: Path, codebase_id: str) -> list[dict[str, Any]]:
    items = read_jsonl(architecture_schema_inventory_path(workspace, codebase_id))
    if not items:
        raise FileNotFoundError("ARCHITECTURE_SCHEMA_INVENTORY_NOT_BUILT")
    return items


def write_architecture_taxonomy(workspace: Path, codebase_id: str, taxonomy: dict[str, Any]) -> None:
    write_json(architecture_taxonomy_path(workspace, codebase_id), taxonomy)


def read_architecture_taxonomy(workspace: Path, codebase_id: str) -> dict[str, Any]:
    taxonomy = read_json(architecture_taxonomy_path(workspace, codebase_id), None)
    if not taxonomy:
        raise FileNotFoundError("ARCHITECTURE_TAXONOMY_NOT_BUILT")
    return taxonomy


def write_architecture_review_queue(workspace: Path, codebase_id: str, queue: list[dict[str, Any]]) -> None:
    write_jsonl(architecture_review_queue_path(workspace, codebase_id), queue)


def read_architecture_review_queue(workspace: Path, codebase_id: str) -> list[dict[str, Any]]:
    items = read_jsonl(architecture_review_queue_path(workspace, codebase_id))
    if not items:
        raise FileNotFoundError("ARCHITECTURE_REVIEW_QUEUE_NOT_BUILT")
    return items


def write_architecture_doc_registry(workspace: Path, codebase_id: str, docs: list[dict[str, Any]], sources: list[dict[str, Any]]) -> None:
    write_jsonl(architecture_docs_path(workspace, codebase_id), docs)
    write_jsonl(architecture_doc_sources_path(workspace, codebase_id), sources)


def read_architecture_doc_registry(workspace: Path, codebase_id: str) -> dict[str, list[dict[str, Any]]]:
    docs = read_jsonl(architecture_docs_path(workspace, codebase_id))
    sources = read_jsonl(architecture_doc_sources_path(workspace, codebase_id))
    if not docs and not sources:
        raise FileNotFoundError("ARCHITECTURE_DOCS_NOT_BUILT")
    return {"documents": docs, "sources": sources}


def write_architecture_doc_claims(workspace: Path, codebase_id: str, claims: list[dict[str, Any]], relations: list[dict[str, Any]]) -> None:
    write_jsonl(architecture_doc_claims_path(workspace, codebase_id), claims)
    write_jsonl(architecture_doc_relations_path(workspace, codebase_id), relations)


def read_architecture_doc_claims(workspace: Path, codebase_id: str) -> dict[str, list[dict[str, Any]]]:
    claims = read_jsonl(architecture_doc_claims_path(workspace, codebase_id))
    relations = read_jsonl(architecture_doc_relations_path(workspace, codebase_id))
    if not claims and not relations:
        raise FileNotFoundError("ARCHITECTURE_DOC_CLAIMS_NOT_BUILT")
    return {"claims": claims, "relations": relations}


def write_architecture_doc_quality(workspace: Path, codebase_id: str, findings: list[dict[str, Any]], summary: dict[str, Any]) -> None:
    write_jsonl(architecture_doc_quality_findings_path(workspace, codebase_id), findings)
    write_json(architecture_doc_quality_summary_path(workspace, codebase_id), summary)


def read_architecture_doc_quality(workspace: Path, codebase_id: str) -> dict[str, Any]:
    findings = read_jsonl(architecture_doc_quality_findings_path(workspace, codebase_id))
    summary = read_json(architecture_doc_quality_summary_path(workspace, codebase_id), None)
    if not findings and not summary:
        raise FileNotFoundError("ARCHITECTURE_DOC_QUALITY_NOT_BUILT")
    return {"findings": findings, "summary": summary or {}}


def write_architecture_doc_code_alignment(workspace: Path, codebase_id: str, alignments: list[dict[str, Any]], drift: list[dict[str, Any]]) -> None:
    write_jsonl(architecture_doc_code_alignment_path(workspace, codebase_id), alignments)
    write_jsonl(architecture_doc_code_drift_v2_path(workspace, codebase_id), drift)


def read_architecture_doc_code_alignment(workspace: Path, codebase_id: str) -> dict[str, list[dict[str, Any]]]:
    alignments = read_jsonl(architecture_doc_code_alignment_path(workspace, codebase_id))
    drift = read_jsonl(architecture_doc_code_drift_v2_path(workspace, codebase_id))
    if not alignments and not drift:
        raise FileNotFoundError("ARCHITECTURE_DOC_ALIGNMENT_NOT_BUILT")
    return {"alignments": alignments, "drift": drift}


def write_architecture_reconstructed_model(workspace: Path, codebase_id: str, model: dict[str, Any], html: str, mermaid: str) -> None:
    write_json(architecture_reconstructed_model_path(workspace, codebase_id), model)
    html_path = architecture_doc_view_path(workspace, codebase_id, "document_code_architecture_report.html")
    mermaid_path = architecture_doc_view_path(workspace, codebase_id, "document_code_architecture_diff.mmd")
    html_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.write_text(html, encoding="utf-8")
    mermaid_path.write_text(mermaid, encoding="utf-8")


def read_architecture_reconstructed_model(workspace: Path, codebase_id: str) -> dict[str, Any]:
    payload = read_json(architecture_reconstructed_model_path(workspace, codebase_id), None)
    if not payload:
        raise FileNotFoundError("ARCHITECTURE_RECONSTRUCTION_NOT_BUILT")
    return payload


def read_architecture_doc_view(workspace: Path, codebase_id: str, view_id: str) -> str:
    path = architecture_doc_view_path(workspace, codebase_id, view_id)
    if not path.exists():
        raise FileNotFoundError("ARCHITECTURE_DOC_VIEW_NOT_FOUND")
    return path.read_text(encoding="utf-8")


def write_architecture_reading_dashboard(workspace: Path, codebase_id: str, dashboard: dict[str, Any], html: str, mermaid: str) -> None:
    write_json(architecture_reading_dashboard_path(workspace, codebase_id), dashboard)
    html_path = architecture_v28_view_path(workspace, codebase_id, "architecture_reading_dashboard.html")
    mermaid_path = architecture_v28_view_path(workspace, codebase_id, "architecture_relationship_summary.mmd")
    html_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.write_text(html, encoding="utf-8")
    mermaid_path.write_text(mermaid, encoding="utf-8")


def read_architecture_reading_dashboard(workspace: Path, codebase_id: str) -> dict[str, Any]:
    payload = read_json(architecture_reading_dashboard_path(workspace, codebase_id), None)
    if not payload:
        raise FileNotFoundError("ARCHITECTURE_READING_DASHBOARD_NOT_BUILT")
    return payload


def read_architecture_v28_view(workspace: Path, codebase_id: str, view_id: str) -> str:
    path = architecture_v28_view_path(workspace, codebase_id, view_id)
    if not path.exists():
        raise FileNotFoundError("ARCHITECTURE_V28_VIEW_NOT_FOUND")
    return path.read_text(encoding="utf-8")


def write_architecture_graph_v28(workspace: Path, codebase_id: str, summary: dict[str, Any], clusters: dict[str, Any], views: dict[str, dict[str, Any]]) -> None:
    write_json(architecture_graph_summary_v28_path(workspace, codebase_id), summary)
    write_json(architecture_graph_clusters_v28_path(workspace, codebase_id), clusters)
    for view_id, view in views.items():
        write_json(architecture_graph_view_v28_path(workspace, codebase_id, view_id), view)


def read_architecture_graph_v28(workspace: Path, codebase_id: str) -> dict[str, Any]:
    summary = read_json(architecture_graph_summary_v28_path(workspace, codebase_id), None)
    clusters = read_json(architecture_graph_clusters_v28_path(workspace, codebase_id), None)
    if not summary or not clusters:
        raise FileNotFoundError("ARCHITECTURE_GRAPH_SUMMARY_NOT_BUILT")
    return {"summary": summary, "clusters": clusters}


def read_architecture_graph_view_v28(workspace: Path, codebase_id: str, view_id: str) -> dict[str, Any]:
    view = read_json(architecture_graph_view_v28_path(workspace, codebase_id, view_id), None)
    if not view:
        raise FileNotFoundError("ARCHITECTURE_GRAPH_VIEW_NOT_FOUND")
    return view


def write_architecture_code_fact_chains(workspace: Path, codebase_id: str, chains: list[dict[str, Any]], boundaries: list[dict[str, Any]]) -> None:
    write_jsonl(architecture_code_fact_chains_v28_path(workspace, codebase_id), chains)
    write_jsonl(architecture_runtime_boundaries_v28_path(workspace, codebase_id), boundaries)


def read_architecture_code_fact_chains(workspace: Path, codebase_id: str) -> dict[str, list[dict[str, Any]]]:
    chains = read_jsonl(architecture_code_fact_chains_v28_path(workspace, codebase_id))
    boundaries = read_jsonl(architecture_runtime_boundaries_v28_path(workspace, codebase_id))
    if not chains and not boundaries:
        raise FileNotFoundError("ARCHITECTURE_CODE_FACT_CHAINS_NOT_BUILT")
    return {"chains": chains, "runtime_boundaries": boundaries}


def write_architecture_signal_ranking(workspace: Path, codebase_id: str, ranking: dict[str, Any], queue: dict[str, Any]) -> None:
    write_json(architecture_signal_ranking_v28_path(workspace, codebase_id), ranking)
    write_json(architecture_review_queue_v2_v28_path(workspace, codebase_id), queue)


def read_architecture_signal_ranking(workspace: Path, codebase_id: str) -> dict[str, Any]:
    ranking = read_json(architecture_signal_ranking_v28_path(workspace, codebase_id), None)
    queue = read_json(architecture_review_queue_v2_v28_path(workspace, codebase_id), None)
    if not ranking and not queue:
        raise FileNotFoundError("ARCHITECTURE_SIGNAL_RANKING_NOT_BUILT")
    return {"ranking": ranking or {}, "review_queue_v2": queue or {}}


def write_architecture_intent_evidence(workspace: Path, codebase_id: str, intents: list[dict[str, Any]]) -> None:
    write_jsonl(architecture_intent_evidence_v28_path(workspace, codebase_id), intents)


def read_architecture_intent_evidence(workspace: Path, codebase_id: str) -> list[dict[str, Any]]:
    items = read_jsonl(architecture_intent_evidence_v28_path(workspace, codebase_id))
    if not items:
        raise FileNotFoundError("ARCHITECTURE_INTENT_EVIDENCE_NOT_BUILT")
    return items


def write_architecture_context_pack_v2(workspace: Path, codebase_id: str, pack_id: str, pack: dict[str, Any]) -> None:
    write_json(architecture_context_pack_v28_path(workspace, codebase_id, pack_id), pack)


def read_architecture_context_pack_v2(workspace: Path, codebase_id: str, pack_id: str) -> dict[str, Any]:
    payload = read_json(architecture_context_pack_v28_path(workspace, codebase_id, pack_id), None)
    if not payload:
        raise FileNotFoundError("ARCHITECTURE_CONTEXT_PACK_NOT_FOUND")
    return payload


def write_architecture_public_surface_evidence_v29(workspace: Path, codebase_id: str, payload: dict[str, Any]) -> None:
    write_json(architecture_public_surface_evidence_v29_path(workspace, codebase_id), payload)


def read_architecture_public_surface_evidence_v29(workspace: Path, codebase_id: str) -> dict[str, Any]:
    payload = read_json(architecture_public_surface_evidence_v29_path(workspace, codebase_id), None)
    if payload:
        return payload
    rows = read_jsonl(architecture_public_surface_evidence_v29_path(workspace, codebase_id))
    if rows:
        return {"schema_version": "v2.9", "evidence": rows, "summary": {"evidence_row_count": len(rows)}, "artifact_refs": architecture_public_surface_evidence_v29_artifact_refs(codebase_id)}
    else:
        raise FileNotFoundError("ARCHITECTURE_PUBLIC_SURFACE_EVIDENCE_NOT_BUILT")


def write_architecture_relationships_v29(workspace: Path, codebase_id: str, payload: dict[str, Any]) -> None:
    write_json(architecture_code_relationships_v29_path(workspace, codebase_id), payload)
    write_json(architecture_module_clusters_v29_path(workspace, codebase_id), {"clusters": payload.get("clusters", []), "summary": payload.get("summary", {})})


def read_architecture_relationships_v29(workspace: Path, codebase_id: str) -> dict[str, Any]:
    payload = read_json(architecture_code_relationships_v29_path(workspace, codebase_id), None)
    if payload:
        return payload
    relationships = read_jsonl(architecture_code_relationships_v29_path(workspace, codebase_id))
    clusters = read_json(architecture_module_clusters_v29_path(workspace, codebase_id), None)
    if not relationships and not clusters:
        raise FileNotFoundError("ARCHITECTURE_RELATIONSHIPS_V29_NOT_BUILT")
    cluster_items = clusters.get("clusters", clusters) if isinstance(clusters, dict) else clusters
    return {"schema_version": "v2.9", "relationships": relationships, "clusters": cluster_items or [], "summary": {"relationship_count": len(relationships), "cluster_count": len(cluster_items or [])}}


def write_architecture_signal_ranking_v29(workspace: Path, codebase_id: str, ranking: dict[str, Any], review_queue: dict[str, Any]) -> None:
    write_json(architecture_signal_ranking_v29_path(workspace, codebase_id), ranking)
    write_json(architecture_review_queue_v29_path(workspace, codebase_id), review_queue)


def read_architecture_signal_ranking_v29(workspace: Path, codebase_id: str) -> dict[str, Any]:
    ranking = read_json(architecture_signal_ranking_v29_path(workspace, codebase_id), None)
    review_queue = read_json(architecture_review_queue_v29_path(workspace, codebase_id), None)
    if not ranking and not review_queue:
        raise FileNotFoundError("ARCHITECTURE_RANKING_V2_NOT_BUILT")
    return {"ranking": ranking or {}, "review_queue_v3": review_queue or {}}


def write_architecture_human_report_v29(workspace: Path, codebase_id: str, report: dict[str, Any], views: dict[str, Any]) -> None:
    write_json(architecture_human_review_report_v29_path(workspace, codebase_id), report)
    for view_id, view in views.items():
        path = architecture_v29_view_path(workspace, codebase_id, view_id)
        path.parent.mkdir(parents=True, exist_ok=True)
        content = view.get("content", "") if isinstance(view, dict) else str(view)
        path.write_text(content, encoding="utf-8")


def read_architecture_human_report_v29(workspace: Path, codebase_id: str) -> dict[str, Any]:
    report = read_json(architecture_human_review_report_v29_path(workspace, codebase_id), None)
    if not report:
        raise FileNotFoundError("ARCHITECTURE_HUMAN_REPORT_V29_NOT_BUILT")
    return {"schema_version": "v2.9", "report": report, "artifact_refs": architecture_human_report_v29_artifact_refs(codebase_id)}


def read_architecture_human_report_view_v29(workspace: Path, codebase_id: str, view_id: str) -> dict[str, Any]:
    path = architecture_v29_view_path(workspace, codebase_id, view_id)
    if not path.exists():
        raise FileNotFoundError("ARCHITECTURE_HUMAN_REPORT_VIEW_NOT_FOUND")
    return {"view_id": view_id, "content_type": "text/html" if view_id.endswith(".html") else "text/mermaid", "content": path.read_text(encoding="utf-8")}


def write_architecture_context_pack_v3(workspace: Path, codebase_id: str, pack_id: str, pack: dict[str, Any]) -> None:
    write_json(architecture_context_pack_v29_path(workspace, codebase_id, pack_id), pack)


def read_architecture_context_pack_v3(workspace: Path, codebase_id: str, pack_id: str) -> dict[str, Any]:
    payload = read_json(architecture_context_pack_v29_path(workspace, codebase_id, pack_id), None)
    if not payload:
        raise FileNotFoundError("ARCHITECTURE_CONTEXT_PACK_V3_NOT_FOUND")
    return payload


def write_architecture_context_pack_optimized_v244(workspace: Path, codebase_id: str, pack_id: str, pack: dict[str, Any], markdown: str, ledger: dict[str, Any], cache_index: dict[str, Any]) -> None:
    write_json(architecture_context_pack_optimized_v244_path(workspace, codebase_id, pack_id), pack)
    md_path = architecture_context_pack_optimized_markdown_v244_path(workspace, codebase_id, pack_id)
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(markdown, encoding="utf-8")
    write_json(architecture_token_budget_ledger_v244_path(workspace, codebase_id), ledger)
    write_json(architecture_context_cache_index_v244_path(workspace, codebase_id), cache_index)


def read_architecture_context_pack_optimized_v244(workspace: Path, codebase_id: str, pack_id: str) -> dict[str, Any]:
    payload = read_json(architecture_context_pack_optimized_v244_path(workspace, codebase_id, pack_id), None)
    if not payload:
        raise FileNotFoundError("ARCHITECTURE_CONTEXT_PACK_OPTIMIZED_V244_NOT_FOUND")
    md_path = architecture_context_pack_optimized_markdown_v244_path(workspace, codebase_id, pack_id)
    payload["markdown"] = md_path.read_text(encoding="utf-8") if md_path.exists() else payload.get("markdown", "")
    payload["ledger"] = read_json(architecture_token_budget_ledger_v244_path(workspace, codebase_id), {})
    payload["cache_index"] = read_json(architecture_context_cache_index_v244_path(workspace, codebase_id), {})
    return payload


def write_architecture_pattern_evidence_v210(workspace: Path, codebase_id: str, payload: dict[str, Any]) -> None:
    write_json(architecture_pattern_adapter_registry_v210_path(workspace, codebase_id), payload["registry"])
    write_jsonl(architecture_adapter_attempts_v210_path(workspace, codebase_id), payload.get("attempts", []))
    write_jsonl(architecture_ast_bindings_v210_path(workspace, codebase_id), payload.get("bindings", []))
    write_jsonl(architecture_definition_lookups_v210_path(workspace, codebase_id), payload.get("definition_lookups", []))
    write_jsonl(architecture_doc_code_evidence_v3_v210_path(workspace, codebase_id), payload.get("doc_code_evidence_v3", []))
    write_jsonl(architecture_manifest_candidates_v210_path(workspace, codebase_id), payload.get("manifest_candidates", []))
    write_jsonl(architecture_runtime_candidates_v210_path(workspace, codebase_id), payload.get("runtime_candidates", []))
    write_jsonl(architecture_accepted_pattern_evidence_v210_path(workspace, codebase_id), payload.get("accepted_evidence", []))
    write_jsonl(architecture_pattern_blockers_v210_path(workspace, codebase_id), payload.get("blockers", []))
    write_json(architecture_pattern_evidence_summary_v210_path(workspace, codebase_id), {"schema_version": "v2.10", **payload.get("summary", {}), "report": payload.get("report", {})})
    for view_id, view in payload.get("views", {}).items():
        path = architecture_v210_view_path(workspace, codebase_id, view_id)
        path.parent.mkdir(parents=True, exist_ok=True)
        content = view.get("content", "") if isinstance(view, dict) else str(view)
        path.write_text(content, encoding="utf-8")


def read_architecture_pattern_evidence_v210(workspace: Path, codebase_id: str) -> dict[str, Any]:
    registry = read_json(architecture_pattern_adapter_registry_v210_path(workspace, codebase_id), None)
    summary = read_json(architecture_pattern_evidence_summary_v210_path(workspace, codebase_id), None)
    if not registry or not summary:
        raise FileNotFoundError("ARCHITECTURE_PATTERN_ADAPTERS_NOT_BUILT")
    return {
        "schema_version": "v2.10",
        "workspace_id": registry.get("workspace_id"),
        "codebase_id": codebase_id,
        "snapshot_id": registry.get("snapshot_id"),
        "registry": registry,
        "attempts": read_jsonl(architecture_adapter_attempts_v210_path(workspace, codebase_id)),
        "bindings": read_jsonl(architecture_ast_bindings_v210_path(workspace, codebase_id)),
        "definition_lookups": read_jsonl(architecture_definition_lookups_v210_path(workspace, codebase_id)),
        "doc_code_evidence_v3": read_jsonl(architecture_doc_code_evidence_v3_v210_path(workspace, codebase_id)),
        "manifest_candidates": read_jsonl(architecture_manifest_candidates_v210_path(workspace, codebase_id)),
        "runtime_candidates": read_jsonl(architecture_runtime_candidates_v210_path(workspace, codebase_id)),
        "accepted_evidence": read_jsonl(architecture_accepted_pattern_evidence_v210_path(workspace, codebase_id)),
        "blockers": read_jsonl(architecture_pattern_blockers_v210_path(workspace, codebase_id)),
        "summary": {key: value for key, value in summary.items() if key != "report"},
        "report": summary.get("report", {}),
        "artifact_refs": architecture_pattern_evidence_v210_artifact_refs(codebase_id),
    }


def read_architecture_pattern_evidence_v210_view(workspace: Path, codebase_id: str, view_id: str) -> dict[str, Any]:
    payload = read_architecture_pattern_evidence_v210(workspace, codebase_id)
    path = architecture_v210_view_path(workspace, codebase_id, view_id)
    if not path.exists():
        raise FileNotFoundError("REPORT_VIEW_NOT_BUILT")
    return {
        "schema_version": "v2.10",
        "codebase_id": codebase_id,
        "snapshot_id": payload.get("snapshot_id"),
        "view_id": view_id,
        "content_type": "text/html" if view_id.endswith(".html") else "text/mermaid",
        "content": path.read_text(encoding="utf-8"),
        "artifact_refs": architecture_pattern_evidence_v210_artifact_refs(codebase_id),
    }


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
