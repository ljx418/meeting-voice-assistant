# UX-09 并行罗马广场讨论工作流 Provider-backed Evidence Summary

ux_id: UX-09
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
provider_invocation_count: 7
station_count: 6
artifact_count: 7
rerun_station_id: architecture_persona
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
