from __future__ import annotations

from pathlib import Path


V5_6_DOCS = [
    Path("docs/design/V5.x/v5_6_web_studio_productization_prd.md"),
    Path("docs/design/V5.x/v5_6_thin_web_console_productization_plan.md"),
    Path("docs/design/V5.x/v5_6_no_false_green_guard.md"),
]


def test_v5_6_docs_do_not_claim_complete_web_studio() -> None:
    for path in V5_6_DOCS:
        text = path.read_text(encoding="utf-8")
        assert "complete Workflow Studio ready" not in text or "No False Green" in text or "不证明" in text
        assert "Agent executor ready" not in text or "No False Green" in text or "不证明" in text


def test_v5_6_evidence_summary_does_not_claim_production_executor() -> None:
    path = Path("docs/design/V5.x/evidence/v5-6-thin-web-console/result-summary.md")
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    assert "V5-6 complete: Thin Web Console productization slice ready for review." in text
    assert "production controlled executor ready" not in text
    assert "complete Workflow Studio ready" not in text

