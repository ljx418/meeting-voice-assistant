# V2.16 差异分析：当前架构到目标架构

## 1. 基线状态

V2.16 的起点是已经验收的 V2.11-V2.15 Coding Agent Actionability 主线。

已具备能力：

- V2.11：Actionability Index、Impact Analysis、Task-to-Edit Plan。
- V2.12：Safe Patch Plan，只读补丁规划与验证建议。
- V2.13：Controlled Runtime Evidence，基于 allowlist 的受控运行证据。
- V2.14：Incremental Intelligence，snapshot diff、task memory、drift timeline。
- V2.15：Review Workbench，静态 HTML / Mermaid / JSON 审查输出。

这些能力证明系统已经可以辅助 Coding Agent 做“读项目、定范围、看风险、准备修改”。但它还没有完成更接近真实代码助手工作流的能力闭环：provider 能力治理、语义 provider 增强、profile 化运行、可读审查台、大项目抽象解释、人工门禁 patch preview。

## 2. 当前架构与目标架构差异

| 差异项 | 当前状态 | V2.16 目标状态 | 用户影响 | 风险等级 |
| --- | --- | --- | --- | --- |
| Provider 能力状态 | Phase 76 已建立统一 Provider Capability Registry 与 Provider Decision Record。 | 后续阶段消费该 registry，不再把 health-known 当作 execution-ready。 | 用户能判断 provider 是已识别、已配置、可执行，还是不可用。 | 已关闭 |
| 语义事实深度 | Phase 77 已把 AST baseline 转成 provider-attributed semantic facts；optional provider 缺失被结构化表达。 | 后续若接入 tree-sitter / Jedi / LSP，只能增强 facts，不能覆盖 AST evidence。 | 用户能看到 symbol/reference 证据来自哪个 provider。 | 已关闭 |
| Runtime 执行控制 | Phase 78 已在 allowlist command 上增加 profile registry 和 profile run。 | 后续阶段可继续扩展更复杂 profile 参数和审批，但默认仍是 deny。 | 用户知道为什么能跑、跑了什么、失败如何处理。 | 已关闭 |
| Workbench 可读性 | Phase 79 已生成 Workbench v2 payload/HTML/Mermaid，展示 provider matrix、runtime profile、semantic coverage 与 blocker board。 | 后续可继续增强交互性，但当前人类已经可用 HTML 快速审查。 | 人类不用读 raw JSON 也能理解项目状态。 | 已关闭 |
| 大项目架构抽象 | Phase 80 已生成泛用 Large-Project Abstraction Advisor，包含 generic adapters、accepted patterns 与 blocker 解释。 | 后续可扩展更多 adapter，但必须保持泛用性。 | 用户能知道系统为什么不能 accepted，以及下一步补什么证据。 | 已关闭 |
| Patch 自动化边界 | Phase 81 已生成 read-only patch preview、diff、rollback 和 approval state；apply without approval blocked。 | 真实 apply 仍需独立高风险审批，不属于默认能力。 | 用户先看 diff 和 rollback，再决定是否允许真实修改。 | 已关闭 |

## 3. 目标架构差异图

drawio 目标状态图：

```text
docs/V2.x/V2_16_TARGET_STATE.drawio
```

该 drawio 同时承担“目标状态图”和“gap 图”职责，包含：

1. 当前 vs 目标架构差异。
2. 目标架构数据流。
3. 功能模块解释。
4. 用户体验路径。
5. Phase 76-82 开发验收。
6. 里程碑与出门条件。
7. 安全门槛与停止条件。

## 4. 差异处理策略

### 4.1 Provider 差异处理

状态：Phase 76 已完成并通过验收，见 `docs/V2.x/V2_16_PHASE_76_ACCEPTANCE_AUDIT_REPORT.md`。

处理方式：

- 新增 provider registry artifact。
- health、configured、execution_supported、available 分开。
- known provider without adapter 返回 `PROVIDER_UNSUPPORTED`。
- missing key 返回 `PROVIDER_MISSING_CREDENTIAL` 或 `provider_unavailable`。

拒绝假验收：

- 不能把 health-known 写成 accepted execution。
- 不能把 skipped optional provider 写成 accepted。
- 不能泄露 key、endpoint、raw provider body。

### 4.2 语义 Provider 差异处理

状态：Phase 77 已完成并通过验收，见 `docs/V2.x/V2_16_PHASE_77_ACCEPTANCE_AUDIT_REPORT.md`。

处理方式：

- AST baseline 保持 mandatory。
- optional provider 可用则增强，不可用则结构化 unavailable。
- 每条 provider fact 必须包含 provider、extractor、confidence、evidence。
- provider conflict 必须进入 `needs_review`。

拒绝假验收：

- import/reference 不能写成 runtime call。
- 不允许输出 full call graph、data flow、control flow、type inference。

### 4.3 Runtime 差异处理

状态：Phase 78 已完成并通过验收，见 `docs/V2.x/V2_16_PHASE_78_ACCEPTANCE_AUDIT_REPORT.md`。

处理方式：

- 用 Runtime Profile Manager 替代散落 command allowlist。
- profile 定义 command template、allowed args、timeout、network、writes_source。
- run artifact 记录 passed / failed / timeout / blocked。
- stdout/stderr 只保存 redacted logs。

拒绝假验收：

- 任意命令不能绕过 profile。
- timeout / failed 不能包装成 passed。
- runtime evidence 不能覆盖 static evidence。

### 4.4 Workbench 可读性差异处理

状态：Phase 79 已完成并通过验收，见 `docs/V2.x/V2_16_PHASE_79_ACCEPTANCE_AUDIT_REPORT.md`。

处理方式：

- Workbench v2 payload 作为唯一事实源。
- HTML/Mermaid 从 persisted payload 渲染。
- 页面展示 provider matrix、risk lanes、blocker board、runtime result、patch readiness。

拒绝假验收：

- HTML 不能生成 payload 中不存在的新事实。
- blocker 和 `needs_review` 不能隐藏。
- Mermaid node 必须能映射到 artifact id。

### 4.5 大项目抽象差异处理

状态：Phase 80 已完成并通过验收，见 `docs/V2.x/V2_16_PHASE_80_ACCEPTANCE_AUDIT_REPORT.md`。

处理方式：

- 建立 generic pattern adapter catalog。
- 通过 taxonomy mapping 解释架构角色、边界、入口、工作流。
- 输出 accepted / needs_review / blocked 分类。
- blocker 必须包含 reason、missing evidence、next actions。

拒绝假验收：

- 不允许 HarnessOS-only hardcoding。
- document claim 不能伪装成 code fact。
- accepted claim 必须有 code evidence。

### 4.6 Patch Sandbox 差异处理

状态：Phase 81 已完成并通过验收，见 `docs/V2.x/V2_16_PHASE_81_ACCEPTANCE_AUDIT_REPORT.md`。

处理方式：

- 基于 safe patch plan 生成 preview。
- 生成 diff artifact 与 rollback artifact。
- 关联 validation profile。
- apply 进入 approval state machine。

拒绝假验收：

- preview 阶段不能修改源码。
- 没有人工高风险审批，apply 必须 blocked。
- git commit / push / reset / restore 不属于默认能力。

## 5. 阶段完成后的目标体验

V2.16 完成后，用户应能完成以下体验：

1. 打开项目审查台，看懂 provider、runtime、risk、blocker、evidence。
2. 输入开发任务，获得 impact、patch plan、runtime profile 和下一步建议。
3. 对大项目获得更清楚的架构抽象和 blocker 解释。
4. 在真实改代码前查看 patch preview、diff 和 rollback。
5. 把 closure report 交给另一个审计者复核。

## 6. 进入实现前的缺口

当前文档已经支撑 V2.16 总体规划，但进入每个 Phase 代码实现前仍必须补：

- Phase 专项开发计划。
- Phase 专项验收计划。
- Phase pre-implementation audit。
- 真实 `data_service` E2E 输入确认。
- HarnessOS 或替代大项目输入确认。
- optional provider 首批目标确认。
- patch apply 高风险审批边界确认。

## 7. 停止条件

出现以下情况必须停止并要求人工确认：

- 需要任意命令执行。
- 需要把代码上传给外部 provider。
- 需要未审批修改源码。
- 需要 git commit / push / reset / restore。
- 需要把 weak inference 标成 accepted。
- 需要为 HarnessOS 写项目专用逻辑。
