# V2.31-V2.36 Task Navigation Closure Audit Report

## 1. 总结论

结论：V2.31-V2.36 Task Navigation / Coding-Agent Token Saving 主线已完成，最终状态为 `accepted_with_blockers`。

该状态表示：

- 所有 planned phase 都已实现并通过测试。
- data_service 与 HarnessOS 均完成真实仓验收。
- 大项目低证据/不可确定关系以 blocker 形式暴露。
- 没有把 blocker、heuristic relationship、missing evidence 伪装为 accepted。
- 修复后真实大项目复验确认：外部项目不再被注入 data_service MCP surfaces；无公开服务面的项目以结构化 blocker 继续完成导航、关系、impact、reading pack、handoff 和 closure。

## 2. 阶段状态

| Phase | 能力 | 状态 | 审计报告 |
| --- | --- | --- | --- |
| 97 | Task-Aware Navigation | accepted | `V2_31_PHASE_97_TASK_NAVIGATION_ACCEPTANCE_AUDIT_REPORT.md` |
| 98 | Lightweight Relationship Graph | accepted | `V2_32_PHASE_98_LIGHTWEIGHT_RELATIONSHIP_ACCEPTANCE_AUDIT_REPORT.md` |
| 99 | Change Impact & Test Selection | accepted | `V2_33_PHASE_99_CHANGE_IMPACT_TEST_SELECTION_ACCEPTANCE_AUDIT_REPORT.md` |
| 100 | Module Reading Pack & Token Ledger | accepted | `V2_34_PHASE_100_MODULE_READING_PACK_ACCEPTANCE_AUDIT_REPORT.md` |
| 101 | Copilot Agent Integration Contracts | accepted | `V2_35_PHASE_101_COPILOT_AGENT_INTEGRATION_ACCEPTANCE_AUDIT_REPORT.md` |
| 102 | Closure, UX Report & Governance | accepted_with_blockers | `V2_36_PHASE_102_CLOSURE_UX_GOVERNANCE_ACCEPTANCE_AUDIT_REPORT.md` |

## 3. 已实现能力

- 从开发任务生成 task-aware navigation candidates。
- 生成 lightweight relationship graph，但不声称 full call graph。
- 生成 change impact 和 test selection。
- 生成 module reading pack 和 token ledger，支持 token budget。
- 生成 Copilot/Codex/Claude/generic handoff。
- 生成 HTML closure report、Mermaid graph、coverage matrix、governance targets。
- HTTP/MCP/CLI 三端暴露主要能力。
- 使用真实 data_service 与 HarnessOS 验收。

## 4. 用户体验达成情况

开发者或 Coding Agent 现在可以：

1. 导入一个大型项目。
2. 生成项目事实层。
3. 输入开发任务。
4. 获取相关入口、文件、符号、测试和文档。
5. 获取压缩阅读包，减少全仓阅读和 token 消耗。
6. 获取面向 Coding Agent 的 handoff。
7. 查看最终 HTML/Mermaid 收口报告。
8. 识别 blocker 和 needs_review 项。

## 5. 明确不支持的过度能力

本阶段不支持：

- 从代码完整恢复人类设计意图。
- full call graph。
- runtime topology。
- data flow/control flow。
- type inference。
- 自动修改代码。
- 自动执行测试并提交结果。

## 6. 真实验收摘要

data_service：

- Phase 100：5 个任务 reading pack 通过。
- Phase 101：5 个任务 handoff 通过。
- Phase 102：closure report 通过，状态 `accepted_with_blockers`。

HarnessOS：

- Phase 100：3 个任务 reading pack 通过。
- Phase 101：3 个任务 handoff 通过，其中低证据任务输出 `HANDOFF_EVIDENCE_UNAVAILABLE`。
- Phase 102：closure report 通过，状态 `accepted_with_blockers`。

### 6.1 修复后大型项目复验

复验工作区：

```text
/private/tmp/data_service_v236_postfix_large_projects_rerun2
```

| 项目 | 文件数 | 状态 | surface 类型 | 关系数 | accepted 关系证据完整性 |
| --- | ---: | --- | --- | ---: | --- |
| data_service | 1074 | accepted_with_blockers | cli/http/mcp/frontend/api_client | 9143 | 9053 accepted，缺 line/evidence/path = 0/0/0 |
| HarnessOS | 2676 | accepted_with_blockers | 无确定性 public surface | 10363 | 10196 accepted，缺 line/evidence/path = 0/0/0 |
| codexPat | 998 | accepted_with_blockers | 无确定性 public surface | 73 | 73 accepted，缺 line/evidence/path = 0/0/0 |

复验结论：

- data_service MCP surface count 为 197，与 `all_tool_specs()` 契约一致。
- HarnessOS 和 codexPat 的 `surface_types` 为空，没有再注入 data_service 的 `knowledge_*` MCP tools。
- HarnessOS/codexPat 在缺少确定性 public surface 时仍完成 task navigation、relationship graph、impact、reading pack、handoff 和 closure。
- 缺少公开入口事实以 `TASK_NAVIGATION_PUBLIC_SURFACES_UNAVAILABLE`、`RELATIONSHIP_PUBLIC_SURFACES_UNAVAILABLE`、`RELATIONSHIP_SURFACE_MAPPINGS_UNAVAILABLE` blocker 暴露，不伪装为 accepted surface。
- 三个项目均生成架构意图 HTML/Mermaid、任务导航 HTML/Mermaid、项目架构概览 HTML/Mermaid。

## 7. 测试摘要

修复后最终回归：

```text
13 passed
```

公共合同：

```text
3 passed
```

补充 targeted 回归：

```text
7 passed
```

覆盖 no-surface 外部项目、MCP inventory 不注入当前 registry、relationship accepted evidence 完整性和 reading pack cache key。

## 8. Open Findings

无 fatal 或 major finding。

Minor：

- 大仓 low-evidence blocker 数量仍高，需要后续阶段继续优化证据覆盖、报告可读性和关系解释。
- closure HTML 是审计摘要，不是完整交互式前端。

## 9. 最终判定

V2.31-V2.36 可以收口。

最终验收状态：

```text
accepted_with_blockers
```
