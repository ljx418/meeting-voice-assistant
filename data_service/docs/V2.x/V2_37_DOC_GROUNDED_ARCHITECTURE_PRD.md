# V2.37 PRD：文档驱动架构重塑与事实核查

## 1. 阶段定位

V2.37 是 Project Intelligence 在 V2.31-V2.36 task navigation 之后的架构理解增强阶段。

它解决的问题不是“从代码自动恢复完整人类设计意图”，而是：

```text
从项目 docs 重塑目标架构；
从代码 artifacts 抽取当前事实；
用双边 evidence 核查二者是否一致；
把 supported / weakly_supported / unsupported / contradicted / code_not_documented 清楚呈现给人和 Agent。
```

HarnessOS 是本阶段的重要真实验收样例，但不是专用规则来源。实现必须适用于 data_service、HarnessOS、codexPat、research-notebook 等不同形态项目。

## 2. 背景与当前缺口

当前 V2.31-V2.36 已能完成：

- 大型项目 snapshot、inventory、symbol、relationship、impact、reading pack、handoff。
- 对 HTTP/MCP/CLI 项目生成较稳定的任务导航。
- 对无 public surface 项目继续生成结构化 blocker，而不伪造入口。

但当前 HTML 架构图仍偏事实枚举：

- 目录、surface、relationship count 能展示。
- 不能稳定说明“系统为什么这样拆”。
- 不能把 docs 中的目标架构图、PRD、gap analysis 与代码事实做强核查。
- 对 HarnessOS 这种 workflow/runtime/agent 项目，不能可靠还原设计层次、运行平面和关键链路。

## 3. 用户目标

### 3.1 维护者

希望快速回答：

- 当前项目目标架构是什么？
- 目标架构哪些部分有代码证据？
- 哪些设计声明没有实现证据？
- 哪些代码事实没有文档描述？
- 架构图、PRD、gap 文档是否过期或互相矛盾？

### 3.2 Coding Agent / Copilot 类 Agent

希望在开发前获得：

- 当前任务相关的目标架构声明。
- 当前实现中支撑这些声明的文件、符号、入口、测试。
- 哪些部分可以信任，哪些需要人工确认。
- 不必全仓阅读即可获得架构上下文。

### 3.3 架构审计者

希望查看：

- target architecture from docs
- current architecture from code facts
- diff / drift / needs_review
- evidence trail
- blocker reason

## 4. In Scope

1. Document Authority Registry v2
   - 识别 PRD、target architecture、gap analysis、drawio、audit、acceptance、README、handoff summary。
   - 建立 authority_role、authority_level、phase/version、stale/superseded 关系。

2. Architecture Claim Graph v2
   - 从 Markdown、drawio、表格、列表、验收门槛、non-goals 中抽取架构声明。
   - 支持 claim 类型：plane、layer、component、workflow、agent、runtime、adapter、artifact、storage、governance、public_interface、quality_gate、non_goal。

3. Project Term Taxonomy
   - 支持项目词表映射，但不写死项目。
   - 示例：`station -> agent_role`、`mission -> workflow`、`runtime_adapter -> adapter`。

4. Current Implementation Model
   - 消费 V2.0-V2.36 artifacts，不重扫已有事实。
   - 汇总当前代码事实：entrypoints、surfaces、symbols、imports、relationships、tests、configs、task navigation、blockers。

5. Claim-to-Code Verification
   - 文档声明与代码事实双边 evidence 对齐。
   - 输出 supported、weakly_supported、unsupported、contradicted、code_not_documented。

6. Architecture Reconstruction Report v2
   - 生成 target/current/diff/needs_review 四视图。
   - 生成 HTML + Mermaid，不展示源码，不引入未持久化事实。

7. Agent Architecture Brief
   - 面向 Coding Agent 输出可压缩架构上下文。
   - 每条建议必须有 evidence 或 needs_review。

8. HTTP/MCP/CLI read contracts
   - 支持 build/read/list/report。
   - 三端 stable fields 一致。

## 5. Out of Scope

- 不从代码完整恢复人类设计意图。
- 不声称 full call graph、data flow、control flow、type inference、runtime topology。
- 不自动修改目标项目代码。
- 不自动重写项目文档。
- 不把 drawio 节点当成 code-derived fact。
- 不把 token overlap 当作 accepted implementation proof。
- 不把 HarnessOS 专用概念硬编码为通用规则。

## 6. 核心用户故事

### US-3701：从 docs 重塑目标架构

作为维护者，我希望服务读取项目 docs，生成目标架构模型，以便理解项目设计意图。

验收：

- 输出 target architecture model。
- 每个节点/边都有 document evidence。
- stale / historical docs 不得作为当前目标架构主来源。

### US-3702：从代码事实生成当前实现模型

作为 Coding Agent，我希望服务生成 current implementation model，以便不全仓阅读也能理解当前代码结构。

验收：

- 输出 current implementation model。
- 节点来自 V2 artifacts。
- 每个 accepted code fact 有 repo-relative path、line_range 或 artifact ref。

### US-3703：文档-代码事实核查

作为架构审计者，我希望服务核查每条架构声明是否有代码证据。

验收：

- 每条 claim 输出 verification_status。
- supported 必须有 document evidence + code evidence。
- weakly_supported / unsupported 必须可见。

### US-3704：生成可读架构报告

作为人类用户，我希望看到图而不是源码，以便快速理解项目。

验收：

- HTML 原位渲染 Mermaid/SVG。
- 展示 target/current/diff/needs_review。
- 不展示 Mermaid 源码块。

### US-3705：用于 Agent 开发上下文

作为 Coding Agent，我希望得到架构 brief，以便知道任务应该在哪些模块内修改，哪些设计约束不能破坏。

验收：

- 输出 role-aware architecture brief。
- 每条 recommendation 有 evidence 或 needs_review。
- 小 token budget 下不得保留无证据建议。

## 7. 成功指标

- data_service、HarnessOS、codexPat 至少 3 个真实项目跑通。
- HarnessOS 目标架构可以从 docs 重塑为 target model。
- HarnessOS 当前实现可以从 code facts 重塑为 current model。
- 至少 10 条 HarnessOS 架构 claim 完成 supported / weak / unsupported 分类。
- HTML 报告能让人类在 5 分钟内看懂目标架构、当前实现和主要差异。
- 无 accepted row 缺 document evidence 或 code evidence。

## 8. 完成定义

V2.37 完成时，必须满足：

1. 所有 Phase 103-108 完成。
2. data_service、HarnessOS、codexPat 真实 E2E 通过。
3. 无 open fatal / major 文档或实现偏差。
4. 不存在 HarnessOS 专用硬编码。
5. 输出 HTML 可读报告、Mermaid 图、JSON artifacts、Agent brief。
6. 全量 backend 测试通过。
7. Coverage matrix 每个 accepted row 有真实证据。
