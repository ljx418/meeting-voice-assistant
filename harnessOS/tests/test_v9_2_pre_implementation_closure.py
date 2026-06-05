from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


V9_ROOT = Path("docs/design/V9.x")
EVIDENCE_ROOT = V9_ROOT / "evidence" / "v9-2-controlled-executor-pre-implementation"


def test_v9_2_pre_implementation_closure_passes_with_scoped_runtime_approval() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "tools.v9.generate_v9_2_pre_implementation_closure"],
        check=False,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    data = json.loads((EVIDENCE_ROOT / "pre-implementation-data.json").read_text(encoding="utf-8"))

    assert data["status"] == "PASS"
    assert data["audit_type"] == "implementation_readiness_closure"
    assert data["v9_2_runtime_implementation_allowed"] is True
    assert data["runtime_executor_route_created"] is False
    assert data["runtime_worker_created"] is False
    assert data["source_agent_durable_mutation_allowed"] is False
    assert data["requires_human_high_risk_decision"] is False
    assert data["external_audit_deferred"] is True
    assert all(check["status"] == "PASS" for check in data["checks"])
    assert any(item["fixture_id"] == "v9-2-source-agent-durable-mutation-denied" for item in data["fixtures"])
    assert "V9-2 runtime evidence must prove only the four allowlisted actions." in data["remaining_blockers"]


def test_v9_2_high_risk_decision_is_scoped_go_for_implementation() -> None:
    decision = json.loads((V9_ROOT / "decisions/v9_2_high_risk_human_decision.json").read_text(encoding="utf-8"))

    assert decision["stage_id"] == "V9-2"
    assert decision["decision"] == "GO_FOR_IMPLEMENTATION"
    assert "runtime_executor_route" in decision["blocked_work"]
    assert "runtime_worker" in decision["blocked_work"]
    assert "source_agent_durable_mutation" in decision["blocked_work"]
    assert "connector_call" in decision["blocked_work"]
    assert "git_push" in decision["blocked_work"]
