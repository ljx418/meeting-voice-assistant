"""V4.x unified experience acceptance tests."""

from __future__ import annotations

from pathlib import Path


ACCEPTANCE = Path("docs/design/V4.x/v4_x_unified_experience_acceptance.md")
SUMMARY = Path("docs/design/V4.x/evidence/unified-experience/result-summary.md")


def test_acceptance_matrix_covers_ux_paths() -> None:
    text = ACCEPTANCE.read_text(encoding="utf-8")

    for index in range(1, 13):
        assert f"UX-{index:02d}" in text
    for assertion in [
        "source=agent cannot execute mutation",
        "durable mutation requires user_confirmed=true",
        "WorkflowSpec cannot mutate runtime truth",
        "Drawio is visualization only",
        "HTML Report is read-only",
        "Browser does not call /v1/rpc",
        "Browser does not call /v1/events/subscribe",
    ]:
        assert assertion in text


def test_unified_result_summary_does_not_false_pass_pending_evidence() -> None:
    text = SUMMARY.read_text(encoding="utf-8")

    assert "status: PASS" in text
    assert "stage: V4-U7 Real Multi-Agent Runtime Evidence" in text
    assert "pass_count: 12" in text
    assert "partial_count: 0" in text
    assert "blocked_count: 0" in text
    assert "UX-12" in text
    assert "UX-08 / UX-09 / UX-10" in text
    assert "provider-backed" in text
