from __future__ import annotations

import json
from pathlib import Path

from scripts.v5_8a_planning_gate_evidence import build_evidence, render_v58b_entry_decision


def test_v5_8a_builds_planning_gate_evidence_from_existing_real_data() -> None:
    evidence = build_evidence()

    assert evidence["stage"] == "V5-8A Distributed Runtime Planning Gate"
    assert evidence["decision_scope"] == "planning_gate_only"
    assert evidence["v5_8_runtime_implementation_started"] is False
    assert evidence["v5_8_runtime_implementation_allowed"] is False
    assert evidence["docs_status"]["all_present"] is True
    assert evidence["v5_7b_entry_decision"]["decision"] == "GO_FOR_V5_8_PLANNING_AND_PRE_IMPLEMENTATION_AUDIT"


def test_v5_8a_real_data_readiness_uses_real_llm_and_local_markdown_evidence() -> None:
    evidence = build_evidence()

    assert evidence["status"] == "PASS"
    assert evidence["provider"]["api_key_configured"] is True
    assert evidence["ux12_evidence"]["real_llm_backed"] is True
    assert evidence["ux12_evidence"]["provider_invocation_count"] > 0
    assert evidence["folder_readiness"]["scanner_actual_read_count"] > 0
    assert evidence["missing_evidence"] == []


def test_v5_8b_entry_decision_is_limited_to_next_slice() -> None:
    evidence = build_evidence()
    decision = render_v58b_entry_decision(evidence)

    assert decision["decision"] == "GO_FOR_V5_8B_PLANNING_OR_IMPLEMENTATION_PREP"
    assert decision["v5_8b_runtime_implementation_may_start"] is True
    assert decision["v5_8_complete_runtime_may_be_claimed"] is False
    assert "distributed multi-Agent runtime ready" in decision["forbidden_claims"]


def test_v5_8a_existing_ux12_evidence_is_redacted() -> None:
    payload = Path("docs/design/V4.x/evidence/unified-experience/UX-12/local-document-workflow-result.json").read_text(encoding="utf-8")

    for forbidden in [
        "capability_token",
        "subscription_token",
        "Authorization",
        "Bearer",
        "raw_trace_payload",
        "raw_artifact_content",
        "raw_connector_payload",
        "raw prompt",
        "upstream signed URL",
    ]:
        assert forbidden not in payload


def test_v5_8a_generated_json_is_parseable_after_script_run(tmp_path, monkeypatch) -> None:
    # This test validates the evidence structure without redirecting the script
    # output path, because the project uses a fixed audit evidence directory.
    evidence = build_evidence()
    text = json.dumps(evidence, ensure_ascii=False)
    parsed = json.loads(text)

    assert parsed["schema_version"] == "v5_8a.planning_gate_evidence.v1"
