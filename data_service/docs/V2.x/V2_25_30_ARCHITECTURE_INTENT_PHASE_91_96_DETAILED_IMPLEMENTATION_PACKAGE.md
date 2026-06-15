# V2.25-V2.30 Phase 91-96 详细实施与验收包

## 1. 使用方式

本文档是 V2.25-V2.30 的执行级文档。每个 Phase 开始前必须先完成本阶段的 pre-implementation audit；若 audit 出现 fatal/major open finding，不得进入业务实现。

所有阶段默认使用真实仓库：

- `data_service`：当前仓库。
- `HarnessOS`：大型复杂工作流项目，用于验证泛用性和 blocker 行为。

## 2. Phase 91：Architecture Source Model

### 2.1 开发目标

建立统一架构源模型，把后续所有输入都登记为可追踪 source：

- Markdown / README / PRD / target architecture / gap / audit / acceptance。
- drawio / Mermaid / PlantUML / Markdown diagram。
- code facts：surface、symbol、module、relationship、existing evidence。
- config / manifest / workflow descriptor。
- tests / fixtures / contract files。
- runtime descriptor，仅限已有只读证据。

### 2.2 设计要点

新增 focused module：

```text
backend/data_service/code_assets/architecture_intent/source_model.py
```

核心输出：

```text
architecture_sources.jsonl
architecture_diagram_cells.jsonl
architecture_source_blocks.jsonl
architecture_source_summary.json
```

关键字段：

```text
source_id
source_type
path
authority_role
authority_level
phase_hint
version_hint
stale_hint
supersedes
superseded_by
locator
evidence
confidence
needs_review
```

### 2.3 验收标准

- data_service 与 HarnessOS source count > 0。
- drawio、Markdown、code、test/config 至少各有一次 attempt 或 structured blocker。
- 所有 public path repo-relative。
- 历史文档不得被误判为当前 target authority。
- artifact 落盘后可读回，schema_version 存在。

### 2.4 假通过拒绝

- 只登记 docs 文件名，不解析 source block。
- HarnessOS 不存在或未扫描却标记通过。
- 绝对路径进入 public payload。

## 3. Phase 92：Diagram-to-Claim Parser

### 3.1 开发目标

将架构图和图形化文档结构化为 claim/relation。

支持：

- drawio XML cell。
- Mermaid diagram block。
- Markdown 中的架构列表、表格、验收门槛。
- PlantUML 若无 parser，可 structured blocker。

### 3.2 设计要点

新增 focused module：

```text
backend/data_service/code_assets/architecture_intent/diagram_claims.py
```

输出：

```text
diagram_claims.jsonl
diagram_relations.jsonl
diagram_parse_warnings.jsonl
```

Claim 类型：

```text
component
layer
boundary
adapter
provider
runtime
workflow
storage
public_interface
quality_gate
milestone
non_goal
forbidden_claim
```

Relation 类型：

```text
depends_on
implements
calls_claimed
publishes
consumes
stores
governs
validates
```

### 3.3 验收标准

- 每条 claim 有 source locator：line_range 或 drawio cell_id。
- drawio node-only claim confidence 默认不超过 0.70，除非有额外文档证据。
- non_goal / forbidden_claim 被一等抽取。
- 无法解析的图格式输出 `ARCHITECTURE_DIAGRAM_PARSE_UNSUPPORTED`。

### 3.4 假通过拒绝

- 把 diagram claim 直接写成 code fact。
- Mermaid/raw label 未 escape 进入报告。
- 图中边关系被标记为 runtime call。

## 4. Phase 93：Code Proof Graph

### 4.1 开发目标

把已有 V2.0-V2.24 code facts 和新增 config/test/runtime evidence 汇总成 proof graph。

### 4.2 设计要点

新增 focused module：

```text
backend/data_service/code_assets/architecture_intent/proof_graph.py
```

Proof node：

```text
document_claim
code_symbol
public_surface
module
config_fact
test_fact
runtime_descriptor
human_confirmed
```

Proof edge：

```text
documented_by
defined_by
exposed_by
configured_by
tested_by
observed_by
confirmed_by
contradicts
```

### 4.3 语义边界

- `module_imports_module` 只能是 dependency evidence，不是 runtime call。
- `tested_by` 只能证明测试引用，不证明生产路径。
- `observed_by` 只有真实运行证据存在时可用。
- runtime 证据缺失时必须是 `runtime_unavailable`，不能 fake。

### 4.4 验收标准

- proof_nodes/proof_edges 非空。
- edge 有 evidence_refs 或 needs_review。
- forbidden edge scan：不得出现 full_call_graph、data_flow、control_flow、type_inferred_dependency。
- data_service 至少覆盖 HTTP/MCP/CLI 或 platform modules。
- HarnessOS 至少覆盖 workflow/agent/station/runtime/governance 中的一类，或输出 blocker。

## 5. Phase 94：Intent Inference Engine

### 5.1 开发目标

生成架构意图候选，而不是确定性设计事实。

### 5.2 设计要点

新增 focused module：

```text
backend/data_service/code_assets/architecture_intent/intent_inference.py
```

Intent 类型：

```text
capability
module_boundary
workflow
governance
runtime
storage
public_surface_strategy
provider_strategy
quality_strategy
```

每条 intent candidate 必须包含：

```text
summary
evidence_bundle_refs
counter_evidence_refs
confidence
status
missing_evidence
review_recommendation
```

### 5.3 置信度规则

```text
accepted: >= 0.85 + 多源 evidence + 无 blocking counter evidence
inferred: 0.65-0.84 + evidence_bundle 存在
weak: 0.40-0.64
needs_review: evidence/counter evidence 冲突或不足
rejected: counter evidence 强
```

LLM 可用于摘要，但不得作为唯一证据。

### 5.4 验收标准

- 每条 intent 有 evidence_bundle 或 needs_review。
- counter evidence 不被隐藏。
- data_service 至少生成 3 类 intent candidate。
- HarnessOS 至少生成 workflow/governance/runtime 相关候选或 blocker。

## 6. Phase 95：Diagram-to-Code Verification

### 6.1 开发目标

把架构图中的节点/边反推到代码事实，输出可审计的落地状态。

### 6.2 设计要点

新增 focused module：

```text
backend/data_service/code_assets/architecture_intent/diagram_verification.py
```

匹配策略：

```text
exact_symbol_id
surface_id
path_line
config_manifest
test_reference
runtime_descriptor
taxonomy_synonym
manual_confirmed
token_overlap_only
```

状态：

```text
accepted
weak_match
missing_code_evidence
undocumented_code_fact
conflict
stale
needs_review
```

### 6.3 accepted 硬门槛

- document_evidence_refs 非空。
- code_evidence_refs 非空。
- match_strategy 不是 token_overlap_only。
- confidence >= 0.80。
- 无 blocking counter evidence。

### 6.4 验收标准

- data_service 有 accepted verification。
- HarnessOS 有 diagram verification result；若 accepted 不足，必须输出 blocker taxonomy。
- weak/missing/conflict/stale 在 report 中可见。
- 不得将文档目标架构当作当前代码事实。

## 7. Phase 96：UX Report、Context Pack、Governance 与 Closure

### 7.1 开发目标

生成用户可读的最终报告和 Agent 可消费的 context pack，并接入 governance confirmation。

### 7.2 设计要点

新增 focused modules：

```text
backend/data_service/code_assets/architecture_intent/report.py
backend/data_service/code_assets/architecture_intent/context_pack.py
backend/data_service/code_assets/architecture_intent/governance.py
```

报告区块：

```text
Target Architecture from Documents
Current Architecture from Code Facts
Inferred Intent Candidates
Human Confirmed Architecture
Diagram-to-Code Verification Board
Diff / Drift / Missing Evidence
Review Queue
Recommended Next Actions
```

### 7.3 验收标准

- HTML 报告非 raw JSON，包含图表、解释和关键关系图。
- Mermaid 节点来自 persisted report JSON，不得新造事实。
- Context Pack 三种模式：project_brief、task_context、architecture_review。
- 每条 recommendation 有 evidence_refs 或 needs_review。
- confirm/revoke 不修改原始 artifact，source hash 不变。
- Full coverage matrix 无 fatal/major open finding。

## 8. 公共接口实现顺序

建议最后统一暴露：

```text
HTTP:
POST /architecture/intent/build
GET  /architecture/intent/report
GET  /architecture/intent/diagram-verification
GET  /architecture/intent/proof-graph
POST /architecture/intent/confirm

MCP:
knowledge_architecture_intent_build
knowledge_architecture_intent_report
knowledge_diagram_code_verification
knowledge_architecture_proof_graph
knowledge_architecture_intent_confirm

CLI:
knowledge architecture intent build
knowledge architecture intent report
knowledge architecture diagram verify
knowledge architecture proof-graph
knowledge architecture intent confirm
```

## 9. 自动化测试建议

```text
test_v2_25_source_model_real_repos.py
test_v2_26_diagram_claim_parser.py
test_v2_27_proof_graph_semantic_boundaries.py
test_v2_28_intent_inference_evidence_policy.py
test_v2_29_diagram_code_verification_thresholds.py
test_v2_30_architecture_intent_report_and_context.py
test_v2_25_30_public_payload_redaction.py
test_v2_25_30_no_false_green.py
```
