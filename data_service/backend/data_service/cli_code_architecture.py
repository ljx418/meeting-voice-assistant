"""CLI subcommands for V2.3 Architecture Abstraction."""

from __future__ import annotations

import argparse


def add_architecture_parser(code_subparsers: argparse._SubParsersAction) -> None:
    architecture = code_subparsers.add_parser("architecture", help="Build and read V2.3 Architecture Abstraction")
    subparsers = architecture.add_subparsers(dest="code_architecture_command", required=True)
    for name, help_text in {
        "scan": "Scan architecture sources and build model",
        "build": "Build Architecture Model",
        "model": "Read Architecture Model",
        "alignment": "Read design-code alignment",
        "findings": "Read architecture findings",
        "view": "Read architecture HTML or Mermaid view",
        "code-build": "Build V2.4 code-derived architecture roles and layers",
        "roles": "Read V2.4 code-derived architecture roles and layers",
        "patterns": "Read V2.4 code-derived architecture boundaries and pattern candidates",
        "code-view": "Read V2.4 code-derived architecture HTML or Mermaid view",
        "scale-build": "Build V2.6 architecture scale profile",
        "scale-profile": "Read V2.6 architecture scale profile",
        "inventory-build": "Build V2.6 lightweight architecture inventory",
        "language-facts": "Read V2.6 lightweight TS/JS/Vue facts",
        "config": "Read V2.6 configuration inventory",
        "deployment": "Read V2.6 deployment inventory",
        "schema": "Read V2.6 schema inventory",
        "taxonomy-build": "Build V2.6 architecture taxonomy",
        "taxonomy": "Read V2.6 architecture taxonomy",
        "review-queue-build": "Build V2.6 architecture review queue",
        "review-queue": "Read V2.6 architecture review queue",
        "large-view-build": "Build V2.6 large-project architecture views",
        "large-view": "Read V2.6 large-project architecture view",
        "docs-build": "Build V2.7 architecture document registry",
        "docs": "Read V2.7 architecture document registry",
        "docs-claims-build": "Build V2.7 architecture document claims and relations",
        "docs-claims": "Read V2.7 architecture document claims and relations",
        "docs-quality-build": "Build V2.7 architecture document quality findings",
        "docs-quality": "Read V2.7 architecture document quality findings",
        "docs-alignment-build": "Build V2.7 architecture document-code alignment and drift",
        "docs-alignment": "Read V2.7 architecture document-code alignment and drift",
        "docs-reconstructed-build": "Build V2.7 target/current/diff reconstructed architecture model and views",
        "docs-reconstructed": "Read V2.7 reconstructed architecture model",
        "docs-view": "Read V2.7 reconstructed architecture HTML or Mermaid view",
        "views-build": "Build V2.8 human-readable architecture dashboard views",
        "views": "Read V2.8 architecture reading dashboard",
        "view-v2-8": "Read V2.8 architecture reading dashboard HTML or Mermaid view",
        "graph-build-v2-8": "Build V2.8 clustered architecture graph summary and views",
        "graph-v2-8": "Read V2.8 clustered architecture graph summary",
        "graph-view-v2-8": "Read V2.8 clustered architecture graph view",
        "chains-build": "Build V2.8 deterministic code fact chains",
        "chains": "Read V2.8 deterministic code fact chains",
        "ranking-build": "Build V2.8 architecture signal ranking and review queue v2",
        "ranking": "Read V2.8 architecture signal ranking and review queue v2",
        "intent-build": "Build V2.8 evidence-backed architecture intent states",
        "intent": "Read V2.8 evidence-backed architecture intent states",
        "context-pack": "Create V2.8 architecture context pack",
        "context-pack-read": "Read V2.8 architecture context pack",
        "evidence-v2-build": "Build V2.9 line-level public surface evidence",
        "evidence-v2": "Read V2.9 line-level public surface evidence",
        "relationships-v2-build": "Build V2.9 shallow code relationships",
        "relationships-v2": "Read V2.9 shallow code relationships",
        "ranking-v2-build": "Build V2.9 ranking calibration",
        "ranking-v2": "Read V2.9 ranking calibration",
        "human-report-v2-build": "Build V2.9 human review report",
        "human-report-v2": "Read V2.9 human review report",
        "human-report-v2-view": "Read V2.9 human review report HTML or Mermaid view",
        "context-pack-v3": "Create V2.9 architecture context pack",
        "context-pack-v3-read": "Read V2.9 architecture context pack",
        "patterns-v2-build": "Build V2.10 generic architecture pattern evidence",
        "patterns-v2": "Read V2.10 generic architecture pattern evidence",
        "pattern-blockers": "Read V2.10 architecture pattern blockers",
        "pattern-view": "Read V2.10 architecture pattern HTML or Mermaid view",
    }.items():
        parser = subparsers.add_parser(name, help=help_text)
        _add_common(parser)
        if name in {"scan", "build", "code-build", "scale-build", "inventory-build", "docs-build", "evidence-v2-build", "patterns-v2-build"}:
            parser.add_argument("--snapshot-id", help="Optional snapshot identifier; defaults to latest")
        if name == "view":
            parser.add_argument("--view-id", default="architecture.html")
        if name == "code-view":
            parser.add_argument("--view-id", default="code_derived_architecture.html")
        if name == "large-view":
            parser.add_argument("--view-id", default="architecture_large_project_overview.html")
        if name == "docs-view":
            parser.add_argument("--view-id", default="document_code_architecture_report.html")
        if name == "view-v2-8":
            parser.add_argument("--view-id", default="architecture_reading_dashboard.html")
        if name == "graph-view-v2-8":
            parser.add_argument("--view-id", default="system_overview")
        if name == "human-report-v2-view":
            parser.add_argument("--view-id", default="architecture_human_review_report_v2.html")
        if name == "pattern-view":
            parser.add_argument("--view-id", default="pattern_evidence_report.html")
        if name == "context-pack":
            parser.add_argument("--mode", default="project_brief")
            parser.add_argument("--task")
            parser.add_argument("--max-tokens", type=int, default=12000)
        if name == "context-pack-v3":
            parser.add_argument("--mode", default="project_brief")
            parser.add_argument("--role", default="maintainer")
            parser.add_argument("--task")
            parser.add_argument("--max-tokens", type=int, default=12000)
        if name == "context-pack-read":
            parser.add_argument("--pack-id", required=True)
        if name == "context-pack-v3-read":
            parser.add_argument("--pack-id", required=True)


def architecture_tool_payload(args: argparse.Namespace) -> tuple[str, dict]:
    mapping = {
        "scan": "knowledge_architecture_sources_scan",
        "build": "knowledge_architecture_model_build",
        "model": "knowledge_architecture_model_read",
        "alignment": "knowledge_architecture_alignment",
        "findings": "knowledge_architecture_findings",
        "view": "knowledge_architecture_view",
        "code-build": "knowledge_code_architecture_build",
        "roles": "knowledge_code_architecture_roles",
        "patterns": "knowledge_code_architecture_patterns",
        "code-view": "knowledge_code_architecture_view",
        "scale-build": "knowledge_code_architecture_scale_build",
        "scale-profile": "knowledge_code_architecture_scale_profile",
        "inventory-build": "knowledge_code_architecture_inventory_build",
        "language-facts": "knowledge_code_architecture_language_facts",
        "config": "knowledge_code_architecture_config_inventory",
        "deployment": "knowledge_code_architecture_deployment_inventory",
        "schema": "knowledge_code_architecture_schema_inventory",
        "taxonomy-build": "knowledge_code_architecture_taxonomy_build",
        "taxonomy": "knowledge_code_architecture_taxonomy",
        "review-queue-build": "knowledge_code_architecture_review_queue_build",
        "review-queue": "knowledge_code_architecture_review_queue",
        "large-view-build": "knowledge_code_architecture_large_project_views_build",
        "large-view": "knowledge_code_architecture_large_project_view",
        "docs-build": "knowledge_code_architecture_docs_build",
        "docs": "knowledge_code_architecture_docs_list",
        "docs-claims-build": "knowledge_code_architecture_doc_claims_build",
        "docs-claims": "knowledge_code_architecture_doc_claims",
        "docs-quality-build": "knowledge_code_architecture_doc_quality_build",
        "docs-quality": "knowledge_code_architecture_doc_quality",
        "docs-alignment-build": "knowledge_code_architecture_doc_code_alignment_build",
        "docs-alignment": "knowledge_code_architecture_doc_code_alignment",
        "docs-reconstructed-build": "knowledge_code_architecture_reconstructed_build",
        "docs-reconstructed": "knowledge_code_architecture_reconstructed",
        "docs-view": "knowledge_code_architecture_doc_view",
        "views-build": "knowledge_code_architecture_views_build",
        "views": "knowledge_code_architecture_views",
        "view-v2-8": "knowledge_code_architecture_view_v2_8",
        "graph-build-v2-8": "knowledge_code_architecture_graph_summary_build",
        "graph-v2-8": "knowledge_code_architecture_graph_summary",
        "graph-view-v2-8": "knowledge_code_architecture_graph_view",
        "chains-build": "knowledge_code_architecture_code_fact_chains_build",
        "chains": "knowledge_code_architecture_code_fact_chains",
        "ranking-build": "knowledge_code_architecture_ranking_build",
        "ranking": "knowledge_code_architecture_ranking",
        "intent-build": "knowledge_code_architecture_intent_evidence_build",
        "intent": "knowledge_code_architecture_intent_evidence",
        "context-pack": "knowledge_code_architecture_context_pack_v2",
        "context-pack-read": "knowledge_code_architecture_context_pack_read",
        "evidence-v2-build": "knowledge_code_architecture_evidence_v2_build",
        "evidence-v2": "knowledge_code_architecture_evidence_v2",
        "relationships-v2-build": "knowledge_code_architecture_relationships_v2_build",
        "relationships-v2": "knowledge_code_architecture_relationships_v2",
        "ranking-v2-build": "knowledge_code_architecture_ranking_v2_build",
        "ranking-v2": "knowledge_code_architecture_ranking_v2",
        "human-report-v2-build": "knowledge_code_architecture_human_report_v2_build",
        "human-report-v2": "knowledge_code_architecture_human_report_v2",
        "human-report-v2-view": "knowledge_code_architecture_human_report_v2_view",
        "context-pack-v3": "knowledge_code_architecture_context_pack_v3",
        "context-pack-v3-read": "knowledge_code_architecture_context_pack_v3_read",
        "patterns-v2-build": "knowledge_code_architecture_patterns_v2_build",
        "patterns-v2": "knowledge_code_architecture_patterns_v2",
        "pattern-blockers": "knowledge_code_architecture_pattern_blockers",
        "pattern-view": "knowledge_code_architecture_pattern_view",
    }
    command = args.code_architecture_command
    payload = {"workspace_id": args.workspace_id, "codebase_id": args.codebase_id}
    if command in {"scan", "build", "code-build", "scale-build", "inventory-build", "docs-build", "evidence-v2-build", "patterns-v2-build"}:
        payload["snapshot_id"] = getattr(args, "snapshot_id", None)
    if command in {"view", "code-view", "large-view", "docs-view", "view-v2-8", "graph-view-v2-8", "human-report-v2-view", "pattern-view"}:
        payload["view_id"] = getattr(args, "view_id", "architecture.html")
    if command == "context-pack":
        payload["mode"] = getattr(args, "mode", "project_brief")
        payload["task"] = getattr(args, "task", None)
        payload["max_tokens"] = getattr(args, "max_tokens", 12000)
    if command == "context-pack-read":
        payload["pack_id"] = getattr(args, "pack_id")
    if command == "context-pack-v3":
        payload["mode"] = getattr(args, "mode", "project_brief")
        payload["role"] = getattr(args, "role", "maintainer")
        payload["task"] = getattr(args, "task", None)
        payload["max_tokens"] = getattr(args, "max_tokens", 12000)
    if command == "context-pack-v3-read":
        payload["pack_id"] = getattr(args, "pack_id")
    return mapping[command], payload


def _add_common(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--workspace-root", help="Managed workspace root; overrides DATA_SERVICE_WORKSPACE_ROOT for this command")
    parser.add_argument("--workspace-id", required=True)
    parser.add_argument("--codebase-id", required=True)
