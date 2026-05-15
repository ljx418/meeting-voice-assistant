# V3.6-F Completion Note

文档状态：V3.6-F complete: Quality evaluation MVP ready.  
当前下一阶段：V3.6-G Pipeline Board Data API.

## 1. Completion Scope

V3.6-F 完成的是 Quality Evaluation MVP，不是 Pipeline Board、business event、workflow patch 或完整 pipeline operating model。

已冻结能力：

- `quality.evaluation.create`
- `quality.evaluation.get`
- `quality.evaluation.list`
- `quality.evaluation.attach`
- rule / manual / llm_placeholder evaluator boundary
- score / status validation
- auto_attach
- attach idempotency
- resource validation for workflow_instance_id / station_run_id / artifact_id
- QualityEvaluation record and trace redaction
- artifact metadata-only evaluation boundary
- no workflow state mutation

## 2. Verified Fixes

- QualityEvaluation redaction 已移除 `raw_artifact_content`、raw connector payload、raw trace payload 等 raw payload key；quality record 和 trace 均不泄露 token-like 字段。
- `quality.evaluation.list` 在传入 `workflow_instance_id` / `station_run_id` 时做 resource validation，不再用空列表掩盖 not-found。
- `llm_placeholder` 只记录 evaluator type，不调用真实 LLM 或外部服务。
- Evaluator MVP 不调用 `artifact.read`，不读取 media/binary/large/external-only 内容。
- failed quality evaluation 不改变 `WorkflowInstance.status` 或 `StationRun.status`，不触发 approval、rerun、board、business event 或 patch。

## 3. Test Evidence

冻结时验收结果：

```text
tests/test_v3_6_quality_evaluation.py + tests/test_v3_6_workflow_contract.py: 25 passed
V3.6 focused: 54 passed
V3.5 focused: 144 passed
full pytest: 404 passed, 3 skipped
TypeScript SDK: 23 passed
drawio XML validation: passed
```

V3.6-G 后续实现会增加 board API 测试数量；该 note 记录的是 V3.6-F 冻结证据。

## 4. No False Green

V3.6-F 完成后只能声明：

```text
V3.6-F complete: Quality evaluation MVP ready.
```

仍不能声明：

```text
Pipeline Board API ready
business event ready
workflow patch ready
V3.6 complete
V4.0 ready
```

## 5. Next Phase

V3.6-G = Pipeline Board Data API.

V3.6-G 必须提供：

- `workflow.board.get`
- `workflow.instance.status`
- `station.output.list`
- station/job/artifact/approval/quality/trace summary
- scope filtering
- redacted trace summary
- no raw artifact content
- no token / subscription token / Authorization leakage

V3.6-G 只消费 V3.6-F QualityEvaluation，不修改 quality evaluation。
