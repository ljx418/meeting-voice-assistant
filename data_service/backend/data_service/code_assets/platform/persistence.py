"""Persistence helpers for V2.18 Platform Console artifacts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from data_service.mcp_common import read_json, write_json

from ..artifacts import codebase_dir, read_jsonl, write_jsonl


def platform_dir(workspace: Path, codebase_id: str) -> Path:
    return codebase_dir(workspace, codebase_id) / "platform"


def console_dir(workspace: Path, codebase_id: str) -> Path:
    return platform_dir(workspace, codebase_id) / "console"


def console_payload_path(workspace: Path, codebase_id: str) -> Path:
    return console_dir(workspace, codebase_id) / "platform_console.json"


def console_html_path(workspace: Path, codebase_id: str) -> Path:
    return console_dir(workspace, codebase_id) / "views" / "platform_console.html"


def console_artifact_refs(codebase_id: str) -> list[dict[str, str]]:
    return [
        {"type": "platform_console", "artifact_ref": f"platform://{codebase_id}/console/platform_console.json"},
        {"type": "platform_console_html", "artifact_ref": f"platform://{codebase_id}/console/views/platform_console.html"},
    ]


def contracts_dir(workspace: Path, codebase_id: str) -> Path:
    return platform_dir(workspace, codebase_id) / "contracts"


def contract_registry_path(workspace: Path, codebase_id: str) -> Path:
    return contracts_dir(workspace, codebase_id) / "artifact_contract_registry.json"


def validation_report_path(workspace: Path, codebase_id: str) -> Path:
    return contracts_dir(workspace, codebase_id) / "validation_report.json"


def contract_artifact_refs(codebase_id: str) -> list[dict[str, str]]:
    return [
        {"type": "artifact_contract_registry", "artifact_ref": f"platform://{codebase_id}/contracts/artifact_contract_registry.json"},
        {"type": "artifact_validation_report", "artifact_ref": f"platform://{codebase_id}/contracts/validation_report.json"},
    ]


def tool_catalog_dir(workspace: Path, codebase_id: str) -> Path:
    return platform_dir(workspace, codebase_id) / "tool_catalog"


def mcp_tool_catalog_path(workspace: Path, codebase_id: str) -> Path:
    return tool_catalog_dir(workspace, codebase_id) / "mcp_tool_catalog.json"


def workflow_guides_path(workspace: Path, codebase_id: str) -> Path:
    return tool_catalog_dir(workspace, codebase_id) / "workflow_guides.json"


def tool_catalog_artifact_refs(codebase_id: str) -> list[dict[str, str]]:
    return [
        {"type": "mcp_tool_catalog", "artifact_ref": f"platform://{codebase_id}/tool_catalog/mcp_tool_catalog.json"},
        {"type": "workflow_guides", "artifact_ref": f"platform://{codebase_id}/tool_catalog/workflow_guides.json"},
    ]


def incremental_dir(workspace: Path, codebase_id: str) -> Path:
    return platform_dir(workspace, codebase_id) / "incremental"


def incremental_build_plan_path(workspace: Path, codebase_id: str) -> Path:
    return incremental_dir(workspace, codebase_id) / "incremental_build_plan.json"


def cache_decisions_path(workspace: Path, codebase_id: str) -> Path:
    return incremental_dir(workspace, codebase_id) / "cache_decisions.jsonl"


def scan_profile_path(workspace: Path, codebase_id: str) -> Path:
    return incremental_dir(workspace, codebase_id) / "scan_profile.json"


def incremental_artifact_refs(codebase_id: str) -> list[dict[str, str]]:
    return [
        {"type": "incremental_build_plan", "artifact_ref": f"platform://{codebase_id}/incremental/incremental_build_plan.json"},
        {"type": "cache_decisions", "artifact_ref": f"platform://{codebase_id}/incremental/cache_decisions.jsonl"},
        {"type": "scan_profile", "artifact_ref": f"platform://{codebase_id}/incremental/scan_profile.json"},
    ]


def providers_dir(workspace: Path, codebase_id: str) -> Path:
    return platform_dir(workspace, codebase_id) / "providers"


def provider_capabilities_path(workspace: Path, codebase_id: str) -> Path:
    return providers_dir(workspace, codebase_id) / "provider_capabilities.json"


def provider_execution_contract_path(workspace: Path, codebase_id: str) -> Path:
    return providers_dir(workspace, codebase_id) / "provider_execution_contract.json"


def provider_artifact_refs(codebase_id: str) -> list[dict[str, str]]:
    return [
        {"type": "provider_capabilities", "artifact_ref": f"platform://{codebase_id}/providers/provider_capabilities.json"},
        {"type": "provider_execution_contract", "artifact_ref": f"platform://{codebase_id}/providers/provider_execution_contract.json"},
    ]


def governance_dir(workspace: Path, codebase_id: str) -> Path:
    return platform_dir(workspace, codebase_id) / "governance"


def governance_feedback_path(workspace: Path, codebase_id: str) -> Path:
    return governance_dir(workspace, codebase_id) / "feedback.jsonl"


def governance_rules_path(workspace: Path, codebase_id: str) -> Path:
    return governance_dir(workspace, codebase_id) / "rules.jsonl"


def governance_overlay_report_path(workspace: Path, codebase_id: str) -> Path:
    return governance_dir(workspace, codebase_id) / "overlay_report.json"


def governance_artifact_refs(codebase_id: str) -> list[dict[str, str]]:
    return [
        {"type": "platform_governance_feedback", "artifact_ref": f"platform://{codebase_id}/governance/feedback.jsonl"},
        {"type": "platform_governance_rules", "artifact_ref": f"platform://{codebase_id}/governance/rules.jsonl"},
        {"type": "platform_governance_overlay_report", "artifact_ref": f"platform://{codebase_id}/governance/overlay_report.json"},
    ]


def ci_dir(workspace: Path, codebase_id: str) -> Path:
    return platform_dir(workspace, codebase_id) / "ci"


def ci_readiness_report_path(workspace: Path, codebase_id: str) -> Path:
    return ci_dir(workspace, codebase_id) / "ci_readiness_report.json"


def release_readiness_report_path(workspace: Path, codebase_id: str) -> Path:
    return ci_dir(workspace, codebase_id) / "release_readiness_report.md"


def ci_artifact_refs(codebase_id: str) -> list[dict[str, str]]:
    return [
        {"type": "ci_readiness_report", "artifact_ref": f"platform://{codebase_id}/ci/ci_readiness_report.json"},
        {"type": "release_readiness_report", "artifact_ref": f"platform://{codebase_id}/ci/release_readiness_report.md"},
    ]


def write_console(workspace: Path, codebase_id: str, payload: dict[str, Any], html: str) -> None:
    write_json(console_payload_path(workspace, codebase_id), payload)
    console_html_path(workspace, codebase_id).parent.mkdir(parents=True, exist_ok=True)
    console_html_path(workspace, codebase_id).write_text(html, encoding="utf-8")


def read_console(workspace: Path, codebase_id: str) -> dict[str, Any]:
    payload = read_json(console_payload_path(workspace, codebase_id), None)
    if not payload:
        raise FileNotFoundError("PLATFORM_CONSOLE_NOT_FOUND")
    return payload


def write_contracts(workspace: Path, codebase_id: str, registry: dict[str, Any], report: dict[str, Any]) -> None:
    write_json(contract_registry_path(workspace, codebase_id), registry)
    write_json(validation_report_path(workspace, codebase_id), report)


def read_contract_registry(workspace: Path, codebase_id: str) -> dict[str, Any]:
    payload = read_json(contract_registry_path(workspace, codebase_id), None)
    if not payload:
        raise FileNotFoundError("ARTIFACT_CONTRACT_REGISTRY_NOT_FOUND")
    return payload


def read_validation_report(workspace: Path, codebase_id: str) -> dict[str, Any]:
    payload = read_json(validation_report_path(workspace, codebase_id), None)
    if not payload:
        raise FileNotFoundError("ARTIFACT_VALIDATION_REPORT_NOT_FOUND")
    return payload


def write_tool_catalog(workspace: Path, codebase_id: str, catalog: dict[str, Any], guides: dict[str, Any]) -> None:
    write_json(mcp_tool_catalog_path(workspace, codebase_id), catalog)
    write_json(workflow_guides_path(workspace, codebase_id), guides)


def read_tool_catalog(workspace: Path, codebase_id: str) -> dict[str, Any]:
    payload = read_json(mcp_tool_catalog_path(workspace, codebase_id), None)
    if not payload:
        raise FileNotFoundError("MCP_TOOL_CATALOG_NOT_FOUND")
    return payload


def read_workflow_guides(workspace: Path, codebase_id: str) -> dict[str, Any]:
    payload = read_json(workflow_guides_path(workspace, codebase_id), None)
    if not payload:
        raise FileNotFoundError("WORKFLOW_GUIDES_NOT_FOUND")
    return payload


def write_incremental_plan(workspace: Path, codebase_id: str, plan: dict[str, Any], decisions: list[dict[str, Any]], scan_profile: dict[str, Any]) -> None:
    write_json(incremental_build_plan_path(workspace, codebase_id), plan)
    write_jsonl(cache_decisions_path(workspace, codebase_id), decisions)
    write_json(scan_profile_path(workspace, codebase_id), scan_profile)


def read_incremental_plan(workspace: Path, codebase_id: str) -> dict[str, Any]:
    payload = read_json(incremental_build_plan_path(workspace, codebase_id), None)
    if not payload:
        raise FileNotFoundError("INCREMENTAL_BUILD_PLAN_NOT_FOUND")
    return payload


def read_cache_decisions(workspace: Path, codebase_id: str) -> list[dict[str, Any]]:
    path = cache_decisions_path(workspace, codebase_id)
    if not path.exists():
        raise FileNotFoundError("CACHE_DECISIONS_NOT_FOUND")
    return read_jsonl(path)


def read_scan_profile(workspace: Path, codebase_id: str) -> dict[str, Any]:
    payload = read_json(scan_profile_path(workspace, codebase_id), None)
    if not payload:
        raise FileNotFoundError("SCAN_PROFILE_NOT_FOUND")
    return payload


def write_provider_artifacts(workspace: Path, codebase_id: str, capabilities: dict[str, Any], contract: dict[str, Any]) -> None:
    write_json(provider_capabilities_path(workspace, codebase_id), capabilities)
    write_json(provider_execution_contract_path(workspace, codebase_id), contract)


def read_provider_capabilities(workspace: Path, codebase_id: str) -> dict[str, Any]:
    payload = read_json(provider_capabilities_path(workspace, codebase_id), None)
    if not payload:
        raise FileNotFoundError("PROVIDER_CAPABILITIES_NOT_FOUND")
    return payload


def read_provider_execution_contract(workspace: Path, codebase_id: str) -> dict[str, Any]:
    payload = read_json(provider_execution_contract_path(workspace, codebase_id), None)
    if not payload:
        raise FileNotFoundError("PROVIDER_EXECUTION_CONTRACT_NOT_FOUND")
    return payload


def write_governance_feedback(workspace: Path, codebase_id: str, rows: list[dict[str, Any]]) -> None:
    write_jsonl(governance_feedback_path(workspace, codebase_id), rows)


def read_governance_feedback(workspace: Path, codebase_id: str) -> list[dict[str, Any]]:
    return read_jsonl(governance_feedback_path(workspace, codebase_id))


def write_governance_rules(workspace: Path, codebase_id: str, rows: list[dict[str, Any]]) -> None:
    write_jsonl(governance_rules_path(workspace, codebase_id), rows)


def read_governance_rules(workspace: Path, codebase_id: str) -> list[dict[str, Any]]:
    return read_jsonl(governance_rules_path(workspace, codebase_id))


def write_governance_overlay_report(workspace: Path, codebase_id: str, payload: dict[str, Any]) -> None:
    write_json(governance_overlay_report_path(workspace, codebase_id), payload)


def read_governance_overlay_report(workspace: Path, codebase_id: str) -> dict[str, Any]:
    payload = read_json(governance_overlay_report_path(workspace, codebase_id), None)
    if not payload:
        raise FileNotFoundError("PLATFORM_GOVERNANCE_OVERLAY_NOT_FOUND")
    return payload


def write_ci_readiness_report(workspace: Path, codebase_id: str, payload: dict[str, Any], markdown: str) -> None:
    write_json(ci_readiness_report_path(workspace, codebase_id), payload)
    release_readiness_report_path(workspace, codebase_id).parent.mkdir(parents=True, exist_ok=True)
    release_readiness_report_path(workspace, codebase_id).write_text(markdown, encoding="utf-8")


def read_ci_readiness_report(workspace: Path, codebase_id: str) -> dict[str, Any]:
    payload = read_json(ci_readiness_report_path(workspace, codebase_id), None)
    if not payload:
        raise FileNotFoundError("CI_READINESS_NOT_BUILT")
    return payload


def read_release_readiness_report(workspace: Path, codebase_id: str) -> str:
    path = release_readiness_report_path(workspace, codebase_id)
    if not path.exists():
        raise FileNotFoundError("CI_READINESS_NOT_BUILT")
    return path.read_text(encoding="utf-8")
