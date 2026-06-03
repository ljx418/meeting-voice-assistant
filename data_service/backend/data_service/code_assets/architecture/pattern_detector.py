"""Pattern candidate detection for V2.4 code-derived architecture."""

from __future__ import annotations

from typing import Any

from .code_model import architecture_pattern_candidate


PATTERN_RULES = [
    ("fastapi_router", "FastAPI router", {"api_router"}, ["api_router_role"]),
    ("mcp_registry", "MCP registry and tooling", {"mcp_tooling"}, ["mcp_tooling_role"]),
    ("cli_command_group", "CLI command group", {"cli_tooling"}, ["cli_tooling_role"]),
    ("provider_adapter", "Provider adapter", {"provider"}, ["provider_role"]),
    ("artifact_store", "Artifact store", {"artifact_store", "storage"}, ["artifact_storage_role"]),
    ("quality_gate", "Quality governance gate", {"governance", "policy"}, ["governance_role"]),
]


def detect_patterns(
    *,
    workspace_id: str,
    codebase_id: str,
    snapshot_id: str,
    roles: list[dict[str, Any]],
    source_artifact_refs: list[dict[str, str]],
) -> list[dict[str, Any]]:
    patterns: list[dict[str, Any]] = []
    for pattern_type, name, role_types, signals in PATTERN_RULES:
        matches = _matching_roles(roles, role_types)
        if matches:
            patterns.append(_pattern(workspace_id, codebase_id, snapshot_id, pattern_type, name, matches, signals, source_artifact_refs))
    name_patterns = [
        ("context_pack", "Agent Context Pack", ("context", "agent_context")),
        ("devwiki", "DevWiki", ("devwiki",)),
        ("code_graph", "Code Graph", ("graph",)),
        ("architecture_alignment", "Architecture Alignment", ("architecture",)),
        ("pipeline", "Build or operation pipeline", ("build", "pipeline", "operation")),
    ]
    for pattern_type, name, needles in name_patterns:
        matches = [role for role in roles if _role_has_name(role, needles) and float(role.get("confidence") or 0) >= 0.7]
        if matches:
            patterns.append(_pattern(workspace_id, codebase_id, snapshot_id, pattern_type, name, matches, [f"name_contains:{'/'.join(needles)}"], source_artifact_refs))
    return _dedupe(patterns)


def _matching_roles(roles: list[dict[str, Any]], role_types: set[str]) -> list[dict[str, Any]]:
    return [role for role in roles if role.get("role_type") in role_types and float(role.get("confidence") or 0) >= 0.8]


def _role_has_name(role: dict[str, Any], needles: tuple[str, ...]) -> bool:
    haystack = " ".join(str(role.get(key) or "") for key in ("name", "path", "target_id")).lower()
    return any(needle in haystack for needle in needles)


def _pattern(workspace_id: str, codebase_id: str, snapshot_id: str, pattern_type: str, name: str, roles: list[dict[str, Any]], signals: list[str], source_artifact_refs: list[dict[str, str]]) -> dict[str, Any]:
    targets = [
        {
            "role_id": role.get("role_id"),
            "role_type": role.get("role_type"),
            "target_type": role.get("target_type"),
            "target_id": role.get("target_id"),
            "name": role.get("name"),
            "path": role.get("path"),
        }
        for role in roles[:100]
    ]
    evidence = []
    seen = set()
    for role in roles:
        for item in role.get("evidence") or []:
            if not isinstance(item, dict):
                continue
            key = f"{item.get('path')}:{item.get('line_range')}"
            if key in seen:
                continue
            seen.add(key)
            evidence.append(dict(item))
            if len(evidence) >= 20:
                break
        if len(evidence) >= 20:
            break
    return architecture_pattern_candidate(
        workspace_id=workspace_id,
        codebase_id=codebase_id,
        snapshot_id=snapshot_id,
        pattern_type=pattern_type,
        name=name,
        targets=targets,
        signals=[*signals, f"roles:{len(roles)}"],
        evidence=evidence,
        confidence=0.85 if evidence else 0.55,
        needs_review=[] if evidence else [{"reason": "pattern_missing_evidence"}],
        source_artifact_refs=source_artifact_refs,
    )


def _dedupe(patterns: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: dict[str, dict[str, Any]] = {}
    for pattern in patterns:
        seen[str(pattern["pattern_id"])] = pattern
    return list(seen.values())
