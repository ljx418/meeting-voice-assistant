"""CLI helpers for V2 codebase assets."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

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
    if args.code_command not in {"import", "list", "snapshot", "describe", "archive"}:
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
