import json
from pathlib import Path


V6_DIR = Path("docs/design/V6.x")
CLOSURE_JSON = V6_DIR / "evidence" / "v6-4-controlled-executor" / "pre-implementation-closure.json"


def test_v6_4_high_risk_decision_allows_limited_runtime_implementation() -> None:
    data = json.loads(CLOSURE_JSON.read_text(encoding="utf-8"))

    assert data["current_decision"] == "GO_FOR_LIMITED_RUNTIME_IMPLEMENTATION"
    assert data["human_high_risk_proceed_decision_recorded"] is True
    assert data["v6_4_runtime_implementation_allowed"] is True
    assert data["runtime_implementation_created"] is True
    assert data["production_executor_route_created"] is False
    assert data["production_runtime_worker_created"] is False
    assert "source_agent_durable_mutation" in data["blocked_work"]
    assert "connector_call" in data["blocked_work"]
    assert "external_llm_call" in data["blocked_work"]


def test_v6_4_required_before_human_proceed_decision_is_complete() -> None:
    data = json.loads(CLOSURE_JSON.read_text(encoding="utf-8"))

    assert data["required_before_human_proceed_decision"] == [
        "v6_4_external_design_review_accepted",
        "v6_4_pre_implementation_audit_has_no_critical_prd_drift",
        "v6_4_test_matrix_accepted",
        "evidence_package_structure_accepted",
        "no_false_green_claim_scan_passes",
        "execution_envelope_conditional_actor_fields_clarified",
    ]


def test_v6_4_execution_envelope_uses_conditional_actor_fields() -> None:
    text = (V6_DIR / "v6_4_execution_contract_model.md").read_text(encoding="utf-8")

    assert "actor_type=human_user:" in text
    assert "requires user_id" in text
    assert "service_account_id optional / null" in text
    assert "actor_type=service_account_with_human_authorization:" in text
    assert "requires service_account_id" in text
    assert "requires authorization_subject_actor_id or user_id as authorizing human" in text


def test_v6_4_test_matrix_covers_external_audit_feedback() -> None:
    text = (V6_DIR / "v6_4_test_matrix.md").read_text(encoding="utf-8")

    required_cases = [
        "approved_api_human_authorization_ref_expired_before_execution_denied",
        "approved_api_without_human_authorization_denied",
        "approved_api_wrong_tenant_denied",
        "approved_api_source_agent_denied",
        "execution_envelope_actor_type_conditional_fields",
        "service_account_without_human_authorization_denied",
        "service_account_expired_authorization_denied",
        "service_account_wrong_operation_denied",
        "service_account_as_agent_executor_denied",
    ]
    for case in required_cases:
        assert case in text


def test_v6_4_no_false_green_claims_are_forbidden() -> None:
    data = json.loads(CLOSURE_JSON.read_text(encoding="utf-8"))
    assert data["allowed_claim"] == "V6-4 complete: limited production controlled executor pilot slice ready for review."
    assert "production controlled executor ready" in data["forbidden_claims"]
    assert "Agent executor ready" in data["forbidden_claims"]
    assert data["runtime_implementation_created"] is True
    assert data["production_executor_route_created"] is False
    assert data["source_agent_durable_mutation_allowed"] is False
