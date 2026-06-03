# V6-4 Runtime State Model

文档状态：V6-4 runtime state design / pre-implementation audit input。本文定义 pilot runtime state，不实现代码。

## 1. State Boundary

V6-4 pilot runtime state 只用于生产试点验收，不替代项目最终 production runtime truth。

必须保留：

```text
WorkflowSpec is not runtime truth.
Drawio / Blueprint is visualization only.
Runtime Report is read-only.
Evidence Chain is read-only.
EventBridge refresh-only.
```

## 2. V6ControlledRuntimeState

Required fields:

```text
workflow_instance_id
tenant_id
workspace_id
project_id
app_id
status
station_attempts
downstream_stale
artifact_versions
quality_evaluations
revision
updated_at
runtime_result_refs
incident_timeline_refs
audit_event_refs
pilot_slice_ready_for_review=true
production_ready=false
```

Allowed workflow statuses:

```text
created
running
failed
completed
blocked
```

## 3. Station Attempt History

Each attempt:

```text
attempt_id
station_id
station_run_id
attempt_number
status
error_ref
producer_runtime_result_ref
created_at
```

Rules:

```text
station.rerun never deletes old attempt
station.rerun creates new attempt_number
failed rerun leaves old attempt recoverable
downstream stale is recorded by station_id
```

## 4. Artifact Versions

Each artifact version:

```text
artifact_version_id
artifact_id
operation=append_version
content_ref
producer_station_id
producer_attempt_id
producer_runtime_result_ref
created_at
redaction_status
```

Rules:

```text
artifact.write never overwrites previous version silently
raw_artifact_content is forbidden
correction uses append new version or retract ref
```

## 5. Quality Evaluations

Each evaluation:

```text
quality_evaluation_id
quality_rule_ref
target_ref
score_ref
operation=append_evaluation
producer_runtime_result_ref
created_at
redaction_status
```

Rules:

```text
quality.evaluation.create never overwrites previous score silently
correction evaluation keeps previous score
quality_rule_ref / target_ref / evaluation_ref must be recorded
```

## 6. Read Model Outputs

V6-4 may project runtime state into:

```text
Runtime Report
Review Console
Evidence Chain
Audit Export
Incident Timeline
```

Projection rules:

```text
read models are read-only
read models do not expose Apply / Publish / Approve / Reject / Execute / Run buttons
read models do not construct runtime truth
```
