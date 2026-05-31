"""V1.3 folder collection contract for authorized local folder scans.

This module intentionally returns only relative paths. The caller may provide
an absolute authorized root, but that value must not be reflected in response
payloads, fixtures, or workflow logs.
"""

from __future__ import annotations

import fnmatch
import hashlib
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any

from data_service.security import validate_source_paths

SUPPORTED_TEXT_EXTENSIONS = {".md", ".txt"}
DEFAULT_EXCLUDED_DIRS = {
    ".git",
    ".hg",
    ".svn",
    ".cache",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    "__pycache__",
    "node_modules",
    "dist",
    "build",
}
SECRET_LIKE_NAMES = {
    ".env",
    ".env.local",
    ".env.production",
    "id_rsa",
    "id_dsa",
    "id_ecdsa",
    "id_ed25519",
}
SECRET_LIKE_SUFFIXES = {".pem", ".key", ".crt", ".p12", ".pfx"}


class FolderCollectionValidationError(ValueError):
    """Raised when the folder scan request violates the V1.3 contract."""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _digest(prefix: str, *parts: object) -> str:
    value = "\n".join(str(part) for part in parts)
    return f"{prefix}_{hashlib.sha256(value.encode('utf-8')).hexdigest()[:16]}"


def _relative_path(root: Path, path: Path) -> str:
    if path == root:
        return "."
    return PurePosixPath(path.relative_to(root).as_posix()).as_posix()


def _parent_relative(relative_path: str) -> str | None:
    if relative_path == ".":
        return None
    parent = PurePosixPath(relative_path).parent.as_posix()
    return "." if parent == "." else parent


def _normalize_extensions(values: list[str] | None) -> set[str]:
    if not values:
        return set(SUPPORTED_TEXT_EXTENSIONS)
    normalized = {value.lower() if value.startswith(".") else f".{value.lower()}" for value in values}
    unsupported = sorted(normalized - SUPPORTED_TEXT_EXTENSIONS)
    if unsupported:
        raise FolderCollectionValidationError(
            f"VALIDATION_ERROR: V1.3-B folder scan only supports md/txt include_extensions: {', '.join(unsupported)}"
        )
    return normalized


def _is_hidden(path: Path, root: Path) -> bool:
    if path == root:
        return False
    return any(part.startswith(".") for part in path.relative_to(root).parts)


def _is_secret_like(path: Path) -> bool:
    name = path.name.lower()
    if name in SECRET_LIKE_NAMES:
        return True
    if path.suffix.lower() in SECRET_LIKE_SUFFIXES:
        return True
    return any(token in name for token in ("secret", "token", "credential", "private-key"))


def _matches_exclude(relative_path: str, exclude_globs: list[str]) -> bool:
    return any(fnmatch.fnmatch(relative_path, pattern) for pattern in exclude_globs)


def _is_binary_file(path: Path) -> bool:
    try:
        sample = path.read_bytes()[:1024]
    except OSError:
        return False
    return b"\0" in sample


def _skip(relative_path: str, reason: str) -> dict[str, str]:
    return {"relative_path": relative_path, "skipped_reason": reason}


def resolve_authorized_root_input(value: str) -> str:
    normalized = str(value or "").strip()
    if normalized.startswith("Desktop/"):
        return str(Path.home() / normalized)
    if normalized.startswith("桌面/"):
        return str(Path.home() / "Desktop" / normalized.split("/", 1)[1])
    return normalized


def scan_folder_collection(
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
) -> dict[str, Any]:
    """Return a sanitized V1.3 folder manifest for an authorized local folder."""

    if not dry_run:
        raise FolderCollectionValidationError("VALIDATION_ERROR: V1.3-B only supports dry_run=true folder manifest scans.")
    if follow_symlinks:
        raise FolderCollectionValidationError("VALIDATION_ERROR: V1.3-B requires follow_symlinks=false.")
    if not permission_grant_id.strip():
        raise FolderCollectionValidationError("VALIDATION_ERROR: permission_grant_id is required.")
    if max_depth is not None and max_depth < 0:
        raise FolderCollectionValidationError("VALIDATION_ERROR: max_depth must be non-negative.")

    extensions = _normalize_extensions(include_extensions)
    excludes = list(exclude_globs or [])
    root = Path(validate_source_paths([resolve_authorized_root_input(authorized_root)], workspace=workspace)[0])
    if not root.exists() or not root.is_dir():
        raise FolderCollectionValidationError("VALIDATION_ERROR: authorized_root must be an existing directory.")

    root_label = root.name or "authorized-folder"
    collection_id = _digest("fc", workspace_id, root_label, permission_grant_id)
    folder_ids: dict[str, str] = {}
    folder_meta: dict[str, dict[str, int]] = {}
    files: list[dict[str, Any]] = []
    skipped_files: list[dict[str, str]] = []

    def folder_id(relative_path: str) -> str:
        if relative_path not in folder_ids:
            folder_ids[relative_path] = _digest("fld", collection_id, relative_path)
        return folder_ids[relative_path]

    def ensure_folder(relative_path: str, depth: int) -> None:
        folder_id(relative_path)
        folder_meta.setdefault(relative_path, {"depth": depth, "file_count": 0, "child_folder_count": 0})

    def add_skipped(path: Path, reason: str) -> None:
        skipped_files.append(_skip(_relative_path(root, path), reason))

    def visit_dir(directory: Path, depth: int) -> None:
        relative = _relative_path(root, directory)
        ensure_folder(relative, depth)
        if max_depth is not None and depth >= max_depth:
            return
        try:
            entries = sorted(directory.iterdir(), key=lambda item: (not item.is_dir(), item.name.lower()))
        except PermissionError:
            add_skipped(directory, "permission_denied")
            return
        except OSError:
            add_skipped(directory, "extract_failed")
            return

        for entry in entries:
            rel = _relative_path(root, entry)
            if entry.is_symlink():
                skipped_files.append(_skip(rel, "symlink_skipped"))
                continue
            if _matches_exclude(rel, excludes):
                skipped_files.append(_skip(rel, "excluded_dir" if entry.is_dir() else "unsupported_extension"))
                continue
            if entry.is_dir():
                if entry.name in DEFAULT_EXCLUDED_DIRS:
                    skipped_files.append(_skip(rel, "excluded_dir"))
                    continue
                if _is_hidden(entry, root):
                    skipped_files.append(_skip(rel, "hidden_dir"))
                    continue
                folder_meta[relative]["child_folder_count"] += 1
                ensure_folder(rel, depth + 1)
                if recursive:
                    visit_dir(entry, depth + 1)
                continue

            if _is_hidden(entry, root):
                skipped_files.append(_skip(rel, "hidden_file"))
                continue
            if _is_secret_like(entry):
                skipped_files.append(_skip(rel, "secret_like_file"))
                continue
            try:
                stat = entry.stat()
            except PermissionError:
                skipped_files.append(_skip(rel, "permission_denied"))
                continue
            except OSError:
                skipped_files.append(_skip(rel, "extract_failed"))
                continue
            suffix = entry.suffix.lower()
            if suffix not in extensions:
                skipped_files.append(_skip(rel, "unsupported_extension"))
                continue
            if stat.st_size > max_file_size_bytes:
                skipped_files.append(_skip(rel, "max_file_size_exceeded"))
                continue
            if _is_binary_file(entry):
                skipped_files.append(_skip(rel, "binary_file"))
                continue

            folder_meta[relative]["file_count"] += 1
            files.append(
                {
                    "file_id": _digest("file", collection_id, rel),
                    "folder_id": folder_id(relative),
                    "relative_path": rel,
                    "extension": suffix,
                    "size_bytes": stat.st_size,
                    "extraction_status": "skipped",
                }
            )

    visit_dir(root, 0)

    folders = [
        {
            "folder_id": folder_id(relative),
            "parent_folder_id": folder_id(parent) if (parent := _parent_relative(relative)) else None,
            "relative_path": relative,
            "depth": meta["depth"],
            "file_count": meta["file_count"],
            "child_folder_count": meta["child_folder_count"],
        }
        for relative, meta in sorted(folder_meta.items(), key=lambda item: (item[1]["depth"], item[0]))
    ]
    for folder in folders:
        if folder["parent_folder_id"] is None:
            folder.pop("parent_folder_id")

    timestamp = _now()
    return {
        "collection": {
            "collection_id": collection_id,
            "workspace_id": workspace_id,
            "root_label": root_label,
            "folders": folders,
            "files": sorted(files, key=lambda item: item["relative_path"]),
            "skipped_files": sorted(skipped_files, key=lambda item: (item["relative_path"], item["skipped_reason"])),
        },
        "permission_grant": {
            "permission_grant_id": permission_grant_id,
            "workspace_id": workspace_id,
            "root_label": root_label,
            "scopes": ["scan"],
            "status": "active",
            "created_at": timestamp,
            "expires_at": None,
        },
    }
