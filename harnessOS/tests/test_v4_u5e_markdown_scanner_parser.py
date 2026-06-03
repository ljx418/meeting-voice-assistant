from pathlib import Path

from core.workflows.v4_u5e_local_document_workflow import scan_markdown_folder


FIXTURE = Path("tests/fixtures/desktop/技术分享")


def test_markdown_scanner_parser_reads_actual_files():
    scan = scan_markdown_folder(FIXTURE)

    assert scan["scanner_actual_read_count"] == 5
    assert scan["markdown_file_count"] == 5
    assert scan["unsupported_files"] == ["未支持/test.pdf"]
    assert scan["empty_folders"] == ["空文件夹"]
    docs = scan["documents"]
    assert any(doc.relative_path == "AgentOS/01-架构.md" for doc in docs)
    assert any("AgentOS 采用 proposal-first" in doc.content for doc in docs)
