"""V2.21 platform incremental build plan builder."""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any

from data_service.mcp_common import now

from ..artifacts import read_jsonl, snapshot_files_path
from ..coding_agent.service import CodingAgentActionabilityService
from ..registry import CodebaseRegistry
from ..snapshot import CodebaseSnapshotService
from .persistence import (
    incremental_artifact_refs,
    read_cache_decisions,
    read_incremental_plan,
    read_scan_profile,
    write_incremental_plan,
)


INCREMENTAL_SCHEMA_VERSION = "v2.21"

ARTIFACT_FAMILIES = (
    "snapshot",
    "inventory",
    "symbols",
    "trace",
    "overview",
    "agent_context",
    "devwiki",
    "graph",
    "architecture",
    "coding_agent",
    "platform_console",
    "platform_contracts",
    "platform_tool_catalog",
)


class PlatformIncrementalService:
    def __init__(self, workspace: Path, *, workspace_id: str) -> None:
        self.workspace = Path(workspace)
        self.workspace_id = workspace_id
        self.registry = CodebaseRegistry(workspace, workspace_id=workspace_id)
        self.snapshots = CodebaseSnapshotService(workspace, workspace_id=workspace_id)

    def build_incremental_plan(self, codebase_id: str, *, from_snapshot_id: str, to_snapshot_id: str) -> dict[str, Any]:
        started = time.perf_counter()
        self.registry.describe(codebase_id)
        from_snapshot = self.snapshots.read_snapshot(codebase_id, from_snapshot_id)
        to_snapshot = self.snapshots.read_snapshot(codebase_id, to_snapshot_id)
        diff = CodingAgentActionabilityService(self.workspace, workspace_id=self.workspace_id).build_incremental_diff(
            codebase_id,
            from_snapshot_id=from_snapshot_id,
            to_snapshot_id=to_snapshot_id,
            task="platform incremental build planning",
        )
        to_files = read_jsonl(snapshot_files_path(self.workspace, codebase_id, to_snapshot_id))
        changed_files = list(diff.get("changed_files") or [])
        decisions = _cache_decisions(self.workspace_id, codebase_id, from_snapshot_id, to_snapshot_id, changed_files)
        scan_profile = _scan_profile(
            workspace_id=self.workspace_id,
            codebase_id=codebase_id,
            from_snapshot=from_snapshot,
            to_snapshot=to_snapshot,
            to_files=to_files,
            changed_files=changed_files,
            duration_ms=int((time.perf_counter() - started) * 1000),
        )
        refs = incremental_artifact_refs(codebase_id)
        fallback_reason = _fallback_reason(changed_files)
        plan = {
            "schema_version": INCREMENTAL_SCHEMA_VERSION,
            "artifact_type": "incremental_build_plan",
            "workspace_id": self.workspace_id,
            "codebase_id": codebase_id,
            "from_snapshot_id": from_snapshot_id,
            "to_snapshot_id": to_snapshot_id,
            "diff_id": diff.get("diff_id"),
            "summary": {
                "changed_file_count": len(changed_files),
                "cache_decision_count": len(decisions),
                "reused_count": sum(1 for item in decisions if item["decision"] == "reuse"),
                "refreshed_count": sum(1 for item in decisions if item["decision"] == "refresh"),
                "invalidated_count": sum(1 for item in decisions if item["decision"] == "invalidate"),
                "full_rebuild_required_count": sum(1 for item in decisions if item["decision"] == "full_rebuild_required"),
                "budget_status": scan_profile["budget"]["status"],
            },
            "changed_files": changed_files,
            "reused_artifacts": [item for item in decisions if item["decision"] == "reuse"],
            "refreshed_artifacts": [item for item in decisions if item["decision"] == "refresh"],
            "invalidated_artifacts": [item for item in decisions if item["decision"] == "invalidate"],
            "cache_decisions_ref": refs[1]["artifact_ref"],
            "scan_profile_ref": refs[2]["artifact_ref"],
            "scan_budget": scan_profile["budget"],
            "fallback_reason": fallback_reason,
            "warnings": [],
            "unresolved": [] if not fallback_reason else [{"code": fallback_reason, "message": "Full rebuild should be considered for this diff.", "retryable": False}],
            "artifact_refs": refs,
            "created_at": now(),
        }
        write_incremental_plan(self.workspace, codebase_id, plan, decisions, scan_profile)
        return {"plan": plan, "cache_decisions": decisions, "scan_profile": scan_profile, "artifact_refs": refs}

    def read_incremental_plan(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        return {
            "plan": read_incremental_plan(self.workspace, codebase_id),
            "cache_decisions": read_cache_decisions(self.workspace, codebase_id),
            "scan_profile": read_scan_profile(self.workspace, codebase_id),
            "artifact_refs": incremental_artifact_refs(codebase_id),
        }


def public_incremental_payload(payload: dict[str, Any]) -> dict[str, Any]:
    plan = dict(payload.get("plan", {}))
    plan["changed_files"] = [_public_changed_file(row) for row in list(plan.get("changed_files") or [])]
    return {
        "schema_version": INCREMENTAL_SCHEMA_VERSION,
        "artifact_type": "incremental_build_bundle",
        "plan": plan,
        "cache_decisions": payload.get("cache_decisions", []),
        "scan_profile": payload.get("scan_profile", {}),
        "artifact_refs": payload.get("artifact_refs", []),
    }


def _public_changed_file(row: dict[str, Any]) -> dict[str, Any]:
    item = dict(row)
    if item.get("path") and not item.get("source_file"):
        item["source_file"] = item["path"]
    return item


def _cache_decisions(workspace_id: str, codebase_id: str, from_snapshot_id: str, to_snapshot_id: str, changed_files: list[dict[str, Any]]) -> list[dict[str, Any]]:
    paths = [str(item.get("path") or "") for item in changed_files if item.get("path")]
    kinds = _change_kinds(paths)
    rows = []
    for family in ARTIFACT_FAMILIES:
        decision, reason, related = _decision_for_family(family, paths, kinds)
        rows.append(
            {
                "schema_version": INCREMENTAL_SCHEMA_VERSION,
                "workspace_id": workspace_id,
                "codebase_id": codebase_id,
                "from_snapshot_id": from_snapshot_id,
                "to_snapshot_id": to_snapshot_id,
                "artifact_family": family,
                "decision": decision,
                "reason": reason,
                "related_changed_paths": related[:50],
                "safe_to_reuse": decision == "reuse",
                "needs_review": [] if decision != "reuse" or not paths else ["reuse decision with changed files must be justified by family-specific policy"],
                "created_at": now(),
            }
        )
    return rows


def _decision_for_family(family: str, paths: list[str], kinds: set[str]) -> tuple[str, str, list[str]]:
    if not paths:
        return "reuse", "no changed files between snapshots", []
    if "build_config" in kinds and family not in {"snapshot", "platform_tool_catalog"}:
        return "full_rebuild_required", "build or dependency config changed", paths
    if family == "snapshot":
        return "refresh", "target snapshot is the new build input", paths
    if family == "inventory":
        return ("refresh", "public surface candidate changed", paths) if kinds & {"api", "mcp", "cli", "frontend", "config"} else ("reuse", "changed paths do not affect public surface inventory policy", [])
    if family == "symbols":
        return ("refresh", "code file changed and symbol index may be stale", paths) if kinds & {"code", "api", "mcp", "cli"} else ("reuse", "no symbol-bearing code changes detected", [])
    if family == "trace":
        return ("invalidate", "surface/symbol evidence may be stale", paths) if kinds & {"code", "api", "mcp", "cli"} else ("reuse", "no trace-relevant code changes detected", [])
    if family in {"overview", "agent_context", "devwiki"}:
        return ("refresh", "project-readable artifact should reflect code or documentation changes", paths) if kinds & {"code", "docs", "api", "mcp", "cli", "config"} else ("reuse", "no project-summary relevant change detected", [])
    if family in {"graph", "architecture", "coding_agent"}:
        return ("invalidate", "derived architecture/coding-agent artifact depends on changed source facts", paths) if kinds & {"code", "api", "mcp", "cli", "config"} else ("reuse", "no graph or coding-agent relevant change detected", [])
    if family == "platform_console":
        return "refresh", "console summarizes latest artifact states", paths
    if family == "platform_contracts":
        return ("refresh", "platform contracts should rescan artifact inventory after changed source facts", paths) if kinds & {"code", "config"} else ("reuse", "no artifact contract relevant change detected", [])
    if family == "platform_tool_catalog":
        return ("refresh", "MCP tool implementation or registry may have changed", paths) if kinds & {"mcp", "cli"} else ("reuse", "no MCP/CLI tool registry change detected", [])
    return "invalidate", "unknown artifact family policy", paths


def _change_kinds(paths: list[str]) -> set[str]:
    kinds: set[str] = set()
    for path in paths:
        lowered = path.lower()
        if lowered.endswith((".py", ".ts", ".tsx", ".vue", ".js", ".jsx", ".go", ".rs", ".java", ".kt", ".swift")):
            kinds.add("code")
        if lowered.endswith((".md", ".drawio", ".mmd", ".txt")) or lowered.startswith("docs/"):
            kinds.add("docs")
        if any(token in lowered for token in ("api", "router", "route")):
            kinds.add("api")
        if "mcp" in lowered or "tool_registry" in lowered:
            kinds.add("mcp")
        if "__main__" in lowered or "cli" in lowered:
            kinds.add("cli")
        if lowered.startswith("frontend/") or lowered.endswith((".vue", ".tsx", ".jsx", ".css", ".scss")):
            kinds.add("frontend")
        if lowered.endswith(("pyproject.toml", "package.json", "package-lock.json", "pnpm-lock.yaml", "requirements.txt", "uv.lock", "poetry.lock", "vite.config.ts")):
            kinds.add("build_config")
        if lowered.endswith((".json", ".yaml", ".yml", ".toml")):
            kinds.add("config")
    return kinds or {"unknown"}


def _scan_profile(*, workspace_id: str, codebase_id: str, from_snapshot: dict[str, Any], to_snapshot: dict[str, Any], to_files: list[dict[str, Any]], changed_files: list[dict[str, Any]], duration_ms: int) -> dict[str, Any]:
    included = [item for item in to_files if item.get("included")]
    changed_paths = {str(item.get("path") or "") for item in changed_files}
    changed_records = [item for item in to_files if item.get("path") in changed_paths]
    loc_total = sum(int(item.get("loc") or item.get("line_count") or 0) for item in included)
    changed_loc = sum(int(item.get("loc") or item.get("line_count") or 0) for item in changed_records)
    language_counts: dict[str, int] = {}
    for item in changed_records:
        language = str(item.get("language") or "unknown")
        language_counts[language] = language_counts.get(language, 0) + 1
    max_changed_files = 500
    max_changed_ratio = 0.25
    changed_ratio = (len(changed_files) / max(1, len(included)))
    over_budget = len(changed_files) > max_changed_files or changed_ratio > max_changed_ratio
    return {
        "schema_version": INCREMENTAL_SCHEMA_VERSION,
        "artifact_type": "scan_profile",
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "from_snapshot_id": from_snapshot.get("snapshot_id"),
        "to_snapshot_id": to_snapshot.get("snapshot_id"),
        "file_count": len(included),
        "loc_total": loc_total,
        "changed_file_count": len(changed_files),
        "changed_loc_estimate": changed_loc,
        "changed_ratio": round(changed_ratio, 6),
        "changed_languages": language_counts,
        "budget": {
            "max_changed_files": max_changed_files,
            "max_changed_ratio": max_changed_ratio,
            "duration_ms": max(0, duration_ms),
            "over_budget": over_budget,
            "status": "over_budget" if over_budget else "within_budget",
        },
        "warnings": [],
        "created_at": now(),
    }


def _fallback_reason(changed_files: list[dict[str, Any]]) -> str | None:
    paths = [str(item.get("path") or "") for item in changed_files]
    kinds = _change_kinds(paths)
    if "build_config" in kinds:
        return "full_rebuild_required"
    return None
