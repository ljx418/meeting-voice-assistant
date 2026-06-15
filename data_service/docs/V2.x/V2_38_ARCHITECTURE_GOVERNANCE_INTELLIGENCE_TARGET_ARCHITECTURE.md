# V2.38 目标架构：版本化架构核查与增量 Agent 上下文服务

## 1. 架构目标

V2.38 的目标架构不是单纯生成图，而是建立一条可版本化、可增量更新、可被 Agent 调用的架构理解链路：

```text
Docs + Code Facts + Version Diff
  -> Architecture Knowledge Store
  -> Verification / Impact / Context
  -> Human Report + Agent Pack
```

## 2. 核心数据流

```text
Repo Snapshot
  -> Code Fact Index
  -> Capability Chain Builder
  -> Current Architecture Model

Docs Snapshot
  -> Document Authority Registry
  -> Architecture Claim Graph
  -> Target Architecture Model

Git/Snapshot Diff
  -> Incremental Impact Analyzer
  -> Stale Understanding Detector

Target + Current + Diff
  -> Verification Matrix
  -> Drift Findings
  -> Architecture Version Index
  -> Human Report v3
  -> Architecture Context Pack v5
```

## 3. 目标组件

### 3.1 Architecture Version Index

职责：

- 记录每次架构理解构建的 snapshot_id、docs hash、code fact hash、report hash。
- 支持比较前后版本。
- 标记 stale artifacts。

输出：

```text
architecture_version_index.json
architecture_version_diff.json
```

### 3.2 Incremental Architecture Impact Analyzer

职责：

- 消费 git diff / snapshot diff。
- 计算受影响 files、symbols、surfaces、capabilities、claims、tests。
- 标记哪些报告或 Context Pack 需要刷新。

输出：

```text
architecture_incremental_impact.json
impacted_nodes.jsonl
stale_artifacts.jsonl
```

### 3.3 Capability-to-Implementation Chain v2

职责：

- 构建轻量可信链路：

```text
capability -> public surface -> handler/symbol -> module/file -> test/reference
```

边界：

- 允许 import/reference/handler mapping。
- 不声称完整 runtime call graph。
- heuristic 边必须标记 confidence 和 needs_review。

输出：

```text
capability_implementation_chains_v2.jsonl
chain_coverage_summary.json
```

### 3.4 Document-Code Verification v3

职责：

- 强化 V2.37 verification。
- 加入 version/stale/context 信息。
- 输出 supported、weakly_supported、unsupported、contradicted、code_not_documented。

硬规则：

- supported 必须有 document evidence + code evidence。
- token_overlap_only 永远不能 supported。
- contradicted 必须有冲突证据。

### 3.5 Architecture Context Pack v5

职责：

- 面向 Agent 生成任务级上下文。
- 根据 token budget 裁剪。
- 优先保留 evidence-backed chain、design constraints、tests。

输出：

```text
architecture_context_pack_v5/{pack_id}.json
architecture_context_pack_v5/{pack_id}.md
```

### 3.6 Human Architecture Report v3

职责：

- 给人类展示可读报告。
- 图表必须原位渲染，不能展示 Mermaid 源码。

报告区块：

1. 项目一句话定位。
2. 目标架构图。
3. 当前实现图。
4. 能力入口图。
5. capability chain 图。
6. 设计-实现差异。
7. 增量影响分析。
8. Agent 推荐阅读路径。

## 4. Artifact Layout

```text
workspace/assets/codebase/{codebase_id}/architecture/v2_38/
  architecture_version_index.json
  architecture_version_diff.json
  architecture_incremental_impact.json
  impacted_nodes.jsonl
  stale_artifacts.jsonl
  capability_implementation_chains_v2.jsonl
  chain_coverage_summary.json
  verification_matrix_v3.jsonl
  drift_findings_v3.jsonl
  human_architecture_report_v3.json
  views/
    architecture_report_v3.html
    target_current_diff.svg
    capability_chains.svg
    impact_map.svg
  architecture_context_pack_v5/
    {pack_id}.json
    {pack_id}.md
```

## 5. Public Contract

HTTP:

```text
POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/v2_38/build
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/v2_38/report
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/v2_38/impact
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/v2_38/chains
POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/v2_38/context-pack
```

MCP:

```text
knowledge_code_architecture_v238_build
knowledge_code_architecture_v238_report
knowledge_code_architecture_v238_impact
knowledge_code_architecture_v238_chains
knowledge_code_architecture_context_pack_v5
```

CLI:

```text
knowledge code architecture v2-38 build
knowledge code architecture v2-38 report
knowledge code architecture v2-38 impact
knowledge code architecture v2-38 chains
knowledge code architecture v2-38 context-pack
```

## 6. 架构边界

V2.38 只读消费 V2.0-V2.37 artifacts，除非用户显式要求重建对应阶段。

V2.38 不得：

- 修改 source registry。
- 修改目标项目代码。
- 修改目标项目 docs。
- 将 low confidence 输出为确定事实。
- 将 HarnessOS 专用路径写死到通用逻辑。

## 7. 后续目标架构扩展

V2.38 完成后，后续路线会在同一条 architecture knowledge pipeline 上增加以下扩展层。扩展层必须保持 provider 化、profile 化、证据优先，不能把某个真实项目的结构写死到通用逻辑。

```text
Large Repo Scale Profile
  -> Budgeted Scanner
  -> Sharded Artifact Store
  -> Paginated Readback

Multi-language AST/LSP Providers
  -> Language Symbol Facts
  -> Reference Facts
  -> Optional LSP Diagnostics

Workflow / Runtime Extractors
  -> Workflow Candidates
  -> Runtime Adapter Candidates
  -> Entrypoint Candidates

Document Semantic Parser
  -> Markdown Claim Blocks
  -> Drawio Page/Lane/Group/Edge Claims
  -> Acceptance / Non-goal / Gate Claims

Project Profile / Taxonomy Manager
  -> Terminology
  -> Entrypoint Patterns
  -> Workflow Patterns
  -> Authority Rules

Token Budget Optimizer
  -> Reading Budget
  -> Cache Reuse
  -> Omitted Items
  -> Evidence-preserving Compression
```

### 7.1 性能与分层索引层

目标：

- 支持数十万行代码级项目的预算化扫描。
- 对大文件、generated/vendor、binary、超时目录进行可解释跳过。
- 支持 artifact 分片、分页读取和缓存命中统计。

### 7.2 多语言 AST/LSP Provider 层

目标：

- Python AST 保持 mandatory baseline。
- tree-sitter/LSP 作为 optional provider。
- 未配置 provider 时返回 `provider_unavailable`，不能把 fallback 当成真实语言理解。

### 7.3 Workflow / Runtime Extractor 层

目标：

- 识别 workflow、agent、runtime adapter、pipeline、CLI/TUI/console entrypoint 的候选事实。
- 输出 candidate，而不是生产 runtime topology。
- 所有 runtime-like 结论必须有 path/line/config evidence 或 needs_review。

### 7.4 drawio / 文档语义解析层

目标：

- 不只读取文本标签，还要读取图页、容器、泳道、分组、边、图例和验收门槛。
- drawio 输出只能成为 document claim，不能直接成为 code fact。

### 7.5 Project Profile / Taxonomy 层

目标：

- 用配置表达项目族术语和入口模式。
- 支持 HarnessOS 这类大型项目作为真实回归样例，但不把 HarnessOS 写死进 extractor。

### 7.6 Token Budget 与 Agent 上下文层

目标：

- 对每次 Agent 上下文生成记录 token budget、cache hit、reading order、omitted items。
- 保证裁剪时 recommendation 与 evidence 一起保留或一起降级为 needs_review。
