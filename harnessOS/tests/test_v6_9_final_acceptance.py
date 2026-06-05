from __future__ import annotations

import json
from pathlib import Path


FINAL_DIR = Path("docs/design/V6.x/evidence/v6-9-final-acceptance")
DATA_PATH = FINAL_DIR / "final-acceptance-data.json"


def test_v6_9_final_acceptance_data_passes() -> None:
    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))

    assert data["stage"] == "V6-9"
    assert data["status"] == "PASS"
    assert data["allowed_claim"] == "V6 complete: production pilot baseline ready for review."
    assert data["stage_count"] == 9
    assert data["blockers"] == []


def test_v6_9_all_stage_evidence_is_present_and_passed() -> None:
    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))

    assert [stage["stage"] for stage in data["stages"]] == [f"V6-{index}" for index in range(9)]
    for stage in data["stages"]:
        assert stage["status"] == "PASS"
        assert stage["evidence_scope"]
        assert stage["allowed_claim"]
        assert stage["missing_evidence"] == []
        assert stage["claim_violations"] == []
        assert stage["redaction_status"] == "PASS"
        assert stage["evidence_refs"]["acceptance_data"]
        assert stage["evidence_refs"]["result_summary"]


def test_v6_9_no_false_green_and_redaction_pass() -> None:
    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))

    assert data["claim_scan"]["status"] == "PASS"
    assert data["claim_scan"]["violations"] == []
    assert data["redaction_scan"]["status"] == "PASS"
    assert data["redaction_scan"]["violations"] == []
    assert data["drawio_validation"]["status"] == "PASS"


def test_v6_9_runtime_truth_and_forbidden_capability_flags() -> None:
    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))

    assert data["runtime_truth_boundary"]["status"] == "PASS"
    assert all(data["runtime_truth_boundary"]["assertions"].values())
    assert data["production_ready"] is False
    assert data["full_production_ga"] is False
    assert data["complete_workflow_studio_ready"] is False
    assert data["agent_executor_ready"] is False
    assert data["production_controlled_executor_ready"] is False
    assert data["production_ready_external_app_support"] is False
    assert data["full_multi_agent_orchestration_ready"] is False
    assert data["distributed_multi_agent_runtime_ready"] is False
    assert data["autonomous_workflow_editing_ready"] is False


def test_v6_9_high_risk_decisions_are_recorded() -> None:
    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))

    decisions = {item["stage"]: item for item in data["high_risk_decisions"]["decisions"]}
    assert data["high_risk_decisions"]["status"] == "PASS"
    for stage in ("V6-4", "V6-5", "V6-7"):
        assert decisions[stage]["recorded"] is True
        assert decisions[stage]["decision_ref"]
