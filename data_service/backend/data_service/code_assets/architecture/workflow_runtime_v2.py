"""V2.41 workflow/runtime candidate extractors.

Candidates are reviewable facts. This module intentionally does not emit
production runtime topology, full call graph, data flow, or control flow.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

from data_service.mcp_common import now

from ..artifacts import architecture_dir, read_json, read_jsonl, write_json, write_jsonl


SCHEMA_VERSION = "v2.41_workflow_runtime"
TEXT_EXTENSIONS = {".py", ".js", ".jsx", ".ts", ".tsx", ".vue", ".json", ".yaml", ".yml", ".toml", ".md", ".sh"}


def build_workflow_runtime_candidates(
    *,
    workspace: Path,
    workspace_id: str,
    codebase_id: str,
    snapshot_id: str,
    root: Path,
    files: list[dict[str, Any]],
) -> dict[str, Any]:
    included = [item for item in files if item.get("included") and isinstance(item.get("path"), str)]
    workflow: list[dict[str, Any]] = []
    runtime: list[dict[str, Any]] = []
    entrypoints: list[dict[str, Any]] = []
    blockers: list[dict[str, Any]] = []

    for item in included:
        rel = str(item["path"])
        path = root / rel
        suffix = Path(rel).suffix.lower()
        text = _read_text(path) if suffix in TEXT_EXTENSIONS or Path(rel).name in {"Dockerfile", "docker-compose.yml"} else None
        lowered = rel.lower()

        if _is_workflow_manifest(rel):
            workflow.append(_candidate(workspace_id, codebase_id, snapshot_id, rel, "workflow_manifest", _label(rel), [1, _line_count(text)], "deterministic", 0.95, "workflow_manifest_path"))
        if Path(rel).name in {"docker-compose.yml", "docker-compose.yaml"}:
            workflow.append(_candidate(workspace_id, codebase_id, snapshot_id, rel, "pipeline_config", "docker compose", [1, _line_count(text)], "deterministic", 0.92, "pipeline_config_path"))
        if Path(rel).name == "Dockerfile":
            workflow.append(_candidate(workspace_id, codebase_id, snapshot_id, rel, "pipeline_config", "dockerfile", [1, _line_count(text)], "deterministic", 0.9, "pipeline_config_path"))
        if Path(rel).name == "package.json" and text:
            entrypoints.extend(_package_script_candidates(workspace_id, codebase_id, snapshot_id, rel, text))

        if text:
            entrypoints.extend(_cli_candidates(workspace_id, codebase_id, snapshot_id, rel, text))
            entrypoints.extend(_tui_console_candidates(workspace_id, codebase_id, snapshot_id, rel, text))
            runtime.extend(_runtime_candidates(workspace_id, codebase_id, snapshot_id, rel, text))
            runtime.extend(_agent_registry_candidates(workspace_id, codebase_id, snapshot_id, rel, text))
        else:
            if any(token in lowered for token in ("workflow", "runtime", "adapter", "agent", "console", "tui", "cli")):
                blockers.append({"code": "CANDIDATE_FILE_NOT_TEXT", "path": rel, "reason": "candidate-like path is not readable as text"})

    workflow = _dedupe(workflow, "candidate_id")
    runtime = _dedupe(runtime, "candidate_id")
    entrypoints = _dedupe(entrypoints, "candidate_id")
    summary = {
        "schema_version": SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "workflow_candidate_count": len(workflow),
        "runtime_adapter_candidate_count": len(runtime),
        "entrypoint_candidate_count": len(entrypoints),
        "heuristic_candidate_count": sum(1 for item in [*workflow, *runtime, *entrypoints] if item.get("determinism") == "heuristic"),
        "blockers": blockers,
        "artifact_refs": workflow_runtime_artifact_refs(codebase_id),
        "created_at": now(),
    }
    write_jsonl(workflow_candidates_path(workspace, codebase_id), workflow)
    write_jsonl(runtime_adapter_candidates_path(workspace, codebase_id), runtime)
    write_jsonl(entrypoint_candidates_path(workspace, codebase_id), entrypoints)
    write_json(workflow_runtime_summary_path(workspace, codebase_id), summary)
    return {
        "schema_version": SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "workflow_candidates": workflow,
        "runtime_adapter_candidates": runtime,
        "entrypoint_candidates": entrypoints,
        "summary": summary,
        "artifact_refs": workflow_runtime_artifact_refs(codebase_id),
    }


def read_workflow_runtime_candidates(workspace: Path, codebase_id: str) -> dict[str, Any]:
    workflow = read_jsonl(workflow_candidates_path(workspace, codebase_id))
    runtime = read_jsonl(runtime_adapter_candidates_path(workspace, codebase_id))
    entrypoints = read_jsonl(entrypoint_candidates_path(workspace, codebase_id))
    summary = read_json(workflow_runtime_summary_path(workspace, codebase_id), {})
    if not summary:
        raise FileNotFoundError("ARCHITECTURE_WORKFLOW_RUNTIME_NOT_BUILT")
    return {
        "schema_version": SCHEMA_VERSION,
        "workspace_id": summary.get("workspace_id"),
        "codebase_id": codebase_id,
        "snapshot_id": summary.get("snapshot_id"),
        "workflow_candidates": workflow,
        "runtime_adapter_candidates": runtime,
        "entrypoint_candidates": entrypoints,
        "summary": summary,
        "artifact_refs": workflow_runtime_artifact_refs(codebase_id),
    }


def public_workflow_runtime_payload(payload: dict[str, Any], *, limit: int = 50) -> dict[str, Any]:
    workflow = list(payload.get("workflow_candidates") or [])
    runtime = list(payload.get("runtime_adapter_candidates") or [])
    entrypoints = list(payload.get("entrypoint_candidates") or [])
    return {
        "schema_version": payload.get("schema_version", SCHEMA_VERSION),
        "workspace_id": payload.get("workspace_id"),
        "codebase_id": payload.get("codebase_id"),
        "snapshot_id": payload.get("snapshot_id"),
        "summary": payload.get("summary") or {},
        "workflow_candidates": {"total": len(workflow), "sample": workflow[:limit], "truncated": len(workflow) > limit},
        "runtime_adapter_candidates": {"total": len(runtime), "sample": runtime[:limit], "truncated": len(runtime) > limit},
        "entrypoint_candidates": {"total": len(entrypoints), "sample": entrypoints[:limit], "truncated": len(entrypoints) > limit},
        "artifact_refs": payload.get("artifact_refs") or workflow_runtime_artifact_refs(str(payload.get("codebase_id") or "")),
    }


def workflow_runtime_artifact_refs(codebase_id: str) -> list[dict[str, str]]:
    return [
        {"type": "workflow_candidates", "artifact_ref": f"architecture-v2-41://{codebase_id}/workflow_candidates.jsonl"},
        {"type": "runtime_adapter_candidates", "artifact_ref": f"architecture-v2-41://{codebase_id}/runtime_adapter_candidates.jsonl"},
        {"type": "entrypoint_candidates", "artifact_ref": f"architecture-v2-41://{codebase_id}/entrypoint_candidates.jsonl"},
        {"type": "workflow_runtime_summary", "artifact_ref": f"architecture-v2-41://{codebase_id}/workflow_runtime_summary.json"},
    ]


def workflow_candidates_path(workspace: Path, codebase_id: str) -> Path:
    return _v241_dir(workspace, codebase_id) / "workflow_candidates.jsonl"


def runtime_adapter_candidates_path(workspace: Path, codebase_id: str) -> Path:
    return _v241_dir(workspace, codebase_id) / "runtime_adapter_candidates.jsonl"


def entrypoint_candidates_path(workspace: Path, codebase_id: str) -> Path:
    return _v241_dir(workspace, codebase_id) / "entrypoint_candidates.jsonl"


def workflow_runtime_summary_path(workspace: Path, codebase_id: str) -> Path:
    return _v241_dir(workspace, codebase_id) / "workflow_runtime_summary.json"


def _v241_dir(workspace: Path, codebase_id: str) -> Path:
    return architecture_dir(workspace, codebase_id) / "v2_41"


def _candidate(workspace_id: str, codebase_id: str, snapshot_id: str, path: str, candidate_type: str, label: str, line_range: list[int], determinism: str, confidence: float, extractor: str, *, needs_review: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    review = list(needs_review or [])
    if determinism == "heuristic" and not review:
        review.append({"code": "HEURISTIC_CANDIDATE", "message": "Candidate requires human or downstream verification before topology claims."})
    return {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": "workflow_runtime_candidate",
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "candidate_id": _candidate_id(codebase_id, path, candidate_type, label, line_range, extractor),
        "candidate_type": candidate_type,
        "label": label,
        "path": path,
        "line_range": line_range,
        "determinism": determinism,
        "confidence": confidence,
        "extractor": extractor,
        "evidence_refs": [{"type": "file_line", "path": path, "line_range": line_range}],
        "needs_review": review,
        "topology_claim": False,
    }


def _package_script_candidates(workspace_id: str, codebase_id: str, snapshot_id: str, path: str, text: str) -> list[dict[str, Any]]:
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return []
    scripts = data.get("scripts")
    if not isinstance(scripts, dict):
        return []
    items: list[dict[str, Any]] = []
    for name, command in scripts.items():
        line = _line_for_fragment(text, f'"{name}"')
        items.append(_candidate(workspace_id, codebase_id, snapshot_id, path, "cli_entrypoint", f"npm script: {name}", [line, line], "deterministic", 0.88, "package_json_scripts"))
        if isinstance(command, str) and any(token in command.lower() for token in ("vite", "next", "electron", "tauri", "dev")):
            items.append(_candidate(workspace_id, codebase_id, snapshot_id, path, "console_entrypoint", f"app script: {name}", [line, line], "heuristic", 0.66, "package_json_script_command"))
    return items


def _cli_candidates(workspace_id: str, codebase_id: str, snapshot_id: str, path: str, text: str) -> list[dict[str, Any]]:
    patterns = [
        ("argparse", "cli_entrypoint", "python argparse entrypoint", "python_cli_argparse", 0.84),
        ("click.command", "cli_entrypoint", "python click entrypoint", "python_cli_click", 0.84),
        ("typer.Typer", "cli_entrypoint", "python typer entrypoint", "python_cli_typer", 0.84),
        ("if __name__ == \"__main__\"", "cli_entrypoint", "python main entrypoint", "python_main_guard", 0.82),
        ("if __name__ == '__main__'", "cli_entrypoint", "python main entrypoint", "python_main_guard", 0.82),
    ]
    return [_candidate(workspace_id, codebase_id, snapshot_id, path, kind, label, [_line_for_fragment(text, fragment), _line_for_fragment(text, fragment)], "deterministic", confidence, extractor) for fragment, kind, label, extractor, confidence in patterns if fragment in text]


def _tui_console_candidates(workspace_id: str, codebase_id: str, snapshot_id: str, path: str, text: str) -> list[dict[str, Any]]:
    lowered_path = path.lower()
    lowered = text.lower()
    candidates: list[dict[str, Any]] = []
    if any(token in lowered for token in ("textual", "rich.console", "curses", "urwid")) or "tui" in lowered_path:
        candidates.append(_candidate(workspace_id, codebase_id, snapshot_id, path, "tui_entrypoint", _label(path), [_first_nonempty_line(text), _first_nonempty_line(text)], "heuristic", 0.67, "tui_text_hint"))
    if any(token in lowered_path for token in ("console", "terminal", "workbench")) or any(token in lowered for token in ("console.", "terminal", "workbench")):
        candidates.append(_candidate(workspace_id, codebase_id, snapshot_id, path, "console_entrypoint", _label(path), [_first_nonempty_line(text), _first_nonempty_line(text)], "heuristic", 0.65, "console_text_hint"))
    return candidates


def _runtime_candidates(workspace_id: str, codebase_id: str, snapshot_id: str, path: str, text: str) -> list[dict[str, Any]]:
    lowered_path = path.lower()
    lowered = text.lower()
    candidates: list[dict[str, Any]] = []
    if any(token in lowered_path for token in ("runtime", "adapter", "provider", "plugin")):
        candidates.append(_candidate(workspace_id, codebase_id, snapshot_id, path, "runtime_adapter", _label(path), [_first_nonempty_line(text), _first_nonempty_line(text)], "heuristic", 0.7, "runtime_path_hint"))
    if re.search(r"class\s+\w*(Runtime|Adapter|Provider|Plugin)\b", text):
        line = _line_for_regex(text, r"class\s+\w*(Runtime|Adapter|Provider|Plugin)\b")
        candidates.append(_candidate(workspace_id, codebase_id, snapshot_id, path, "runtime_adapter", _label(path), [line, line], "heuristic", 0.74, "runtime_class_hint"))
    if any(token in lowered for token in ("register_adapter", "register_provider", "runtime_registry", "plugin_registry")):
        candidates.append(_candidate(workspace_id, codebase_id, snapshot_id, path, "runtime_adapter", _label(path), [_line_for_any(text, ["register_adapter", "register_provider", "runtime_registry", "plugin_registry"]), _line_for_any(text, ["register_adapter", "register_provider", "runtime_registry", "plugin_registry"])], "heuristic", 0.72, "runtime_registry_hint"))
    return candidates


def _agent_registry_candidates(workspace_id: str, codebase_id: str, snapshot_id: str, path: str, text: str) -> list[dict[str, Any]]:
    lowered_path = path.lower()
    lowered = text.lower()
    if "agent" not in lowered_path and "agent" not in lowered:
        return []
    line = _line_for_any(text, ["agent_registry", "register_agent", "Agent", "agent"])
    return [_candidate(workspace_id, codebase_id, snapshot_id, path, "agent_registry", _label(path), [line, line], "heuristic", 0.7, "agent_registry_hint")]


def _is_workflow_manifest(path: str) -> bool:
    lowered = path.lower()
    return lowered.startswith(".github/workflows/") and lowered.endswith((".yml", ".yaml")) or lowered.endswith((".github/workflows.yml", ".github/workflows.yaml"))


def _read_text(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None


def _line_count(text: str | None) -> int:
    if not text:
        return 1
    return max(1, len(text.splitlines()))


def _first_nonempty_line(text: str) -> int:
    for index, line in enumerate(text.splitlines(), start=1):
        if line.strip():
            return index
    return 1


def _line_for_fragment(text: str, fragment: str) -> int:
    index = text.find(fragment)
    if index < 0:
        return _first_nonempty_line(text)
    return text.count("\n", 0, index) + 1


def _line_for_regex(text: str, pattern: str) -> int:
    match = re.search(pattern, text)
    if not match:
        return _first_nonempty_line(text)
    return text.count("\n", 0, match.start()) + 1


def _line_for_any(text: str, fragments: list[str]) -> int:
    for fragment in fragments:
        line = _line_for_fragment(text, fragment)
        if fragment in text:
            return line
    lowered = text.lower()
    for fragment in fragments:
        if fragment.lower() in lowered:
            return lowered.count("\n", 0, lowered.find(fragment.lower())) + 1
    return _first_nonempty_line(text)


def _label(path: str) -> str:
    return Path(path).stem or Path(path).name


def _candidate_id(*parts: Any) -> str:
    raw = "::".join(str(part) for part in parts)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]


def _dedupe(items: list[dict[str, Any]], key: str) -> list[dict[str, Any]]:
    seen: set[str] = set()
    out: list[dict[str, Any]] = []
    for item in items:
        value = str(item.get(key) or "")
        if not value or value in seen:
            continue
        seen.add(value)
        out.append(item)
    return out
