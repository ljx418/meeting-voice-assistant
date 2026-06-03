"""Binary artifact storage helpers for ResearchNotebook V2.5."""

from __future__ import annotations

import hashlib
import wave
from pathlib import Path
from typing import Any


def binaries_dir(workspace: Path) -> Path:
    return workspace / "research_notebook" / "artifacts" / "binaries"


def binary_path(workspace: Path, artifact_id: str, extension: str) -> Path:
    suffix = extension if extension.startswith(".") else f".{extension}"
    return binaries_dir(workspace) / f"{_safe_id(artifact_id)}{suffix}"


def audio_descriptor(workspace: Path, *, workspace_id: str, artifact_id: str, path: Path, mime_type: str = "audio/wav") -> dict[str, Any]:
    descriptor = binary_descriptor(workspace, workspace_id=workspace_id, artifact_id=artifact_id, path=path, binary="audio", mime_type=mime_type)
    descriptor["duration_ms"] = _wav_duration_ms(path) if mime_type == "audio/wav" else None
    return descriptor


def binary_descriptor(workspace: Path, *, workspace_id: str, artifact_id: str, path: Path, binary: str, mime_type: str) -> dict[str, Any]:
    data = Path(path).read_bytes()
    return {
        "ref": f"artifact://{workspace_id}/{artifact_id}?binary={binary}",
        "mime_type": mime_type,
        "size_bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
    }


def _wav_duration_ms(path: Path) -> int:
    try:
        with wave.open(str(path), "rb") as handle:
            frames = handle.getnframes()
            rate = handle.getframerate()
            if rate <= 0:
                return 0
            return int((frames / float(rate)) * 1000)
    except (wave.Error, OSError, EOFError):
        return 0


def _safe_id(value: str) -> str:
    import re

    return re.sub(r"[^A-Za-z0-9._-]+", "-", str(value or "")).strip("-")[:160]
