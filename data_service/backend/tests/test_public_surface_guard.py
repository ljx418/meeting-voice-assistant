import ast
import json
from argparse import _SubParsersAction
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from data_service import DataService
from data_service.__main__ import _build_knowledge_parser
from data_service.mcp_tool_registry import all_tool_specs


BASELINE_PATH = Path("docs/V1.6/public-surface-baseline.json")
OVERLAY_ROOT = Path("docs/V1.6/public-surface-overlays")
IGNORED_HTTP_METHODS = {"HEAD", "OPTIONS"}
PRODUCTION_SCAN_ROOTS = [
    Path("backend/data_service"),
    Path("backend/app/graphrag/service"),
    Path("backend/app/llmwiki"),
]
UPPER_LAYER_IMPORT_PARTS = {
    "meeting",
    "asr",
    "interview",
    "learning",
    "ide_plugin",
    "agent_workflow",
}
V2_CODEBASE_TOOLS = {
    "knowledge_codebase_import",
    "knowledge_codebase_list",
    "knowledge_codebase_snapshot",
    "knowledge_project_inventory",
    "knowledge_codebase_describe",
    "knowledge_codebase_archive",
    "knowledge_code_symbol_search",
    "knowledge_public_surface_trace",
    "knowledge_project_overview",
    "knowledge_agent_context_pack",
    "knowledge_devwiki_build",
    "knowledge_devwiki_read",
    "knowledge_code_graph_build",
    "knowledge_code_graph_snapshot",
    "knowledge_code_graph_neighbors",
    "knowledge_code_graph_mermaid",
    "knowledge_code_quality_feedback",
    "knowledge_code_quality_summary",
    "knowledge_code_quality_rules_build",
    "knowledge_code_quality_rule_review",
    "knowledge_code_quality_plan",
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
    "knowledge_code_architecture_relationship_chains_v3_build",
    "knowledge_code_architecture_relationship_chains_v3",
    "knowledge_code_architecture_document_semantics_v3_build",
    "knowledge_code_architecture_document_semantics_v3",
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
    "knowledge_architecture_intent_build",
    "knowledge_architecture_intent_report",
    "knowledge_architecture_context_pack_v4",
    "knowledge_diagram_code_verification",
    "knowledge_architecture_proof_graph",
    "knowledge_architecture_intent_governance",
    "knowledge_architecture_intent_confirm",
    "knowledge_architecture_intent_revoke",
    "knowledge_code_provider_registry_build",
    "knowledge_code_provider_registry_read",
    "knowledge_code_semantic_providers_build",
    "knowledge_code_semantic_providers_read",
    "knowledge_code_actionability_build",
    "knowledge_code_actionability_read",
    "knowledge_code_impact_analyze",
    "knowledge_code_task_plan",
    "knowledge_code_patch_plan_create",
    "knowledge_code_patch_plan_read",
    "knowledge_code_patch_preview_create",
    "knowledge_code_patch_preview_read",
    "knowledge_code_patch_preview_apply",
    "knowledge_code_runtime_commands",
    "knowledge_code_runtime_run",
    "knowledge_code_runtime_result",
    "knowledge_code_runtime_profiles_build",
    "knowledge_code_runtime_profiles_read",
    "knowledge_code_runtime_profile_run",
    "knowledge_code_runtime_profile_result",
    "knowledge_code_incremental_diff",
    "knowledge_code_incremental_diff_read",
    "knowledge_code_drift_timeline",
    "knowledge_code_workbench_build",
    "knowledge_code_workbench_read",
    "knowledge_code_workbench_view",
    "knowledge_code_workbench_context_export",
    "knowledge_code_workbench_v2_build",
    "knowledge_code_workbench_v2_read",
    "knowledge_code_workbench_v2_view",
    "knowledge_code_large_project_advisor_build",
    "knowledge_code_large_project_advisor_read",
    "knowledge_code_task_navigation_build",
    "knowledge_code_task_navigation_read",
    "knowledge_code_task_navigation_prepare",
    "knowledge_code_task_navigation_query_read",
    "knowledge_code_task_relationships_build",
    "knowledge_code_task_relationships_read",
    "knowledge_code_task_impact_analyze",
    "knowledge_code_task_impact_read",
    "knowledge_code_module_reading_pack",
    "knowledge_code_module_reading_pack_read",
    "knowledge_code_agent_handoff",
    "knowledge_code_agent_handoff_read",
    "knowledge_code_task_navigation_closure_build",
    "knowledge_code_task_navigation_closure_read",
    "knowledge_code_task_navigation_closure_view",
    "knowledge_code_doc_grounded_architecture_build",
    "knowledge_code_doc_grounded_architecture_report",
    "knowledge_code_doc_grounded_verification",
    "knowledge_code_doc_grounded_architecture_brief",
    "knowledge_code_platform_console_build",
    "knowledge_code_platform_console_read",
    "knowledge_code_platform_console_view",
    "knowledge_code_platform_contracts_build",
    "knowledge_code_platform_contracts_read",
    "knowledge_code_platform_tool_catalog_build",
    "knowledge_code_platform_tool_catalog_read",
    "knowledge_code_platform_incremental_build",
    "knowledge_code_platform_incremental_read",
    "knowledge_code_platform_providers_build",
    "knowledge_code_platform_providers_read",
    "knowledge_code_platform_governance_feedback",
    "knowledge_code_platform_governance_rules_build",
    "knowledge_code_platform_governance_rule_review",
    "knowledge_code_platform_governance_overlay",
    "knowledge_code_platform_ci_readiness_build",
    "knowledge_code_platform_ci_readiness_read",
    "knowledge_code_platform_ci_release_report",
}
V2_TARGET_ROUTE_ADDITIONS = {
    ("POST", "/api/ocr/provider/health"),
    ("POST", "/api/ocr/provider/execution"),
    ("POST", "/api/tts/provider/health"),
    ("POST", "/api/tts/provider/execution"),
    ("POST", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/views/build"),
    ("POST", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/docs/build"),
    ("GET", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/docs"),
    ("POST", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/docs/claims/build"),
    ("GET", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/docs/claims"),
    ("POST", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/docs/quality/build"),
    ("GET", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/docs/quality"),
    ("POST", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/docs/alignment/build"),
    ("GET", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/docs/alignment"),
    ("POST", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/docs/reconstructed/build"),
    ("GET", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/docs/reconstructed"),
    ("GET", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/docs/views/{view_id}"),
    ("POST", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/v2_8/views/build"),
    ("GET", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/v2_8/views"),
    ("GET", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/v2_8/views/{view_id}"),
    ("POST", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/v2_8/graph/build"),
    ("GET", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/v2_8/graph"),
    ("GET", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/v2_8/graph/views/{view_id}"),
    ("POST", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/v2_8/code-fact-chains/build"),
    ("GET", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/v2_8/code-fact-chains"),
    ("POST", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/v2_8/ranking/build"),
    ("GET", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/v2_8/ranking"),
    ("POST", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/v2_8/intent/build"),
    ("GET", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/v2_8/intent"),
    ("POST", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/context-pack"),
    ("GET", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/context-pack/{pack_id}"),
    ("POST", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/v2_9/evidence/build"),
    ("GET", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/v2_9/evidence"),
    ("POST", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/v2_9/relationships/build"),
    ("GET", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/v2_9/relationships"),
    ("POST", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/v2_42/relationship-chains/build"),
    ("GET", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/v2_42/relationship-chains"),
    ("POST", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/v2_43/document-semantics/build"),
    ("GET", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/v2_43/document-semantics"),
    ("POST", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/v2_44/context-pack-optimized"),
    ("GET", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/v2_44/context-pack-optimized/{pack_id}"),
    ("POST", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/v2_45/profile-regression/build"),
    ("GET", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/v2_45/profile-regression"),
    ("POST", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/v2_9/ranking/build"),
    ("GET", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/v2_9/ranking"),
    ("POST", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/v2_9/report/build"),
    ("GET", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/v2_9/report"),
    ("GET", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/v2_9/report/views/{view_id}"),
    ("POST", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/v2_9/context-pack"),
    ("GET", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/v2_9/context-pack/{pack_id}"),
    ("POST", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/v2_10/patterns/build"),
    ("GET", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/v2_10/patterns"),
    ("GET", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/v2_10/patterns/blockers"),
    ("GET", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/v2_10/patterns/views/{view_id}"),
    ("POST", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/doc-grounded/build"),
    ("GET", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/doc-grounded/report"),
    ("GET", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/doc-grounded/verification"),
    ("GET", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/doc-grounded/view"),
    ("POST", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/doc-grounded/brief"),
    ("POST", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/providers/build"),
    ("GET", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/providers"),
    ("POST", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/semantic/build"),
    ("GET", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/semantic"),
    ("POST", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/actionability/build"),
    ("GET", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/actionability"),
    ("POST", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/impact"),
    ("POST", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/task-plan"),
    ("POST", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/patch-plans"),
    ("GET", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/patch-plans/{patch_plan_id}"),
    ("POST", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/patch-sandbox/previews"),
    ("GET", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/patch-sandbox/previews/{preview_id}"),
    ("POST", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/patch-sandbox/previews/{preview_id}/apply"),
    ("POST", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/runtime/commands"),
    ("GET", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/runtime/commands"),
    ("POST", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/runtime/runs"),
    ("GET", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/runtime/runs/{run_id}"),
    ("POST", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/runtime/profiles/build"),
    ("GET", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/runtime/profiles"),
    ("POST", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/runtime/profile-runs"),
    ("GET", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/runtime/profile-runs/{profile_run_id}"),
    ("POST", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/incremental/diff"),
    ("GET", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/incremental/diffs/{diff_id}"),
    ("GET", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/incremental/timeline"),
    ("POST", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/workbench/build"),
    ("GET", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/workbench"),
    ("GET", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/workbench/views/{view_id}"),
    ("POST", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/workbench/context-export"),
    ("POST", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/workbench-v2/build"),
    ("GET", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/workbench-v2"),
    ("GET", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/workbench-v2/views/{view_id}"),
    ("POST", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/large-project-advisor/build"),
    ("GET", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/large-project-advisor"),
    ("POST", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/task-navigation/build"),
    ("GET", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/task-navigation"),
    ("POST", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/task-navigation"),
    ("GET", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/task-navigation/{task_id}"),
    ("POST", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/relationships/build"),
    ("GET", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/relationships"),
    ("POST", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/impact-v2"),
    ("GET", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/impact-v2/{task_id}"),
    ("POST", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/reading-pack"),
    ("GET", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/reading-pack/{pack_id}"),
    ("POST", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/handoff"),
    ("GET", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/handoff/{handoff_id}"),
    ("POST", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/closure/build"),
    ("GET", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/closure"),
    ("GET", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/closure/views/{view_id}"),
    ("POST", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/platform/console/build"),
    ("GET", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/platform/console"),
    ("GET", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/platform/console/views/{view_id}"),
    ("POST", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/platform/contracts/build"),
    ("GET", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/platform/contracts"),
    ("POST", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/platform/tool-catalog/build"),
    ("GET", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/platform/tool-catalog"),
    ("POST", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/platform/incremental/build"),
    ("GET", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/platform/incremental"),
    ("POST", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/platform/providers/build"),
    ("GET", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/platform/providers"),
    ("POST", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/platform/governance/feedback"),
    ("POST", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/platform/governance/rules/build"),
    ("POST", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/platform/governance/rules/{rule_id}/review"),
    ("GET", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/platform/governance/overlay"),
    ("POST", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/platform/ci/readiness/build"),
    ("GET", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/platform/ci/readiness"),
    ("GET", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/platform/ci/release-report"),
    ("POST", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/intent/build"),
    ("GET", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/intent/report"),
    ("GET", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/intent/context-pack"),
    ("GET", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/intent/verification"),
    ("GET", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/intent/proof-graph"),
    ("GET", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/intent/governance"),
    ("POST", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/intent/confirm"),
    ("POST", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/intent/revoke"),
    ("GET", "/api/workspaces/-/ai-provider/health"),
    ("GET", "/api/workspaces/{workspace_id}/capabilities"),
    ("GET", "/api/workspaces/{workspace_id}/codebases"),
    ("POST", "/api/workspaces/{workspace_id}/codebases"),
    ("GET", "/api/workspaces/{workspace_id}/codebases/{codebase_id}"),
    ("POST", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/archive"),
    ("POST", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/snapshots"),
    ("GET", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/snapshots"),
    ("GET", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/snapshots/{snapshot_id}"),
    ("POST", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/inventory"),
    ("GET", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/inventory"),
    ("GET", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/surfaces"),
    ("GET", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/capabilities"),
    ("POST", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/symbols"),
    ("GET", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/symbols"),
    ("GET", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/symbols/{symbol_id}"),
    ("GET", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/imports"),
    ("POST", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/trace/build"),
    ("GET", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/trace/surface/{surface_id:path}"),
    ("GET", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/trace/capability/{capability_id}"),
    ("GET", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/trace/evidence"),
    ("GET", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/overview"),
    ("POST", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/agent/context-pack"),
    ("GET", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/agent/context-packs/{pack_id}"),
    ("POST", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/devwiki/build"),
    ("GET", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/devwiki/pages"),
    ("GET", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/devwiki/pages/{page_slug}"),
    ("POST", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/graph/build"),
    ("GET", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/graph"),
    ("GET", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/graph/neighbors"),
    ("GET", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/graph/mermaid"),
    ("POST", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/quality/feedback"),
    ("GET", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/quality/summary"),
    ("POST", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/quality/rules/build"),
    ("POST", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/quality/rules/{rule_id}/review"),
    ("POST", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/quality/plan"),
    ("POST", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/sources/scan"),
    ("POST", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/build"),
    ("POST", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/code/build"),
    ("POST", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/scale/build"),
    ("POST", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/inventory/build"),
    ("GET", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/code/roles"),
    ("GET", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/code/patterns"),
    ("GET", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/code/views/{view_id}"),
    ("GET", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/scale/profile"),
    ("GET", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/scale/readback"),
    ("GET", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/language-facts"),
    ("POST", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/language-providers/build"),
    ("GET", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/language-providers"),
    ("POST", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/workflow-runtime/build"),
    ("GET", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/workflow-runtime"),
    ("POST", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/v2_42/relationship-chains/build"),
    ("GET", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/v2_42/relationship-chains"),
    ("POST", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/v2_43/document-semantics/build"),
    ("GET", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/v2_43/document-semantics"),
    ("POST", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/v2_44/context-pack-optimized"),
    ("GET", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/v2_44/context-pack-optimized/{pack_id}"),
    ("POST", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/v2_45/profile-regression/build"),
    ("GET", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/v2_45/profile-regression"),
    ("GET", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/config"),
    ("GET", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/deployment"),
    ("GET", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/schema"),
    ("POST", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/taxonomy/build"),
    ("GET", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/taxonomy"),
    ("POST", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/review-queue/build"),
    ("GET", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/review-queue"),
    ("GET", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/model"),
    ("GET", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/alignment"),
    ("GET", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/findings"),
    ("GET", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/views/{view_id}"),
    ("GET", "/api/workspaces/{workspace_id}/guide"),
    ("POST", "/api/workspaces/{workspace_id}/studio/artifacts"),
    ("GET", "/api/workspaces/{workspace_id}/artifacts"),
    ("POST", "/api/workspaces/{workspace_id}/artifacts/audio"),
    ("POST", "/api/workspaces/{workspace_id}/artifacts/slides"),
    ("POST", "/api/workspaces/{workspace_id}/artifacts/slides/export"),
    ("POST", "/api/workspaces/{workspace_id}/artifacts/mindmap"),
    ("POST", "/api/workspaces/{workspace_id}/artifacts/compare"),
    ("GET", "/api/workspaces/{workspace_id}/artifacts/{artifact_id}"),
    ("DELETE", "/api/workspaces/{workspace_id}/artifacts/{artifact_id}"),
    ("GET", "/api/workspaces/{workspace_id}/artifacts/{artifact_id}/status"),
    ("GET", "/api/workspaces/{workspace_id}/artifacts/{artifact_id}/download"),
    ("POST", "/api/workspaces/{workspace_id}/research"),
    ("POST", "/api/workspaces/{workspace_id}/folder-collections/scan"),
    ("POST", "/api/workspaces/{workspace_id}/workflows/folder-summary/runs"),
    ("POST", "/api/workspaces/{workspace_id}/agent-workflows/draft"),
    ("POST", "/api/workspaces/{workspace_id}/sources/{source_id}/ocr"),
    ("GET", "/api/workspaces/{workspace_id}/sources/{source_id}/ocr/status"),
    ("GET", "/api/workspaces/{workspace_id}/sources/{source_id:path}/trace"),
    ("GET", "/api/workspaces/{workspace_id}/sources/{source_id}/preview"),
    ("GET", "/api/workspaces/{workspace_id}/sources/{source_id}/units"),
    ("GET", "/api/workspaces/{workspace_id}/sources/{source_id}/units/{unit_id}"),
    ("GET", "/api/workspaces/{workspace_id}/sources/{source_id}/units/{unit_id}/evidence/{evidence_id}"),
}


def _baseline() -> dict:
    return json.loads(BASELINE_PATH.read_text(encoding="utf-8"))


def _accepted_overlays() -> list[dict]:
    return [json.loads(path.read_text(encoding="utf-8")) for path in sorted(OVERLAY_ROOT.glob("v1_*.json"))]


def _as_route_set(routes) -> set[tuple[str, str]]:
    return {(method.upper(), path) for method, path in routes}


def _diff(current: set, expected: set) -> dict:
    return {
        "added": sorted(current - expected),
        "removed": sorted(expected - current),
    }


def _subparser_action(parser):
    return next(action for action in parser._actions if isinstance(action, _SubParsersAction))


def _knowledge_cli_inventory() -> dict[str, list[str]]:
    top_action = _subparser_action(_build_knowledge_parser())
    inventory = {}
    for command, child_parser in top_action.choices.items():
        nested_actions = [action for action in child_parser._actions if isinstance(action, _SubParsersAction)]
        inventory[command] = sorted(nested_actions[0].choices) if nested_actions else []
    return {command: inventory[command] for command in sorted(inventory)}


def _data_service_http_routes() -> set[tuple[str, str]]:
    routes = set()
    for route in app.routes:
        path = getattr(route, "path", "")
        if not (
            path.startswith("/api/v1/knowledge/")
            or path == "/api/workspaces"
            or path.startswith("/api/workspaces/")
            or path.startswith("/api/ocr/")
            or path.startswith("/api/tts/")
        ):
            continue
        for method in sorted(set(getattr(route, "methods", None) or []) - IGNORED_HTTP_METHODS):
            routes.add((method.upper(), path))
    return routes


def _imported_module_parts(path: Path) -> set[str]:
    parts = set()
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                parts.update(alias.name.lower().split("."))
        elif isinstance(node, ast.ImportFrom) and node.module:
            parts.update(node.module.lower().split("."))
    return parts


def test_v16a_mcp_registry_matches_v15_public_surface_baseline():
    baseline = _baseline()["mcp"]
    expected_tools = set(baseline["tools"])
    current_tools = {spec["name"] for spec in all_tool_specs()}

    assert len(current_tools) == baseline["tool_count"] + len(V2_CODEBASE_TOOLS)
    assert _diff(current_tools, expected_tools) == {"added": sorted(V2_CODEBASE_TOOLS), "removed": []}

    graph_session_baseline = {
        "knowledge_graph_neighbors",
        "knowledge_graph_snapshot",
        "knowledge_community_summary",
        "knowledge_session_build_cancel",
        "knowledge_session_build_start",
        "knowledge_session_build_status",
        "knowledge_session_close",
        "knowledge_session_create",
        "knowledge_session_delete",
        "knowledge_session_get",
        "knowledge_session_ingest",
        "knowledge_session_list",
        "knowledge_session_query",
    }
    assert graph_session_baseline <= current_tools


def test_v16a_knowledge_cli_parser_matches_v15_public_surface_baseline():
    baseline = _baseline()["cli"]
    overlays = _accepted_overlays()
    current_inventory = _knowledge_cli_inventory()
    expected_nested = {command: list(items) for command, items in baseline["nested_commands"].items()}
    for overlay in overlays:
        for command, additions in (overlay.get("allowed_cli_nested_additions") or {}).items():
            expected_nested.setdefault(command, [])
            expected_nested[command] = sorted(set(expected_nested[command]) | set(additions or []))

    assert set(current_inventory) == set(baseline["top_level_commands"]) | {"code"}
    expected_nested["code"] = ["architecture", "architecture-intent", "archive", "coding-agent", "context-pack", "describe", "devwiki", "graph", "import", "inventory", "list", "overview", "platform", "quality", "snapshot", "symbols", "trace"]
    assert current_inventory == expected_nested


def test_v16_current_http_route_inventory_matches_v15_baseline_plus_accepted_overlays():
    baseline = _baseline()
    overlays = _accepted_overlays()
    current_routes = _data_service_http_routes()
    expected_target = _as_route_set(baseline["target_http"]["allowlist"])
    allowed_target_additions = set()
    for overlay in overlays:
        allowed_target_additions |= _as_route_set(overlay["allowed_target_http_additions"])
    expected_compat = _as_route_set(baseline["compatibility_http"]["routes"])
    expected_current_target = expected_target | allowed_target_additions | V2_TARGET_ROUTE_ADDITIONS

    current_target = {
        route
        for route in current_routes
        if route[1] == "/api/workspaces"
        or route[1].startswith("/api/workspaces/")
        or route[1].startswith("/api/ocr/")
        or route[1].startswith("/api/tts/")
    }
    current_compat = {route for route in current_routes if route[1].startswith(baseline["compatibility_http"]["required_prefix"])}

    assert current_compat
    assert current_compat == expected_compat
    assert current_target == expected_current_target
    assert _diff(current_target, expected_target) == {"added": sorted(allowed_target_additions | V2_TARGET_ROUTE_ADDITIONS), "removed": []}
    assert _diff(current_target, expected_current_target) == {"added": [], "removed": []}
    assert current_routes == expected_compat | expected_current_target

    allowed_quality_target_paths = {
        "/api/workspaces/{workspace_id}/quality/feedback",
        "/api/workspaces/{workspace_id}/quality/correction-rules",
        "/api/workspaces/{workspace_id}/quality/correction-rules/build",
        "/api/workspaces/{workspace_id}/quality/correction-rules/{rule_id}/review",
        "/api/workspaces/{workspace_id}/quality/correction-plan",
    }
    allowed_additions = allowed_target_additions | V2_TARGET_ROUTE_ADDITIONS
    allowed_addition_paths = {path for _, path in allowed_additions}
    for method, path in current_target - expected_target:
        assert path in allowed_addition_paths
        if "/quality" in path and "/codebases" not in path:
            assert path in allowed_quality_target_paths
        if "/codebases" in path and "/quality" in path:
            assert (method, path) in V2_TARGET_ROUTE_ADDITIONS
        if "/graph" in path:
            assert path in {
                "/api/workspaces/{workspace_id}/graph/neighbors",
                "/api/workspaces/{workspace_id}/graph/community",
                "/api/workspaces/{workspace_id}/graph/query",
                "/api/workspaces/{workspace_id}/graph/session",
                "/api/workspaces/{workspace_id}/codebases/{codebase_id}/graph/build",
                "/api/workspaces/{workspace_id}/codebases/{codebase_id}/graph",
                "/api/workspaces/{workspace_id}/codebases/{codebase_id}/graph/neighbors",
                "/api/workspaces/{workspace_id}/codebases/{codebase_id}/graph/mermaid",
                "/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/v2_8/graph/build",
                "/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/v2_8/graph",
                "/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/v2_8/graph/views/{view_id}",
            }
        if "/codebases" in path:
            assert (method, path) in V2_TARGET_ROUTE_ADDITIONS

    assert len(current_target) == len(expected_current_target)


def test_v16a_boundary_guard_has_no_upper_layer_production_imports():
    violations = []
    for root in PRODUCTION_SCAN_ROOTS:
        for path in root.rglob("*.py"):
            imported_parts = _imported_module_parts(path)
            blocked = sorted(imported_parts & UPPER_LAYER_IMPORT_PARTS)
            if blocked:
                violations.append({"path": str(path), "blocked_import_parts": blocked})

    assert violations == []


def test_v16a_target_http_contract_smoke_matches_legacy_contracts(tmp_path, monkeypatch):
    from data_service.models import QueryMode

    root = tmp_path / "managed"
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(root))
    workspace_id = "v16a-guard"
    workspace = root / workspace_id
    doc = tmp_path / "v16a-source.md"
    doc.write_text("# V1.6-A Guard\n\nPublic surface guard validates target HTTP contract stability.\n", encoding="utf-8")

    service = DataService(workspace)
    plan = service.build_ingest_plan([str(doc)])
    service.run_default_pipeline(plan)
    source_id = service.read_distill_bundle(limit=5)["sources"][0]["source_id"]

    client = TestClient(app)
    legacy_query = client.post(
        "/api/v1/knowledge/query",
        json={"workspace": str(workspace), "query": "V1.6-A", "mode": QueryMode.HYBRID.value, "top_k": 5},
    )
    target_query = client.post(
        f"/api/workspaces/{workspace_id}/query",
        json={"query": "V1.6-A", "mode": QueryMode.HYBRID.value, "top_k": 5},
    )
    assert target_query.status_code == 200
    assert target_query.json()["query"] == legacy_query.json()["query"]
    assert target_query.json()["coverage_status"] in {"no_sources", "insufficient_evidence", "source_supported"}

    legacy_distill = client.post(
        "/api/v1/knowledge/distill",
        json={"workspace": str(workspace), "limit": 5, "typed_unit_type": "concept"},
    )
    target_distill = client.post(
        f"/api/workspaces/{workspace_id}/distill",
        json={"limit": 5, "typed_unit_type": "concept"},
    )
    assert target_distill.status_code == 200
    assert target_distill.json() == legacy_distill.json()

    legacy_trace = client.post(
        "/api/v1/knowledge/source/trace",
        json={"workspace": str(workspace), "source_id": source_id, "limit": 5},
    )
    assert legacy_trace.status_code == 200

    target_trace_slug = client.get(f"/api/workspaces/{workspace_id}/sources/{source_id}/trace", params={"limit": 5})
    assert target_trace_slug.status_code == 422

    target_workspace = client.post("/api/workspaces", json={"name": "V1.6-A target trace registry source"})
    assert target_workspace.status_code == 200
    target_workspace_id = target_workspace.json()["workspace_id"]
    target_import = client.post(
        f"/api/workspaces/{target_workspace_id}/sources",
        json={
            "texts": [
                {
                    "title": "V1.6-A target trace source",
                    "content": "Public surface guard validates registry source trace contract stability.",
                    "metadata": {"kind": "text"},
                }
            ]
        },
    )
    assert target_import.status_code == 200
    target_source_id = target_import.json()["data"]["sources"][0]["source_id"]
    target_trace = client.get(f"/api/workspaces/{target_workspace_id}/sources/{target_source_id}/trace", params={"limit": 5})
    assert target_trace.status_code == 200
    target_payload = target_trace.json()
    assert target_payload["status"] == "ok"
    assert target_payload["data"]["trace"]["source_id"] == target_source_id
