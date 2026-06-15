# V2.37 Phase 103-108 Detailed Implementation Package

## 1. 目的

本文把 V2.37 的 PRD、目标架构和验收计划拆成可执行的工程任务。实现前必须以本文作为 phase-specific development / acceptance / audit baseline。

V2.37 的核心目标不是“自动猜出完整设计意图”，而是：

```text
文档目标架构 claim
  + 当前代码事实
  + 双边 evidence
  -> target/current/diff/needs_review 报告
  -> Agent Architecture Brief
```

## 2. 建议模块边界

核心逻辑放在新的 focused package：

```text
backend/data_service/code_assets/doc_grounded_architecture/
  __init__.py
  models.py
  persistence.py
  authority_registry.py
  document_classifier.py
  markdown_claim_extractor.py
  drawio_claim_extractor.py
  term_taxonomy.py
  current_model_builder.py
  verification.py
  drift_findings.py
  report_model.py
  report_renderer_html.py
  report_renderer_mermaid.py
  agent_brief.py
  redaction.py
  audit.py
```

Thin interface modules：

```text
backend/app/api/v1/code_assets_doc_grounded_architecture.py
backend/data_service/mcp_code_doc_grounded_architecture_tools.py
backend/data_service/cli_code_doc_grounded_architecture.py
```

禁止：

- 把核心逻辑塞进 `backend/app/api/v1/data_service.py`。
- 把核心逻辑塞进 `backend/data_service/service.py`。
- 把所有逻辑堆进一个巨型 `doc_grounded_architecture.py`。
- 改写 V2.0-V2.36 上游 artifacts。
- 改写被审计项目的 docs 或 code。

## 3. Artifact 根目录

```text
workspace/assets/codebase/{codebase_id}/architecture/doc_grounded/
  authority_registry.json
  documents.jsonl
  claims.jsonl
  claim_relations.jsonl
  term_taxonomy.json
  target_architecture_model.json
  current_implementation_model.json
  verification_matrix.jsonl
  drift_findings.jsonl
  architecture_reconstruction_report.json
  views/
    architecture_reconstruction_report.html
    target_current_diff.mmd
    target_current_diff.svg
  agent_briefs/
    {brief_id}.json
    {brief_id}.md
  audits/
    pre_implementation_phase_{phase}.json
    acceptance_phase_{phase}.json
```

所有 artifact 必须包含：

```text
schema_version = v2.37
workspace_id
codebase_id
snapshot_id
source_artifact_refs
created_at
warnings
unresolved
```

## 4. 共享 Pre-Gate

每个 phase 开始前必须执行：

1. 确认 V2.0-V2.36 artifacts 可读取；缺失时输出 `DOC_GROUNDED_SOURCE_ARTIFACT_MISSING`。
2. 记录上游 artifact hash；phase 结束后确认未静默改写。
3. 确认真实项目路径存在：data_service、HarnessOS、codexPat；缺失项目只能标 `unavailable`，不能标 accepted。
4. 确认本 phase 没有 open fatal / major doc finding。
5. 确认没有 HarnessOS-only hardcode 计划。

## 5. Phase 103：Document Authority Registry v2

### 输入

- Repo-relative docs 文件。
- Markdown、drawio、README、PRD、target architecture、gap、audit、acceptance。
- 当前阶段配置中的 include/exclude policy。

### 输出

```text
documents.jsonl
authority_registry.json
audits/pre_implementation_phase_103.json
audits/acceptance_phase_103.json
```

### 实现步骤

1. 扫描 docs 路径，跳过 binary、large file、generated artifact。
2. 按文件名、标题、内容特征识别 `doc_type`。
3. 识别 `authority_role`：
   - PRD / target architecture -> target
   - development plan -> implementation_plan
   - acceptance plan / audit report -> acceptance_result / audit_status
   - old phase docs -> historical_reference
4. 识别 version / phase hint。
5. 建立 supersedes / superseded_by / stale。
6. 输出 document evidence：path + line_range 或 drawio page/cell refs。

### 验收测试

- data_service registry 非空。
- HarnessOS registry 非空，且 design docs 被识别。
- codexPat registry 非空或输出 structured unavailable。
- V2.37 docs 是 current target。
- V2.5/V2.6/V2.7 历史 docs 不能误判为 V2.37 current target。
- public payload 不包含绝对路径。

## 6. Phase 104：Architecture Claim Graph v2

### 输入

```text
documents.jsonl
authority_registry.json
Markdown/drawio source refs
```

### 输出

```text
claims.jsonl
claim_relations.jsonl
term_taxonomy.json
```

### Claim 抽取规则

必须覆盖：

- Markdown heading
- bullet / numbered list
- table row
- acceptance criteria
- non-goal / forbidden claim
- drawio node
- drawio edge

每条 claim 必须包含：

```text
claim_id
doc_id
claim_type
label
normalized_label
source_block_type
source_path
line_range 或 drawio_cell_id
authority_role
confidence
evidence
needs_review
```

### 置信度策略

```text
target PRD / target architecture heading: <= 0.90
acceptance gate: <= 0.85
bullet/table row: <= 0.80
drawio node only: <= 0.70
drawio edge only: <= 0.65
token/label inferred alias: <= 0.60
```

drawio claim 不能直接成为 code fact。

### 验收测试

- data_service/HarnessOS/codexPat 均生成 claims 或 structured blocker。
- non-goal / forbidden claim 一等抽取。
- HarnessOS workflow/runtime/agent/adapter claim 被抽取。
- drawio node 包含 drawio cell id。
- 不存在 `source=document_claim` 却被标为 code-supported 的 claim。

## 7. Phase 105：Current Implementation Model

### 输入

- V2.0 snapshot / inventory / symbols / evidence。
- V2.1 graph / DevWiki / quality。
- V2.4-V2.36 architecture/task navigation artifacts。
- Phase 103/104 outputs。

### 输出

```text
current_implementation_model.json
```

### 实现步骤

1. 读取上游 code facts，不重新扫描已存在事实层。
2. 汇总 node：
   - module
   - package
   - surface
   - symbol
   - workflow_candidate
   - runtime_candidate
   - test
   - config
   - artifact
3. 汇总 edge：
   - contains
   - defines
   - exposes
   - imports
   - references_test
   - has_blocker
4. 标记 evidence tier：
   - deterministic
   - artifact_reference
   - heuristic
   - needs_review

### 验收测试

- 上游 artifact hash 不变。
- accepted code fact 必须有 repo-relative path、line_range 或 artifact ref。
- 无 public surface 项目不能硬失败；必须保留 blocker。
- current model 中不出现 runtime call / data flow / control flow 断言。

## 8. Phase 106：Claim-to-Code Verification

### 输入

```text
claims.jsonl
claim_relations.jsonl
term_taxonomy.json
current_implementation_model.json
```

### 输出

```text
verification_matrix.jsonl
drift_findings.jsonl
```

### Match Strategy

允许：

```text
exact_id
path_line_match
artifact_ref_match
taxonomy_alias
graph_relation
manual_reviewed
token_overlap_only
```

`token_overlap_only` 永远不能产生 `supported`。

### Verification Status

```text
supported
weakly_supported
unsupported
contradicted
code_not_documented
needs_review
```

### 硬规则

- `supported` 必须有 document evidence + code evidence。
- `contradicted` 必须有 document evidence + contradiction code evidence。
- 缺任何一边证据时只能是 `weakly_supported`、`unsupported` 或 `needs_review`。
- code facts 没有对应 doc claim 时输出 `code_not_documented`。

### 验收测试

- HarnessOS 至少 10 条 claim 完成分类。
- supported row 100% 有双边 evidence。
- token_overlap_only supported count 必须为 0。
- code_not_documented summary 存在。
- contradicted row 抽样可追踪双边证据。

## 9. Phase 107：Reconstruction Report + Agent Brief

### 输入

```text
target_architecture_model.json
current_implementation_model.json
verification_matrix.jsonl
drift_findings.jsonl
```

### 输出

```text
architecture_reconstruction_report.json
views/architecture_reconstruction_report.html
views/target_current_diff.mmd
views/target_current_diff.svg
agent_briefs/{brief_id}.json
agent_briefs/{brief_id}.md
```

### HTML 报告必须包含

1. Executive summary。
2. Target Architecture from Docs。
3. Current Implementation from Code Facts。
4. Diff / Drift。
5. Needs Review。
6. Verification Matrix 摘要。
7. 推荐阅读路径。
8. HarnessOS blocker / unsupported 解释。

### Agent Brief 必须包含

```text
task_or_review_goal
role
relevant_target_claims
relevant_current_nodes
verification_summary
constraints
recommended_reading_order
recommended_next_steps
risks
evidence_refs
needs_review
omitted_items
token_estimate
```

### 验收测试

- HTML 原位渲染 Mermaid/SVG，不展示 Mermaid 源码。
- HTML 中每个 node id 能回到 report JSON。
- Mermaid 中每个 node id 能回到 persisted model。
- Brief 中每条 recommendation 有 evidence 或 needs_review。
- 小 token budget 下不能保留无 evidence 建议。
- HTML escaping / link sanitization 通过。

## 10. Phase 108：Closure Acceptance

### 输入

- Phase 103-107 artifacts。
- Phase 103-107 acceptance audits。
- Real repo E2E outputs。
- Full PRD coverage matrix。

### 输出

```text
V2_37_CLOSURE_AUDIT_REPORT.md
updated V2_37_DOC_GROUNDED_ARCHITECTURE_FULL_COVERAGE_MATRIX.md
real repo acceptance reports
```

### Closure 验收

- data_service E2E 通过。
- HarnessOS E2E 通过或 structured blocker accepted。
- codexPat E2E 通过或 structured blocker accepted。
- 全量 backend tests 通过。
- HTTP/MCP/CLI success 和 error parity 通过。
- no-hardcode audit 通过。
- redaction audit 通过。
- 上游 artifact hash gate 通过。
- 无 open fatal / major finding。

## 11. 建议测试清单

```text
test_v2_37_document_authority_registry.py
test_v2_37_claim_extraction_markdown.py
test_v2_37_claim_extraction_drawio.py
test_v2_37_current_implementation_model.py
test_v2_37_claim_code_verification.py
test_v2_37_no_token_overlap_supported.py
test_v2_37_report_renderer_integrity.py
test_v2_37_agent_brief_evidence_floor.py
test_v2_37_http_mcp_cli_parity.py
test_v2_37_real_repo_e2e.py
test_v2_37_no_harnessos_hardcode.py
test_v2_37_redaction_and_path_safety.py
```

## 12. 开发完成后的目标体验

用户应能：

1. 对 data_service 生成自举架构核查报告。
2. 对 HarnessOS 从 docs 重塑 workflow/runtime/agent/adapter target model，并核查代码事实。
3. 对 codexPat 生成 current model 和 document coverage gaps。
4. 打开 HTML 看到渲染后的图，而不是 Mermaid 源码。
5. 给 Copilot 类 Agent 提供 Architecture Brief，减少重复读仓和 token 消耗。

## 13. 不可接受结果

- 只生成目录树或文件数量图。
- 只复制 docs/drawio 的目标图，不做代码事实核查。
- 只靠 token overlap 标记 supported。
- HarnessOS 报告好看，但靠项目专用硬编码。
- HTML 出现绝对路径、secret、raw traceback。
- Renderer 生成 artifact 中不存在的新事实。
