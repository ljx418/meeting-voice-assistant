"""Persistence helpers for V2.11 Coding Agent actionability artifacts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from data_service.mcp_common import read_json, write_json

from ..artifacts import codebase_dir, read_jsonl, write_jsonl


def coding_agent_dir(workspace: Path, codebase_id: str) -> Path:
    return codebase_dir(workspace, codebase_id) / "coding_agent"


def actionability_dir(workspace: Path, codebase_id: str) -> Path:
    return coding_agent_dir(workspace, codebase_id) / "actionability"


def actionability_index_path(workspace: Path, codebase_id: str) -> Path:
    return actionability_dir(workspace, codebase_id) / "index.json"


def actionability_definitions_path(workspace: Path, codebase_id: str) -> Path:
    return actionability_dir(workspace, codebase_id) / "definitions.jsonl"


def actionability_references_path(workspace: Path, codebase_id: str) -> Path:
    return actionability_dir(workspace, codebase_id) / "references.jsonl"


def actionability_test_mapping_path(workspace: Path, codebase_id: str) -> Path:
    return actionability_dir(workspace, codebase_id) / "test_mapping.jsonl"


def impact_dir(workspace: Path, codebase_id: str) -> Path:
    return coding_agent_dir(workspace, codebase_id) / "impact"


def impact_path(workspace: Path, codebase_id: str, impact_id: str) -> Path:
    safe = impact_id.strip().replace("/", "_") or "impact"
    return impact_dir(workspace, codebase_id) / f"{safe}.json"


def task_plan_path(workspace: Path, codebase_id: str, plan_id: str) -> Path:
    safe = plan_id.strip().replace("/", "_") or "task_to_edit_plan"
    return actionability_dir(workspace, codebase_id) / f"task_to_edit_plan_{safe}.json"


def patch_plans_dir(workspace: Path, codebase_id: str) -> Path:
    return coding_agent_dir(workspace, codebase_id) / "patch_plans"


def patch_plan_path(workspace: Path, codebase_id: str, patch_plan_id: str) -> Path:
    safe = patch_plan_id.strip().replace("/", "_") or "patch_plan"
    return patch_plans_dir(workspace, codebase_id) / f"{safe}.json"


def patch_plan_artifact_ref(codebase_id: str, patch_plan_id: str) -> dict[str, str]:
    return {"type": "patch_plan", "artifact_ref": f"coding-agent://{codebase_id}/patch_plans/{patch_plan_id}.json"}


def runtime_dir(workspace: Path, codebase_id: str) -> Path:
    return coding_agent_dir(workspace, codebase_id) / "runtime"


def runtime_registry_path(workspace: Path, codebase_id: str) -> Path:
    return runtime_dir(workspace, codebase_id) / "command_registry.json"


def runtime_runs_dir(workspace: Path, codebase_id: str) -> Path:
    return runtime_dir(workspace, codebase_id) / "runs"


def runtime_logs_dir(workspace: Path, codebase_id: str) -> Path:
    return runtime_dir(workspace, codebase_id) / "logs"


def runtime_run_path(workspace: Path, codebase_id: str, run_id: str) -> Path:
    safe = run_id.strip().replace("/", "_") or "runtime_run"
    return runtime_runs_dir(workspace, codebase_id) / f"{safe}.json"


def runtime_log_path(workspace: Path, codebase_id: str, run_id: str, stream: str) -> Path:
    safe = run_id.strip().replace("/", "_") or "runtime_run"
    suffix = "stderr" if stream == "stderr" else "stdout"
    return runtime_logs_dir(workspace, codebase_id) / f"{safe}.{suffix}.redacted.txt"


def runtime_registry_artifact_ref(codebase_id: str) -> dict[str, str]:
    return {"type": "runtime_command_registry", "artifact_ref": f"coding-agent://{codebase_id}/runtime/command_registry.json"}


def runtime_run_artifact_ref(codebase_id: str, run_id: str) -> dict[str, str]:
    return {"type": "runtime_run", "artifact_ref": f"coding-agent://{codebase_id}/runtime/runs/{run_id}.json"}


def incremental_dir(workspace: Path, codebase_id: str) -> Path:
    return coding_agent_dir(workspace, codebase_id) / "incremental"


def fingerprint_index_dir(workspace: Path, codebase_id: str) -> Path:
    return incremental_dir(workspace, codebase_id) / "fingerprint_index"


def fingerprint_index_path(workspace: Path, codebase_id: str, snapshot_id: str) -> Path:
    safe = snapshot_id.strip().replace("/", "_") or "snapshot"
    return fingerprint_index_dir(workspace, codebase_id) / f"{safe}.json"


def snapshot_diffs_dir(workspace: Path, codebase_id: str) -> Path:
    return incremental_dir(workspace, codebase_id) / "snapshot_diffs"


def snapshot_diff_path(workspace: Path, codebase_id: str, diff_id: str) -> Path:
    safe = diff_id.strip().replace("/", "_") or "snapshot_diff"
    return snapshot_diffs_dir(workspace, codebase_id) / f"{safe}.json"


def task_memory_path(workspace: Path, codebase_id: str) -> Path:
    return incremental_dir(workspace, codebase_id) / "task_memory.jsonl"


def drift_timeline_path(workspace: Path, codebase_id: str) -> Path:
    return incremental_dir(workspace, codebase_id) / "drift_timeline.jsonl"


def snapshot_diff_artifact_ref(codebase_id: str, diff_id: str) -> dict[str, str]:
    return {"type": "incremental_snapshot_diff", "artifact_ref": f"coding-agent://{codebase_id}/incremental/snapshot_diffs/{diff_id}.json"}


def workbench_dir(workspace: Path, codebase_id: str) -> Path:
    return coding_agent_dir(workspace, codebase_id) / "workbench"


def workbench_payload_path(workspace: Path, codebase_id: str) -> Path:
    return workbench_dir(workspace, codebase_id) / "review_workbench.json"


def workbench_html_path(workspace: Path, codebase_id: str) -> Path:
    return workbench_dir(workspace, codebase_id) / "review_workbench.html"


def workbench_mermaid_path(workspace: Path, codebase_id: str) -> Path:
    return workbench_dir(workspace, codebase_id) / "capability_graph.mmd"


def context_exports_dir(workspace: Path, codebase_id: str) -> Path:
    return workbench_dir(workspace, codebase_id) / "context_exports"


def context_export_path(workspace: Path, codebase_id: str, export_id: str) -> Path:
    safe = export_id.strip().replace("/", "_") or "context_export"
    return context_exports_dir(workspace, codebase_id) / f"{safe}.json"


def workbench_artifact_refs(codebase_id: str) -> list[dict[str, str]]:
    return [
        {"type": "workbench_payload", "artifact_ref": f"coding-agent://{codebase_id}/workbench/review_workbench.json"},
        {"type": "workbench_html", "artifact_ref": f"coding-agent://{codebase_id}/workbench/review_workbench.html"},
        {"type": "workbench_mermaid", "artifact_ref": f"coding-agent://{codebase_id}/workbench/capability_graph.mmd"},
    ]


def actionability_artifact_refs(codebase_id: str) -> list[dict[str, str]]:
    return [
        {"type": "actionability_index", "artifact_ref": f"coding-agent://{codebase_id}/actionability/index.json"},
        {"type": "definitions", "artifact_ref": f"coding-agent://{codebase_id}/actionability/definitions.jsonl"},
        {"type": "references", "artifact_ref": f"coding-agent://{codebase_id}/actionability/references.jsonl"},
        {"type": "test_mapping", "artifact_ref": f"coding-agent://{codebase_id}/actionability/test_mapping.jsonl"},
    ]


def write_actionability_bundle(workspace: Path, codebase_id: str, index: dict[str, Any], definitions: list[dict[str, Any]], references: list[dict[str, Any]], test_mapping: list[dict[str, Any]]) -> None:
    write_json(actionability_index_path(workspace, codebase_id), index)
    write_jsonl(actionability_definitions_path(workspace, codebase_id), definitions)
    write_jsonl(actionability_references_path(workspace, codebase_id), references)
    write_jsonl(actionability_test_mapping_path(workspace, codebase_id), test_mapping)


def read_actionability_bundle(workspace: Path, codebase_id: str) -> dict[str, Any]:
    index = read_json(actionability_index_path(workspace, codebase_id), None)
    if not index:
        raise FileNotFoundError("ACTIONABILITY_INDEX_NOT_FOUND")
    return {
        "index": index,
        "definitions": read_jsonl(actionability_definitions_path(workspace, codebase_id)),
        "references": read_jsonl(actionability_references_path(workspace, codebase_id)),
        "test_mapping": read_jsonl(actionability_test_mapping_path(workspace, codebase_id)),
        "artifact_refs": actionability_artifact_refs(codebase_id),
    }


def write_impact(workspace: Path, codebase_id: str, payload: dict[str, Any]) -> None:
    write_json(impact_path(workspace, codebase_id, str(payload["impact_id"])), payload)


def read_impact(workspace: Path, codebase_id: str, impact_id: str) -> dict[str, Any]:
    payload = read_json(impact_path(workspace, codebase_id, impact_id), None)
    if not payload:
        raise FileNotFoundError("IMPACT_NOT_FOUND")
    return payload


def write_task_plan(workspace: Path, codebase_id: str, payload: dict[str, Any]) -> None:
    write_json(task_plan_path(workspace, codebase_id, str(payload["plan_id"])), payload)


def read_task_plan(workspace: Path, codebase_id: str, plan_id: str) -> dict[str, Any]:
    payload = read_json(task_plan_path(workspace, codebase_id, plan_id), None)
    if not payload:
        raise FileNotFoundError("TASK_PLAN_NOT_FOUND")
    return payload


def write_patch_plan(workspace: Path, codebase_id: str, payload: dict[str, Any]) -> None:
    write_json(patch_plan_path(workspace, codebase_id, str(payload["patch_plan_id"])), payload)


def read_patch_plan(workspace: Path, codebase_id: str, patch_plan_id: str) -> dict[str, Any]:
    payload = read_json(patch_plan_path(workspace, codebase_id, patch_plan_id), None)
    if not payload:
        raise FileNotFoundError("PATCH_PLAN_NOT_FOUND")
    return payload


def write_runtime_registry(workspace: Path, codebase_id: str, payload: dict[str, Any]) -> None:
    write_json(runtime_registry_path(workspace, codebase_id), payload)


def read_runtime_registry(workspace: Path, codebase_id: str) -> dict[str, Any]:
    payload = read_json(runtime_registry_path(workspace, codebase_id), None)
    if not payload:
        raise FileNotFoundError("RUNTIME_COMMAND_REGISTRY_NOT_FOUND")
    return payload


def write_runtime_run(workspace: Path, codebase_id: str, payload: dict[str, Any], stdout: str, stderr: str) -> None:
    write_json(runtime_run_path(workspace, codebase_id, str(payload["run_id"])), payload)
    runtime_log_path(workspace, codebase_id, str(payload["run_id"]), "stdout").parent.mkdir(parents=True, exist_ok=True)
    runtime_log_path(workspace, codebase_id, str(payload["run_id"]), "stdout").write_text(stdout, encoding="utf-8")
    runtime_log_path(workspace, codebase_id, str(payload["run_id"]), "stderr").write_text(stderr, encoding="utf-8")


def read_runtime_run(workspace: Path, codebase_id: str, run_id: str) -> dict[str, Any]:
    payload = read_json(runtime_run_path(workspace, codebase_id, run_id), None)
    if not payload:
        raise FileNotFoundError("RUNTIME_RUN_NOT_FOUND")
    return payload


def write_fingerprint_index(workspace: Path, codebase_id: str, snapshot_id: str, payload: dict[str, Any]) -> None:
    write_json(fingerprint_index_path(workspace, codebase_id, snapshot_id), payload)


def read_fingerprint_index(workspace: Path, codebase_id: str, snapshot_id: str) -> dict[str, Any]:
    payload = read_json(fingerprint_index_path(workspace, codebase_id, snapshot_id), None)
    if not payload:
        raise FileNotFoundError("FINGERPRINT_INDEX_NOT_FOUND")
    return payload


def write_snapshot_diff(workspace: Path, codebase_id: str, payload: dict[str, Any], task_memory: list[dict[str, Any]], drift_events: list[dict[str, Any]]) -> None:
    write_json(snapshot_diff_path(workspace, codebase_id, str(payload["diff_id"])), payload)
    existing_memory = read_jsonl(task_memory_path(workspace, codebase_id))
    existing_drift = read_jsonl(drift_timeline_path(workspace, codebase_id))
    write_jsonl(task_memory_path(workspace, codebase_id), existing_memory + task_memory)
    write_jsonl(drift_timeline_path(workspace, codebase_id), existing_drift + drift_events)


def read_snapshot_diff(workspace: Path, codebase_id: str, diff_id: str) -> dict[str, Any]:
    payload = read_json(snapshot_diff_path(workspace, codebase_id, diff_id), None)
    if not payload:
        raise FileNotFoundError("INCREMENTAL_DIFF_NOT_FOUND")
    return payload


def read_drift_timeline(workspace: Path, codebase_id: str) -> list[dict[str, Any]]:
    return read_jsonl(drift_timeline_path(workspace, codebase_id))


def write_workbench(workspace: Path, codebase_id: str, payload: dict[str, Any], html: str, mermaid: str) -> None:
    write_json(workbench_payload_path(workspace, codebase_id), payload)
    workbench_html_path(workspace, codebase_id).parent.mkdir(parents=True, exist_ok=True)
    workbench_html_path(workspace, codebase_id).write_text(html, encoding="utf-8")
    workbench_mermaid_path(workspace, codebase_id).write_text(mermaid, encoding="utf-8")


def read_workbench(workspace: Path, codebase_id: str) -> dict[str, Any]:
    payload = read_json(workbench_payload_path(workspace, codebase_id), None)
    if not payload:
        raise FileNotFoundError("WORKBENCH_PAYLOAD_NOT_FOUND")
    return payload


def write_context_export(workspace: Path, codebase_id: str, payload: dict[str, Any]) -> None:
    write_json(context_export_path(workspace, codebase_id, str(payload["export_id"])), payload)


def read_context_export(workspace: Path, codebase_id: str, export_id: str) -> dict[str, Any]:
    payload = read_json(context_export_path(workspace, codebase_id, export_id), None)
    if not payload:
        raise FileNotFoundError("WORKBENCH_CONTEXT_EXPORT_NOT_FOUND")
    return payload
