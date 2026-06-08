"""V2.16 semantic provider orchestration.

This phase turns deterministic AST baseline facts into provider-attributed
semantic facts. It does not claim runtime calls, data flow, control flow, or
type inference.
"""

from __future__ import annotations

import hashlib
from typing import Any

from data_service.mcp_common import now

from .persistence import semantic_artifact_refs


SCHEMA_VERSION = "v2.16"
FORBIDDEN_CLAIMS = {"runtime_call", "runtime_calls", "data_flow", "control_flow", "type_inferred", "type_inferred_dependency"}


def build_semantic_payload(
    *,
    workspace_id: str,
    codebase_id: str,
    snapshot_id: str,
    actionability: dict[str, Any],
    provider_registry: dict[str, Any],
) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
    facts = _facts_from_actionability(codebase_id, snapshot_id, actionability)
    conflicts = _conflicts(facts)
    blockers = [
        {
            "provider_id": provider["provider_id"],
            "status": provider["status"],
            "reason_code": provider.get("reason_code") or provider.get("error", {}).get("code"),
            "message": provider.get("reason") or provider.get("error", {}).get("message"),
        }
        for provider in provider_registry.get("providers", [])
        if provider.get("status") != "available" and str(provider.get("provider_id", "")).startswith("semantic:")
    ]
    forbidden_count = sum(1 for fact in facts if fact.get("claim_type") in FORBIDDEN_CLAIMS)
    index = {
        "schema_version": SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "semantic_index_id": _stable_id("semantic", codebase_id, snapshot_id, len(facts), len(conflicts)),
        "source_phase": "V2.16 Phase 77",
        "provider_registry_ref": f"coding-agent://{codebase_id}/v2_16/providers/capability_registry.json",
        "summary": {
            "provider_fact_count": len(facts),
            "accepted_fact_count": sum(1 for fact in facts if fact["status"] == "accepted"),
            "provider_blocker_count": len(blockers),
            "conflict_count": len(conflicts),
            "forbidden_claim_count": forbidden_count,
            "provider_count": len({fact["provider_id"] for fact in facts}),
        },
        "provider_blockers": blockers,
        "provider_conflict_count": len(conflicts),
        "warnings": [] if facts else [{"code": "NO_AST_FACTS", "message": "No AST baseline facts were available."}],
        "unresolved": blockers,
        "artifact_refs": semantic_artifact_refs(codebase_id),
        "created_at": now(),
    }
    return index, facts, conflicts


def public_semantic_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "index": dict(payload["index"]),
        "provider_facts": [dict(item) for item in payload.get("provider_facts", [])[:1000]],
        "provider_conflicts": [dict(item) for item in payload.get("provider_conflicts", [])],
        "artifact_refs": list(payload.get("artifact_refs") or []),
    }


def _facts_from_actionability(codebase_id: str, snapshot_id: str, actionability: dict[str, Any]) -> list[dict[str, Any]]:
    facts: list[dict[str, Any]] = []
    for definition in actionability.get("definitions", [])[:800]:
        path = str(definition.get("path") or definition.get("source_file") or "")
        line_range = list(definition.get("line_range") or [])
        evidence_refs = list(definition.get("evidence_refs") or [])
        if not evidence_refs and path and len(line_range) == 2:
            evidence_refs = [f"code://{codebase_id}/{snapshot_id}/{path}#L{line_range[0]}-L{line_range[1]}"]
        facts.append(
            {
                "fact_id": _stable_id("semfact", "definition", definition.get("definition_id"), path, line_range),
                "fact_type": "symbol_definition",
                "claim_type": "definition",
                "provider_id": "semantic:python_ast",
                "extractor": "python_ast",
                "status": "accepted" if evidence_refs and len(line_range) == 2 else "needs_review",
                "confidence": 0.95 if evidence_refs and len(line_range) == 2 else 0.5,
                "source_file": path,
                "line_range": line_range,
                "qualified_name": definition.get("qualified_name"),
                "symbol_kind": definition.get("kind"),
                "evidence_refs": evidence_refs,
                "needs_review": [] if evidence_refs and len(line_range) == 2 else ["missing line-level evidence"],
            }
        )
    for reference in actionability.get("references", [])[:800]:
        path = str(reference.get("path") or reference.get("source_file") or "")
        line_range = list(reference.get("line_range") or [])
        relation_type = str(reference.get("relation_type") or "reference")
        evidence_refs = list(reference.get("evidence_refs") or [])
        if not evidence_refs and path and len(line_range) == 2:
            evidence_refs = [f"code://{codebase_id}/{snapshot_id}/{path}#L{line_range[0]}-L{line_range[1]}"]
        has_line_evidence = bool(evidence_refs) and len(line_range) == 2
        is_forbidden = relation_type in FORBIDDEN_CLAIMS
        status = "blocked" if is_forbidden else "accepted" if has_line_evidence else "needs_review"
        facts.append(
            {
                "fact_id": _stable_id("semfact", "reference", reference.get("reference_id"), path, line_range),
                "fact_type": "symbol_reference",
                "claim_type": relation_type,
                "provider_id": "semantic:python_ast",
                "extractor": "python_ast",
                "status": status,
                "confidence": 0.75 if status == "accepted" else 0.5 if status == "needs_review" else 0.0,
                "source_file": path,
                "line_range": line_range,
                "qualified_name": reference.get("qualified_name") or reference.get("target_name"),
                "symbol_kind": reference.get("kind") or "reference",
                "evidence_refs": evidence_refs,
                "needs_review": _reference_needs_review(is_forbidden=is_forbidden, has_line_evidence=has_line_evidence),
            }
        )
    return facts


def _reference_needs_review(*, is_forbidden: bool, has_line_evidence: bool) -> list[str]:
    if is_forbidden:
        return ["forbidden semantic claim"]
    if not has_line_evidence:
        return ["missing line-level evidence"]
    return []


def _conflicts(facts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_key: dict[tuple[str, str], set[str]] = {}
    for fact in facts:
        key = (str(fact.get("source_file")), str(fact.get("qualified_name")))
        by_key.setdefault(key, set()).add(str(fact.get("provider_id")))
    conflicts = []
    for (path, qualified_name), providers in sorted(by_key.items()):
        if len(providers) > 1:
            conflicts.append(
                {
                    "conflict_id": _stable_id("semconflict", path, qualified_name, sorted(providers)),
                    "source_file": path,
                    "qualified_name": qualified_name,
                    "provider_ids": sorted(providers),
                    "status": "needs_review",
                }
            )
    return conflicts


def _stable_id(prefix: str, *parts: Any) -> str:
    encoded = "|".join(_jsonish(part) for part in parts)
    return f"{prefix}_{hashlib.sha256(encoded.encode('utf-8')).hexdigest()[:20]}"


def _jsonish(value: Any) -> str:
    if isinstance(value, (list, tuple)):
        return "[" + ",".join(_jsonish(item) for item in value) + "]"
    if isinstance(value, dict):
        return "{" + ",".join(f"{key}:{_jsonish(value[key])}" for key in sorted(value)) + "}"
    return str(value)
