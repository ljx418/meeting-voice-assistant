from pathlib import Path

from app.llmwiki.config import LLMWikiConfig
from app.llmwiki.engine import WikiEngine


def test_config_prefers_workspace_llmwiki_layout(monkeypatch, tmp_path):
    workspace = tmp_path / "workspace"
    monkeypatch.setenv("LLMWIKI_WORKSPACE", str(workspace))
    monkeypatch.delenv("LLMWIKI_DB_PATH", raising=False)
    monkeypatch.delenv("LLMWIKI_VAULT_PATH", raising=False)
    monkeypatch.delenv("LLMWIKI_MARKDOWN_OUTPUT_DIR", raising=False)

    config = LLMWikiConfig.from_env()

    assert config.vault_path == (workspace / "llmwiki" / "raw").resolve()
    assert config.db_path == (workspace / "llmwiki" / "state" / "llmwiki.db").resolve()
    assert config.markdown_output_dir == (workspace / "llmwiki" / "pages").resolve()
    assert config.normalized_output_dir == (workspace / "llmwiki" / "normalized").resolve()
    assert config.readable_docs_dir == (workspace / "llmwiki" / "readable").resolve()
    assert config.summary_path == (workspace / "summary.md").resolve()


def test_config_keeps_legacy_paths_when_present(monkeypatch, tmp_path):
    workspace = tmp_path / "workspace"
    (workspace / "llmwiki.db").parent.mkdir(parents=True, exist_ok=True)
    (workspace / "llmwiki.db").write_text("", encoding="utf-8")

    monkeypatch.setenv("LLMWIKI_WORKSPACE", str(workspace))
    monkeypatch.delenv("LLMWIKI_DB_PATH", raising=False)

    config = LLMWikiConfig.from_env()

    assert config.db_path == (workspace / "llmwiki.db").resolve()


def test_ingest_writes_normalized_and_summary(monkeypatch, tmp_path):
    workspace = tmp_path / "workspace"
    doc = tmp_path / "doc.md"
    doc.write_text("# OpenClaw\n\nOpenClaw setup notes.\n", encoding="utf-8")

    monkeypatch.setenv("LLMWIKI_WORKSPACE", str(workspace))
    monkeypatch.setenv("LLMWIKI_LLM_PROVIDER", "null")

    engine = WikiEngine(LLMWikiConfig.from_env())
    result = engine.ingest([str(doc)])

    source_id = result["sources"][0]
    normalized_path = engine.config.normalized_output_dir / f"{source_id}.json"

    assert normalized_path.exists()
    assert engine.config.summary_path.exists()
    summary = engine.config.summary_path.read_text(encoding="utf-8")
    assert "## Layers" in summary
    assert "## Current Status" in summary
    assert "llmwiki" in summary
