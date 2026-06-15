"""MCP tools for V2.3 Architecture Abstraction."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from .code_assets.architecture.persistence import architecture_artifact_refs, architecture_code_fact_chain_artifact_refs, architecture_context_pack_optimized_v244_artifact_refs, architecture_context_pack_v2_artifact_refs, architecture_context_pack_v3_artifact_refs, architecture_doc_claim_artifact_refs, architecture_doc_code_alignment_artifact_refs, architecture_doc_quality_artifact_refs, architecture_doc_registry_artifact_refs, architecture_document_semantics_v243_artifact_refs, architecture_graph_v28_artifact_refs, architecture_human_report_v29_artifact_refs, architecture_intent_evidence_artifact_refs, architecture_inventory_artifact_refs, architecture_pattern_evidence_v210_artifact_refs, architecture_public_surface_evidence_v29_artifact_refs, architecture_reading_dashboard_artifact_refs, architecture_reconstructed_artifact_refs, architecture_relationship_chains_v242_artifact_refs, architecture_relationships_v29_artifact_refs, architecture_scale_artifact_refs, architecture_signal_ranking_artifact_refs, architecture_signal_ranking_v29_artifact_refs, architecture_taxonomy_artifact_refs, code_architecture_artifact_refs
from .code_assets.architecture.service import ArchitectureService, public_architecture_code_fact_chain_payload, public_architecture_code_relationships_v2_payload, public_architecture_context_pack_v2_payload, public_architecture_context_pack_v3_payload, public_architecture_document_claims_payload, public_architecture_document_code_alignment_payload, public_architecture_document_quality_payload, public_architecture_document_registry_payload, public_architecture_document_semantics_v3_payload, public_architecture_graph_summary_payload, public_architecture_human_review_report_v2_payload, public_architecture_human_review_report_view_v2_payload, public_architecture_intent_evidence_payload, public_architecture_inventory_list_payload, public_architecture_inventory_payload, public_architecture_optimized_context_pack_v244_payload, public_architecture_pattern_blockers_v2_payload, public_architecture_pattern_evidence_v2_payload, public_architecture_pattern_view_v2_payload, public_architecture_payload, public_architecture_profile_taxonomy_regression_v245_payload, public_architecture_public_surface_evidence_v2_payload, public_architecture_ranking_calibration_v2_payload, public_architecture_reading_payload, public_architecture_reconstructed_payload, public_architecture_relationship_chains_v3_payload, public_architecture_review_queue_payload, public_architecture_scale_profile_payload, public_architecture_signal_ranking_payload, public_architecture_taxonomy_payload, public_code_architecture_payload, public_language_provider_payload, public_workflow_runtime_payload
from .code_assets.envelope import v2_error_envelope, v2_success_envelope


ARCHITECTURE_TOOL_NAMES = {
    "knowledge_architecture_sources_scan",
    "knowledge_architecture_model_build",
    "knowledge_architecture_model_read",
    "knowledge_architecture_alignment",
    "knowledge_architecture_findings",
    "knowledge_architecture_view",
    "knowledge_code_architecture_build",
    "knowledge_code_architecture_roles",
    "knowledge_code_architecture_patterns",
    "knowledge_code_architecture_view",
    "knowledge_code_architecture_scale_build",
    "knowledge_code_architecture_scale_profile",
    "knowledge_code_architecture_scale_readback",
    "knowledge_code_architecture_inventory_build",
    "knowledge_code_architecture_language_facts",
    "knowledge_code_architecture_language_providers_build",
    "knowledge_code_architecture_language_providers",
    "knowledge_code_architecture_workflow_runtime_build",
    "knowledge_code_architecture_workflow_runtime",
    "knowledge_code_architecture_config_inventory",
    "knowledge_code_architecture_deployment_inventory",
    "knowledge_code_architecture_schema_inventory",
    "knowledge_code_architecture_taxonomy_build",
    "knowledge_code_architecture_taxonomy",
    "knowledge_code_architecture_review_queue_build",
    "knowledge_code_architecture_review_queue",
    "knowledge_code_architecture_large_project_views_build",
    "knowledge_code_architecture_large_project_view",
    "knowledge_code_architecture_docs_build",
    "knowledge_code_architecture_docs_list",
    "knowledge_code_architecture_doc_claims_build",
    "knowledge_code_architecture_doc_claims",
    "knowledge_code_architecture_doc_quality_build",
    "knowledge_code_architecture_doc_quality",
    "knowledge_code_architecture_doc_code_alignment_build",
    "knowledge_code_architecture_doc_code_alignment",
    "knowledge_code_architecture_reconstructed_build",
    "knowledge_code_architecture_reconstructed",
    "knowledge_code_architecture_doc_view",
    "knowledge_code_architecture_views_build",
    "knowledge_code_architecture_views",
    "knowledge_code_architecture_view_v2_8",
    "knowledge_code_architecture_graph_summary_build",
    "knowledge_code_architecture_graph_summary",
    "knowledge_code_architecture_graph_view",
    "knowledge_code_architecture_code_fact_chains_build",
    "knowledge_code_architecture_code_fact_chains",
    "knowledge_code_architecture_ranking_build",
    "knowledge_code_architecture_ranking",
    "knowledge_code_architecture_intent_evidence_build",
    "knowledge_code_architecture_intent_evidence",
    "knowledge_code_architecture_context_pack_v2",
    "knowledge_code_architecture_context_pack_read",
    "knowledge_code_architecture_evidence_v2_build",
    "knowledge_code_architecture_evidence_v2",
    "knowledge_code_architecture_relationships_v2_build",
    "knowledge_code_architecture_relationships_v2",
    "knowledge_code_architecture_relationship_chains_v3_build",
    "knowledge_code_architecture_relationship_chains_v3",
    "knowledge_code_architecture_document_semantics_v3_build",
    "knowledge_code_architecture_document_semantics_v3",
    "knowledge_code_architecture_ranking_v2_build",
    "knowledge_code_architecture_ranking_v2",
    "knowledge_code_architecture_human_report_v2_build",
    "knowledge_code_architecture_human_report_v2",
    "knowledge_code_architecture_human_report_v2_view",
    "knowledge_code_architecture_context_pack_v3",
    "knowledge_code_architecture_context_pack_v3_read",
    "knowledge_code_architecture_context_pack_optimized",
    "knowledge_code_architecture_context_pack_optimized_read",
    "knowledge_code_architecture_profile_regression_build",
    "knowledge_code_architecture_profile_regression",
    "knowledge_code_architecture_patterns_v2_build",
    "knowledge_code_architecture_patterns_v2",
    "knowledge_code_architecture_pattern_blockers",
    "knowledge_code_architecture_pattern_view",
}


ARCHITECTURE_TOOL_SPECS = [
    {
        "name": "knowledge_architecture_sources_scan",
        "description": "Scan and build V2.3 architecture source index",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}, "snapshot_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_architecture_model_build",
        "description": "Build a V2.3 Architecture Model from architecture docs, Drawio/Mermaid, and V2.1 code artifacts",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}, "snapshot_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_architecture_model_read",
        "description": "Read the persisted V2.3 Architecture Model",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_architecture_alignment",
        "description": "Read V2.3 design-code alignment",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_architecture_findings",
        "description": "Read V2.3 architecture gap findings",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_architecture_view",
        "description": "Read V2.3 architecture view content",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}, "view_id": {"type": "string", "default": "architecture.html"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_architecture_build",
        "description": "Build V2.4 code-derived architecture roles and layers from accepted code artifacts",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}, "snapshot_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_architecture_roles",
        "description": "Read V2.4 code-derived architecture roles and layers",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_architecture_patterns",
        "description": "Read V2.4 code-derived architecture boundaries and pattern candidates",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_architecture_view",
        "description": "Read V2.4 code-derived architecture HTML or Mermaid view",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}, "view_id": {"type": "string", "default": "code_derived_architecture.html"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_architecture_scale_build",
        "description": "Build V2.39 architecture scale profile for a codebase snapshot",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}, "snapshot_id": {"type": "string"}, "max_files": {"type": "integer"}, "max_loc": {"type": "integer"}, "max_file_size_mb": {"type": "integer"}, "timeout_seconds": {"type": "integer"}, "shard_size": {"type": "integer"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_architecture_scale_profile",
        "description": "Read V2.39 architecture scale profile",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_architecture_scale_readback",
        "description": "Read a V2.39 architecture scale shard page",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}, "shard": {"type": "string", "default": "files"}, "page": {"type": "integer", "default": 1}, "page_size": {"type": "integer", "default": 100}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_architecture_inventory_build",
        "description": "Build V2.6 lightweight language/config/deployment/schema inventory",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}, "snapshot_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_architecture_language_facts",
        "description": "Read V2.6 lightweight TS/JS/Vue language facts",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_architecture_language_providers_build",
        "description": "Build V2.40 language provider symbol and reference facts",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}, "snapshot_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_architecture_language_providers",
        "description": "Read V2.40 language provider status, symbol facts, and reference facts",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_architecture_workflow_runtime_build",
        "description": "Build V2.41 workflow/runtime candidate facts",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}, "snapshot_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_architecture_workflow_runtime",
        "description": "Read V2.41 workflow/runtime candidate facts",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_architecture_relationship_chains_v3_build",
        "description": "Build V2.42 capability-to-implementation relationship chains from evidence-backed facts",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}, "snapshot_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_architecture_relationship_chains_v3",
        "description": "Read V2.42 relationship chains and forbidden edge scan",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_architecture_document_semantics_v3_build",
        "description": "Build V2.43 markdown and drawio document semantic claims and relations",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}, "snapshot_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_architecture_document_semantics_v3",
        "description": "Read V2.43 document semantic claims and relations",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_architecture_config_inventory",
        "description": "Read V2.6 configuration inventory",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_architecture_deployment_inventory",
        "description": "Read V2.6 deployment inventory",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_architecture_schema_inventory",
        "description": "Read V2.6 lightweight schema inventory",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_architecture_taxonomy_build",
        "description": "Build V2.6 architecture taxonomy",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_architecture_taxonomy",
        "description": "Read V2.6 architecture taxonomy",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_architecture_review_queue_build",
        "description": "Build V2.6 architecture review queue",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_architecture_review_queue",
        "description": "Read V2.6 architecture review queue",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_architecture_large_project_views_build",
        "description": "Build V2.6 large-project architecture HTML and Mermaid views",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_architecture_large_project_view",
        "description": "Read a V2.6 large-project architecture view",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}, "view_id": {"type": "string", "default": "architecture_large_project_overview.html"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_architecture_docs_build",
        "description": "Build V2.7 architecture document asset registry",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}, "snapshot_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_architecture_docs_list",
        "description": "Read V2.7 architecture document asset registry",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_architecture_doc_claims_build",
        "description": "Build V2.7 architecture document claims and relations from registered architecture docs",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_architecture_doc_claims",
        "description": "Read V2.7 architecture document claims and relations",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_architecture_doc_quality_build",
        "description": "Build V2.7 architecture document quality findings and summary",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_architecture_doc_quality",
        "description": "Read V2.7 architecture document quality findings and summary",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_architecture_doc_code_alignment_build",
        "description": "Build V2.7 architecture document-code alignment and drift artifacts",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_architecture_doc_code_alignment",
        "description": "Read V2.7 architecture document-code alignment and drift artifacts",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_architecture_reconstructed_build",
        "description": "Build V2.7 target/current/diff reconstructed architecture model and views",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_architecture_reconstructed",
        "description": "Read V2.7 target/current/diff reconstructed architecture model",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_architecture_doc_view",
        "description": "Read V2.7 reconstructed architecture HTML or Mermaid document-code view",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}, "view_id": {"type": "string", "default": "document_code_architecture_report.html"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_architecture_views_build",
        "description": "Build V2.8 human-readable architecture dashboard views from persisted V2.7 artifacts",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_architecture_views",
        "description": "Read the V2.8 architecture reading dashboard summary and chart metadata",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_architecture_view_v2_8",
        "description": "Read a V2.8 architecture reading dashboard HTML or Mermaid view",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}, "view_id": {"type": "string", "default": "architecture_reading_dashboard.html"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_architecture_graph_summary_build",
        "description": "Build V2.8 clustered architecture graph summary and graph views",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_architecture_graph_summary",
        "description": "Read V2.8 clustered architecture graph summary",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_architecture_graph_view",
        "description": "Read a V2.8 deterministic filtered architecture graph view",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}, "view_id": {"type": "string", "default": "system_overview"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_architecture_code_fact_chains_build",
        "description": "Build V2.8 deterministic code fact chains and runtime boundary hints",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_architecture_code_fact_chains",
        "description": "Read V2.8 deterministic code fact chains and runtime boundary hints",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_architecture_ranking_build",
        "description": "Build V2.8 architecture signal ranking and review queue v2",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_architecture_ranking",
        "description": "Read V2.8 architecture signal ranking and review queue v2",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_architecture_intent_evidence_build",
        "description": "Build V2.8 evidence-backed architecture intent states",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_architecture_intent_evidence",
        "description": "Read V2.8 evidence-backed architecture intent states",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_architecture_context_pack_v2",
        "description": "Create a V2.8 architecture context pack from dashboard, graph, ranking, chains, and intent evidence",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}, "mode": {"type": "string", "default": "project_brief"}, "task": {"type": "string"}, "max_tokens": {"type": "integer", "default": 12000}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_architecture_context_pack_read",
        "description": "Read a persisted V2.8 architecture context pack",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}, "pack_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id", "pack_id"]},
    },
    {
        "name": "knowledge_code_architecture_evidence_v2_build",
        "description": "Build V2.9 line-level public surface evidence v2",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}, "snapshot_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_architecture_evidence_v2",
        "description": "Read V2.9 line-level public surface evidence v2",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_architecture_relationships_v2_build",
        "description": "Build V2.9 shallow code relationship layer v2",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_architecture_relationships_v2",
        "description": "Read V2.9 shallow code relationship layer v2",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_architecture_ranking_v2_build",
        "description": "Build V2.9 ranking calibration v2",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_architecture_ranking_v2",
        "description": "Read V2.9 ranking calibration v2",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_architecture_human_report_v2_build",
        "description": "Build V2.9 human architecture review report v2",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_architecture_human_report_v2",
        "description": "Read V2.9 human architecture review report v2",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_architecture_human_report_v2_view",
        "description": "Read a V2.9 human report HTML or Mermaid view",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}, "view_id": {"type": "string", "default": "architecture_human_review_report_v2.html"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_architecture_context_pack_v3",
        "description": "Create a V2.9 Architecture Context Pack v3 from evidence, relationships, ranking, and human report",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}, "mode": {"type": "string", "default": "project_brief"}, "role": {"type": "string", "default": "maintainer"}, "task": {"type": "string"}, "max_tokens": {"type": "integer", "default": 12000}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_architecture_context_pack_v3_read",
        "description": "Read a persisted V2.9 Architecture Context Pack v3",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}, "pack_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id", "pack_id"]},
    },
    {
        "name": "knowledge_code_architecture_context_pack_optimized",
        "description": "Create a V2.44 optimized architecture context pack with token ledger and cache binding",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}, "mode": {"type": "string", "default": "project_brief"}, "role": {"type": "string", "default": "maintainer"}, "task": {"type": "string"}, "max_tokens": {"type": "integer", "default": 4000}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_architecture_context_pack_optimized_read",
        "description": "Read a persisted V2.44 optimized architecture context pack",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}, "pack_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id", "pack_id"]},
    },
    {
        "name": "knowledge_code_architecture_profile_regression_build",
        "description": "Build V2.45 project profile, taxonomy registry, regression matrix, and no-hardcode audit",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}, "snapshot_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_architecture_profile_regression",
        "description": "Read V2.45 project profile, taxonomy registry, regression matrix, and no-hardcode audit",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_architecture_patterns_v2_build",
        "description": "Build V2.10 generic architecture pattern evidence adapters",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}, "snapshot_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_architecture_patterns_v2",
        "description": "Read V2.10 generic architecture pattern evidence",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_architecture_pattern_blockers",
        "description": "Read V2.10 architecture pattern blockers",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_architecture_pattern_view",
        "description": "Read V2.10 architecture pattern HTML or Mermaid view",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}, "view_id": {"type": "string", "default": "pattern_evidence_report.html"}}, "required": ["workspace_id", "codebase_id"]},
    },
]


def handle_architecture_tool(name: str, arguments: dict[str, Any], *, blocked: Callable[..., dict[str, Any]], envelope: Callable[..., dict[str, Any]], ensure_workspace_meta: Callable[..., dict[str, Any]], resolve_workspace: Callable[[str | None, str | None], Path]) -> dict[str, Any]:
    if name not in ARCHITECTURE_TOOL_NAMES:
        raise ValueError(f"Unknown architecture tool: {name}")
    workspace_path = resolve_workspace(arguments.get("workspace_id"), None)
    meta = ensure_workspace_meta(workspace_path)
    workspace_id = str(meta["workspace_id"])
    codebase_id = str(arguments.get("codebase_id") or "").strip()
    if not codebase_id:
        return blocked(workspace_id=workspace_id, message="codebase_id is required", next_actions=["knowledge_codebase_list"], code="invalid_codebase_id")
    service = ArchitectureService(workspace_path, workspace_id=workspace_id)
    snapshot_id = str(arguments.get("snapshot_id") or "").strip() or None
    try:
        if name == "knowledge_code_architecture_build":
            payload = service.build_code_architecture(codebase_id, snapshot_id=snapshot_id)
            data = {"code_architecture": {"summary": payload["summary"]}}
            refs = code_architecture_artifact_refs(codebase_id)
            return envelope(workspace_id=workspace_id, artifact_refs=refs, next_actions=["knowledge_code_architecture_roles"], data=_with_v2(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=str(payload["snapshot_id"]), data=data, artifact_refs=refs))
        if name == "knowledge_code_architecture_roles":
            payload = public_code_architecture_payload(service.read_code_architecture(codebase_id))
            refs = code_architecture_artifact_refs(codebase_id)
            data = {"code_architecture": payload}
            return envelope(workspace_id=workspace_id, artifact_refs=refs, data=_with_v2(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=str(payload.get("snapshot_id") or ""), data=data, artifact_refs=refs))
        if name == "knowledge_code_architecture_patterns":
            payload = public_code_architecture_payload(service.read_code_architecture(codebase_id))
            refs = code_architecture_artifact_refs(codebase_id)
            data = {"patterns": payload.get("patterns", []), "boundaries": payload.get("boundaries", []), "summary": payload.get("summary", {})}
            return envelope(workspace_id=workspace_id, artifact_refs=refs, data=_with_v2(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=str(payload.get("snapshot_id") or ""), data=data, artifact_refs=refs))
        if name == "knowledge_code_architecture_view":
            view = service.read_code_view(codebase_id, str(arguments.get("view_id") or "code_derived_architecture.html"))
            refs = code_architecture_artifact_refs(codebase_id)
            data = {"view": view}
            return envelope(workspace_id=workspace_id, artifact_refs=refs, data=_with_v2(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=str(view["snapshot_id"]), data=data, artifact_refs=refs))
        if name == "knowledge_code_architecture_scale_build":
            profile = service.build_scale_profile(codebase_id, snapshot_id=snapshot_id, budget=_scale_budget_from_arguments(arguments))
            refs = architecture_scale_artifact_refs(codebase_id)
            data = {"scale_profile": public_architecture_scale_profile_payload(profile)}
            return envelope(workspace_id=workspace_id, artifact_refs=refs, next_actions=["knowledge_code_architecture_scale_profile"], data=_with_v2(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=str(profile["snapshot_id"]), data=data, artifact_refs=refs))
        if name == "knowledge_code_architecture_scale_profile":
            profile = service.read_scale_profile(codebase_id)
            refs = architecture_scale_artifact_refs(codebase_id)
            data = {"scale_profile": public_architecture_scale_profile_payload(profile)}
            return envelope(workspace_id=workspace_id, artifact_refs=refs, data=_with_v2(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=str(profile.get("snapshot_id") or ""), data=data, artifact_refs=refs))
        if name == "knowledge_code_architecture_scale_readback":
            payload = service.read_scale_shard(codebase_id, shard=str(arguments.get("shard") or "files"), page=int(arguments.get("page") or 1), page_size=int(arguments.get("page_size") or 100))
            refs = architecture_scale_artifact_refs(codebase_id)
            data = {"scale_readback": payload}
            return envelope(workspace_id=workspace_id, artifact_refs=refs, data=_with_v2(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=str(payload.get("snapshot_id") or ""), data=data, artifact_refs=refs))
        if name == "knowledge_code_architecture_inventory_build":
            payload = service.build_inventory(codebase_id, snapshot_id=snapshot_id)
            refs = architecture_inventory_artifact_refs(codebase_id)
            data = {"architecture_inventory": public_architecture_inventory_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=refs, next_actions=["knowledge_code_architecture_config_inventory", "knowledge_code_architecture_deployment_inventory", "knowledge_code_architecture_schema_inventory"], data=_with_v2(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=str(payload.get("snapshot_id") or ""), data=data, artifact_refs=refs))
        if name in {"knowledge_code_architecture_language_facts", "knowledge_code_architecture_config_inventory", "knowledge_code_architecture_deployment_inventory", "knowledge_code_architecture_schema_inventory"}:
            if name == "knowledge_code_architecture_language_facts":
                items = service.read_language_facts(codebase_id)
                payload_key, item_key = "language_facts", "fact_type"
            elif name == "knowledge_code_architecture_config_inventory":
                items = service.read_config_inventory(codebase_id)
                payload_key, item_key = "config_inventory", "item_type"
            elif name == "knowledge_code_architecture_deployment_inventory":
                items = service.read_deployment_inventory(codebase_id)
                payload_key, item_key = "deployment_inventory", "deployment_type"
            else:
                items = service.read_schema_inventory(codebase_id)
                payload_key, item_key = "schema_inventory", "schema_type"
            refs = architecture_inventory_artifact_refs(codebase_id)
            data = public_architecture_inventory_list_payload(items, payload_key=payload_key, item_key=item_key, codebase_id=codebase_id)
            snapshot = str(items[0].get("snapshot_id") or "") if items else ""
            return envelope(workspace_id=workspace_id, artifact_refs=refs, data=_with_v2(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot, data=data, artifact_refs=refs))
        if name == "knowledge_code_architecture_language_providers_build":
            payload = service.build_language_provider_facts(codebase_id, snapshot_id=snapshot_id)
            refs = payload.get("artifact_refs", [])
            data = {"language_providers": public_language_provider_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=refs, next_actions=["knowledge_code_architecture_language_providers"], data=_with_v2(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=str(payload.get("snapshot_id") or ""), data=data, artifact_refs=refs))
        if name == "knowledge_code_architecture_language_providers":
            payload = service.read_language_provider_facts(codebase_id)
            refs = payload.get("artifact_refs", [])
            data = {"language_providers": public_language_provider_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=refs, data=_with_v2(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=str(payload.get("snapshot_id") or ""), data=data, artifact_refs=refs))
        if name == "knowledge_code_architecture_workflow_runtime_build":
            payload = service.build_workflow_runtime_candidates(codebase_id, snapshot_id=snapshot_id)
            refs = payload.get("artifact_refs", [])
            data = {"workflow_runtime": public_workflow_runtime_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=refs, next_actions=["knowledge_code_architecture_workflow_runtime"], data=_with_v2(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=str(payload.get("snapshot_id") or ""), data=data, artifact_refs=refs))
        if name == "knowledge_code_architecture_workflow_runtime":
            payload = service.read_workflow_runtime_candidates(codebase_id)
            refs = payload.get("artifact_refs", [])
            data = {"workflow_runtime": public_workflow_runtime_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=refs, data=_with_v2(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=str(payload.get("snapshot_id") or ""), data=data, artifact_refs=refs))
        if name == "knowledge_code_architecture_relationship_chains_v3_build":
            payload = service.build_relationship_chains_v3(codebase_id, snapshot_id=snapshot_id)
            refs = architecture_relationship_chains_v242_artifact_refs(codebase_id)
            data = {"relationship_chains_v3": public_architecture_relationship_chains_v3_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=refs, next_actions=["knowledge_code_architecture_relationship_chains_v3"], data=_with_v2(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=str(payload.get("snapshot_id") or ""), data=data, artifact_refs=refs))
        if name == "knowledge_code_architecture_relationship_chains_v3":
            payload = service.read_relationship_chains_v3(codebase_id)
            refs = architecture_relationship_chains_v242_artifact_refs(codebase_id)
            data = {"relationship_chains_v3": public_architecture_relationship_chains_v3_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=refs, data=_with_v2(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=str(payload.get("snapshot_id") or ""), data=data, artifact_refs=refs))
        if name == "knowledge_code_architecture_document_semantics_v3_build":
            payload = service.build_document_semantics_v3(codebase_id, snapshot_id=snapshot_id)
            refs = architecture_document_semantics_v243_artifact_refs(codebase_id)
            data = {"document_semantics_v3": public_architecture_document_semantics_v3_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=refs, next_actions=["knowledge_code_architecture_document_semantics_v3"], data=_with_v2(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=str(payload.get("snapshot_id") or ""), data=data, artifact_refs=refs))
        if name == "knowledge_code_architecture_document_semantics_v3":
            payload = service.read_document_semantics_v3(codebase_id)
            refs = architecture_document_semantics_v243_artifact_refs(codebase_id)
            data = {"document_semantics_v3": public_architecture_document_semantics_v3_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=refs, data=_with_v2(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=str(payload.get("snapshot_id") or ""), data=data, artifact_refs=refs))
        if name == "knowledge_code_architecture_taxonomy_build":
            taxonomy = service.build_taxonomy(codebase_id)
            refs = architecture_taxonomy_artifact_refs(codebase_id)
            data = {"taxonomy": public_architecture_taxonomy_payload(taxonomy)}
            return envelope(workspace_id=workspace_id, artifact_refs=refs, next_actions=["knowledge_code_architecture_review_queue_build"], data=_with_v2(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=None, data=data, artifact_refs=refs))
        if name == "knowledge_code_architecture_taxonomy":
            taxonomy = service.read_taxonomy(codebase_id)
            refs = architecture_taxonomy_artifact_refs(codebase_id)
            data = {"taxonomy": public_architecture_taxonomy_payload(taxonomy)}
            return envelope(workspace_id=workspace_id, artifact_refs=refs, data=_with_v2(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=None, data=data, artifact_refs=refs))
        if name == "knowledge_code_architecture_review_queue_build":
            payload = service.build_review_queue(codebase_id)
            refs = architecture_taxonomy_artifact_refs(codebase_id)
            data = {"review_queue": public_architecture_review_queue_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=refs, next_actions=["knowledge_code_architecture_review_queue"], data=_with_v2(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=str(payload.get("snapshot_id") or ""), data=data, artifact_refs=refs))
        if name == "knowledge_code_architecture_review_queue":
            payload = service.read_review_queue(codebase_id)
            refs = architecture_taxonomy_artifact_refs(codebase_id)
            data = {"review_queue": public_architecture_review_queue_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=refs, data=_with_v2(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=str(payload.get("snapshot_id") or ""), data=data, artifact_refs=refs))
        if name == "knowledge_code_architecture_large_project_views_build":
            payload = service.build_large_project_views(codebase_id)
            refs = payload.get("artifact_refs", [])
            data = {"views": payload}
            return envelope(workspace_id=workspace_id, artifact_refs=refs, next_actions=["knowledge_code_architecture_large_project_view"], data=_with_v2(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=str(payload.get("snapshot_id") or ""), data=data, artifact_refs=refs))
        if name == "knowledge_code_architecture_large_project_view":
            view = service.read_large_project_view(codebase_id, str(arguments.get("view_id") or "architecture_large_project_overview.html"))
            refs = view.get("artifact_refs", [])
            data = {"view": view}
            return envelope(workspace_id=workspace_id, artifact_refs=refs, data=_with_v2(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=str(view.get("snapshot_id") or ""), data=data, artifact_refs=refs))
        if name == "knowledge_code_architecture_docs_build":
            payload = service.build_document_registry(codebase_id, snapshot_id=snapshot_id)
            refs = architecture_doc_registry_artifact_refs(codebase_id)
            data = {"document_registry": public_architecture_document_registry_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=refs, next_actions=["knowledge_code_architecture_docs_list"], data=_with_v2(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=str(payload.get("snapshot_id") or ""), data=data, artifact_refs=refs))
        if name == "knowledge_code_architecture_docs_list":
            payload = service.read_document_registry(codebase_id)
            refs = architecture_doc_registry_artifact_refs(codebase_id)
            data = {"document_registry": public_architecture_document_registry_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=refs, data=_with_v2(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=str(payload.get("snapshot_id") or ""), data=data, artifact_refs=refs))
        if name == "knowledge_code_architecture_doc_claims_build":
            payload = service.build_document_claims(codebase_id)
            refs = architecture_doc_claim_artifact_refs(codebase_id)
            data = {"document_claims": public_architecture_document_claims_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=refs, next_actions=["knowledge_code_architecture_doc_claims"], data=_with_v2(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=str(payload.get("snapshot_id") or ""), data=data, artifact_refs=refs))
        if name == "knowledge_code_architecture_doc_claims":
            payload = service.read_document_claims(codebase_id)
            refs = architecture_doc_claim_artifact_refs(codebase_id)
            data = {"document_claims": public_architecture_document_claims_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=refs, data=_with_v2(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=str(payload.get("snapshot_id") or ""), data=data, artifact_refs=refs))
        if name == "knowledge_code_architecture_doc_quality_build":
            payload = service.build_document_quality(codebase_id)
            refs = architecture_doc_quality_artifact_refs(codebase_id)
            data = {"document_quality": public_architecture_document_quality_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=refs, next_actions=["knowledge_code_architecture_doc_quality"], data=_with_v2(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=str(payload.get("snapshot_id") or ""), data=data, artifact_refs=refs))
        if name == "knowledge_code_architecture_doc_quality":
            payload = service.read_document_quality(codebase_id)
            refs = architecture_doc_quality_artifact_refs(codebase_id)
            data = {"document_quality": public_architecture_document_quality_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=refs, data=_with_v2(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=str(payload.get("snapshot_id") or ""), data=data, artifact_refs=refs))
        if name == "knowledge_code_architecture_doc_code_alignment_build":
            payload = service.build_document_code_alignment(codebase_id)
            refs = architecture_doc_code_alignment_artifact_refs(codebase_id)
            data = {"document_code_alignment": public_architecture_document_code_alignment_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=refs, next_actions=["knowledge_code_architecture_doc_code_alignment"], data=_with_v2(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=str(payload.get("snapshot_id") or ""), data=data, artifact_refs=refs))
        if name == "knowledge_code_architecture_doc_code_alignment":
            payload = service.read_document_code_alignment(codebase_id)
            refs = architecture_doc_code_alignment_artifact_refs(codebase_id)
            data = {"document_code_alignment": public_architecture_document_code_alignment_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=refs, data=_with_v2(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=str(payload.get("snapshot_id") or ""), data=data, artifact_refs=refs))
        if name == "knowledge_code_architecture_reconstructed_build":
            payload = service.build_reconstructed_architecture(codebase_id)
            refs = architecture_reconstructed_artifact_refs(codebase_id)
            data = {"reconstructed_architecture": public_architecture_reconstructed_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=refs, next_actions=["knowledge_code_architecture_reconstructed", "knowledge_code_architecture_doc_view"], data=_with_v2(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=str(payload.get("snapshot_id") or ""), data=data, artifact_refs=refs))
        if name == "knowledge_code_architecture_reconstructed":
            payload = service.read_reconstructed_architecture(codebase_id)
            refs = architecture_reconstructed_artifact_refs(codebase_id)
            data = {"reconstructed_architecture": public_architecture_reconstructed_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=refs, data=_with_v2(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=str(payload.get("snapshot_id") or ""), data=data, artifact_refs=refs))
        if name == "knowledge_code_architecture_doc_view":
            view = service.read_document_architecture_view(codebase_id, str(arguments.get("view_id") or "document_code_architecture_report.html"))
            refs = architecture_reconstructed_artifact_refs(codebase_id)
            data = {"view": view}
            return envelope(workspace_id=workspace_id, artifact_refs=refs, data=_with_v2(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=str(view.get("snapshot_id") or ""), data=data, artifact_refs=refs))
        if name == "knowledge_code_architecture_views_build":
            payload = service.build_architecture_reading_dashboard(codebase_id)
            refs = architecture_reading_dashboard_artifact_refs(codebase_id)
            data = {"reading_dashboard": public_architecture_reading_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=refs, next_actions=["knowledge_code_architecture_views"], data=_with_v2(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=str(payload.get("snapshot_id") or ""), data=data, artifact_refs=refs))
        if name == "knowledge_code_architecture_views":
            payload = service.read_architecture_reading_dashboard(codebase_id)
            refs = architecture_reading_dashboard_artifact_refs(codebase_id)
            data = {"reading_dashboard": public_architecture_reading_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=refs, data=_with_v2(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=str(payload.get("snapshot_id") or ""), data=data, artifact_refs=refs))
        if name == "knowledge_code_architecture_view_v2_8":
            view = service.read_architecture_reading_view(codebase_id, str(arguments.get("view_id") or "architecture_reading_dashboard.html"))
            refs = architecture_reading_dashboard_artifact_refs(codebase_id)
            data = {"view": view}
            return envelope(workspace_id=workspace_id, artifact_refs=refs, data=_with_v2(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=str(view.get("snapshot_id") or ""), data=data, artifact_refs=refs))
        if name == "knowledge_code_architecture_graph_summary_build":
            payload = service.build_architecture_graph_summary(codebase_id)
            refs = architecture_graph_v28_artifact_refs(codebase_id)
            data = {"graph_summary": public_architecture_graph_summary_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=refs, next_actions=["knowledge_code_architecture_graph_summary"], data=_with_v2(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=str(payload.get("summary", {}).get("snapshot_id") or ""), data=data, artifact_refs=refs))
        if name == "knowledge_code_architecture_graph_summary":
            payload = service.read_architecture_graph_summary(codebase_id)
            refs = architecture_graph_v28_artifact_refs(codebase_id)
            data = {"graph_summary": public_architecture_graph_summary_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=refs, data=_with_v2(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=str(payload.get("summary", {}).get("snapshot_id") or ""), data=data, artifact_refs=refs))
        if name == "knowledge_code_architecture_graph_view":
            view = service.read_architecture_graph_view(codebase_id, str(arguments.get("view_id") or "system_overview"))
            refs = architecture_graph_v28_artifact_refs(codebase_id)
            data = {"graph_view": view}
            return envelope(workspace_id=workspace_id, artifact_refs=refs, data=_with_v2(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=str(view.get("snapshot_id") or ""), data=data, artifact_refs=refs))
        if name == "knowledge_code_architecture_code_fact_chains_build":
            payload = service.build_code_fact_chains(codebase_id)
            refs = architecture_code_fact_chain_artifact_refs(codebase_id)
            data = {"code_fact_chains": public_architecture_code_fact_chain_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=refs, next_actions=["knowledge_code_architecture_code_fact_chains"], data=_with_v2(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=str(payload.get("summary", {}).get("snapshot_id") or ""), data=data, artifact_refs=refs))
        if name == "knowledge_code_architecture_code_fact_chains":
            payload = service.read_code_fact_chains(codebase_id)
            refs = architecture_code_fact_chain_artifact_refs(codebase_id)
            data = {"code_fact_chains": public_architecture_code_fact_chain_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=refs, data=_with_v2(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=str(payload.get("summary", {}).get("snapshot_id") or ""), data=data, artifact_refs=refs))
        if name == "knowledge_code_architecture_ranking_build":
            payload = service.build_signal_ranking(codebase_id)
            refs = architecture_signal_ranking_artifact_refs(codebase_id)
            data = {"signal_ranking": public_architecture_signal_ranking_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=refs, next_actions=["knowledge_code_architecture_ranking"], data=_with_v2(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=str(payload.get("ranking", {}).get("snapshot_id") or ""), data=data, artifact_refs=refs))
        if name == "knowledge_code_architecture_ranking":
            payload = service.read_signal_ranking(codebase_id)
            refs = architecture_signal_ranking_artifact_refs(codebase_id)
            data = {"signal_ranking": public_architecture_signal_ranking_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=refs, data=_with_v2(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=str(payload.get("ranking", {}).get("snapshot_id") or ""), data=data, artifact_refs=refs))
        if name == "knowledge_code_architecture_intent_evidence_build":
            payload = service.build_intent_evidence(codebase_id)
            refs = architecture_intent_evidence_artifact_refs(codebase_id)
            data = {"intent_evidence": public_architecture_intent_evidence_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=refs, next_actions=["knowledge_code_architecture_intent_evidence"], data=_with_v2(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=str(payload.get("summary", {}).get("snapshot_id") or ""), data=data, artifact_refs=refs))
        if name == "knowledge_code_architecture_intent_evidence":
            payload = service.read_intent_evidence(codebase_id)
            refs = architecture_intent_evidence_artifact_refs(codebase_id)
            data = {"intent_evidence": public_architecture_intent_evidence_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=refs, data=_with_v2(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=str(payload.get("summary", {}).get("snapshot_id") or ""), data=data, artifact_refs=refs))
        if name == "knowledge_code_architecture_context_pack_v2":
            pack = service.create_architecture_context_pack_v2(codebase_id, mode=str(arguments.get("mode") or "project_brief"), task=arguments.get("task"), max_tokens=int(arguments.get("max_tokens") or 12000))
            refs = architecture_context_pack_v2_artifact_refs(codebase_id, str(pack.get("pack_id") or ""))
            data = {"architecture_context_pack": public_architecture_context_pack_v2_payload(pack)}
            return envelope(workspace_id=workspace_id, artifact_refs=refs, next_actions=["knowledge_code_architecture_context_pack_read"], data=_with_v2(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=str(pack.get("snapshot_id") or ""), data=data, artifact_refs=refs))
        if name == "knowledge_code_architecture_context_pack_read":
            pack_id = str(arguments.get("pack_id") or "").strip()
            if not pack_id:
                return blocked(workspace_id=workspace_id, message="pack_id is required", next_actions=["knowledge_code_architecture_context_pack_v2"], code="invalid_pack_id")
            pack = service.read_architecture_context_pack_v2(codebase_id, pack_id)
            refs = architecture_context_pack_v2_artifact_refs(codebase_id, pack_id)
            data = {"architecture_context_pack": public_architecture_context_pack_v2_payload(pack)}
            return envelope(workspace_id=workspace_id, artifact_refs=refs, data=_with_v2(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=str(pack.get("snapshot_id") or ""), data=data, artifact_refs=refs))
        if name == "knowledge_code_architecture_evidence_v2_build":
            payload = service.build_public_surface_evidence_v2(codebase_id, snapshot_id=snapshot_id)
            refs = architecture_public_surface_evidence_v29_artifact_refs(codebase_id)
            data = {"public_surface_evidence_v2": public_architecture_public_surface_evidence_v2_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=refs, next_actions=["knowledge_code_architecture_evidence_v2"], data=_with_v2(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=str(payload.get("snapshot_id") or ""), data=data, artifact_refs=refs))
        if name == "knowledge_code_architecture_evidence_v2":
            payload = service.read_public_surface_evidence_v2(codebase_id)
            refs = architecture_public_surface_evidence_v29_artifact_refs(codebase_id)
            data = {"public_surface_evidence_v2": public_architecture_public_surface_evidence_v2_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=refs, data=_with_v2(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=str(payload.get("snapshot_id") or ""), data=data, artifact_refs=refs))
        if name == "knowledge_code_architecture_relationships_v2_build":
            payload = service.build_code_relationships_v2(codebase_id)
            refs = architecture_relationships_v29_artifact_refs(codebase_id)
            data = {"code_relationships_v2": public_architecture_code_relationships_v2_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=refs, next_actions=["knowledge_code_architecture_relationships_v2"], data=_with_v2(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=str(payload.get("snapshot_id") or ""), data=data, artifact_refs=refs))
        if name == "knowledge_code_architecture_relationships_v2":
            payload = service.read_code_relationships_v2(codebase_id)
            refs = architecture_relationships_v29_artifact_refs(codebase_id)
            data = {"code_relationships_v2": public_architecture_code_relationships_v2_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=refs, data=_with_v2(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=str(payload.get("snapshot_id") or ""), data=data, artifact_refs=refs))
        if name == "knowledge_code_architecture_ranking_v2_build":
            payload = service.build_ranking_calibration_v2(codebase_id)
            refs = architecture_signal_ranking_v29_artifact_refs(codebase_id)
            data = {"ranking_calibration_v2": public_architecture_ranking_calibration_v2_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=refs, next_actions=["knowledge_code_architecture_ranking_v2"], data=_with_v2(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=str(payload.get("ranking", {}).get("snapshot_id") or ""), data=data, artifact_refs=refs))
        if name == "knowledge_code_architecture_ranking_v2":
            payload = service.read_ranking_calibration_v2(codebase_id)
            refs = architecture_signal_ranking_v29_artifact_refs(codebase_id)
            data = {"ranking_calibration_v2": public_architecture_ranking_calibration_v2_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=refs, data=_with_v2(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=str(payload.get("ranking", {}).get("snapshot_id") or ""), data=data, artifact_refs=refs))
        if name == "knowledge_code_architecture_human_report_v2_build":
            payload = service.build_human_review_report_v2(codebase_id)
            refs = architecture_human_report_v29_artifact_refs(codebase_id)
            data = {"human_review_report_v2": public_architecture_human_review_report_v2_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=refs, next_actions=["knowledge_code_architecture_human_report_v2"], data=_with_v2(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=str(payload.get("report", {}).get("snapshot_id") or ""), data=data, artifact_refs=refs))
        if name == "knowledge_code_architecture_human_report_v2":
            payload = service.read_human_review_report_v2(codebase_id)
            refs = architecture_human_report_v29_artifact_refs(codebase_id)
            data = {"human_review_report_v2": public_architecture_human_review_report_v2_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=refs, data=_with_v2(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=str(payload.get("report", {}).get("snapshot_id") or ""), data=data, artifact_refs=refs))
        if name == "knowledge_code_architecture_human_report_v2_view":
            view = service.read_human_review_report_view_v2(codebase_id, str(arguments.get("view_id") or "architecture_human_review_report_v2.html"))
            refs = architecture_human_report_v29_artifact_refs(codebase_id)
            data = {"view": public_architecture_human_review_report_view_v2_payload(view)}
            return envelope(workspace_id=workspace_id, artifact_refs=refs, data=_with_v2(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=str(view.get("snapshot_id") or ""), data=data, artifact_refs=refs))
        if name == "knowledge_code_architecture_context_pack_v3":
            pack = service.create_architecture_context_pack_v3(codebase_id, mode=str(arguments.get("mode") or "project_brief"), role=str(arguments.get("role") or "maintainer"), task=arguments.get("task"), max_tokens=int(arguments.get("max_tokens") or 12000))
            refs = architecture_context_pack_v3_artifact_refs(codebase_id, str(pack.get("pack_id") or ""))
            data = {"architecture_context_pack_v3": public_architecture_context_pack_v3_payload(pack)}
            return envelope(workspace_id=workspace_id, artifact_refs=refs, next_actions=["knowledge_code_architecture_context_pack_v3_read"], data=_with_v2(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=str(pack.get("snapshot_id") or ""), data=data, artifact_refs=refs))
        if name == "knowledge_code_architecture_context_pack_v3_read":
            pack_id = str(arguments.get("pack_id") or "").strip()
            if not pack_id:
                return blocked(workspace_id=workspace_id, message="pack_id is required", next_actions=["knowledge_code_architecture_context_pack_v3"], code="invalid_pack_id")
            pack = service.read_architecture_context_pack_v3(codebase_id, pack_id)
            refs = architecture_context_pack_v3_artifact_refs(codebase_id, pack_id)
            data = {"architecture_context_pack_v3": public_architecture_context_pack_v3_payload(pack)}
            return envelope(workspace_id=workspace_id, artifact_refs=refs, data=_with_v2(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=str(pack.get("snapshot_id") or ""), data=data, artifact_refs=refs))
        if name == "knowledge_code_architecture_context_pack_optimized":
            pack = service.create_optimized_context_pack_v244(codebase_id, mode=str(arguments.get("mode") or "project_brief"), role=str(arguments.get("role") or "maintainer"), task=arguments.get("task"), max_tokens=int(arguments.get("max_tokens") or 4000))
            refs = architecture_context_pack_optimized_v244_artifact_refs(codebase_id, str(pack.get("pack_id") or ""))
            data = {"architecture_context_pack_optimized": public_architecture_optimized_context_pack_v244_payload(pack)}
            return envelope(workspace_id=workspace_id, artifact_refs=refs, next_actions=["knowledge_code_architecture_context_pack_optimized_read"], data=_with_v2(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=str(pack.get("snapshot_id") or ""), data=data, artifact_refs=refs))
        if name == "knowledge_code_architecture_context_pack_optimized_read":
            pack_id = str(arguments.get("pack_id") or "").strip()
            if not pack_id:
                return blocked(workspace_id=workspace_id, message="pack_id is required", next_actions=["knowledge_code_architecture_context_pack_optimized"], code="invalid_pack_id")
            pack = service.read_optimized_context_pack_v244(codebase_id, pack_id)
            refs = architecture_context_pack_optimized_v244_artifact_refs(codebase_id, pack_id)
            data = {"architecture_context_pack_optimized": public_architecture_optimized_context_pack_v244_payload(pack)}
            return envelope(workspace_id=workspace_id, artifact_refs=refs, data=_with_v2(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=str(pack.get("snapshot_id") or ""), data=data, artifact_refs=refs))
        if name == "knowledge_code_architecture_profile_regression_build":
            payload = service.build_profile_taxonomy_regression_v245(codebase_id, snapshot_id=snapshot_id)
            refs = payload.get("artifact_refs") or []
            data = {"profile_taxonomy_regression": public_architecture_profile_taxonomy_regression_v245_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=refs, next_actions=["knowledge_code_architecture_profile_regression"], data=_with_v2(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=str(payload.get("snapshot_id") or ""), data=data, artifact_refs=refs))
        if name == "knowledge_code_architecture_profile_regression":
            payload = service.read_profile_taxonomy_regression_v245(codebase_id)
            refs = payload.get("artifact_refs") or []
            data = {"profile_taxonomy_regression": public_architecture_profile_taxonomy_regression_v245_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=refs, data=_with_v2(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=str(payload.get("snapshot_id") or ""), data=data, artifact_refs=refs))
        if name == "knowledge_code_architecture_patterns_v2_build":
            payload = service.build_pattern_evidence_v2(codebase_id, snapshot_id=snapshot_id)
            refs = architecture_pattern_evidence_v210_artifact_refs(codebase_id)
            data = {"pattern_evidence_v2": public_architecture_pattern_evidence_v2_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=refs, next_actions=["knowledge_code_architecture_patterns_v2"], data=_with_v2(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=str(payload.get("snapshot_id") or ""), data=data, artifact_refs=refs))
        if name == "knowledge_code_architecture_patterns_v2":
            payload = service.read_pattern_evidence_v2(codebase_id)
            refs = architecture_pattern_evidence_v210_artifact_refs(codebase_id)
            data = {"pattern_evidence_v2": public_architecture_pattern_evidence_v2_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=refs, data=_with_v2(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=str(payload.get("snapshot_id") or ""), data=data, artifact_refs=refs))
        if name == "knowledge_code_architecture_pattern_blockers":
            payload = service.read_pattern_evidence_v2(codebase_id)
            refs = architecture_pattern_evidence_v210_artifact_refs(codebase_id)
            data = {"pattern_blockers": public_architecture_pattern_blockers_v2_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=refs, data=_with_v2(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=str(payload.get("snapshot_id") or ""), data=data, artifact_refs=refs))
        if name == "knowledge_code_architecture_pattern_view":
            view = service.read_pattern_evidence_view_v2(codebase_id, str(arguments.get("view_id") or "pattern_evidence_report.html"))
            refs = architecture_pattern_evidence_v210_artifact_refs(codebase_id)
            data = {"view": public_architecture_pattern_view_v2_payload(view)}
            return envelope(workspace_id=workspace_id, artifact_refs=refs, data=_with_v2(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=str(view.get("snapshot_id") or ""), data=data, artifact_refs=refs))
        if name in {"knowledge_architecture_model_build", "knowledge_architecture_sources_scan"}:
            bundle = service.build_architecture(codebase_id, snapshot_id=snapshot_id)
            data = {"architecture": {"summary": bundle["summary"]}}
            return envelope(workspace_id=workspace_id, artifact_refs=architecture_artifact_refs(codebase_id), next_actions=["knowledge_architecture_model_read", "knowledge_architecture_findings"], data=_with_v2(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=str(bundle["summary"]["snapshot_id"]), data=data, artifact_refs=architecture_artifact_refs(codebase_id)))
        if name == "knowledge_architecture_view":
            view = service.read_view(codebase_id, str(arguments.get("view_id") or "architecture.html"))
            data = {"view": view}
            return envelope(workspace_id=workspace_id, artifact_refs=architecture_artifact_refs(codebase_id), data=_with_v2(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=str(view["snapshot_id"]), data=data, artifact_refs=architecture_artifact_refs(codebase_id)))
        bundle = service.read_architecture(codebase_id)
        payload = public_architecture_payload(bundle)
        data = {"architecture": payload}
        if name == "knowledge_architecture_alignment":
            data = {"alignment": payload["alignment"]}
        if name == "knowledge_architecture_findings":
            data = {"findings": payload["findings"], "summary": payload["summary"]}
        return envelope(workspace_id=workspace_id, artifact_refs=architecture_artifact_refs(codebase_id), data=_with_v2(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=str(bundle["model"]["snapshot_id"]), data=data, artifact_refs=architecture_artifact_refs(codebase_id)))
    except FileNotFoundError as exc:
        return _blocked_v2(envelope, workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, code=_architecture_error_code(str(exc)), message=_architecture_error_message(str(exc)), next_actions=["knowledge_codebase_snapshot", "knowledge_code_graph_build", "knowledge_architecture_model_build"])
    except ValueError as exc:
        return _blocked_v2(envelope, workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, code=str(exc), message=str(exc), next_actions=["knowledge_architecture_model_build"])


def _with_v2(*, workspace_id: str, data: dict[str, Any], codebase_id: str, snapshot_id: str | None, artifact_refs: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    payload = dict(data)
    payload["v2"] = v2_success_envelope(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, data=data, artifact_refs=artifact_refs)
    return payload


def _blocked_v2(envelope: Callable[..., dict[str, Any]], *, workspace_id: str, codebase_id: str, snapshot_id: str | None, code: str, message: str, next_actions: list[str] | None = None) -> dict[str, Any]:
    return envelope(workspace_id=workspace_id, status="blocked", warnings=[message], next_actions=next_actions, data={"error": {"code": code, "message": message, "retryable": False}, "v2": v2_error_envelope(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, code=code, message=message, next_actions=next_actions)})


def _architecture_error_code(error: str) -> str:
    if "ARCHITECTURE_SOURCE_NOT_FOUND" in error:
        return "ARCHITECTURE_SOURCE_NOT_FOUND"
    if "ARCHITECTURE_MODEL_NOT_BUILT" in error:
        return "ARCHITECTURE_MODEL_NOT_BUILT"
    if "CODE_ARCHITECTURE_NOT_BUILT" in error:
        return "CODE_ARCHITECTURE_NOT_BUILT"
    if "ARCHITECTURE_SCALE_PROFILE_NOT_BUILT" in error:
        return "ARCHITECTURE_SCALE_PROFILE_NOT_BUILT"
    if "SHARD_NOT_FOUND" in error:
        return "ARCHITECTURE_SCALE_SHARD_NOT_FOUND"
    if "ARCHITECTURE_INVENTORY_NOT_BUILT" in error:
        return "ARCHITECTURE_INVENTORY_NOT_BUILT"
    if "ARCHITECTURE_LANGUAGE_FACTS_NOT_BUILT" in error:
        return "ARCHITECTURE_LANGUAGE_FACTS_NOT_BUILT"
    if "ARCHITECTURE_LANGUAGE_PROVIDERS_NOT_BUILT" in error:
        return "ARCHITECTURE_LANGUAGE_PROVIDERS_NOT_BUILT"
    if "ARCHITECTURE_WORKFLOW_RUNTIME_NOT_BUILT" in error:
        return "ARCHITECTURE_WORKFLOW_RUNTIME_NOT_BUILT"
    if "ARCHITECTURE_CONFIG_INVENTORY_NOT_BUILT" in error:
        return "ARCHITECTURE_CONFIG_INVENTORY_NOT_BUILT"
    if "ARCHITECTURE_DEPLOYMENT_INVENTORY_NOT_BUILT" in error:
        return "ARCHITECTURE_DEPLOYMENT_INVENTORY_NOT_BUILT"
    if "ARCHITECTURE_SCHEMA_INVENTORY_NOT_BUILT" in error:
        return "ARCHITECTURE_SCHEMA_INVENTORY_NOT_BUILT"
    if "ARCHITECTURE_TAXONOMY_NOT_BUILT" in error:
        return "ARCHITECTURE_TAXONOMY_NOT_BUILT"
    if "ARCHITECTURE_REVIEW_QUEUE_NOT_BUILT" in error:
        return "ARCHITECTURE_REVIEW_QUEUE_NOT_BUILT"
    if "ARCHITECTURE_DOCS_NOT_BUILT" in error:
        return "ARCHITECTURE_DOCS_NOT_BUILT"
    if "ARCHITECTURE_DOC_CLAIMS_NOT_BUILT" in error:
        return "ARCHITECTURE_DOC_CLAIMS_NOT_BUILT"
    if "ARCHITECTURE_DOC_CLAIMS_NOT_FOUND" in error:
        return "ARCHITECTURE_DOC_CLAIMS_NOT_FOUND"
    if "ARCHITECTURE_DOC_QUALITY_NOT_BUILT" in error:
        return "ARCHITECTURE_DOC_QUALITY_NOT_BUILT"
    if "ARCHITECTURE_DOC_ALIGNMENT_NOT_BUILT" in error:
        return "ARCHITECTURE_DOC_ALIGNMENT_NOT_BUILT"
    if "ARCHITECTURE_RECONSTRUCTION_NOT_BUILT" in error:
        return "ARCHITECTURE_RECONSTRUCTION_NOT_BUILT"
    if "ARCHITECTURE_DOC_VIEW_NOT_FOUND" in error:
        return "ARCHITECTURE_DOC_VIEW_NOT_FOUND"
    if "ARCHITECTURE_READING_DASHBOARD_NOT_BUILT" in error:
        return "ARCHITECTURE_READING_DASHBOARD_NOT_BUILT"
    if "ARCHITECTURE_V28_VIEW_NOT_FOUND" in error:
        return "ARCHITECTURE_V28_VIEW_NOT_FOUND"
    if "ARCHITECTURE_GRAPH_SUMMARY_NOT_BUILT" in error:
        return "ARCHITECTURE_GRAPH_SUMMARY_NOT_BUILT"
    if "ARCHITECTURE_GRAPH_VIEW_NOT_FOUND" in error:
        return "ARCHITECTURE_GRAPH_VIEW_NOT_FOUND"
    if "ARCHITECTURE_CODE_FACT_CHAINS_NOT_BUILT" in error:
        return "ARCHITECTURE_CODE_FACT_CHAINS_NOT_BUILT"
    if "ARCHITECTURE_PUBLIC_SURFACE_EVIDENCE_NOT_BUILT" in error:
        return "ARCHITECTURE_PUBLIC_SURFACE_EVIDENCE_NOT_BUILT"
    if "ARCHITECTURE_RELATIONSHIPS_V29_NOT_BUILT" in error:
        return "ARCHITECTURE_RELATIONSHIPS_V29_NOT_BUILT"
    if "ARCHITECTURE_RELATIONSHIP_CHAINS_V3_NOT_BUILT" in error:
        return "ARCHITECTURE_RELATIONSHIP_CHAINS_V3_NOT_BUILT"
    if "ARCHITECTURE_DOCUMENT_SEMANTICS_V3_NOT_BUILT" in error:
        return "ARCHITECTURE_DOCUMENT_SEMANTICS_V3_NOT_BUILT"
    if "ARCHITECTURE_RANKING_V29_NOT_BUILT" in error:
        return "ARCHITECTURE_RANKING_V29_NOT_BUILT"
    if "ARCHITECTURE_HUMAN_REPORT_V29_NOT_BUILT" in error:
        return "ARCHITECTURE_HUMAN_REPORT_V29_NOT_BUILT"
    if "ARCHITECTURE_CONTEXT_PACK_V3_NOT_FOUND" in error:
        return "ARCHITECTURE_CONTEXT_PACK_V3_NOT_FOUND"
    if "ARCHITECTURE_DOC_SOURCE_NOT_FOUND" in error:
        return "ARCHITECTURE_DOC_SOURCE_NOT_FOUND"
    if "SNAPSHOT_FILES_NOT_FOUND" in error:
        return "SNAPSHOT_FILES_NOT_FOUND"
    if "INVENTORY_NOT_FOUND" in error:
        return "INVENTORY_NOT_FOUND"
    if "SYMBOL_INDEX_NOT_FOUND" in error:
        return "SYMBOL_INDEX_NOT_FOUND"
    if "DRAWIO_PARSE_FAILED" in error:
        return "DRAWIO_PARSE_FAILED"
    if "SNAPSHOT_NOT_FOUND" in error:
        return "SNAPSHOT_NOT_FOUND"
    return "ARCHITECTURE_ERROR"


def _scale_budget_from_arguments(arguments: dict[str, Any]) -> dict[str, int] | None:
    budget: dict[str, int] = {}
    for key in ("max_files", "max_loc", "max_file_size_mb", "timeout_seconds", "shard_size"):
        if arguments.get(key) is None:
            continue
        try:
            value = int(arguments[key])
        except (TypeError, ValueError):
            continue
        if value > 0:
            budget[key] = value
    return budget or None


def _architecture_error_message(error: str) -> str:
    code = _architecture_error_code(error)
    if code == "ARCHITECTURE_SOURCE_NOT_FOUND":
        return "No architecture source was found in the codebase snapshot"
    if code == "ARCHITECTURE_MODEL_NOT_BUILT":
        return "Architecture Model has not been built"
    if code == "CODE_ARCHITECTURE_NOT_BUILT":
        return "Code-derived Architecture Model has not been built"
    if code == "ARCHITECTURE_SCALE_PROFILE_NOT_BUILT":
        return "Architecture Scale Profile has not been built"
    if code == "ARCHITECTURE_SCALE_SHARD_NOT_FOUND":
        return "Architecture scale shard was not found"
    if code == "ARCHITECTURE_LANGUAGE_PROVIDERS_NOT_BUILT":
        return "Architecture language providers have not been built"
    if code == "ARCHITECTURE_WORKFLOW_RUNTIME_NOT_BUILT":
        return "Architecture workflow/runtime candidates have not been built"
    if code == "ARCHITECTURE_DOCS_NOT_BUILT":
        return "Architecture document registry has not been built"
    if code == "ARCHITECTURE_DOC_CLAIMS_NOT_BUILT":
        return "Architecture document claims have not been built"
    if code == "ARCHITECTURE_DOC_CLAIMS_NOT_FOUND":
        return "No architecture document claims were found"
    if code == "ARCHITECTURE_DOC_QUALITY_NOT_BUILT":
        return "Architecture document quality has not been built"
    if code == "ARCHITECTURE_DOC_ALIGNMENT_NOT_BUILT":
        return "Architecture document-code alignment has not been built"
    if code == "ARCHITECTURE_RECONSTRUCTION_NOT_BUILT":
        return "Architecture document-code reconstruction has not been built"
    if code == "ARCHITECTURE_DOC_VIEW_NOT_FOUND":
        return "Architecture document-code view was not found"
    if code == "ARCHITECTURE_READING_DASHBOARD_NOT_BUILT":
        return "Architecture reading dashboard has not been built"
    if code == "ARCHITECTURE_V28_VIEW_NOT_FOUND":
        return "Architecture V2.8 reading view was not found"
    if code == "ARCHITECTURE_GRAPH_SUMMARY_NOT_BUILT":
        return "Architecture graph summary has not been built"
    if code == "ARCHITECTURE_GRAPH_VIEW_NOT_FOUND":
        return "Architecture graph view was not found"
    if code == "ARCHITECTURE_CODE_FACT_CHAINS_NOT_BUILT":
        return "Architecture code fact chains have not been built"
    if code == "ARCHITECTURE_PUBLIC_SURFACE_EVIDENCE_NOT_BUILT":
        return "Architecture public surface evidence v2 has not been built"
    if code == "ARCHITECTURE_RELATIONSHIPS_V29_NOT_BUILT":
        return "Architecture code relationships v2 have not been built"
    if code == "ARCHITECTURE_RELATIONSHIP_CHAINS_V3_NOT_BUILT":
        return "Architecture relationship chains v3 have not been built"
    if code == "ARCHITECTURE_DOCUMENT_SEMANTICS_V3_NOT_BUILT":
        return "Architecture document semantics v3 have not been built"
    if code == "ARCHITECTURE_RANKING_V29_NOT_BUILT":
        return "Architecture ranking calibration v2 has not been built"
    if code == "ARCHITECTURE_HUMAN_REPORT_V29_NOT_BUILT":
        return "Architecture human report v2 has not been built"
    if code == "ARCHITECTURE_CONTEXT_PACK_V3_NOT_FOUND":
        return "Architecture Context Pack v3 was not found"
    if code == "ARCHITECTURE_DOC_SOURCE_NOT_FOUND":
        return "No architecture document source was found in the codebase snapshot"
    if code == "SNAPSHOT_FILES_NOT_FOUND":
        return "Snapshot file manifest has not been built"
    if code == "INVENTORY_NOT_FOUND":
        return "Public surface inventory has not been built"
    if code == "SYMBOL_INDEX_NOT_FOUND":
        return "Python symbol index has not been built"
    return error or "Architecture request failed"
