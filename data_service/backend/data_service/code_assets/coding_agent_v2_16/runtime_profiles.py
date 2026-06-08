"""V2.16 runtime profile manager."""

from __future__ import annotations

import hashlib
from typing import Any

from data_service.mcp_common import now

from .persistence import runtime_profile_artifact_refs


SCHEMA_VERSION = "v2.16"


def build_runtime_profiles_payload(*, workspace_id: str, codebase_id: str, snapshot_id: str, runtime_registry: dict[str, Any]) -> dict[str, Any]:
    profiles = []
    for command in runtime_registry.get("allowlisted_commands", []):
        profile_id = _stable_id("profile", codebase_id, snapshot_id, command.get("command_id"))
        profiles.append(
            {
                "profile_id": profile_id,
                "profile_type": command.get("command_type") or "runtime_validation",
                "label": command.get("label") or command.get("command_id"),
                "command_id": command.get("command_id"),
                "command_template": _public_command_template(command.get("command")),
                "allowed_args_policy": {"mode": "none", "user_args_allowed": False},
                "timeout_seconds": int(runtime_registry.get("policy", {}).get("timeout_seconds") or 20),
                "writes_source": False,
                "network": "disabled_by_policy",
                "status": "available",
                "evidence_refs": list(command.get("evidence_refs") or []),
            }
        )
    return {
        "schema_version": SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "profile_registry_id": _stable_id("profiles", codebase_id, snapshot_id, [item["profile_id"] for item in profiles]),
        "source_phase": "V2.16 Phase 78",
        "policy": {
            "default": "deny",
            "requires_profile_id": True,
            "user_args_allowed": False,
            "writes_source": False,
            "network": "disabled_by_policy",
        },
        "profiles": profiles,
        "summary": {
            "profile_count": len(profiles),
            "pytest_profile_count": sum(1 for item in profiles if item["profile_type"] == "pytest"),
            "syntax_profile_count": sum(1 for item in profiles if item["profile_type"] == "python_ast_check"),
        },
        "warnings": [] if profiles else [{"code": "NO_RUNTIME_PROFILES", "message": "No allowlisted runtime commands were available."}],
        "unresolved": [],
        "artifact_refs": runtime_profile_artifact_refs(codebase_id),
        "created_at": now(),
    }


def blocked_profile_run(*, workspace_id: str, codebase_id: str, snapshot_id: str | None, profile_id: str, reason: str = "RUNTIME_PROFILE_NOT_REGISTERED") -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "profile_run_id": _stable_id("profilerun", codebase_id, snapshot_id, profile_id, reason),
        "profile_id": profile_id,
        "command_id": None,
        "status": "blocked",
        "linked_runtime_run_id": None,
        "error": {"code": reason, "message": "Runtime profile is not registered and cannot be executed.", "retryable": False},
        "logs": {"redacted": True, "stdout_preview": "", "stderr_preview": ""},
        "warnings": [reason],
        "unresolved": [{"code": reason, "message": "Only registered profile_id values may be executed.", "retryable": False}],
        "artifact_refs": [],
        "created_at": now(),
    }


def profile_run_from_runtime(*, workspace_id: str, codebase_id: str, profile: dict[str, Any], runtime_run: dict[str, Any]) -> dict[str, Any]:
    profile_run_id = _stable_id("profilerun", codebase_id, runtime_run.get("snapshot_id"), profile.get("profile_id"), runtime_run.get("run_id"))
    return {
        "schema_version": SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": runtime_run.get("snapshot_id"),
        "profile_run_id": profile_run_id,
        "profile_id": profile.get("profile_id"),
        "profile_type": profile.get("profile_type"),
        "command_id": profile.get("command_id"),
        "status": runtime_run.get("status"),
        "exit_code": runtime_run.get("exit_code"),
        "linked_runtime_run_id": runtime_run.get("run_id"),
        "duration_ms": runtime_run.get("duration_ms"),
        "error": runtime_run.get("error"),
        "logs": runtime_run.get("logs", {}),
        "warnings": runtime_run.get("warnings", []),
        "unresolved": runtime_run.get("unresolved", []),
        "artifact_refs": runtime_profile_artifact_refs(codebase_id, profile_run_id) + list(runtime_run.get("artifact_refs") or []),
        "created_at": now(),
    }


def public_runtime_profiles_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return dict(payload)


def public_runtime_profile_run_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return dict(payload)


def _stable_id(prefix: str, *parts: Any) -> str:
    encoded = "|".join(str(part) for part in parts)
    return f"{prefix}_{hashlib.sha256(encoded.encode('utf-8')).hexdigest()[:20]}"


def _public_command_template(command: Any) -> str | None:
    if command is None:
        return None
    parts = str(command).split()
    if parts and parts[0].startswith("/"):
        parts[0] = "<runtime>"
    return " ".join(parts)
