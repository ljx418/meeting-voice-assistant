"""Repo snapshot artifacts for V2 codebase assets."""

from __future__ import annotations

import fnmatch
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

from data_service.mcp_common import now, read_json, write_json

from .artifacts import (
    read_jsonl,
    snapshot_dir,
    snapshot_files_path,
    snapshot_json_path,
    snapshot_stats_path,
    snapshot_warnings_path,
    snapshots_dir,
    write_jsonl,
)
from .models import DEFAULT_SCAN_POLICY
from .registry import CodebaseRegistry


SNAPSHOT_SCHEMA_VERSION = "v2.0"
SELF_ARTIFACT_EXCLUDES = (
    "workspace/assets/codebase/**",
    "workspace/*/assets/codebase/**",
    "assets/codebase/**",
    ".data_service/**",
)
DEFAULT_INCLUDE_EXTENSIONS = {
    ".py",
    ".md",
    ".txt",
    ".toml",
    ".json",
    ".yaml",
    ".yml",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".vue",
    ".html",
    ".drawio",
    ".mmd",
    ".css",
    ".scss",
    ".sh",
    ".sql",
    ".rs",
    ".go",
    ".java",
    ".kt",
    ".swift",
    ".c",
    ".h",
    ".cpp",
    ".hpp",
}
LANGUAGE_BY_EXTENSION = {
    ".py": "python",
    ".md": "markdown",
    ".txt": "text",
    ".toml": "toml",
    ".json": "json",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".js": "javascript",
    ".jsx": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".vue": "vue",
    ".html": "html",
    ".drawio": "drawio",
    ".mmd": "mermaid",
    ".css": "css",
    ".scss": "scss",
    ".sh": "shell",
    ".sql": "sql",
    ".rs": "rust",
    ".go": "go",
    ".java": "java",
    ".kt": "kotlin",
    ".swift": "swift",
    ".c": "c",
    ".h": "c",
    ".cpp": "cpp",
    ".hpp": "cpp",
}
SENSITIVE_NAMES = {".env", "id_rsa", "id_dsa", "id_ecdsa", "id_ed25519"}
SENSITIVE_SUFFIXES = (".pem", ".key", ".p12", ".pfx")
SENSITIVE_HINTS = ("secret", "credential", "private_key")
SENSITIVE_TOKEN_NAMES = {".token", "token", "token.txt", "token.json", "token.yaml", "token.yml"}


class CodebaseSnapshotService:
    def __init__(self, workspace: Path, *, workspace_id: str) -> None:
        self.workspace = workspace
        self.workspace_id = workspace_id
        self.registry = CodebaseRegistry(workspace, workspace_id=workspace_id)

    def create_snapshot(
        self,
        codebase_id: str,
        *,
        scan_policy: dict[str, Any] | None = None,
        include_git: bool = True,
    ) -> dict[str, Any]:
        asset = self.registry.describe(codebase_id)
        if asset.status != "active":
            raise ValueError("CODEBASE_NOT_ACTIVE")
        merged_policy = merge_scan_policy(asset.scan_policy, scan_policy or {})
        root = Path(asset.root_path).expanduser().resolve()
        records, warnings = scan_repo(root, merged_policy)
        stats = build_stats(records)
        important_paths = detect_important_paths(records)
        content_fingerprint = fingerprint_records(records, merged_policy)
        git = git_metadata(root) if include_git else {"vcs": "disabled", "dirty": None}
        dirty_fingerprint = hashlib.sha256(
            json.dumps({"content": content_fingerprint, "dirty": git.get("dirty"), "status": git.get("status_hash")}, sort_keys=True).encode("utf-8")
        ).hexdigest()
        scan_policy_hash = hashlib.sha256(json.dumps(merged_policy, sort_keys=True).encode("utf-8")).hexdigest()
        snapshot_identity = {
            "codebase_id": codebase_id,
            "content_fingerprint": content_fingerprint,
            "scan_policy_hash": scan_policy_hash,
            "git_commit": git.get("commit_sha"),
        }
        snapshot_id = "snap_" + hashlib.sha256(
            json.dumps(snapshot_identity, sort_keys=True).encode("utf-8")
        ).hexdigest()[:20]

        created_at = now()
        refs = snapshot_artifact_refs(codebase_id, snapshot_id)
        snapshot = {
            "schema_version": SNAPSHOT_SCHEMA_VERSION,
            "workspace_id": self.workspace_id,
            "codebase_id": codebase_id,
            "snapshot_id": snapshot_id,
            "created_at": created_at,
            "scan_policy_hash": scan_policy_hash,
            "content_fingerprint": content_fingerprint,
            "dirty_fingerprint": dirty_fingerprint,
            "snapshot_identity": snapshot_identity,
            "git": public_git(git),
            "stats": stats,
            "important_paths": important_paths,
            "warning_count": len(warnings),
            "artifact_refs": refs,
        }
        target = snapshot_dir(self.workspace, codebase_id, snapshot_id)
        target.mkdir(parents=True, exist_ok=True)
        write_json(snapshot_json_path(self.workspace, codebase_id, snapshot_id), snapshot)
        write_json(snapshot_stats_path(self.workspace, codebase_id, snapshot_id), stats)
        write_jsonl(snapshot_files_path(self.workspace, codebase_id, snapshot_id), records)
        write_jsonl(snapshot_warnings_path(self.workspace, codebase_id, snapshot_id), warnings)
        return {"snapshot": snapshot, "files": records, "warnings": warnings, "stats": stats}

    def read_snapshot(self, codebase_id: str, snapshot_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        payload = read_json(snapshot_json_path(self.workspace, codebase_id, snapshot_id), None)
        if not payload:
            raise FileNotFoundError(snapshot_id)
        return payload

    def list_snapshots(self, codebase_id: str, *, limit: int = 100) -> list[dict[str, Any]]:
        self.registry.describe(codebase_id)
        base = snapshots_dir(self.workspace, codebase_id)
        if not base.exists():
            return []
        items = []
        for item in sorted(base.iterdir()):
            if not item.is_dir():
                continue
            payload = read_json(item / "snapshot.json", None)
            if payload:
                items.append(public_snapshot(payload))
        return sorted(items, key=lambda item: (str(item.get("created_at") or ""), str(item.get("snapshot_id") or "")), reverse=True)[:limit]

    def read_files(self, codebase_id: str, snapshot_id: str) -> list[dict[str, Any]]:
        return read_jsonl(snapshot_files_path(self.workspace, codebase_id, snapshot_id))

    def read_warnings(self, codebase_id: str, snapshot_id: str) -> list[dict[str, Any]]:
        return read_jsonl(snapshot_warnings_path(self.workspace, codebase_id, snapshot_id))


def merge_scan_policy(base: dict[str, Any] | None, override: dict[str, Any]) -> dict[str, Any]:
    policy = dict(DEFAULT_SCAN_POLICY)
    policy.update(base or {})
    if override:
        policy.update(override)
    validate_scan_policy(policy)
    exclude = list(dict.fromkeys([*policy.get("exclude", []), *SELF_ARTIFACT_EXCLUDES]))
    policy["exclude"] = exclude
    policy["max_file_size_mb"] = float(policy.get("max_file_size_mb") or DEFAULT_SCAN_POLICY["max_file_size_mb"])
    policy["include"] = list(policy.get("include") or [])
    policy["binary_policy"] = policy.get("binary_policy") or "skip"
    return policy


def validate_scan_policy(policy: dict[str, Any]) -> None:
    for field in ("include", "exclude"):
        value = policy.get(field, [])
        if value is None:
            continue
        if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
            raise ValueError("INVALID_SCAN_POLICY")
    try:
        max_size = float(policy.get("max_file_size_mb") or DEFAULT_SCAN_POLICY["max_file_size_mb"])
    except (TypeError, ValueError) as exc:
        raise ValueError("INVALID_SCAN_POLICY") from exc
    if max_size <= 0:
        raise ValueError("INVALID_SCAN_POLICY")
    if policy.get("binary_policy", "skip") != "skip":
        raise ValueError("INVALID_SCAN_POLICY")


def scan_repo(root: Path, scan_policy: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    records: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    max_bytes = int(float(scan_policy.get("max_file_size_mb", 2)) * 1024 * 1024)
    git_ignored = ignored_by_git(root) if scan_policy.get("respect_gitignore", True) else set()
    for path in sorted(root.rglob("*")):
        relative = _relative_path(root, path)
        if not relative or should_exclude(relative, scan_policy) or is_git_ignored(relative, git_ignored):
            continue
        if path.is_dir():
            continue
        if path.is_symlink():
            records.append(skip_record(relative, "symlink", "SYMLINK_SKIPPED"))
            warnings.append(warning("SYMLINK_SKIPPED", relative, "Symlink file skipped"))
            continue
        if is_sensitive(relative):
            records.append(skip_record(relative, "file", "SENSITIVE_SKIPPED"))
            warnings.append(warning("SENSITIVE_SKIPPED", relative, "Sensitive-looking file skipped"))
            continue
        if not should_include(relative, scan_policy):
            continue
        try:
            stat = path.stat()
        except OSError:
            records.append(skip_record(relative, "file", "UNREADABLE"))
            warnings.append(warning("UNREADABLE", relative, "File could not be statted"))
            continue
        if stat.st_size > max_bytes:
            records.append(skip_record(relative, "file", "FILE_TOO_LARGE", size_bytes=stat.st_size))
            warnings.append(warning("FILE_TOO_LARGE", relative, "File exceeds max_file_size_mb"))
            continue
        try:
            raw = path.read_bytes()
        except OSError:
            records.append(skip_record(relative, "file", "UNREADABLE", size_bytes=stat.st_size))
            warnings.append(warning("UNREADABLE", relative, "File could not be read"))
            continue
        if is_binary(raw):
            records.append(skip_record(relative, "file", "BINARY_SKIPPED", size_bytes=stat.st_size))
            warnings.append(warning("BINARY_SKIPPED", relative, "Binary file skipped"))
            continue
        digest = hashlib.sha256(raw).hexdigest()
        text = raw.decode("utf-8", errors="replace")
        records.append(
            {
                "schema_version": SNAPSHOT_SCHEMA_VERSION,
                "path": relative,
                "kind": "file",
                "language": language_for(relative),
                "size_bytes": stat.st_size,
                "loc": count_loc(text),
                "sha256": digest,
                "included": True,
                "skip_reason": None,
            }
        )
    return records, warnings


def should_include(relative: str, scan_policy: dict[str, Any]) -> bool:
    include = scan_policy.get("include") or []
    if include:
        return any(fnmatch.fnmatch(relative, pattern) or (pattern.startswith("**/") and fnmatch.fnmatch(relative, pattern[3:])) for pattern in include)
    return Path(relative).suffix.lower() in DEFAULT_INCLUDE_EXTENSIONS or Path(relative).name in {"Dockerfile", "Makefile"}


def should_exclude(relative: str, scan_policy: dict[str, Any]) -> bool:
    patterns = scan_policy.get("exclude") or []
    return any(fnmatch.fnmatch(relative, pattern) or fnmatch.fnmatch(relative + "/", pattern) for pattern in patterns)


def ignored_by_git(root: Path) -> set[str]:
    try:
        result = subprocess.run(
            ["git", "-C", str(root), "ls-files", "--others", "--ignored", "--exclude-standard", "-z"],
            check=False,
            capture_output=True,
            timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired):
        return set()
    if result.returncode != 0:
        return set()
    return {item.decode("utf-8", errors="replace").rstrip("/") for item in result.stdout.split(b"\x00") if item}


def is_git_ignored(relative: str, ignored: set[str]) -> bool:
    if relative in ignored:
        return True
    return any(relative.startswith(prefix + "/") for prefix in ignored)


def is_sensitive(relative: str) -> bool:
    name = Path(relative).name.lower()
    if name in SENSITIVE_NAMES or name.startswith(".env."):
        return True
    if name.endswith(SENSITIVE_SUFFIXES):
        return True
    if name in SENSITIVE_TOKEN_NAMES or name.endswith(".token"):
        return True
    lowered = relative.lower()
    return any(hint in lowered for hint in SENSITIVE_HINTS)


def is_binary(raw: bytes) -> bool:
    sample = raw[:8192]
    if b"\x00" in sample:
        return True
    try:
        sample.decode("utf-8")
    except UnicodeDecodeError:
        return True
    return False


def skip_record(relative: str, kind: str, reason: str, *, size_bytes: int | None = None) -> dict[str, Any]:
    return {
        "schema_version": SNAPSHOT_SCHEMA_VERSION,
        "path": relative,
        "kind": kind,
        "language": language_for(relative),
        "size_bytes": size_bytes,
        "loc": 0,
        "sha256": None,
        "included": False,
        "skip_reason": reason,
    }


def warning(code: str, relative: str, message: str) -> dict[str, Any]:
    return {
        "schema_version": SNAPSHOT_SCHEMA_VERSION,
        "code": code,
        "path": relative,
        "message": message,
        "severity": "warning",
    }


def build_stats(records: list[dict[str, Any]]) -> dict[str, Any]:
    languages: dict[str, dict[str, int]] = {}
    included = [record for record in records if record.get("included")]
    for record in included:
        lang = str(record.get("language") or "unknown")
        bucket = languages.setdefault(lang, {"files": 0, "loc": 0, "bytes": 0})
        bucket["files"] += 1
        bucket["loc"] += int(record.get("loc") or 0)
        bucket["bytes"] += int(record.get("size_bytes") or 0)
    return {
        "schema_version": SNAPSHOT_SCHEMA_VERSION,
        "file_count": len(included),
        "tracked_record_count": len(records),
        "skipped_count": len(records) - len(included),
        "loc_total": sum(int(record.get("loc") or 0) for record in included),
        "languages": dict(sorted(languages.items())),
    }


def detect_important_paths(records: list[dict[str, Any]]) -> dict[str, list[str]]:
    paths = [record["path"] for record in records if record.get("included")]
    return {
        "readme": sorted(path for path in paths if Path(path).name.lower().startswith("readme")),
        "docs": sorted(path for path in paths if path.startswith("docs/")),
        "entrypoints": sorted(
            path
            for path in paths
            if path.endswith("/main.py")
            or path.endswith("__main__.py")
            or path.endswith("mcp_stdio.py")
            or Path(path).name in {"package.json", "vite.config.ts"}
        ),
        "tests": sorted(path for path in paths if "/tests/" in f"/{path}" or path.startswith("tests/")),
        "frontend": sorted(path for path in paths if path.startswith("frontend/")),
        "configs": sorted(path for path in paths if Path(path).name in {"pyproject.toml", "package.json", "vite.config.ts", "tsconfig.json", "pytest.ini"} or path.endswith((".yaml", ".yml", ".toml"))),
    }


def fingerprint_records(records: list[dict[str, Any]], scan_policy: dict[str, Any]) -> str:
    stable_records = [
        {
            "path": record.get("path"),
            "included": record.get("included"),
            "sha256": record.get("sha256"),
            "skip_reason": record.get("skip_reason"),
            "size_bytes": record.get("size_bytes"),
        }
        for record in records
    ]
    return hashlib.sha256(json.dumps({"records": stable_records, "exclude": scan_policy.get("exclude")}, sort_keys=True).encode("utf-8")).hexdigest()


def git_metadata(root: Path) -> dict[str, Any]:
    if not _git_ok(root, "rev-parse", "--is-inside-work-tree"):
        return {"vcs": "none", "dirty": None, "branch": None, "commit_sha": None, "status_hash": None}
    branch = _git_text(root, "rev-parse", "--abbrev-ref", "HEAD")
    commit = _git_text(root, "rev-parse", "HEAD")
    status = _git_text(root, "status", "--porcelain") or ""
    return {
        "vcs": "git",
        "branch": branch,
        "commit_sha": commit,
        "dirty": bool(status.strip()),
        "status_hash": hashlib.sha256(status.encode("utf-8")).hexdigest(),
    }


def public_git(git: dict[str, Any]) -> dict[str, Any]:
    return {key: git.get(key) for key in ["vcs", "branch", "commit_sha", "dirty"]}


def _git_ok(root: Path, *args: str) -> bool:
    try:
        result = subprocess.run(["git", "-C", str(root), *args], check=False, capture_output=True, text=True, timeout=5)
    except (OSError, subprocess.TimeoutExpired):
        return False
    return result.returncode == 0


def _git_text(root: Path, *args: str) -> str | None:
    try:
        result = subprocess.run(["git", "-C", str(root), *args], check=False, capture_output=True, text=True, timeout=5)
    except (OSError, subprocess.TimeoutExpired):
        return None
    if result.returncode != 0:
        return None
    return result.stdout.strip()


def language_for(relative: str) -> str:
    name = Path(relative).name
    if name == "Dockerfile":
        return "dockerfile"
    if name == "Makefile":
        return "makefile"
    return LANGUAGE_BY_EXTENSION.get(Path(relative).suffix.lower(), "unknown")


def count_loc(text: str) -> int:
    if not text:
        return 0
    return len(text.splitlines())


def snapshot_artifact_refs(codebase_id: str, snapshot_id: str) -> list[dict[str, str]]:
    return [
        {"type": "snapshot", "artifact_ref": f"snapshot://{codebase_id}/{snapshot_id}"},
        {"type": "snapshot_files", "artifact_ref": f"snapshot-files://{codebase_id}/{snapshot_id}"},
        {"type": "snapshot_stats", "artifact_ref": f"snapshot-stats://{codebase_id}/{snapshot_id}"},
        {"type": "snapshot_warnings", "artifact_ref": f"snapshot-warnings://{codebase_id}/{snapshot_id}"},
    ]


def public_snapshot(snapshot: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": snapshot.get("schema_version"),
        "workspace_id": snapshot.get("workspace_id"),
        "codebase_id": snapshot.get("codebase_id"),
        "snapshot_id": snapshot.get("snapshot_id"),
        "created_at": snapshot.get("created_at"),
        "git": snapshot.get("git"),
        "stats": snapshot.get("stats"),
        "important_paths": snapshot.get("important_paths"),
        "warning_count": snapshot.get("warning_count", 0),
        "artifact_refs": snapshot.get("artifact_refs", []),
    }


def _relative_path(root: Path, path: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return ""
