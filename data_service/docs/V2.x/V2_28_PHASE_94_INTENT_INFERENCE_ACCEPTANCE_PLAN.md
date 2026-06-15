# V2.28 Phase 94 验收计划：Intent Inference Engine

## 1. 自动化测试

必须通过：

```text
backend/tests/test_v2_28_intent_inference.py
```

覆盖：

- intent_candidates / counter_evidence / summary 落盘。
- 每条 intent 有 evidence_bundle_refs 或 needs_review。
- counter evidence 不被隐藏。
- intent status 不全是 accepted。
- LLM-only 字段不得出现。

## 2. 真实仓库 E2E

### data_service

- intent_candidate_count > 0。
- 至少覆盖 public_surface_strategy、quality_strategy、storage/workflow/provider 中两类。
- 每条 recommendation 有 evidence 或 needs_review。

### HarnessOS

- intent_candidate_count > 0。
- workflow/runtime/governance 相关 intent 至少出现一类，或 structured blocker。
- weak/needs_review 不得隐藏。

## 3. PRD 规格检视

- intent candidate 不是 accepted architecture fact。
- accepted intent 不得无 evidence。
- counter evidence 必须进入输出。

## 4. False-green 拒绝条件

- LLM-only conclusion marked accepted。
- 所有 intent 都 accepted。
- 没有 evidence bundle 却无 needs_review。
- HarnessOS 未跑却通过。
- public payload 泄露绝对路径。
