"""CLI subcommands for V2.1 code quality governance."""

from __future__ import annotations

import argparse
import json


def add_quality_parser(code_subparsers: argparse._SubParsersAction) -> None:
    quality = code_subparsers.add_parser("quality", help="Govern V2.1 code quality artifacts")
    subparsers = quality.add_subparsers(dest="code_quality_command", required=True)

    feedback = subparsers.add_parser("feedback", help="Record code quality feedback")
    _add_common(feedback)
    feedback.add_argument("--target-type", required=True)
    feedback.add_argument("--target-id", required=True)
    feedback.add_argument("--action", required=True)
    feedback.add_argument("--rule-type", required=True)
    feedback.add_argument("--severity", default="medium")
    feedback.add_argument("--reason", default="")
    feedback.add_argument("--suggested-value", default="")
    feedback.add_argument("--metadata-json", default="{}")

    summary = subparsers.add_parser("summary", help="Read code quality summary")
    _add_common(summary)

    rules = subparsers.add_parser("rules", help="Build code quality rules")
    rules_subparsers = rules.add_subparsers(dest="code_quality_rules_command", required=True)
    rules_build = rules_subparsers.add_parser("build", help="Build draft rules")
    _add_common(rules_build)

    rule = subparsers.add_parser("rule", help="Review one code quality rule")
    rule_subparsers = rule.add_subparsers(dest="code_quality_rule_command", required=True)
    rule_review = rule_subparsers.add_parser("review", help="Approve, reject, or revoke a rule")
    _add_common(rule_review)
    rule_review.add_argument("--rule-id", required=True)
    rule_review.add_argument("--status", required=True, choices=["approved", "rejected", "revoked"])
    rule_review.add_argument("--reviewer", default="")
    rule_review.add_argument("--note", default="")

    plan = subparsers.add_parser("plan", help="Build code quality plan")
    _add_common(plan)


def quality_tool_payload(args: argparse.Namespace) -> tuple[str, dict]:
    if args.code_quality_command == "feedback":
        metadata = json.loads(getattr(args, "metadata_json", "{}") or "{}")
        if not isinstance(metadata, dict):
            raise ValueError("metadata-json must be a JSON object")
        return (
            "knowledge_code_quality_feedback",
            {
                "workspace_id": args.workspace_id,
                "codebase_id": args.codebase_id,
                "target_type": args.target_type,
                "target_id": args.target_id,
                "action": args.action,
                "rule_type": args.rule_type,
                "severity": args.severity,
                "reason": args.reason,
                "suggested_value": args.suggested_value,
                "metadata": metadata,
            },
        )
    if args.code_quality_command == "summary":
        return "knowledge_code_quality_summary", {"workspace_id": args.workspace_id, "codebase_id": args.codebase_id}
    if args.code_quality_command == "rules" and args.code_quality_rules_command == "build":
        return "knowledge_code_quality_rules_build", {"workspace_id": args.workspace_id, "codebase_id": args.codebase_id}
    if args.code_quality_command == "rule" and args.code_quality_rule_command == "review":
        return (
            "knowledge_code_quality_rule_review",
            {
                "workspace_id": args.workspace_id,
                "codebase_id": args.codebase_id,
                "rule_id": args.rule_id,
                "status": args.status,
                "reviewer": args.reviewer,
                "note": args.note,
            },
        )
    if args.code_quality_command == "plan":
        return "knowledge_code_quality_plan", {"workspace_id": args.workspace_id, "codebase_id": args.codebase_id}
    raise ValueError(f"Unknown quality command: {args.code_quality_command}")


def _add_common(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--workspace-root", help="Managed workspace root; overrides DATA_SERVICE_WORKSPACE_ROOT for this command")
    parser.add_argument("--workspace-id", required=True)
    parser.add_argument("--codebase-id", required=True)
