from __future__ import annotations

import pytest

from core.config import get_app_config
from packs.knowledge.workflow import _validate_source_path


def test_knowledge_source_path_must_stay_inside_allowed_roots(tmp_path, monkeypatch):
    allowed = tmp_path / "allowed"
    outside = tmp_path / "outside"
    allowed.mkdir()
    outside.mkdir()
    allowed_file = allowed / "source.md"
    outside_file = outside / "source.md"
    allowed_file.write_text("allowed", encoding="utf-8")
    outside_file.write_text("outside", encoding="utf-8")
    monkeypatch.setenv("HARNESS_DATA_SERVICE_MCP_ALLOWED_SOURCE_ROOTS", str(allowed))
    get_app_config.cache_clear()

    _validate_source_path(allowed_file)
    with pytest.raises(ValueError, match="outside allowed roots"):
        _validate_source_path(outside_file)


def test_knowledge_source_path_blocks_symlink_and_large_file(tmp_path, monkeypatch):
    allowed = tmp_path / "allowed"
    allowed.mkdir()
    target = allowed / "target.md"
    target.write_text("target", encoding="utf-8")
    symlink = allowed / "source-link.md"
    symlink.symlink_to(target)
    monkeypatch.setenv("HARNESS_DATA_SERVICE_MCP_ALLOWED_SOURCE_ROOTS", str(allowed))
    get_app_config.cache_clear()

    with pytest.raises(ValueError, match="symlink"):
        _validate_source_path(symlink)

    large = allowed / "large.md"
    large.write_text("12345", encoding="utf-8")
    monkeypatch.setenv("HARNESS_KNOWLEDGE_SOURCE_MAX_BYTES", "4")
    with pytest.raises(ValueError, match="size limit"):
        _validate_source_path(large)
