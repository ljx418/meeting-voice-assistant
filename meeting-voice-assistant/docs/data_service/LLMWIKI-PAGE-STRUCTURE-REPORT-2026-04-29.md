# LLMWiki 页面结构阶段报告

日期：2026-04-29

## 目标

本阶段目标是提升 LLMWiki topic 页面正文结构，避免 title-only / low-content topic 把来源标题重复写成 `TL;DR / Key Ideas / Facts`，从而让页面对“标题级信号”和“可验证事实”有更清楚的区分。

## 已完成

- topic 页面默认结构从 `TL;DR / Key Ideas` 调整为 `Overview / Source Signals / Evidence Notes`
- title-only source 不再被写入 `Facts`
- source 标题级材料进入 `Source Signals`
- 只有与 source signal 不重复的内容才进入 `Evidence Notes`
- 页面 `meta_json` 新增 `source_signal_count`

## 验收结果

自动化测试：

```bash
python3 -m pytest backend/tests/test_llmwiki.py backend/tests/test_llmwiki_layers.py backend/tests/test_data_service.py backend/tests/test_data_service_api.py -q
```

结果：

- 90 passed

真实知识库端到端验证：

```bash
python3 -m data_service ingest \
  --workspace /tmp/data-service-llmwiki-page-structure-2-20260429 \
  /Users/Zhuanz/Desktop/workspace/知识库/row/deepseek_split
```

结果：

- 86 sources
- 79 topic pages
- 248 distilled units
- `llmwiki: success`
- `graphrag: indexed`
- GraphRAG compat state: 85 entities / 76 themes / 131 relationships
- `topic_source_signal_pages`: 79
- `topic_evidence_notes_pages`: 4
- `topic_facts_pages`: 0
- `bad_source_titles`: 0
- `bad_page_titles`: 0
- `bad_topic_titles`: 0

代表性页面结构：

- `VSCode`：`Overview + Source Signals + Citations`
- `小米SU7`：`Overview + Source Signals + Citations`
- `creample`：`Overview + Source Signals + Citations`

## 后续

页面结构第一轮已完成。下一步继续推进：

- topic 合并策略
- source 页面结构细化
- `/knowledge` 质量反馈与人工校正入口
