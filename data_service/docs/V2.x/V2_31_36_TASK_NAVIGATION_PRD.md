# V2.31-V2.36 PRD：任务感知代码导航、轻量影响关系与 Agent Token 节流

## 1. 阶段定位

V2.31-V2.36 接续已验收的 V2.25-V2.30 Architecture Intent 公共合同。前序阶段已经能导入项目、构建代码事实、生成架构意图报告、验证架构图与代码事实，并通过 HTTP/MCP/CLI 对外暴露。当前阶段的目标不是继续扩大“架构图展示”，而是把这些事实变成 Copilot 类 Coding Agent 可直接使用的任务导航能力。

本阶段核心定位：

```text
从“项目能被解释”推进到“开发任务能被节流、导航、影响分析和交付给 Agent”。
```

它要解决的真实问题：

- 大项目中，Coding Agent 反复全仓搜索，重复读取同一批文件，消耗大量 token。
- 当前 Context Pack 能给出开发上下文，但还不够严格地区分必读、选读、可跳过。
- 当前关系层避免了 full call graph 伪承诺，但缺少可管理的轻量调用、引用、handler、test 影响关系。
- 当前测试建议偏人工经验，需要从 surface、symbol、relationship、history artifact 中形成可解释推荐。
- 当前 MCP/HTTP/CLI 更偏报告读取，需要面向 Agent IDE / Copilot 的任务级调用合同。

## 2. 产品目标

V2.31-V2.36 完成后，用户或外部 Coding Agent 可以输入一个开发任务，例如：

```text
我要新增一个 MCP tool，并同步 HTTP API、CLI 命令和测试。
```

系统应返回：

- 任务解释、任务类型和相关 capability。
- 最小必读文件、符号、public surface、测试和文档。
- 轻量调用、引用、handler dispatch、registry、config、test relationship。
- 影响分析：可能受影响的模块、接口、测试、文档、架构边界。
- Token 预算账本：included、optional、omitted、reason、evidence-retained。
- 推荐开发顺序、验证命令、风险和 blocker。
- 可由 MCP/HTTP/CLI 稳定调用的结构化结果。

## 3. 目标用户与体验

| 用户 | 目标体验 |
| --- | --- |
| Coding Agent | 不全仓阅读，直接拿到任务相关最小上下文和下一步动作。 |
| 维护者 | 看清一个改动会影响哪些 public surface、模块、测试和文档。 |
| Review Agent | 用影响图和 evidence 快速判断 patch 风险。 |
| 架构看护者 | 发现任务是否绕过既有架构边界或复用模式。 |
| 新成员 | 通过任务导航理解项目，而不是先阅读全部仓库。 |

## 4. In Scope

- Task-Aware Code Navigation Index。
- Lightweight Call / Reference / Impact Graph。
- Change Impact Analysis。
- Test Recommendation。
- Module Reading Pack。
- Token Budget Ledger。
- Reuse Pattern Recommendation。
- Architecture Guardrail Check。
- Copilot Agent MCP/HTTP/CLI task APIs。
- data_service 与 HarnessOS 真实仓库 E2E。
- HTML/Mermaid 用户验收报告。

## 5. Out of Scope

- 完整调用图。
- 数据流、控制流、类型推断。
- 生产运行时拓扑恢复。
- 自动修改代码。
- 自动提交 PR。
- 无 evidence 的 LLM-only 开发建议。
- 把 import dependency、token overlap、heuristic relation 当成 runtime call。
- 为 HarnessOS 特化规则，牺牲通用项目能力。

## 6. 阶段拆分

| 阶段 | 名称 | 目标 |
| --- | --- | --- |
| V2.31 / Phase 97 | Task-Aware Navigation Index | 建立任务导航索引，支持 task -> capability/surface/symbol/test/doc 的相关性检索。 |
| V2.32 / Phase 98 | Lightweight Call & Impact Graph | 建立轻量调用、引用、导入、handler dispatch、registry、test 关系层，并标注语义边界。 |
| V2.33 / Phase 99 | Change Impact & Test Selection | 输入 task/file/symbol/capability，输出影响范围、测试建议、风险和 blocker。 |
| V2.34 / Phase 100 | Module Reading Pack & Token Ledger | 生成必读/选读/跳过阅读包、token 预算账本和裁剪理由。 |
| V2.35 / Phase 101 | Copilot Agent Integration Contracts | 暴露 task navigation、impact、test selection、context compression、handoff 公共合同。 |
| V2.36 / Phase 102 | Closure, UX Report & Governance | 生成 HTML/Mermaid 报告、治理反馈、coverage matrix 和最终验收审计。 |

## 7. 用户场景验收

### 场景 A：新增 MCP Tool

用户输入：

```text
新增一个 architecture intent MCP read tool，并同步 HTTP/CLI。
```

期望体验：

- 系统给出必读文件：MCP registry、tool dispatcher、HTTP router、CLI command、public surface guard、相关 tests。
- 系统给出复用模式：已有 code platform / architecture intent tools。
- 系统提示禁止事项：不要把核心逻辑塞进旧大文件，不要漏 public surface guard。
- Agent 可直接用 Context Pack 开始开发。

### 场景 B：修改 HarnessOS 工作流

用户输入：

```text
调整 HarnessOS 的 workflow dispatch 行为。
```

期望体验：

- 系统尝试定位 workflow manifest、runtime adapter、station/agent descriptor、tests。
- 如果无法证明运行时调用关系，输出 structured blocker。
- 不允许为了好看生成 full runtime topology。

### 场景 C：审查 Patch 风险

用户输入：

```text
这个 patch 改了 codebase snapshot 和 public surface inventory，请审查影响。
```

期望体验：

- 系统输出 impacted public surfaces、symbols、tests、docs、context packs。
- fatal/major 风险不被 ranking 隐藏。
- 输出建议测试和证据行号。

### 场景 D：Token 节流阅读

用户输入：

```text
给 Coding Agent 生成 12k token 以内的阅读包。
```

期望体验：

- 系统保留关键 evidence，不保留无证据建议。
- 系统列出 omitted_items 和 reason。
- 用户能看到相对 naive all-related-files 的 token 节省估算。

## 8. 完成定义

V2.31-V2.36 可以关闭，当且仅当：

- data_service 至少 5 个真实开发任务完成任务导航 E2E。
- HarnessOS 至少 3 个真实开发任务完成任务导航或 structured blocker。
- 每条 accepted relationship 有 repo-relative path、line range、symbol/config/test artifact evidence。
- Token ledger 能说明 included、optional、omitted、reason 和 estimated token。
- MCP/HTTP/CLI 输出 stable fields 一致。
- HTML/Mermaid 报告可读，且不引入 artifact 中不存在的新事实。
- 全量后端测试通过。
- Coverage matrix 无 open fatal/major。
