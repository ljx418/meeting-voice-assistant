from pathlib import Path

from core.workflows.v4_u5e_local_document_workflow import (
    FakeLLMProviderAdapter,
    render_ux12_summary,
    run_local_document_workflow,
    write_u5e_evidence_package,
)


FIXTURE = Path("tests/fixtures/desktop/技术分享")


def test_fallback_demo_only_cannot_render_ux12_pass():
    result = run_local_document_workflow(
        provider_adapter=FakeLLMProviderAdapter(),
        requested_path="tests/fixtures/desktop/技术分享",
        fixture_root=FIXTURE,
    )
    summary = render_ux12_summary(result)

    assert "status: BLOCKED" in summary
    assert "fallback_demo_only: true" in summary
    assert "real_llm_backed: false" in summary


def test_u5e_evidence_package_writes_redacted_outputs(tmp_path):
    result = run_local_document_workflow(
        provider_adapter=FakeLLMProviderAdapter(),
        requested_path="tests/fixtures/desktop/技术分享",
        fixture_root=FIXTURE,
    )
    write_u5e_evidence_package(result, tmp_path)

    assert (tmp_path / "local-document-workflow-result.json").exists()
    assert (tmp_path / "quality_report.json").exists()
    assert (tmp_path / "evidence_chain.json").exists()
    assert (tmp_path / "result-summary.md").exists()
    assert (tmp_path / "artifacts" / "AgentOS_总结.md").exists()
    payload = (tmp_path / "local-document-workflow-result.json").read_text(encoding="utf-8")
    assert '"content":' not in payload
    assert "AgentOS 采用 proposal-first" not in payload


def test_existing_ux12_reality_check_reflects_real_llm_evidence_when_present():
    text = Path("docs/design/V4.x/evidence/unified-experience/UX-12/result-summary.md").read_text(encoding="utf-8")

    if "real_llm_backed: true" in text:
        assert "status: PASS" in text
        assert "evidence_scope: real_runtime" in text
        assert "provider_invocation_count:" in text
    else:
        assert "status: BLOCKED" in text
        assert "MiniMax or OpenAI-compatible provider invocation evidence" in text
