from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


V9_ROOT = Path("docs/design/V9.x")
EVIDENCE_ROOT = V9_ROOT / "evidence" / "v9-1-safety-gate-implementation"


def test_v9_1_safety_gate_evidence_package_is_runtime_blocked() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "tools.v9.generate_safety_gate_evidence"],
        check=False,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    data = json.loads((EVIDENCE_ROOT / "acceptance-data.json").read_text(encoding="utf-8"))
    html = (EVIDENCE_ROOT / "index.html").read_text(encoding="utf-8")

    assert data["status"] == "PASS"
    assert data["evidence_scope"] == "real_code_policy_validation"
    assert data["runtime_backed"] is False
    assert data["runtime_execution_allowed"] is False
    assert data["runtime_executor_route_created"] is False
    assert data["runtime_worker_created"] is False
    assert data["controlled_executor_action_execution"] is False
    assert data["source_agent_durable_mutation_allowed"] is False
    assert data["agent_executor_ready"] is False
    assert all(scenario["status"] == "PASS" for scenario in data["scenarios"])
    assert "runtime_execution_allowed: false" in html
    assert data["blocked_capability_claim_flags"]["agent_executor_ready"] is False
    assert data["blocked_capability_claim_flags"]["complete_workflow_studio_ready"] is False


def test_v9_1_safety_gate_evidence_includes_required_negative_scenarios() -> None:
    subprocess.run([sys.executable, "-m", "tools.v9.generate_safety_gate_evidence"], check=True, text=True, capture_output=True)
    data = json.loads((EVIDENCE_ROOT / "acceptance-data.json").read_text(encoding="utf-8"))
    scenarios = {scenario["scenario_id"]: scenario for scenario in data["scenarios"]}

    for scenario_id in (
        "source_agent_durable_mutation_denied",
        "missing_confirmation_or_authorization_denied",
        "expired_human_authorization_ref_denied",
        "wrong_tenant_human_authorization_ref_denied",
        "artifact_write_requires_approval_gate",
        "raw_content_rejected",
    ):
        assert scenarios[scenario_id]["status"] == "PASS"
        assert scenarios[scenario_id]["runtime_execution_allowed"] is False
