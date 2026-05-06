# Quality Correction Plan 阶段报告

日期：2026-04-30

## 本轮结论

本轮完成 `approved` 校正规则消费第一版。系统现在会把已批准规则转换为 `workspace/quality/correction_plan.json`，并在 Graph 快照、GraphRAG query、LLMWiki read page 读取时应用非破坏性的展示治理策略。

## 已完成

- workspace 新增 `quality/correction_plan.json`
- HTTP 新增：
  - `POST /api/v1/knowledge/quality/corrections/plan`
- `summary.json.quality.correction_plan` 新增 action 数量、action 类型分布、target engine 分布、target type 分布
- `/knowledge` 新增“生成消费计划”按钮
- `correction_plan.json` 中每条 action 新增 `impact` 字段，用于展示影响范围：
  - `graph_nodes`
  - `graph_edges`
  - `llmwiki_pages`
  - `query_hits` 预留为读时查询影响
- `/knowledge` 新增“消费计划影响范围”区域，展示每条 action 命中的节点、边和页面
- `/knowledge` 查询区域新增 filtered / rewritten / actions 计数，展示本次查询受到的治理影响
- Graph 快照读取时会消费 approved 规则：
  - `suppress`：隐藏匹配节点并移除相关边
  - `rename`：把节点展示名替换为 approved 的 proposed value
  - `merge`：把节点展示名归到 canonical value，并保留 `quality_merge_target`
- GraphRAG query 读取时会消费同一套规则：
  - suppress 节点不会进入 query hits
  - rename / merge 会同步改写 query hit title 和 snippet 的展示文本
  - `quality_plan.query_hit_impact` 会记录 `suppressed_hits / rewritten_hits`
- LLMWiki read page 读取时会消费同一套规则：
  - page title / summary / body_md 会应用 rename / merge 展示替换
  - sources / citations / backlinks 会附带展示治理结果
  - suppress 不删除页面，只标记 `quality_suppressed`
- LLMWiki ingest/compile 落盘时也会消费同一套规则：
  - rename / merge 会改写生成的 markdown 展示文本
  - suppress 会在 markdown 顶部写入 `<!-- quality_suppressed: true -->`
  - row 原始资料不被改写
- 规则回滚已接入：
  - approved 规则可置为 `revoked`
  - revoked 规则会立即从 `correction_plan.json` 移除
  - rejected / archived / revoked 规则可重新置为 `draft`
- topic 合并策略已接入：
  - approved merge 命中旧 topic/page markdown 时写入 `quality_merged_into`
  - canonical 页面追加 `Merged Topic Signals`
  - 旧页面不删除，保护已有链接

## 设计边界

- 本轮不改写 row 原始资料
- 本轮不直接重写 LLMWiki markdown 页面
- 本轮不直接重建 GraphRAG DB
- `correction_plan.json` 是可审计的治理计划，Graph 展示层先按读时策略消费

## 验证

```bash
python3 -m pytest backend/tests/test_data_service.py backend/tests/test_data_service_api.py -q
```

结果：`65 passed`

```bash
npx vite build
```

结果：通过，构建产物生成成功。

## 阶段性手工验收

1. 在 `/knowledge` 提交 `rename_suggest / merge_suggest / mark_noise` 反馈
2. 点击“生成规则”
3. 批准其中一条或多条规则
4. 点击“生成消费计划”
5. 确认 `summary.json.quality.correction_plan.action_count` 增加
6. 确认 Graph 区域显示已应用 action 数量
7. 对 `mark_noise` 规则，确认对应图节点在 Graph 预览中被隐藏
8. 对 `rename_suggest / merge_suggest` 规则，确认对应图节点展示名变为 proposed value
9. 用 GraphRAG 或 hybrid 查询同一对象，确认噪音节点不再进入 hits，rename / merge 的展示名一致
10. 打开相关 LLMWiki 页面，确认 title / body / backlink 的展示名与治理计划一致
11. 查看“消费计划影响范围”，确认 action 的 Graph nodes、Graph edges、LLMWiki pages 计数与样例列表可见
12. 运行 GraphRAG 或 hybrid 查询，确认查询卡片显示 filtered / rewritten / actions 计数
13. 重新运行 ingest/compile 后，确认相关 LLMWiki markdown 已应用 rename / merge，suppress 页面带 `quality_suppressed` 标记
14. 对 approved 规则点击撤回，确认消费计划 action 数减少且 Graph/query/page 不再消费该规则
15. 对 rejected / archived / revoked 规则重新置草稿，确认它重新进入待审核队列
16. 对 topic/page merge 规则重新运行落盘治理，确认旧页面出现 `quality_merged_into`，canonical 页面出现 `Merged Topic Signals`

## 下一步

- 精细化 MCP / Agent tools，让 Agent 可读取质量计划、影响范围并提交受控反馈
