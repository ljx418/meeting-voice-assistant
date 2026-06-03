"""V4.2-B controlled runtime design gate tests."""

from __future__ import annotations

import json
from pathlib import Path


CONTRACT_PATH = Path("docs/design/V4.2/v4_2_b_controlled_runtime_design_gate_contract.json")
DOC_PATHS = [
    CONTRACT_PATH,
    Path("docs/design/V4.2/v4_2_b_controlled_runtime_design_gate_plan.md"),
    Path("docs/design/V4.2/v4_2_b_controlled_runtime_design_gate_acceptance.md"),
    Path("docs/design/V4.2/v4_2_b_controlled_runtime_design_gate_audit.md"),
    Path("docs/design/V4.2/v4_2_b_controlled_runtime_design_gate_completion_note.md"),
]
FORBIDDEN_CLAIMS = [
    "controlled executor ready",
    "Agent executor ready",
    "autonomous workflow editing ready",
    "complete Workflow Studio ready",
    "complete AgentTalkWindow ready",
    "production-ready external app support",
    "full multi-Agent orchestration ready",
]
SAFE_CONTEXT = (
    "forbidden",
    "Forbidden",
    "must not",
    "does not prove",
    "不能声明",
    "禁止",
    "不实现",
    "不证明",
)


def _contract() -> dict:
    return json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))


def _safe_context_for(text: str, index: int, phrase: str) -> str:
    block_start = max(0, text.rfind("\n\n", 0, index) + 2)
    block_end = text.find("\n\n", index)
    if block_end == -1:
        block_end = len(text)
    return text[max(block_start, index - 320) : min(block_end, index + len(phrase) + 160)]


def test_v42b_design_gate_contract_exists_and_is_not_runtime_implementation() -> None:
    contract = _contract()

    assert contract["stage"] == "V4.2-B"
    assert contract["status"] == "design_gate_complete"
    assert contract["implementation_enabled"] is False
    assert contract["generic_runtime_mutation_enabled"] is False
    assert contract["agent_mutation_enabled"] is False
    assert contract["allowed_claim"] == "V4.2-B complete: controlled runtime design gate ready for implementation review."


def test_v42b_contract_preserves_governance_boundaries() -> None:
    boundary = _contract()["boundary"]

    assert boundary["source_agent_can_execute_mutation"] is False
    assert boundary["user_confirmed_required_for_durable_mutation"] is True
    assert boundary["high_risk_action_approval_gated"] is True
    assert boundary["event_payload_truth"] is False
    assert boundary["executor_reads_only_redacted_or_approved_inputs"] is True
    assert boundary["workflow_spec_runtime_truth"] is False
    assert boundary["drawio_runtime_truth"] is False
    assert boundary["html_report_mutation_surface"] is False


def test_v42c_runtime_contract_requires_user_confirmation_and_rejects_agent_source() -> None:
    runtime_contract = _contract()["runtime_contract"]

    for operation in ("generic_workflow_start", "generic_station_rerun"):
        item = runtime_contract[operation]
        assert item["stage"] == "V4.2-C"
        assert item["requires_user_confirmed"] is True
        assert "agent" in item["forbidden_sources"]
        assert item["must_record_evidence"] is True

    rerun = runtime_contract["generic_station_rerun"]
    assert rerun["must_create_new_attempt"] is True
    assert rerun["must_preserve_previous_attempts"] is True


def test_v42b_acceptance_requires_real_data_and_no_static_runtime_evidence() -> None:
    acceptance = Path("docs/design/V4.2/v4_2_b_controlled_runtime_design_gate_acceptance.md").read_text(encoding="utf-8")
    contract = _contract()

    assert "tests/fixtures/desktop/技术分享" in acceptance
    assert "tests/fixtures/desktop/技术分享_损坏" in acceptance
    assert "cannot pass on static reports alone" in acceptance
    assert any("Use real V4.1 local Markdown workflow data" in item for item in contract["acceptance_requirements"])


def test_v42b_evidence_contract_is_redacted_and_complete() -> None:
    evidence_contract = _contract()["evidence_contract"]

    for field in [
        "operation_type",
        "workflow_instance_id",
        "station_run_id",
        "attempt",
        "user_confirmed",
        "source",
        "policy_decision",
        "runtime_result_ref",
        "correlation_id",
        "idempotency_key",
        "redaction_status",
    ]:
        assert field in evidence_contract["required_fields"]

    for forbidden in [
        "capability_token",
        "subscription_token",
        "Authorization",
        "Bearer",
        "secret",
        "raw_trace_payload",
        "raw_artifact_content",
        "raw_connector_payload",
        "raw prompt",
        "upstream signed URL",
    ]:
        assert forbidden in evidence_contract["forbidden_fields"]


def test_v42b_no_false_green_claims_outside_forbidden_context() -> None:
    for path in DOC_PATHS:
        text = path.read_text(encoding="utf-8")
        for claim in FORBIDDEN_CLAIMS:
            start = 0
            while True:
                index = text.find(claim, start)
                if index < 0:
                    break
                context = _safe_context_for(text, index, claim)
                assert any(marker in context for marker in SAFE_CONTEXT), f"{claim!r} unsafe in {path}:{text.count(chr(10), 0, index) + 1}"
                start = index + len(claim)


def test_v42b_route_guard_blocks_new_runtime_routes() -> None:
    route_guard = _contract()["route_guard"]

    assert route_guard["v4_2_b_new_runtime_routes_allowed"] is False
    for pattern in ["/execute", "/agent/execute", "/kill-switch", "/rollback", "/admin-override"]:
        assert pattern in route_guard["forbidden_new_route_patterns"]
