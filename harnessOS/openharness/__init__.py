"""Compatibility bridge for the bundled OpenHarness package."""

from __future__ import annotations

from pathlib import Path

_project_root = Path(__file__).resolve().parents[1]
_openharness_src = _project_root / "examples" / "open-harness" / "src" / "openharness"

if _openharness_src.is_dir():
    src_path = str(_openharness_src)
    if src_path not in __path__:
        __path__.append(src_path)

__all__ = []
