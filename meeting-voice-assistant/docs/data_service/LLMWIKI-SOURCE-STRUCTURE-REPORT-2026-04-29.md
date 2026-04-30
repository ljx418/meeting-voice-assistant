# LLMWiki Source 页面结构阶段报告

日期：2026-04-29

## 目标

本阶段目标是把“标题是线索，不是结论”的质量边界从 topic 页继续延伸到 source 页，避免 title-only / low-content source 把来源标题重复写成 `Core Conclusion` 或 `Evidence`。

## 已完成

- source outline 会识别与 source title 等价的 passage
- 如果 `Core Conclusion` 只是来源标题本身，则降级为空
- title-only source 页显示 `暂无明确结论，建议回看原文`
- 来源标题级材料进入 `Source Signals`
- 与 `Source Signals` 重复的 passage 不再进入 `Evidence`

## 验收结果

自动化测试：

```bash
python3 -m pytest backend/tests/test_llmwiki.py backend/tests/test_llmwiki_layers.py backend/tests/test_data_service.py backend/tests/test_data_service_api.py -q
```

结果：

- 91 passed

真实知识库端到端验证：

```bash
python3 -m data_service ingest \
  --workspace /tmp/data-service-llmwiki-source-structure-20260429 \
  /Users/Zhuanz/Desktop/workspace/知识库/row/deepseek_split
```

结果：

- 86 sources
- 248 distilled units
- `llmwiki: success`
- `graphrag: indexed`
- GraphRAG compat state: 85 entities / 76 themes / 131 relationships
- `source_signal_pages`: 86
- `source_evidence_pages`: 0
- `bad_source_titles`: 0
- `bad_page_titles`: 0
- `bad_topic_titles`: 0

抽样确认：

- `Hermes配置微信飞书401认证错误解决`：`Core Conclusion` 为暂无明确结论，标题进入 `Source Signals`
- `小米SU7玻璃防晒性能解析`：`Core Conclusion` 为暂无明确结论，标题进入 `Source Signals`
- `已安装VSCode选项验证`：`Core Conclusion` 为暂无明确结论，标题进入 `Source Signals`
- `社招`：`Core Conclusion` 为暂无明确结论，标题进入 `Source Signals`
- `税后50万计算税前工资`：`Core Conclusion` 为暂无明确结论，标题进入 `Source Signals`

## 后续

Source 页面结构第一轮已完成。下一步继续推进：

- topic 合并策略
- `/knowledge` 质量反馈与人工校正入口
- GraphRAG 弱实体与专有名词归并
