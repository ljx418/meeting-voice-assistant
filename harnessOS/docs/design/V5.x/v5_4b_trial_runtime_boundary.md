# V5-4B Trial Runtime Boundary

文档状态：V5-4B synthetic-only core slice implemented for review。

## Allowed Trial Scope

```text
user-confirmed workflow.instance.start
user-confirmed station.rerun
redacted artifact read/write
runtime evidence recording
timeout and kill switch baseline
```

V5-4B limited implementation:

```text
synthetic in-memory workflow state only
synthetic_only=true
runtime_backed=false
no V4 runtime call
no WorkflowDraft / WorkflowVersion / WorkflowStore write
```

## Denied Trial Scope

```text
source=agent direct mutation
production connector.call
production external_llm.call without credential boundary
production tenant control plane
production audit export
```
