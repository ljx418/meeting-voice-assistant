"""V2.22 platform provider plugin contract builder."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from data_service.mcp_common import now

from ..coding_agent_v2_16.provider_registry import ProviderCapabilityRegistryService
from ..registry import CodebaseRegistry
from .persistence import (
    provider_artifact_refs,
    read_provider_capabilities,
    read_provider_execution_contract,
    write_provider_artifacts,
)


PROVIDER_SCHEMA_VERSION = "v2.22"


class PlatformProviderService:
    def __init__(self, workspace: Path, *, workspace_id: str) -> None:
        self.workspace = Path(workspace)
        self.workspace_id = workspace_id
        self.registry = CodebaseRegistry(workspace, workspace_id=workspace_id)

    def build_provider_artifacts(self, codebase_id: str, *, snapshot_id: str | None = None) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        source = ProviderCapabilityRegistryService(self.workspace, workspace_id=self.workspace_id).build_registry(codebase_id, snapshot_id=snapshot_id)
        providers = [_provider_capability(row) for row in source.get("providers", [])]
        refs = provider_artifact_refs(codebase_id)
        capabilities = {
            "schema_version": PROVIDER_SCHEMA_VERSION,
            "artifact_type": "provider_capabilities",
            "workspace_id": self.workspace_id,
            "codebase_id": codebase_id,
            "snapshot_id": source.get("snapshot_id"),
            "source_provider_registry_schema_version": source.get("schema_version"),
            "summary": _summary(providers),
            "providers": providers,
            "decision_records": source.get("decision_records", []),
            "warnings": source.get("warnings", []),
            "unresolved": [row for row in providers if row.get("status") != "ready"],
            "needs_review": _needs_review(providers),
            "artifact_refs": refs,
            "created_at": now(),
        }
        contract = _execution_contract(self.workspace_id, codebase_id, source.get("snapshot_id"), providers, refs)
        write_provider_artifacts(self.workspace, codebase_id, capabilities, contract)
        return {"provider_capabilities": capabilities, "provider_execution_contract": contract, "artifact_refs": refs}

    def read_provider_artifacts(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        return {
            "provider_capabilities": read_provider_capabilities(self.workspace, codebase_id),
            "provider_execution_contract": read_provider_execution_contract(self.workspace, codebase_id),
            "artifact_refs": provider_artifact_refs(codebase_id),
        }


def public_provider_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": PROVIDER_SCHEMA_VERSION,
        "artifact_type": "provider_plugin_bundle",
        "provider_capabilities": payload.get("provider_capabilities", {}),
        "provider_execution_contract": payload.get("provider_execution_contract", {}),
        "artifact_refs": payload.get("artifact_refs", []),
    }


def _provider_capability(row: dict[str, Any]) -> dict[str, Any]:
    provider_id = str(row.get("provider_id") or "")
    configured = bool(row.get("configured"))
    execution_supported = bool(row.get("execution_supported"))
    health_known = True
    mandatory = provider_id == "semantic:python_ast"
    ready = configured and execution_supported and str(row.get("status") or "") == "available"
    status = "ready" if ready else ("provider_unsupported" if configured and not execution_supported else str(row.get("status") or "provider_unavailable"))
    return {
        "provider_id": provider_id,
        "provider_name": row.get("provider_name"),
        "capability": row.get("capability"),
        "kind": row.get("kind"),
        "mandatory": mandatory,
        "health_known": health_known,
        "configured": configured,
        "execution_supported": execution_supported,
        "status": status,
        "accepted": ready,
        "reason": row.get("reason"),
        "reason_code": row.get("reason_code"),
        "evidence_refs": list(row.get("evidence_refs") or row.get("evidence") or []),
        "needs_review": list(row.get("needs_review") or ([] if ready else ["provider is not execution accepted"])),
        "next_actions": list(row.get("next_actions") or []),
    }


def _summary(providers: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "provider_count": len(providers),
        "ready_count": sum(1 for row in providers if row["status"] == "ready"),
        "mandatory_ready_count": sum(1 for row in providers if row["mandatory"] and row["status"] == "ready"),
        "optional_unavailable_count": sum(1 for row in providers if not row["mandatory"] and row["status"] == "provider_unavailable"),
        "unsupported_count": sum(1 for row in providers if row["status"] == "provider_unsupported"),
        "execution_supported_count": sum(1 for row in providers if row["execution_supported"]),
    }


def _needs_review(providers: list[dict[str, Any]]) -> list[str]:
    items = []
    if not any(row["provider_id"] == "semantic:python_ast" and row["status"] == "ready" for row in providers):
        items.append("mandatory python_ast provider is not ready")
    optional_accepted = [row["provider_id"] for row in providers if not row["mandatory"] and row["accepted"]]
    if optional_accepted:
        items.append("optional provider accepted; verify adapter evidence before relying on it")
    return items


def _execution_contract(workspace_id: str, codebase_id: str, snapshot_id: str | None, providers: list[dict[str, Any]], refs: list[dict[str, str]]) -> dict[str, Any]:
    return {
        "schema_version": PROVIDER_SCHEMA_VERSION,
        "artifact_type": "provider_execution_contract",
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "contract": {
            "request_fields": ["workspace_id", "codebase_id", "provider_id", "capability", "input_refs"],
            "result_fields": ["ok", "provider", "status", "output_refs", "confidence", "evidence_refs", "error", "warnings"],
            "error_fields": ["code", "message", "retryable"],
            "health_config_execution_separated": True,
        },
        "provider_execution": [
            {
                "provider_id": row["provider_id"],
                "health_known": row["health_known"],
                "configured": row["configured"],
                "execution_supported": row["execution_supported"],
                "execution_status": "execution_ready" if row["accepted"] else "execution_unavailable",
                "unsupported_reason": None if row["accepted"] else row.get("reason_code") or row.get("reason") or "PROVIDER_UNAVAILABLE",
            }
            for row in providers
        ],
        "public_error_codes": [
            "PROVIDER_UNAVAILABLE",
            "PROVIDER_UNSUPPORTED",
            "PROVIDER_MISSING_CREDENTIAL",
            "PROVIDER_AUTH_FAILED",
            "PROVIDER_TIMEOUT",
            "PROVIDER_EXECUTION_FAILED",
            "PROVIDER_OUTPUT_INVALID",
        ],
        "warnings": [],
        "artifact_refs": refs,
        "created_at": now(),
    }
