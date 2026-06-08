# V2.16 开发及验收计划

## 1. 阶段总览

V2.16 分为 Phase 76-82。每个子阶段必须先完成专项开发计划、专项验收计划和 pre-implementation audit；只有没有 fatal / major 规格偏差后，才能进入实现。

| Phase | 名称 | 用户可见目标 | 工程目标 |
| ---: | --- | --- | --- |
| 76 | Provider Capability Registry | 用户能看懂 provider 哪些可用、哪些只是被识别、哪些不能执行。 | 建立 provider 能力矩阵、decision record 和结构化 unavailable/unsupported 错误。 |
| 77 | Semantic Provider Orchestrator | 用户能看到更强的符号/引用证据，并知道证据来自哪个 provider。 | 在 AST baseline 上接入可选 semantic provider，并合并 provider facts。 |
| 78 | Runtime Profile Manager | 用户能选择安全 profile 跑测试/检查，并看到诊断结果。 | 从 command allowlist 升级为 profile-based runtime evidence。 |
| 79 | Workbench v2 | 用户能通过更清晰的页面审查任务、证据、风险、blocker 和导出内容。 | 生成 filterable backend payload、HTML、Mermaid 和 context export。 |
| 80 | Large-Project Abstraction Advisor | 用户能用系统审计大项目，并理解哪些结论 accepted、哪些需要 review。 | 增强 generic pattern adapters、taxonomy 和 blocker 解释。 |
| 81 | Human-Gated Patch Sandbox | 用户能先看 patch preview/diff/rollback，再决定是否批准修改。 | 生成 dry-run patch preview、diff artifact、rollback artifact 和 approval state。 |
| 82 | 最终闭环验收 | 用户拿到完整验收报告和可交付状态说明。 | 完成真实仓 E2E、接口一致性、假验收审计和覆盖矩阵。 |

## 2. 统一开发流程

每个 Phase 必须执行：

1. 专项开发计划。
2. 专项验收计划。
3. PRD / 架构规格检视。
4. pre-implementation audit。
5. 实现。
6. focused tests。
7. 真实 `data_service` E2E。
8. HarnessOS 或替代大项目 E2E。
9. artifact 磁盘检查。
10. HTTP/MCP/CLI parity。
11. public payload redaction。
12. false-green audit。
13. acceptance audit。

如果任一阶段出现以下问题，必须停止找人确认：

- 需要任意命令执行。
- 需要把代码发给外部 provider。
- 需要未审批修改源码。
- 需要 git commit / push / reset / restore。
- 需要把 weak inference 标记为 accepted。

## 3. Phase 76：Provider Capability Registry

### 开发内容

- 新增 provider capability schema。
- 新增 provider registry artifact。
- 新增 provider decision record。
- 区分：
  - `known`
  - `configured`
  - `execution_supported`
  - `available`
  - `provider_unavailable`
  - `provider_unsupported`
- 新增 HTTP/MCP/CLI read contract。

### 用户体验

用户打开 provider 页面或调用 API 后能看到：

- 哪些 provider 是 local。
- 哪些 provider 是 external。
- 哪些 provider 缺 key。
- 哪些 provider 只是 health-known，但没有 execution adapter。
- 哪些 provider 可以安全执行。
- 下一步该怎么配置。

### 验收标准

- 缺失 provider 不得算 accepted。
- known provider without adapter 必须返回 `PROVIDER_UNSUPPORTED`。
- external provider 不能泄露 endpoint、key、raw body。
- `data_service` 真实 E2E 能生成 provider matrix。
- HTTP/MCP/CLI 稳定字段一致。

## 4. Phase 77：Semantic Provider Orchestrator

### 开发内容

- AST provider 继续作为 mandatory baseline。
- 设计 optional provider interface。
- 接入 tree-sitter / LSP / Jedi 或等价 provider 的 unavailable/available 路径。
- 生成 provider facts。
- 生成 merged semantic index。
- 处理 provider conflict。

### 用户体验

用户在 actionability / workbench 中能看到：

- 某个 symbol/reference 来自 AST、tree-sitter、LSP 还是 Jedi。
- 该事实的 confidence。
- provider 是否冲突。
- 为什么某条事实只能 `needs_review`。

### 验收标准

- 没有 optional provider 时，AST baseline 仍可完整运行。
- optional provider unavailable 是结构化状态，不是失败。
- provider fact 必须有 provider、extractor、confidence、evidence。
- import/reference 不能被写成 runtime call。
- 不允许出现 full call graph / data flow / control flow / type inference claim。

## 5. Phase 78：Runtime Profile Manager

### 开发内容

- 新增 runtime profile registry。
- 新增 command template。
- 新增 profile argument validation。
- 新增 profile run artifact。
- 新增 result classification。
- 新增 redacted logs。
- 将 runtime result 关联 patch plan / evidence。

### 用户体验

用户能看到：

- 当前任务推荐哪些 runtime profile。
- 每个 profile 会执行什么命令模板。
- 该 profile 是否需要审批。
- 执行结果是 passed、failed、timeout 还是 blocked。
- 失败原因和下一步建议。

### 验收标准

- 非 profile 命令必须 blocked。
- approved profile 可在 `data_service` 上运行。
- HarnessOS 或大项目 profile 返回 pass/fail/blocker，不得伪装成功。
- runtime evidence 不覆盖 static evidence。
- logs 不泄露绝对路径、secret、raw traceback。

## 6. Phase 79：Workbench v2

### 开发内容

- 新增 workbench v2 backend payload。
- 新增 filter model：
  - status
  - risk
  - evidence coverage
  - provider
  - runtime status
  - blocker
- 新增 HTML report。
- 新增 Mermaid graph。
- 新增 reviewer export 和 agent context export。

### 用户体验

用户打开 HTML 页面能看到：

- 项目/任务摘要。
- Provider 状态矩阵。
- Impact map。
- Patch readiness。
- Runtime results。
- 风险分层视图。
- Blocker board。
- Evidence links。
- 下一步建议。

### 验收标准

- HTML/Mermaid 只能来自 persisted payload。
- 每个可见 graph node 都能解析到 artifact id。
- blocker 和 `needs_review` 必须可见。
- 不允许绝对路径或 secret 泄露。
- 人类不用读 raw JSON 也能理解当前状态。

## 7. Phase 80：Large-Project Abstraction Advisor

### 开发内容

- 增强 generic adapter catalog。
- 增强 taxonomy mapping。
- 增强 pattern evidence explanation。
- 归一化 blocker。
- 输出 large-project abstraction report。

### 用户体验

用户对 HarnessOS 或同类大项目运行审计后能看到：

- 哪些架构 claim 来自文档。
- 哪些当前事实来自代码。
- 哪些 pattern 被识别。
- 哪些部分证据不足。
- 为什么不能 accepted。
- 下一步需要补哪些证据或文档。

### 验收标准

- `data_service` E2E 通过。
- HarnessOS E2E 通过，或 blocker 比 V2.15 更精确。
- 不允许 HarnessOS-only hardcoding。
- accepted claim 必须有 code evidence。
- document-only claim 必须保持 document claim。

## 8. Phase 81：Human-Gated Patch Sandbox

### 开发内容

- 新增 patch preview artifact。
- 新增 sandbox diff artifact。
- 新增 rollback artifact。
- 新增 validation profile linkage。
- 新增 approval state machine。

### 用户体验

用户能看到：

- 这个 patch 会改哪些文件。
- diff preview。
- 为什么建议这样改。
- 应该跑哪些验证。
- 出问题如何 rollback。
- 当前是否允许 apply。

### 验收标准

- dry-run preview 不修改 source repo。
- diff artifact 可读。
- rollback scope 覆盖所有 previewed files。
- 没有 explicit high-risk approval 时 apply 必须 blocked。
- git commit / push 不属于默认验收范围。

## 9. Phase 82：最终闭环验收

### 开发内容

- 更新 coverage matrix。
- 更新 real repo E2E matrix。
- 生成 closure audit report。
- 生成 final false-green review。

### 验收标准

- 所有 focused tests 通过。
- 真实 `data_service` E2E 通过。
- HarnessOS 或替代大项目 E2E 通过或 structured blocker 被接受。
- HTTP/MCP/CLI parity 通过。
- public redaction 通过。
- 无 open fatal / major finding。
- in-scope coverage row 无 pending。

## 10. 全局假验收拒绝规则

以下情况一律不得通过：

- provider health 被当作 provider execution。
- optional provider skipped test 被当作 accepted。
- import/reference 被写成 runtime call。
- runtime command 绕过 profile 执行。
- workbench 隐藏 blocker。
- 大项目输出 hardcode HarnessOS。
- patch preview 修改源文件。
- patch apply 没有人类审批。
- public payload 泄露绝对路径、secret、raw provider body、traceback。
