# V2.38 PRD：版本化架构核查与增量 Agent 上下文服务

## 1. 阶段定位

V2.38 承接 V2.37 的“文档驱动架构核查”能力，目标是把项目推进为面向人类和 Coding Agent 的架构治理服务：

```text
代码 + 文档 + 版本变化 = 可追踪、可更新、可审计的架构理解模型。
```

V2.38 不声称“完全理解复杂项目的一切设计意图”，而是提供可验证的能力：

- 帮助人类快速阅读大型项目架构。
- 帮助 Agent 快速定位能力入口、调用/依赖链路、相关模块和测试。
- 对架构设计文档与代码实现进行双向核查。
- 在代码或文档变更后增量更新项目理解，减少重复读仓库导致的 token 消耗。

## 2. 当前剩余缺口

V2.37 已经完成：

- Document Authority Registry v2。
- Architecture Claim Graph v2。
- Current Implementation Model。
- Claim-to-Code Verification。
- HTML 报告与 Agent Brief。

仍未完整实现：

1. 大型项目增量理解：代码变更后只更新受影响架构节点和上下文包。
2. 调用链/依赖链增强：从 capability 到 surface、handler、module、test 的可信链路仍不够稳定。
3. 架构图与代码事实双向核查增强：drawio / Markdown claim 与代码实现的匹配策略仍偏基础。
4. Agent token 成本治理：缺少任务级阅读预算、缓存命中、重复阅读减少指标。
5. 架构版本治理：缺少跨 snapshot 的 target/current/diff 演进视图。
6. 多项目泛化：HarnessOS 可作为验收样例，但不能成为硬编码 profile。
7. 大型项目性能优化：数十万行代码级项目需要 scan budget、分层索引、缓存、分片 readback 和超时降级。
8. 多语言 AST/LSP：Python AST 已较成熟，但 TS/JS/Go/Rust/Java 等语言仍缺统一 provider contract；LSP/tree-sitter 仍应是可选增强。
9. workflow/runtime extractor：需要更通用地识别 workflow manifest、runtime adapter、agent registry、TUI/CLI/console entrypoint，而不是只适配某个仓库。
10. drawio/文档语义解析：当前图节点抽取偏标签级，需要识别页面语义、泳道、分组、边含义、验收门槛和禁用声明。
11. project profile / taxonomy 管理：需要为不同项目族配置术语、入口模式、边界规则和验收基线，同时避免把 HarnessOS 写死进通用逻辑。
12. 真实大型项目持续回归集：需要把 data_service、HarnessOS、codexPat 等作为长期回归样例，持续验证泛化能力。

## 3. 目标用户

- 维护者 / Tech Lead：审查项目是否偏离目标架构。
- Coding Agent：快速获得任务相关的模块、链路、约束和测试建议。
- 文档 Agent：检查架构文档是否过期、缺证据或与代码冲突。
- 新开发者：通过图表和阅读路径理解大型项目。

## 4. 核心用户故事

### US-001：人类快速理解大型项目

用户导入 HarnessOS 这类大型项目后，希望看到目标架构、当前实现、关键能力入口、调用/依赖链路、偏差与风险，而不是只看到文件枚举。

验收：

- HTML 报告包含系统总览图、能力入口图、目标/当前/差异图。
- 每个关键节点可追踪到文档证据或代码证据。
- 不把低置信推断渲染成确定事实。

### US-002：Agent 修复 bug 前获得上下文

Agent 输入任务，例如“修复 workflow executor 的 fan-in bug”，服务返回：

- 任务相关 capability。
- 入口 surface / handler。
- 相关模块、测试、配置。
- 相关架构 claim 和设计约束。
- 需要避免破坏的边界。
- 建议执行命令。

验收：

- Context Pack 不包含无证据强建议。
- 小 token budget 下删除低优先级内容，而不是保留建议后删除证据。
- 输出包含 omitted_items 和 token estimate。

### US-003：代码更新后增量更新理解

用户修改代码后，服务基于 git diff / snapshot diff 计算受影响模块与架构节点。

验收：

- 输出 impacted files / symbols / capabilities / claims / tests。
- 未受影响的 cached artifacts 不重建。
- stale report 能明确指出哪些理解需要刷新。

### US-004：架构设计与实现双向审计

用户希望知道：

- 文档里声明的架构是否有代码实现。
- 代码中存在的能力是否有文档说明。
- 哪些地方设计与实现冲突。

验收：

- supported 必须有 document evidence + code evidence。
- code_not_documented 必须可见。
- contradicted / unsupported 不得被隐藏。

## 5. V2.38 In Scope

1. Architecture Version Index。
2. Incremental Architecture Impact Analyzer。
3. Capability-to-Implementation Chain v2。
4. Document-Code Verification v3。
5. Architecture Context Pack v5。
6. Human Architecture Report v3。
7. Token Budget and Cache Metrics。
8. HTTP / MCP / CLI read contracts。
9. data_service + HarnessOS + codexPat 真实项目 E2E。

## 6. V2.38 Out of Scope

- 不声称完整恢复人类设计意图。
- 不做完整 call graph。
- 不做完整 data flow / control flow。
- 不做 runtime trace，除非后续阶段显式加入运行时观测。
- 不自动修改目标项目代码。
- 不自动重写目标项目文档。
- 不将 HarnessOS 专用术语硬编码为通用规则。

## 7. 成功定义

V2.38 可宣布完成，当且仅当：

1. 三个真实项目可生成架构核查报告。
2. 至少一个大型项目可生成任务级 Architecture Context Pack。
3. 代码变更可产生增量影响分析。
4. capability -> surface -> handler/module -> test 链路具备 evidence。
5. target/current/diff 报告可读，且图表原位渲染。
6. token budget / cache / omitted_items 指标可见。
7. 所有 accepted/supported 结论都有证据。
8. 无 open fatal / major 审计发现。

## 8. 后续路线纳入范围

V2.38 作为当前收口阶段，解决版本化架构核查、增量影响分析、能力链路、人类报告和 Agent 上下文压缩。以下能力纳入 V2.38 之后的连续路线图，不要求 V2.38 一次性完成：

| 阶段 | 目标 | 关键验收 |
| --- | --- | --- |
| V2.39 | 大型项目性能与分层索引 | 20 万行级样例可在预算内生成 profile；超时/过大文件 structured blocker；缓存命中率可见 |
| V2.40 | 多语言 AST/LSP Provider Contract | AST provider mandatory；tree-sitter/LSP optional unavailable unless configured；至少 Python + TS/JS fixture 通过 |
| V2.41 | Workflow / Runtime Extractor v2 | 识别 workflow manifest、runtime adapter、agent registry、CLI/TUI/console entrypoint；不声称生产运行时拓扑 |
| V2.42 | 调用/依赖链路增强 v3 | capability -> entrypoint -> handler -> dependency -> test 链路更稳定；heuristic 与 deterministic 分离 |
| V2.43 | drawio / 文档语义解析 v3 | 抽取 page/lane/group/edge semantics、acceptance gate、non-goal；drawio claim 不直接变 code fact |
| V2.44 | Token Budget Optimizer + Context Cache | 任务级阅读预算、缓存命中、重复阅读减少指标、omitted_items 与 evidence 保持一致 |
| V2.45 | Project Profile / Taxonomy + 大型项目回归集 | profile 可配置、不可硬编码 HarnessOS；data_service/HarnessOS/codexPat 持续回归矩阵通过 |

这些阶段共同服务同一个长期目标：让本项目成为面向人类与 Copilot 类 Agent 的项目阅读、架构看护、调用关系管理和低 token 成本上下文服务。
