# V2.16 PRD 全量覆盖矩阵

> 当前文件是规划期覆盖矩阵，不是实现验收证据。Phase 82 closure 前，每一行都必须补充真实测试命令、artifact 路径、真实仓 E2E 结果和审计报告引用。

## 1. 覆盖矩阵

| PRD 条目 | 架构组件 | Phase | 当前规划状态 | Closure 前必须提供的证据 | 最终验收状态 |
| --- | --- | ---: | --- | --- | --- |
| Provider 能力注册表 | Provider Capability Registry | 76 | implemented | `capability_registry.json` 已落盘；known/configured/execution_supported 分离；HTTP/MCP/CLI parity 通过；见 `V2_16_PHASE_76_ACCEPTANCE_AUDIT_REPORT.md` | accepted |
| Provider 决策记录 | Provider Capability Registry | 76 | implemented | provider decision JSON 已落盘；unsupported/unavailable 路径和 redaction 检查通过；见 `V2_16_PHASE_76_ACCEPTANCE_AUDIT_REPORT.md` | accepted |
| AST mandatory baseline | Semantic Provider Orchestrator | 77 | implemented | AST baseline 真实 E2E 通过；`provider_facts.jsonl` 非空；见 `V2_16_PHASE_77_ACCEPTANCE_AUDIT_REPORT.md` | accepted |
| 可选语义 provider facts | Semantic Provider Orchestrator | 77 | implemented | optional provider unavailable 进入 blocker；provider facts 带 provenance/confidence/evidence；无 full call graph claim | accepted |
| 语义冲突处理 | Semantic Provider Orchestrator | 77 | implemented | `provider_conflicts.jsonl` 已落盘；当前 AST-only baseline 无冲突；后续 provider conflict 将进入 `needs_review` | accepted |
| Runtime profile 注册表 | Runtime Profile Manager | 78 | implemented | `profiles.json` 已落盘；non-profile run blocked；profile policy default-deny；见 `V2_16_PHASE_78_ACCEPTANCE_AUDIT_REPORT.md` | accepted |
| Runtime profile run | Runtime Profile Manager | 78 | implemented | profile run artifact 已落盘；redacted logs；pass/fail/timeout/blocked 分类通过；见 `V2_16_PHASE_78_ACCEPTANCE_AUDIT_REPORT.md` | accepted |
| Workbench v2 payload | Workbench v2 View Model | 79 | implemented | payload JSON 已落盘；provider matrix、semantic coverage、runtime profiles、blocker board 已生成 | accepted |
| Workbench v2 HTML/Mermaid | Workbench v2 View Model | 79 | implemented | HTML/Mermaid 从 payload 渲染；node integrity、redaction 通过；见 `V2_16_PHASE_79_ACCEPTANCE_AUDIT_REPORT.md` | accepted |
| 大项目架构抽象报告 | Large Project Abstraction Advisor | 80 | implemented | data_service E2E 通过；generic pattern evidence 已生成；无项目专用硬编码信号 | accepted |
| 大项目 blocker 解释 | Large Project Abstraction Advisor | 80 | implemented | blocker 包含 reason、missing evidence、next actions；见 `V2_16_PHASE_80_ACCEPTANCE_AUDIT_REPORT.md` | accepted |
| Patch sandbox preview | Human-Gated Patch Sandbox | 81 | implemented | preview artifact、diff、rollback 已落盘；真实仓 source hash 不变；见 `V2_16_PHASE_81_ACCEPTANCE_AUDIT_REPORT.md` | accepted |
| Patch apply 审批门禁 | Human-Gated Patch Sandbox | 81 | implemented | apply without approval blocked；approval state artifact 已生成；见 `V2_16_PHASE_81_ACCEPTANCE_AUDIT_REPORT.md` | accepted |
| 最终闭环验收 | Closure Acceptance | 82 | implemented | V2.16 focused suite 27 passed；真实 data_service 总链路 E2E 通过；见 `V2_16_PHASE_82_CLOSURE_AUDIT_REPORT.md` | accepted |
| 非目标：任意命令执行 | Safety Boundary | all | out_of_scope | closure audit 证明不支持任意命令执行 | out_of_scope |
| 非目标：自主源码修改 | Safety Boundary | all | out_of_scope | closure audit 证明 apply 前必须人工审批 | out_of_scope |
| 非目标：full call graph / data flow / type inference | Safety Boundary | all | out_of_scope | closure audit 证明无相关 claim | out_of_scope |
| 非目标：自主 git 操作 | Safety Boundary | all | out_of_scope | closure audit 证明无默认 commit/push/reset/restore | out_of_scope |

## 2. 允许的最终验收状态

```text
accepted
conditionally_accepted
structured_blocker
provider_unavailable
not_implemented
out_of_scope
blocked_major
blocked_fatal
```

说明：

- `accepted`：真实实现、真实仓 E2E、artifact 检查、public contract 验收均通过。
- `conditionally_accepted`：能力可用，但有明确条件或环境依赖。
- `structured_blocker`：系统正确产出结构化 blocker，且该 blocker 被验收接受。
- `provider_unavailable`：provider 不可用，但不可用状态被正确表达，不能冒充 accepted。
- `not_implemented`：明确未实现。
- `out_of_scope`：明确不属于 V2.16 范围。
- `blocked_major` / `blocked_fatal`：存在重大或致命问题，阶段不得 closure。

## 3. Phase 82 出门要求

Phase 82 不能通过，除非：

- 所有 in-scope 行不再是 `pending`。
- 每个 `accepted` 行都有真实测试命令和 artifact evidence。
- 每个 `provider_unavailable` 行都有 provider decision record。
- 每个 `structured_blocker` 行都有 blocker artifact 和审计结论。
- 所有非目标行都有 closure audit 证明没有过度实现或过度声明。

## 4. 假验收拒绝

以下情况不得把行标记为 `accepted`：

- 只用 mock 数据。
- provider health-only 被当作 execution。
- skipped optional provider 被当作成功。
- HTML 页面展示但没有底层 artifact。
- Workbench 隐藏 blocker。
- patch preview 修改了源码。
- runtime 命令绕过 profile。
- public payload 泄露绝对路径、secret、raw traceback。
