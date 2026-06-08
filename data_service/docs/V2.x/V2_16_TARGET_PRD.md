# V2.16 目标 PRD：Coding Agent 能力补全与自动化安全边界

## 1. 阶段定位

V2.16 是在已验收的 V2.11-V2.15 Coding Agent Actionability 基础上，继续补齐“真正可给代码助手使用”的工程闭环。

当前系统已经能做到：

- 导入项目并生成项目事实。
- 抽取代码符号、公开服务面、文档声明和架构证据。
- 生成 actionability index、impact analysis、task plan。
- 生成只读 safe patch plan。
- 执行 allowlist-only 的受控运行证据。
- 维护 snapshot diff、task memory 和 drift timeline。
- 生成静态 HTML / Mermaid / JSON workbench。

但是，从一个真实 Coding Agent 的角度看，仍有几个短板：

1. 可选 provider 状态分散，用户很难判断“这个 provider 只是被识别了，还是能真的执行”。
2. AST baseline 能用，但对多语言、大项目和复杂引用关系的理解仍浅。
3. runtime evidence 目前只有 allowlist command，缺少更清晰的 profile、审批和诊断层。
4. workbench 可读性有限，更像技术报告，不像人类审查台。
5. HarnessOS 等大项目仍有大量 `needs_review`，需要更泛化的架构抽象和 blocker 解释。
6. patch plan 仍是只读建议；如果未来要真正尝试补丁，必须先有 sandbox preview、diff、rollback 和人工审批门禁。

V2.16 的目标不是让系统自动改代码，而是：

> 让本项目成为一个更安全、更可解释、更接近真实 Coding Agent 工作流的本地项目智能与审查平台。

## 1.1 阶段结束后的目标体验

V2.16 完成后，用户打开本项目时，目标体验应从“读一堆 artifact 文件”升级为“使用一个本地 Coding Agent 审查台”。

用户应该能完成以下连续路径：

```text
导入项目
  -> 打开项目审查台
  -> 查看 provider 能力边界
  -> 输入开发任务
  -> 查看影响范围、证据、风险和 blocker
  -> 选择受控 runtime profile 验证
  -> 查看大项目架构抽象或 patch preview
  -> 决定是否人工批准下一步高风险动作
```

该体验必须满足：

- 用户能看懂，而不是只能机器读。
- 关键结论有证据，而不是只给总结。
- blocker 显式展示，而不是隐藏在日志里。
- 高风险动作默认 blocked，而不是自动执行。
- 大项目输出解释“为什么不能 accepted”，而不是假装理解。

## 2. 目标用户

| 用户 | 目标 |
| --- | --- |
| Coding Agent | 在动手修改前拿到可执行的任务计划、证据、风险、测试建议和 patch preview。 |
| 项目维护者 | 快速判断某个改动会影响哪些能力、模块、测试和文档。 |
| 代码审查者 | 用 workbench 查看证据链、风险、runtime 结果和 blocker。 |
| 架构审查者 | 对大项目做架构抽象、文档/代码差异分析和风险定位。 |
| 文档 Agent | 根据事实和 evidence 生成更可靠的开发说明、审计报告和迁移建议。 |
| 本地操作者 | 审批高风险动作，例如外部 provider、非默认 runtime profile、patch apply、git 操作。 |

## 3. 用户能拿本项目做什么

### 场景 A：接手陌生项目

用户输入一个本地 repo 路径，系统输出：

- 当前项目有哪些公开能力。
- 入口文件、核心模块、测试和文档在哪里。
- 哪些结论来自代码事实，哪些来自文档声明。
- 哪些部分证据不足，需要 review。
- 可视化 workbench，包含架构图、风险 lane、blocker 和 evidence 链接。

用户体验目标：

> 新开发者不用全仓乱搜，可以先通过本系统获得一个可验证的项目地图。

用户验收样例：

```text
用户问题：这个项目有哪些公开入口？代码资产导入能力在哪里？
期望输出：能力摘要、HTTP/MCP/CLI 入口、handler、文件、line range、证据链接、needs_review。
```

### 场景 B：让 Coding Agent 准备一个改动

用户输入任务，例如：

```text
给 codebase import 增加一个新的校验逻辑，并同步 HTTP/MCP/CLI。
```

系统输出：

- impact analysis：可能受影响的文件、符号、API、MCP tool、CLI command。
- task plan：建议先读哪些代码、参考哪些模式。
- safe patch plan：候选编辑区域、patch options、validation plan、rollback plan。
- runtime profile：哪些测试/检查可以安全运行。
- workbench export：可放进 Coding Agent 上下文的压缩包。

用户体验目标：

> Agent 修改前先拿到结构化证据和风险，不再只靠 grep 和直觉。

用户验收样例：

```text
用户任务：给 codebase import 增加路径校验，并同步 HTTP/MCP/CLI。
期望输出：候选文件、相关 public surface、相关测试、patch options、runtime profiles、rollback 建议。
```

### 场景 C：审查一次改动风险

用户选择一个 patch plan 或任务，系统输出：

- 改动涉及哪些能力和公共入口。
- 哪些测试与候选修改相关。
- runtime evidence 是 passed、failed、timeout 还是 blocked。
- 哪些建议证据不足。
- 哪些 blocker 必须人工处理。

用户体验目标：

> 维护者可以把系统当作“改动前审查台”，快速判断是否能继续。

用户验收样例：

```text
用户问题：这个 patch plan 是否可以推进？
期望输出：risk lanes、runtime result、failed/blocked 原因、必须人工处理的 blocker。
```

### 场景 D：审计 HarnessOS 这类大型项目

系统对大项目输出：

- 当前抽到的代码事实。
- 文档架构声明。
- 泛化 pattern evidence。
- 目标架构 vs 当前代码事实的差异。
- 为什么某些架构抽象无法 accepted。
- 更精确的 blocker，而不是一句“无法识别”。

用户体验目标：

> 系统可以解释“大项目为什么难识别”，并给出下一步补证据的路线。

用户验收样例：

```text
用户问题：HarnessOS 的目标架构和当前代码事实差在哪里？
期望输出：document claim、code fact、pattern evidence、accepted/needs_review/blocked 分类、缺失证据。
```

### 场景 E：未来尝试补丁预览

系统不会直接改代码，而是先生成：

- patch sandbox preview。
- diff artifact。
- rollback artifact。
- validation profile。
- apply approval state。

用户体验目标：

> 用户先看 diff 和 rollback，再决定是否批准真正修改源码。

用户验收样例：

```text
用户操作：生成 patch preview。
期望输出：diff artifact、rollback artifact、validation profile、apply_status=blocked、reason=human approval required。
```

## 4. V2.16 功能范围

### 4.1 Provider 能力治理

要解决的问题：

- 用户不知道 provider 是“被识别了”还是“能执行”。
- cloud/local provider 的安全边界不清。
- provider unavailable 容易被误写成 accepted。

目标能力：

- Provider Capability Registry。
- Provider Decision Record。
- health / configured / execution_supported 分离。
- provider unavailable / unsupported / auth failed / timeout 等结构化错误。
- public payload 自动脱敏。

验收重点：

- provider health 不能算执行成功。
- 没有 adapter 的 provider 必须返回 `PROVIDER_UNSUPPORTED`。
- 没有 key 的 provider 必须返回 `PROVIDER_MISSING_CREDENTIAL` 或 `provider_unavailable`。

### 4.2 可选语义 Provider 增强

要解决的问题：

- 当前 AST baseline 对多语言和复杂项目理解有限。
- 但系统不能因此过度承诺 full call graph。

目标能力：

- Python AST 继续作为 mandatory baseline。
- tree-sitter / LSP / Jedi 等作为 optional provider。
- provider fact 必须包含 provider、extractor、confidence、evidence。
- provider 之间冲突时进入 `needs_review`。

验收重点：

- 没有 optional provider 时系统仍可运行。
- optional provider unavailable 不算失败。
- import/reference 不能被升级成 runtime call。

### 4.3 Runtime Profile Manager

要解决的问题：

- V2.13 只有 allowlist command，粒度还不够。
- 用户需要知道“这条命令为什么允许跑、跑了什么、结果怎样”。

目标能力：

- runtime profile registry。
- command template approval。
- profile run artifact。
- result classification：passed / failed / timeout / blocked。
- redacted logs。
- patch plan / evidence linkage。

验收重点：

- 非 profile 命令 blocked。
- profile run 不泄露绝对路径、secret、raw traceback。
- runtime evidence 不覆盖 static evidence。

### 4.4 Workbench v2

要解决的问题：

- 当前 HTML/Mermaid 可用，但不够像审查产品。
- 用户需要更直观地看项目状态、风险和证据。

目标能力：

- filterable backend payload。
- 风险 lane。
- blocker board。
- evidence navigation。
- capability / surface / symbol / runtime / diff 关联视图。
- reviewer export 和 agent context export。

验收重点：

- 所有可见节点都来自 persisted artifacts。
- HTML/Mermaid 不引入新事实。
- blocker 和 `needs_review` 必须可见。

### 4.5 大项目架构抽象增强

要解决的问题：

- HarnessOS 类项目结构复杂，代码事实和设计文档之间存在抽象差。
- 系统需要解释“为什么不能 accepted”，而不是假装理解。

目标能力：

- generic adapter catalog。
- configurable taxonomy。
- architecture blocker normalization。
- document claim / code fact / pattern evidence 的三方解释。
- 大项目 report 中清楚标注 accepted、needs_review、blocked。

验收重点：

- 不允许 HarnessOS-only hardcoding。
- 至少用 `data_service` + HarnessOS 或替代大项目做 E2E。
- accepted claim 必须有代码 evidence。

### 4.6 Human-Gated Patch Sandbox

要解决的问题：

- 当前 patch plan 只能建议，不能安全生成预览 diff。
- 如果未来进入自动补丁，必须先有强安全门禁。

目标能力：

- patch preview artifact。
- sandbox diff artifact。
- rollback artifact。
- validation profile linkage。
- approval state machine。

验收重点：

- preview 阶段不修改源码。
- apply 没有人类高风险审批必须 blocked。
- git commit / push / reset / restore 全部不在默认范围内。

## 5. 非目标

V2.16 不做：

- 无审批自动修改源码。
- 自动 git commit 或 push。
- 任意命令执行。
- full call graph。
- data flow。
- control flow。
- type inference。
- runtime topology inference。
- 未配置外部 provider 调用。
- 未经允许把代码发给外部服务。

## 6. 完成定义

V2.16 完成必须满足：

1. Provider 能力状态可查询、可解释、不可假验收。
2. Semantic provider 输出有 provenance、confidence 和 evidence。
3. Runtime profile 默认拒绝，只有审批 profile 可执行。
4. Workbench v2 可读性显著提升，能面向人类审查。
5. 大项目输出能给出 accepted / needs_review / blocker 的清晰解释。
6. Patch sandbox 只生成 preview/diff/rollback，不经审批不改源码。
7. HTTP/MCP/CLI 三端合同一致。
8. 真实 `data_service` 和大项目 E2E 通过或结构化 blocker 可信。
9. 无 open fatal / major finding。
