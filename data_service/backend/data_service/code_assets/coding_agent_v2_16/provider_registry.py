"""V2.16 provider capability registry.

The registry is deliberately descriptive. It reports what is known,
configured, supported by this service, and safe to execute. It does not call
external providers or expose local secrets/endpoints.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import shutil
from pathlib import Path
from typing import Any

from data_service.mcp_common import now

from ..registry import CodebaseRegistry
from ..snapshot import CodebaseSnapshotService
from .persistence import provider_registry_artifact_refs, read_provider_registry, write_provider_registry


SCHEMA_VERSION = "v2.16"
SOURCE_PHASE = "V2.16 Phase 76"
PROVIDER_STATUSES = {
    "available",
    "provider_unavailable",
    "provider_unsupported",
    "provider_missing_credential",
    "provider_auth_failed",
    "provider_timeout",
    "provider_execution_failed",
}
PUBLIC_REASON_CODES = {
    "available": None,
    "provider_unavailable": "PROVIDER_UNAVAILABLE",
    "provider_unsupported": "PROVIDER_UNSUPPORTED",
    "provider_missing_credential": "PROVIDER_MISSING_CREDENTIAL",
    "provider_auth_failed": "PROVIDER_AUTH_FAILED",
    "provider_timeout": "PROVIDER_TIMEOUT",
    "provider_execution_failed": "PROVIDER_EXECUTION_FAILED",
}


class ProviderCapabilityRegistryService:
    def __init__(self, workspace: Path, *, workspace_id: str) -> None:
        self.workspace = Path(workspace)
        self.workspace_id = workspace_id
        self.registry = CodebaseRegistry(workspace, workspace_id=workspace_id)
        self.snapshots = CodebaseSnapshotService(workspace, workspace_id=workspace_id)

    def build_registry(self, codebase_id: str, *, snapshot_id: str | None = None) -> dict[str, Any]:
        asset = self.registry.describe(codebase_id)
        if asset.status != "active":
            raise ValueError("CODEBASE_NOT_ACTIVE")
        resolved_snapshot_id = snapshot_id or self._latest_snapshot_id(codebase_id)
        self.snapshots.read_snapshot(codebase_id, resolved_snapshot_id)

        created_at = now()
        providers = _build_provider_matrix(created_at=created_at)
        decisions = _build_decisions(
            workspace_id=self.workspace_id,
            codebase_id=codebase_id,
            snapshot_id=resolved_snapshot_id,
            providers=providers,
            created_at=created_at,
        )
        decision_ids = [str(item["decision_id"]) for item in decisions]
        refs = provider_registry_artifact_refs(codebase_id, decision_ids)
        summary = _summary(providers, decisions)
        warnings = _warnings(providers)
        next_actions = _next_actions(providers)
        payload = {
            "schema_version": SCHEMA_VERSION,
            "workspace_id": self.workspace_id,
            "codebase_id": codebase_id,
            "snapshot_id": resolved_snapshot_id,
            "created_at": created_at,
            "source_phase": SOURCE_PHASE,
            "summary": summary,
            "providers": providers,
            "decision_records": decisions,
            "warnings": warnings,
            "unresolved": [item for item in providers if item["status"] != "available"],
            "next_actions": next_actions,
            "artifact_refs": refs,
            "evidence_refs": [
                f"snapshot://{codebase_id}/{resolved_snapshot_id}",
                f"codebase://{codebase_id}",
            ],
            "needs_review": [] if summary["available_count"] else ["no provider is currently available"],
        }
        write_provider_registry(self.workspace, codebase_id, payload)
        return payload

    def read_registry(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        return read_provider_registry(self.workspace, codebase_id)

    def _latest_snapshot_id(self, codebase_id: str) -> str:
        snapshots = self.snapshots.list_snapshots(codebase_id, limit=1)
        if not snapshots:
            raise FileNotFoundError("SNAPSHOT_NOT_FOUND")
        return str(snapshots[0]["snapshot_id"])


def _build_provider_matrix(*, created_at: str) -> list[dict[str, Any]]:
    return [
        _provider(
            "semantic:python_ast",
            "python_ast",
            "semantic_index",
            "local",
            configured=True,
            execution_supported=True,
            status="available",
            reason="mandatory baseline provider available in the Python standard library",
            evidence=["python_stdlib:ast"],
            created_at=created_at,
            next_actions=[],
        ),
        _optional_import_provider(
            provider_id="semantic:tree_sitter",
            provider_name="tree_sitter",
            package="tree_sitter",
            capability="semantic_index",
            adapter_supported=False,
            created_at=created_at,
        ),
        _optional_import_provider(
            provider_id="semantic:jedi",
            provider_name="jedi",
            package="jedi",
            capability="semantic_index",
            adapter_supported=False,
            created_at=created_at,
        ),
        _provider(
            "semantic:lsp",
            "language_server_protocol",
            "semantic_index",
            "local",
            configured=bool(shutil.which("pyright-langserver") or shutil.which("pylsp")),
            execution_supported=False,
            status="provider_unsupported",
            reason="provider is known but no execution adapter is wired in Phase 76",
            reason_code="PROVIDER_UNSUPPORTED",
            evidence=[],
            needs_review=["provider adapter must be implemented before execution"],
            created_at=created_at,
            next_actions=["implement_lsp_adapter"],
        ),
        _provider(
            "runtime:local_profile_runner",
            "local_profile_runner",
            "runtime_profile",
            "local",
            configured=True,
            execution_supported=True,
            status="available",
            reason="local allowlist runtime is supported by the V2.13 baseline",
            evidence=["coding-agent:v2.13-runtime-registry"],
            created_at=created_at,
            next_actions=[],
        ),
        _provider(
            "patch:sandbox_preview",
            "sandbox_preview",
            "patch_preview",
            "local",
            configured=True,
            execution_supported=True,
            status="available",
            reason="read-only sandbox preview capability is supported for planning",
            evidence=["coding-agent:v2.12-patch-plan"],
            created_at=created_at,
            next_actions=[],
        ),
        _external_credential_provider(
            provider_id="external:llm_review",
            provider_name="external_llm_review",
            capability="review_assistance",
            env_names=["OPENAI_API_KEY", "ANTHROPIC_API_KEY", "MINIMAX_API_KEY"],
            created_at=created_at,
        ),
    ]


def _optional_import_provider(
    *,
    provider_id: str,
    provider_name: str,
    package: str,
    capability: str,
    adapter_supported: bool,
    created_at: str,
) -> dict[str, Any]:
    configured = importlib.util.find_spec(package) is not None
    if not configured:
        return _provider(
            provider_id,
            provider_name,
            capability,
            "local",
            configured=False,
            execution_supported=adapter_supported,
            status="provider_unavailable",
            reason="optional provider package is not installed",
            reason_code="PROVIDER_UNAVAILABLE",
            evidence=[],
            needs_review=["install provider package and implement adapter before accepting results"],
            created_at=created_at,
            next_actions=[f"install_{provider_name}", f"implement_{provider_name}_adapter"],
        )
    if not adapter_supported:
        return _provider(
            provider_id,
            provider_name,
            capability,
            "local",
            configured=True,
            execution_supported=False,
            status="provider_unsupported",
            reason="provider package is importable but this service has no execution adapter for it",
            reason_code="PROVIDER_UNSUPPORTED",
            evidence=[f"python_import:{package}"],
            needs_review=["adapter is required before this provider can be accepted"],
            created_at=created_at,
            next_actions=[f"implement_{provider_name}_adapter"],
        )
    return _provider(
        provider_id,
        provider_name,
        capability,
        "local",
        configured=True,
        execution_supported=True,
        status="available",
        reason="provider package and execution adapter are available",
        evidence=[f"python_import:{package}"],
        created_at=created_at,
        next_actions=[],
    )


def _external_credential_provider(
    *,
    provider_id: str,
    provider_name: str,
    capability: str,
    env_names: list[str],
    created_at: str,
) -> dict[str, Any]:
    configured = any(bool(os.environ.get(name)) for name in env_names)
    if not configured:
        return _provider(
            provider_id,
            provider_name,
            capability,
            "external",
            configured=False,
            execution_supported=False,
            status="provider_missing_credential",
            reason="no supported external provider credential is configured",
            reason_code="PROVIDER_MISSING_CREDENTIAL",
            evidence=[],
            needs_review=["configure an external provider credential before enabling execution"],
            created_at=created_at,
            next_actions=["configure_external_provider_credential"],
        )
    return _provider(
        provider_id,
        provider_name,
        capability,
        "external",
        configured=True,
        execution_supported=False,
        status="provider_unsupported",
        reason="credential presence is known, but external execution adapter is not enabled in Phase 76",
        reason_code="PROVIDER_UNSUPPORTED",
        evidence=["env:credential_present"],
        needs_review=["external adapter and policy review required before execution"],
        created_at=created_at,
        next_actions=["implement_external_provider_adapter", "complete_provider_policy_review"],
    )


def _provider(
    provider_id: str,
    provider_name: str,
    capability: str,
    kind: str,
    *,
    configured: bool,
    execution_supported: bool,
    status: str,
    reason: str,
    created_at: str,
    evidence: list[str] | None = None,
    reason_code: str | None = None,
    needs_review: list[str] | None = None,
    next_actions: list[str] | None = None,
) -> dict[str, Any]:
    if status not in PROVIDER_STATUSES:
        raise ValueError(f"Invalid provider status: {status}")
    available = status == "available" and configured and execution_supported
    accepted = available
    return {
        "schema_version": SCHEMA_VERSION,
        "provider_id": provider_id,
        "provider_name": provider_name,
        "capability": capability,
        "kind": kind,
        "known": True,
        "configured": bool(configured),
        "execution_supported": bool(execution_supported),
        "available": available,
        "accepted": accepted,
        "status": status,
        "reason_code": reason_code or PUBLIC_REASON_CODES.get(status),
        "reason": reason,
        "evidence": list(evidence or []),
        "needs_review": list(needs_review or ([] if accepted else [reason])),
        "next_actions": list(next_actions or []),
        "created_at": created_at,
    }


def _build_decisions(
    *,
    workspace_id: str,
    codebase_id: str,
    snapshot_id: str,
    providers: list[dict[str, Any]],
    created_at: str,
) -> list[dict[str, Any]]:
    semantic = [item for item in providers if item["capability"] == "semantic_index"]
    selected = next(item for item in semantic if item["provider_id"] == "semantic:python_ast")
    unsupported = [item["provider_id"] for item in semantic if item.get("reason_code") == "PROVIDER_UNSUPPORTED"]
    unavailable = [item["provider_id"] for item in semantic if item["status"] != "available"]
    semantic_decision = {
        "schema_version": SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "decision_id": _stable_id("decision", codebase_id, snapshot_id, "semantic_index", selected["provider_id"]),
        "capability": "semantic_index",
        "selected_provider": selected["provider_id"],
        "decision": "accepted_baseline",
        "reason": "python_ast is the mandatory deterministic baseline; optional semantic providers are not accepted unless available and adapter-supported",
        "real_fixture_evidence": [f"snapshot://{codebase_id}/{snapshot_id}"],
        "unsupported_providers": unsupported,
        "unavailable_providers": unavailable,
        "created_at": created_at,
        "source_phase": SOURCE_PHASE,
        "evidence_refs": [f"provider://{selected['provider_id']}"],
        "needs_review": [] if not unavailable else ["optional semantic providers remain unavailable or unsupported"],
    }
    external = [item for item in providers if item["kind"] == "external"]
    external_decision = {
        "schema_version": SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "decision_id": _stable_id("decision", codebase_id, snapshot_id, "external_provider_execution"),
        "capability": "review_assistance",
        "selected_provider": None,
        "decision": "provider_unavailable" if any(item["status"] == "provider_missing_credential" for item in external) else "out_of_scope",
        "reason": "external provider execution is not enabled by Phase 76 registry; credentials and endpoints are never exposed",
        "real_fixture_evidence": [f"snapshot://{codebase_id}/{snapshot_id}"],
        "unsupported_providers": [item["provider_id"] for item in external if item.get("reason_code") == "PROVIDER_UNSUPPORTED"],
        "unavailable_providers": [item["provider_id"] for item in external if item["status"] != "available"],
        "created_at": created_at,
        "source_phase": SOURCE_PHASE,
        "evidence_refs": [],
        "needs_review": ["provider policy and adapter review required before external execution"],
    }
    return [semantic_decision, external_decision]


def _summary(providers: list[dict[str, Any]], decisions: list[dict[str, Any]]) -> dict[str, Any]:
    by_status: dict[str, int] = {}
    by_kind: dict[str, int] = {}
    for item in providers:
        by_status[item["status"]] = by_status.get(item["status"], 0) + 1
        by_kind[item["kind"]] = by_kind.get(item["kind"], 0) + 1
    return {
        "provider_count": len(providers),
        "known_count": sum(1 for item in providers if item["known"]),
        "configured_count": sum(1 for item in providers if item["configured"]),
        "execution_supported_count": sum(1 for item in providers if item["execution_supported"]),
        "available_count": sum(1 for item in providers if item["available"]),
        "accepted_count": sum(1 for item in providers if item["accepted"]),
        "unavailable_count": sum(1 for item in providers if item["status"] != "available"),
        "unsupported_count": sum(1 for item in providers if item["status"] == "provider_unsupported"),
        "missing_credential_count": sum(1 for item in providers if item["status"] == "provider_missing_credential"),
        "by_status": dict(sorted(by_status.items())),
        "by_kind": dict(sorted(by_kind.items())),
        "decision_count": len(decisions),
    }


def _warnings(providers: list[dict[str, Any]]) -> list[str]:
    warnings = []
    if any(item["status"] == "provider_missing_credential" for item in providers):
        warnings.append("external provider credential is missing")
    if any(item["status"] == "provider_unsupported" for item in providers):
        warnings.append("one or more known providers have no execution adapter")
    if any(item["status"] == "provider_unavailable" for item in providers):
        warnings.append("one or more optional providers are unavailable")
    return sorted(warnings)


def _next_actions(providers: list[dict[str, Any]]) -> list[str]:
    actions: list[str] = []
    for item in providers:
        actions.extend(str(action) for action in item.get("next_actions", []) if str(action))
    return sorted(set(actions))


def _stable_id(*parts: Any) -> str:
    digest = hashlib.sha256(json.dumps(parts, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()[:16]
    return f"decision_{digest}"


def public_provider_registry_payload(payload: dict[str, Any]) -> dict[str, Any]:
    result = {
        "schema_version": payload.get("schema_version", SCHEMA_VERSION),
        "workspace_id": payload.get("workspace_id"),
        "codebase_id": payload.get("codebase_id"),
        "snapshot_id": payload.get("snapshot_id"),
        "created_at": payload.get("created_at"),
        "source_phase": payload.get("source_phase", SOURCE_PHASE),
        "summary": dict(payload.get("summary") or {}),
        "providers": [dict(item) for item in payload.get("providers", [])],
        "decision_records": [dict(item) for item in payload.get("decision_records", [])],
        "warnings": list(payload.get("warnings") or []),
        "unresolved": [dict(item) for item in payload.get("unresolved", [])],
        "next_actions": list(payload.get("next_actions") or []),
        "artifact_refs": list(payload.get("artifact_refs") or []),
        "evidence_refs": list(payload.get("evidence_refs") or []),
        "needs_review": list(payload.get("needs_review") or []),
    }
    return result
