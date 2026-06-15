# V2.28 Phase 94 开发计划：Intent Inference Engine

## 1. 阶段目标

Phase 94 基于 Phase 93 proof graph 生成 evidence-backed architecture intent candidates。Intent candidate 是推断候选，不是确定事实。

本阶段不使用 LLM 作为唯一证据，不做 diagram-to-code accepted verification，不做人工确认。

## 2. 实现范围

新增模块：

```text
backend/data_service/code_assets/architecture_intent/intent_inference.py
```

输出：

```text
workspace/assets/codebase/{codebase_id}/architecture/intent/intent/
  intent_candidates.jsonl
  counter_evidence.jsonl
  intent_summary.json
```

新增测试：

```text
backend/tests/test_v2_28_intent_inference.py
```

## 3. Intent 类型

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

## 4. 置信度策略

- accepted：confidence >= 0.85，证据数量足够，无 blocking counter evidence。
- inferred：0.65 <= confidence < 0.85，有 evidence bundle。
- weak：0.40 <= confidence < 0.65。
- needs_review：证据不足、反证存在或来源冲突。
- rejected：强反证。

## 5. 不做内容

- 不把 intent candidate 写成 code fact。
- 不调用外部 LLM。
- 不做 runtime observation。
- 不做 diagram-to-code verification。
