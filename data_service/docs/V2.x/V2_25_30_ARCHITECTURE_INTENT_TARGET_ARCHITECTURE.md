# V2.25-V2.30 目标架构：Architecture Intent & Diagram Verification

## 1. 架构目标

本阶段目标架构要把项目智能从“扫描和展示代码事实”推进到“证据化架构意图理解与目标架构落地验证”。

核心原则：

- 文档声明是 document claim，不是代码事实。
- 代码事实是 code fact，不代表人类设计意图。
- 架构意图是 inference candidate，必须携带 evidence/counter_evidence/confidence。
- 人工确认后的结论是 human_confirmed，可以进入治理闭环。
- 所有 public report 必须显示 accepted、weak_match、missing、conflict、needs_review。

## 2. 总体架构

```text
Architecture Sources
  Markdown / drawio / Mermaid / PlantUML / PRD / README / API matrix
  Code / config / manifest / tests / runtime descriptors
        |
        v
Architecture Source Model
  doc_asset / diagram_cell / claim / relation / source block
        |
        v
Code Proof Graph
  surface / symbol / module / config / test / runtime / evidence span
        |
        v
Intent Inference Engine
  intent candidate / evidence bundle / counter evidence / confidence
        |
        v
Diagram-to-Code Verification
  matched / weak_match / missing_code_evidence / conflict / stale / needs_review
        |
        v
Architecture Understanding UX
  target/current/inferred/confirmed/diff report
  MCP / HTTP / CLI / Context Pack / Governance Review Queue
```

## 3. 核心组件

### 3.1 Architecture Source Model

职责：

- 统一登记文档、图、配置、测试、运行描述符。
- 保存 source path、line range、drawio cell id、diagram page、source block type。
- 处理文档权威性：target、plan、acceptance、audit、historical、unknown。

输出：

```text
architecture_sources.jsonl
architecture_diagram_cells.jsonl
architecture_source_blocks.jsonl
```

### 3.2 Diagram-to-Claim Parser

职责：

- 解析 drawio、Mermaid、PlantUML、Markdown diagram。
- 抽取 component、layer、boundary、runtime、provider、adapter、storage、workflow、public_interface。
- 抽取 relation：depends_on、implements、calls_claimed、publishes、consumes、stores、governs。
- 对模糊关系降级为 weak_claim。

边界：

- 图中节点不得直接成为 code fact。
- 未解析图格式必须输出 structured blocker。

### 3.3 Code Proof Graph

职责：

- 聚合 V2.0-V2.24 既有 code facts。
- 增强 config/test/runtime descriptor 作为佐证节点。
- 形成 proof edges：defined_by、exposed_by、configured_by、tested_by、observed_by、documented_by、confirmed_by。

边界：

- import/reference 不是 runtime call。
- test reference 只能证明测试覆盖线索，不证明生产调用。
- runtime descriptor 只有在真实运行证据存在时才能标 `runtime_observed`。

### 3.4 Intent Inference Engine

职责：

- 根据 proof graph 和 document claims 生成架构意图候选。
- 输出 confidence、evidence bundle、counter evidence、missing evidence、review recommendation。
- 支持能力级、模块级、边界级、流程级 intent candidate。

禁止：

- LLM-only conclusion 进入 accepted fact。
- 无 evidence 的意图候选隐藏 needs_review。
- 把“当前代码依赖”写成“设计目标”。

### 3.5 Diagram-to-Code Verification Engine

职责：

- 将 diagram node/edge 反推到 code facts。
- 多策略匹配：exact id、symbol/path、surface/capability、config manifest、test reference、runtime descriptor、taxonomy synonym、manual confirmed。
- 输出 status：accepted、weak_match、missing_code_evidence、undocumented_code_fact、conflict、stale、needs_review。

accepted 条件：

- 文档侧 evidence 存在。
- 代码侧 evidence 存在。
- 匹配策略不是 token_overlap_only。
- confidence >= 0.80。
- 无 blocking counter evidence。

### 3.6 Architecture Understanding UX

页面必须包含：

- Target Architecture from Documents。
- Current Architecture from Code Facts。
- Inferred Intent Candidates。
- Human Confirmed Architecture。
- Diff / Drift / Missing Evidence。
- Diagram Node Verification Board。
- Capability-to-Evidence Map。
- Review Queue and Governance Actions。

## 4. 存储布局

```text
workspace/assets/codebase/{codebase_id}/architecture/intent/
  sources/
    architecture_sources.jsonl
    diagram_cells.jsonl
    source_blocks.jsonl
  claims/
    diagram_claims.jsonl
    diagram_relations.jsonl
  proof_graph/
    proof_nodes.jsonl
    proof_edges.jsonl
    evidence_bundles.jsonl
  intent/
    intent_candidates.jsonl
    counter_evidence.jsonl
  verification/
    diagram_code_alignment.jsonl
    architecture_diff.json
  reports/
    architecture_intent_report.json
    architecture_intent_report.html
    architecture_intent_diff.mmd
  governance/
    review_queue.jsonl
    confirmed_facts.jsonl
```

## 5. 公共接口

目标 HTTP：

```text
POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/intent/build
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/intent/report
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/intent/diagram-verification
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/intent/proof-graph
POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/intent/confirm
```

目标 MCP：

```text
knowledge_architecture_intent_build
knowledge_architecture_intent_report
knowledge_diagram_code_verification
knowledge_architecture_proof_graph
knowledge_architecture_intent_confirm
```

目标 CLI：

```text
knowledge architecture intent build
knowledge architecture intent report
knowledge architecture diagram verify
knowledge architecture proof-graph
knowledge architecture intent confirm
```

## 6. 架构门禁

- 不修改 V2.0-V2.24 原始 artifacts，除非由对应 owning phase 显式 rebuild。
- 不把 document claim 直接升级为 code fact。
- 不把 token-only match 标为 accepted。
- 不输出无 evidence 的重要建议。
- 不泄露绝对路径、secret、raw traceback。
- 不声称 full call graph、data flow、control flow、runtime topology。
- Governance confirmation 必须记录 reviewer、evidence、timestamp、scope。
