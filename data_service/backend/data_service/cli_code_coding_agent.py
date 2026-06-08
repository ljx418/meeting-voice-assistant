"""CLI subcommands for V2.11 Coding Agent actionability."""

from __future__ import annotations

import argparse


def add_coding_agent_parser(code_subparsers: argparse._SubParsersAction) -> None:
    coding_agent = code_subparsers.add_parser("coding-agent", help="Build and read V2.11 Coding Agent actionability")
    subparsers = coding_agent.add_subparsers(dest="code_coding_agent_command", required=True)
    for name, help_text in {
        "providers-build": "Build V2.16 provider capability registry",
        "providers": "Read V2.16 provider capability registry",
        "semantic-build": "Build V2.16 semantic provider index",
        "semantic": "Read V2.16 semantic provider index",
        "actionability-build": "Build V2.11 actionability index",
        "actionability": "Read V2.11 actionability index",
        "impact": "Analyze likely impacted files and tests",
        "task-plan": "Create an evidence-backed advisory edit plan",
        "patch-plan": "Create a V2.12 read-only safe patch plan",
        "patch-plan-read": "Read a V2.12 safe patch plan",
        "patch-preview": "Create V2.16 read-only patch preview",
        "patch-preview-read": "Read V2.16 patch preview",
        "patch-preview-apply": "Attempt V2.16 patch preview apply; blocked without approval",
        "runtime-commands": "Build/read V2.13 controlled runtime command registry",
        "runtime-run": "Run one allowlisted V2.13 runtime command",
        "runtime-result": "Read a V2.13 runtime run result",
        "runtime-profiles-build": "Build V2.16 runtime profiles",
        "runtime-profiles": "Read V2.16 runtime profiles",
        "runtime-profile-run": "Run one V2.16 runtime profile",
        "runtime-profile-result": "Read a V2.16 runtime profile run",
        "incremental-diff": "Build V2.14 snapshot diff and drift timeline",
        "incremental-read": "Read a V2.14 snapshot diff",
        "incremental-timeline": "Read V2.14 drift timeline",
        "workbench-build": "Build V2.15 review workbench",
        "workbench-read": "Read V2.15 review workbench",
        "workbench-view": "Read V2.15 workbench HTML or Mermaid view",
        "workbench-context-export": "Create V2.15 workbench context export",
        "workbench-v2-build": "Build V2.16 review workbench v2",
        "workbench-v2-read": "Read V2.16 review workbench v2",
        "workbench-v2-view": "Read V2.16 workbench v2 HTML or Mermaid view",
        "large-project-advisor-build": "Build V2.16 large-project advisor",
        "large-project-advisor": "Read V2.16 large-project advisor",
    }.items():
        parser = subparsers.add_parser(name, help=help_text)
        parser.add_argument("--workspace-root", help="Managed workspace root; overrides DATA_SERVICE_WORKSPACE_ROOT for this command")
        parser.add_argument("--workspace-id", required=True)
        parser.add_argument("--codebase-id", required=True)
        if name in {"providers-build", "semantic-build", "actionability-build", "impact", "task-plan", "patch-plan", "patch-preview", "runtime-commands", "runtime-run", "runtime-profiles-build", "runtime-profile-run", "workbench-build", "workbench-v2-build", "large-project-advisor-build"}:
            parser.add_argument("--snapshot-id")
        if name in {"impact", "task-plan", "patch-plan", "patch-preview"}:
            parser.add_argument("--task", required=name != "patch-preview")
            parser.add_argument("--focus-path", action="append", default=[])
        if name == "task-plan":
            parser.add_argument("--max-items", type=int, default=12)
        if name == "patch-plan":
            parser.add_argument("--task-plan-id")
            parser.add_argument("--max-options", type=int, default=3)
        if name == "patch-plan-read":
            parser.add_argument("--patch-plan-id", required=True)
        if name == "patch-preview":
            parser.add_argument("--patch-plan-id")
        if name in {"patch-preview-read", "patch-preview-apply"}:
            parser.add_argument("--preview-id", required=True)
        if name in {"runtime-commands", "runtime-run", "runtime-profiles-build", "runtime-profile-run"}:
            parser.add_argument("--patch-plan-id")
        if name == "runtime-run":
            parser.add_argument("--command-id", required=True)
        if name == "runtime-result":
            parser.add_argument("--run-id", required=True)
        if name == "runtime-profile-run":
            parser.add_argument("--profile-id", required=True)
        if name == "runtime-profile-result":
            parser.add_argument("--profile-run-id", required=True)
        if name == "incremental-diff":
            parser.add_argument("--from-snapshot-id", required=True)
            parser.add_argument("--to-snapshot-id", required=True)
            parser.add_argument("--task")
        if name == "incremental-read":
            parser.add_argument("--diff-id", required=True)
        if name in {"workbench-view", "workbench-v2-view"}:
            parser.add_argument("--view-id", default="html")
        if name == "workbench-context-export":
            parser.add_argument("--mode", default="coding_agent")
            parser.add_argument("--max-items", type=int, default=25)


def coding_agent_tool_payload(args: argparse.Namespace) -> tuple[str, dict]:
    mapping = {
        "providers-build": "knowledge_code_provider_registry_build",
        "providers": "knowledge_code_provider_registry_read",
        "semantic-build": "knowledge_code_semantic_providers_build",
        "semantic": "knowledge_code_semantic_providers_read",
        "actionability-build": "knowledge_code_actionability_build",
        "actionability": "knowledge_code_actionability_read",
        "impact": "knowledge_code_impact_analyze",
        "task-plan": "knowledge_code_task_plan",
        "patch-plan": "knowledge_code_patch_plan_create",
        "patch-plan-read": "knowledge_code_patch_plan_read",
        "patch-preview": "knowledge_code_patch_preview_create",
        "patch-preview-read": "knowledge_code_patch_preview_read",
        "patch-preview-apply": "knowledge_code_patch_preview_apply",
        "runtime-commands": "knowledge_code_runtime_commands",
        "runtime-run": "knowledge_code_runtime_run",
        "runtime-result": "knowledge_code_runtime_result",
        "runtime-profiles-build": "knowledge_code_runtime_profiles_build",
        "runtime-profiles": "knowledge_code_runtime_profiles_read",
        "runtime-profile-run": "knowledge_code_runtime_profile_run",
        "runtime-profile-result": "knowledge_code_runtime_profile_result",
        "incremental-diff": "knowledge_code_incremental_diff",
        "incremental-read": "knowledge_code_incremental_diff_read",
        "incremental-timeline": "knowledge_code_drift_timeline",
        "workbench-build": "knowledge_code_workbench_build",
        "workbench-read": "knowledge_code_workbench_read",
        "workbench-view": "knowledge_code_workbench_view",
        "workbench-context-export": "knowledge_code_workbench_context_export",
        "workbench-v2-build": "knowledge_code_workbench_v2_build",
        "workbench-v2-read": "knowledge_code_workbench_v2_read",
        "workbench-v2-view": "knowledge_code_workbench_v2_view",
        "large-project-advisor-build": "knowledge_code_large_project_advisor_build",
        "large-project-advisor": "knowledge_code_large_project_advisor_read",
    }
    command = args.code_coding_agent_command
    payload = {"workspace_id": args.workspace_id, "codebase_id": args.codebase_id}
    if command in {"providers-build", "semantic-build", "actionability-build", "impact", "task-plan", "patch-plan", "patch-preview", "runtime-commands", "runtime-run", "runtime-profiles-build", "runtime-profile-run", "workbench-build", "workbench-v2-build", "large-project-advisor-build"}:
        payload["snapshot_id"] = getattr(args, "snapshot_id", None)
    if command in {"impact", "task-plan", "patch-plan", "patch-preview"}:
        payload["task"] = getattr(args, "task", "") or ""
        payload["focus_paths"] = getattr(args, "focus_path", []) or []
    if command == "task-plan":
        payload["max_items"] = getattr(args, "max_items", 12)
    if command == "patch-plan":
        payload["task_plan_id"] = getattr(args, "task_plan_id", None)
        payload["max_options"] = getattr(args, "max_options", 3)
    if command == "patch-plan-read":
        payload["patch_plan_id"] = getattr(args, "patch_plan_id")
    if command == "patch-preview":
        payload["patch_plan_id"] = getattr(args, "patch_plan_id", None)
    if command in {"patch-preview-read", "patch-preview-apply"}:
        payload["preview_id"] = getattr(args, "preview_id")
    if command in {"runtime-commands", "runtime-run", "runtime-profiles-build", "runtime-profile-run"}:
        payload["patch_plan_id"] = getattr(args, "patch_plan_id", None)
    if command == "runtime-run":
        payload["command_id"] = getattr(args, "command_id")
    if command == "runtime-result":
        payload["run_id"] = getattr(args, "run_id")
    if command == "runtime-profile-run":
        payload["profile_id"] = getattr(args, "profile_id")
    if command == "runtime-profile-result":
        payload["profile_run_id"] = getattr(args, "profile_run_id")
    if command == "incremental-diff":
        payload["from_snapshot_id"] = getattr(args, "from_snapshot_id")
        payload["to_snapshot_id"] = getattr(args, "to_snapshot_id")
        payload["task"] = getattr(args, "task", None)
    if command == "incremental-read":
        payload["diff_id"] = getattr(args, "diff_id")
    if command in {"workbench-view", "workbench-v2-view"}:
        payload["view_id"] = getattr(args, "view_id", "html")
    if command == "workbench-context-export":
        payload["mode"] = getattr(args, "mode", "coding_agent")
        payload["max_items"] = getattr(args, "max_items", 25)
    return mapping[command], payload
