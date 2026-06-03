"""V4.2-A HTML report generator tests."""

from __future__ import annotations

from pathlib import Path

from scripts.v4_2_headless_evidence import FORBIDDEN_TERMS


EVIDENCE_DIR = Path("docs/design/V4.2/evidence/headless-interaction")
HTML_REPORTS = [
    "workflow_board.html",
    "artifacts.html",
    "quality.html",
    "evidence.html",
    "thin_web_console.html",
]


def test_html_reports_are_read_only() -> None:
    for filename in HTML_REPORTS:
        text = (EVIDENCE_DIR / filename).read_text(encoding="utf-8")
        lowered = text.lower()
        assert "<form" not in lowered
        assert "<button" not in lowered
        assert "method=\"post\"" not in lowered
        assert "fetch(" not in lowered
        assert "只读" in text


def test_html_reports_have_data_source_markers() -> None:
    expected = {
        "workflow_board.html": "Data source: spec / draft-version / runtime",
        "artifacts.html": "Data source: artifact / runtime",
        "quality.html": "Data source: quality / runtime",
        "evidence.html": "Data source: evidence / governance review",
        "thin_web_console.html": "Data source: spec / runtime / artifact / quality / evidence",
    }

    for filename, marker in expected.items():
        assert marker in (EVIDENCE_DIR / filename).read_text(encoding="utf-8")


def test_html_reports_do_not_leak_tokens_or_raw_payloads() -> None:
    for filename in HTML_REPORTS:
        text = (EVIDENCE_DIR / filename).read_text(encoding="utf-8")
        for term in FORBIDDEN_TERMS:
            assert term not in text
