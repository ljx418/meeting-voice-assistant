"""MCP tool dispatcher for data_service."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .mcp_build_runtime import BuildRuntime
from .mcp_build_tools import BUILD_TOOL_NAMES, handle_build_tool
from .mcp_code_tools import CODE_TOOL_NAMES, handle_code_tool
from .mcp_common import blocked, bounded_int, envelope, now, read_json, slug, write_json
from .mcp_core_tools import CORE_TOOL_NAMES, handle_core_tool
from .mcp_quality_tools import QUALITY_TOOL_NAMES, handle_quality_tool
from .mcp_session_tools import SESSION_TOOL_NAMES, handle_session_tool
from .mcp_source_tools import SOURCE_TOOL_NAMES, handle_source_tool
from .mcp_tool_registry import V2_TOOL_MAP
from .mcp_workspace_runtime import WorkspaceRuntime
from .mcp_workspace_tools import WORKSPACE_TOOL_NAMES, handle_workspace_tool
from .service import DataService
from .session_service import normalize_workspace_arg


class MCPToolDispatcher:
    def __init__(
        self,
        *,
        default_workspace: Path,
        workspace_runtime: WorkspaceRuntime,
        build_runtime: BuildRuntime,
    ) -> None:
        self.default_workspace = default_workspace
        self.workspace_runtime = workspace_runtime
        self.build_runtime = build_runtime

    async def call_tool(self, name: str, arguments: dict[str, Any] | None) -> dict[str, Any]:
        arguments = arguments or {}
        service = self.service(normalize_workspace_arg(arguments.get("workspace")), arguments.get("workspace_id"))

        if name in V2_TOOL_MAP:
            return await self._call_v2_tool(name, arguments, service)

        if name in CODE_TOOL_NAMES:
            return handle_code_tool(
                name,
                arguments,
                blocked=blocked,
                envelope=envelope,
                ensure_workspace_meta=self.workspace_runtime.ensure_workspace_meta,
                resolve_workspace=self.workspace_runtime.resolve_workspace,
            )

        if name in SESSION_TOOL_NAMES:
            return handle_session_tool(
                name,
                arguments,
                service=service,
                workspace_id=self.workspace_runtime.workspace_id_for_service(service),
                envelope=envelope,
                blocked=blocked,
                bounded_int=bounded_int,
            )

        if name in CORE_TOOL_NAMES:
            return handle_core_tool(
                name,
                arguments,
                service=service,
                bounded_int=bounded_int,
            )

        if name in QUALITY_TOOL_NAMES:
            return handle_quality_tool(
                name,
                arguments,
                service=service,
                bounded_int=bounded_int,
            )

        if name in WORKSPACE_TOOL_NAMES:
            return handle_workspace_tool(
                name,
                arguments,
                bounded_int=bounded_int,
                envelope=envelope,
                ensure_workspace_meta=self.workspace_runtime.ensure_workspace_meta,
                layout_payload=self.workspace_runtime.layout_payload,
                now=now,
                operations_dir=self.workspace_runtime.operations_dir,
                read_json=read_json,
                resolve_workspace=self.workspace_runtime.resolve_workspace,
                slug=slug,
                workspace_meta_path=self.workspace_runtime.workspace_meta_path,
                workspace_root=self.workspace_runtime.workspace_root,
                write_json=write_json,
            )

        if name in SOURCE_TOOL_NAMES:
            return handle_source_tool(
                name,
                arguments,
                blocked=blocked,
                bounded_int=bounded_int,
                envelope=envelope,
                ensure_workspace_meta=self.workspace_runtime.ensure_workspace_meta,
                now=now,
                read_json=read_json,
                resolve_workspace=self.workspace_runtime.resolve_workspace,
                sources_manifest_path=self.workspace_runtime.sources_manifest_path,
                write_json=write_json,
            )

        if name in BUILD_TOOL_NAMES:
            return handle_build_tool(
                name,
                arguments,
                blocked=blocked,
                ensure_build_worker=self.build_runtime.ensure_build_worker,
                ensure_workspace_meta=self.workspace_runtime.ensure_workspace_meta,
                envelope=envelope,
                now=now,
                operation_envelope=self.build_runtime.operation_envelope,
                operation_path=self.workspace_runtime.operation_path,
                read_json=read_json,
                resolve_workspace=self.workspace_runtime.resolve_workspace,
                write_json=write_json,
            )

        raise ValueError(f"Unknown tool: {name}")

    def service(self, workspace: str | None = None, workspace_id: str | None = None) -> DataService:
        if workspace or workspace_id:
            return DataService(self.workspace_runtime.resolve_workspace(workspace_id, workspace))
        return DataService(self.default_workspace)

    async def _call_v2_tool(
        self,
        name: str,
        arguments: dict[str, Any],
        service: DataService,
    ) -> dict[str, Any]:
        legacy_name = V2_TOOL_MAP[name]
        workspace_id = self.workspace_runtime.workspace_id_for_service(service)
        if legacy_name in {"knowledge_ingest", "knowledge_quality_feedback", "knowledge_review_correction_rule"}:
            if self.workspace_runtime.is_workspace_archived(service.workspace):
                return blocked(
                    workspace_id=workspace_id,
                    message="Workspace is archived and cannot be modified",
                    next_actions=["knowledge_workspace_describe"],
                )
        try:
            legacy_payload = await self.call_tool(legacy_name, arguments)
        except ValueError as exc:
            return blocked(
                workspace_id=workspace_id,
                message=str(exc),
                next_actions=[],
            )
        return envelope(
            workspace_id=workspace_id,
            artifact_refs=[{"type": "workspace", "path": str(service.workspace)}],
            next_actions=[],
            data=json.loads(json.dumps(legacy_payload)),
        )
