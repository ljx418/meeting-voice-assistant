"""CLI subcommands for V2.25-V2.30 architecture intent public contracts."""

from __future__ import annotations

import argparse


def add_architecture_intent_parser(code_subparsers: argparse._SubParsersAction) -> None:
    intent = code_subparsers.add_parser("architecture-intent", help="Build and read V2.25-V2.30 architecture intent artifacts")
    subparsers = intent.add_subparsers(dest="code_architecture_intent_command", required=True)
    for name, help_text in {
        "build": "Build architecture intent artifacts",
        "report": "Read Architecture Intent report",
        "context-pack": "Read Architecture Context Pack v4",
        "verification": "Read diagram-to-code verification",
        "proof-graph": "Read architecture proof graph",
        "governance": "Read governance overlay",
        "confirm": "Confirm architecture target as read-time overlay",
        "revoke": "Revoke architecture target confirmation",
    }.items():
        parser = subparsers.add_parser(name, help=help_text)
        parser.add_argument("--workspace-root", help="Managed workspace root; overrides DATA_SERVICE_WORKSPACE_ROOT for this command")
        parser.add_argument("--workspace-id", required=True)
        parser.add_argument("--codebase-id", required=True)
        if name == "build":
            parser.add_argument("--snapshot-id")
            parser.add_argument("--mode", default="architecture_review")
        if name in {"confirm", "revoke"}:
            parser.add_argument("--snapshot-id")
            parser.add_argument("--target-type", required=True)
            parser.add_argument("--target-id", required=True)
            parser.add_argument("--note", default="")
            parser.add_argument("--reviewer", default="local")


def architecture_intent_tool_payload(args: argparse.Namespace) -> tuple[str, dict]:
    mapping = {
        "build": "knowledge_architecture_intent_build",
        "report": "knowledge_architecture_intent_report",
        "context-pack": "knowledge_architecture_context_pack_v4",
        "verification": "knowledge_diagram_code_verification",
        "proof-graph": "knowledge_architecture_proof_graph",
        "governance": "knowledge_architecture_intent_governance",
        "confirm": "knowledge_architecture_intent_confirm",
        "revoke": "knowledge_architecture_intent_revoke",
    }
    command = args.code_architecture_intent_command
    payload = {"workspace_id": args.workspace_id, "codebase_id": args.codebase_id}
    if command == "build":
        payload["snapshot_id"] = getattr(args, "snapshot_id", None)
        payload["mode"] = getattr(args, "mode", "architecture_review")
    if command in {"confirm", "revoke"}:
        payload.update(
            {
                "snapshot_id": getattr(args, "snapshot_id", None),
                "target_type": getattr(args, "target_type"),
                "target_id": getattr(args, "target_id"),
                "note": getattr(args, "note", ""),
                "reviewer": getattr(args, "reviewer", "local"),
            }
        )
    return mapping[command], payload
