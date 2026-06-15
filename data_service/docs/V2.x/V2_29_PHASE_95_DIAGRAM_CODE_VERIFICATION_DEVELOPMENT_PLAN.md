# V2.29 Phase 95 开发计划：Diagram-to-Code Verification

## 1. 阶段目标

Phase 95 将 Phase 92 的 diagram/document claims、Phase 93 proof graph、Phase 94 intent candidates 进行对齐，输出架构图/文档声明与代码事实之间的 verification 结果。

本阶段目标不是从代码完整恢复设计意图，而是判断：

- 哪些文档/图中声明有代码、配置、测试或 runtime descriptor 证据支持。
- 哪些声明只有弱匹配。
- 哪些声明缺少代码证据。
- 哪些代码事实没有对应文档声明。
- 哪些关系存在冲突、过期或需要人工复核。

## 2. 新增模块

```text
backend/data_service/code_assets/architecture_intent/diagram_verification.py
```

## 3. 新增 artifact

```text
workspace/assets/codebase/{codebase_id}/architecture/intent/verification/
  diagram_code_alignment.jsonl
  undocumented_code_facts.jsonl
  architecture_diff.json
  verification_summary.json
```

## 4. 核心设计

### 4.1 输入

- `claims/diagram_claims.jsonl`
- `proof_graph/proof_nodes.jsonl`
- `proof_graph/proof_edges.jsonl`
- `proof_graph/evidence_bundles.jsonl`
- `intent/intent_candidates.jsonl`
- `intent/counter_evidence.jsonl`

### 4.2 Match Strategy

允许策略：

- `exact_source_ref`
- `path_name_match`
- `claim_type_to_node_type`
- `config_manifest`
- `test_reference`
- `runtime_descriptor`
- `taxonomy_synonym`
- `token_overlap_only`

`token_overlap_only` 永远不能产生 accepted，只能产生 `weak_match` 或 `needs_review`。

### 4.3 Match Status

- `accepted`
- `weak_match`
- `missing_code_evidence`
- `undocumented_code_fact`
- `conflict`
- `stale`
- `needs_review`

### 4.4 Accepted 硬门槛

一条 verification 只有同时满足以下条件才能是 `accepted`：

- `document_evidence_refs` 非空。
- `code_evidence_refs` 非空。
- `match_strategy != token_overlap_only`。
- `confidence >= 0.80`。
- 无 blocking counter evidence。
- 路径为 repo-relative。

## 5. 实施步骤

1. 在 `paths.py` 增加 verification artifact path 与 refs。
2. 新增 `diagram_verification.py`。
3. 读取 Phase 92/93/94 artifact。
4. 建立 claim normalized label、claim type、source path 到 proof node 的索引。
5. 生成 claim-to-code alignment。
6. 生成 code-to-document coverage，即 undocumented code facts。
7. 生成 diff summary：accepted / weak / missing / undocumented / conflict / stale。
8. 增加 focused tests。
9. 使用 data_service 与 HarnessOS 真实仓库执行 E2E。

## 6. 不做事项

- 不输出 runtime call graph。
- 不输出 data flow / control flow。
- 不做 type inference。
- 不把文档 target architecture 当作当前代码事实。
- 不把 token overlap 伪装为 accepted。
- 不调用外部 LLM。

## 7. 受影响文件

预计新增：

- `backend/data_service/code_assets/architecture_intent/diagram_verification.py`
- `backend/tests/test_v2_29_diagram_code_verification.py`
- `docs/V2.x/V2_29_PHASE_95_DIAGRAM_CODE_VERIFICATION_ACCEPTANCE_AUDIT_REPORT.md`

预计修改：

- `backend/data_service/code_assets/architecture_intent/paths.py`
- `backend/data_service/code_assets/architecture_intent/__init__.py`
- `docs/V2.x/V2_25_30_ARCHITECTURE_INTENT_FULL_COVERAGE_MATRIX.md`
- `docs/V2.x/README.md`

## 8. 出门条件

- focused tests 通过。
- V2.18-V2.24 + Phase 91-95 回归子集通过。
- data_service 与 HarnessOS 真实 E2E 通过。
- 每条 accepted verification 满足硬门槛。
- missing/weak/undocumented 不能被隐藏。
- PRD 规格检视无 fatal / major finding。
