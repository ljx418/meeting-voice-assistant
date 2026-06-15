# V2.18-V2.24 PRD：平台产品化、可维护性与生产化路线图

## 1. 阶段定位

V2.18-V2.24 是 `data_service` 在完成 V2.0-V2.17 项目智能、架构审计、Coding Agent 工具层和 HarnessOS MCP 接入特殊验收后的平台产品化阶段。

本阶段不再优先扩展单点能力，而是把已经实现的大量能力收敛成：

> 一个可发现、可操作、可验证、可维护、可生产化接入的本地项目智能平台。

## 2. 当前基础

已完成能力：

- Codebase registry、snapshot、public surface、symbols、evidence。
- DevWiki、Code Graph、Quality Governance。
- 文档资产治理、架构 claim 抽取、文档-代码对齐。
- 架构报告、Human Review Report、Architecture Context Pack。
- 大项目 pattern evidence、structured blocker、review queue。
- Coding Agent actionability、impact analysis、task plan。
- Safe patch plan、patch preview、runtime profiles、Workbench v2。
- MCP registry 当前已有大量工具，最近检查为 156 tools。
- V2.17 已确认可作为 HarnessOS 项目智能 MCP 工具层进入真实接入前试运行。

主要问题：

- 能力多，但用户入口分散。
- Artifact schema 跨阶段不够统一。
- MCP tools 数量多，外部 Agent 难以知道调用顺序。
- 大项目扫描和刷新仍偏全量。
- Optional provider 尚未形成插件生态。
- 文档和治理反馈闭环仍可加强。
- CI/test/warning/safety gate 需要生产化整理。

## 3. 产品目标

### 3.1 总目标

让用户和外部 Agent 能在一个稳定入口里完成：

```text
导入项目
  -> 查看项目状态
  -> 查找可调用工具
  -> 生成项目与任务上下文
  -> 审查证据、风险、blocker
  -> 查看 patch preview 和 runtime profile
  -> 反馈治理问题
  -> 进行增量刷新和生产化验证
```

### 3.2 阶段目标

| 阶段 | 名称 | 产品目标 |
| --- | --- | --- |
| V2.18 | Product Console & Report UX | 统一项目智能控制台，让人类可读、可操作。 |
| V2.19 | Artifact Schema & Public Contract Consolidation | 统一 artifact schema、public envelope、validator 和 contract tests。 |
| V2.20 | MCP Tool Discovery & Agent Workflow Guide | 让 Agent 知道该调用哪个工具、按什么顺序调用。 |
| V2.21 | Incremental Build & Large Repo Performance | 支持 snapshot diff 驱动的局部刷新、大项目 scan profile 和 cache invalidation。 |
| V2.22 | Provider Plugin System | 建立 provider adapter SDK，支持 AST mandatory 与 tree-sitter/Jedi/LSP optional。 |
| V2.23 | Governance Feedback Loop | 把用户反馈、correction rule、read-time overlay 做成闭环。 |
| V2.24 | Production Readiness & CI Hardening | 测试分层、warning 清理、安全门禁、发布验收。 |

## 4. 目标用户和场景

### 场景 A：开发者打开一个陌生项目

用户期望：

- 不读 raw JSON。
- 看到项目摘要、入口、风险、证据覆盖和下一步建议。
- 能直接跳转到 Context Pack、Human Report、Patch Preview。

成功标准：

- 5 分钟内理解项目主入口和当前 blocker。
- 所有关键结论有 evidence 或 needs_review。

### 场景 B：外部 Agent 想知道下一步该调用哪个 MCP tool

用户期望：

- 输入目标：项目理解 / 开发任务 / 审查 / 运行验证。
- 系统返回推荐工具序列。
- 每个工具说明前置 artifact、输出 artifact、失败原因和 next actions。

成功标准：

- Agent 不需要人工翻 156 个工具。
- 工具链调用失败时有结构化修复建议。

### 场景 C：维护者审查项目智能输出质量

用户期望：

- 对某条 finding、claim、context recommendation 或 evidence 提反馈。
- 反馈生成 correction rule。
- rule 经审核后 read-time 生效。
- 可 revoke，且不改写原始 artifact。

成功标准：

- 治理闭环可追踪。
- source artifact hash 不变。

### 场景 D：大项目重复刷新

用户期望：

- 修改少量文件后不必全量重建所有 artifacts。
- 系统说明哪些 artifact 被刷新、哪些复用、哪些失效。
- 扫描 budget、跳过文件和 blocker 清楚可见。

成功标准：

- snapshot diff 可驱动局部刷新。
- cache invalidation 有明确规则和验收。

## 5. In Scope

1. 统一 Project Intelligence Console。
2. Artifact schema 统一与 validator。
3. MCP Tool Catalog 和 Workflow Guide。
4. Snapshot diff、增量构建、cache invalidation。
5. Provider plugin SDK 与 optional provider contract。
6. Governance feedback / correction rule / overlay / revoke。
7. 测试分层、warning 清理、public contract CI。
8. 文档索引和状态治理。

## 6. Out of Scope

本阶段不做：

- 自动源码修改无审批执行。
- 自动 git commit / push。
- 任意命令执行。
- full call graph、data flow、control flow、type inference。
- 替代 IDE/LSP/Sourcegraph。
- 多租户 SaaS。
- 在线权限系统。
- HarnessOS workflow orchestration。

## 7. 成功指标

| 指标 | 目标 |
| --- | --- |
| 控制台可读性 | 用户无需 raw JSON 即可理解项目状态。 |
| Artifact contract | 主要 artifact 均有 schema_version、validator 和 contract tests。 |
| MCP 可发现性 | Agent 可通过目录工具获得推荐调用链。 |
| 增量刷新 | 修改小文件后能报告 reused/refreshed/invalidated artifacts。 |
| Provider 插件 | 未配置 provider 不 fake accepted，已配置 provider 有统一 health/execution。 |
| 治理闭环 | feedback -> rule -> review -> overlay -> revoke 可跑通。 |
| CI | 测试分层、warning 降噪、public contract guard 稳定。 |
