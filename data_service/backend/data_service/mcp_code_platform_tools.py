"""MCP tools for V2.18 Platform Product Console."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from .code_assets.envelope import v2_error_envelope, v2_success_envelope
from .code_assets.platform.ci import PlatformCIReadinessService, public_ci_readiness_payload, public_release_report_payload
from .code_assets.platform.contracts import ArtifactContractService, public_contract_payload
from .code_assets.platform.console import (
    PlatformConsoleService,
    public_platform_console_payload,
    public_platform_console_view_payload,
)
from .code_assets.platform.governance import PlatformGovernanceService, public_governance_payload
from .code_assets.platform.incremental import PlatformIncrementalService, public_incremental_payload
from .code_assets.platform.providers import PlatformProviderService, public_provider_payload
from .code_assets.platform.tool_catalog import ToolCatalogService, public_tool_catalog_payload


PLATFORM_TOOL_NAMES = {
    "knowledge_code_platform_console_build",
    "knowledge_code_platform_console_read",
    "knowledge_code_platform_console_view",
    "knowledge_code_platform_contracts_build",
    "knowledge_code_platform_contracts_read",
    "knowledge_code_platform_tool_catalog_build",
    "knowledge_code_platform_tool_catalog_read",
    "knowledge_code_platform_incremental_build",
    "knowledge_code_platform_incremental_read",
    "knowledge_code_platform_providers_build",
    "knowledge_code_platform_providers_read",
    "knowledge_code_platform_governance_feedback",
    "knowledge_code_platform_governance_rules_build",
    "knowledge_code_platform_governance_rule_review",
    "knowledge_code_platform_governance_overlay",
    "knowledge_code_platform_ci_readiness_build",
    "knowledge_code_platform_ci_readiness_read",
    "knowledge_code_platform_ci_release_report",
}


PLATFORM_TOOL_SPECS = [
    {
        "name": "knowledge_code_platform_console_build",
        "description": "Build V2.18 Product Console from persisted project-intelligence artifacts",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}, "snapshot_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_platform_console_read",
        "description": "Read V2.18 Product Console payload",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_platform_console_view",
        "description": "Read V2.18 Product Console HTML view",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}, "view_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_platform_contracts_build",
        "description": "Build V2.19 artifact contract registry and validation report",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_platform_contracts_read",
        "description": "Read V2.19 artifact contract registry and validation report",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_platform_tool_catalog_build",
        "description": "Build V2.20 MCP tool catalog and workflow guides",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_platform_tool_catalog_read",
        "description": "Read V2.20 MCP tool catalog and workflow guides",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_platform_incremental_build",
        "description": "Build V2.21 incremental build plan, cache decisions, and scan profile",
        "inputSchema": {
            "type": "object",
            "properties": {
                "workspace_id": {"type": "string"},
                "codebase_id": {"type": "string"},
                "from_snapshot_id": {"type": "string"},
                "to_snapshot_id": {"type": "string"},
            },
            "required": ["workspace_id", "codebase_id", "from_snapshot_id", "to_snapshot_id"],
        },
    },
    {
        "name": "knowledge_code_platform_incremental_read",
        "description": "Read V2.21 incremental build plan, cache decisions, and scan profile",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_platform_providers_build",
        "description": "Build V2.22 provider plugin capabilities and execution contract",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}, "snapshot_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_platform_providers_read",
        "description": "Read V2.22 provider plugin capabilities and execution contract",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_platform_governance_feedback",
        "description": "Record V2.23 platform governance feedback for a platform artifact target",
        "inputSchema": {
            "type": "object",
            "properties": {
                "workspace_id": {"type": "string"},
                "codebase_id": {"type": "string"},
                "target_type": {"type": "string"},
                "target_id": {"type": "string"},
                "action": {"type": "string"},
                "rule_type": {"type": "string"},
                "severity": {"type": "string"},
                "reason": {"type": "string"},
                "suggested_value": {"type": "string"},
            },
            "required": ["workspace_id", "codebase_id", "target_type", "target_id", "action"],
        },
    },
    {
        "name": "knowledge_code_platform_governance_rules_build",
        "description": "Build V2.23 platform governance rules from recorded feedback",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_platform_governance_rule_review",
        "description": "Review or revoke a V2.23 platform governance rule",
        "inputSchema": {
            "type": "object",
            "properties": {
                "workspace_id": {"type": "string"},
                "codebase_id": {"type": "string"},
                "rule_id": {"type": "string"},
                "status": {"type": "string"},
                "reviewer": {"type": "string"},
                "note": {"type": "string"},
            },
            "required": ["workspace_id", "codebase_id", "rule_id", "status"],
        },
    },
    {
        "name": "knowledge_code_platform_governance_overlay",
        "description": "Read V2.23 platform governance read-time overlay report",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_platform_ci_readiness_build",
        "description": "Build V2.24 CI readiness and release readiness artifacts",
        "inputSchema": {
            "type": "object",
            "properties": {
                "workspace_id": {"type": "string"},
                "codebase_id": {"type": "string"},
                "snapshot_id": {"type": "string"},
                "command_evidence": {"type": "object"},
                "warning_budget": {"type": "integer"},
            },
            "required": ["workspace_id", "codebase_id"],
        },
    },
    {
        "name": "knowledge_code_platform_ci_readiness_read",
        "description": "Read V2.24 CI readiness artifact",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_platform_ci_release_report",
        "description": "Read V2.24 release readiness Markdown report",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
]


def handle_platform_tool(
    name: str,
    arguments: dict[str, Any],
    *,
    blocked: Callable[..., dict[str, Any]],
    envelope: Callable[..., dict[str, Any]],
    ensure_workspace_meta: Callable[..., dict[str, Any]],
    resolve_workspace: Callable[[str | None, str | None], Path],
    tool_specs_provider: Callable[[], list[dict[str, Any]]] | None = None,
) -> dict[str, Any]:
    if name not in PLATFORM_TOOL_NAMES:
        raise ValueError(f"Unknown platform tool: {name}")
    workspace_path = resolve_workspace(arguments.get("workspace_id"), None)
    meta = ensure_workspace_meta(workspace_path)
    workspace_id = str(meta["workspace_id"])
    codebase_id = str(arguments.get("codebase_id") or "").strip()
    if not codebase_id:
        return blocked(workspace_id=workspace_id, message="codebase_id is required", next_actions=["knowledge_codebase_list"], code="invalid_codebase_id")
    snapshot_id = str(arguments.get("snapshot_id") or "").strip() or None
    try:
        if name == "knowledge_code_platform_console_build":
            service = PlatformConsoleService(workspace_path, workspace_id=workspace_id)
            payload = service.build_console(codebase_id, snapshot_id=snapshot_id)
            data = {"platform_console": public_platform_console_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=payload.get("artifact_refs", []), next_actions=["knowledge_code_platform_console_read"], data=_with_v2(workspace_id, codebase_id, payload.get("snapshot_id"), data, payload.get("artifact_refs", []), warnings=payload.get("warnings", []), next_actions=payload.get("next_actions", [])))
        if name == "knowledge_code_platform_console_read":
            service = PlatformConsoleService(workspace_path, workspace_id=workspace_id)
            payload = service.read_console(codebase_id)
            data = {"platform_console": public_platform_console_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=payload.get("artifact_refs", []), data=_with_v2(workspace_id, codebase_id, payload.get("snapshot_id"), data, payload.get("artifact_refs", []), warnings=payload.get("warnings", []), next_actions=payload.get("next_actions", [])))
        if name == "knowledge_code_platform_console_view":
            service = PlatformConsoleService(workspace_path, workspace_id=workspace_id)
            payload = service.read_console_view(codebase_id, str(arguments.get("view_id") or "html"))
            data = {"platform_console_view": public_platform_console_view_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=payload.get("artifact_refs", []), data=_with_v2(workspace_id, codebase_id, None, data, payload.get("artifact_refs", [])))
        contract_service = ArtifactContractService(workspace_path, workspace_id=workspace_id)
        if name == "knowledge_code_platform_contracts_build":
            payload = contract_service.build_contracts(codebase_id)
            data = {"artifact_contracts": public_contract_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=payload.get("artifact_refs", []), next_actions=["knowledge_code_platform_contracts_read"], data=_with_v2(workspace_id, codebase_id, None, data, payload.get("artifact_refs", [])))
        if name == "knowledge_code_platform_contracts_read":
            payload = contract_service.read_contracts(codebase_id)
            data = {"artifact_contracts": public_contract_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=payload.get("artifact_refs", []), data=_with_v2(workspace_id, codebase_id, None, data, payload.get("artifact_refs", [])))
        catalog_service = ToolCatalogService(workspace_path, workspace_id=workspace_id)
        if name == "knowledge_code_platform_tool_catalog_build":
            if tool_specs_provider is None:
                from .mcp_tool_registry import all_tool_specs

                tool_specs_provider = all_tool_specs
            payload = catalog_service.build_tool_catalog(codebase_id, tool_specs_provider())
            data = {"tool_catalog": public_tool_catalog_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=payload.get("artifact_refs", []), next_actions=["knowledge_code_platform_tool_catalog_read"], data=_with_v2(workspace_id, codebase_id, None, data, payload.get("artifact_refs", [])))
        if name == "knowledge_code_platform_tool_catalog_read":
            payload = catalog_service.read_tool_catalog(codebase_id)
            data = {"tool_catalog": public_tool_catalog_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=payload.get("artifact_refs", []), data=_with_v2(workspace_id, codebase_id, None, data, payload.get("artifact_refs", [])))
        incremental_service = PlatformIncrementalService(workspace_path, workspace_id=workspace_id)
        if name == "knowledge_code_platform_incremental_build":
            payload = incremental_service.build_incremental_plan(
                codebase_id,
                from_snapshot_id=str(arguments.get("from_snapshot_id") or ""),
                to_snapshot_id=str(arguments.get("to_snapshot_id") or ""),
            )
            data = {"incremental_build": public_incremental_payload(payload)}
            plan = payload.get("plan", {})
            return envelope(workspace_id=workspace_id, artifact_refs=payload.get("artifact_refs", []), next_actions=["knowledge_code_platform_incremental_read"], data=_with_v2(workspace_id, codebase_id, plan.get("to_snapshot_id"), data, payload.get("artifact_refs", []), warnings=plan.get("warnings", []), next_actions=["knowledge_code_platform_incremental_read"]))
        if name == "knowledge_code_platform_incremental_read":
            payload = incremental_service.read_incremental_plan(codebase_id)
            data = {"incremental_build": public_incremental_payload(payload)}
            plan = payload.get("plan", {})
            return envelope(workspace_id=workspace_id, artifact_refs=payload.get("artifact_refs", []), data=_with_v2(workspace_id, codebase_id, plan.get("to_snapshot_id"), data, payload.get("artifact_refs", []), warnings=plan.get("warnings", [])))
        provider_service = PlatformProviderService(workspace_path, workspace_id=workspace_id)
        if name == "knowledge_code_platform_providers_build":
            payload = provider_service.build_provider_artifacts(codebase_id, snapshot_id=snapshot_id)
            data = {"provider_plugins": public_provider_payload(payload)}
            capabilities = payload.get("provider_capabilities", {})
            return envelope(workspace_id=workspace_id, artifact_refs=payload.get("artifact_refs", []), next_actions=["knowledge_code_platform_providers_read"], data=_with_v2(workspace_id, codebase_id, capabilities.get("snapshot_id"), data, payload.get("artifact_refs", []), warnings=capabilities.get("warnings", []), next_actions=["knowledge_code_platform_providers_read"]))
        if name == "knowledge_code_platform_providers_read":
            payload = provider_service.read_provider_artifacts(codebase_id)
            data = {"provider_plugins": public_provider_payload(payload)}
            capabilities = payload.get("provider_capabilities", {})
            return envelope(workspace_id=workspace_id, artifact_refs=payload.get("artifact_refs", []), data=_with_v2(workspace_id, codebase_id, capabilities.get("snapshot_id"), data, payload.get("artifact_refs", []), warnings=capabilities.get("warnings", [])))
        ci_service = PlatformCIReadinessService(workspace_path, workspace_id=workspace_id)
        if name == "knowledge_code_platform_ci_readiness_build":
            payload = ci_service.build_readiness(
                codebase_id,
                snapshot_id=snapshot_id,
                command_evidence=dict(arguments.get("command_evidence") or {}),
                warning_budget=int(arguments.get("warning_budget") or 700),
            )
            data = {"ci_readiness": public_ci_readiness_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=payload.get("artifact_refs", []), next_actions=["knowledge_code_platform_ci_readiness_read"], data=_with_v2(workspace_id, codebase_id, payload.get("snapshot_id"), data, payload.get("artifact_refs", []), warnings=payload.get("warnings", [])))
        if name == "knowledge_code_platform_ci_readiness_read":
            payload = ci_service.read_readiness(codebase_id)
            data = {"ci_readiness": public_ci_readiness_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=payload.get("artifact_refs", []), data=_with_v2(workspace_id, codebase_id, payload.get("snapshot_id"), data, payload.get("artifact_refs", []), warnings=payload.get("warnings", [])))
        if name == "knowledge_code_platform_ci_release_report":
            payload = ci_service.read_release_report(codebase_id)
            data = {"ci_release_report": public_release_report_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=payload.get("artifact_refs", []), data=_with_v2(workspace_id, codebase_id, None, data, payload.get("artifact_refs", [])))
        governance_service = PlatformGovernanceService(workspace_path, workspace_id=workspace_id)
        if name == "knowledge_code_platform_governance_feedback":
            payload = governance_service.record_feedback(
                codebase_id,
                target_type=str(arguments.get("target_type") or ""),
                target_id=str(arguments.get("target_id") or ""),
                action=str(arguments.get("action") or ""),
                rule_type=str(arguments.get("rule_type") or "read_time_overlay"),
                severity=str(arguments.get("severity") or "medium"),
                reason=str(arguments.get("reason") or ""),
                suggested_value=str(arguments.get("suggested_value") or ""),
            )
            data = {"platform_governance": public_governance_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=payload.get("artifact_refs", []), next_actions=["knowledge_code_platform_governance_rules_build"], data=_with_v2(workspace_id, codebase_id, None, data, payload.get("artifact_refs", []), next_actions=["knowledge_code_platform_governance_rules_build"]))
        if name == "knowledge_code_platform_governance_rules_build":
            payload = governance_service.build_rules(codebase_id)
            data = {"platform_governance": public_governance_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=payload.get("artifact_refs", []), next_actions=["knowledge_code_platform_governance_overlay"], data=_with_v2(workspace_id, codebase_id, None, data, payload.get("artifact_refs", []), next_actions=["knowledge_code_platform_governance_overlay"]))
        if name == "knowledge_code_platform_governance_rule_review":
            payload = governance_service.review_rule(
                codebase_id,
                str(arguments.get("rule_id") or ""),
                status=str(arguments.get("status") or ""),
                reviewer=str(arguments.get("reviewer") or ""),
                note=str(arguments.get("note") or ""),
            )
            data = {"platform_governance": public_governance_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=payload.get("artifact_refs", []), data=_with_v2(workspace_id, codebase_id, None, data, payload.get("artifact_refs", [])))
        report = governance_service.read_overlay_report(codebase_id)
        payload = {"overlay_report": report, "artifact_refs": report.get("artifact_refs", [])}
        data = {"platform_governance": public_governance_payload(payload)}
        return envelope(workspace_id=workspace_id, artifact_refs=payload.get("artifact_refs", []), data=_with_v2(workspace_id, codebase_id, None, data, payload.get("artifact_refs", []), warnings=report.get("warnings", [])))
    except FileNotFoundError as exc:
        return envelope(workspace_id=workspace_id, status="blocked", warnings=[str(exc)], next_actions=["knowledge_code_platform_console_build"], data={"error": {"code": str(exc), "message": str(exc), "retryable": False}, "v2": v2_error_envelope(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, code=str(exc), message=str(exc))})


def _with_v2(workspace_id: str, codebase_id: str, snapshot_id: str | None, data: dict[str, Any], refs: list[dict[str, Any]], *, warnings: list[Any] | None = None, next_actions: list[str] | None = None) -> dict[str, Any]:
    payload = dict(data)
    payload["v2"] = v2_success_envelope(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, data=data, artifact_refs=refs, warnings=warnings, next_actions=next_actions)
    return payload
