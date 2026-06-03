# V4.x Report Schema

文档状态：V4-U3 报告投影合同。

## 1. 目的

Report Schema 统一 Workflow Blueprint、Runtime Report、Review Console、Evidence Chain、TUI status 和 HTML Report 的数据投影。

报告是 read model，不是 runtime truth。

## 2. WorkflowReportDTO

```json
{
  "report_id": "report_001",
  "workflow_spec_ref": "spec_local_markdown_summary",
  "workflow_version_ref": "version_001",
  "workflow_instance_ref": "instance_001",
  "generated_at": "2026-05-29T00:00:00Z",
  "source_refs": ["WorkflowSpec", "WorkflowVersion", "WorkflowInstance", "OperationEvidence"],
  "stations": [],
  "artifacts": [],
  "quality": [],
  "evidence": [],
  "available_actions": [],
  "redaction_status": "redacted"
}
```

## 3. StationReportDTO

```json
{
  "station_id": "markdown_parse",
  "station_run_id": "run_markdown_parse_001",
  "state": "Completed",
  "attempt_count": 1,
  "latest_attempt_id": "attempt_001",
  "input_artifact_refs": [],
  "output_artifact_refs": [],
  "quality_status": "passed",
  "error_summary": null,
  "available_actions": []
}
```

## 4. EvidenceReportDTO

```json
{
  "proposal_id": "proposal_001",
  "handoff_id": "handoff_001",
  "user_confirmed": true,
  "operation_type": "workflow.instance.start",
  "runtime_result_ref": "runtime_result_001",
  "risk_flags": [],
  "policy_decision": "user_confirmed_only",
  "correlation_id": "corr_001",
  "redaction_status": "redacted",
  "review_status": "ReviewReady"
}
```

## 5. Read-only Rules

1. HTML Report must not include hidden mutation forms。
2. Drawio must not include mutation instructions。
3. Reports must not expose token、secret、raw payload、raw prompt、signed URL。
4. Report actions are view or handoff actions only。
5. Runtime status must come from BFF / runtime DTO, not EventBridge payload。

