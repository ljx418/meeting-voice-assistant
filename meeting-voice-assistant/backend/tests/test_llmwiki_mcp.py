import json

import pytest

from app.llmwiki.config import LLMWikiConfig

pytest.importorskip("mcp")

from app.llmwiki.mcp_stdio import _read_index


def test_mcp_index_exposes_layers_and_positioning(monkeypatch, tmp_path):
    workspace = tmp_path / "workspace"
    monkeypatch.setenv("LLMWIKI_WORKSPACE", str(workspace))

    config = LLMWikiConfig.from_env()
    config.ensure_directories()

    # Reuse module globals through environment-driven config.
    result = _read_index()
    payload = json.loads(result.text)

    assert payload["role"]["system"] == "LLMWiki"
    assert "GraphRAG" in payload["role"]["complements"]
    assert payload["layers"]["row"]
    assert payload["layers"]["llmwiki"]
    assert payload["layers"]["summary"]
    assert payload["paths"]["summary"].endswith("summary.md")
