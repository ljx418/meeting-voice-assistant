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
    service = CodingAgentActionabilityService(workspace_path, workspace_id=workspace_id)
    snapshot_id = str(arguments.get("snapshot_id") or "").strip() or None
    try:
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
