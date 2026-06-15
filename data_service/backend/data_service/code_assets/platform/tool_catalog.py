"""V2.20 MCP tool catalog and workflow guide builder."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from data_service.mcp_common import now

from ..registry import CodebaseRegistry
from .persistence import (
    read_tool_catalog,
    read_workflow_guides,
    tool_catalog_artifact_refs,
    write_tool_catalog,
)


TOOL_CATALOG_SCHEMA_VERSION = "v2.20"


class ToolCatalogService:
    def __init__(self, workspace: Path, *, workspace_id: str) -> None:
        self.workspace = workspace
        self.workspace_id = workspace_id
        self.registry = CodebaseRegistry(workspace, workspace_id=workspace_id)

    def build_tool_catalog(self, codebase_id: str, tool_specs: list[dict[str, Any]]) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        tools = [_tool_entry(spec) for spec in sorted(tool_specs, key=lambda item: str(item.get("name") or ""))]
        tool_names = {item["tool_name"] for item in tools}
        groups = _groups(tools)
        guides = _workflow_guides(self.workspace_id, codebase_id, tool_names)
        refs = tool_catalog_artifact_refs(codebase_id)
        missing_refs = sorted(
            {
                tool
                for guide in guides["guides"]
                for step in guide["steps"]
                for tool in [step["tool_name"]]
                if tool not in tool_names
            }
        )
        catalog = {
            "schema_version": TOOL_CATALOG_SCHEMA_VERSION,
            "artifact_type": "mcp_tool_catalog",
            "workspace_id": self.workspace_id,
            "codebase_id": codebase_id,
            "generated_at": now(),
            "tool_count": len(tools),
            "group_count": len(groups),
            "groups": groups,
            "tools": tools,
            "validation_summary": {
                "registry_count": len(tool_specs),
                "catalog_count": len(tools),
                "missing_workflow_tool_count": len(missing_refs),
            },
            "artifact_refs": refs,
        }
        guides["validation_summary"] = {
            "guide_count": len(guides["guides"]),
            "missing_tool_refs": missing_refs,
        }
        guides["artifact_refs"] = refs
        write_tool_catalog(self.workspace, codebase_id, catalog, guides)
        return {"catalog": catalog, "workflow_guides": guides, "artifact_refs": refs}

    def read_tool_catalog(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        return {
            "catalog": read_tool_catalog(self.workspace, codebase_id),
            "workflow_guides": read_workflow_guides(self.workspace, codebase_id),
            "artifact_refs": tool_catalog_artifact_refs(codebase_id),
        }


def public_tool_catalog_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": TOOL_CATALOG_SCHEMA_VERSION,
        "artifact_type": "mcp_tool_catalog_bundle",
        "catalog": payload.get("catalog", {}),
        "workflow_guides": payload.get("workflow_guides", {}),
        "artifact_refs": payload.get("artifact_refs", []),
    }


def _tool_entry(spec: dict[str, Any]) -> dict[str, Any]:
    name = str(spec.get("name") or "")
    schema = spec.get("inputSchema") or {}
    required = list(schema.get("required") or [])
    properties = schema.get("properties") or {}
    optional = sorted(str(key) for key in properties if key not in required)
    return {
        "tool_name": name,
        "group_id": _group_for(name),
        "description": str(spec.get("description") or ""),
        "required_inputs": sorted(str(item) for item in required),
        "optional_inputs": optional,
        "goal_tags": _goal_tags(name),
        "outputs": _outputs(name),
        "failure_modes": _failure_modes(name),
    }


def _group_for(name: str) -> str:
    if name.startswith("knowledge_code_platform_"):
        return "platform"
    if name.startswith("knowledge_code_architecture_") or name.startswith("knowledge_architecture_"):
        return "architecture"
    if name.startswith("knowledge_code_") or name.startswith("knowledge_project_") or name.startswith("knowledge_agent_"):
        return "codebase"
    if name.startswith("knowledge_workspace_"):
        return "workspace"
    if name.startswith("knowledge_source_"):
        return "source"
    if name.startswith("knowledge_build_"):
        return "build"
    if name.startswith("knowledge_quality_") or name.startswith("knowledge_correction_"):
        return "quality"
    if name.startswith("knowledge_session_") or name.startswith("knowledge_actor_"):
        return "session"
    if name.startswith("knowledge_graph_"):
        return "graph"
    return "core"


def _goal_tags(name: str) -> list[str]:
    tags = []
    if any(token in name for token in ("overview", "devwiki", "human_report", "platform_console")):
        tags.append("project_reading")
    if any(token in name for token in ("task_plan", "impact", "context_pack", "patch_plan", "workbench")):
        tags.append("coding_task_preparation")
    if any(token in name for token in ("architecture", "evidence", "relationships", "ranking")):
        tags.append("architecture_review")
    if any(token in name for token in ("quality", "governance", "rules")):
        tags.append("governance_review")
    return sorted(set(tags or ["general"]))


def _outputs(name: str) -> list[str]:
    if name.endswith("_build") or name.endswith("build"):
        return ["persisted_artifact", "artifact_refs"]
    if name.endswith("_read") or name.endswith("read"):
        return ["artifact_payload", "artifact_refs"]
    if "view" in name:
        return ["rendered_view"]
    return ["structured_payload"]


def _failure_modes(name: str) -> list[str]:
    modes = ["missing_workspace", "missing_codebase"]
    if "build" in name or "snapshot" in name:
        modes.append("source_artifact_missing")
    if "provider" in name:
        modes.append("provider_unavailable")
    if "runtime" in name:
        modes.append("runtime_command_blocked")
    return sorted(set(modes))


def _groups(tools: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[str]] = {}
    for tool in tools:
        grouped.setdefault(tool["group_id"], []).append(tool["tool_name"])
    return [
        {"group_id": group_id, "tool_count": len(names), "tools": sorted(names)}
        for group_id, names in sorted(grouped.items())
    ]


def _workflow_guides(workspace_id: str, codebase_id: str, tool_names: set[str]) -> dict[str, Any]:
    specs = [
        (
            "project_reading",
            "Project reading and summary",
            ["knowledge_codebase_snapshot", "knowledge_project_inventory", "knowledge_project_overview", "knowledge_code_platform_console_build"],
        ),
        (
            "coding_task_preparation",
            "Prepare evidence-backed coding context",
            ["knowledge_code_actionability_build", "knowledge_code_impact_analyze", "knowledge_code_task_plan", "knowledge_code_workbench_v2_build"],
        ),
        (
            "architecture_review",
            "Review architecture evidence and human report",
            ["knowledge_code_architecture_evidence_v2_build", "knowledge_code_architecture_relationships_v2_build", "knowledge_code_architecture_human_report_v2_build", "knowledge_code_architecture_context_pack_v3"],
        ),
    ]
    return {
        "schema_version": TOOL_CATALOG_SCHEMA_VERSION,
        "artifact_type": "workflow_guides",
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "generated_at": now(),
        "guides": [
            {
                "goal_id": goal_id,
                "title": title,
                "steps": [
                    {
                        "step_index": index,
                        "tool_name": tool,
                        "status": "available" if tool in tool_names else "missing",
                        "preconditions": ["workspace_id", "codebase_id"],
                        "expected_outputs": _outputs(tool),
                        "failure_modes": _failure_modes(tool),
                    }
                    for index, tool in enumerate(chain, start=1)
                ],
            }
            for goal_id, title, chain in specs
        ],
    }
