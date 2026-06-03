from pathlib import Path

from core.workflows.v4_u5e_local_document_workflow import FakeLLMProviderAdapter, run_local_document_workflow


FIXTURE = Path("tests/fixtures/desktop/技术分享")


def test_llm_provider_invocation_count_matches_folder_and_overview_summaries():
    adapter = FakeLLMProviderAdapter()
    result = run_local_document_workflow(provider_adapter=adapter, requested_path="tests/fixtures/desktop/技术分享", fixture_root=FIXTURE)

    assert result["status"] == "completed"
    assert result["real_llm_backed"] is False
    assert result["fallback_demo_only"] is True
    assert result["quality_report"]["scanner_actual_read_count"] == 5
    assert result["quality_report"]["provider_invocation_count"] == 4
    assert adapter.invocation_count == 4
