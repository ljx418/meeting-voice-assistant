"""Human-gated patch sandbox preview for V2.16."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from data_service.mcp_common import now

from .persistence import patch_preview_artifact_refs


SCHEMA_VERSION = "v2.16"


def build_patch_preview_payload(
    *,
    workspace_id: str,
    codebase_id: str,
    snapshot_id: str | None,
    patch_plan: dict[str, Any],
    repo_root: Path,
) -> tuple[dict[str, Any], str]:
    candidates = patch_plan.get("edit_candidates", [])[:10]
    preview_id = _stable_id("preview", codebase_id, snapshot_id, patch_plan.get("patch_plan_id"), [item.get("target_id") for item in candidates])
    target_hashes = [_file_hash(repo_root, str(item.get("path") or item.get("source_file") or "")) for item in candidates]
    diff_text = _render_preview_diff(candidates)
    payload = {
        "schema_version": SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "preview_id": preview_id,
        "source_phase": "V2.16 Phase 81",
        "source_patch_plan_id": patch_plan.get("patch_plan_id"),
        "mutates_source": False,
        "approval_state": {
            "status": "approval_required",
            "required_for": "patch_apply",
            "approved": False,
        },
        "summary": {
            "candidate_count": len(candidates),
            "diff_available": bool(diff_text),
            "rollback_step_count": len(candidates),
            "validation_profile_count": len(patch_plan.get("validation_plan", [])),
        },
        "target_hashes_before": target_hashes,
        "diff_ref": f"coding-agent://{codebase_id}/v2_16/patch_sandbox/diffs/{preview_id}.diff",
        "rollback_plan": [
            {
                "path": target_hashes[index].get("path"),
                "action": "restore_original_content_before_apply",
                "source_hash": target_hashes[index].get("sha256"),
            }
            for index, item in enumerate(candidates)
        ],
        "validation_profiles": patch_plan.get("validation_plan", []),
        "evidence_refs": patch_plan.get("evidence", []) or patch_plan.get("artifact_refs", []),
        "warnings": [],
        "unresolved": [{"code": "PATCH_APPLY_REQUIRES_HUMAN_APPROVAL", "message": "Preview is read-only. Apply is blocked until human approval is provided.", "retryable": False}],
        "artifact_refs": patch_preview_artifact_refs(codebase_id, preview_id),
        "created_at": now(),
    }
    return payload, diff_text


def blocked_patch_apply(*, workspace_id: str, codebase_id: str, preview_id: str) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "preview_id": preview_id,
        "status": "blocked",
        "mutates_source": False,
        "approval_state": {"status": "approval_required", "approved": False},
        "error": {
            "code": "PATCH_APPLY_REQUIRES_HUMAN_APPROVAL",
            "message": "Patch apply is blocked until explicit human approval is implemented and granted.",
            "retryable": False,
        },
        "artifact_refs": [],
        "warnings": ["PATCH_APPLY_REQUIRES_HUMAN_APPROVAL"],
        "unresolved": [{"code": "PATCH_APPLY_REQUIRES_HUMAN_APPROVAL", "message": "No source files were modified.", "retryable": False}],
    }


def public_patch_preview_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return dict(payload)


def _render_preview_diff(candidates: list[dict[str, Any]]) -> str:
    lines = ["# V2.16 read-only patch preview", "# This is not applied to source files."]
    for item in candidates:
        path = item.get("path") or item.get("source_file") or "unknown"
        lines.extend(
            [
                f"--- a/{path}",
                f"+++ b/{path}",
                f"@@ preview:{item.get('target_id', 'candidate')} @@",
                f"+# Suggested action: {item.get('action', 'inspect_or_modify')}",
            ]
        )
    return "\n".join(lines) + "\n"


def _file_hash(repo_root: Path, path_text: str) -> dict[str, Any]:
    candidate = Path(path_text)
    if not path_text or candidate.is_absolute() or ".." in candidate.parts:
        return {"path": "<invalid-target>", "exists": False, "sha256": None, "warning": "invalid repo-relative target path"}
    resolved = (repo_root / candidate).resolve()
    try:
        relative = resolved.relative_to(repo_root)
    except ValueError:
        return {"path": "<invalid-target>", "exists": False, "sha256": None, "warning": "target path escapes repo root"}
    if not resolved.exists() or not resolved.is_file():
        return {"path": relative.as_posix(), "exists": False, "sha256": None}
    return {"path": relative.as_posix(), "exists": True, "sha256": hashlib.sha256(resolved.read_bytes()).hexdigest()}


def _stable_id(prefix: str, *parts: Any) -> str:
    return f"{prefix}_{hashlib.sha256('|'.join(str(part) for part in parts).encode('utf-8')).hexdigest()[:20]}"
