# V2.27 Phase 93 开发计划：Code Proof Graph

## 1. 阶段目标

Phase 93 消费 Phase 91 source model 与 Phase 92 diagram claims，建立 code/config/test/runtime/document/human proof graph。

本阶段只表达证据连接，不做 intent inference，不做 accepted diagram-to-code verification。

## 2. 实现范围

新增模块：

```text
backend/data_service/code_assets/architecture_intent/proof_graph.py
```

输出：

```text
workspace/assets/codebase/{codebase_id}/architecture/intent/proof_graph/
  proof_nodes.jsonl
  proof_edges.jsonl
  evidence_bundles.jsonl
  proof_graph_summary.json
```

新增测试：

```text
backend/tests/test_v2_27_code_proof_graph.py
```

## 3. Proof Node 类型

```text
document_claim
architecture_source
code_file
config_fact
test_fact
runtime_descriptor
human_confirmed
```

## 4. Proof Edge 类型

```text
documented_by
defined_by
configured_by
tested_by
described_by
confirmed_by
contradicts
```

本阶段禁止：

```text
runtime_calls
data_flow
control_flow
type_inferred_dependency
runtime_observed
```

## 5. 验收重点

- 每个 document_claim 至少 documented_by 一个 source。
- code/config/test/runtime descriptor sources 进入 proof nodes。
- runtime_descriptor 只能是 descriptor，不得变成 runtime_observed。
- forbidden edge scan 必须为 0。
