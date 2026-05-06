"""Filesystem-backed artifact registry for gateway-visible outputs."""

from __future__ import annotations

import json
import mimetypes
from datetime import datetime
from pathlib import Path
from typing import Any, Optional, Union

from apps.gateway.persistence import atomic_write_text, read_json_locked, update_json_list_locked
from apps.gateway.protocol import new_id
from apps.gateway.secrets import mask_value
from core.config import get_meeting_mcp_config


MAX_INLINE_ARTIFACT_READ_BYTES = 1024 * 1024
VIDEO_MIME_PREFIXES = ("video/",)


class ArtifactError(RuntimeError):
    """Raised when artifact registration or reading fails."""


class ArtifactRegistry:
    """Register existing output files as harnessOS artifacts."""

    def __init__(
        self,
        root: Optional[Union[str, Path]] = None,
        *,
        allowed_roots: Optional[list[Union[str, Path]]] = None,
    ) -> None:
        default_root = Path(__file__).resolve().parents[2] / ".harnessos" / "artifacts"
        self.root = Path(root or default_root).expanduser().resolve()
        self.index_path = self.root / "index.json"
        self.allowed_roots = _default_allowed_roots(self.root, allowed_roots)

    def register_file(
        self,
        path: str,
        *,
        session_id: Optional[str] = None,
        turn_id: Optional[str] = None,
        app_id: str = "default",
        project_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        domain: Optional[str] = None,
        kind: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Register an existing local file without moving it."""
        file_path = Path(path).expanduser().resolve()
        if not file_path.exists() or not file_path.is_file():
            raise ArtifactError(f"Artifact file does not exist: {file_path}")
        if not _is_under_allowed_root(file_path, self.allowed_roots):
            raise ArtifactError(f"Artifact file is outside allowed roots: {file_path}")

        record = {
            "artifact_id": new_id("art"),
            "session_id": session_id,
            "turn_id": turn_id,
            "app_id": app_id,
            "project_id": project_id,
            "workspace_id": workspace_id,
            "domain": domain,
            "kind": kind or file_path.stem,
            "name": file_path.name,
            "path": str(file_path),
            "mime": _guess_mime(file_path),
            "size": file_path.stat().st_size,
            "created_at": datetime.now().isoformat(),
            "metadata": mask_value(metadata or {}),
        }
        return update_json_list_locked(
            self.index_path,
            lambda records: _append_record(records, record),
            ArtifactError,
        )

    def register_external(
        self,
        *,
        external_asset_uri: str,
        session_id: Optional[str] = None,
        turn_id: Optional[str] = None,
        app_id: str = "default",
        project_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        domain: Optional[str] = None,
        kind: str = "external_asset",
        name: str = "",
        mime: str = "application/octet-stream",
        preview_uri: Optional[str] = None,
        thumbnail_uri: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Register an external asset without copying or reading its content."""
        if not external_asset_uri.strip():
            raise ArtifactError("external_asset_uri is required")
        record = {
            "artifact_id": new_id("art"),
            "session_id": session_id,
            "turn_id": turn_id,
            "app_id": app_id,
            "project_id": project_id,
            "workspace_id": workspace_id,
            "domain": domain,
            "kind": kind,
            "name": name or external_asset_uri.rsplit("/", 1)[-1],
            "path": None,
            "uri": external_asset_uri,
            "external_asset_uri": external_asset_uri,
            "preview_uri": preview_uri,
            "thumbnail_uri": thumbnail_uri,
            "mime": mime,
            "size": None,
            "created_at": datetime.now().isoformat(),
            "metadata": mask_value(metadata or {}),
        }
        return update_json_list_locked(
            self.index_path,
            lambda records: _append_record(records, record),
            ArtifactError,
        )

    def list_artifacts(
        self,
        *,
        session_id: Optional[str] = None,
        domain: Optional[str] = None,
        kind: Optional[str] = None,
        app_id: Optional[str] = None,
        project_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """List registered artifacts, optionally filtered."""
        records = self._load_index()
        if session_id is not None:
            records = [record for record in records if record.get("session_id") == session_id]
        if domain is not None:
            records = [record for record in records if record.get("domain") == domain]
        if kind is not None:
            records = [record for record in records if record.get("kind") == kind]
        if app_id is not None:
            records = [record for record in records if record.get("app_id", "default") == app_id]
        if project_id is not None:
            records = [record for record in records if record.get("project_id") == project_id]
        if workspace_id is not None:
            records = [record for record in records if record.get("workspace_id") == workspace_id]
        return records

    def get_artifact(self, artifact_id: str) -> dict[str, Any]:
        """Return one artifact record."""
        for record in self._load_index():
            if record.get("artifact_id") == artifact_id:
                return record
        raise KeyError(f"Artifact not found: {artifact_id}")

    def read_artifact(self, artifact_id: str) -> dict[str, Any]:
        """Read one artifact as text or JSON."""
        record = self.get_artifact(artifact_id)
        mime = str(record.get("mime") or "application/octet-stream")
        if any(mime.startswith(prefix) for prefix in VIDEO_MIME_PREFIXES):
            raise ArtifactError("Video artifacts cannot be read inline; use artifact.read_metadata.")
        size = record.get("size")
        if isinstance(size, int) and size > MAX_INLINE_ARTIFACT_READ_BYTES:
            raise ArtifactError("Large artifacts cannot be read inline; use artifact.read_metadata.")
        raw_path = record.get("path")
        if not isinstance(raw_path, str) or not raw_path:
            raise ArtifactError("External artifacts cannot be read inline; use artifact.read_metadata.")
        path = Path(raw_path).expanduser().resolve()
        if not path.exists() or not path.is_file():
            raise ArtifactError(f"Artifact file does not exist: {path}")
        if not _is_under_allowed_root(path, self.allowed_roots):
            raise ArtifactError(f"Artifact file is outside allowed roots: {path}")
        text = path.read_text(encoding="utf-8")
        content: Any = text
        if record.get("mime") == "application/json" or path.suffix.lower() == ".json":
            content = json.loads(text)
        return {"artifact": mask_value(record), "content": mask_value(content)}

    def read_metadata(self, artifact_id: str) -> dict[str, Any]:
        """Return artifact metadata without reading content."""
        return {"artifact": mask_value(self.get_artifact(artifact_id))}

    def _load_index(self) -> list[dict[str, Any]]:
        if not self.index_path.exists():
            return []
        payload = read_json_locked(self.index_path, [], ArtifactError)
        if not isinstance(payload, list):
            raise ArtifactError(f"Artifact index must be a list: {self.index_path}")
        return [record for record in payload if isinstance(record, dict)]

    def _save_index(self, records: list[dict[str, Any]]) -> None:
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        atomic_write_text(
            self.index_path,
            json.dumps(records, ensure_ascii=False, indent=2) + "\n",
        )


def _guess_mime(path: Path) -> str:
    if path.suffix.lower() == ".md":
        return "text/markdown"
    guessed, _encoding = mimetypes.guess_type(str(path))
    return guessed or "application/octet-stream"


def _append_record(records: list[dict[str, Any]], record: dict[str, Any]) -> dict[str, Any]:
    records.append(record)
    return record


def _default_allowed_roots(
    root: Path,
    configured: Optional[list[Union[str, Path]]],
) -> list[Path]:
    roots = [root, root.parent, Path(__file__).resolve().parents[2]]
    if configured:
        roots.extend(Path(item).expanduser() for item in configured)
    try:
        meeting_config = get_meeting_mcp_config()
        meeting_cwd = Path(meeting_config.cwd).expanduser()
        roots.append(meeting_cwd)
        roots.append(meeting_cwd.parent)
        if meeting_config.output_root:
            roots.append(Path(meeting_config.output_root).expanduser())
    except Exception:
        pass
    resolved: list[Path] = []
    for item in roots:
        try:
            resolved.append(item.resolve())
        except OSError:
            continue
    return resolved


def _is_under_allowed_root(path: Path, allowed_roots: list[Path]) -> bool:
    return any(path == root or root in path.parents for root in allowed_roots)
