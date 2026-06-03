from pathlib import Path

from core.workflows.v4_u5e_local_document_workflow import FakeLLMProviderAdapter, run_local_document_workflow


FIXTURE = Path("tests/fixtures/desktop/技术分享")


def test_summary_artifacts_include_required_metadata_and_sections():
    result = run_local_document_workflow(
        provider_adapter=FakeLLMProviderAdapter(),
        requested_path="tests/fixtures/desktop/技术分享",
        fixture_root=FIXTURE,
    )

    summaries = [artifact for artifact in result["artifacts"] if artifact["name"].endswith("_总结.md")]
    assert {artifact["name"] for artifact in summaries} == {
        "AgentOS_总结.md",
        "前端低代码_总结.md",
        "项目复盘_总结.md",
    }
    overview = next(artifact for artifact in result["artifacts"] if artifact["name"] == "总览总结.md")
    for artifact in [*summaries, overview]:
        assert artifact["metadata"]["generated_by"] == "fallback_demo"
        assert artifact["metadata"]["provider"] == "fake"
        assert artifact["metadata"]["prompt_template_ref"]
        for section in ["内容概览", "核心主题", "关键知识点", "重要文件列表", "引用文件"]:
            assert section in artifact["content"]
