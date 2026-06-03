"""OCR artifact persistence for ResearchNotebook V2.5."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from data_service.research_notebook.providers.ocr_tesseract import run_tesseract_ocr
from data_service.research_notebook.providers.redaction import redact_public_value


ARTIFACT_SCHEMA_VERSION = "research-notebook-artifact-2.5"


def create_ocr_artifact(workspace: Path, *, workspace_id: str, source_id: str) -> dict[str, Any]:
    record = _source_record(workspace, source_id)
    if not record:
        return _public_error(workspace_id, source_id, "SOURCE_NOT_FOUND", "Source was not found.")
    source_path = _safe_source_path(workspace, record)
    if not source_path:
        return _public_error(workspace_id, source_id, "SOURCE_NOT_FOUND", "Source file was not found.")

    result = run_tesseract_ocr(source_path)
    if not result.get("ok"):
        artifact = _base_artifact(workspace_id=workspace_id, source_id=source_id, source_record=record, status="error", artifact_available=False)
        artifact.update(
            {
                "unsupported_reason": (result.get("error") or {}).get("code"),
                "error": result.get("error"),
                "provider": result.get("provider"),
                "pages": [],
            }
        )
        return _write_artifact(workspace, artifact)

    pages = _attach_evidence(result.get("pages") or [], source_id=source_id)
    artifact = _base_artifact(workspace_id=workspace_id, source_id=source_id, source_record=record)
    artifact.update(
        {
            "provider": result.get("provider"),
            "pages": pages,
            "summary": _summary(pages),
            "evidence_refs": _page_evidence(pages),
            "generation_metadata": {
                "fallback_mode": False,
                "provider": "tesseract",
                "rasterizer": (result.get("rasterizer") or {}).get("name") or "none",
                "rasterizer_version": (result.get("rasterizer") or {}).get("version"),
                "embedded_text_probe": result.get("embedded_text_probe"),
                "duration_ms": result.get("duration_ms"),
                "evidence_ref_count": len(_page_evidence(pages)),
                "prompt_version": "v2_5_phase33_ocr_provider_real_run",
            },
        }
    )
    return _write_artifact(workspace, artifact)


def ocr_status(workspace: Path, *, workspace_id: str, source_id: str) -> dict[str, Any]:
    artifacts = []
    for path in sorted(_artifacts_dir(workspace).glob("*.json")):
        payload = _read_json(path, {})
        if payload.get("artifact_type") == "ocr" and payload.get("source_id") == source_id:
            artifacts.append(payload)
    if artifacts:
        latest = sorted(artifacts, key=lambda item: str(item.get("updated_at") or item.get("created_at") or ""))[-1]
        return {
            "source_id": source_id,
            "status": latest.get("status", "ready"),
            "progress": 100 if latest.get("status") == "ready" else 0,
            "artifact_id": latest.get("artifact_id"),
            "artifact_ref": f"artifact://{workspace_id}/{latest.get('artifact_id')}",
            "error": latest.get("error"),
        }
    return {"source_id": source_id, "status": "not_started", "progress": 0}


def _base_artifact(*, workspace_id: str, source_id: str, source_record: dict[str, Any], status: str = "ready", artifact_available: bool = True) -> dict[str, Any]:
    created_at = _now_iso()
    digest = hashlib.sha256(f"{workspace_id}:ocr:{source_id}:{created_at}".encode("utf-8")).hexdigest()[:12]
    return {
        "schema_version": ARTIFACT_SCHEMA_VERSION,
        "artifact_id": f"art_ocr_{digest}",
        "workspace_id": workspace_id,
        "type": "ocr",
        "artifact_type": "ocr",
        "title": f"OCR: {source_record.get('title') or source_id}",
        "status": status,
        "artifact_available": artifact_available,
        "source_id": source_id,
        "source_ids": [source_id],
        "source_metadata": {
            "source_type": (source_record.get("metadata") or {}).get("source_type"),
            "file_name": (source_record.get("metadata") or {}).get("file_name"),
            "content_type": (source_record.get("metadata") or {}).get("content_type"),
        },
        "pages": [],
        "evidence_refs": [],
        "summary": "",
        "unsupported_reason": None,
        "error": None,
        "generation_metadata": {
            "fallback_mode": False,
            "provider": "tesseract",
            "evidence_ref_count": 0,
            "prompt_version": "v2_5_phase33_ocr_provider_real_run",
        },
        "created_at": created_at,
        "updated_at": created_at,
    }


def _write_artifact(workspace: Path, artifact: dict[str, Any]) -> dict[str, Any]:
    path = _artifacts_dir(workspace) / f"{_safe_id(artifact['artifact_id'])}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(artifact, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return _public_artifact(artifact, workspace_id=str(artifact["workspace_id"]))


def _public_artifact(artifact: dict[str, Any], *, workspace_id: str) -> dict[str, Any]:
    payload = dict(artifact)
    payload["workspace_id"] = workspace_id
    payload["artifact_ref"] = f"artifact://{workspace_id}/{artifact.get('artifact_id')}"
    return _strip_public(payload)


def _public_error(workspace_id: str, source_id: str, code: str, message: str) -> dict[str, Any]:
    return {
        "schema_version": ARTIFACT_SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "type": "ocr",
        "artifact_type": "ocr",
        "status": "error",
        "artifact_available": False,
        "source_id": source_id,
        "source_ids": [source_id],
        "pages": [],
        "error": {"code": code, "message": message, "retryable": False},
        "unsupported_reason": code,
    }


def _source_record(workspace: Path, source_id: str) -> dict[str, Any] | None:
    manifest = _read_json(workspace / "lifecycle" / "sources.json", {"items": []})
    for item in manifest.get("items", []):
        if item.get("source_id") == source_id:
            return dict(item)
    return None


def _safe_source_path(workspace: Path, record: dict[str, Any]) -> Path | None:
    raw = str(record.get("path") or "").strip()
    if not raw:
        return None
    path = Path(raw).expanduser().resolve()
    try:
        path.relative_to(workspace.resolve())
    except ValueError:
        return None
    return path if path.is_file() else None


def _attach_evidence(pages: list[dict[str, Any]], *, source_id: str) -> list[dict[str, Any]]:
    result = []
    for page in pages:
        page_index = int(page.get("page_index") or 0)
        blocks = []
        for block_index, block in enumerate(page.get("blocks") or []):
            public_block = dict(block)
            locator = dict(public_block.get("locator") or {})
            locator.setdefault("page", page_index + 1)
            locator.setdefault("block_index", block_index)
            evidence = {
                "source_id": source_id,
                "locator": f"source://{source_id}#page={locator['page']}&block={locator['block_index']}",
                "confidence": public_block.get("confidence"),
            }
            public_block["locator"] = locator
            public_block["evidence_refs"] = [evidence]
            blocks.append(public_block)
        result.append({"page_index": page_index, "blocks": blocks})
    return result


def _page_evidence(pages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    refs = []
    for page in pages:
        for block in page.get("blocks") or []:
            refs.extend(block.get("evidence_refs") or [])
    return refs


def _summary(pages: list[dict[str, Any]]) -> str:
    texts = []
    for page in pages:
        for block in page.get("blocks") or []:
            text = str(block.get("text") or "").strip()
            if text:
                texts.append(text)
    joined = " ".join(texts)
    return joined[:280]


def _artifacts_dir(workspace: Path) -> Path:
    return workspace / "research_notebook" / "artifacts"


def _read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return default


def _safe_id(value: str) -> str:
    import re

    return re.sub(r"[^A-Za-z0-9._-]+", "-", str(value or "")).strip("-")[:160]


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _strip_public(value: Any) -> Any:
    if isinstance(value, list):
        return [_strip_public(item) for item in value]
    if isinstance(value, dict):
        return {
            key: _strip_public(item)
            for key, item in value.items()
            if key not in {"path", "paths", "artifact_path", "physical_path"}
        }
    return redact_public_value(value)
