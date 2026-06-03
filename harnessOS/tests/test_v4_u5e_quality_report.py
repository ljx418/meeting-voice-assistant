from pathlib import Path

from core.workflows.v4_u5e_local_document_workflow import FakeLLMProviderAdapter, run_local_document_workflow


FIXTURE = Path("tests/fixtures/desktop/技术分享")


def test_quality_report_records_unsupported_and_empty_folders():
    result = run_local_document_workflow(
        provider_adapter=FakeLLMProviderAdapter(),
        requested_path="tests/fixtures/desktop/技术分享",
        fixture_root=FIXTURE,
    )
    quality = result["quality_report"]

    assert quality["status"] == "passed"
    assert quality["unsupported_files"] == ["未支持/test.pdf"]
    assert quality["empty_folders"] == ["空文件夹"]
    assert quality["summary_coverage"] == {"expected_folder_count": 3, "generated_summary_count": 3}
    assert quality["scanner_actual_read_count"] == 5
    assert quality["provider_invocation_count"] == 4
