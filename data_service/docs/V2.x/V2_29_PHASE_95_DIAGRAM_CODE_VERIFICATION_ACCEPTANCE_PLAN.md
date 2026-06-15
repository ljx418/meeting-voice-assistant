# V2.29 Phase 95 验收计划：Diagram-to-Code Verification

## 1. 自动化测试

必须新增并通过：

```text
backend/tests/test_v2_29_diagram_code_verification.py
```

测试覆盖：

- `diagram_code_alignment.jsonl` / `undocumented_code_facts.jsonl` / `architecture_diff.json` / `verification_summary.json` 落盘。
- accepted verification 必须有 document evidence 和 code evidence。
- accepted verification 不能使用 `token_overlap_only`。
- confidence < 0.80 的项不能 accepted。
- token overlap only 只能 weak / needs_review。
- undocumented code facts 不得缺席。
- runtime descriptor 不能写成 runtime observed。
- public payload 不泄露绝对路径。

## 2. 回归测试

执行：

```text
PYTHONPATH=backend pytest -q \
  backend/tests/test_v2_18_platform_console.py \
  backend/tests/test_v2_19_artifact_contracts.py \
  backend/tests/test_v2_20_tool_catalog.py \
  backend/tests/test_v2_21_incremental_build.py \
  backend/tests/test_v2_22_provider_plugins.py \
  backend/tests/test_v2_23_platform_governance.py \
  backend/tests/test_v2_24_ci_readiness.py \
  backend/tests/test_v2_25_architecture_source_model.py \
  backend/tests/test_v2_26_diagram_to_claim_parser.py \
  backend/tests/test_v2_27_code_proof_graph.py \
  backend/tests/test_v2_28_intent_inference.py \
  backend/tests/test_v2_29_diagram_code_verification.py
```

## 3. 真实仓库 E2E

必须使用：

- `/Users/Zhuanz/Desktop/workspace/data_service`
- `/Users/Zhuanz/Desktop/workspace/harnessOS`

执行链路：

```text
import codebase
snapshot
Phase 91 source model
Phase 92 diagram/document claims
Phase 93 proof graph
Phase 94 intent inference
Phase 95 diagram-to-code verification
readback validation
```

### data_service 验收

- `verification_count > 0`
- `accepted_count > 0`
- `undocumented_code_fact_count > 0`
- `weak_or_missing_count >= 0`
- accepted 行全部满足硬门槛。

### HarnessOS 验收

- `verification_count > 0`
- 若 `accepted_count == 0`，必须输出 structured blocker。
- `undocumented_code_fact_count > 0`
- weak/missing/conflict/stale 必须可见，不得隐藏。

## 4. PRD 规格检视

- 文档 claim 与代码 fact 必须保留双边 evidence。
- 文档 target/current 不得混淆。
- diagram node 不能直接变成 code fact。
- token-only 不能 accepted。
- runtime descriptor 不能当运行时观测。

## 5. False-Green 拒绝条件

- HarnessOS 未跑却通过。
- token_overlap_only 被标记 accepted。
- accepted 行缺 document evidence 或 code evidence。
- confidence < 0.80 仍 accepted。
- undocumented code facts 被省略。
- public payload 泄露绝对路径、secret 或 traceback。
- 生成 runtime call graph / data flow / control flow / type inference。

## 6. 出门条件

验收审计报告必须包含：

- 测试命令和结果。
- data_service 真实 E2E 指标。
- HarnessOS 真实 E2E 指标。
- accepted hard-gate 抽样结论。
- PRD 规格检视。
- false-green 审计。
- 是否可以进入 Phase 96。
