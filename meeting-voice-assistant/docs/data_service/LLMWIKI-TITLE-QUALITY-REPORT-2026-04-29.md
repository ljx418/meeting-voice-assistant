# LLMWiki 标题质量阶段报告

日期：2026-04-29

## 目标

本阶段目标是修复真实知识库 ingest 后 LLMWiki source/page 标题中残留 UUID、`conversation id`、字面量 `title`、`Untitled Source` 的问题，让页面标题更接近用户可读主题。

## 已完成

- 聊天 JSON 无显式 `title` 时，优先从首条 user question 生成可读标题
- mapping 导出的 readable Markdown H1 不再退化为 UUID
- conversation payload 标题不再默认使用 UUID 或文件名
- source title 派生时会跳过 `conversation id`、UUID、`title/name/subject` 等元字段名
- JSON 顶层 `title` 字段会使用字段值，而不是把字段名 `title` 当标题
- 两个汉字的中文短标题（如 `社招`）不再被误判为无意义标题

## 验收结果

自动化测试：

```bash
python3 -m pytest backend/tests/test_llmwiki.py backend/tests/test_llmwiki_layers.py backend/tests/test_data_service.py backend/tests/test_data_service_api.py -q
```

结果：

- 83 passed

真实知识库端到端验证：

```bash
python3 -m data_service ingest \
  --workspace /tmp/data-service-llmwiki-quality-3-20260429 \
  /Users/Zhuanz/Desktop/workspace/知识库/row/deepseek_split
```

结果：

- 86 sources
- 248 distilled units
- `llmwiki: success`
- `graphrag: indexed`
- graph execution owner: `app.graphrag`
- 85 entities
- 76 themes
- 131 relationships
- `bad_source_titles`: 0
- `bad_page_titles`: 0

抽样确认：

- `Hermes配置微信飞书401认证错误解决`
- `Hermes使用`
- `社招`

## 后续

标题质量第一轮已完成。下一步继续推进 topic 聚合质量、页面内容结构和 `/knowledge` 质量反馈能力。
