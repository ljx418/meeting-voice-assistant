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
    }.items():
        parser = subparsers.add_parser(name, help=help_text)
        _add_common(parser)
        if name in {"scan", "build", "code-build"}:
            parser.add_argument("--snapshot-id", help="Optional snapshot identifier; defaults to latest")
        if name == "view":
            parser.add_argument("--view-id", default="architecture.html")
        if name == "code-view":
            parser.add_argument("--view-id", default="code_derived_architecture.html")


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
    }
    command = args.code_architecture_command
    payload = {"workspace_id": args.workspace_id, "codebase_id": args.codebase_id}
    if command in {"scan", "build", "code-build"}:
        payload["snapshot_id"] = getattr(args, "snapshot_id", None)
    if command in {"view", "code-view"}:
        payload["view_id"] = getattr(args, "view_id", "architecture.html")
    return mapping[command], payload


def _add_common(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--workspace-root", help="Managed workspace root; overrides DATA_SERVICE_WORKSPACE_ROOT for this command")
    parser.add_argument("--workspace-id", required=True)
    parser.add_argument("--codebase-id", required=True)
