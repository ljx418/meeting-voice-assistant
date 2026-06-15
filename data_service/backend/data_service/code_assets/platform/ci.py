"""V2.24 production readiness and CI hardening artifacts."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from data_service.mcp_common import now

from ..registry import CodebaseRegistry
from .persistence import (
    cache_decisions_path,
    ci_artifact_refs,
    console_payload_path,
    contract_registry_path,
    governance_overlay_report_path,
    mcp_tool_catalog_path,
    platform_dir,
    provider_capabilities_path,
    release_readiness_report_path,
    scan_profile_path,
    validation_report_path,
    workflow_guides_path,
    write_ci_readiness_report,
    read_ci_readiness_report,
    read_release_readiness_report,
)


CI_SCHEMA_VERSION = "v2.24"
MANDATORY_LAYERS = ["unit", "contract", "artifact", "frontend", "real_repo_e2e"]
ALL_LAYERS = [*MANDATORY_LAYERS, "slow_nightly"]
PASSABLE_STATUSES = {"passed", "failed", "skipped", "not_run"}


class PlatformCIReadinessService:
    def __init__(self, workspace: Path, *, workspace_id: str) -> None:
        self.workspace = Path(workspace)
        self.workspace_id = workspace_id
        self.registry = CodebaseRegistry(workspace, workspace_id=workspace_id)

    def build_readiness(
        self,
        codebase_id: str,
        *,
        snapshot_id: str | None = None,
        command_evidence: dict[str, Any] | None = None,
        warning_budget: int = 700,
    ) -> dict[str, Any]:
        asset = self.registry.describe(codebase_id)
        layers = _normalize_layers(command_evidence or {})
        warnings = _extract_warning_count(command_evidence or {})
        artifact_gate = self._artifact_gate(codebase_id)
        security_gate = self._security_gate(codebase_id, Path(asset.root_path))
        warning_gate = {
            "current": warnings,
            "budget": int(warning_budget),
            "over_budget": warnings > int(warning_budget),
        }
        blockers = []
        needs_review = []
        for layer_name in MANDATORY_LAYERS:
            status = layers[layer_name]["status"]
            if status != "passed":
                blockers.append({"code": "TEST_LAYER_NOT_PASSED", "layer": layer_name, "status": status})
        if warning_gate["over_budget"]:
            blockers.append({"code": "WARNING_BUDGET_EXCEEDED", "current": warnings, "budget": int(warning_budget)})
        if security_gate["redaction"] != "passed":
            blockers.append({"code": "PUBLIC_PAYLOAD_REDACTION_FAILED", **security_gate})
        for item in artifact_gate["missing_artifacts"]:
            blockers.append({"code": "PLATFORM_ARTIFACT_MISSING", "artifact": item})
        for layer_name, layer in layers.items():
            if layer["status"] in {"skipped", "not_run"} and layer_name not in MANDATORY_LAYERS:
                needs_review.append({"code": "OPTIONAL_LAYER_NOT_RUN", "layer": layer_name, "status": layer["status"], "reason": layer.get("reason", "")})

        release_ready = not blockers
        report = {
            "schema_version": CI_SCHEMA_VERSION,
            "artifact_type": "ci_readiness",
            "workspace_id": self.workspace_id,
            "codebase_id": codebase_id,
            "snapshot_id": snapshot_id,
            "artifact_id": f"ci_readiness:{codebase_id}",
            "created_at": now(),
            "overall_status": "ready" if release_ready else "blocked",
            "test_layers": layers,
            "warning_budget": warning_gate,
            "security_gate": security_gate,
            "artifact_gate": artifact_gate,
            "release_gate": {"ready": release_ready, "blockers": blockers, "needs_review": needs_review},
            "source_policy": {
                "command_evidence_required": True,
                "skipped_not_counted_as_passed": True,
                "readiness_artifact_only": True,
            },
            "artifact_refs": ci_artifact_refs(codebase_id),
            "warnings": [item["code"] for item in blockers],
            "unresolved": needs_review,
        }
        markdown = render_release_readiness_markdown(report)
        write_ci_readiness_report(self.workspace, codebase_id, report, markdown)
        return report

    def read_readiness(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        return read_ci_readiness_report(self.workspace, codebase_id)

    def read_release_report(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        return {
            "schema_version": CI_SCHEMA_VERSION,
            "artifact_type": "release_readiness_report",
            "workspace_id": self.workspace_id,
            "codebase_id": codebase_id,
            "content_type": "text/markdown",
            "content": read_release_readiness_report(self.workspace, codebase_id),
            "artifact_refs": ci_artifact_refs(codebase_id),
        }

    def _artifact_gate(self, codebase_id: str) -> dict[str, Any]:
        required = {
            "platform_console": console_payload_path(self.workspace, codebase_id),
            "artifact_contract_registry": contract_registry_path(self.workspace, codebase_id),
            "artifact_validation_report": validation_report_path(self.workspace, codebase_id),
            "mcp_tool_catalog": mcp_tool_catalog_path(self.workspace, codebase_id),
            "workflow_guides": workflow_guides_path(self.workspace, codebase_id),
            "cache_decisions": cache_decisions_path(self.workspace, codebase_id),
            "scan_profile": scan_profile_path(self.workspace, codebase_id),
            "provider_capabilities": provider_capabilities_path(self.workspace, codebase_id),
            "platform_governance_overlay": governance_overlay_report_path(self.workspace, codebase_id),
        }
        present = [name for name, path in required.items() if path.exists()]
        missing = [name for name, path in required.items() if not path.exists()]
        return {
            "required_artifact_count": len(required),
            "present_artifact_count": len(present),
            "missing_artifacts": missing,
        }

    def _security_gate(self, codebase_id: str, repo_root: Path) -> dict[str, Any]:
        candidates = [str(repo_root), str(self.workspace), "/private/tmp/"]
        env_keys = [key for key in os.environ if any(token in key.upper() for token in ("TOKEN", "API_KEY", "SECRET", "PASSWORD"))]
        for key in env_keys:
            value = os.environ.get(key)
            if value and len(value) >= 8:
                candidates.append(value)
        absolute_path_leak_count = 0
        secret_leak_count = 0
        scanned_files = 0
        base = platform_dir(self.workspace, codebase_id)
        if base.exists():
            for path in base.rglob("*"):
                if not path.is_file() or path.suffix.lower() not in {".json", ".jsonl", ".md", ".html"}:
                    continue
                if "platform/ci/" in path.as_posix():
                    continue
                scanned_files += 1
                text = path.read_text(encoding="utf-8", errors="ignore")
                for value in candidates[:3]:
                    absolute_path_leak_count += text.count(value)
                for value in candidates[3:]:
                    secret_leak_count += text.count(value)
        passed = absolute_path_leak_count == 0 and secret_leak_count == 0
        return {
            "redaction": "passed" if passed else "failed",
            "absolute_path_leak_count": absolute_path_leak_count,
            "secret_leak_count": secret_leak_count,
            "scanned_file_count": scanned_files,
        }


def public_ci_readiness_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": payload.get("schema_version"),
        "artifact_type": payload.get("artifact_type"),
        "workspace_id": payload.get("workspace_id"),
        "codebase_id": payload.get("codebase_id"),
        "snapshot_id": payload.get("snapshot_id"),
        "overall_status": payload.get("overall_status"),
        "test_layers": payload.get("test_layers", {}),
        "warning_budget": payload.get("warning_budget", {}),
        "security_gate": payload.get("security_gate", {}),
        "artifact_gate": payload.get("artifact_gate", {}),
        "release_gate": payload.get("release_gate", {}),
        "source_policy": payload.get("source_policy", {}),
        "artifact_refs": payload.get("artifact_refs", []),
        "warnings": payload.get("warnings", []),
        "unresolved": payload.get("unresolved", []),
    }


def public_release_report_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return dict(payload)


def render_release_readiness_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Release Readiness Report",
        "",
        f"- Schema version: `{report.get('schema_version')}`",
        f"- Codebase: `{report.get('codebase_id')}`",
        f"- Overall status: `{report.get('overall_status')}`",
        f"- Release ready: `{report.get('release_gate', {}).get('ready')}`",
        "",
        "## Test Layers",
        "",
        "| Layer | Status | Command |",
        "| --- | --- | --- |",
    ]
    for name in ALL_LAYERS:
        layer = report.get("test_layers", {}).get(name, {})
        command = str(layer.get("command") or layer.get("reason") or "")
        lines.append(f"| `{name}` | `{layer.get('status')}` | `{_escape_md(command)}` |")
    lines.extend(
        [
            "",
            "## Warning Budget",
            "",
            f"- Current: `{report.get('warning_budget', {}).get('current')}`",
            f"- Budget: `{report.get('warning_budget', {}).get('budget')}`",
            f"- Over budget: `{report.get('warning_budget', {}).get('over_budget')}`",
            "",
            "## Security Gate",
            "",
            f"- Redaction: `{report.get('security_gate', {}).get('redaction')}`",
            f"- Absolute path leaks: `{report.get('security_gate', {}).get('absolute_path_leak_count')}`",
            f"- Secret leaks: `{report.get('security_gate', {}).get('secret_leak_count')}`",
            "",
            "## Release Blockers",
            "",
        ]
    )
    blockers = report.get("release_gate", {}).get("blockers", [])
    if blockers:
        for blocker in blockers:
            lines.append(f"- `{blocker.get('code')}`: `{_escape_md(str(blocker))}`")
    else:
        lines.append("- None.")
    return "\n".join(lines) + "\n"


def _normalize_layers(command_evidence: dict[str, Any]) -> dict[str, dict[str, Any]]:
    layers: dict[str, dict[str, Any]] = {}
    for name in ALL_LAYERS:
        raw = command_evidence.get(name) or {}
        if isinstance(raw, str):
            raw = {"status": raw}
        status = str(raw.get("status") or ("skipped" if name == "slow_nightly" else "not_run")).strip()
        if status not in PASSABLE_STATUSES:
            status = "failed"
        layers[name] = {
            "status": status,
            "command": str(raw.get("command") or ""),
            "exit_code": raw.get("exit_code"),
            "duration_seconds": raw.get("duration_seconds"),
            "warning_count": int(raw.get("warning_count") or 0),
            "reason": str(raw.get("reason") or ""),
        }
    return layers


def _extract_warning_count(command_evidence: dict[str, Any]) -> int:
    total = 0
    for raw in command_evidence.values():
        if isinstance(raw, dict):
            total += int(raw.get("warning_count") or 0)
    return total


def _escape_md(text: str) -> str:
    return text.replace("|", "\\|").replace("\n", " ")
