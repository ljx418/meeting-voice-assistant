"""MCP tools for V2.11 Coding Agent actionability."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from .code_assets.coding_agent.persistence import actionability_artifact_refs
from .code_assets.coding_agent.service import (
    CodingAgentActionabilityService,
    public_large_project_advisor_payload,
    public_actionability_payload,
    public_impact_payload,
    public_incremental_diff_payload,
    public_incremental_timeline_payload,
    public_patch_plan_payload,
    public_patch_preview_payload,
    public_provider_registry_payload,
    public_runtime_registry_payload,
    public_runtime_profile_run_payload,
    public_runtime_profiles_payload,
    public_runtime_run_payload,
    public_semantic_payload,
    public_task_plan_payload,
    public_workbench_context_export_payload,
    public_workbench_payload,
    public_workbench_v2_payload,
    public_workbench_view_payload,
)
from .code_assets.coding_agent_navigation.service import (
    CodingAgentNavigationService,
    public_task_navigation_index_payload,
    public_task_navigation_query_payload,
    public_task_handoff_payload,
    public_task_impact_payload,
    public_task_reading_pack_payload,
    public_task_closure_payload,
    public_task_relationship_graph_payload,
    public_task_test_selection_payload,
    task_impact_refs,
    task_handoff_refs,
    task_closure_refs,
    task_navigation_refs,
    task_query_refs,
    task_reading_pack_refs,
    task_relationship_refs,
)
from .code_assets.envelope import v2_error_envelope, v2_success_envelope


CODING_AGENT_TOOL_NAMES = {
    "knowledge_code_provider_registry_build",
    "knowledge_code_provider_registry_read",
    "knowledge_code_semantic_providers_build",
    "knowledge_code_semantic_providers_read",
    "knowledge_code_actionability_build",
    "knowledge_code_actionability_read",
    "knowledge_code_impact_analyze",
    "knowledge_code_task_plan",
    "knowledge_code_patch_plan_create",
    "knowledge_code_patch_plan_read",
    "knowledge_code_patch_preview_create",
    "knowledge_code_patch_preview_read",
    "knowledge_code_patch_preview_apply",
    "knowledge_code_runtime_commands",
    "knowledge_code_runtime_run",
    "knowledge_code_runtime_result",
    "knowledge_code_runtime_profiles_build",
    "knowledge_code_runtime_profiles_read",
    "knowledge_code_runtime_profile_run",
    "knowledge_code_runtime_profile_result",
    "knowledge_code_incremental_diff",
    "knowledge_code_incremental_diff_read",
    "knowledge_code_drift_timeline",
    "knowledge_code_workbench_build",
    "knowledge_code_workbench_read",
    "knowledge_code_workbench_view",
    "knowledge_code_workbench_context_export",
    "knowledge_code_workbench_v2_build",
    "knowledge_code_workbench_v2_read",
    "knowledge_code_workbench_v2_view",
    "knowledge_code_large_project_advisor_build",
    "knowledge_code_large_project_advisor_read",
    "knowledge_code_task_navigation_build",
    "knowledge_code_task_navigation_read",
    "knowledge_code_task_navigation_prepare",
    "knowledge_code_task_navigation_query_read",
    "knowledge_code_task_relationships_build",
    "knowledge_code_task_relationships_read",
    "knowledge_code_task_impact_analyze",
    "knowledge_code_task_impact_read",
    "knowledge_code_module_reading_pack",
    "knowledge_code_module_reading_pack_read",
    "knowledge_code_agent_handoff",
    "knowledge_code_agent_handoff_read",
    "knowledge_code_task_navigation_closure_build",
    "knowledge_code_task_navigation_closure_read",
    "knowledge_code_task_navigation_closure_view",
}


CODING_AGENT_TOOL_SPECS = [
    {
        "name": "knowledge_code_provider_registry_build",
        "description": "Build V2.16 Coding Agent provider capability registry and decision records",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}, "snapshot_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_provider_registry_read",
        "description": "Read V2.16 Coding Agent provider capability registry",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_semantic_providers_build",
        "description": "Build V2.16 semantic provider facts and merged semantic index",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}, "snapshot_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_semantic_providers_read",
        "description": "Read V2.16 semantic provider facts and merged semantic index",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_actionability_build",
        "description": "Build V2.11 Coding Agent actionability index from deterministic code facts",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}, "snapshot_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_actionability_read",
        "description": "Read V2.11 Coding Agent actionability index",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_impact_analyze",
        "description": "Analyze likely impacted files, symbols, and tests for a coding task",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}, "task": {"type": "string"}, "snapshot_id": {"type": "string"}, "focus_paths": {"type": "array", "items": {"type": "string"}}}, "required": ["workspace_id", "codebase_id", "task"]},
    },
    {
        "name": "knowledge_code_task_plan",
        "description": "Create evidence-backed advisory edit plan for a coding task without mutating files",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}, "task": {"type": "string"}, "snapshot_id": {"type": "string"}, "focus_paths": {"type": "array", "items": {"type": "string"}}, "max_items": {"type": "integer", "default": 12}}, "required": ["workspace_id", "codebase_id", "task"]},
    },
    {
        "name": "knowledge_code_patch_plan_create",
        "description": "Create a V2.12 read-only safe patch plan with edit candidates, patch options, validation descriptors, rollback, readiness, and evidence",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}, "task": {"type": "string"}, "snapshot_id": {"type": "string"}, "task_plan_id": {"type": "string"}, "focus_paths": {"type": "array", "items": {"type": "string"}}, "max_options": {"type": "integer", "default": 3}}, "required": ["workspace_id", "codebase_id", "task"]},
    },
    {
        "name": "knowledge_code_patch_plan_read",
        "description": "Read a persisted V2.12 safe patch plan",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}, "patch_plan_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id", "patch_plan_id"]},
    },
    {
        "name": "knowledge_code_patch_preview_create",
        "description": "Create V2.16 human-gated read-only patch preview",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}, "task": {"type": "string"}, "snapshot_id": {"type": "string"}, "patch_plan_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_patch_preview_read",
        "description": "Read V2.16 human-gated patch preview",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}, "preview_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id", "preview_id"]},
    },
    {
        "name": "knowledge_code_patch_preview_apply",
        "description": "Attempt V2.16 patch preview apply; blocked without human approval",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}, "preview_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id", "preview_id"]},
    },
    {
        "name": "knowledge_code_runtime_commands",
        "description": "Build/read V2.13 allowlisted controlled runtime command registry",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}, "snapshot_id": {"type": "string"}, "patch_plan_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_runtime_run",
        "description": "Run one allowlisted V2.13 runtime command by command_id and persist redacted evidence",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}, "command_id": {"type": "string"}, "snapshot_id": {"type": "string"}, "patch_plan_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id", "command_id"]},
    },
    {
        "name": "knowledge_code_runtime_result",
        "description": "Read a persisted V2.13 runtime run result",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}, "run_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id", "run_id"]},
    },
    {
        "name": "knowledge_code_runtime_profiles_build",
        "description": "Build V2.16 runtime profiles from allowlisted runtime commands",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}, "snapshot_id": {"type": "string"}, "patch_plan_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_runtime_profiles_read",
        "description": "Read V2.16 runtime profiles",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_runtime_profile_run",
        "description": "Run one registered V2.16 runtime profile",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}, "profile_id": {"type": "string"}, "snapshot_id": {"type": "string"}, "patch_plan_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id", "profile_id"]},
    },
    {
        "name": "knowledge_code_runtime_profile_result",
        "description": "Read a persisted V2.16 runtime profile run",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}, "profile_run_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id", "profile_run_id"]},
    },
    {
        "name": "knowledge_code_incremental_diff",
        "description": "Build V2.14 snapshot diff, fingerprint index, task memory, and drift timeline",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}, "from_snapshot_id": {"type": "string"}, "to_snapshot_id": {"type": "string"}, "task": {"type": "string"}}, "required": ["workspace_id", "codebase_id", "from_snapshot_id", "to_snapshot_id"]},
    },
    {
        "name": "knowledge_code_incremental_diff_read",
        "description": "Read a persisted V2.14 snapshot diff",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}, "diff_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id", "diff_id"]},
    },
    {
        "name": "knowledge_code_drift_timeline",
        "description": "Read V2.14 drift timeline events",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_workbench_build",
        "description": "Build V2.15 interactive review workbench JSON, HTML, and Mermaid views",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}, "snapshot_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_workbench_read",
        "description": "Read V2.15 interactive review workbench payload",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_workbench_view",
        "description": "Read V2.15 HTML or Mermaid workbench view",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}, "view_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id", "view_id"]},
    },
    {
        "name": "knowledge_code_workbench_context_export",
        "description": "Create V2.15 context export from persisted workbench evidence",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}, "mode": {"type": "string"}, "max_items": {"type": "integer"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_workbench_v2_build",
        "description": "Build V2.16 human-readable Coding Agent workbench v2",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}, "snapshot_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_workbench_v2_read",
        "description": "Read V2.16 Coding Agent workbench v2 payload",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_workbench_v2_view",
        "description": "Read V2.16 Coding Agent workbench v2 HTML or Mermaid view",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}, "view_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id", "view_id"]},
    },
    {
        "name": "knowledge_code_large_project_advisor_build",
        "description": "Build V2.16 generic large-project abstraction advisor",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}, "snapshot_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_large_project_advisor_read",
        "description": "Read V2.16 generic large-project abstraction advisor",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_task_navigation_build",
        "description": "Build V2.31 task-aware navigation index from deterministic project facts",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}, "snapshot_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_task_navigation_read",
        "description": "Read V2.31 task-aware navigation index",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_task_navigation_prepare",
        "description": "Prepare V2.31 task-aware navigation candidates for a coding task",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}, "snapshot_id": {"type": "string"}, "task": {"type": "string"}, "limit": {"type": "integer", "default": 25}}, "required": ["workspace_id", "codebase_id", "task"]},
    },
    {
        "name": "knowledge_code_task_navigation_query_read",
        "description": "Read one persisted V2.31 task navigation query artifact",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}, "task_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id", "task_id"]},
    },
    {
        "name": "knowledge_code_task_relationships_build",
        "description": "Build V2.32 lightweight coding-agent relationship graph",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}, "snapshot_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_task_relationships_read",
        "description": "Read V2.32 lightweight coding-agent relationship graph",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_task_impact_analyze",
        "description": "Build V2.33 task change impact analysis and test selection",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}, "snapshot_id": {"type": "string"}, "task": {"type": "string"}, "task_id": {"type": "string"}, "max_items": {"type": "integer", "default": 50}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_task_impact_read",
        "description": "Read V2.33 task impact analysis and test selection by task_id",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}, "task_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id", "task_id"]},
    },
    {
        "name": "knowledge_code_module_reading_pack",
        "description": "Build V2.34 module reading pack and token ledger for a coding task",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}, "snapshot_id": {"type": "string"}, "task": {"type": "string"}, "task_id": {"type": "string"}, "max_tokens": {"type": "integer", "default": 12000}, "role": {"type": "string", "default": "coding_agent"}, "max_items": {"type": "integer", "default": 50}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_module_reading_pack_read",
        "description": "Read one persisted V2.34 module reading pack and token ledger",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}, "pack_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id", "pack_id"]},
    },
    {
        "name": "knowledge_code_agent_handoff",
        "description": "Build V2.35 Coding Agent handoff contract for Copilot/Codex/Claude/generic agents",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}, "target_agent": {"type": "string", "default": "generic"}, "pack_id": {"type": "string"}, "snapshot_id": {"type": "string"}, "task": {"type": "string"}, "task_id": {"type": "string"}, "max_tokens": {"type": "integer", "default": 12000}, "max_items": {"type": "integer", "default": 50}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_agent_handoff_read",
        "description": "Read one persisted V2.35 Coding Agent handoff artifact",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}, "handoff_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id", "handoff_id"]},
    },
    {
        "name": "knowledge_code_task_navigation_closure_build",
        "description": "Build V2.36 task navigation closure report, HTML, Mermaid, coverage, and governance artifacts",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}, "handoff_id": {"type": "string"}, "snapshot_id": {"type": "string"}, "task": {"type": "string"}, "task_id": {"type": "string"}, "max_tokens": {"type": "integer", "default": 12000}, "max_items": {"type": "integer", "default": 50}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_task_navigation_closure_read",
        "description": "Read V2.36 task navigation closure bundle",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_task_navigation_closure_view",
        "description": "Read V2.36 task navigation closure HTML or Mermaid view",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}, "view_id": {"type": "string", "default": "html"}}, "required": ["workspace_id", "codebase_id"]},
    },
]


def handle_coding_agent_tool(name: str, arguments: dict[str, Any], *, blocked: Callable[..., dict[str, Any]], envelope: Callable[..., dict[str, Any]], ensure_workspace_meta: Callable[..., dict[str, Any]], resolve_workspace: Callable[[str | None, str | None], Path]) -> dict[str, Any]:
    if name not in CODING_AGENT_TOOL_NAMES:
        raise ValueError(f"Unknown coding agent tool: {name}")
    workspace_path = resolve_workspace(arguments.get("workspace_id"), None)
    meta = ensure_workspace_meta(workspace_path)
    workspace_id = str(meta["workspace_id"])
    codebase_id = str(arguments.get("codebase_id") or "").strip()
    if not codebase_id:
        return blocked(workspace_id=workspace_id, message="codebase_id is required", next_actions=["knowledge_codebase_list"], code="invalid_codebase_id")
    navigation_service = CodingAgentNavigationService(workspace_path, workspace_id=workspace_id)
    service = CodingAgentActionabilityService(workspace_path, workspace_id=workspace_id)
    snapshot_id = str(arguments.get("snapshot_id") or "").strip() or None
    try:
        if name == "knowledge_code_task_navigation_build":
            payload = navigation_service.build_navigation_index(codebase_id, snapshot_id=snapshot_id)
            refs = task_navigation_refs(codebase_id)
            data = {"task_navigation_index": public_task_navigation_index_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=refs, next_actions=["knowledge_code_task_navigation_prepare"], data=_with_v2(workspace_id, codebase_id, payload.get("snapshot_id"), data, refs))
        if name == "knowledge_code_task_navigation_read":
            payload = navigation_service.read_navigation_index(codebase_id)
            refs = task_navigation_refs(codebase_id)
            data = {"task_navigation_index": public_task_navigation_index_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=refs, data=_with_v2(workspace_id, codebase_id, payload.get("snapshot_id"), data, refs))
        if name == "knowledge_code_task_navigation_prepare":
            payload = navigation_service.prepare_task_navigation(codebase_id, task=str(arguments.get("task") or ""), snapshot_id=snapshot_id, limit=int(arguments.get("limit") or 25))
            refs = task_query_refs(codebase_id, str(payload.get("task_id")))
            data = {"task_navigation_query": public_task_navigation_query_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=refs, next_actions=["knowledge_code_task_navigation_query_read"], data=_with_v2(workspace_id, codebase_id, payload.get("snapshot_id"), data, refs))
        if name == "knowledge_code_task_navigation_query_read":
            task_id = str(arguments.get("task_id") or "").strip()
            if not task_id:
                return envelope(workspace_id=workspace_id, status="blocked", warnings=["task_id is required"], data={"error": {"code": "invalid_task_id", "message": "task_id is required", "retryable": False}})
            payload = navigation_service.read_task_query(codebase_id, task_id)
            refs = task_query_refs(codebase_id, task_id)
            data = {"task_navigation_query": public_task_navigation_query_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=refs, data=_with_v2(workspace_id, codebase_id, payload.get("snapshot_id"), data, refs))
        if name == "knowledge_code_task_relationships_build":
            payload = navigation_service.build_relationship_graph(codebase_id, snapshot_id=snapshot_id)
            refs = task_relationship_refs(codebase_id)
            data = {"relationship_graph": public_task_relationship_graph_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=refs, next_actions=["knowledge_code_task_relationships_read"], data=_with_v2(workspace_id, codebase_id, payload.get("snapshot_id"), data, refs))
        if name == "knowledge_code_task_relationships_read":
            payload = navigation_service.read_relationship_graph(codebase_id)
            refs = task_relationship_refs(codebase_id)
            data = {"relationship_graph": public_task_relationship_graph_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=refs, data=_with_v2(workspace_id, codebase_id, payload.get("snapshot_id"), data, refs))
        if name == "knowledge_code_task_impact_analyze":
            impact, test_selection = navigation_service.build_impact_analysis(
                codebase_id,
                task=str(arguments.get("task") or ""),
                task_id=str(arguments.get("task_id") or "").strip() or None,
                snapshot_id=snapshot_id,
                max_items=int(arguments.get("max_items") or 50),
            )
            refs = task_impact_refs(codebase_id, str(impact.get("task_id")))
            data = {"impact_analysis": public_task_impact_payload(impact), "test_selection": public_task_test_selection_payload(test_selection)}
            return envelope(workspace_id=workspace_id, artifact_refs=refs, next_actions=["knowledge_code_task_impact_read"], data=_with_v2(workspace_id, codebase_id, impact.get("snapshot_id"), data, refs))
        if name == "knowledge_code_task_impact_read":
            task_id = str(arguments.get("task_id") or "").strip()
            if not task_id:
                return envelope(workspace_id=workspace_id, status="blocked", warnings=["task_id is required"], data={"error": {"code": "invalid_task_id", "message": "task_id is required", "retryable": False}})
            impact, test_selection = navigation_service.read_impact_analysis(codebase_id, task_id)
            refs = task_impact_refs(codebase_id, task_id)
            data = {"impact_analysis": public_task_impact_payload(impact), "test_selection": public_task_test_selection_payload(test_selection)}
            return envelope(workspace_id=workspace_id, artifact_refs=refs, data=_with_v2(workspace_id, codebase_id, impact.get("snapshot_id"), data, refs))
        if name == "knowledge_code_module_reading_pack":
            pack, markdown, ledger = navigation_service.build_reading_pack(
                codebase_id,
                task=str(arguments.get("task") or "") or None,
                task_id=str(arguments.get("task_id") or "").strip() or None,
                snapshot_id=snapshot_id,
                max_tokens=int(arguments.get("max_tokens") or 12000),
                role=str(arguments.get("role") or "coding_agent"),
                max_items=int(arguments.get("max_items") or 50),
            )
            refs = task_reading_pack_refs(codebase_id, str(pack.get("pack_id")))
            data = {"reading_pack": public_task_reading_pack_payload(pack), "markdown": markdown, "token_ledger": ledger}
            return envelope(workspace_id=workspace_id, artifact_refs=refs, next_actions=["knowledge_code_module_reading_pack_read"], data=_with_v2(workspace_id, codebase_id, pack.get("snapshot_id"), data, refs))
        if name == "knowledge_code_module_reading_pack_read":
            pack_id = str(arguments.get("pack_id") or "").strip()
            if not pack_id:
                return envelope(workspace_id=workspace_id, status="blocked", warnings=["pack_id is required"], data={"error": {"code": "invalid_pack_id", "message": "pack_id is required", "retryable": False}})
            pack, markdown, ledger = navigation_service.read_reading_pack(codebase_id, pack_id)
            refs = task_reading_pack_refs(codebase_id, pack_id)
            data = {"reading_pack": public_task_reading_pack_payload(pack), "markdown": markdown, "token_ledger": ledger}
            return envelope(workspace_id=workspace_id, artifact_refs=refs, data=_with_v2(workspace_id, codebase_id, pack.get("snapshot_id"), data, refs))
        if name == "knowledge_code_agent_handoff":
            payload = navigation_service.build_agent_handoff(
                codebase_id,
                target_agent=str(arguments.get("target_agent") or "generic"),
                pack_id=str(arguments.get("pack_id") or "").strip() or None,
                task=str(arguments.get("task") or "") or None,
                task_id=str(arguments.get("task_id") or "").strip() or None,
                snapshot_id=snapshot_id,
                max_tokens=int(arguments.get("max_tokens") or 12000),
                max_items=int(arguments.get("max_items") or 50),
            )
            refs = list(payload.get("artifact_refs") or task_handoff_refs(codebase_id, str(payload.get("handoff_id"))))
            data = {"agent_handoff": public_task_handoff_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=refs, next_actions=["knowledge_code_agent_handoff_read"], data=_with_v2(workspace_id, codebase_id, payload.get("snapshot_id"), data, refs))
        if name == "knowledge_code_agent_handoff_read":
            handoff_id = str(arguments.get("handoff_id") or "").strip()
            if not handoff_id:
                return envelope(workspace_id=workspace_id, status="blocked", warnings=["handoff_id is required"], data={"error": {"code": "invalid_handoff_id", "message": "handoff_id is required", "retryable": False}})
            payload = navigation_service.read_agent_handoff(codebase_id, handoff_id)
            refs = list(payload.get("artifact_refs") or task_handoff_refs(codebase_id, handoff_id))
            data = {"agent_handoff": public_task_handoff_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=refs, data=_with_v2(workspace_id, codebase_id, payload.get("snapshot_id"), data, refs))
        if name == "knowledge_code_task_navigation_closure_build":
            report, html, mermaid, coverage, governance, audit = navigation_service.build_closure_report(
                codebase_id,
                handoff_id=str(arguments.get("handoff_id") or "").strip() or None,
                task=str(arguments.get("task") or "") or None,
                task_id=str(arguments.get("task_id") or "").strip() or None,
                snapshot_id=snapshot_id,
                max_tokens=int(arguments.get("max_tokens") or 12000),
                max_items=int(arguments.get("max_items") or 50),
            )
            refs = task_closure_refs(codebase_id)
            data = {"closure_report": public_task_closure_payload(report), "html": html, "mermaid": mermaid, "coverage_matrix": coverage, "governance_targets": governance, "closure_audit": audit}
            return envelope(workspace_id=workspace_id, artifact_refs=refs, next_actions=["knowledge_code_task_navigation_closure_read"], data=_with_v2(workspace_id, codebase_id, report.get("snapshot_id"), data, refs))
        if name == "knowledge_code_task_navigation_closure_read":
            report, html, mermaid, coverage, governance, audit = navigation_service.read_closure_report(codebase_id)
            refs = task_closure_refs(codebase_id)
            data = {"closure_report": public_task_closure_payload(report), "html": html, "mermaid": mermaid, "coverage_matrix": coverage, "governance_targets": governance, "closure_audit": audit}
            return envelope(workspace_id=workspace_id, artifact_refs=refs, data=_with_v2(workspace_id, codebase_id, report.get("snapshot_id"), data, refs))
        if name == "knowledge_code_task_navigation_closure_view":
            payload = navigation_service.read_closure_view(codebase_id, str(arguments.get("view_id") or "html"))
            refs = task_closure_refs(codebase_id)
            data = {"closure_view": payload}
            return envelope(workspace_id=workspace_id, artifact_refs=refs, data=_with_v2(workspace_id, codebase_id, None, data, refs))
        if name == "knowledge_code_provider_registry_build":
            payload = service.build_provider_registry(codebase_id, snapshot_id=snapshot_id)
            data = {"provider_registry": public_provider_registry_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=payload.get("artifact_refs", []), next_actions=["knowledge_code_provider_registry_read"], data=_with_v2(workspace_id, codebase_id, payload.get("snapshot_id"), data, payload.get("artifact_refs", [])))
        if name == "knowledge_code_provider_registry_read":
            payload = service.read_provider_registry(codebase_id)
            data = {"provider_registry": public_provider_registry_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=payload.get("artifact_refs", []), data=_with_v2(workspace_id, codebase_id, payload.get("snapshot_id"), data, payload.get("artifact_refs", [])))
        if name == "knowledge_code_semantic_providers_build":
            payload = service.build_semantic_provider_index(codebase_id, snapshot_id=snapshot_id)
            data = {"semantic_provider_index": public_semantic_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=payload.get("artifact_refs", []), next_actions=["knowledge_code_semantic_providers_read"], data=_with_v2(workspace_id, codebase_id, payload["index"].get("snapshot_id"), data, payload.get("artifact_refs", [])))
        if name == "knowledge_code_semantic_providers_read":
            payload = service.read_semantic_provider_index(codebase_id)
            data = {"semantic_provider_index": public_semantic_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=payload.get("artifact_refs", []), data=_with_v2(workspace_id, codebase_id, payload["index"].get("snapshot_id"), data, payload.get("artifact_refs", [])))
        if name == "knowledge_code_actionability_build":
            payload = service.build_actionability(codebase_id, snapshot_id=snapshot_id)
            refs = actionability_artifact_refs(codebase_id)
            data = {"actionability": public_actionability_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=refs, next_actions=["knowledge_code_actionability_read"], data=_with_v2(workspace_id, codebase_id, payload["index"].get("snapshot_id"), data, refs))
        if name == "knowledge_code_actionability_read":
            payload = service.read_actionability(codebase_id)
            refs = actionability_artifact_refs(codebase_id)
            data = {"actionability": public_actionability_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=refs, data=_with_v2(workspace_id, codebase_id, payload["index"].get("snapshot_id"), data, refs))
        if name == "knowledge_code_impact_analyze":
            payload = service.analyze_impact(codebase_id, task=str(arguments.get("task") or ""), focus_paths=list(arguments.get("focus_paths") or []), snapshot_id=snapshot_id)
            data = {"impact": public_impact_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=payload.get("artifact_refs", []), next_actions=["knowledge_code_task_plan"], data=_with_v2(workspace_id, codebase_id, payload.get("snapshot_id"), data, payload.get("artifact_refs", [])))
        if name == "knowledge_code_task_plan":
            payload = service.create_task_plan(codebase_id, task=str(arguments.get("task") or ""), focus_paths=list(arguments.get("focus_paths") or []), max_items=int(arguments.get("max_items") or 12), snapshot_id=snapshot_id)
            data = {"task_plan": public_task_plan_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=payload.get("artifact_refs", []), data=_with_v2(workspace_id, codebase_id, payload.get("snapshot_id"), data, payload.get("artifact_refs", [])))
        if name == "knowledge_code_patch_plan_create":
            payload = service.create_patch_plan(codebase_id, task=str(arguments.get("task") or ""), focus_paths=list(arguments.get("focus_paths") or []), max_options=int(arguments.get("max_options") or 3), snapshot_id=snapshot_id, task_plan_id=str(arguments.get("task_plan_id") or "").strip() or None)
            data = {"patch_plan": public_patch_plan_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=payload.get("artifact_refs", []), next_actions=["knowledge_code_patch_plan_read"], data=_with_v2(workspace_id, codebase_id, payload.get("snapshot_id"), data, payload.get("artifact_refs", [])))
        if name == "knowledge_code_patch_preview_create":
            payload = service.create_patch_preview(codebase_id, task=str(arguments.get("task") or ""), patch_plan_id=str(arguments.get("patch_plan_id") or "").strip() or None, snapshot_id=snapshot_id)
            data = {"patch_preview": public_patch_preview_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=payload.get("artifact_refs", []), next_actions=["knowledge_code_patch_preview_read"], data=_with_v2(workspace_id, codebase_id, payload.get("snapshot_id"), data, payload.get("artifact_refs", [])))
        if name == "knowledge_code_patch_preview_read":
            payload = service.read_patch_preview(codebase_id, str(arguments.get("preview_id") or ""))
            data = {"patch_preview": public_patch_preview_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=payload.get("artifact_refs", []), data=_with_v2(workspace_id, codebase_id, payload.get("snapshot_id"), data, payload.get("artifact_refs", [])))
        if name == "knowledge_code_patch_preview_apply":
            payload = service.apply_patch_preview(codebase_id, str(arguments.get("preview_id") or ""))
            data = {"patch_apply": payload}
            return envelope(workspace_id=workspace_id, status="blocked", artifact_refs=payload.get("artifact_refs", []), data=_with_v2(workspace_id, codebase_id, None, data, payload.get("artifact_refs", [])))
        if name == "knowledge_code_runtime_commands":
            payload = service.build_runtime_registry(codebase_id, snapshot_id=snapshot_id, patch_plan_id=str(arguments.get("patch_plan_id") or "").strip() or None)
            data = {"runtime_commands": public_runtime_registry_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=payload.get("artifact_refs", []), data=_with_v2(workspace_id, codebase_id, payload.get("snapshot_id"), data, payload.get("artifact_refs", [])))
        if name == "knowledge_code_runtime_run":
            payload = service.run_runtime_command(codebase_id, command_id=str(arguments.get("command_id") or ""), patch_plan_id=str(arguments.get("patch_plan_id") or "").strip() or None, snapshot_id=snapshot_id)
            data = {"runtime_run": public_runtime_run_payload(payload)}
            return envelope(workspace_id=workspace_id, status=payload.get("status", "ok"), artifact_refs=payload.get("artifact_refs", []), data=_with_v2(workspace_id, codebase_id, payload.get("snapshot_id"), data, payload.get("artifact_refs", [])))
        if name == "knowledge_code_runtime_result":
            run_id = str(arguments.get("run_id") or "").strip()
            if not run_id:
                return envelope(workspace_id=workspace_id, status="blocked", warnings=["run_id is required"], data={"error": {"code": "invalid_run_id", "message": "run_id is required", "retryable": False}})
            payload = service.read_runtime_run(codebase_id, run_id)
            data = {"runtime_run": public_runtime_run_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=payload.get("artifact_refs", []), data=_with_v2(workspace_id, codebase_id, payload.get("snapshot_id"), data, payload.get("artifact_refs", [])))
        if name == "knowledge_code_runtime_profiles_build":
            payload = service.build_runtime_profiles(codebase_id, snapshot_id=snapshot_id, patch_plan_id=str(arguments.get("patch_plan_id") or "").strip() or None)
            data = {"runtime_profiles": public_runtime_profiles_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=payload.get("artifact_refs", []), next_actions=["knowledge_code_runtime_profiles_read"], data=_with_v2(workspace_id, codebase_id, payload.get("snapshot_id"), data, payload.get("artifact_refs", [])))
        if name == "knowledge_code_runtime_profiles_read":
            payload = service.read_runtime_profiles_v2_16(codebase_id)
            data = {"runtime_profiles": public_runtime_profiles_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=payload.get("artifact_refs", []), data=_with_v2(workspace_id, codebase_id, payload.get("snapshot_id"), data, payload.get("artifact_refs", [])))
        if name == "knowledge_code_runtime_profile_run":
            payload = service.run_runtime_profile(codebase_id, profile_id=str(arguments.get("profile_id") or ""), patch_plan_id=str(arguments.get("patch_plan_id") or "").strip() or None, snapshot_id=snapshot_id)
            data = {"runtime_profile_run": public_runtime_profile_run_payload(payload)}
            return envelope(workspace_id=workspace_id, status=payload.get("status", "ok"), artifact_refs=payload.get("artifact_refs", []), data=_with_v2(workspace_id, codebase_id, payload.get("snapshot_id"), data, payload.get("artifact_refs", [])))
        if name == "knowledge_code_runtime_profile_result":
            profile_run_id = str(arguments.get("profile_run_id") or "").strip()
            if not profile_run_id:
                return envelope(workspace_id=workspace_id, status="blocked", warnings=["profile_run_id is required"], data={"error": {"code": "invalid_profile_run_id", "message": "profile_run_id is required", "retryable": False}})
            payload = service.read_runtime_profile_run(codebase_id, profile_run_id)
            data = {"runtime_profile_run": public_runtime_profile_run_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=payload.get("artifact_refs", []), data=_with_v2(workspace_id, codebase_id, payload.get("snapshot_id"), data, payload.get("artifact_refs", [])))
        if name == "knowledge_code_incremental_diff":
            payload = service.build_incremental_diff(codebase_id, from_snapshot_id=str(arguments.get("from_snapshot_id") or ""), to_snapshot_id=str(arguments.get("to_snapshot_id") or ""), task=str(arguments.get("task") or "") or None)
            data = {"incremental_diff": public_incremental_diff_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=payload.get("artifact_refs", []), data=_with_v2(workspace_id, codebase_id, payload.get("to_snapshot_id"), data, payload.get("artifact_refs", [])))
        if name == "knowledge_code_incremental_diff_read":
            diff_id = str(arguments.get("diff_id") or "").strip()
            if not diff_id:
                return envelope(workspace_id=workspace_id, status="blocked", warnings=["diff_id is required"], data={"error": {"code": "invalid_diff_id", "message": "diff_id is required", "retryable": False}})
            payload = service.read_incremental_diff(codebase_id, diff_id)
            data = {"incremental_diff": public_incremental_diff_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=payload.get("artifact_refs", []), data=_with_v2(workspace_id, codebase_id, payload.get("to_snapshot_id"), data, payload.get("artifact_refs", [])))
        if name == "knowledge_code_drift_timeline":
            payload = service.read_incremental_timeline(codebase_id)
            data = {"drift_timeline": public_incremental_timeline_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=payload.get("artifact_refs", []), data=_with_v2(workspace_id, codebase_id, None, data, payload.get("artifact_refs", [])))
        if name == "knowledge_code_workbench_build":
            payload = service.build_workbench(codebase_id, snapshot_id=snapshot_id)
            data = {"workbench": public_workbench_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=payload.get("artifact_refs", []), data=_with_v2(workspace_id, codebase_id, payload.get("snapshot_id"), data, payload.get("artifact_refs", [])))
        if name == "knowledge_code_workbench_read":
            payload = service.read_workbench(codebase_id)
            data = {"workbench": public_workbench_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=payload.get("artifact_refs", []), data=_with_v2(workspace_id, codebase_id, payload.get("snapshot_id"), data, payload.get("artifact_refs", [])))
        if name == "knowledge_code_workbench_view":
            payload = service.read_workbench_view(codebase_id, str(arguments.get("view_id") or "html"))
            data = {"workbench_view": public_workbench_view_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=payload.get("artifact_refs", []), data=_with_v2(workspace_id, codebase_id, None, data, payload.get("artifact_refs", [])))
        if name == "knowledge_code_workbench_context_export":
            payload = service.create_workbench_context_export(codebase_id, mode=str(arguments.get("mode") or "coding_agent"), max_items=int(arguments.get("max_items") or 25))
            data = {"context_export": public_workbench_context_export_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=payload.get("artifact_refs", []), data=_with_v2(workspace_id, codebase_id, payload.get("snapshot_id"), data, payload.get("artifact_refs", [])))
        if name == "knowledge_code_workbench_v2_build":
            payload = service.build_workbench_v2(codebase_id, snapshot_id=snapshot_id)
            data = {"workbench_v2": public_workbench_v2_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=payload.get("artifact_refs", []), next_actions=["knowledge_code_workbench_v2_read"], data=_with_v2(workspace_id, codebase_id, payload.get("snapshot_id"), data, payload.get("artifact_refs", [])))
        if name == "knowledge_code_workbench_v2_read":
            payload = service.read_workbench_v2(codebase_id)
            data = {"workbench_v2": public_workbench_v2_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=payload.get("artifact_refs", []), data=_with_v2(workspace_id, codebase_id, payload.get("snapshot_id"), data, payload.get("artifact_refs", [])))
        if name == "knowledge_code_workbench_v2_view":
            payload = service.read_workbench_v2_view(codebase_id, str(arguments.get("view_id") or "html"))
            data = {"workbench_v2_view": payload}
            return envelope(workspace_id=workspace_id, artifact_refs=payload.get("artifact_refs", []), data=_with_v2(workspace_id, codebase_id, None, data, payload.get("artifact_refs", [])))
        if name == "knowledge_code_large_project_advisor_build":
            payload = service.build_large_project_advisor(codebase_id, snapshot_id=snapshot_id)
            data = {"large_project_advisor": public_large_project_advisor_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=payload.get("artifact_refs", []), next_actions=["knowledge_code_large_project_advisor_read"], data=_with_v2(workspace_id, codebase_id, payload.get("snapshot_id"), data, payload.get("artifact_refs", [])))
        if name == "knowledge_code_large_project_advisor_read":
            payload = service.read_large_project_advisor(codebase_id)
            data = {"large_project_advisor": public_large_project_advisor_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=payload.get("artifact_refs", []), data=_with_v2(workspace_id, codebase_id, payload.get("snapshot_id"), data, payload.get("artifact_refs", [])))
        patch_plan_id = str(arguments.get("patch_plan_id") or "").strip()
        if not patch_plan_id:
            return envelope(workspace_id=workspace_id, status="blocked", warnings=["patch_plan_id is required"], data={"error": {"code": "invalid_patch_plan_id", "message": "patch_plan_id is required", "retryable": False}})
        payload = service.read_patch_plan(codebase_id, patch_plan_id)
        data = {"patch_plan": public_patch_plan_payload(payload)}
        return envelope(workspace_id=workspace_id, artifact_refs=payload.get("artifact_refs", []), data=_with_v2(workspace_id, codebase_id, payload.get("snapshot_id"), data, payload.get("artifact_refs", [])))
    except FileNotFoundError as exc:
        return envelope(workspace_id=workspace_id, status="blocked", warnings=[str(exc)], next_actions=["knowledge_codebase_snapshot"], data={"error": {"code": str(exc), "message": str(exc), "retryable": False}, "v2": v2_error_envelope(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, code=str(exc), message=str(exc))})


def _with_v2(workspace_id: str, codebase_id: str, snapshot_id: str | None, data: dict[str, Any], refs: list[dict[str, Any]]) -> dict[str, Any]:
    payload = dict(data)
    payload["v2"] = v2_success_envelope(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, data=data, artifact_refs=refs)
    return payload
