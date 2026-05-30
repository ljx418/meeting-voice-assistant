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


def run_code_command(args: argparse.Namespace) -> int:
    if args.code_command != "import":
        raise ValueError(f"Unknown code command: {args.code_command}")

    root = Path(args.workspace_root).expanduser() if getattr(args, "workspace_root", None) else None
    runtime = WorkspaceRuntime((root / "_default") if root else (Path.cwd() / "workspace"), workspace_root=root)
    try:
        metadata = json.loads(getattr(args, "metadata_json", "{}") or "{}")
        scan_policy = json.loads(getattr(args, "scan_policy_json", "{}") or "{}")
    except json.JSONDecodeError as exc:
        raise ValueError(f"metadata-json and scan-policy-json must be valid JSON objects: {exc}") from exc
    if not isinstance(metadata, dict) or not isinstance(scan_policy, dict):
        raise ValueError("metadata-json and scan-policy-json must be JSON objects")

    payload = handle_code_tool(
        "knowledge_codebase_import",
        {
            "workspace_id": getattr(args, "workspace_id", None),
            "path": getattr(args, "path", None),
            "codebase_id": getattr(args, "codebase_id", None),
            "name": getattr(args, "name", None),
            "metadata": metadata,
            "scan_policy": scan_policy,
        },
        blocked=blocked,
        envelope=envelope,
        ensure_workspace_meta=runtime.ensure_workspace_meta,
        resolve_workspace=runtime.resolve_workspace,
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0
