"""V2.18 Platform Console service."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from data_service.mcp_common import now, read_json

from ..artifacts import (
    agent_context_dir,
    architecture_code_relationships_v29_path,
    architecture_context_pack_v29_dir,
    architecture_human_review_report_v29_path,
    architecture_public_surface_evidence_v29_path,
    architecture_signal_ranking_v29_path,
    architecture_v29_view_path,
    codebase_dir,
    evidence_path,
    inventory_surfaces_path,
    overview_path,
    read_jsonl,
    snapshots_dir,
)
from ..coding_agent.persistence import patch_plans_dir
from ..coding_agent_v2_16.persistence import (
    patch_sandbox_previews_dir,
    runtime_profiles_path,
    workbench_v2_payload_path,
)
from ..registry import CodebaseRegistry
from .persistence import console_artifact_refs, console_html_path, read_console, write_console
from .renderer_html import render_platform_console_html


PLATFORM_CONSOLE_SCHEMA_VERSION = "v2.18"
PANEL_IDS = ["overview", "evidence", "architecture", "agent", "runtime", "patch", "next_actions"]


class PlatformConsoleService:
    def __init__(self, workspace: Path, *, workspace_id: str) -> None:
        self.workspace = workspace
        self.workspace_id = workspace_id
        self.registry = CodebaseRegistry(workspace, workspace_id=workspace_id)

    def build_console(self, codebase_id: str, *, snapshot_id: str | None = None) -> dict[str, Any]:
        asset = self.registry.describe(codebase_id)
        resolved_snapshot_id = snapshot_id or self._latest_snapshot_id(codebase_id)
        panels = [
            self._overview_panel(codebase_id, resolved_snapshot_id, asset.name),
            self._evidence_panel(codebase_id, resolved_snapshot_id),
            self._architecture_panel(codebase_id),
            self._agent_panel(codebase_id),
            self._runtime_panel(codebase_id),
            self._patch_panel(codebase_id),
        ]
        next_actions = self._next_actions(panels)
        panels.append(
            {
                "panel_id": "next_actions",
                "title": "Next Actions",
                "status": "ready" if next_actions else "partial",
                "description": "Recommended build/read commands based on missing platform inputs.",
                "metrics": {"action_count": len(next_actions)},
                "artifact_refs": [],
                "needs_review": [],
                "actions": next_actions,
            }
        )
        payload = {
            "schema_version": PLATFORM_CONSOLE_SCHEMA_VERSION,
            "artifact_type": "platform_console",
            "workspace_id": self.workspace_id,
            "codebase_id": codebase_id,
            "snapshot_id": resolved_snapshot_id,
            "generated_at": now(),
            "source_policy": {
                "fact_source": "persisted_artifacts_only",
                "no_repo_rescan": True,
                "missing_artifacts_marked_needs_build": True,
            },
            "summary": self._summary(panels),
            "panels": panels,
            "warnings": self._warnings(panels),
            "next_actions": next_actions,
            "artifact_refs": console_artifact_refs(codebase_id),
        }
        write_console(self.workspace, codebase_id, payload, render_platform_console_html(payload))
        return payload

    def read_console(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        return read_console(self.workspace, codebase_id)

    def read_console_view(self, codebase_id: str, view_id: str = "html") -> dict[str, Any]:
        self.registry.describe(codebase_id)
        if view_id not in {"html", "platform_console.html"}:
            raise FileNotFoundError("PLATFORM_CONSOLE_VIEW_NOT_FOUND")
        path = console_html_path(self.workspace, codebase_id)
        if not path.exists():
            raise FileNotFoundError("PLATFORM_CONSOLE_VIEW_NOT_FOUND")
        return {
            "schema_version": PLATFORM_CONSOLE_SCHEMA_VERSION,
            "workspace_id": self.workspace_id,
            "codebase_id": codebase_id,
            "view_id": "platform_console.html",
            "content_type": "text/html",
            "content": path.read_text(encoding="utf-8"),
            "artifact_refs": console_artifact_refs(codebase_id),
        }

    def _latest_snapshot_id(self, codebase_id: str) -> str | None:
        base = snapshots_dir(self.workspace, codebase_id)
        if not base.exists():
            return None
        candidates = []
        for path in base.iterdir():
            if not path.is_dir():
                continue
            payload = read_json(path / "snapshot.json", None)
            if payload:
                candidates.append(payload)
        if not candidates:
            return None
        latest = sorted(candidates, key=lambda item: str(item.get("created_at") or item.get("snapshot_id") or ""))[-1]
        return str(latest.get("snapshot_id") or "") or None

    def _overview_panel(self, codebase_id: str, snapshot_id: str | None, name: str) -> dict[str, Any]:
        path = overview_path(self.workspace, codebase_id)
        overview = read_json(path, None)
        metrics = {"snapshot_present": bool(snapshot_id), "overview_present": bool(overview)}
        status = "ready" if snapshot_id and overview else "needs_build"
        refs = [{"type": "project_overview", "artifact_ref": f"codebase://{codebase_id}/overview.json"}] if overview else []
        needs_review = [] if overview else [_need("project_overview_missing", "Project overview artifact is missing.", "knowledge_project_overview")]
        return _panel("overview", "Overview", status, f"Project identity and summary for {name or codebase_id}.", metrics, refs, needs_review)

    def _evidence_panel(self, codebase_id: str, snapshot_id: str | None) -> dict[str, Any]:
        if not snapshot_id:
            return _panel("evidence", "Evidence", "blocked", "Line-level public surface and code evidence.", {"surface_count": 0, "evidence_count": 0, "v29_evidence_count": 0}, [], [_need("snapshot_missing", "Snapshot is required before evidence can be summarized.", "knowledge_codebase_snapshot")])
        surfaces = read_jsonl(inventory_surfaces_path(self.workspace, codebase_id, snapshot_id))
        evidence = read_jsonl(evidence_path(self.workspace, codebase_id, snapshot_id))
        v29_evidence = read_jsonl(architecture_public_surface_evidence_v29_path(self.workspace, codebase_id))
        refs = []
        if surfaces:
            refs.append({"type": "public_surfaces", "artifact_ref": f"codebase://{codebase_id}/snapshots/{snapshot_id}/surfaces.jsonl"})
        if evidence:
            refs.append({"type": "code_evidence", "artifact_ref": f"codebase://{codebase_id}/snapshots/{snapshot_id}/evidence.jsonl"})
        if v29_evidence:
            refs.append({"type": "architecture_public_surface_evidence_v2", "artifact_ref": f"architecture://{codebase_id}/v2_9/architecture_public_surface_evidence_v2.jsonl"})
        status = "ready" if evidence or v29_evidence else "needs_build"
        needs = [] if status == "ready" else [_need("evidence_missing", "Evidence artifacts are missing.", "knowledge_public_surface_trace")]
        return _panel("evidence", "Evidence", status, "Public surface and source evidence coverage.", {"surface_count": len(surfaces), "evidence_count": len(evidence), "v29_evidence_count": len(v29_evidence)}, refs, needs)

    def _architecture_panel(self, codebase_id: str) -> dict[str, Any]:
        paths = [
            ("relationships", architecture_code_relationships_v29_path(self.workspace, codebase_id), "architecture://{codebase_id}/v2_9/architecture_code_relationships_v2.jsonl"),
            ("ranking", architecture_signal_ranking_v29_path(self.workspace, codebase_id), "architecture://{codebase_id}/v2_9/architecture_signal_ranking_v2.json"),
            ("human_report", architecture_human_review_report_v29_path(self.workspace, codebase_id), "architecture://{codebase_id}/v2_9/architecture_human_review_report_v2.json"),
            ("human_report_html", architecture_v29_view_path(self.workspace, codebase_id, "architecture_human_review_report_v2.html"), "architecture://{codebase_id}/v2_9/views/architecture_human_review_report_v2.html"),
        ]
        refs = []
        metrics: dict[str, Any] = {}
        for key, path, ref in paths:
            exists = path.exists()
            metrics[f"{key}_present"] = exists
            if exists:
                refs.append({"type": key, "artifact_ref": ref.format(codebase_id=codebase_id)})
        status = "ready" if len(refs) >= 3 else "partial" if refs else "needs_build"
        needs = [] if status == "ready" else [_need("architecture_report_missing", "Architecture report/ranking/relationship artifacts are incomplete.", "knowledge_code_architecture_human_report_v2_build")]
        return _panel("architecture", "Architecture", status, "Architecture review report, relationships, ranking, and rendered views.", metrics, refs, needs)

    def _agent_panel(self, codebase_id: str) -> dict[str, Any]:
        context_dir = architecture_context_pack_v29_dir(self.workspace, codebase_id)
        legacy_context_dir = agent_context_dir(self.workspace, codebase_id)
        workbench = read_json(workbench_v2_payload_path(self.workspace, codebase_id), None)
        context_count = _json_count(context_dir) + _json_count(legacy_context_dir)
        refs = []
        if workbench:
            refs.append({"type": "workbench_v2", "artifact_ref": f"coding-agent://{codebase_id}/v2_16/workbench_v2/review_workbench_v2.json"})
        if context_count:
            refs.append({"type": "context_packs", "artifact_ref": f"architecture://{codebase_id}/context-packs"})
        status = "ready" if workbench and context_count else "partial" if workbench or context_count else "needs_build"
        needs = [] if status == "ready" else [_need("agent_context_missing", "Agent workbench or context packs are missing.", "knowledge_code_workbench_v2_build")]
        return _panel("agent", "Agent", status, "Agent-facing workbench and context assets.", {"workbench_present": bool(workbench), "context_pack_count": context_count}, refs, needs)

    def _runtime_panel(self, codebase_id: str) -> dict[str, Any]:
        profiles = read_json(runtime_profiles_path(self.workspace, codebase_id), None)
        profile_count = len((profiles or {}).get("profiles", [])) if isinstance(profiles, dict) else 0
        refs = [{"type": "runtime_profiles", "artifact_ref": f"coding-agent://{codebase_id}/v2_16/runtime_profiles/profiles.json"}] if profiles else []
        status = "ready" if profile_count else "needs_build"
        needs = [] if status == "ready" else [_need("runtime_profiles_missing", "Runtime profiles are missing.", "knowledge_code_runtime_profiles_build")]
        return _panel("runtime", "Runtime", status, "Controlled runtime profile readiness.", {"runtime_profile_count": profile_count}, refs, needs)

    def _patch_panel(self, codebase_id: str) -> dict[str, Any]:
        plan_count = _json_count(patch_plans_dir(self.workspace, codebase_id))
        preview_count = _json_count(patch_sandbox_previews_dir(self.workspace, codebase_id))
        refs = []
        if plan_count:
            refs.append({"type": "patch_plans", "artifact_ref": f"coding-agent://{codebase_id}/patch_plans"})
        if preview_count:
            refs.append({"type": "patch_previews", "artifact_ref": f"coding-agent://{codebase_id}/v2_16/patch_sandbox/previews"})
        status = "ready" if plan_count and preview_count else "partial" if plan_count or preview_count else "needs_build"
        needs = [] if status == "ready" else [_need("patch_assets_missing", "Patch plans or previews are missing.", "knowledge_code_patch_plan_create")]
        return _panel("patch", "Patch", status, "Human-gated patch planning and preview status.", {"patch_plan_count": plan_count, "patch_preview_count": preview_count}, refs, needs)

    def _summary(self, panels: list[dict[str, Any]]) -> dict[str, Any]:
        return {
            "panel_count": len(panels),
            "ready_panel_count": sum(1 for panel in panels if panel.get("status") == "ready"),
            "needs_build_panel_count": sum(1 for panel in panels if panel.get("status") in {"needs_build", "partial"}),
            "blocked_panel_count": sum(1 for panel in panels if panel.get("status") == "blocked"),
        }

    def _warnings(self, panels: list[dict[str, Any]]) -> list[str]:
        warnings = []
        for panel in panels:
            if panel.get("status") in {"needs_build", "partial", "blocked"}:
                warnings.append(f"{panel.get('panel_id')}: {panel.get('status')}")
        return warnings

    def _next_actions(self, panels: list[dict[str, Any]]) -> list[str]:
        actions = []
        for panel in panels:
            for item in panel.get("needs_review", []):
                action = str(item.get("next_action") or "")
                if action:
                    actions.append(action)
        return sorted(set(actions))


def public_platform_console_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": payload.get("schema_version"),
        "artifact_type": payload.get("artifact_type"),
        "workspace_id": payload.get("workspace_id"),
        "codebase_id": payload.get("codebase_id"),
        "snapshot_id": payload.get("snapshot_id"),
        "generated_at": payload.get("generated_at"),
        "source_policy": payload.get("source_policy", {}),
        "summary": payload.get("summary", {}),
        "panels": payload.get("panels", []),
        "warnings": payload.get("warnings", []),
        "next_actions": payload.get("next_actions", []),
        "artifact_refs": payload.get("artifact_refs", []),
    }


def public_platform_console_view_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return dict(payload)


def _panel(panel_id: str, title: str, status: str, description: str, metrics: dict[str, Any], artifact_refs: list[dict[str, str]], needs_review: list[dict[str, str]]) -> dict[str, Any]:
    return {
        "panel_id": panel_id,
        "title": title,
        "status": status,
        "description": description,
        "metrics": metrics,
        "artifact_refs": artifact_refs,
        "needs_review": needs_review,
    }


def _need(reason: str, message: str, next_action: str) -> dict[str, str]:
    return {"reason": reason, "message": message, "next_action": next_action}


def _json_count(path: Path) -> int:
    if not path.exists() or not path.is_dir():
        return 0
    return sum(1 for item in path.iterdir() if item.is_file() and item.suffix == ".json")
