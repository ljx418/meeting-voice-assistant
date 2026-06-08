"""Persistence helpers for V2.16 Coding Agent artifacts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from data_service.mcp_common import read_json, write_json

from ..artifacts import codebase_dir, read_jsonl, write_jsonl


def v2_16_dir(workspace: Path, codebase_id: str) -> Path:
    return codebase_dir(workspace, codebase_id) / "coding_agent" / "v2_16"


def providers_dir(workspace: Path, codebase_id: str) -> Path:
    return v2_16_dir(workspace, codebase_id) / "providers"


def provider_decisions_dir(workspace: Path, codebase_id: str) -> Path:
    return providers_dir(workspace, codebase_id) / "decisions"


def provider_registry_path(workspace: Path, codebase_id: str) -> Path:
    return providers_dir(workspace, codebase_id) / "capability_registry.json"


def provider_decision_path(workspace: Path, codebase_id: str, decision_id: str) -> Path:
    safe = str(decision_id or "decision").strip().replace("/", "_")
    return provider_decisions_dir(workspace, codebase_id) / f"{safe}.json"


def provider_registry_artifact_refs(codebase_id: str, decision_ids: list[str] | None = None) -> list[dict[str, str]]:
    refs = [
        {
            "type": "provider_capability_registry",
            "artifact_ref": f"coding-agent://{codebase_id}/v2_16/providers/capability_registry.json",
        }
    ]
    for decision_id in sorted(set(str(item) for item in list(decision_ids or []) if str(item))):
        refs.append(
            {
                "type": "provider_decision_record",
                "artifact_ref": f"coding-agent://{codebase_id}/v2_16/providers/decisions/{decision_id}.json",
            }
        )
    return refs


def write_provider_registry(workspace: Path, codebase_id: str, payload: dict[str, Any]) -> None:
    write_json(provider_registry_path(workspace, codebase_id), payload)
    for decision in payload.get("decision_records", []):
        write_json(provider_decision_path(workspace, codebase_id, str(decision["decision_id"])), decision)


def read_provider_registry(workspace: Path, codebase_id: str) -> dict[str, Any]:
    payload = read_json(provider_registry_path(workspace, codebase_id), None)
    if not payload:
        raise FileNotFoundError("PROVIDER_REGISTRY_NOT_FOUND")
    return payload


def semantic_dir(workspace: Path, codebase_id: str) -> Path:
    return v2_16_dir(workspace, codebase_id) / "semantic"


def semantic_provider_facts_path(workspace: Path, codebase_id: str) -> Path:
    return semantic_dir(workspace, codebase_id) / "provider_facts.jsonl"


def semantic_index_path(workspace: Path, codebase_id: str) -> Path:
    return semantic_dir(workspace, codebase_id) / "merged_semantic_index.json"


def semantic_conflicts_path(workspace: Path, codebase_id: str) -> Path:
    return semantic_dir(workspace, codebase_id) / "provider_conflicts.jsonl"


def semantic_artifact_refs(codebase_id: str) -> list[dict[str, str]]:
    return [
        {
            "type": "semantic_provider_facts",
            "artifact_ref": f"coding-agent://{codebase_id}/v2_16/semantic/provider_facts.jsonl",
        },
        {
            "type": "merged_semantic_index",
            "artifact_ref": f"coding-agent://{codebase_id}/v2_16/semantic/merged_semantic_index.json",
        },
        {
            "type": "semantic_provider_conflicts",
            "artifact_ref": f"coding-agent://{codebase_id}/v2_16/semantic/provider_conflicts.jsonl",
        },
    ]


def write_semantic_index(workspace: Path, codebase_id: str, index: dict[str, Any], facts: list[dict[str, Any]], conflicts: list[dict[str, Any]]) -> None:
    write_json(semantic_index_path(workspace, codebase_id), index)
    write_jsonl(semantic_provider_facts_path(workspace, codebase_id), facts)
    write_jsonl(semantic_conflicts_path(workspace, codebase_id), conflicts)


def read_semantic_index(workspace: Path, codebase_id: str) -> dict[str, Any]:
    index = read_json(semantic_index_path(workspace, codebase_id), None)
    if not index:
        raise FileNotFoundError("SEMANTIC_INDEX_NOT_FOUND")
    return {
        "index": index,
        "provider_facts": read_jsonl(semantic_provider_facts_path(workspace, codebase_id)),
        "provider_conflicts": read_jsonl(semantic_conflicts_path(workspace, codebase_id)),
        "artifact_refs": semantic_artifact_refs(codebase_id),
    }


def runtime_profiles_dir(workspace: Path, codebase_id: str) -> Path:
    return v2_16_dir(workspace, codebase_id) / "runtime_profiles"


def runtime_profiles_path(workspace: Path, codebase_id: str) -> Path:
    return runtime_profiles_dir(workspace, codebase_id) / "profiles.json"


def runtime_profile_runs_dir(workspace: Path, codebase_id: str) -> Path:
    return runtime_profiles_dir(workspace, codebase_id) / "runs"


def runtime_profile_run_path(workspace: Path, codebase_id: str, profile_run_id: str) -> Path:
    safe = str(profile_run_id or "profile_run").strip().replace("/", "_")
    return runtime_profile_runs_dir(workspace, codebase_id) / f"{safe}.json"


def runtime_profile_artifact_refs(codebase_id: str, profile_run_id: str | None = None) -> list[dict[str, str]]:
    refs = [
        {
            "type": "runtime_profiles",
            "artifact_ref": f"coding-agent://{codebase_id}/v2_16/runtime_profiles/profiles.json",
        }
    ]
    if profile_run_id:
        refs.append(
            {
                "type": "runtime_profile_run",
                "artifact_ref": f"coding-agent://{codebase_id}/v2_16/runtime_profiles/runs/{profile_run_id}.json",
            }
        )
    return refs


def write_runtime_profiles(workspace: Path, codebase_id: str, payload: dict[str, Any]) -> None:
    write_json(runtime_profiles_path(workspace, codebase_id), payload)


def read_runtime_profiles(workspace: Path, codebase_id: str) -> dict[str, Any]:
    payload = read_json(runtime_profiles_path(workspace, codebase_id), None)
    if not payload:
        raise FileNotFoundError("RUNTIME_PROFILES_NOT_FOUND")
    return payload


def write_runtime_profile_run(workspace: Path, codebase_id: str, payload: dict[str, Any]) -> None:
    write_json(runtime_profile_run_path(workspace, codebase_id, str(payload["profile_run_id"])), payload)


def read_runtime_profile_run(workspace: Path, codebase_id: str, profile_run_id: str) -> dict[str, Any]:
    payload = read_json(runtime_profile_run_path(workspace, codebase_id, profile_run_id), None)
    if not payload:
        raise FileNotFoundError("RUNTIME_PROFILE_RUN_NOT_FOUND")
    return payload


def workbench_v2_dir(workspace: Path, codebase_id: str) -> Path:
    return v2_16_dir(workspace, codebase_id) / "workbench_v2"


def workbench_v2_payload_path(workspace: Path, codebase_id: str) -> Path:
    return workbench_v2_dir(workspace, codebase_id) / "review_workbench_v2.json"


def workbench_v2_html_path(workspace: Path, codebase_id: str) -> Path:
    return workbench_v2_dir(workspace, codebase_id) / "review_workbench_v2.html"


def workbench_v2_mermaid_path(workspace: Path, codebase_id: str) -> Path:
    return workbench_v2_dir(workspace, codebase_id) / "review_workbench_v2.mmd"


def workbench_v2_artifact_refs(codebase_id: str) -> list[dict[str, str]]:
    return [
        {"type": "workbench_v2_payload", "artifact_ref": f"coding-agent://{codebase_id}/v2_16/workbench_v2/review_workbench_v2.json"},
        {"type": "workbench_v2_html", "artifact_ref": f"coding-agent://{codebase_id}/v2_16/workbench_v2/review_workbench_v2.html"},
        {"type": "workbench_v2_mermaid", "artifact_ref": f"coding-agent://{codebase_id}/v2_16/workbench_v2/review_workbench_v2.mmd"},
    ]


def write_workbench_v2(workspace: Path, codebase_id: str, payload: dict[str, Any], html: str, mermaid: str) -> None:
    write_json(workbench_v2_payload_path(workspace, codebase_id), payload)
    workbench_v2_html_path(workspace, codebase_id).parent.mkdir(parents=True, exist_ok=True)
    workbench_v2_html_path(workspace, codebase_id).write_text(html, encoding="utf-8")
    workbench_v2_mermaid_path(workspace, codebase_id).write_text(mermaid, encoding="utf-8")


def read_workbench_v2(workspace: Path, codebase_id: str) -> dict[str, Any]:
    payload = read_json(workbench_v2_payload_path(workspace, codebase_id), None)
    if not payload:
        raise FileNotFoundError("WORKBENCH_V2_NOT_FOUND")
    return payload


def large_project_advisor_dir(workspace: Path, codebase_id: str) -> Path:
    return v2_16_dir(workspace, codebase_id) / "large_project_advisor"


def large_project_advisor_path(workspace: Path, codebase_id: str) -> Path:
    return large_project_advisor_dir(workspace, codebase_id) / "abstraction_advisor.json"


def large_project_pattern_adapters_path(workspace: Path, codebase_id: str) -> Path:
    return large_project_advisor_dir(workspace, codebase_id) / "pattern_adapters.json"


def large_project_blockers_path(workspace: Path, codebase_id: str) -> Path:
    return large_project_advisor_dir(workspace, codebase_id) / "blockers.jsonl"


def large_project_advisor_artifact_refs(codebase_id: str) -> list[dict[str, str]]:
    return [
        {"type": "large_project_advisor", "artifact_ref": f"coding-agent://{codebase_id}/v2_16/large_project_advisor/abstraction_advisor.json"},
        {"type": "large_project_pattern_adapters", "artifact_ref": f"coding-agent://{codebase_id}/v2_16/large_project_advisor/pattern_adapters.json"},
        {"type": "large_project_blockers", "artifact_ref": f"coding-agent://{codebase_id}/v2_16/large_project_advisor/blockers.jsonl"},
    ]


def write_large_project_advisor(workspace: Path, codebase_id: str, payload: dict[str, Any], adapters: list[dict[str, Any]], blockers: list[dict[str, Any]]) -> None:
    write_json(large_project_advisor_path(workspace, codebase_id), payload)
    write_json(large_project_pattern_adapters_path(workspace, codebase_id), {"schema_version": payload.get("schema_version"), "adapters": adapters})
    write_jsonl(large_project_blockers_path(workspace, codebase_id), blockers)


def read_large_project_advisor(workspace: Path, codebase_id: str) -> dict[str, Any]:
    payload = read_json(large_project_advisor_path(workspace, codebase_id), None)
    if not payload:
        raise FileNotFoundError("LARGE_PROJECT_ADVISOR_NOT_FOUND")
    return payload


def patch_sandbox_dir(workspace: Path, codebase_id: str) -> Path:
    return v2_16_dir(workspace, codebase_id) / "patch_sandbox"


def patch_sandbox_previews_dir(workspace: Path, codebase_id: str) -> Path:
    return patch_sandbox_dir(workspace, codebase_id) / "previews"


def patch_sandbox_diffs_dir(workspace: Path, codebase_id: str) -> Path:
    return patch_sandbox_dir(workspace, codebase_id) / "diffs"


def patch_preview_path(workspace: Path, codebase_id: str, preview_id: str) -> Path:
    safe = str(preview_id or "preview").strip().replace("/", "_")
    return patch_sandbox_previews_dir(workspace, codebase_id) / f"{safe}.json"


def patch_preview_diff_path(workspace: Path, codebase_id: str, preview_id: str) -> Path:
    safe = str(preview_id or "preview").strip().replace("/", "_")
    return patch_sandbox_diffs_dir(workspace, codebase_id) / f"{safe}.diff"


def patch_preview_artifact_refs(codebase_id: str, preview_id: str) -> list[dict[str, str]]:
    return [
        {"type": "patch_sandbox_preview", "artifact_ref": f"coding-agent://{codebase_id}/v2_16/patch_sandbox/previews/{preview_id}.json"},
        {"type": "patch_sandbox_diff", "artifact_ref": f"coding-agent://{codebase_id}/v2_16/patch_sandbox/diffs/{preview_id}.diff"},
    ]


def write_patch_preview(workspace: Path, codebase_id: str, payload: dict[str, Any], diff_text: str) -> None:
    write_json(patch_preview_path(workspace, codebase_id, str(payload["preview_id"])), payload)
    patch_preview_diff_path(workspace, codebase_id, str(payload["preview_id"])).parent.mkdir(parents=True, exist_ok=True)
    patch_preview_diff_path(workspace, codebase_id, str(payload["preview_id"])).write_text(diff_text, encoding="utf-8")


def read_patch_preview(workspace: Path, codebase_id: str, preview_id: str) -> dict[str, Any]:
    payload = read_json(patch_preview_path(workspace, codebase_id, preview_id), None)
    if not payload:
        raise FileNotFoundError("PATCH_PREVIEW_NOT_FOUND")
    return payload
