# LLMWiki Topic 质量阶段报告

日期：2026-04-29

## 目标

本阶段目标是继续推进 LLMWiki 页面质量，重点处理 topic 聚合与 topic 标题自然度，避免 topic 页以动作词、数值残片、英文句子脚手架或文件名化长标题作为主标题。

## 已完成

- `WikiCompiler` 新增更严格的 topic anchor 提取逻辑
- topic slug 与 topic title 统一使用产品/工具/专有名词优先的 anchor
- 拒绝 `已安装 / 免费 / 助手 / User seeks clarification / 万贷款 / 税后` 等弱 topic 残片
- 补充对工具、产品、代码语言、专利号、薪资/贷款类计算主题的 anchor 识别
- 单 source topic 不再只因为来源标题较长就保留完整文件名化标题

## 验收结果

自动化测试：

```bash
python3 -m pytest backend/tests/test_llmwiki.py backend/tests/test_llmwiki_layers.py backend/tests/test_data_service.py backend/tests/test_data_service_api.py -q
```

结果：

- 88 passed

真实知识库端到端验证：

```bash
python3 -m data_service ingest \
  --workspace /tmp/data-service-llmwiki-topic-quality-2-20260429 \
  /Users/Zhuanz/Desktop/workspace/知识库/row/deepseek_split
```

结果：

- 86 sources
- 79 topic pages
- 248 distilled units
- `llmwiki: success`
- `graphrag: indexed`
- GraphRAG compat state: 85 entities / 76 themes / 131 relationships
- `bad_source_titles`: 0
- `bad_page_titles`: 0
- `bad_topic_titles`: 0

代表性 topic 收缩：

- `已安装VSCode选项验证 -> VSCode`
- `小米SU7玻璃防晒性能解析 -> 小米SU7`
- `股市S1含义解析 -> 股市S1`
- `税后50万计算税前工资 -> 税前工资`
- `30万贷款5年等额本息月供计算 -> 等额本息月供`
- `User seeks clarification on creample term -> creample`

## 后续

Topic 标题与聚合第一轮已完成。下一步继续推进页面内容结构、topic 合并策略和 `/knowledge` 质量反馈能力。
