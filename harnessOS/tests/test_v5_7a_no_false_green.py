from __future__ import annotations

from pathlib import Path


def test_v5_7a_docs_keep_design_gate_boundary() -> None:
    plan = Path("docs/design/V5.x/v5_7a_production_controlled_executor_design_gate_plan.md").read_text(encoding="utf-8")
    assert "design gate only" in plan
    assert "no production executor route" in plan
    assert "no production runtime worker" in plan
    assert "not executable runtime code" in plan


def test_v5_7b_remains_blocked() -> None:
    plan = Path("docs/design/V5.x/v5_7b_production_controlled_executor_runtime_plan.md").read_text(encoding="utf-8")
    assert "默认 blocked" in plan
    assert "human high-risk proceed decision is recorded" in plan
    assert "V5-6 product console / manual confirmation UX external review accepted" in plan
    assert "source=agent direct durable mutation" in plan


def test_v5_7a_evidence_summary_does_not_claim_runtime_ready() -> None:
    path = Path("docs/design/V5.x/evidence/v5-7a-production-controlled-executor-design-gate/result-summary.md")
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    assert "V5-7A complete: production controlled executor design gate ready for review." in text
    assert "production controlled executor ready" not in text.split("No False Green:")[0]
    assert "Runtime Execution Enabled: False" in text
