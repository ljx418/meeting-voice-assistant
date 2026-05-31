"""Path validation for V2 codebase assets."""

from __future__ import annotations

from pathlib import Path

from data_service.security import configured_allowed_roots, default_allowed_roots, is_relative_to_any


def validate_codebase_root(path: str | Path, *, workspace: str | Path) -> Path:
    resolved = Path(path).expanduser().resolve()
    workspace_path = Path(workspace).expanduser().resolve()
    fallback_roots = [workspace_path, workspace_path.parent, *default_allowed_roots()]
    roots = configured_allowed_roots("DATA_SERVICE_ALLOWED_CODEBASE_ROOTS", fallback=fallback_roots)
    if not is_relative_to_any(resolved, roots):
        raise ValueError("CODEBASE_PATH_NOT_ALLOWED")
    return resolved
