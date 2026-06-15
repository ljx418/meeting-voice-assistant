# V2.26 Phase 92 验收计划：Diagram-to-Claim Parser

## 1. 验收目标

确认 Phase 92 可以基于 Phase 91 artifacts 生成可追踪、可解释、不过度承诺的架构 claim/relation。

## 2. 自动化测试

必须新增并通过：

```text
backend/tests/test_v2_26_diagram_to_claim_parser.py
```

测试覆盖：

- drawio node -> claim。
- drawio edge -> relation，未标注 edge needs_review。
- Mermaid fenced block -> claim/relation。
- Markdown 架构 bullet -> claim。
- forbidden/non-goal 一等抽取。
- token/code/runtime 不被标为 code fact/runtime call。

## 3. 真实仓库 E2E

### data_service

必须满足：

- `diagram_claims.jsonl` 非空。
- `diagram_relations.jsonl` 非空或 summary 中说明无 relation。
- claim_type 覆盖至少 component/layer/boundary/public_interface/quality_gate 中两类。
- forbidden/non_goal 若在 V2 文档中出现，必须被抽取。

### HarnessOS

必须满足：

- workflow/agent/runtime/governance 相关 claim 至少出现一类。
- drawio cell 或 Markdown block 可追踪到 source locator。
- 无法确定关系的 edge 必须 needs_review。
- 不得把 document claim 写成 code fact。

## 4. Artifact inspection

检查路径：

```text
workspace/assets/codebase/{codebase_id}/architecture/intent/claims/
  diagram_claims.jsonl
  diagram_relations.jsonl
  diagram_claim_summary.json
```

断言：

- JSON/JSONL 可解析。
- 每条 claim 有 source_locator。
- 每条 relation 有 relation_type 和 evidence。
- public payload 无绝对路径。

## 5. PRD 规格检视

- Phase 92 没有实现代码落地验证。
- Phase 92 没有把 claim 当 code fact。
- Phase 92 没有声称 runtime relationship。

## 6. False-green 拒绝条件

- 只统计 claim count，不写 claim rows。
- drawio edge 无 target/source 却 accepted relation。
- relation_type 使用 runtime_calls / data_flow / control_flow。
- HarnessOS 没跑却标记通过。
- raw HTML/script 进入 label。

## 7. 验收输出

验收通过后必须产出：

```text
docs/V2.x/V2_26_PHASE_92_DIAGRAM_TO_CLAIM_ACCEPTANCE_AUDIT_REPORT.md
```
