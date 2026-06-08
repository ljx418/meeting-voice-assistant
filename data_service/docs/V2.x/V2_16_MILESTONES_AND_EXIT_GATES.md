# V2.16 项目里程碑与出门条件

## 1. 阶段目标

V2.16 的交付目标是把本项目从“可辅助 Coding Agent 做行动规划”推进到“可作为本地 Coding Agent 审查台和安全自动化边界”。

阶段结束后，用户应能体验到：

- 看懂 provider 哪些能用、哪些不能用、为什么不能用。
- 使用更强的语义事实辅助项目理解，但不被误导为 full call graph。
- 通过 runtime profile 安全运行验证。
- 通过 Workbench v2 阅读项目状态、风险、blocker 和 evidence。
- 对大型项目获得泛化架构抽象和明确 blocker。
- 在真正修改源码前查看 patch preview、diff、rollback 和审批状态。

## 2. 里程碑总览

| 里程碑 | 对应 Phase | 交付物 | 用户可见结果 | 出门判定 |
| --- | ---: | --- | --- | --- |
| M1 | 76 | Provider Capability Registry | 用户能看到 provider 能力矩阵和不可用原因。 | provider health / config / execution 边界清楚。 |
| M2 | 77 | Semantic Provider Orchestrator | 用户能看到 symbol/reference 的 provider 来源和 confidence。 | AST baseline 可用；optional provider 不可用时结构化返回。 |
| M3 | 78 | Runtime Profile Manager | 用户能选择安全 profile 运行测试/检查，并查看诊断结果。 | 非 profile 命令 blocked；日志脱敏。 |
| M4 | 79 | Workbench v2 | 用户能用页面审查任务、证据、风险、blocker、runtime、patch readiness。 | HTML/Mermaid/JSON 一致，不引入新事实。 |
| M5 | 80 | Large-Project Abstraction Advisor | 用户能理解大项目哪些结论 accepted、哪些需要 review、哪些 blocked。 | 泛化逻辑通过，不允许 HarnessOS-only hardcoding。 |
| M6 | 81 | Human-Gated Patch Sandbox | 用户能先看 patch preview、diff、rollback，再决定是否审批 apply。 | preview 不改源码；apply 无审批必须 blocked。 |
| M7 | 82 | 最终闭环验收 | 用户拿到完整验收包和可交付结论。 | 无 open fatal / major finding；coverage 无 pending。 |

## 3. 每个里程碑的最低出门条件

### M1：Provider 能力治理出门条件

必须满足：

- `capability_registry.json` 落盘。
- 至少包含 local baseline provider 和 optional provider 的 unavailable / unsupported 示例。
- known、configured、execution_supported、available 字段不能混用。
- HTTP/MCP/CLI 返回稳定字段一致。
- public payload 不泄露 key、endpoint、raw body。

不得通过：

- provider health 被当成 execution accepted。
- unsupported provider 静默 fallback 到其他 provider。
- skipped provider-enabled test 被标记 accepted。

### M2：语义 Provider 出门条件

必须满足：

- AST provider 作为 mandatory baseline 通过真实 `data_service` E2E。
- optional provider unavailable 不阻塞系统。
- provider facts 包含 provider、extractor、confidence、evidence。
- conflict 必须进入 `needs_review`。

不得通过：

- import/reference 被写成 runtime call。
- 输出 full call graph、data flow、control flow、type inference。

### M3：Runtime Profile 出门条件

必须满足：

- `profiles.json` 落盘。
- approved profile 可在真实 `data_service` 上运行。
- non-profile command blocked。
- run artifact 包含 status、duration、exit_code、redacted logs。
- HarnessOS 或替代大项目输出 pass / fail / blocked，不伪装成功。

不得通过：

- 任意 shell command 绕过 profile。
- failed / timeout 被改写成 passed。
- 日志泄露绝对路径、secret、raw traceback。

### M4：Workbench v2 出门条件

必须满足：

- `payload.json`、`report.html`、`graph.mmd` 落盘。
- 页面展示 provider matrix、risk lanes、blocker board、runtime results、patch readiness。
- HTML/Mermaid 中每个节点能映射到 artifact id。
- blocker 和 `needs_review` 可见。

不得通过：

- 页面只展示 raw JSON。
- renderer 生成 payload 中不存在的新事实。
- 页面隐藏 major/fatal/blocker。

### M5：大项目抽象出门条件

必须满足：

- `abstraction_report.json` 落盘。
- `data_service` E2E 通过。
- HarnessOS 或替代大项目 E2E 通过，或 structured blocker 被接受。
- 输出 document claim、code fact、pattern evidence 的来源区分。
- accepted claim 有 code evidence。

不得通过：

- 为 HarnessOS 写项目专用规则。
- document-only claim 被标记为 code fact。
- blocker 只有“识别失败”，没有原因和下一步。

### M6：Patch Sandbox 出门条件

必须满足：

- preview artifact 落盘。
- diff artifact 可读。
- rollback artifact 覆盖 previewed files。
- validation profiles 与 patch preview 关联。
- apply approval state 存在。

不得通过：

- dry-run preview 修改源码。
- 没有 explicit high-risk approval 却允许 apply。
- 默认执行 git commit / push / reset / restore。

### M7：Closure 出门条件

必须满足：

- Phase 76-81 acceptance audit reports 均存在。
- focused tests 通过。
- 真实 `data_service` E2E 通过。
- HarnessOS 或替代大项目 E2E 通过，或 structured blocker 被接受。
- HTTP/MCP/CLI parity 通过。
- redaction 通过。
- full coverage matrix 所有 in-scope row 不再 pending。
- 无 open fatal / major finding。

## 4. 人工审批门槛

以下动作必须人工审批，不能由系统默认执行：

- 使用外部 provider 接收代码内容。
- 运行非默认 runtime profile。
- 修改源码。
- apply patch。
- git commit / push / reset / restore / checkout。
- 暴露 raw provider response 或 raw runtime logs。
- 把 weak inference 升级为 accepted。

## 5. 架构出门门槛

每个 Phase 必须满足：

- 新核心逻辑不进入 legacy 大文件。
- V2.16 artifact 必须写入 `coding_agent/v2_16/`。
- V2.0-V2.15 artifacts 只读消费，不静默改写。
- Workbench 只渲染 persisted payload。
- Runtime 默认拒绝。
- Patch preview 默认不修改源码。

## 6. 用户体验出门门槛

阶段完成后，用户必须能完成以下体验：

1. 打开一个项目审查页面，看懂项目状态。
2. 查看 provider 能力和不可用原因。
3. 查看任务影响、风险、证据和 blocker。
4. 安全运行 profile 并查看诊断。
5. 对大项目理解 accepted / needs_review / blocked。
6. 在改代码前查看 patch preview 和 rollback。

如果用户仍必须阅读大量 raw JSON 才能理解结果，则 Workbench v2 不得通过验收。

## 7. 假验收拒绝

以下情况一律拒绝通过：

- 只用 mock repo 验收。
- provider unavailable 写 accepted。
- optional provider skipped 写 accepted。
- import/reference 写成 runtime call。
- runtime command 绕过 profile。
- Workbench 隐藏 blocker。
- HTML/Mermaid 引入 artifact 中不存在的新事实。
- patch preview 修改源码。
- public payload 泄露绝对路径、secret、raw traceback。
- 大项目逻辑 hardcode HarnessOS。
