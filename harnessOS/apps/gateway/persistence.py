"""Small persistence helpers for local gateway stores."""

from __future__ import annotations

import contextlib
import fcntl
import json
import os
from pathlib import Path
from typing import Any, Callable, Iterator, TypeVar


T = TypeVar("T")


@contextlib.contextmanager
def file_lock(path: Path) -> Iterator[None]:
    """Acquire an exclusive advisory lock for one persistence path."""
    lock_path = path.with_suffix(path.suffix + ".lock")
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    with lock_path.open("a+", encoding="utf-8") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def atomic_write_text(path: Path, text: str) -> None:
    """Atomically replace a text file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_name(f".{path.name}.tmp.{os.getpid()}")
    temp_path.write_text(text, encoding="utf-8")
    os.replace(temp_path, path)


def append_text_locked(path: Path, text: str) -> None:
    """Append text while holding the path lock."""
    with file_lock(path):
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as handle:
            handle.write(text)


def read_json_locked(path: Path, default: T, error_factory: Callable[[str], Exception]) -> T:
    """Read JSON while holding the path lock."""
    with file_lock(path):
        if not path.exists():
            return default
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise error_factory(f"JSON file is invalid: {path}") from exc


def update_json_list_locked(
    path: Path,
    updater: Callable[[list[dict[str, Any]]], T],
    error_factory: Callable[[str], Exception],
) -> T:
    """Read, mutate, and persist a JSON list under one lock."""
    with file_lock(path):
        records: list[dict[str, Any]]
        if path.exists():
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                raise error_factory(f"JSON index is invalid: {path}") from exc
            if not isinstance(payload, list):
                raise error_factory(f"JSON index must be a list: {path}")
            records = [record for record in payload if isinstance(record, dict)]
        else:
            records = []

        result = updater(records)
        atomic_write_text(
            path,
            json.dumps(records, ensure_ascii=False, indent=2) + "\n",
        )
        return result
