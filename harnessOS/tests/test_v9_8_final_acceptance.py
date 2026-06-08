from __future__ import annotations

import json
import subprocess
from pathlib import Path

from tools.v9.generate_v9_8_final_acceptance import build_final_acceptance


OUT_DIR = Path("docs/design/V9.x/evidence/v9-8-final-acceptance")


def test_v9_8_allows_final_claim_when_storyboard_provider_evidence_passes() -> None:
    data = build_final_acceptance()

    assert data["status"] == "PASS"
    assert data["final_claim"] == "V9 complete: high-risk Agent execution and workflow productization baseline ready for review."
    assert data["blockers"] == []
    assert data["production_ready"] is False
    assert data["agent_executor_ready"] is False
    assert data["complete_workflow_studio_ready"] is False
    scenarios = {item["scenario_id"]: item for item in data["user_scenarios"]}
    assert scenarios["US-V9-08"]["evidence_scope"] == "real_provider_backed_runtime_fixture"
    assert scenarios["US-V9-08"]["storyboard_image_count"] == 4


def test_v9_8_generates_pass_dashboard_without_forbidden_capability_claims() -> None:
    result = subprocess.run(["./.venv/bin/python", "-m", "tools.v9.generate_v9_8_final_acceptance"], check=False, text=True, capture_output=True)

    assert result.returncode == 0
    assert (OUT_DIR / "v9-final-acceptance-dashboard.html").exists()
    assert (OUT_DIR / "v9-final-acceptance-data.json").exists()
    data = json.loads((OUT_DIR / "v9-final-acceptance-data.json").read_text(encoding="utf-8"))
    assert data["status"] == "PASS"
    assert data["final_claim"]
    assert data["planning_docs_counted_as_runtime_evidence"] is False
    assert data["agent_executor_ready"] is False
    assert data["full_multi_agent_orchestration_ready"] is False


def test_v9_8_global_gates_pass_with_provider_backed_storyboard_evidence() -> None:
    data = build_final_acceptance()

    assert data["claim_scan"] == "PASS"
    assert data["redaction_scan"] == "PASS"
    assert data["drawio_xml"] == "PASS"
    assert all(item["status"] == "PASS" for item in data["stage_results"])
