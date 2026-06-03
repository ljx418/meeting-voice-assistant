"""CLI subcommands for V2.1 Code Graph assets."""

from __future__ import annotations

import argparse


def add_graph_parser(code_subparsers: argparse._SubParsersAction) -> None:
    graph = code_subparsers.add_parser("graph", help="Build and read V2.1 Code Graph")
    subparsers = graph.add_subparsers(dest="code_graph_command", required=True)

    build = subparsers.add_parser("build", help="Build Code Graph")
    _add_common(build)
    build.add_argument("--snapshot-id", help="Optional snapshot identifier; defaults to latest")

    snapshot = subparsers.add_parser("snapshot", help="Read Code Graph")
    _add_common(snapshot)

    neighbors = subparsers.add_parser("neighbors", help="Read Code Graph neighbors")
    _add_common(neighbors)
    neighbors.add_argument("--node-id", required=True)
    neighbors.add_argument("--depth", type=int, default=1)
    neighbors.add_argument("--limit", type=int, default=100)

    mermaid = subparsers.add_parser("mermaid", help="Read Code Graph Mermaid export")
    _add_common(mermaid)


def graph_tool_payload(args: argparse.Namespace) -> tuple[str, dict]:
    if args.code_graph_command == "build":
        return "knowledge_code_graph_build", {"workspace_id": args.workspace_id, "codebase_id": args.codebase_id, "snapshot_id": getattr(args, "snapshot_id", None)}
    if args.code_graph_command == "snapshot":
        return "knowledge_code_graph_snapshot", {"workspace_id": args.workspace_id, "codebase_id": args.codebase_id}
    if args.code_graph_command == "neighbors":
        return "knowledge_code_graph_neighbors", {"workspace_id": args.workspace_id, "codebase_id": args.codebase_id, "node_id": args.node_id, "depth": args.depth, "limit": args.limit}
    if args.code_graph_command == "mermaid":
        return "knowledge_code_graph_mermaid", {"workspace_id": args.workspace_id, "codebase_id": args.codebase_id}
    raise ValueError(f"Unknown graph command: {args.code_graph_command}")


def _add_common(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--workspace-root", help="Managed workspace root; overrides DATA_SERVICE_WORKSPACE_ROOT for this command")
    parser.add_argument("--workspace-id", required=True)
    parser.add_argument("--codebase-id", required=True)
