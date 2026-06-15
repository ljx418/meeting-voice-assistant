# V2.27 Phase 93 验收计划：Code Proof Graph

## 1. 自动化测试

必须通过：

```text
backend/tests/test_v2_27_code_proof_graph.py
```

覆盖：

- proof_nodes/proof_edges/evidence_bundles 落盘。
- document_claim -> architecture_source documented_by。
- code/config/test/runtime_descriptor nodes 存在。
- runtime descriptor 不产生 runtime_observed。
- forbidden edge scan 为 0。

## 2. 真实仓库 E2E

### data_service

- proof_node_count > 0。
- proof_edge_count > 0。
- document_claim、code_file、config_fact、test_fact、runtime_descriptor 至少覆盖三类。
- forbidden_edge_count = 0。
- absolute_path_leak = false。

### HarnessOS

- proof graph 非空。
- workflow/governance/runtime 相关 claim 能进入 document_claim nodes。
- runtime_descriptor 节点存在但不标 runtime_observed。
- 大项目 blocker 不得 silent pass。

## 3. PRD 规格检视

- Phase 93 不做 intent inference。
- Phase 93 不做 diagram-to-code accepted match。
- Phase 93 不声称 full call graph、data flow、control flow。

## 4. False-green 拒绝条件

- 出现 runtime_calls/data_flow/control_flow/type_inferred_dependency edge。
- runtime_descriptor 被标记为 runtime_observed。
- proof graph 只有 summary 没有 rows。
- HarnessOS 未跑却通过。
- public payload 泄露绝对路径。
