"""CLI subcommands for V2.1 DevWiki code assets."""

from __future__ import annotations

import argparse


def add_devwiki_parser(code_subparsers: argparse._SubParsersAction) -> None:
    devwiki = code_subparsers.add_parser("devwiki", help="Build and read V2.1 DevWiki pages")
    subparsers = devwiki.add_subparsers(dest="devwiki_command", required=True)

    build = subparsers.add_parser("build", help="Build DevWiki pages from accepted V2.0 artifacts")
    _add_common(build)
    build.add_argument("--snapshot-id", help="Optional snapshot identifier; defaults to latest")

    pages = subparsers.add_parser("pages", help="List DevWiki pages")
    _add_common(pages)

    read = subparsers.add_parser("read", help="Read one DevWiki page")
    _add_common(read)
    read.add_argument("--page-slug", required=True, help="DevWiki page slug")


def devwiki_tool_payload(args: argparse.Namespace) -> tuple[str, dict]:
    if args.devwiki_command == "build":
        return (
            "knowledge_devwiki_build",
            {
                "workspace_id": getattr(args, "workspace_id", None),
                "codebase_id": getattr(args, "codebase_id", None),
                "snapshot_id": getattr(args, "snapshot_id", None),
            },
        )
    if args.devwiki_command == "pages":
        return (
            "knowledge_devwiki_read",
            {
                "workspace_id": getattr(args, "workspace_id", None),
                "codebase_id": getattr(args, "codebase_id", None),
            },
        )
    if args.devwiki_command == "read":
        return (
            "knowledge_devwiki_read",
            {
                "workspace_id": getattr(args, "workspace_id", None),
                "codebase_id": getattr(args, "codebase_id", None),
                "page_slug": getattr(args, "page_slug", None),
            },
        )
    raise ValueError(f"Unknown devwiki command: {args.devwiki_command}")


def _add_common(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--workspace-root", help="Managed workspace root; overrides DATA_SERVICE_WORKSPACE_ROOT for this command")
    parser.add_argument("--workspace-id", required=True, help="Managed workspace identifier")
    parser.add_argument("--codebase-id", required=True, help="Codebase identifier")
