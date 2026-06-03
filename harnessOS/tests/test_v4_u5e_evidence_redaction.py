import json
from pathlib import Path

from core.workflows.v4_u5e_local_document_workflow import (
    FakeLLMProviderAdapter,
    assert_no_sensitive_text,
    run_local_document_workflow,
)


FIXTURE = Path("tests/fixtures/desktop/技术分享")


def test_evidence_chain_records_provider_refs_without_raw_prompt_or_content():
    result = run_local_document_workflow(
        provider_adapter=FakeLLMProviderAdapter(),
        requested_path="tests/fixtures/desktop/技术分享",
        fixture_root=FIXTURE,
    )
    evidence = result["evidence_chain"]

    assert len(evidence) == 4
    for item in evidence:
        assert item["provider"] == "fake"
        assert item["model_ref"] == "fake-model"
        assert item["provider_config_source"] == "test"
        assert item["prompt_template_ref"]
        assert item["input_artifact_refs"]
        assert item["output_artifact_refs"]
        assert item["redaction_status"] == "redacted"
        assert item["raw_prompt_exposed"] is False
        assert item["raw_file_content_exposed"] is False
        assert item["token_exposed"] is False

    payload = json.dumps(result, ensure_ascii=False)
    assert "AgentOS 采用 proposal-first" not in payload
    assert "请基于以下 Markdown 技术文档" not in payload
    assert_no_sensitive_text(result)
