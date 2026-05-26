"""V4.0-Z final audit / release gate tests."""

from __future__ import annotations

import json
from pathlib import Path

from tests.v4_0_guard_utils import (
    SAFE_FORBIDDEN_CLAIM_CONTEXT_MARKERS,
    assert_phrases_only_in_safe_context,
    v4_0_doc_and_frontend_files,
)


CONTRACT_PATH = Path("docs/design/V4.0/v4_0_z_final_audit_release_gate_contract.json")
REQUIRED_STAGE_MARKERS = ["V4.0-O", "V4.0-P", "V4.0-Q", "V4.0-R", "V4.0-S", "V4.0-T", "V4.0-U", "V4.0-V", "V4.0-W", "V4.0-X", "V4.0-Y", "V4.0-Z"]
FORBIDDEN_CLAIMS = {
    "production-ready external app support",
    "enterprise auth ready",
    "multi-tenant control plane ready",
    "OAuth ready",
    "SSO ready",
    "controlled executor ready",
    "Agent executor ready",
    "autonomous workflow editing ready",
    "complete Workflow Studio ready",
    "complete AgentTalkWindow ready",
    "full low-code canvas editing ready",
}
def _contract() -> dict:
    return json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))


def test_z_final_audit_contract_contains_allowed_claims_and_stage_claims() -> None:
    contract = _contract()
    assert contract["stage"] == "V4.0-Z"
    assert contract["allowed_stage_claim"] == "V4.0-Z complete: V4.0 final audit package ready for review."
    assert contract["allowed_final_claim"] == "V4.0 complete: governed dev/local Workflow Console and production readiness design gates ready for implementation review."
    claims = "\n".join(contract["completed_stage_claims"])
    for marker in REQUIRED_STAGE_MARKERS:
        assert marker in claims


def test_z_final_result_is_review_ready_but_not_false_ready() -> None:
    result = _contract()["final_result"]
    assert result["governed_dev_local_workflow_console_ready"] is True
    assert result["production_readiness_design_gates_ready_for_review"] is True
    assert result["production_ready"] is False
    assert result["enterprise_auth_ready"] is False
    assert result["multi_tenant_control_plane_ready"] is False
    assert result["controlled_executor_ready"] is False
    assert result["agent_executor_ready"] is False
    assert result["complete_workflow_studio_ready"] is False
    assert result["complete_agenttalkwindow_ready"] is False


def test_z_core_docs_reference_final_allowed_claim_and_no_false_green() -> None:
    for path in [
        Path("docs/design/V4.0/00_README.md"),
        Path("docs/design/V4.0/v4_0_current_gap_analysis.md"),
        Path("docs/design/V4.0/v4_0_completion_audit_report.md"),
    ]:
        text = path.read_text(encoding="utf-8")
        assert "V4.0 complete: governed dev/local Workflow Console and production readiness design gates ready for implementation review." in text
        assert "No False Green" in text or "不能声明" in text


def test_z_gap_analysis_has_no_stale_planned_rows_after_final_gate() -> None:
    gap = Path("docs/design/V4.0/v4_0_current_gap_analysis.md").read_text(encoding="utf-8")
    roadmap = gap.split("### 6.3", 1)[0]
    assert "| V4.0-Z | Final Audit / Release Gate |" in roadmap
    assert "计划中：" not in roadmap
    for marker in REQUIRED_STAGE_MARKERS:
        assert roadmap.count(f"| {marker} |") == 1


def test_z_claim_guard_allows_forbidden_claims_only_in_safe_context() -> None:
    assert_phrases_only_in_safe_context(
        files=v4_0_doc_and_frontend_files(),
        phrases=FORBIDDEN_CLAIMS,
        safe_markers=SAFE_FORBIDDEN_CLAIM_CONTEXT_MARKERS,
    )
