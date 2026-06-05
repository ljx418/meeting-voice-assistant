"""Agent context pack service for V2 codebase assets."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from data_service.mcp_common import now

from ..architecture.service import ArchitectureService
from ..inventory import CodebaseInventoryService
from ..overview import CodebaseOverviewService, public_overview_payload
from ..registry import CodebaseRegistry
from ..symbols import CodebaseSymbolIndexService
from ..trace import CodebaseTraceService
from .model import CONTEXT_SCHEMA_VERSION, normalize_format, normalize_mode, stable_pack_id, token_estimate
from .persistence import context_artifact_refs, read_context_pack, write_context_pack
from .renderer_json import render_json_pack
from .renderer_markdown import render_markdown
from .selector import select_context_items
from .token_budget import apply_token_budget


class CodebaseAgentContextService:
    def __init__(self, workspace: Path, *, workspace_id: str) -> None:
        self.workspace = workspace
        self.workspace_id = workspace_id
        self.registry = CodebaseRegistry(workspace, workspace_id=workspace_id)
        self.overviews = CodebaseOverviewService(workspace, workspace_id=workspace_id)
        self.inventory = CodebaseInventoryService(workspace, workspace_id=workspace_id)
        self.symbols = CodebaseSymbolIndexService(workspace, workspace_id=workspace_id)
        self.trace = CodebaseTraceService(workspace, workspace_id=workspace_id)
        self.architecture = ArchitectureService(workspace, workspace_id=workspace_id)

    def create_pack(
        self,
        codebase_id: str,
        *,
        snapshot_id: str | None = None,
        mode: str | None = None,
        task: str | None = None,
        output_format: str | None = None,
        max_tokens: int = 16000,
        focus: dict[str, Any] | None = None,
        include: list[str] | None = None,
    ) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        normalized_mode = normalize_mode(mode, task)
        normalized_format = normalize_format(output_format)
        overview = self.overviews.read_overview(codebase_id, snapshot_id=snapshot_id, build_if_missing=True)
        resolved_snapshot_id = str(overview["snapshot_id"])
        inventory = self.inventory.read_inventory(codebase_id, snapshot_id=resolved_snapshot_id)
        symbol_index = self.symbols.read_symbol_index(codebase_id, snapshot_id=resolved_snapshot_id)
        trace = self.trace.read_trace(codebase_id, snapshot_id=resolved_snapshot_id)
        pack_id = stable_pack_id(
            workspace_id=self.workspace_id,
            codebase_id=codebase_id,
            snapshot_id=resolved_snapshot_id,
            mode=normalized_mode,
            task=task,
            output_format=normalized_format,
            focus=focus,
            include=include,
            max_tokens=max_tokens,
        )
        selected = select_context_items(
            overview=public_overview_payload(overview),
            inventory=inventory,
            symbol_index=symbol_index,
            trace=trace,
            mode=normalized_mode,
            task=task,
            focus=focus,
            include=include,
        )
        base = {
            "schema_version": CONTEXT_SCHEMA_VERSION,
            "workspace_id": self.workspace_id,
            "codebase_id": codebase_id,
            "snapshot_id": resolved_snapshot_id,
            "pack_id": pack_id,
            "created_at": now(),
            "mode": normalized_mode,
            "task": task,
            "format": normalized_format,
            "project_summary": {
                "project_one_liner": overview.get("project_one_liner"),
                "language_stats": overview.get("language_stats"),
                "public_surface_summary": overview.get("public_surface_summary"),
                "core_modules": overview.get("core_modules", [])[:8],
                "storage_summary": overview.get("storage_summary"),
                "evidence": overview.get("evidence", [])[:12],
            },
            "confidence": overview.get("confidence", 0.8),
            "needs_review": overview.get("needs_review", []),
            "artifact_refs": context_artifact_refs(codebase_id, pack_id),
            "source_artifact_refs": overview.get("source_artifact_refs", []),
            "omitted_items": [],
        }
        architecture_summary = self.architecture.build_context_architecture_summary(codebase_id)
        if architecture_summary:
            base["architecture_summary"] = architecture_summary
            base["source_artifact_refs"] = [*base["source_artifact_refs"], *architecture_summary.get("artifact_refs", [])]
        pack = render_json_pack(base, selected)
        pack = apply_token_budget(pack, max_tokens=max_tokens)
        if normalized_format == "markdown":
            pack["content"] = render_markdown(pack)
            pack["token_estimate"] = token_estimate(pack["content"])
        else:
            pack["content"] = None
            pack["token_estimate"] = token_estimate(pack)
        write_context_pack(self.workspace, codebase_id, pack_id, pack)
        return pack

    def read_pack(self, codebase_id: str, pack_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        return read_context_pack(self.workspace, codebase_id, pack_id)


def public_context_pack_payload(pack: dict[str, Any]) -> dict[str, Any]:
    return dict(pack)
