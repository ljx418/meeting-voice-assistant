# Quality Rule Review 阶段报告

日期：2026-04-30

## 结论

本轮完成质量校正规则审核动作第一版。`quality/correction_rules.json` 中的规则现在可以从 `draft` 进入 `approved / rejected / archived`，并记录 reviewer、review_note、reviewed_at。系统仍不自动改写 LLMWiki、GraphRAG 或 row 原始资料；`approved` 规则只是进入后续规则消费阶段。

## 新增能力

- HTTP API 新增：
  - `POST /api/v1/knowledge/quality/corrections/review`
- 支持规则状态：
  - `draft`
  - `approved`
  - `rejected`
  - `archived`
- 重新执行 `corrections/build` 时会按 `source_feedback_id` 保留既有审核状态和审核备注
- `/knowledge` 待审核规则列表新增：
  - 批准
  - 拒绝
  - 归档
- `summary.json.quality.correction_rules.status_counts` 可展示审核后的状态分布

## 自动化验收

```bash
python3 -m pytest backend/tests/test_data_service.py backend/tests/test_data_service_api.py -q
```

结果：

- `58 passed`

前端打包验证：

```bash
npx vite build
```

结果：

- Vite build passed

## 手工验收标准

打开 `/knowledge`：

- 提交 `rename_suggest / merge_suggest / mark_noise / needs_review` 反馈
- 点击“生成规则”
- “待审核规则”列表出现 draft 规则
- 点击“批准”后，该规则状态变为 `approved`
- 点击“拒绝”后，该规则状态变为 `rejected`
- 点击“归档”后，该规则状态变为 `archived`
- 再次点击“生成规则”，已审核状态不会被重置回 `draft`
- `summary.json.quality.correction_rules.status_counts` 与界面计数一致

## 下一步

- 只消费 `approved` 规则
- 将 `approved rename / merge / suppress` 接入 LLMWiki topic 合并和 GraphRAG 噪音屏蔽
- 增加 MCP / Agent 读取待审核规则与已批准规则的工具
