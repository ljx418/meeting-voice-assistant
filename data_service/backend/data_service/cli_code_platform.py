"""CLI subcommands for V2.18 Platform Product Console."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def add_platform_parser(code_subparsers: argparse._SubParsersAction) -> None:
    platform = code_subparsers.add_parser("platform", help="Build and read V2.18 Product Console")
    subparsers = platform.add_subparsers(dest="code_platform_command", required=True)
    for name, help_text in {
        "console-build": "Build V2.18 Product Console",
        "console": "Read V2.18 Product Console",
        "console-view": "Read V2.18 Product Console HTML view",
        "contracts-build": "Build V2.19 artifact contract registry",
        "contracts": "Read V2.19 artifact contract registry",
        "tool-catalog-build": "Build V2.20 MCP tool catalog",
        "tool-catalog": "Read V2.20 MCP tool catalog",
        "incremental-build": "Build V2.21 incremental build plan",
        "incremental": "Read V2.21 incremental build plan",
        "providers-build": "Build V2.22 provider plugin capabilities",
        "providers": "Read V2.22 provider plugin capabilities",
        "governance-feedback": "Record V2.23 platform governance feedback",
        "governance-rules-build": "Build V2.23 platform governance rules",
        "governance-rule-review": "Review or revoke a V2.23 platform governance rule",
        "governance-overlay": "Read V2.23 platform governance overlay report",
        "ci-readiness-build": "Build V2.24 CI readiness artifact",
        "ci-readiness": "Read V2.24 CI readiness artifact",
        "ci-release-report": "Read V2.24 release readiness Markdown report",
    }.items():
        parser = subparsers.add_parser(name, help=help_text)
        parser.add_argument("--workspace-root", help="Managed workspace root; overrides DATA_SERVICE_WORKSPACE_ROOT for this command")
        parser.add_argument("--workspace-id", required=True)
        parser.add_argument("--codebase-id", required=True)
        if name == "console-build":
            parser.add_argument("--snapshot-id")
        if name == "console-view":
            parser.add_argument("--view-id", default="html")
        if name == "incremental-build":
            parser.add_argument("--from-snapshot-id", required=True)
            parser.add_argument("--to-snapshot-id", required=True)
        if name == "providers-build":
            parser.add_argument("--snapshot-id")
        if name == "governance-feedback":
            parser.add_argument("--target-type", required=True)
            parser.add_argument("--target-id", required=True)
            parser.add_argument("--action", required=True)
            parser.add_argument("--rule-type", default="read_time_overlay")
            parser.add_argument("--severity", default="medium")
            parser.add_argument("--reason", default="")
            parser.add_argument("--suggested-value", default="")
        if name == "governance-rule-review":
            parser.add_argument("--rule-id", required=True)
            parser.add_argument("--status", required=True)
            parser.add_argument("--reviewer", default="")
            parser.add_argument("--note", default="")
        if name == "ci-readiness-build":
            parser.add_argument("--snapshot-id")
            parser.add_argument("--command-evidence-json", help="Path to command evidence JSON")
            parser.add_argument("--warning-budget", type=int, default=700)


def platform_tool_payload(args: argparse.Namespace) -> tuple[str, dict]:
    mapping = {
        "console-build": "knowledge_code_platform_console_build",
        "console": "knowledge_code_platform_console_read",
        "console-view": "knowledge_code_platform_console_view",
        "contracts-build": "knowledge_code_platform_contracts_build",
        "contracts": "knowledge_code_platform_contracts_read",
        "tool-catalog-build": "knowledge_code_platform_tool_catalog_build",
        "tool-catalog": "knowledge_code_platform_tool_catalog_read",
        "incremental-build": "knowledge_code_platform_incremental_build",
        "incremental": "knowledge_code_platform_incremental_read",
        "providers-build": "knowledge_code_platform_providers_build",
        "providers": "knowledge_code_platform_providers_read",
        "governance-feedback": "knowledge_code_platform_governance_feedback",
        "governance-rules-build": "knowledge_code_platform_governance_rules_build",
        "governance-rule-review": "knowledge_code_platform_governance_rule_review",
        "governance-overlay": "knowledge_code_platform_governance_overlay",
        "ci-readiness-build": "knowledge_code_platform_ci_readiness_build",
        "ci-readiness": "knowledge_code_platform_ci_readiness_read",
        "ci-release-report": "knowledge_code_platform_ci_release_report",
    }
    command = args.code_platform_command
    payload = {"workspace_id": args.workspace_id, "codebase_id": args.codebase_id}
    if command == "console-build":
        payload["snapshot_id"] = getattr(args, "snapshot_id", None)
    if command == "console-view":
        payload["view_id"] = getattr(args, "view_id", "html")
    if command == "incremental-build":
        payload["from_snapshot_id"] = getattr(args, "from_snapshot_id")
        payload["to_snapshot_id"] = getattr(args, "to_snapshot_id")
    if command == "providers-build":
        payload["snapshot_id"] = getattr(args, "snapshot_id", None)
    if command == "governance-feedback":
        payload.update(
            {
                "target_type": getattr(args, "target_type"),
                "target_id": getattr(args, "target_id"),
                "action": getattr(args, "action"),
                "rule_type": getattr(args, "rule_type", "read_time_overlay"),
                "severity": getattr(args, "severity", "medium"),
                "reason": getattr(args, "reason", ""),
                "suggested_value": getattr(args, "suggested_value", ""),
            }
        )
    if command == "governance-rule-review":
        payload.update(
            {
                "rule_id": getattr(args, "rule_id"),
                "status": getattr(args, "status"),
                "reviewer": getattr(args, "reviewer", ""),
                "note": getattr(args, "note", ""),
            }
        )
    if command == "ci-readiness-build":
        payload["snapshot_id"] = getattr(args, "snapshot_id", None)
        payload["warning_budget"] = getattr(args, "warning_budget", 700)
        evidence_path = getattr(args, "command_evidence_json", None)
        if evidence_path:
            payload["command_evidence"] = json.loads(Path(evidence_path).read_text(encoding="utf-8"))
    return mapping[command], payload
