# MCP / Agent 质量治理 Tools 阶段报告

日期：2026-04-30

## 结论

本轮完成 `data_service` MCP stdio server 的质量治理工具安全收紧版。Agent 现在不只可以通过 MCP ingest/query，也可以读取质量 summary、读取 approved correction plan、提交质量反馈、列出校正规则、执行受控审核；LLMWiki markdown 默认不由 MCP 落盘改写，approved quality plan 通过读时治理消费。

## 新增能力

- `knowledge_quality_summary`
  - 返回 `summary.json.quality`
  - 返回近期 quality feedback、correction rules、approved correction plan
- `knowledge_correction_plan`
  - 读取或重建 `workspace/quality/correction_plan.json`
  - 返回 action impact，用于判断规则影响 Graph nodes、Graph edges、LLMWiki pages
- `knowledge_quality_feedback`
  - 写入 `workspace/quality/feedback.jsonl`
  - 自动生成 draft correction rules
- `knowledge_correction_rules`
  - 支持按 `draft / approved / rejected / archived / revoked` 状态读取规则
- `knowledge_review_correction_rule`
  - 支持受控审核状态流转
  - 审核后自动刷新 approved correction plan 摘要
  - 将 approved quality plan 应用到已生成的 LLMWiki markdown 文件

## 开发意义

- Agent 可以在同一条 MCP 通道里完成“发现质量问题 -> 提交反馈 -> 审核规则 -> 读取影响范围”的闭环。
- 质量治理仍保持非破坏性：原始 `row` 不被改写，规则先进入 workspace quality 层，再由 approved plan 控制下游展示和落盘。
- MCP tool 的审核状态使用 enum 约束，降低 Agent 误写非法状态的风险。

## 验收记录

自动化验证：

```bash
python3 -m pytest backend/tests/test_data_service.py backend/tests/test_data_service_api.py backend/tests/test_data_service_mcp.py -q
```

结果：

```text
65 passed, 3 skipped
```

`3 skipped` 来自环境依赖型 MCP import skip，不影响 DataService / API 主链路。

## 下一步

- 低信号 `0 unit` source 继续观察和保守补强
- 根据真实 Agent 调用反馈继续收紧 MCP tool 输出字段
- `/knowledge` 继续补质量运营视图和图谱质量可视化
- 已按 `../harnessOS/docs/architecture/data-service-mcp-codex-handoff.md` 增加面向外部 Harness 工程的知识库生命周期 tools：workspace 创建/列出/描述/归档、source 导入/列出/停用、build 启动/状态/取消
- 所有 lifecycle tools 返回统一 envelope：`workspace_id / operation_id / status / warnings / artifact_refs / next_actions / data`
- HarnessOS 已完成 `data_service_mcp` connector ref、tool contract、lifecycle/v2/legacy tool 注册与真实 stdio MCP execution 验收；当前项目侧继续提供真实 stdio MCP tools
- 生命周期 tools 第一版优先走 stdio MCP；build start 已进入后台 operation 模式；后续如需跨进程/跨机器调用，再复用同一套 schema 增加 streamable HTTP MCP bridge
- 现有 `knowledge_query / quality` tools 已支持 `workspace_id`，外部 Harness 可用 opaque workspace id 完成查询和质量治理
- 当前验证：`python3.12 -m pytest backend/tests/test_data_service_mcp.py -q` 为 `14 passed`；外部 HarnessOS 真实 data_service MCP E2E 最终 `status=ok`、`warnings=[]`
