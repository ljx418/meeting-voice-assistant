"""V1.3 deterministic folder summary workflow runtime contract.

V1.3-C only provides a dry-run runtime. It consumes the V1.3-B folder scan
manifest and returns a WorkflowRun with step timeline and run report. It does
not extract file content, generate summaries, or create evidence citations.
"""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from data_service.folder_collection_contract import resolve_authorized_root_input, scan_folder_collection


class FolderSummaryWorkflowValidationError(ValueError):
    """Raised when a V1.3-C workflow request violates the runtime contract."""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _digest(prefix: str, *parts: object) -> str:
    value = "\n".join(str(part) for part in parts)
    return f"{prefix}_{hashlib.sha256(value.encode('utf-8')).hexdigest()[:16]}"


def _step(
    *,
    run_id: str,
    name: str,
    status: str,
    input_ref: str | None = None,
    output_ref: str | None = None,
    logs: list[str] | None = None,
    error_code: str | None = None,
    error_message: str | None = None,
    artifact_refs: list[str] | None = None,
) -> dict[str, Any]:
    timestamp = _now()
    payload: dict[str, Any] = {
        "step_id": _digest("step", run_id, name),
        "name": name,
        "status": status,
        "logs": list(logs or []),
        "started_at": timestamp,
        "finished_at": timestamp,
        "retry_count": 0,
        "artifact_refs": list(artifact_refs or []),
    }
    if input_ref:
        payload["input_ref"] = input_ref
    if output_ref:
        payload["output_ref"] = output_ref
    if error_code:
        payload["error_code"] = error_code
    if error_message:
        payload["error_message"] = error_message
    return payload


def run_folder_summary_workflow(
    *,
    workspace_id: str,
    workspace: Path,
    authorized_root: str,
    permission_grant_id: str,
    dry_run: bool = True,
    recursive: bool = True,
    include_extensions: list[str] | None = None,
    exclude_globs: list[str] | None = None,
    max_depth: int | None = None,
    max_file_size_bytes: int = 2 * 1024 * 1024,
    follow_symlinks: bool = False,
    confirm_extract: bool = False,
) -> dict[str, Any]:
    if not dry_run and not confirm_extract:
        raise FolderSummaryWorkflowValidationError("VALIDATION_ERROR: non-dry-run folder summary requires confirm_extract=true.")

    started_at = _now()
    scan = scan_folder_collection(
        workspace_id=workspace_id,
        workspace=workspace,
        authorized_root=authorized_root,
        permission_grant_id=permission_grant_id,
        dry_run=True,
        recursive=recursive,
        include_extensions=include_extensions,
        exclude_globs=exclude_globs,
        max_depth=max_depth,
        max_file_size_bytes=max_file_size_bytes,
        follow_symlinks=follow_symlinks,
    )
    collection = scan["collection"]
    run_id = _digest("run", workspace_id, collection["collection_id"], permission_grant_id)
    workflow_id = _digest("wf", workspace_id, "folder_summary_v1")
    collection_ref = f"folder_collection://{collection['collection_id']}"
    report_ref = f"workflow_run://{run_id}/report"
    grouped_folder_count = max(len(collection.get("folders", [])) - 1, 0)

    artifacts: list[dict[str, Any]] = []
    extracted_count = 0
    create_sources_status = "skipped"
    summarize_status = "skipped"
    index_status = "skipped"
    write_status = "skipped"
    if not dry_run:
        artifacts, extracted_count = _generate_summary_artifacts(
            workspace_id=workspace_id,
            workspace=workspace,
            authorized_root=authorized_root,
            collection=collection,
        )
        create_sources_status = "completed"
        summarize_status = "completed"
        index_status = "completed"
        write_status = "completed"

    steps = [
        _step(
            run_id=run_id,
            name="scan_folder",
            status="completed",
            output_ref=collection_ref,
            logs=[
                f"Manifest ready: folders={len(collection.get('folders', []))}, files={len(collection.get('files', []))}, skipped={len(collection.get('skipped_files', []))}.",
                "Response contains relative_path only.",
            ],
        ),
        _step(
            run_id=run_id,
            name="extract_text",
            status="skipped" if dry_run else "completed",
            input_ref=collection_ref,
            logs=[
                "V1.3-C dry-run runtime does not extract file content before user-confirmed workflow execution."
                if dry_run
                else f"Extracted md/txt content for {extracted_count} files after explicit confirm_extract=true."
            ],
        ),
        _step(
            run_id=run_id,
            name="group_by_subfolder",
            status="completed",
            input_ref=collection_ref,
            output_ref=report_ref,
            logs=[f"Grouped {len(collection.get('files', []))} md/txt files across {grouped_folder_count} subfolders."],
        ),
        _step(
            run_id=run_id,
            name="create_sources",
            status=create_sources_status,
            input_ref=collection_ref,
            logs=[
                "Source creation is deferred during dry-run."
                if dry_run
                else "Registered md/txt extracted files as workspace sources for summary evidence navigation."
            ],
        ),
        _step(
            run_id=run_id,
            name="summarize_folder",
            status=summarize_status,
            logs=[
                "Summary generation is owned by V1.3-D and is not executed in V1.3-C."
                if dry_run
                else f"Generated {len(artifacts)} deterministic SummaryArtifact records."
            ],
        ),
        _step(
            run_id=run_id,
            name="generate_index_report",
            status=index_status,
            logs=[
                "Index report generation is owned by V1.3-D after SummaryArtifact contract is active."
                if dry_run
                else "Generated root overview artifact from folder summaries."
            ],
        ),
        _step(
            run_id=run_id,
            name="write_artifacts",
            status=write_status,
            logs=[
                "No artifacts are written during the V1.3-C dry-run runtime."
                if dry_run
                else "Returned SummaryArtifact payloads without writing private filesystem output."
            ],
        ),
    ]
    finished_at = _now()
    workflow = {
        "workflow_id": workflow_id,
        "name": "Folder Summary V1",
        "template_id": "folder_summary_v1",
        "status": "ready",
        "required_permissions": ["folder:scan"],
        "steps": steps,
    }
    run = {
        "run_id": run_id,
        "workflow_id": workflow_id,
        "status": "completed",
        "created_at": started_at,
        "finished_at": finished_at,
        "dry_run": bool(dry_run),
        "run_report": {
            "scanned_file_count": len(collection.get("files", [])) + len(collection.get("skipped_files", [])),
            "manifest_file_count": len(collection.get("files", [])),
            "extracted_file_count": extracted_count,
            "skipped_file_count": len(collection.get("skipped_files", [])),
            "folder_count": len(collection.get("folders", [])),
            "generated_artifact_count": len(artifacts),
        },
        "artifacts": artifacts,
    }
    return {
        "workflow": workflow,
        "run": run,
        "collection": collection,
        "permission_grant": scan["permission_grant"],
    }


def _generate_summary_artifacts(
    *,
    workspace_id: str,
    workspace: Path,
    authorized_root: str,
    collection: dict[str, Any],
) -> tuple[list[dict[str, Any]], int]:
    root = Path(resolve_authorized_root_input(authorized_root)).expanduser().resolve()
    files = list(collection.get("files", []))
    folders_by_relative = {str(folder.get("relative_path")): folder for folder in collection.get("folders", [])}
    grouped: dict[str, list[dict[str, Any]]] = {}
    extracted_text: dict[str, str] = {}
    source_evidence_by_relative: dict[str, dict[str, Any]] = {}

    for file in files:
        relative_path = str(file.get("relative_path") or "")
        if not relative_path or relative_path.startswith("/") or ".." in Path(relative_path).parts:
            continue
        try:
            candidate = (root / relative_path).resolve()
            candidate.relative_to(root)
            text = candidate.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        extracted_text[relative_path] = text
        source_ref = _register_summary_source(
            workspace=workspace,
            root=root,
            file=file,
            relative_path=relative_path,
            text=text,
        )
        if source_ref:
            source_evidence_by_relative[relative_path] = source_ref
        top = relative_path.split("/", 1)[0] if "/" in relative_path else "."
        grouped.setdefault(top, []).append(file)

    artifacts: list[dict[str, Any]] = []
    collection_id = str(collection.get("collection_id"))
    schema_version = "v1.3-summary-artifact"
    for folder_relative, folder_files in sorted(grouped.items()):
        if folder_relative == ".":
            folder = folders_by_relative.get(".")
            title = "根目录文件总结"
            artifact_type = "root_summary"
        else:
            folder = folders_by_relative.get(folder_relative)
            title = f"{folder_relative} 子文件夹总结"
            artifact_type = "folder_summary"
        evidence_refs = [_evidence_ref(file, source_evidence_by_relative=source_evidence_by_relative) for file in folder_files]
        markdown = _folder_summary_markdown(title=title, files=folder_files, extracted_text=extracted_text)
        artifacts.append(
            {
                "artifact_id": _digest("sum", workspace_id, collection_id, folder_relative),
                "title": title,
                "artifact_type": artifact_type,
                "folder_id": folder.get("folder_id") if folder else None,
                "collection_id": collection_id,
                "status": "ready",
                "schema_version": schema_version,
                "coverage": {
                    "file_count": len(folder_files),
                    "extracted_file_count": len(folder_files),
                    "skipped_file_count": 0,
                    "evidence_ref_count": len(evidence_refs),
                },
                "markdown": markdown,
                "evidence_refs": evidence_refs,
            }
        )

    root_evidence = [
        _evidence_ref(file, source_evidence_by_relative=source_evidence_by_relative)
        for file in files
        if str(file.get("relative_path")) in extracted_text
    ]
    root_markdown = _folder_summary_markdown(title="根目录总览", files=files, extracted_text=extracted_text)
    artifacts.insert(
        0,
        {
            "artifact_id": _digest("sum", workspace_id, collection_id, "root-overview"),
            "title": "根目录总览",
            "artifact_type": "root_summary",
            "folder_id": folders_by_relative.get(".", {}).get("folder_id"),
            "collection_id": collection_id,
            "status": "ready",
            "schema_version": schema_version,
            "coverage": {
                "file_count": len(files),
                "extracted_file_count": len(extracted_text),
                "skipped_file_count": len(collection.get("skipped_files", [])),
                "evidence_ref_count": len(root_evidence),
            },
            "markdown": root_markdown,
            "evidence_refs": root_evidence,
        },
    )
    return artifacts, len(extracted_text)


def _read_json(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return default


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _document_unit_segments(text: str) -> list[str]:
    segments = [segment.strip() for segment in re.split(r"\n\s*\n+", text.strip()) if segment.strip()]
    return segments or ([text] if text else [])


def _stable_document_unit_id(*, source_id: str, order_index: int, text: str) -> str:
    text_digest = hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()[:16]
    digest = hashlib.sha256(f"{source_id}:{order_index}:{text_digest}".encode("utf-8")).hexdigest()[:16]
    return f"unit_{digest}"


def _stable_evidence_id(*, source_id: str, unit_id: str, start_offset: int, end_offset: int, snippet: str) -> str:
    digest = hashlib.sha256(
        f"{source_id}:{unit_id}:{start_offset}:{end_offset}:{snippet}".encode("utf-8", errors="replace")
    ).hexdigest()[:16]
    return f"ev_{digest}"


def _register_summary_source(
    *,
    workspace: Path,
    root: Path,
    file: dict[str, Any],
    relative_path: str,
    text: str,
) -> dict[str, Any] | None:
    try:
        candidate = (root / relative_path).resolve()
        candidate.relative_to(root)
        content = candidate.read_bytes()
    except OSError:
        return None
    sha256 = hashlib.sha256(content).hexdigest()
    source_id = f"src_{sha256[:16]}"
    title = Path(relative_path).stem or source_id
    imported_dir = workspace / "sources" / "imported"
    imported_dir.mkdir(parents=True, exist_ok=True)
    target = imported_dir / f"{source_id}{Path(relative_path).suffix or '.txt'}"
    if not target.exists():
        target.write_bytes(content)

    manifest_path = workspace / "lifecycle" / "sources.json"
    manifest = _read_json(manifest_path, {"items": []})
    existing = next((item for item in manifest.get("items", []) if item.get("source_id") == source_id), None)
    if not existing:
        manifest.setdefault("items", []).append(
            {
                "source_id": source_id,
                "sha256": sha256,
                "title": title,
                "status": "active",
                "path": str(target),
                "original_path": relative_path,
                "metadata": {"source_type": "markdown" if target.suffix.lower() == ".md" else "text", "origin": "folder_summary_v1"},
                "imported_at": _now(),
                "low_signal": {},
                "ingest_status": "pending",
            }
        )
        _write_json(manifest_path, manifest)

    first_segment = _document_unit_segments(text)[0] if text else ""
    unit_id = _stable_document_unit_id(source_id=source_id, order_index=0, text=first_segment)
    snippet = first_segment[: min(280, len(first_segment))]
    evidence_id = _stable_evidence_id(
        source_id=source_id,
        unit_id=unit_id,
        start_offset=0,
        end_offset=len(snippet),
        snippet=snippet,
    )
    return {
        "source_id": source_id,
        "source_title": title,
        "unit_id": unit_id,
        "evidence_id": evidence_id,
        "snippet": snippet,
        "file_id": file.get("file_id"),
        "relative_path": relative_path,
        "evidence_status": "source_unit_span",
    }


def _evidence_ref(file: dict[str, Any], *, source_evidence_by_relative: dict[str, dict[str, Any]]) -> dict[str, Any]:
    relative_path = str(file.get("relative_path") or "")
    source_ref = source_evidence_by_relative.get(relative_path)
    if source_ref:
        return dict(source_ref)
    return {
        "file_id": file.get("file_id"),
        "relative_path": relative_path,
        "evidence_status": "relative_path_only",
    }


def _folder_summary_markdown(*, title: str, files: list[dict[str, Any]], extracted_text: dict[str, str]) -> str:
    topic_counts: dict[str, int] = {}
    key_files: list[str] = []
    for file in files[:8]:
        relative_path = str(file.get("relative_path"))
        key_files.append(relative_path)
        text = extracted_text.get(relative_path, "")
        for line in text.splitlines():
            normalized = line.strip().lstrip("#").strip()
            if len(normalized) < 2 or len(normalized) > 80:
                continue
            topic_counts[normalized] = topic_counts.get(normalized, 0) + 1
            if len(topic_counts) >= 8:
                break
    topics = sorted(topic_counts, key=lambda item: (-topic_counts[item], item))[:5]
    lines = [
        f"# {title}",
        "",
        "## 概览",
        f"该分组包含 {len(files)} 个 md/txt 文件，摘要由确定性规则生成。",
        "",
        "## 主要主题",
    ]
    lines.extend([f"- {topic}" for topic in topics] or ["- 暂无可提取标题或短句。"])
    lines.extend(["", "## 关键文件"])
    lines.extend([f"- {relative_path}" for relative_path in key_files] or ["- 暂无文件。"])
    lines.extend(
        [
            "",
            "## 技术要点",
            "- 当前阶段只做 md/txt deterministic summary，不处理 PDF/PPTX/DOCX/video/audio/image。",
            "",
            "## 可复用材料",
            "- 可作为后续 Agent workflow 的 SummaryArtifact 输入。",
            "",
            "## 风险与缺口",
            "- V1.3-G 仅在 evidence refs 返回 source_id、unit_id、evidence_id 时启用 citation 回跳。",
        ]
    )
    return "\n".join(lines)
