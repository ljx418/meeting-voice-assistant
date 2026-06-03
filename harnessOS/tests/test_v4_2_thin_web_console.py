"""V4.2-A Thin Web Console observation boundary tests."""

from __future__ import annotations

from pathlib import Path


EVIDENCE_DIR = Path("docs/design/V4.2/evidence/headless-interaction")


def test_thin_web_console_is_observation_only() -> None:
    text = (EVIDENCE_DIR / "thin_web_console.html").read_text(encoding="utf-8")

    assert "仅作为观察入口" in text
    assert "不提供完整拖拽编辑" in text
    assert "不提供通用运行或重跑" in text
    assert "workflow.drawio" in text
    assert "workflow_board.html" in text
    assert "artifacts.html" in text
    assert "quality.html" in text
    assert "evidence.html" in text


def test_thin_web_console_has_no_direct_runtime_routes() -> None:
    text = (EVIDENCE_DIR / "thin_web_console.html").read_text(encoding="utf-8")

    assert "/v1/rpc" not in text
    assert "/v1/events/subscribe" not in text
    assert "/bff/v4_1/folder-summary/proposals" not in text
    assert "/start-local-workflow" not in text
    assert "/rerun-node" not in text
