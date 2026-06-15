"""CLI helpers for V2 codebase assets."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .cli_code_devwiki import add_devwiki_parser, devwiki_tool_payload
from .cli_code_graph import add_graph_parser, graph_tool_payload
from .cli_code_quality import add_quality_parser, quality_tool_payload
from .cli_code_architecture import add_architecture_parser, architecture_tool_payload
from .cli_code_architecture_intent import add_architecture_intent_parser, architecture_intent_tool_payload
from .cli_code_coding_agent import add_coding_agent_parser, coding_agent_tool_payload
from .cli_code_platform import add_platform_parser, platform_tool_payload
from .mcp_code_tools import handle_code_tool
from .mcp_common import blocked, envelope
from .mcp_workspace_runtime import WorkspaceRuntime


def add_code_parser(subparsers: argparse._SubParsersAction) -> None:
    code = subparsers.add_parser("code", help="Manage V2 codebase assets")
    code_subparsers = code.add_subparsers(dest="code_command", required=True)

    code_import = code_subparsers.add_parser("import", help="Import a local repository as a codebase asset")
    code_import.add_argument("--workspace-root", help="Managed workspace root; overrides DATA_SERVICE_WORKSPACE_ROOT for this command")
    code_import.add_argument("--workspace-id", required=True, help="Managed workspace identifier")
    code_import.add_argument("--path", required=True, help="Codebase root path")
    code_import.add_argument("--codebase-id", help="Optional stable codebase identifier")
    code_import.add_argument("--name", help="Optional codebase display name")
    code_import.add_argument("--metadata-json", default="{}", help="Optional JSON object metadata")
    code_import.add_argument("--scan-policy-json", default="{}", help="Optional JSON object scan policy")

    code_list = code_subparsers.add_parser("list", help="List codebase assets")
    code_list.add_argument("--workspace-root", help="Managed workspace root; overrides DATA_SERVICE_WORKSPACE_ROOT for this command")
    code_list.add_argument("--workspace-id", required=True, help="Managed workspace identifier")
    code_list.add_argument("--include-archived", action="store_true", help="Include archived codebase assets")
    code_list.add_argument("--limit", type=int, default=100, help="Max codebases to return")

    code_snapshot = code_subparsers.add_parser("snapshot", help="Generate a repo snapshot for a codebase asset")
    code_snapshot.add_argument("--workspace-root", help="Managed workspace root; overrides DATA_SERVICE_WORKSPACE_ROOT for this command")
    code_snapshot.add_argument("--workspace-id", required=True, help="Managed workspace identifier")
    code_snapshot.add_argument("--codebase-id", required=True, help="Codebase identifier")
    code_snapshot.add_argument("--scan-policy-json", default="{}", help="Optional JSON object scan policy override")
    code_snapshot.add_argument("--no-git", action="store_true", help="Skip git metadata collection")

    code_inventory = code_subparsers.add_parser("inventory", help="Build or read public surface inventory for a codebase asset")
    code_inventory.add_argument("--workspace-root", help="Managed workspace root; overrides DATA_SERVICE_WORKSPACE_ROOT for this command")
    code_inventory.add_argument("--workspace-id", required=True, help="Managed workspace identifier")
    code_inventory.add_argument("--codebase-id", required=True, help="Codebase identifier")
    code_inventory.add_argument("--snapshot-id", help="Optional snapshot identifier; defaults to latest")
    code_inventory.add_argument("--read-only", action="store_true", help="Read existing inventory instead of rebuilding it")

    code_symbols = code_subparsers.add_parser("symbols", help="Build or search Python symbols for a codebase asset")
    code_symbols.add_argument("--workspace-root", help="Managed workspace root; overrides DATA_SERVICE_WORKSPACE_ROOT for this command")
    code_symbols.add_argument("--workspace-id", required=True, help="Managed workspace identifier")
    code_symbols.add_argument("--codebase-id", required=True, help="Codebase identifier")
    code_symbols.add_argument("--snapshot-id", help="Optional snapshot identifier; defaults to latest")
    code_symbols.add_argument("--query", help="Optional symbol search query")
    code_symbols.add_argument("--kind", help="Optional symbol kind filter")
    code_symbols.add_argument("--limit", type=int, default=20, help="Max symbols to return")
    code_symbols.add_argument("--build", action="store_true", help="Build or refresh the symbol index before searching")

    code_trace = code_subparsers.add_parser("trace", help="Build or read evidence trace for public surfaces and capabilities")
    code_trace.add_argument("--workspace-root", help="Managed workspace root; overrides DATA_SERVICE_WORKSPACE_ROOT for this command")
    code_trace.add_argument("--workspace-id", required=True, help="Managed workspace identifier")
    code_trace.add_argument("--codebase-id", required=True, help="Codebase identifier")
    code_trace.add_argument("--snapshot-id", help="Optional snapshot identifier; defaults to latest")
    code_trace.add_argument("--surface-id", help="Optional surface identifier to trace")
    code_trace.add_argument("--capability", help="Optional capability identifier to trace")
    code_trace.add_argument("--limit", type=int, default=50, help="Max evidence items to return")
    code_trace.add_argument("--build", action="store_true", help="Build or refresh trace artifacts before reading")

    code_overview = code_subparsers.add_parser("overview", help="Generate or read an evidence-backed project overview")
    code_overview.add_argument("--workspace-root", help="Managed workspace root; overrides DATA_SERVICE_WORKSPACE_ROOT for this command")
    code_overview.add_argument("--workspace-id", required=True, help="Managed workspace identifier")
    code_overview.add_argument("--codebase-id", required=True, help="Codebase identifier")
    code_overview.add_argument("--snapshot-id", help="Optional snapshot identifier; defaults to latest")

    code_context = code_subparsers.add_parser("context-pack", help="Generate or read an evidence-backed Agent Context Pack")
    code_context.add_argument("--workspace-root", help="Managed workspace root; overrides DATA_SERVICE_WORKSPACE_ROOT for this command")
    code_context.add_argument("--workspace-id", required=True, help="Managed workspace identifier")
    code_context.add_argument("--codebase-id", required=True, help="Codebase identifier")
    code_context.add_argument("--snapshot-id", help="Optional snapshot identifier; defaults to latest")
    code_context.add_argument("--pack-id", help="Read an existing context pack by id")
    code_context.add_argument("--mode", choices=["project_brief", "task_context"], help="Context mode")
    code_context.add_argument("--task", help="Task text for task_context")
    code_context.add_argument("--format", choices=["json", "markdown"], default="json", help="Output format")
    code_context.add_argument("--max-tokens", type=int, default=16000, help="Maximum approximate context tokens")
    code_context.add_argument("--focus-json", default="{}", help="Optional JSON object focus hints")
    code_context.add_argument("--include-json", default="[]", help="Optional JSON array of section names to include")

    add_devwiki_parser(code_subparsers)
    add_graph_parser(code_subparsers)
    add_quality_parser(code_subparsers)
    add_architecture_parser(code_subparsers)
    add_architecture_intent_parser(code_subparsers)
    add_coding_agent_parser(code_subparsers)
    add_platform_parser(code_subparsers)

    code_describe = code_subparsers.add_parser("describe", help="Describe one codebase asset")
    code_describe.add_argument("--workspace-root", help="Managed workspace root; overrides DATA_SERVICE_WORKSPACE_ROOT for this command")
    code_describe.add_argument("--workspace-id", required=True, help="Managed workspace identifier")
    code_describe.add_argument("--codebase-id", required=True, help="Codebase identifier")

    code_archive = code_subparsers.add_parser("archive", help="Archive one codebase asset")
    code_archive.add_argument("--workspace-root", help="Managed workspace root; overrides DATA_SERVICE_WORKSPACE_ROOT for this command")
    code_archive.add_argument("--workspace-id", required=True, help="Managed workspace identifier")
    code_archive.add_argument("--codebase-id", required=True, help="Codebase identifier")
    code_archive.add_argument("--reason", default="", help="Optional archive reason")


def run_code_command(args: argparse.Namespace) -> int:
    if args.code_command not in {"import", "list", "snapshot", "inventory", "symbols", "trace", "overview", "context-pack", "devwiki", "graph", "quality", "architecture", "architecture-intent", "coding-agent", "platform", "describe", "archive"}:
        raise ValueError(f"Unknown code command: {args.code_command}")

    root = Path(args.workspace_root).expanduser() if getattr(args, "workspace_root", None) else None
    runtime = WorkspaceRuntime((root / "_default") if root else (Path.cwd() / "workspace"), workspace_root=root)
    if args.code_command == "import":
        try:
            metadata = json.loads(getattr(args, "metadata_json", "{}") or "{}")
            scan_policy = json.loads(getattr(args, "scan_policy_json", "{}") or "{}")
        except json.JSONDecodeError as exc:
            raise ValueError(f"metadata-json and scan-policy-json must be valid JSON objects: {exc}") from exc
        if not isinstance(metadata, dict) or not isinstance(scan_policy, dict):
            raise ValueError("metadata-json and scan-policy-json must be JSON objects")
        tool_name = "knowledge_codebase_import"
        payload_args = {
            "workspace_id": getattr(args, "workspace_id", None),
            "path": getattr(args, "path", None),
            "codebase_id": getattr(args, "codebase_id", None),
            "name": getattr(args, "name", None),
            "metadata": metadata,
            "scan_policy": scan_policy,
        }
    elif args.code_command == "list":
        tool_name = "knowledge_codebase_list"
        payload_args = {
            "workspace_id": getattr(args, "workspace_id", None),
            "include_archived": getattr(args, "include_archived", False),
            "limit": getattr(args, "limit", 100),
        }
    elif args.code_command == "snapshot":
        try:
            scan_policy = json.loads(getattr(args, "scan_policy_json", "{}") or "{}")
        except json.JSONDecodeError as exc:
            raise ValueError(f"scan-policy-json must be a valid JSON object: {exc}") from exc
        if not isinstance(scan_policy, dict):
            raise ValueError("scan-policy-json must be a JSON object")
        tool_name = "knowledge_codebase_snapshot"
        payload_args = {
            "workspace_id": getattr(args, "workspace_id", None),
            "codebase_id": getattr(args, "codebase_id", None),
            "scan_policy": scan_policy,
            "include_git": not getattr(args, "no_git", False),
        }
    elif args.code_command == "inventory":
        tool_name = "knowledge_project_inventory"
        payload_args = {
            "workspace_id": getattr(args, "workspace_id", None),
            "codebase_id": getattr(args, "codebase_id", None),
            "snapshot_id": getattr(args, "snapshot_id", None),
            "build": not getattr(args, "read_only", False),
        }
    elif args.code_command == "symbols":
        tool_name = "knowledge_code_symbol_search"
        payload_args = {
            "workspace_id": getattr(args, "workspace_id", None),
            "codebase_id": getattr(args, "codebase_id", None),
            "snapshot_id": getattr(args, "snapshot_id", None),
            "query": getattr(args, "query", None),
            "kind": getattr(args, "kind", None),
            "limit": getattr(args, "limit", 20),
            "build": getattr(args, "build", False),
        }
    elif args.code_command == "trace":
        tool_name = "knowledge_public_surface_trace"
        payload_args = {
            "workspace_id": getattr(args, "workspace_id", None),
            "codebase_id": getattr(args, "codebase_id", None),
            "snapshot_id": getattr(args, "snapshot_id", None),
            "surface_id": getattr(args, "surface_id", None),
            "capability": getattr(args, "capability", None),
            "limit": getattr(args, "limit", 50),
            "build": getattr(args, "build", False),
        }
    elif args.code_command == "overview":
        tool_name = "knowledge_project_overview"
        payload_args = {
            "workspace_id": getattr(args, "workspace_id", None),
            "codebase_id": getattr(args, "codebase_id", None),
            "snapshot_id": getattr(args, "snapshot_id", None),
        }
    elif args.code_command == "context-pack":
        try:
            focus = json.loads(getattr(args, "focus_json", "{}") or "{}")
            include = json.loads(getattr(args, "include_json", "[]") or "[]")
        except json.JSONDecodeError as exc:
            raise ValueError(f"focus-json and include-json must be valid JSON: {exc}") from exc
        if not isinstance(focus, dict):
            raise ValueError("focus-json must be a JSON object")
        if not isinstance(include, list):
            raise ValueError("include-json must be a JSON array")
        tool_name = "knowledge_agent_context_pack"
        payload_args = {
            "workspace_id": getattr(args, "workspace_id", None),
            "codebase_id": getattr(args, "codebase_id", None),
            "snapshot_id": getattr(args, "snapshot_id", None),
            "pack_id": getattr(args, "pack_id", None),
            "mode": getattr(args, "mode", None),
            "task": getattr(args, "task", None),
            "format": getattr(args, "format", "json"),
            "max_tokens": getattr(args, "max_tokens", 16000),
            "focus": focus,
            "include": include,
        }
    elif args.code_command == "devwiki":
        tool_name, payload_args = devwiki_tool_payload(args)
    elif args.code_command == "graph":
        tool_name, payload_args = graph_tool_payload(args)
    elif args.code_command == "quality":
        tool_name, payload_args = quality_tool_payload(args)
    elif args.code_command == "architecture":
        tool_name, payload_args = architecture_tool_payload(args)
    elif args.code_command == "architecture-intent":
        tool_name, payload_args = architecture_intent_tool_payload(args)
    elif args.code_command == "coding-agent":
        tool_name, payload_args = coding_agent_tool_payload(args)
    elif args.code_command == "platform":
        tool_name, payload_args = platform_tool_payload(args)
    elif args.code_command == "describe":
        tool_name = "knowledge_codebase_describe"
        payload_args = {
            "workspace_id": getattr(args, "workspace_id", None),
            "codebase_id": getattr(args, "codebase_id", None),
        }
    else:
        tool_name = "knowledge_codebase_archive"
        payload_args = {
            "workspace_id": getattr(args, "workspace_id", None),
            "codebase_id": getattr(args, "codebase_id", None),
            "reason": getattr(args, "reason", ""),
        }

    payload = handle_code_tool(
        tool_name,
        payload_args,
        blocked=blocked,
        envelope=envelope,
        ensure_workspace_meta=runtime.ensure_workspace_meta,
        resolve_workspace=runtime.resolve_workspace,
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0
