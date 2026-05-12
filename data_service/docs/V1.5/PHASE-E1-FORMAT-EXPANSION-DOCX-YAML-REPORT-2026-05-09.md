# PhaseE1 Format Expansion Docx/Yaml Report

日期：2026-05-09

## 目标

补齐 V1.5 PhaseE 的首个格式扩展子阶段：`docx` 与 `yaml/yml` 能作为正式 source 进入 Data Service 的 scan、distill、LLMWiki 和 GraphRAG 链路。

## 已完成

- 新增 `backend/app/llmwiki/extractors/docx_zip.py`，使用 Open XML zip 结构抽取 DOCX 段落，不引入 python-docx 运行时依赖。
- 新增 `backend/app/llmwiki/extractors/yamlfile.py`，使用 `yaml.safe_load` 将 YAML 叶子节点转为 normalized sections。
- LLMWiki extractor registry 注册 `DocxExtractor` 与 `YamlExtractor`。
- LLMWiki `SourceType` 与 source type detection 支持 `docx/yaml/yml`。
- `DataService.SUPPORTED_SOURCE_SUFFIXES` 支持 `docx/yaml/yml`。
- DataService distill excerpt 对 `docx/yaml/yml` 复用 LLMWiki extractor 输出，避免在 data_service 内重复实现格式解析。
- 新增 extractor 注册与解析测试。
- 新增 docx/yaml 同时进入 `run_default_pipeline()` 的端到端测试，覆盖 distill、LLMWiki 和 GraphRAG。

## 出门验证

```bash
backend/.venv/bin/python -m py_compile backend/data_service/service.py backend/app/llmwiki/extractors/docx_zip.py backend/app/llmwiki/extractors/yamlfile.py backend/app/llmwiki/extractors/__init__.py backend/app/llmwiki/models.py backend/app/llmwiki/engine.py backend/tests/test_data_service.py backend/tests/test_llmwiki.py
```

结果：通过。

```bash
backend/.venv/bin/python -m pytest backend/tests/test_llmwiki.py::test_docx_yaml_extractors_are_registered_and_parse_content backend/tests/test_data_service.py::test_data_service_phasee_docx_yaml_run_default_pipeline -q
```

结果：`2 passed`。

## 对外能力检查

- 新增对外能力：目录扫描、source ingest、distill、LLMWiki 和 GraphRAG 现在接受 `docx/yaml/yml`。
- 未新增新的 MCP tool、HTTP route、CLI 命令或请求字段。
- 未改变既有 `json/txt/md/html/csv/pdf/ppt/pptx` 的后缀判断和 handler。
- 内部 workspace layout 未作为稳定 contract 暴露。

## 下一步

按用户要求，PhaseE1 完成后暂停继续开发，先做代码检视和全量测试，重点确认外部开放能力无隐藏性变更。
