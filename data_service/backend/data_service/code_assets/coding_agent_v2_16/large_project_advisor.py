"""Generic large-project abstraction advisor for V2.16."""

from __future__ import annotations

import hashlib
from typing import Any

from data_service.mcp_common import now

from .persistence import large_project_advisor_artifact_refs


SCHEMA_VERSION = "v2.16"


def build_large_project_advisor_payload(
    *,
    workspace_id: str,
    codebase_id: str,
    snapshot_id: str,
    files: list[dict[str, Any]],
    semantic_index: dict[str, Any],
    workbench_v2: dict[str, Any],
) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
    adapters = _adapter_catalog()
    accepted, needs_review, blockers = _evaluate_adapters(codebase_id, snapshot_id, files, semantic_index, adapters)
    payload = {
        "schema_version": SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "advisor_id": _stable_id("largeadvisor", codebase_id, snapshot_id, len(files), len(accepted), len(blockers)),
        "source_phase": "V2.16 Phase 80",
        "scale_profile": _scale_profile(files),
        "summary": {
            "generic_adapter_count": len(adapters),
            "accepted_pattern_count": len(accepted),
            "needs_review_count": len(needs_review),
            "blocker_count": len(blockers),
            "workbench_blocker_count": workbench_v2.get("summary", {}).get("blocker_count", 0),
        },
        "accepted_patterns": accepted,
        "needs_review_patterns": needs_review,
        "blockers": blockers,
        "generic_pattern_adapters": adapters,
        "warnings": [],
        "unresolved": blockers,
        "artifact_refs": large_project_advisor_artifact_refs(codebase_id),
        "created_at": now(),
    }
    return payload, adapters, blockers


def public_large_project_advisor_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return dict(payload)


def _adapter_catalog() -> list[dict[str, Any]]:
    return [
        {"adapter_id": "generic_python_backend", "role": "backend", "required_path_suffixes": [".py"], "required_terms": ["backend", "data_service", "app"]},
        {"adapter_id": "generic_http_api_surface", "role": "public_interface", "required_path_terms": ["api"], "required_terms": ["route", "router", "endpoint"]},
        {"adapter_id": "generic_mcp_tool_surface", "role": "agent_interface", "required_path_terms": ["mcp"], "required_terms": ["tool", "dispatcher", "registry"]},
        {"adapter_id": "generic_cli_surface", "role": "operator_interface", "required_path_terms": ["cli", "__main__"], "required_terms": ["argparse", "command"]},
        {"adapter_id": "generic_test_boundary", "role": "validation", "required_path_terms": ["test"], "required_terms": ["pytest", "test"]},
        {"adapter_id": "generic_architecture_docs", "role": "documentation", "required_path_suffixes": [".md", ".drawio"], "required_terms": ["architecture", "prd", "design"]},
    ]


def _evaluate_adapters(codebase_id: str, snapshot_id: str, files: list[dict[str, Any]], semantic_index: dict[str, Any], adapters: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    paths = [str(row.get("path") or "") for row in files if row.get("included", True)]
    semantic_facts = semantic_index.get("provider_facts", [])
    fact_paths = {str(fact.get("source_file") or "") for fact in semantic_facts if fact.get("status") == "accepted"}
    accepted = []
    review = []
    blockers = []
    for adapter in adapters:
        matched_paths = _matching_paths(paths, adapter)
        evidence_paths = [path for path in matched_paths if path in fact_paths][:10]
        if evidence_paths:
            accepted.append(
                {
                    "pattern_id": _stable_id("pattern", adapter["adapter_id"], evidence_paths),
                    "adapter_id": adapter["adapter_id"],
                    "role": adapter["role"],
                    "status": "accepted",
                    "confidence": 0.85,
                    "evidence_refs": [f"code://{codebase_id}/{snapshot_id}/{path}" for path in evidence_paths],
                    "matched_paths": evidence_paths,
                }
            )
        elif matched_paths:
            review.append(
                {
                    "adapter_id": adapter["adapter_id"],
                    "role": adapter["role"],
                    "status": "needs_review",
                    "confidence": 0.55,
                    "matched_paths": matched_paths[:10],
                    "needs_review": ["path pattern matched but accepted code semantic evidence was not available"],
                }
            )
        else:
            blockers.append(
                {
                    "blocker_id": _stable_id("blocker", adapter["adapter_id"]),
                    "adapter_id": adapter["adapter_id"],
                    "code": "GENERIC_PATTERN_EVIDENCE_MISSING",
                    "reason": "No generic path or semantic evidence matched this adapter.",
                    "missing_evidence": ["matching repo-relative path", "accepted semantic provider fact"],
                    "next_actions": ["check whether the project uses a custom convention", "add generic adapter only if it applies to multiple repositories"],
                }
            )
    return accepted, review, blockers


def _matching_paths(paths: list[str], adapter: dict[str, Any]) -> list[str]:
    suffixes = adapter.get("required_path_suffixes") or []
    path_terms = [term.lower() for term in adapter.get("required_path_terms") or []]
    required_terms = [term.lower() for term in adapter.get("required_terms") or []]
    matches = []
    for path in paths:
        lower = path.lower()
        if suffixes and not any(lower.endswith(suffix) for suffix in suffixes):
            continue
        if path_terms and not any(term in lower for term in path_terms):
            continue
        if required_terms and not any(term in lower for term in required_terms):
            continue
        matches.append(path)
    return sorted(matches)


def _scale_profile(files: list[dict[str, Any]]) -> dict[str, Any]:
    included = [row for row in files if row.get("included", True)]
    return {
        "file_count": len(included),
        "large_project": len(included) >= 1000,
        "python_file_count": sum(1 for row in included if str(row.get("path") or "").endswith(".py")),
        "doc_file_count": sum(1 for row in included if str(row.get("path") or "").endswith((".md", ".drawio"))),
    }


def _stable_id(prefix: str, *parts: Any) -> str:
    return f"{prefix}_{hashlib.sha256('|'.join(str(part) for part in parts).encode('utf-8')).hexdigest()[:20]}"
