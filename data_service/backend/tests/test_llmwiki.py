import os
import zipfile
from pathlib import Path

from app.llmwiki.config import LLMWikiConfig
from app.llmwiki.extractors import get_extractor
from app.llmwiki.extractors.docx_zip import DocxExtractor
from app.llmwiki.extractors.jsonfile import ChatJsonExtractor
from app.llmwiki.extractors.yamlfile import YamlExtractor
from app.llmwiki.dotenv_support import load_llmwiki_dotenv
from app.llmwiki.engine import WikiEngine
from app.llmwiki.compiler.llm_compiler import WikiCompiler
from app.llmwiki.models import Passage, SourceRecord


def _write_markdown(path: Path, title: str, body: str) -> None:
    path.write_text(f"# {title}\n\n{body}\n", encoding="utf-8")


def _write_minimal_docx(path: Path, paragraphs: list[str]) -> None:
    document_body = "".join(
        f"<w:p><w:r><w:t>{text}</w:t></w:r></w:p>"
        for text in paragraphs
    )
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("[Content_Types].xml", "<Types xmlns=\"http://schemas.openxmlformats.org/package/2006/content-types\"/>")
        archive.writestr("_rels/.rels", "")
        archive.writestr(
            "word/document.xml",
            (
                "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>"
                "<w:document xmlns:w=\"http://schemas.openxmlformats.org/wordprocessingml/2006/main\">"
                f"<w:body>{document_body}</w:body></w:document>"
            ),
        )


def test_docx_yaml_extractors_are_registered_and_parse_content(tmp_path):
    docx_path = tmp_path / "contract.docx"
    yaml_path = tmp_path / "contract.yaml"
    _write_minimal_docx(docx_path, ["OpenClaw 治理方案", "MCP 出门验证覆盖 GraphRAG。"])
    yaml_path.write_text("title: PhaseE\ncapabilities:\n  - yaml structured parsing\n", encoding="utf-8")

    assert isinstance(get_extractor(str(docx_path)), DocxExtractor)
    assert isinstance(get_extractor(str(yaml_path)), YamlExtractor)
    docx_result = DocxExtractor().extract(str(docx_path))
    yaml_result = YamlExtractor().extract(str(yaml_path))

    assert docx_result.status == "success"
    assert "OpenClaw" in "\n".join(section.text for section in docx_result.sections)
    assert yaml_result.status == "success"
    assert any(section.locator["kind"] == "yaml_path" for section in yaml_result.sections)
    assert "yaml structured parsing" in "\n".join(section.text for section in yaml_result.sections)


def test_ingest_writes_markdown_and_source_page(tmp_path, monkeypatch):
    workspace = tmp_path / "workspace"
    doc = tmp_path / "docs" / "claude.md"
    doc.parent.mkdir(parents=True)
    _write_markdown(doc, "Claude Code", "Claude Code helps with code review and implementation.")

    monkeypatch.setenv("LLMWIKI_WORKSPACE", str(workspace))
    monkeypatch.setenv("LLMWIKI_LLM_PROVIDER", "null")

    engine = WikiEngine(LLMWikiConfig.from_env())
    result = engine.ingest([str(doc)])

    assert result["success"] == 1
    assert len(result["pages"]) >= 1

    page = engine.storage.get_page(result["pages"][0])
    assert page is not None
    assert page.markdown_path
    assert Path(page.markdown_path).exists()
    assert page.compile_status in {"fallback", "disabled"}

    source = engine.storage.get_source(result["sources"][0])
    assert source is not None
    assert source.compile_status in {"fallback", "disabled"}


def test_ingest_generates_topic_pages(tmp_path, monkeypatch):
    workspace = tmp_path / "workspace"
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir(parents=True)
    _write_markdown(docs_dir / "llm-a.md", "LLM Notes A", "LLM systems use prompts and models.")
    _write_markdown(docs_dir / "llm-b.md", "LLM Notes B", "GPT workflows rely on prompts and evaluation.")

    monkeypatch.setenv("LLMWIKI_WORKSPACE", str(workspace))
    monkeypatch.setenv("LLMWIKI_LLM_PROVIDER", "null")

    engine = WikiEngine(LLMWikiConfig.from_env())
    result = engine.ingest([str(docs_dir)])

    pages = engine.storage.list_pages(limit=20)
    kinds = {page.kind.value if hasattr(page.kind, "value") else page.kind for page in pages}
    assert "topic" in kinds
    assert len(result["pages"]) >= 2


def test_search_uses_fts_after_ingest(tmp_path, monkeypatch):
    workspace = tmp_path / "workspace"
    doc = tmp_path / "notes.md"
    _write_markdown(doc, "Meeting Transcript", "OpenAI compatible interfaces and ClaudeCode setup.")

    monkeypatch.setenv("LLMWIKI_WORKSPACE", str(workspace))
    monkeypatch.setenv("LLMWIKI_LLM_PROVIDER", "null")

    engine = WikiEngine(LLMWikiConfig.from_env())
    engine.ingest([str(doc)])

    result = engine.search("ClaudeCode")
    assert result["pages"] or result["passages"]


def test_reingest_existing_source_recompiles_when_model_changes(tmp_path, monkeypatch):
    workspace = tmp_path / "workspace"
    doc = tmp_path / "reingest.md"
    _write_markdown(doc, "Claude Code", "Claude Code helps with implementation.")

    monkeypatch.setenv("LLMWIKI_WORKSPACE", str(workspace))
    monkeypatch.setenv("LLMWIKI_LLM_PROVIDER", "null")
    engine = WikiEngine(LLMWikiConfig.from_env())
    first = engine.ingest([str(doc)])
    assert first["success"] == 1

    monkeypatch.setenv("LLMWIKI_LLM_PROVIDER", "http")
    monkeypatch.setenv("LLMWIKI_LLM_API_BASE", "https://example.invalid")
    monkeypatch.setenv("LLMWIKI_LLM_API_KEY_ENV", "TEST_KEY")
    monkeypatch.setenv("TEST_KEY", "x")

    engine = WikiEngine(LLMWikiConfig.from_env())
    second = engine.ingest([str(doc)])
    assert second["success"] == 1
    assert second["skipped"] == 0


def test_chat_json_extractor_reads_mapping_fragments(tmp_path):
    payload = {
        "id": "conv-1",
        "title": "安装openclaw",
        "mapping": {
            "1": {
                "id": "1",
                "message": {
                    "inserted_at": "2025-03-15T20:34:07.776000+08:00",
                    "fragments": [{"type": "REQUEST", "content": "怎么安装 OpenClaw？"}],
                },
            },
            "2": {
                "id": "2",
                "message": {
                    "inserted_at": "2025-03-15T20:34:08.776000+08:00",
                    "fragments": [{"type": "RESPONSE", "content": "先安装 Python，再执行安装脚本。"}],
                },
            },
        },
    }
    path = tmp_path / "conversation.json"
    path.write_text(__import__("json").dumps(payload, ensure_ascii=False), encoding="utf-8")

    result = ChatJsonExtractor().extract(str(path))

    assert result.status == "success"
    assert len(result.sections) == 2
    assert "OpenClaw" in result.sections[0].text
    assert "安装脚本" in result.sections[1].text


def test_topic_slug_refines_beyond_general():
    compiler = WikiCompiler(LLMWikiConfig())
    source = SourceRecord(title="安装OpenClaw", original_path="/tmp/install-openclaw.json")

    refined = compiler._refine_topic_slug("general", source, "OpenClaw installation steps and config")

    assert refined != "general"
    assert "openclaw" in refined


def test_chinese_two_character_source_title_is_meaningful():
    compiler = WikiCompiler(LLMWikiConfig())
    source = SourceRecord(title="社招", original_path="/tmp/recruiting.json")

    title = compiler._display_title_for_source(
        source,
        {
            "question": "社招",
            "core_conclusion": "",
            "summary": "",
            "steps": [],
            "risks": [],
            "key_points": [],
            "keywords": ["社招"],
        },
    )

    assert title == "社招"


def test_sanitize_text_removes_uuid_noise():
    compiler = WikiCompiler(LLMWikiConfig())
    cleaned = compiler._sanitize_text(
        "conversation_id: 34a473e3-fc17-43d3-8196-1b5a205b045e\n"
        "2025-03-15T20:34:07.776000+08:00\n"
        "安装 Claude Code 的具体步骤"
    )

    assert "34a473e3" not in cleaned
    assert "2025-03-15" not in cleaned
    assert "安装 Claude Code" in cleaned


def test_derive_source_title_uses_json_title_value_not_key(tmp_path, monkeypatch):
    workspace = tmp_path / "workspace"
    path = tmp_path / "record.json"
    path.write_text(
        __import__("json").dumps(
            {
                "title": "Hermes配置微信飞书401认证错误解决",
                "content": "回调地址和应用凭证需要同步检查。",
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("LLMWIKI_WORKSPACE", str(workspace))
    monkeypatch.setenv("LLMWIKI_LLM_PROVIDER", "null")

    engine = WikiEngine(LLMWikiConfig.from_env())
    result = engine.ingest([str(path)])

    source = engine.storage.get_source(result["sources"][0])
    assert source is not None
    assert source.title == "Hermes配置微信飞书401认证错误解决"
    assert source.title != "title"


def test_extract_conversations_list_to_files(tmp_path):
    workspace = tmp_path / "workspace"
    payload = [
        {"id": "conv-a", "title": "安装OpenClaw", "mapping": {"1": {"id": "1", "message": {"fragments": [{"type": "REQUEST", "content": "OpenClaw 怎么装"}]}}}},
        {"id": "conv-b", "title": "ClaudeCode", "mapping": {"1": {"id": "1", "message": {"fragments": [{"type": "REQUEST", "content": "ClaudeCode"}]}}}},
    ]
    path = tmp_path / "conversations.json"
    path.write_text(__import__("json").dumps(payload, ensure_ascii=False), encoding="utf-8")
    os.environ["LLMWIKI_WORKSPACE"] = str(workspace)

    files = ChatJsonExtractor.preprocess_json_for_ingest(str(path))

    assert len(files) == 2
    assert all(Path(file).exists() for file in files)
    assert all(file.endswith(".md") for file in files)
    assert str(workspace / "intermediate" / "llmwiki_docs" / "conversations") in files[0]
    assert Path(files[0]).parent == workspace / "intermediate" / "llmwiki_docs" / "conversations"
    content = Path(files[0]).read_text(encoding="utf-8")
    assert "# 安装OpenClaw" in content
    assert "## Question" in content
    assert "## Core Conclusion" in content
    assert "## Conversation" in content
    assert "### Turn 1" in content


def test_preprocess_mapping_json_derives_title_from_user_question(tmp_path, monkeypatch):
    workspace = tmp_path / "workspace"
    conv_id = "758e5c7e-5b91-4d3f-9df6-32c5ad7356aa"
    payload = {
        "id": conv_id,
        "mapping": {
            "1": {
                "id": "1",
                "message": {
                    "fragments": [{"type": "REQUEST", "content": "Hermes配置微信飞书401认证错误怎么解决？"}],
                },
            },
            "2": {
                "id": "2",
                "message": {
                    "fragments": [{"type": "RESPONSE", "content": "检查回调地址、应用凭证和签名配置。"}],
                },
            },
        },
    }
    path = tmp_path / "conversations.json"
    path.write_text(__import__("json").dumps(payload, ensure_ascii=False), encoding="utf-8")
    monkeypatch.setenv("LLMWIKI_WORKSPACE", str(workspace))

    files = ChatJsonExtractor.preprocess_json_for_ingest(str(path))

    content = Path(files[0]).read_text(encoding="utf-8")
    assert "# Hermes配置微信飞书401认证错误怎么解决" in content
    assert f"# {conv_id}" not in content
    assert conv_id in Path(files[0]).name


def test_load_conversation_payload_derives_human_title_without_raw_title(tmp_path):
    conv_id = "34a473e3-fc17-43d3-8196-1b5a205b045e"
    payload = {
        "id": conv_id,
        "turns": [
            {"role": "user", "content": "请帮我整理 GraphRAG 索引失败排查步骤"},
            {"role": "assistant", "content": "先检查 CLI，再检查工作区配置。"},
        ],
    }
    path = tmp_path / "chat.json"
    path.write_text(__import__("json").dumps(payload, ensure_ascii=False), encoding="utf-8")

    bundle = ChatJsonExtractor.load_conversation_payload(str(path))

    assert bundle is not None
    assert bundle["conversation_id"] == conv_id
    assert bundle["title"] == "整理 GraphRAG 索引失败排查步骤"
    assert conv_id not in bundle["title"]


def test_simple_turns_json_does_not_get_rewritten(tmp_path):
    payload = {
        "title": "简单对话",
        "turns": [
            {"role": "user", "content": "你好"},
            {"role": "assistant", "content": "你好，有什么可以帮你？"},
        ],
    }
    path = tmp_path / "simple.json"
    path.write_text(__import__("json").dumps(payload, ensure_ascii=False), encoding="utf-8")

    files = ChatJsonExtractor.preprocess_json_for_ingest(str(path))

    assert files == [str(path)]


def test_ingest_chat_json_persists_conversation_and_secondary_authority(tmp_path, monkeypatch):
    workspace = tmp_path / "workspace"
    path = tmp_path / "chat.json"
    path.write_text(
        __import__("json").dumps(
            {
                "id": "conv-1",
                "title": "OpenClaw 安装问答",
                "turns": [
                    {"role": "user", "content": "怎么安装 OpenClaw？"},
                    {"role": "assistant", "content": "先安装 Python，再执行安装脚本。"},
                ],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    monkeypatch.setenv("LLMWIKI_WORKSPACE", str(workspace))
    monkeypatch.setenv("LLMWIKI_LLM_PROVIDER", "null")

    engine = WikiEngine(LLMWikiConfig.from_env())
    result = engine.ingest([str(path)])

    source = engine.storage.get_source(result["sources"][0])
    assert source is not None
    assert source.authority == "SECONDARY_CHAT"

    conversation = engine.storage.get_conversation_by_source(source.source_id)
    assert conversation is not None
    assert conversation.title == "OpenClaw 安装问答"

    turns = engine.storage.get_turns(conversation.conversation_id)
    assert len(turns) == 2

    pages = engine.storage.get_pages_by_source(source.source_id)
    kinds = {page.kind.value if hasattr(page.kind, "value") else page.kind for page in pages}
    assert "conversation_note" in kinds
    source_page = next(page for page in pages if (page.kind.value if hasattr(page.kind, "value") else page.kind) == "source_note")
    assert "## Verification Status" in source_page.body_md
    assert "## Unverified Notes" in source_page.body_md


def test_ingest_mapping_json_without_title_uses_question_as_source_title(tmp_path, monkeypatch):
    workspace = tmp_path / "workspace"
    conv_id = "758e5c7e-5b91-4d3f-9df6-32c5ad7356aa"
    path = tmp_path / "chat-export.json"
    path.write_text(
        __import__("json").dumps(
            {
                "id": conv_id,
                "mapping": {
                    "1": {
                        "id": "1",
                        "message": {
                            "fragments": [{"type": "REQUEST", "content": "Hermes配置微信飞书401认证错误怎么解决？"}],
                        },
                    },
                    "2": {
                        "id": "2",
                        "message": {
                            "fragments": [{"type": "RESPONSE", "content": "检查回调地址、应用凭证和签名配置。"}],
                        },
                    },
                },
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    monkeypatch.setenv("LLMWIKI_WORKSPACE", str(workspace))
    monkeypatch.setenv("LLMWIKI_LLM_PROVIDER", "null")

    engine = WikiEngine(LLMWikiConfig.from_env())
    result = engine.ingest([str(path)])

    source = engine.storage.get_source(result["sources"][0])
    assert source is not None
    assert source.title == "Hermes配置微信飞书401认证错误怎么解决"
    assert conv_id not in source.title
    pages = engine.storage.get_pages_by_source(source.source_id)
    source_page = next(page for page in pages if (page.kind.value if hasattr(page.kind, "value") else page.kind) == "source_note")
    assert source_page.title == "Hermes配置微信飞书401认证错误怎么解决"
    assert conv_id not in source_page.title


def test_read_page_returns_source_citations(tmp_path, monkeypatch):
    workspace = tmp_path / "workspace"
    doc = tmp_path / "notes.md"
    _write_markdown(doc, "OpenClaw Notes", "OpenClaw setup includes Python and API key configuration.")

    monkeypatch.setenv("LLMWIKI_WORKSPACE", str(workspace))
    monkeypatch.setenv("LLMWIKI_LLM_PROVIDER", "null")

    engine = WikiEngine(LLMWikiConfig.from_env())
    result = engine.ingest([str(doc)])
    page = engine.read_page(result["pages"][0])

    assert page["citations"]
    assert page["citations"][0]["type"] == "source"
    assert page["citations"][0]["locator"] == str(doc)


def test_load_llmwiki_dotenv_reads_backend_app_env(monkeypatch):
    monkeypatch.delenv("LLMWIKI_LLM_PROVIDER", raising=False)
    monkeypatch.delenv("LLMWIKI_LLM_MODEL", raising=False)

    load_llmwiki_dotenv()

    assert os.getenv("LLMWIKI_LLM_PROVIDER") == "http"
    assert os.getenv("LLMWIKI_LLM_MODEL") == "MiniMax-M2.7"


def test_topic_title_prefers_meaningful_source_title():
    compiler = WikiCompiler(LLMWikiConfig())
    sources = [
        SourceRecord(title="tmp_claudecode_conversation"),
        SourceRecord(title="安装OpenClaw"),
    ]
    title = compiler._topic_title_from_sources(
        "tmp-claudecode-conversation",
        sources,
        [Passage(text="OpenClaw installation and setup walkthrough")],
    )

    assert title == "OpenClaw"


def test_source_fallback_page_is_structured(tmp_path, monkeypatch):
    workspace = tmp_path / "workspace"
    doc = tmp_path / "conversation.md"
    doc.write_text(
        "# 安装 OpenClaw\n\n"
        "## Question\n\n"
        "怎么安装 OpenClaw？\n\n"
        "## Core Conclusion\n\n"
        "先安装 Python，再运行安装脚本并配置 API Key。\n\n"
        "## Actionable Steps\n\n"
        "1. 安装 Python\n"
        "2. 运行安装脚本\n"
        "3. 配置 API Key\n",
        encoding="utf-8",
    )

    monkeypatch.setenv("LLMWIKI_WORKSPACE", str(workspace))
    monkeypatch.setenv("LLMWIKI_LLM_PROVIDER", "null")

    engine = WikiEngine(LLMWikiConfig.from_env())
    result = engine.ingest([str(doc)])
    page = engine.storage.get_page(result["pages"][0])

    assert page is not None
    assert "## Question" in page.body_md
    assert "## Core Conclusion" in page.body_md
    assert "## Actionable Steps" in page.body_md
    assert "安装 Python" in page.body_md
    assert "## Source Context" in page.body_md
    assert "## Source Details" not in page.body_md
    assert page.title == "安装 OpenClaw"


def test_derive_source_title_prefers_markdown_heading(tmp_path):
    workspace = tmp_path / "workspace"
    doc = tmp_path / ".llmwiki_docs_conversations" / "34c9ceec-91d5-46bf-a246-1cb71c2dabc3_中国人平均寿命达78_2岁.md"
    doc.parent.mkdir(parents=True)
    _write_markdown(doc, "中国人平均寿命达78.2岁", "问答正文")

    engine = WikiEngine(LLMWikiConfig(workspace_path=workspace))
    result = engine.ingest([str(doc)])

    source = engine.storage.get_source(result["sources"][0])
    assert source is not None
    assert source.title == "中国人平均寿命达78.2岁"


def test_title_group_slug_prefers_question_theme():
    compiler = WikiCompiler(LLMWikiConfig())

    slug = compiler._title_group_slug("武汉理工硕士可考公务员岗位")

    assert slug == "武汉理工硕士可考公务员岗位"


def test_semantic_topic_slug_groups_by_entity():
    compiler = WikiCompiler(LLMWikiConfig())

    slug = compiler._semantic_topic_slug("怎么安装 OpenClaw", "OpenClaw 安装步骤和配置")

    assert slug == "openclaw"


def test_semantic_topic_slug_prefers_product_anchor_over_status_fragment():
    compiler = WikiCompiler(LLMWikiConfig())

    assert compiler._semantic_topic_slug("已安装VSCode选项验证", "VSCode 已安装") == "vscode"
    assert compiler._semantic_topic_slug("小米SU7玻璃防晒性能解析", "小米 SU7 玻璃防晒") == "小米su7"
    assert compiler._semantic_topic_slug("股市S1含义解析", "股市 S1 表示市场阶段") == "股市s1"


def test_semantic_topic_slug_rejects_weak_title_fragments():
    compiler = WikiCompiler(LLMWikiConfig())

    assert compiler._semantic_topic_slug("税后50万计算税前工资", "税后收入和税前工资换算") == "税前工资"
    assert compiler._semantic_topic_slug("User seeks clarification on creample term", "creample is a coined term") == "creample"


def test_semantic_topic_slug_covers_low_signal_title_anchors():
    compiler = WikiCompiler(LLMWikiConfig())

    assert compiler._semantic_topic_slug("36岁停止工作确保退休资金充足", "") == "退休资金"
    assert compiler._semantic_topic_slug("管培生实践移植案例", "") == "管培生"
    assert compiler._semantic_topic_slug("端午节看望老人注意事项", "") == "端午节"
    assert compiler._semantic_topic_slug("生成两份云南菜评价", "") == "云南菜"
    assert compiler._semantic_topic_slug("车企相关", "") == "车企"
    assert compiler._semantic_topic_slug("跨设备智能卡片交互系统专利", "") == "智能卡片"
    assert compiler._semantic_topic_slug("香农极限及其在通信中的应用", "") == "香农极限"


def test_conversation_overview_extracts_steps():
    extractor = ChatJsonExtractor()
    overview = extractor._conversation_overview(
        [
            {"role": "user", "content": "怎么安装 OpenClaw？"},
            {"role": "assistant", "content": "1. 安装 Python\n2. 运行安装脚本\n3. 配置 API Key"},
        ]
    )

    assert overview["question"] == "怎么安装 OpenClaw？"
    assert "安装 Python" in overview["steps"][0]


def test_conversation_overview_prefers_concise_conclusion():
    extractor = ChatJsonExtractor()
    overview = extractor._conversation_overview(
        [
            {"role": "user", "content": "怎么部署服务？"},
            {
                "role": "assistant",
                "content": (
                    "可以先完成基础依赖，然后按顺序执行部署。\n"
                    "1. 安装依赖\n"
                    "2. 设置环境变量\n"
                    "3. 启动服务"
                ),
            },
        ]
    )

    assert overview["conclusion"] == "可以先完成基础依赖，然后按顺序执行部署。"
    assert overview["steps"] == ["安装依赖", "设置环境变量", "启动服务"]


def test_topic_outline_avoids_noisy_related_topics():
    compiler = WikiCompiler(LLMWikiConfig())
    outline = compiler._derive_topic_outline(
        "OpenClaw",
        [
            SourceRecord(title="怎么安装 OpenClaw"),
            SourceRecord(title="OpenClaw 配置说明"),
        ],
        [
            Passage(text="[assistant]: OpenClaw 需要先安装 Python，然后配置 API Key。"),
            Passage(text="Path: /tmp/openclaw.md"),
        ],
    )

    assert outline["summary"] == "OpenClaw 需要先安装 Python，然后配置 API Key。"
    assert outline["related_topics"] == []


def test_topic_outline_treats_title_only_material_as_source_signal():
    compiler = WikiCompiler(LLMWikiConfig())
    outline = compiler._derive_topic_outline(
        "VSCode",
        [SourceRecord(title="已安装VSCode选项验证")],
        [Passage(text="已安装VSCode选项验证")],
    )

    assert outline["facts"] == []
    assert outline["source_signals"] == ["已安装VSCode选项验证"]
    assert outline["summary"] == "Collected source material about VSCode from 1 source."


def test_topic_page_uses_source_signals_instead_of_repeating_title_as_fact():
    compiler = WikiCompiler(LLMWikiConfig())
    result = compiler._compile_single_topic(
        "vscode",
        [SourceRecord(source_id="source-vscode", title="已安装VSCode选项验证")],
        [Passage(text="已安装VSCode选项验证")],
    )

    page = result.page
    assert "## Overview" in page.body_md
    assert "## Source Signals" in page.body_md
    assert "## Facts" not in page.body_md
    assert "## Key Ideas" not in page.body_md
    assert "## Evidence Notes" not in page.body_md
    assert page.meta_json["source_signal_count"] == 1


def test_topic_title_prefers_common_entity_over_task_fragments():
    compiler = WikiCompiler(LLMWikiConfig())
    title = compiler._topic_title_from_sources(
        "openclaw",
        [
            SourceRecord(title="怎么安装 OpenClaw"),
            SourceRecord(title="OpenClaw 配置说明"),
        ],
        [
            Passage(text="OpenClaw 需要先安装 Python。"),
            Passage(text="OpenClaw 配置需要 API Key。"),
        ],
    )

    assert title == "OpenClaw"


def test_topic_title_prefers_product_anchor_for_single_noisy_source():
    compiler = WikiCompiler(LLMWikiConfig())

    title = compiler._topic_title_from_sources(
        "vscode",
        [SourceRecord(title="已安装VSCode选项验证")],
        [Passage(text="VSCode 已安装选项需要验证。")],
    )

    assert title == "VSCode"


def test_source_title_cleans_tmp_and_conversation_markers():
    compiler = WikiCompiler(LLMWikiConfig())
    source = SourceRecord(
        source_id="abc12345",
        title="tmp_conversation_id_34a473e3-fc17-43d3-8196-1b5a205b045e",
        original_path="/tmp/tmp_conversation_id_34a473e3-fc17-43d3-8196-1b5a205b045e.json",
    )

    page = compiler._build_structured_source_page(
        source,
        [],
        [Passage(text="怎么安装 OpenClaw？"), Passage(text="先安装 Python，再运行安装脚本。")],
        {
            "question": "怎么安装 OpenClaw？",
            "core_conclusion": "先安装 Python，再运行安装脚本。",
            "summary": "先安装 Python，再运行安装脚本。",
            "steps": ["安装 Python", "运行安装脚本"],
            "risks": [],
            "key_points": [],
            "keywords": ["OpenClaw"],
        },
    )

    assert page.title == "安装 OpenClaw"


def test_source_page_treats_title_only_material_as_source_signal():
    compiler = WikiCompiler(LLMWikiConfig())
    source = SourceRecord(
        source_id="source-vscode",
        title="已安装VSCode选项验证",
        original_path="/tmp/vscode.json",
    )
    outline = compiler._derive_source_outline(
        source,
        [],
        [Passage(text="已安装VSCode选项验证")],
    )

    page = compiler._build_structured_source_page(
        source,
        [],
        [Passage(text="已安装VSCode选项验证")],
        outline,
    )

    assert outline["core_conclusion"] == ""
    assert outline["summary"] == ""
    assert outline["source_signals"] == ["已安装VSCode选项验证"]
    assert "## Core Conclusion\n\n暂无明确结论，建议回看原文。" in page.body_md
    assert "## Source Signals" in page.body_md
    assert "## Evidence" not in page.body_md
