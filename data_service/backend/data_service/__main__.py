"""CLI entrypoint for the local knowledge governance service."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .cli_code import add_code_parser, run_code_command
from .models import GraphExecutionOwner, QueryMode
from .distill_contract import run_distill_contract
from .graph_community_contract import graph_community_payload
from .graph_neighbors_contract import graph_neighbors_payload
from .graph_query_contract import graph_query_payload
from .graph_session_contract import graph_session_payload
from .mcp_build_runtime import BuildRuntime
from .mcp_build_tools import handle_build_tool
from .mcp_common import blocked, bounded_int, envelope, now, read_json, slug, write_json
from .mcp_session_tools import handle_session_tool
from .session_service import SessionKnowledgeService
from .mcp_source_tools import handle_source_tool
from .mcp_workspace_runtime import WorkspaceRuntime
from .mcp_workspace_tools import handle_workspace_tool
from .quality_contract import (
    quality_correction_plan_preview_payload,
    quality_correction_rule_review_payload,
    quality_correction_rules_build_payload,
    quality_correction_rules_payload,
    quality_feedback_list_payload,
    quality_summary_payload,
    record_quality_feedback_payload,
)
from .query_contract import run_query_contract
from .service import DataService
from .source_trace_contract import source_trace_payload


def _add_workspace_argument(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--workspace", "--workspace-id", dest="workspace", required=True, help="Workspace directory")


def _add_quality_parser(subparsers: argparse._SubParsersAction) -> None:
    quality = subparsers.add_parser("quality", help="Preview quality governance state")
    quality_subparsers = quality.add_subparsers(dest="quality_command", required=True)

    quality_summary = quality_subparsers.add_parser("summary", help="Preview quality governance summary")
    _add_workspace_argument(quality_summary)

    quality_plan = quality_subparsers.add_parser("correction-plan", help="Preview approved quality correction plan")
    _add_workspace_argument(quality_plan)
    quality_plan.add_argument("--rebuild", action="store_true", help="Rebuild the plan from approved rules before reading")

    quality_feedback = quality_subparsers.add_parser("feedback-list", help="List quality feedback records")
    _add_workspace_argument(quality_feedback)
    quality_feedback.add_argument("--target-type", help="Optional target_type filter")
    quality_feedback.add_argument("--target-id", help="Optional target_id filter")
    quality_feedback.add_argument("--limit", type=int, default=100, help="Max feedback records to return")

    quality_feedback_write = quality_subparsers.add_parser("feedback", help="Record controlled quality feedback")
    _add_workspace_argument(quality_feedback_write)
    quality_feedback_write.add_argument("--target-type", required=True, help="Target type, e.g. entity, source, community")
    quality_feedback_write.add_argument("--target-id", required=True, help="Target identifier")
    quality_feedback_write.add_argument("--action", required=True, help="Feedback action, e.g. rename_suggest or merge_suggest")
    quality_feedback_write.add_argument("--label", default="", help="Optional human-readable target label")
    quality_feedback_write.add_argument("--suggested-value", default="", help="Optional suggested canonical value")
    quality_feedback_write.add_argument("--reason", default="", help="Optional review reason")
    quality_feedback_write.add_argument("--metadata-json", default="{}", help="Optional JSON object metadata")

    quality_rules = quality_subparsers.add_parser("rules", help="List quality correction rules")
    _add_workspace_argument(quality_rules)
    quality_rules.add_argument("--status", choices=["draft", "approved", "rejected", "archived", "revoked"], help="Optional review status filter")
    quality_rules.add_argument("--limit", type=int, default=100, help="Max rules to return")

    quality_rules_build = quality_subparsers.add_parser("rules-build", help="Build draft quality correction rules from feedback")
    _add_workspace_argument(quality_rules_build)

    quality_review = quality_subparsers.add_parser("review", help="Review one quality correction rule")
    _add_workspace_argument(quality_review)
    quality_review.add_argument("--rule-id", required=True, help="Correction rule identifier")
    quality_review.add_argument("--status", required=True, choices=["draft", "approved", "rejected", "archived", "revoked"], help="Review status")
    quality_review.add_argument("--reviewer", default="", help="Reviewer identifier")
    quality_review.add_argument("--note", default="", help="Optional review note")


def _add_query_parser(subparsers: argparse._SubParsersAction) -> None:
    query = subparsers.add_parser("query", help="Query llmwiki, graphrag, or both")
    query.add_argument("query", help="Query text")
    _add_workspace_argument(query)
    query.add_argument("--mode", choices=[mode.value for mode in QueryMode], default=QueryMode.HYBRID.value)
    query.add_argument("--top-k", type=int, default=8)


def _add_workspace_lifecycle_parser(subparsers: argparse._SubParsersAction) -> None:
    workspace = subparsers.add_parser("workspace", help="Read managed workspace lifecycle state")
    workspace_subparsers = workspace.add_subparsers(dest="workspace_command", required=True)

    workspace_create = workspace_subparsers.add_parser("create", help="Create or register a managed knowledge workspace")
    workspace_create.add_argument("--workspace-root", help="Managed workspace root; overrides DATA_SERVICE_WORKSPACE_ROOT for this command")
    workspace_create.add_argument("--name", required=True, help="Workspace display name")
    workspace_create.add_argument("--owner", help="Optional owner")
    workspace_create.add_argument("--tag", dest="tags", action="append", default=[], help="Optional workspace tag; repeatable")

    workspace_list = workspace_subparsers.add_parser("list", help="List managed knowledge workspaces")
    workspace_list.add_argument("--workspace-root", help="Managed workspace root; overrides DATA_SERVICE_WORKSPACE_ROOT for this command")
    workspace_list.add_argument("--owner", help="Optional owner filter")
    workspace_list.add_argument("--tag", help="Optional tag filter")
    workspace_list.add_argument("--limit", type=int, default=50, help="Max workspaces to return")

    workspace_describe = workspace_subparsers.add_parser("describe", help="Describe one managed knowledge workspace")
    workspace_describe.add_argument("--workspace-root", help="Managed workspace root; overrides DATA_SERVICE_WORKSPACE_ROOT for this command")
    workspace_describe.add_argument("--workspace-id", help="Managed workspace identifier")
    workspace_describe.add_argument("--workspace", help="Compat workspace directory")

    workspace_archive = workspace_subparsers.add_parser("archive", help="Archive a managed knowledge workspace")
    workspace_archive.add_argument("--workspace-root", help="Managed workspace root; overrides DATA_SERVICE_WORKSPACE_ROOT for this command")
    workspace_archive.add_argument("--workspace-id", required=True, help="Managed workspace identifier")
    workspace_archive.add_argument("--reason", default="", help="Optional archive reason")


def _add_source_lifecycle_parser(subparsers: argparse._SubParsersAction) -> None:
    source = subparsers.add_parser("source", help="Manage source registry state")
    source_subparsers = source.add_subparsers(dest="source_command", required=True)

    source_import = source_subparsers.add_parser("import", help="Import files or text into a managed workspace")
    source_import.add_argument("--workspace-root", help="Managed workspace root; overrides DATA_SERVICE_WORKSPACE_ROOT for this command")
    source_import.add_argument("--workspace-id", required=True, help="Managed workspace identifier")
    source_import.add_argument("--path", dest="paths", action="append", default=[], help="Source file path; repeatable")
    source_import.add_argument("--text", help="Inline text source content")
    source_import.add_argument("--title", default="text-source", help="Title for inline text source")
    source_import.add_argument("--metadata-json", default="{}", help="Optional JSON object metadata shared by imported sources")

    source_list = source_subparsers.add_parser("list", help="List imported sources for a managed workspace")
    source_list.add_argument("--workspace-root", help="Managed workspace root; overrides DATA_SERVICE_WORKSPACE_ROOT for this command")
    source_list.add_argument("--workspace-id", required=True, help="Managed workspace identifier")
    source_list.add_argument("--status", choices=["active", "removed", "duplicate", "blocked"], help="Optional source status filter")
    source_list.add_argument("--limit", type=int, default=100, help="Max sources to return")

    source_remove = source_subparsers.add_parser("remove", help="Soft-remove one imported source from a managed workspace")
    source_remove.add_argument("--workspace-root", help="Managed workspace root; overrides DATA_SERVICE_WORKSPACE_ROOT for this command")
    source_remove.add_argument("--workspace-id", required=True, help="Managed workspace identifier")
    source_remove.add_argument("--source-id", required=True, help="Imported source identifier")
    source_remove.add_argument("--reason", default="", help="Optional remove reason")


def _add_build_lifecycle_parser(subparsers: argparse._SubParsersAction) -> None:
    build = subparsers.add_parser("build", help="Manage build operation state")
    build_subparsers = build.add_subparsers(dest="build_command", required=True)

    build_start = build_subparsers.add_parser("start", help="Start a managed build operation")
    build_start.add_argument("--workspace-root", help="Managed workspace root; overrides DATA_SERVICE_WORKSPACE_ROOT for this command")
    build_start.add_argument("--workspace-id", required=True, help="Managed workspace identifier")
    build_start.add_argument("--mode", choices=["full", "incremental", "graph_only", "llmwiki_only"], default="full", help="Build mode")

    build_status = build_subparsers.add_parser("status", help="Poll one managed build operation")
    build_status.add_argument("--workspace-root", help="Managed workspace root; overrides DATA_SERVICE_WORKSPACE_ROOT for this command")
    build_status.add_argument("--workspace-id", required=True, help="Managed workspace identifier")
    build_status.add_argument("--operation-id", required=True, help="Build operation identifier")

    build_cancel = build_subparsers.add_parser("cancel", help="Cancel a managed build operation")
    build_cancel.add_argument("--workspace-root", help="Managed workspace root; overrides DATA_SERVICE_WORKSPACE_ROOT for this command")
    build_cancel.add_argument("--workspace-id", required=True, help="Managed workspace identifier")
    build_cancel.add_argument("--operation-id", required=True, help="Build operation identifier")
    build_cancel.add_argument("--reason", default="", help="Optional cancel reason")


def _add_graph_lifecycle_parser(subparsers: argparse._SubParsersAction) -> None:
    graph = subparsers.add_parser("graph", help="Read managed graph state")
    graph_subparsers = graph.add_subparsers(dest="graph_command", required=True)

    graph_snapshot = graph_subparsers.add_parser("snapshot", help="Read a managed workspace graph snapshot")
    graph_snapshot.add_argument("--workspace-root", help="Managed workspace root; overrides DATA_SERVICE_WORKSPACE_ROOT for this command")
    graph_snapshot.add_argument("--workspace-id", help="Managed workspace identifier")
    graph_snapshot.add_argument("--workspace", help="Compat workspace directory")
    graph_snapshot.add_argument("--max-nodes", type=int, default=200, help="Max graph nodes to return")

    graph_neighbors = graph_subparsers.add_parser("neighbors", help="Read managed workspace graph neighbors")
    graph_neighbors.add_argument("--workspace-root", help="Managed workspace root; overrides DATA_SERVICE_WORKSPACE_ROOT for this command")
    graph_neighbors.add_argument("--workspace-id", help="Managed workspace identifier")
    graph_neighbors.add_argument("--workspace", help="Compat workspace directory")
    graph_neighbors.add_argument("--node-id", help="Graph node identifier")
    graph_neighbors.add_argument("--entity-id", help="Graph entity identifier")
    graph_neighbors.add_argument("--depth", type=int, default=1, help="Neighbor traversal depth, 1-3")
    graph_neighbors.add_argument("--max-nodes", type=int, default=80, help="Max nodes to return")
    graph_neighbors.add_argument("--json", action="store_true", help="Emit JSON output")

    graph_community = graph_subparsers.add_parser("community", help="Read managed workspace graph communities")
    graph_community.add_argument("--workspace-root", help="Managed workspace root; overrides DATA_SERVICE_WORKSPACE_ROOT for this command")
    graph_community.add_argument("--workspace-id", help="Managed workspace identifier")
    graph_community.add_argument("--workspace", help="Compat workspace directory")
    graph_community.add_argument("--community-id", help="Graph community identifier")
    graph_community.add_argument("--limit", type=int, default=20, help="Max communities to return, 1-100")
    graph_community.add_argument("--include-members", action="store_true", help="Include stable community member summaries")
    graph_community.add_argument("--json", action="store_true", help="Emit JSON output")

    graph_query = graph_subparsers.add_parser("query", help="Query managed workspace graph state")
    graph_query.add_argument("--workspace-root", help="Managed workspace root; overrides DATA_SERVICE_WORKSPACE_ROOT for this command")
    graph_query.add_argument("--workspace-id", help="Managed workspace identifier")
    graph_query.add_argument("--workspace", help="Compat workspace directory")
    graph_query.add_argument("--query", "--q", dest="query", help="Graph query text")
    graph_query.add_argument("--top-k", type=int, default=10, help="Max graph query items, 1-50")
    graph_query.add_argument("--include-nodes", dest="include_nodes", action="store_true", default=True, help="Include stable graph nodes")
    graph_query.add_argument("--no-include-nodes", dest="include_nodes", action="store_false", help="Omit graph nodes")
    graph_query.add_argument("--include-edges", dest="include_edges", action="store_true", default=True, help="Include stable graph edges")
    graph_query.add_argument("--no-include-edges", dest="include_edges", action="store_false", help="Omit graph edges")
    graph_query.add_argument("--include-communities", action="store_true", help="Include stable graph communities")
    graph_query.add_argument("--json", action="store_true", help="Emit JSON output")

    graph_session = graph_subparsers.add_parser("session", help="Inspect existing session graph artifacts")
    graph_session.add_argument("--workspace-root", help="Managed workspace root; overrides DATA_SERVICE_WORKSPACE_ROOT for this command")
    graph_session.add_argument("--workspace-id", help="Managed workspace identifier")
    graph_session.add_argument("--workspace", help="Compat workspace directory")
    graph_session.add_argument("--session-id", help="Optional session graph identifier")
    graph_session.add_argument("--limit", type=int, default=20, help="Max session graph summaries to return, 1-100")
    graph_session.add_argument("--include-nodes", action="store_true", help="Include stable node summaries for detail")
    graph_session.add_argument("--include-edges", action="store_true", help="Include stable edge summaries for detail")
    graph_session.add_argument("--node-limit", type=int, default=50, help="Max nodes to return when included, 1-200")
    graph_session.add_argument("--edge-limit", type=int, default=100, help="Max edges to return when included, 1-500")
    graph_session.add_argument("--json", action="store_true", help="Emit JSON output")


def _add_trace_lifecycle_parser(subparsers: argparse._SubParsersAction) -> None:
    trace = subparsers.add_parser("trace", help="Read managed source trace state")
    trace_subparsers = trace.add_subparsers(dest="trace_command", required=True)

    trace_source = trace_subparsers.add_parser("source", help="Trace one source through distill, wiki, and graph artifacts")
    trace_source.add_argument("--workspace-root", help="Managed workspace root; overrides DATA_SERVICE_WORKSPACE_ROOT for this command")
    trace_source.add_argument("--workspace-id", help="Managed workspace identifier")
    trace_source.add_argument("--workspace", help="Compat workspace directory")
    trace_source.add_argument("--source-id", required=True, help="Source identifier")
    trace_source.add_argument("--limit", type=int, default=12, help="Max trace items per section")


def _build_parser(*, prog: str = "data_service") -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog=prog,
        description="MCP-first local knowledge governance service CLI",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    ingest = subparsers.add_parser("ingest", help="Run the knowledge governance ingest/build pipeline")
    ingest.add_argument("paths", nargs="+", help="File paths to ingest")
    ingest.add_argument("--workspace", required=True, help="Workspace directory")
    ingest.add_argument(
        "--graphrag-owner",
        choices=[owner.value for owner in GraphExecutionOwner],
        default=GraphExecutionOwner.APP_GRAPHRAG.value,
        help="Who executes GraphRAG indexing: local data_service or app.graphrag handoff",
    )

    summary = subparsers.add_parser("summary", help="Render workspace summary")
    _add_workspace_argument(summary)

    distill = subparsers.add_parser("distill", help="Preview distill artifacts")
    _add_workspace_argument(distill)
    distill.add_argument("--source-id", help="Optional source_id to inspect")
    distill.add_argument("--limit", type=int, default=20, help="Max sources/units to return")
    distill.add_argument("--kind", help="Optional unit kind filter")
    distill.add_argument("--typed-type", dest="typed_unit_type", help="Optional typed unit type filter")
    distill.add_argument("--min-importance", type=float, default=0.0, help="Minimum unit importance")
    distill.add_argument("--llm-enriched-only", action="store_true", help="Only return llm-enriched units")
    distill.add_argument("--authority", help="Optional authority filter, e.g. PRIMARY_DOC or SECONDARY_CHAT")
    distill.add_argument("--min-source-weight", type=float, default=0.0, help="Minimum source_weight")
    distill.add_argument("--min-source-density", type=float, default=0.0, help="Minimum source_density_score")

    boundary = subparsers.add_parser("boundary", help="Inspect the current governance service vs graph engine boundary")
    _add_workspace_argument(boundary)

    graphrag_execute = subparsers.add_parser("graphrag-execute", help="Run delegated app.graphrag execution for a workspace")
    _add_workspace_argument(graphrag_execute)

    _add_query_parser(subparsers)
    _add_quality_parser(subparsers)

    return parser


def _build_knowledge_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="knowledge",
        description="MCP-first local knowledge governance service CLI",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    _add_workspace_lifecycle_parser(subparsers)
    _add_source_lifecycle_parser(subparsers)
    _add_build_lifecycle_parser(subparsers)
    _add_graph_lifecycle_parser(subparsers)
    _add_trace_lifecycle_parser(subparsers)
    add_code_parser(subparsers)
    _add_query_parser(subparsers)
    _add_quality_parser(subparsers)
    return parser


def _workspace_runtime(args: argparse.Namespace) -> WorkspaceRuntime:
    workspace_root = getattr(args, "workspace_root", None)
    root = Path(workspace_root).expanduser() if workspace_root else None
    default_workspace = (root / "_default") if root else (Path.cwd() / "workspace")
    return WorkspaceRuntime(default_workspace, workspace_root=root)


def _run_workspace_command(args: argparse.Namespace) -> int:
    runtime = _workspace_runtime(args)
    if args.workspace_command == "create":
        name = "knowledge_workspace_create"
        arguments = {
            "name": getattr(args, "name", None),
            "owner": getattr(args, "owner", None),
            "tags": getattr(args, "tags", []),
        }
    elif args.workspace_command == "list":
        name = "knowledge_workspace_list"
        arguments = {
            "owner": getattr(args, "owner", None),
            "tag": getattr(args, "tag", None),
            "limit": getattr(args, "limit", 50),
        }
    elif args.workspace_command == "describe":
        name = "knowledge_workspace_describe"
        arguments = {
            "workspace_id": getattr(args, "workspace_id", None),
            "workspace": getattr(args, "workspace", None),
        }
    elif args.workspace_command == "archive":
        name = "knowledge_workspace_archive"
        arguments = {
            "workspace_id": getattr(args, "workspace_id", None),
            "reason": getattr(args, "reason", ""),
        }
    else:
        return 1

    payload = handle_workspace_tool(
        name,
        arguments,
        bounded_int=bounded_int,
        envelope=envelope,
        ensure_workspace_meta=runtime.ensure_workspace_meta,
        layout_payload=runtime.layout_payload,
        now=now,
        operations_dir=runtime.operations_dir,
        read_json=read_json,
        resolve_workspace=runtime.resolve_workspace,
        slug=slug,
        workspace_meta_path=runtime.workspace_meta_path,
        workspace_root=runtime.workspace_root,
        write_json=write_json,
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


def _run_source_command(args: argparse.Namespace) -> int:
    runtime = _workspace_runtime(args)
    if args.source_command == "import":
        try:
            metadata = json.loads(getattr(args, "metadata_json", "{}") or "{}")
        except json.JSONDecodeError as exc:
            raise SystemExit(f"--metadata-json must be a JSON object: {exc}") from exc
        if not isinstance(metadata, dict):
            raise SystemExit("--metadata-json must be a JSON object")

        texts = []
        text = getattr(args, "text", None)
        if text is not None:
            texts.append(
                {
                    "title": getattr(args, "title", "text-source"),
                    "content": text,
                    "metadata": {},
                }
            )
        name = "knowledge_source_import"
        arguments = {
            "workspace_id": getattr(args, "workspace_id", None),
            "paths": getattr(args, "paths", []),
            "texts": texts,
            "metadata": metadata,
        }
    elif args.source_command == "list":
        name = "knowledge_source_list"
        arguments = {
            "workspace_id": getattr(args, "workspace_id", None),
            "status": getattr(args, "status", None),
            "limit": getattr(args, "limit", 100),
        }
    elif args.source_command == "remove":
        name = "knowledge_source_remove"
        arguments = {
            "workspace_id": getattr(args, "workspace_id", None),
            "source_id": getattr(args, "source_id", None),
            "reason": getattr(args, "reason", ""),
        }
    else:
        return 1

    payload = handle_source_tool(
        name,
        arguments,
        blocked=blocked,
        bounded_int=bounded_int,
        envelope=envelope,
        ensure_workspace_meta=runtime.ensure_workspace_meta,
        now=now,
        read_json=read_json,
        resolve_workspace=runtime.resolve_workspace,
        sources_manifest_path=runtime.sources_manifest_path,
        write_json=write_json,
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


def _run_build_command(args: argparse.Namespace) -> int:
    runtime = _workspace_runtime(args)
    build_runtime = BuildRuntime(runtime)
    if args.build_command == "start":
        name = "knowledge_build_start"
        arguments = {
            "workspace_id": getattr(args, "workspace_id", None),
            "mode": getattr(args, "mode", "full"),
        }
    elif args.build_command == "status":
        name = "knowledge_build_status"
        arguments = {
            "workspace_id": getattr(args, "workspace_id", None),
            "operation_id": getattr(args, "operation_id", None),
        }
    elif args.build_command == "cancel":
        name = "knowledge_build_cancel"
        arguments = {
            "workspace_id": getattr(args, "workspace_id", None),
            "operation_id": getattr(args, "operation_id", None),
            "reason": getattr(args, "reason", ""),
        }
    else:
        return 1

    payload = handle_build_tool(
        name,
        arguments,
        blocked=blocked,
        ensure_build_worker=build_runtime.ensure_build_worker,
        ensure_workspace_meta=runtime.ensure_workspace_meta,
        envelope=envelope,
        now=now,
        operation_envelope=build_runtime.operation_envelope,
        operation_path=runtime.operation_path,
        read_json=read_json,
        resolve_workspace=runtime.resolve_workspace,
        write_json=write_json,
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


def _run_graph_command(args: argparse.Namespace) -> int:
    runtime = _workspace_runtime(args)
    if args.graph_command == "snapshot":
        workspace = runtime.resolve_workspace(getattr(args, "workspace_id", None), getattr(args, "workspace", None))
        service = DataService(workspace)
        name = "knowledge_graph_snapshot"
        arguments = {
            "workspace_id": getattr(args, "workspace_id", None),
            "workspace": getattr(args, "workspace", None),
            "scope": "workspace",
            "max_nodes": getattr(args, "max_nodes", 200),
        }
    elif args.graph_command == "neighbors":
        workspace = runtime.resolve_workspace(getattr(args, "workspace_id", None), getattr(args, "workspace", None))
        service = DataService(workspace)
        try:
            payload = graph_neighbors_payload(
                service,
                workspace_id=runtime.workspace_id_for_service(service),
                node_id=getattr(args, "node_id", None),
                entity_id=getattr(args, "entity_id", None),
                depth=getattr(args, "depth", 1),
                max_nodes=getattr(args, "max_nodes", 80),
                envelope=envelope,
                blocked=blocked,
            )
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            return 2
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0
    elif args.graph_command == "community":
        workspace = runtime.resolve_workspace(getattr(args, "workspace_id", None), getattr(args, "workspace", None))
        service = DataService(workspace)
        try:
            payload = graph_community_payload(
                service,
                workspace_id=runtime.workspace_id_for_service(service),
                community_id=getattr(args, "community_id", None),
                limit=getattr(args, "limit", 20),
                include_members=bool(getattr(args, "include_members", False)),
                envelope=envelope,
                blocked=blocked,
            )
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            return 2
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0
    elif args.graph_command == "query":
        workspace = runtime.resolve_workspace(getattr(args, "workspace_id", None), getattr(args, "workspace", None))
        service = DataService(workspace)
        try:
            payload = graph_query_payload(
                service,
                workspace_id=runtime.workspace_id_for_service(service),
                query=getattr(args, "query", None),
                top_k=getattr(args, "top_k", 10),
                include_nodes=bool(getattr(args, "include_nodes", True)),
                include_edges=bool(getattr(args, "include_edges", True)),
                include_communities=bool(getattr(args, "include_communities", False)),
                envelope=envelope,
                blocked=blocked,
            )
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            return 2
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0
    elif args.graph_command == "session":
        try:
            workspace = runtime.resolve_workspace(getattr(args, "workspace_id", None), getattr(args, "workspace", None))
            service = DataService(workspace)
            payload = graph_session_payload(
                SessionKnowledgeService(workspace, workspace_id=runtime.workspace_id_for_service(service)),
                workspace_id=runtime.workspace_id_for_service(service),
                session_id=getattr(args, "session_id", None),
                limit=getattr(args, "limit", 20),
                include_nodes=bool(getattr(args, "include_nodes", False)),
                include_edges=bool(getattr(args, "include_edges", False)),
                node_limit=getattr(args, "node_limit", 50),
                edge_limit=getattr(args, "edge_limit", 100),
                envelope=envelope,
                blocked=blocked,
            )
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            return 2
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0
    else:
        return 1

    payload = handle_session_tool(
        name,
        arguments,
        service=service,
        workspace_id=runtime.workspace_id_for_service(service),
        envelope=envelope,
        blocked=blocked,
        bounded_int=bounded_int,
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


def _run_trace_command(args: argparse.Namespace) -> int:
    runtime = _workspace_runtime(args)
    if args.trace_command == "source":
        workspace = runtime.resolve_workspace(getattr(args, "workspace_id", None), getattr(args, "workspace", None))
        service = DataService(workspace)
        payload = source_trace_payload(
            service,
            getattr(args, "source_id", None),
            limit=getattr(args, "limit", 12),
        )
    else:
        return 1

    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


def _run_parsed_args(args: argparse.Namespace) -> int:
    if args.command == "workspace":
        return _run_workspace_command(args)
    if args.command == "source":
        return _run_source_command(args)
    if args.command == "build":
        return _run_build_command(args)
    if args.command == "graph":
        return _run_graph_command(args)
    if args.command == "trace":
        return _run_trace_command(args)
    if args.command == "code":
        return run_code_command(args)

    service = DataService(Path(args.workspace))

    if args.command == "ingest":
        plan = service.build_ingest_plan(
            args.paths,
            graphrag_execution_owner=GraphExecutionOwner(args.graphrag_owner),
        )
        service.write_summary_files(plan)
        results = service.run_default_pipeline_and_refresh_summary(plan)
        print(json.dumps(
            {
                "workspace": str(service.workspace),
                "results": [
                    {"engine": result.engine, "status": result.status, "meta": result.meta}
                    for result in results
                ],
                "summary": str(service.layout.summary_md),
            },
            ensure_ascii=False,
            indent=2,
        ))
        return 0

    if args.command == "summary":
        plan = service.build_ingest_plan([])
        service.write_summary_files(plan)
        print(service.layout.summary_md.read_text(encoding="utf-8"))
        return 0

    if args.command == "distill":
        print(json.dumps(
            run_distill_contract(
                service,
                source_id=getattr(args, "source_id", None),
                limit=getattr(args, "limit", 20),
                kind=getattr(args, "kind", None),
                typed_unit_type=getattr(args, "typed_unit_type", None),
                min_importance=getattr(args, "min_importance", 0.0),
                llm_enriched_only=getattr(args, "llm_enriched_only", False),
                authority=getattr(args, "authority", None),
                min_source_weight=getattr(args, "min_source_weight", 0.0),
                min_source_density=getattr(args, "min_source_density", 0.0),
            ),
            ensure_ascii=False,
            indent=2,
        ))
        return 0

    if args.command == "boundary":
        print(json.dumps(service.read_boundary_audit(), ensure_ascii=False, indent=2))
        return 0

    if args.command == "graphrag-execute":
        print(json.dumps(service.run_graphrag_execution_request(), ensure_ascii=False, indent=2))
        return 0

    if args.command == "query":
        print(json.dumps(
            run_query_contract(service, args.query, mode=args.mode, top_k=args.top_k),
            ensure_ascii=False,
            indent=2,
        ))
        return 0

    if args.command == "quality":
        if args.quality_command == "summary":
            payload = quality_summary_payload(service)
        elif args.quality_command == "correction-plan":
            payload = quality_correction_plan_preview_payload(service, rebuild=getattr(args, "rebuild", False))
        elif args.quality_command == "feedback-list":
            payload = quality_feedback_list_payload(
                service,
                limit=getattr(args, "limit", 100),
                target_type=getattr(args, "target_type", None),
                target_id=getattr(args, "target_id", None),
            )
        elif args.quality_command == "rules":
            payload = quality_correction_rules_payload(
                service,
                limit=getattr(args, "limit", 100),
                status=getattr(args, "status", None),
            )
        elif args.quality_command == "feedback":
            try:
                metadata = json.loads(getattr(args, "metadata_json", "{}") or "{}")
            except json.JSONDecodeError as exc:
                raise SystemExit(f"--metadata-json must be a JSON object: {exc}") from exc
            if not isinstance(metadata, dict):
                raise SystemExit("--metadata-json must be a JSON object")
            payload = record_quality_feedback_payload(
                service,
                target_type=getattr(args, "target_type", ""),
                target_id=getattr(args, "target_id", ""),
                action=getattr(args, "action", ""),
                label=getattr(args, "label", ""),
                suggested_value=getattr(args, "suggested_value", ""),
                reason=getattr(args, "reason", ""),
                metadata=metadata,
            )
        elif args.quality_command == "rules-build":
            payload = quality_correction_rules_build_payload(service)
        elif args.quality_command == "review":
            payload = quality_correction_rule_review_payload(
                service,
                rule_id=getattr(args, "rule_id", ""),
                status=getattr(args, "status", ""),
                reviewer=getattr(args, "reviewer", ""),
                note=getattr(args, "note", ""),
            )
        else:
            return 1
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    return 1


def main(argv: list[str] | None = None, *, prog: str = "data_service") -> int:
    return _run_parsed_args(_build_parser(prog=prog).parse_args(argv))


def knowledge_main(argv: list[str] | None = None) -> int:
    return _run_parsed_args(_build_knowledge_parser().parse_args(sys.argv[1:] if argv is None else argv))


if __name__ == "__main__":
    raise SystemExit(main())
