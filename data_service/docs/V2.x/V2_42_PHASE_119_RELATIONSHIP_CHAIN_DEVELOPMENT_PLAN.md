# V2.42 Phase 119 Relationship Chain v3 Development Plan

## 1. 阶段目标

Phase 119 的目标是在 V2.39 scale profile、V2.40 language facts、V2.41 workflow/runtime candidates 之上，生成面向 Agent 阅读的轻量 relationship chain：

```text
capability -> entrypoint -> handler/symbol -> dependency/reference -> test/config/doc claim
```

本阶段不实现 full call graph，不输出 runtime call，不做 data flow、control flow、type inference 或 production topology。

## 2. 输入

- V2.0 public surface / symbols / evidence artifacts
- V2.39 scale profile
- V2.40 symbol facts / reference facts
- V2.41 workflow/runtime candidates
- V2.7/V2.37 document claims and verification artifacts（若存在）
- 真实项目：data_service、HarnessOS、codexPat

## 3. 输出 Artifacts

```text
workspace/assets/codebase/{codebase_id}/architecture/v2_42/
  relationship_chains_v3.jsonl
  relationship_chain_summary.json
  forbidden_edge_scan.json
```

## 4. Edge 类型

允许：

- `capability_has_entrypoint`
- `entrypoint_handled_by_symbol`
- `symbol_references_symbol`
- `module_imports_module`
- `module_referenced_by_test`
- `module_uses_config`
- `claim_constrains_capability`
- `candidate_hint`

禁止 accepted：

- `runtime_call`
- `data_flow`
- `control_flow`
- `production_topology`
- `type_inferred_dependency`

## 5. 实现计划

1. 新增 `relationship_chains_v3.py`。
2. 建立 chain node / edge / provenance schema。
3. 从 public surface、symbols、language facts、workflow candidates、docs claims 拼接浅层链路。
4. 为每条 edge 写入 `evidence_refs`、`confidence`、`determinism`、`source_extractor`。
5. 增加 completeness score 和 blocker reason。
6. 暴露 HTTP/MCP/CLI build/read。
7. 增加 forbidden edge scan。

## 6. 架构边界

- relationship chain 是阅读线索，不是运行时执行路径。
- heuristic edge 必须可见且不能变成 accepted runtime claim。
- HarnessOS 只能通过 profile/taxonomy 配置影响 pattern，不得硬编码在通用模块。

## 7. 进入实现前门禁

- Phase 116-118 acceptance audit 均存在。
- V2.41 workflow/runtime regression 通过。
- no open fatal / major。
