# Quality Correction Rules 阶段报告

日期：2026-04-30

## 结论

本轮把 `/knowledge` 的人工反馈推进为“可审核校正规则”第一版。系统仍不自动改写 LLMWiki、GraphRAG 或 row 原始资料，而是把可执行意图沉淀到 `quality/correction_rules.json`，作为后续审核和规则消费的队列。

## 新增能力

- workspace 新增 `quality/correction_rules.json`
- `rename_suggest` 生成 `draft rename` 规则
- `merge_suggest` 生成 `draft merge` 规则
- `mark_noise` 生成 `draft suppress` 规则
- `needs_review` 生成 `draft review` 规则
- `confirm_good / note` 只保留为反馈，不自动生成规则
- `summary.json.quality.correction_rules` 新增规则总数、状态分布、规则类型分布、target type 分布
- HTTP API 新增：
  - `POST /api/v1/knowledge/quality/corrections`
  - `POST /api/v1/knowledge/quality/corrections/build`
- `/knowledge` 反馈面板新增“生成规则”和“待审核规则”列表

## 自动化验收

```bash
python3 -m pytest backend/tests/test_data_service.py backend/tests/test_data_service_api.py -q
```

结果：

- `57 passed`

前端打包验证：

```bash
npx vite build
```

结果：

- Vite build passed

## API Smoke Test

提交反馈：

```bash
POST /api/v1/knowledge/quality/feedback
{
  "workspace": "/tmp/data-service-quality-rules-check-20260430",
  "target_type": "entity",
  "target_id": "old-node",
  "action": "merge_suggest",
  "label": "Old Node",
  "suggested_value": "Canonical Node",
  "reason": "smoke test"
}
```

读取规则：

```bash
POST /api/v1/knowledge/quality/corrections
{
  "workspace": "/tmp/data-service-quality-rules-check-20260430",
  "limit": 5,
  "status": "draft"
}
```

结果：

- `total_count = 1`
- `rule_type = merge`
- `status = draft`
- `proposed_value = Canonical Node`

## 下一步

- 增加规则审核动作：approve / reject / archive
- 将已批准规则接入 LLMWiki topic 合并和 GraphRAG 噪音屏蔽
- 给 MCP / Agent 增加读取待审核规则的 tool
