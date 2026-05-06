"""Security helpers for data_service entry points."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path
from typing import Iterable, List, Sequence


def _split_roots(value: str) -> List[Path]:
    roots: List[Path] = []
    for item in value.split(os.pathsep):
        item = item.strip()
        if item:
            roots.append(Path(item).expanduser().resolve())
    return roots


def default_allowed_roots() -> List[Path]:
    repo_root = Path(__file__).resolve().parents[2]
    roots = [
        repo_root,
        repo_root / "workspace",
        Path("/tmp"),
        Path(tempfile.gettempdir()),
    ]
    home_workspace = Path.home() / "Desktop" / "workspace"
    if home_workspace.exists():
        roots.append(home_workspace)
    return roots


def configured_allowed_roots(env_name: str, fallback: Sequence[Path] | None = None) -> List[Path]:
    configured = os.getenv(env_name, "").strip()
    if configured:
        return _split_roots(configured)
    return [Path(root).expanduser().resolve() for root in (fallback or default_allowed_roots())]


def is_relative_to_any(path: Path, roots: Iterable[Path]) -> bool:
    resolved = Path(path).expanduser().resolve()
    for root in roots:
        root = Path(root).expanduser().resolve()
        if resolved == root or root in resolved.parents:
            return True
    return False


def validate_workspace_path(workspace: str | Path) -> Path:
    resolved = Path(workspace).expanduser().resolve()
    roots = configured_allowed_roots("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS")
    if not is_relative_to_any(resolved, roots):
        allowed = ", ".join(str(root) for root in roots)
        raise ValueError(f"Workspace is outside allowed roots: {resolved}. Allowed roots: {allowed}")
    return resolved


def validate_source_paths(paths: Iterable[str | Path], *, workspace: str | Path) -> List[str]:
    workspace_path = Path(workspace).expanduser().resolve()
    fallback_roots = [workspace_path, workspace_path.parent, *default_allowed_roots()]
    roots = configured_allowed_roots("DATA_SERVICE_ALLOWED_SOURCE_ROOTS", fallback=fallback_roots)
    validated: List[str] = []
    for raw_path in paths:
        resolved = Path(raw_path).expanduser().resolve()
        if not is_relative_to_any(resolved, roots):
            allowed = ", ".join(str(root) for root in roots)
            raise ValueError(f"Source path is outside allowed roots: {resolved}. Allowed roots: {allowed}")
        validated.append(str(resolved))
    return validated
