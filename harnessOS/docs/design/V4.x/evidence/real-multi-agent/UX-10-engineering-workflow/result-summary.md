# UX-10 长时工程任务工作流 Provider-backed Evidence Summary

ux_id: UX-10
status: PASS
evidence_scope: real_runtime
runtime_backed: true
deterministic_only: false
transcript_only: false
report_only: false
false_green_risk: MEDIUM
claim_risk: MEDIUM
provider: minimax
model_ref: MiniMax-M2.1
provider_config_source: .env.local
provider_invocation_count: 12
station_count: 11
artifact_count: 12
rerun_station_id: code_review
evidence_refs:
- runtime-result.json
- operation-evidence.json
- attempt-history.json
- downstream-stale.json
- runtime-report.html
- artifacts.html
- quality.html
- evidence.html
- workflow.drawio
- workflow_status.drawio
- artifact_lineage.drawio
missing_evidence:
- none

notes: This evidence proves dev/local provider-backed scenario runtime only. It does not prove production readiness, Agent executor behavior, or unrestricted orchestration.
