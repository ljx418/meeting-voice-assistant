"""ResearchNotebook V2.5 artifact and provider contracts."""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from data_service.research_notebook.artifacts.binary_store import audio_descriptor, binary_descriptor, binary_path
from data_service.research_notebook.providers import capability_flags, provider_execution_status, provider_health, redact_public_value
from data_service.research_notebook.artifacts import create_ocr_artifact, ocr_status
from data_service.research_notebook.providers.pptx_exporter import PPTX_MIME_TYPE, export_slides_to_pptx
from data_service.research_notebook.providers.tts_espeak import synthesize_wav
from data_service.research_notebook.providers.tts_minimax import synthesize_minimax_tts


ARTIFACT_SCHEMA_VERSION = "research-notebook-artifact-2.5"
SUPPORTED_ARTIFACT_TYPES = {"studio", "slides", "audio_overview", "mindmap", "compare", "ocr"}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def artifacts_dir(workspace: Path) -> Path:
    return workspace / "research_notebook" / "artifacts"


def artifact_path(workspace: Path, artifact_id: str) -> Path:
    return artifacts_dir(workspace) / f"{_safe_id(artifact_id)}.json"


def list_artifacts(workspace: Path, *, workspace_id: str, artifact_type: str | None = None) -> list[dict[str, Any]]:
    items = []
    for path in sorted(artifacts_dir(workspace).glob("*.json")):
        artifact = _read_json(path, {})
        if not artifact:
            continue
        if artifact_type and artifact.get("type") != artifact_type:
            continue
        items.append(_public_artifact(artifact, workspace_id=workspace_id))
    return items


def read_artifact(workspace: Path, *, workspace_id: str, artifact_id: str) -> dict[str, Any] | None:
    artifact = _read_json(artifact_path(workspace, artifact_id), None)
    if not artifact:
        return None
    return _public_artifact(artifact, workspace_id=workspace_id)


def delete_artifact(workspace: Path, artifact_id: str) -> bool:
    path = artifact_path(workspace, artifact_id)
    if not path.exists():
        return False
    path.unlink()
    return True


def artifact_status(workspace: Path, artifact_id: str) -> dict[str, Any] | None:
    artifact = _read_json(artifact_path(workspace, artifact_id), None)
    if not artifact:
        return None
    return {
        "artifact_id": artifact.get("artifact_id"),
        "status": artifact.get("status", "ready"),
        "progress": 100 if artifact.get("status", "ready") == "ready" else 0,
        "unsupported_reason": artifact.get("unsupported_reason"),
        "error": artifact.get("error"),
    }


def download_descriptor(workspace: Path, *, workspace_id: str, artifact_id: str, fmt: str | None = None) -> dict[str, Any] | None:
    artifact = read_artifact(workspace, workspace_id=workspace_id, artifact_id=artifact_id)
    if not artifact:
        return None
    artifact_type = artifact.get("type")
    requested = (fmt or ("md" if artifact_type == "slides" else "json")).lower()
    supported_formats = _supported_download_formats(str(artifact_type or ""))
    if requested not in supported_formats:
        return {
            "error": {
                "code": "UNSUPPORTED_ARTIFACT_FORMAT",
                "message": f"Artifact format '{requested}' is not supported for {artifact_type}.",
                "retryable": False,
            },
            "artifact_id": artifact_id,
            "format": requested,
            "supported_formats": supported_formats,
        }
    if artifact_type == "audio_overview" and requested in {"wav", "audio"}:
        binary = dict(artifact.get("binary") or {})
        if not binary:
            return {
                "error": {
                    "code": "AUDIO_OVERVIEW_NOT_READY",
                    "message": "Audio binary is not available.",
                }
            }
        return {
            "url": binary.get("ref"),
            "format": "wav",
            "mime_type": binary.get("mime_type"),
            "size_bytes": binary.get("size_bytes"),
            "sha256": binary.get("sha256"),
            "duration_ms": binary.get("duration_ms"),
        }
    if artifact_type == "pptx_export" and requested in {"pptx", "binary"}:
        binary = dict(artifact.get("binary") or {})
        if not binary:
            return {
                "error": {
                    "code": "SLIDE_OUTLINE_ONLY",
                    "message": "PPTX binary is not available.",
                }
            }
        return {
            "url": binary.get("ref"),
            "format": "pptx",
            "mime_type": binary.get("mime_type"),
            "size_bytes": binary.get("size_bytes"),
            "sha256": binary.get("sha256"),
        }
    if requested == "pptx" and not capability_flags()["pptx_export"]:
        return {
            "error": {
                "code": "SLIDE_OUTLINE_ONLY",
                "message": "PPTX export not available, use Markdown download instead.",
            }
        }
    content = json.dumps(artifact, ensure_ascii=False, indent=2)
    if requested == "md" and artifact_type == "slides":
        content = _slides_markdown(artifact)
    return {
        "url": f"artifact://{workspace_id}/{artifact_id}?format={requested}",
        "format": requested,
        "size_bytes": len(content.encode("utf-8")),
    }


def _supported_download_formats(artifact_type: str) -> list[str]:
    if artifact_type == "slides":
        return ["json", "md"]
    if artifact_type == "audio_overview":
        return ["json", "wav", "audio"]
    if artifact_type == "pptx_export":
        return ["json", "pptx", "binary"]
    return ["json"]


def create_audio_artifact(workspace: Path, *, workspace_id: str, source_ids: list[str], language: str | None = None, voice_id: str | None = None) -> dict[str, Any]:
    health = provider_health("tts")
    if not health.get("available"):
        return _write_artifact(
            workspace,
            _base_artifact(
                workspace_id=workspace_id,
                artifact_type="audio_overview",
                title="Audio Overview",
                source_ids=source_ids,
                status="error",
                artifact_available=False,
                unsupported_reason="AUDIO_OVERVIEW_NOT_READY",
                error={"code": "AUDIO_OVERVIEW_NOT_READY", "message": "TTS provider is not configured."},
            ),
        )
    evidence = evidence_refs(workspace, source_ids=source_ids)
    if not evidence:
        return _insufficient_artifact(workspace, workspace_id=workspace_id, artifact_type="audio_overview", source_ids=source_ids, title="Audio Overview")
    artifact = _base_artifact(workspace_id=workspace_id, artifact_type="audio_overview", title="Audio Overview", source_ids=source_ids)
    script = [{"text": ref.get("snippet", ""), "start_time": 0.0, "end_time": 3.5, "evidence_refs": [ref]} for ref in evidence[:6]]
    script_text = " ".join(str(item.get("text") or "") for item in script)
    if health.get("provider") == "minimax":
        output_path = binary_path(workspace, str(artifact["artifact_id"]), "wav")
        tts_result = synthesize_minimax_tts(script_text, output_path, voice=voice_id)
        if not tts_result.get("ok"):
            artifact.update(
                {
                    "status": "error",
                    "artifact_available": False,
                    "script_available": True,
                    "audio_available": False,
                    "script": script,
                    "unsupported_reason": (tts_result.get("error") or {}).get("code"),
                    "error": tts_result.get("error"),
                    "provider": tts_result.get("provider"),
                    "citations": evidence,
                    "evidence_refs": evidence,
                }
            )
            return _write_artifact(workspace, artifact)
        binary = audio_descriptor(workspace, workspace_id=workspace_id, artifact_id=str(artifact["artifact_id"]), path=output_path)
        artifact.update(
            {
                "script_available": True,
                "audio_available": True,
                "script": script,
                "citations": evidence,
                "duration_seconds": round((binary.get("duration_ms") or 0) / 1000, 3),
                "voice_metadata": {
                    "provider": "minimax",
                    "engine": "minimax_t2a_v2",
                    "voice_id": voice_id or (tts_result.get("provider") or {}).get("voice_id"),
                    "language": language or "en-US",
                },
                "provider": tts_result.get("provider"),
                "binary": binary,
                "evidence_refs": evidence,
                "generation_metadata": {
                    "fallback_mode": False,
                    "evidence_ref_count": len(evidence),
                    "prompt_version": "v2_5_phase39_minimax_tts_real_run",
                    "provider": "minimax",
                    "engine": "minimax_t2a_v2",
                    "synthesis_duration_ms": tts_result.get("duration_ms"),
                },
            }
        )
        return _write_artifact(workspace, artifact)
    if health.get("provider") != "local":
        artifact.update(
            {
                "status": "error",
                "artifact_available": False,
                "script_available": True,
                "audio_available": False,
                "script": script,
                "unsupported_reason": "PROVIDER_UNSUPPORTED",
                "error": {"code": "PROVIDER_UNSUPPORTED", "message": "Configured TTS provider is not implemented in this local phase.", "retryable": False},
                "citations": evidence,
                "evidence_refs": evidence,
            }
        )
        return _write_artifact(workspace, artifact)
    output_path = binary_path(workspace, str(artifact["artifact_id"]), "wav")
    tts_result = synthesize_wav(script_text, output_path, voice=voice_id or "en")
    if not tts_result.get("ok"):
        artifact.update(
            {
                "status": "error",
                "artifact_available": False,
                "script_available": True,
                "audio_available": False,
                "script": script,
                "unsupported_reason": (tts_result.get("error") or {}).get("code"),
                "error": tts_result.get("error"),
                "provider": tts_result.get("provider"),
                "citations": evidence,
                "evidence_refs": evidence,
            }
        )
        return _write_artifact(workspace, artifact)
    binary = audio_descriptor(workspace, workspace_id=workspace_id, artifact_id=str(artifact["artifact_id"]), path=output_path)
    artifact.update(
        {
            "script_available": True,
            "audio_available": True,
            "script": script,
            "citations": evidence,
            "duration_seconds": round((binary.get("duration_ms") or 0) / 1000, 3),
            "voice_metadata": {
                "provider": health.get("provider"),
                "engine": "espeak-ng",
                "voice_id": voice_id or health.get("default_voice") or "en",
                "language": language or "en-US",
            },
            "provider": tts_result.get("provider"),
            "binary": binary,
            "evidence_refs": evidence,
            "generation_metadata": {
                "fallback_mode": False,
                "evidence_ref_count": len(evidence),
                "prompt_version": "v2_5_phase34_tts_provider_real_run",
                "provider": "local",
                "engine": "espeak-ng",
                "synthesis_duration_ms": tts_result.get("duration_ms"),
            },
        }
    )
    return _write_artifact(workspace, artifact)


def create_slides_artifact(workspace: Path, *, workspace_id: str, source_ids: list[str], topic: str | None = None, slide_count: int = 10) -> dict[str, Any]:
    evidence = evidence_refs(workspace, source_ids=source_ids)
    if not evidence:
        return _insufficient_artifact(workspace, workspace_id=workspace_id, artifact_type="slides", source_ids=source_ids, title="Presentation Overview")
    count = max(1, min(int(slide_count or 10), 30))
    title = topic or "Presentation Overview"
    slides = []
    for index in range(count):
        ref = evidence[index % len(evidence)]
        slides.append(
            {
                "slide_num": index + 1,
                "title": title if index == 0 else f"Evidence-backed point {index + 1}",
                "bullets": [_clip(ref.get("snippet") or "Source-backed point", 120)],
                "speaker_notes": "This slide is generated from available source evidence.",
                "layout_hint": "bullets",
                "evidence_refs": [ref],
            }
        )
    artifact = _base_artifact(workspace_id=workspace_id, artifact_type="slides", title=title, source_ids=source_ids)
    artifact.update({"slides": slides, "summary": f"{len(slides)} slide outline generated from source evidence.", "evidence_refs": evidence})
    return _write_artifact(workspace, artifact)


def create_mindmap_artifact(workspace: Path, *, workspace_id: str, source_ids: list[str], topic: str | None = None, max_depth: int = 3) -> dict[str, Any]:
    evidence = evidence_refs(workspace, source_ids=source_ids)
    if not evidence:
        return _insufficient_artifact(workspace, workspace_id=workspace_id, artifact_type="mindmap", source_ids=source_ids, title=f"Mindmap: {topic or 'Sources'}")
    children = []
    for index, ref in enumerate(evidence[: min(8, max(1, max_depth) * 3)]):
        children.append({"node_id": f"node_{index + 1}", "label": _clip(ref.get("source_title") or ref.get("source_id") or "Source", 48), "summary": _clip(ref.get("snippet") or "", 160), "parent_id": "node_root", "children": [], "evidence_refs": [ref]})
    artifact = _base_artifact(workspace_id=workspace_id, artifact_type="mindmap", title=f"Mindmap: {topic or 'Sources'}", source_ids=source_ids)
    artifact.update({"root_node": {"node_id": "node_root", "label": topic or "Sources", "children": children, "evidence_refs": evidence[:3]}, "evidence_refs": evidence})
    return _write_artifact(workspace, artifact)


def create_compare_artifact(workspace: Path, *, workspace_id: str, source_ids: list[str]) -> dict[str, Any]:
    if len(source_ids) < 2:
        return _base_error_artifact(workspace, workspace_id=workspace_id, artifact_type="compare", title="Document Comparison", source_ids=source_ids, code="INSUFFICIENT_SOURCES", message="资料不足，无法生成 Compare。请先添加更多 sources。")
    evidence = evidence_refs(workspace, source_ids=source_ids)
    by_source = {source_id: [ref for ref in evidence if ref.get("source_id") == source_id] for source_id in source_ids}
    if not all(by_source.get(source_id) for source_id in source_ids[:2]):
        return _insufficient_artifact(workspace, workspace_id=workspace_id, artifact_type="compare", source_ids=source_ids, title="Document Comparison")
    a, b = source_ids[0], source_ids[1]
    ref_a, ref_b = by_source[a][0], by_source[b][0]
    artifact = _base_artifact(workspace_id=workspace_id, artifact_type="compare", title="Document Comparison", source_ids=source_ids)
    artifact.update(
        {
            "compare_set": source_ids,
            "result": {
                "summary": "Deterministic comparison outline generated from cited source snippets.",
                "source_pairs": [
                    {
                        "source_a": a,
                        "source_b": b,
                        "source_a_title": ref_a.get("source_title"),
                        "source_b_title": ref_b.get("source_title"),
                        "similarities": [{"topic": "Shared evidence basis", "description": "Both sources have extractable evidence snippets.", "evidence_refs": [ref_a, ref_b]}],
                        "differences": [{"topic": "Source-specific wording", "source_a_position": _clip(ref_a.get("snippet") or "", 140), "source_b_position": _clip(ref_b.get("snippet") or "", 140), "evidence_a": [ref_a], "evidence_b": [ref_b]}],
                        "conflicts": [],
                    }
                ],
            },
            "evidence_refs": evidence,
        }
    )
    return _write_artifact(workspace, artifact)


def export_slides(workspace: Path, *, workspace_id: str, artifact_id: str) -> dict[str, Any]:
    artifact = read_artifact(workspace, workspace_id=workspace_id, artifact_id=artifact_id)
    if not artifact:
        return {"error": {"code": "not_found", "message": "Artifact not found."}}
    if not capability_flags()["pptx_export"]:
        return {"error": {"code": "SLIDE_OUTLINE_ONLY", "message": "PPTX export not available, use Markdown download instead."}}
    slides = list(artifact.get("slides") or [])
    export_artifact = _base_artifact(
        workspace_id=workspace_id,
        artifact_type="pptx_export",
        title=f"PPTX Export: {artifact.get('title') or artifact_id}",
        source_ids=list(artifact.get("source_ids") or []),
    )
    output_path = binary_path(workspace, str(export_artifact["artifact_id"]), "pptx")
    result = export_slides_to_pptx(slides, output_path)
    if not result.get("ok"):
        export_artifact.update(
            {
                "status": "error",
                "artifact_available": False,
                "source_slides_artifact_id": artifact_id,
                "slide_count": len(slides),
                "unsupported_reason": (result.get("error") or {}).get("code"),
                "error": result.get("error"),
                "evidence_refs": artifact.get("evidence_refs") or [],
            }
        )
        return _write_artifact(workspace, export_artifact)
    binary = binary_descriptor(workspace, workspace_id=workspace_id, artifact_id=str(export_artifact["artifact_id"]), path=output_path, binary="pptx", mime_type=PPTX_MIME_TYPE)
    export_artifact.update(
        {
            "source_slides_artifact_id": artifact_id,
            "slide_count": int(result.get("slide_count") or len(slides)),
            "binary": binary,
            "format": "pptx",
            "mime_type": PPTX_MIME_TYPE,
            "evidence_refs": artifact.get("evidence_refs") or [],
            "generation_metadata": {
                "fallback_mode": False,
                "evidence_ref_count": len(artifact.get("evidence_refs") or []),
                "prompt_version": "v2_5_phase35_pptx_export_real_run",
                "exporter": "local_openxml",
                "source_slides_artifact_id": artifact_id,
            },
        }
    )
    return _write_artifact(workspace, export_artifact)


def evidence_refs(workspace: Path, *, source_ids: list[str]) -> list[dict[str, Any]]:
    manifest = _read_json(workspace / "lifecycle" / "sources.json", {"items": []})
    wanted = set(source_ids or [])
    refs = []
    for item in manifest.get("items", []):
        source_id = str(item.get("source_id") or "")
        if wanted and source_id not in wanted:
            continue
        if item.get("status") != "active":
            continue
        snippet = _source_snippet(item)
        if not snippet:
            continue
        refs.append(
            {
                "source_id": source_id,
                "source_title": item.get("title") or source_id,
                "snippet": snippet,
                "confidence": 0.75,
            }
        )
    return refs


def _source_snippet(item: dict[str, Any]) -> str:
    path = item.get("path")
    if not path:
        return ""
    try:
        text = Path(str(path)).read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""
    text = re.sub(r"\s+", " ", text).strip()
    return _clip(text, 240)


def _base_artifact(*, workspace_id: str, artifact_type: str, title: str, source_ids: list[str], status: str = "ready", artifact_available: bool = True, unsupported_reason: str | None = None, error: dict[str, Any] | None = None) -> dict[str, Any]:
    created_at = now_iso()
    digest = hashlib.sha256(f"{workspace_id}:{artifact_type}:{title}:{','.join(source_ids)}:{created_at}".encode("utf-8")).hexdigest()[:12]
    return {
        "schema_version": ARTIFACT_SCHEMA_VERSION,
        "artifact_id": f"art_{artifact_type}_{digest}",
        "workspace_id": workspace_id,
        "type": artifact_type,
        "artifact_type": artifact_type,
        "title": title,
        "status": status,
        "artifact_available": artifact_available,
        "summary": "",
        "source_ids": source_ids,
        "evidence_refs": [],
        "unsupported_reason": unsupported_reason,
        "generation_metadata": {"fallback_mode": True, "evidence_ref_count": 0, "prompt_version": "v2_5_research_notebook_artifact_contract"},
        "created_at": created_at,
        "updated_at": created_at,
        "error": error,
    }


def _insufficient_artifact(workspace: Path, *, workspace_id: str, artifact_type: str, source_ids: list[str], title: str) -> dict[str, Any]:
    return _base_error_artifact(workspace, workspace_id=workspace_id, artifact_type=artifact_type, title=title, source_ids=source_ids, code="INSUFFICIENT_SOURCES", message=f"资料不足，无法生成 {artifact_type}。请先添加更多 sources。")


def _base_error_artifact(workspace: Path, *, workspace_id: str, artifact_type: str, title: str, source_ids: list[str], code: str, message: str) -> dict[str, Any]:
    return _write_artifact(workspace, _base_artifact(workspace_id=workspace_id, artifact_type=artifact_type, title=title, source_ids=source_ids, status="error", artifact_available=False, unsupported_reason=code, error={"code": code, "message": message}))


def _write_artifact(workspace: Path, artifact: dict[str, Any]) -> dict[str, Any]:
    path = artifact_path(workspace, str(artifact["artifact_id"]))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(artifact, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return _public_artifact(artifact, workspace_id=str(artifact["workspace_id"]))


def _public_artifact(artifact: dict[str, Any], *, workspace_id: str) -> dict[str, Any]:
    payload = dict(artifact)
    payload["workspace_id"] = workspace_id
    payload["artifact_ref"] = f"artifact://{workspace_id}/{artifact.get('artifact_id')}"
    return _strip_public_artifact(payload)


def _read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return default


def _slides_markdown(artifact: dict[str, Any]) -> str:
    lines = [f"# {artifact.get('title') or 'Slides'}", ""]
    for slide in artifact.get("slides") or []:
        lines.append(f"## {slide.get('slide_num')}. {slide.get('title')}")
        for bullet in slide.get("bullets") or []:
            lines.append(f"- {bullet}")
        lines.append("")
    return "\n".join(lines)


def _safe_id(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "-", str(value or "")).strip("-")[:160]


def _clip(value: object, limit: int) -> str:
    text = str(value or "").strip()
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "..."


def _strip_public_artifact(value: Any) -> Any:
    if isinstance(value, list):
        return [_strip_public_artifact(item) for item in value]
    if isinstance(value, dict):
        return {
            key: _strip_public_artifact(item)
            for key, item in value.items()
            if key not in {"path", "paths", "artifact_path", "physical_path"}
        }
    return redact_public_value(value)
