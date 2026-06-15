# V2.39-V2.45 PRD：大项目架构阅读、语义抽取与 Agent 上下文优化路线

## 1. 阶段定位

V2.39-V2.45 承接 V2.38 的版本化架构治理能力，目标是把项目推进为可用于大型代码库的架构阅读、架构看护、调用链路辅助和 Agent 上下文压缩平台。

本阶段不追求“完全自动恢复人类设计意图”，也不承诺完整 call graph、data flow、control flow、runtime topology 或类型推断。它追求的是：

- 用预算化扫描和分层索引支撑数十万行代码级项目。
- 用多语言 AST/LSP provider contract 扩展事实来源。
- 用 workflow/runtime extractor 识别候选工作流、运行时适配器和入口。
- 用更强的 relationship chain 帮助 Agent 快速定位相关实现。
- 用 drawio/Markdown 语义解析提升文档架构图理解质量。
- 用 token budget 和 context cache 减少重复读仓库成本。
- 用 project profile / taxonomy 管理不同项目族的术语和入口模式。
- 用 data_service、HarnessOS、codexPat 等真实项目作为持续回归集。

## 2. 背景问题

当前项目已经能生成文档驱动的架构核查报告，并能把目标架构、当前实现和差异以 evidence 方式呈现。但面对 HarnessOS 这类大型项目时仍有明显短板：

1. 扫描成本和 readback 成本仍偏高，缺少规模预算和分片产物。
2. Python 事实较强，多语言 symbol/import/reference 抽取能力不足。
3. workflow、runtime adapter、agent registry、TUI/CLI/console entrypoint 的泛化抽取不足。
4. capability 到实现链路仍以浅层 evidence 为主，对 dependency/test/reference 串联不够稳定。
5. drawio 架构图的页面、泳道、分组、边语义没有被充分利用。
6. Agent Context Pack 缺少可量化 token 节省、缓存命中和重复阅读减少指标。
7. 项目族 profile 与 taxonomy 还没有系统治理，真实项目回归也缺长期矩阵。

## 3. 目标体验

### 3.1 人类维护者

维护者导入大型项目后，可以看到：

- 项目规模和扫描预算使用情况。
- 目标架构、当前实现、差异和高风险节点。
- workflow / runtime / public entrypoint 的候选图。
- capability 到入口、handler、模块、测试的链路。
- 哪些架构图节点已经被代码事实支持，哪些只是文档声明。

### 3.2 Coding Agent

Agent 面对一个开发任务时，可以请求 task-aware context：

- 只读取和任务相关的能力、入口、模块、测试和设计约束。
- 获得 recommended reading order。
- 获得 token budget、cache hit、omitted_items。
- 在低预算下仍保留证据，不输出无证据强建议。

### 3.3 架构审计者

审计者可以比较 docs 架构图与代码事实：

- drawio page/lane/group/edge 变成 document claims。
- code facts 仍来自 AST/LSP/surface/symbol/config/test 等证据。
- supported 必须有 document evidence + code evidence。
- weak/unsupported/contradicted/needs_review 全部可见。

## 4. 范围

### 4.1 In Scope

1. 大型项目性能优化与分层索引。
2. 多语言 AST/LSP Provider Contract。
3. Workflow / Runtime Extractor v2。
4. 调用/依赖链路增强 v3。
5. drawio / 文档语义解析 v3。
6. Token Budget Optimizer + Context Cache。
7. Project Profile / Taxonomy Manager。
8. data_service / HarnessOS / codexPat 持续回归集。
9. HTTP / MCP / CLI read contracts。
10. HTML/SVG 高质量图表渲染。

### 4.2 Out of Scope

- 不声称完整恢复人类设计意图。
- 不做完整 call graph。
- 不做完整 data flow / control flow。
- 不做生产 runtime topology 推断。
- 不自动修改目标项目代码。
- 不自动重写目标项目文档。
- 不把 HarnessOS 专用路径、术语或目录写死在通用 extractor 中。

## 5. 阶段拆分

| 阶段 | 名称 | 目标 |
| --- | --- | --- |
| V2.39 | 大型项目性能优化 | budgeted scanner、scale profile、sharded artifacts、paginated readback |
| V2.40 | 多语言 AST/LSP Provider Contract | Python mandatory，TS/JS baseline，tree-sitter/LSP optional |
| V2.41 | Workflow / Runtime Extractor v2 | workflow/runtime/agent/CLI/TUI/console candidates |
| V2.42 | 调用/依赖链路增强 v3 | capability -> entrypoint -> handler -> dependency -> test/reference |
| V2.43 | drawio / 文档语义解析 v3 | page/lane/group/edge/gate/non-goal semantic claims |
| V2.44 | Token Budget Optimizer + Context Cache | token budget、cache hit、omitted_items、重复阅读减少指标 |
| V2.45 | Profile / Taxonomy + 持续回归集 | profile 配置、taxonomy 治理、真实项目回归矩阵 |

## 6. 完成定义

V2.39-V2.45 可宣布完成，当且仅当：

1. data_service、HarnessOS、codexPat 至少完成当前阶段真实 E2E，不能运行时必须 structured unavailable。
2. 大型项目 scale profile、预算状态、跳过原因和分片 readback 可见。
3. AST/LSP provider 状态区分 configured、unavailable、unsupported、failed、accepted。
4. workflow/runtime extractor 输出 candidate + evidence 或 blocker，不伪造生产运行时拓扑。
5. relationship chain 不输出禁止类型作为 accepted。
6. drawio semantic claims 与 code facts 严格分离。
7. Context Pack 输出 token estimate、cache hit、omitted_items，每条建议有 evidence 或 needs_review。
8. profile/taxonomy 可配置，no-hardcode audit 通过。
9. HTML/SVG 报告原位渲染图表，不展示 Mermaid 源码，不引入 artifact 外事实。
10. 无 open fatal / major 审计发现。

## 7. 自动化开发门禁

当前文档基线要求每个剩余子阶段在进入代码实现前必须具备三类专项文档：

```text
development plan
acceptance plan
pre-implementation audit report
```

阶段完成后必须补：

```text
acceptance audit report
```

截至当前 closure 更新：

- Phase 116 / V2.39：已完成实现与验收。
- Phase 117 / V2.40：已完成实现与验收。
- Phase 118 / V2.41：已完成实现与验收。
- Phase 119 / V2.42：已完成实现与验收。
- Phase 120 / V2.43：已完成实现与验收。
- Phase 121 / V2.44：已完成实现与验收。
- Phase 122 / V2.45：已完成实现与验收。

V2.39-V2.45 closure 不等于完整静态分析能力完成；它只接受本 PRD 范围内的大项目规模处理、多语言 provider contract、workflow/runtime candidate、浅层关系链、文档语义、token/context cache、profile/taxonomy 和真实项目回归能力。后续阶段仍不得跳过真实项目 E2E、artifact inspection、HTTP/MCP/CLI parity、PRD/spec review 和 false-green audit。
