from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


V9_ROOT = Path("docs/design/V9.x")
DURABLE_OPERATIONS = {
    "workflow.instance.start",
    "station.rerun",
    "artifact.write",
    "quality.evaluation.create",
}


def _run_module(module: str, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", module, *args],
        check=False,
        text=True,
        capture_output=True,
    )


def test_v9_agent_execution_envelope_requires_authorization_for_all_durable_actions() -> None:
    schema = json.loads((V9_ROOT / "schemas/agent_execution_envelope.schema.json").read_text(encoding="utf-8"))
    schema_text = json.dumps(schema, ensure_ascii=False)

    for operation in DURABLE_OPERATIONS:
        assert operation in schema_text
    assert "user_confirmed" in schema_text
    assert "human_authorization_ref" in schema_text
    assert "agent" in schema_text
    assert "not" in schema_text


def test_v9_schema_bundle_and_negative_fixtures_generate_pass_reports() -> None:
    result = _run_module("tools.v9.validate_schema_bundle", "--write-reports")

    assert result.returncode == 0, result.stdout + result.stderr
    contract = json.loads((V9_ROOT / "reports/v9_1_contract_validation_report.json").read_text(encoding="utf-8"))
    negative = json.loads((V9_ROOT / "reports/v9_1_negative_test_results.json").read_text(encoding="utf-8"))
    assert contract["status"] == "PASS"
    assert negative["status"] == "PASS"
    assert contract["runtime_evidence"] is False


def test_v9_no_false_green_and_redaction_scans_pass_for_allowed_contexts() -> None:
    claim = _run_module("tools.v9.scan_no_false_green", "--write-report")
    redaction = _run_module("tools.v9.scan_redaction_forbidden_content", "--write-report")

    assert claim.returncode == 0, claim.stdout + claim.stderr
    assert redaction.returncode == 0, redaction.stdout + redaction.stderr
    claim_report = json.loads((V9_ROOT / "reports/v9_1_no_false_green_scan.json").read_text(encoding="utf-8"))
    redaction_report = json.loads((V9_ROOT / "reports/v9_1_redaction_scan.json").read_text(encoding="utf-8"))
    assert claim_report["status"] == "PASS"
    assert claim_report["violations"] == []
    assert redaction_report["status"] == "PASS"
    assert redaction_report["violations"] == []


def test_v9_evidence_validator_rejects_planning_only_v9_8_fixture() -> None:
    result = _run_module(
        "tools.v9.validate_evidence_package",
        "docs/design/V9.x/fixtures/evidence/v9_8_reject_planning_only_sample.json",
    )

    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["status"] == "FAIL"
    assert "V9-8 cannot pass with runtime_backed=false" in payload["failures"]


def test_v9_high_risk_human_decision_keeps_runtime_no_go() -> None:
    decision = json.loads((V9_ROOT / "decisions/v9_1_high_risk_human_decision.json").read_text(encoding="utf-8"))

    assert decision["decision"] == "GO_FOR_IMPLEMENTATION"
    assert "Safety Gate implementation only" in decision["scope"]
    assert "runtime_worker" in decision["blocked_work"]
    assert "source_agent_durable_mutation" in decision["blocked_work"]
    assert "controlled_executor_action_execution" in decision["blocked_work"]
    assert "agent_execution_envelope_validator" in decision["allowed_work"]
    assert "human_authorization_ref_validator" in decision["allowed_work"]
    assert "capability_resolver_deny_by_default_engine" in decision["allowed_work"]
    assert "schema_validator" in decision["allowed_work"]
