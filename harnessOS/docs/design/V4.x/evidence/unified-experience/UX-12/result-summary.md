# UX-12 真实 LLM 本地技术文档解析 Evidence Summary

ux_id: UX-12
status: PASS
evidence_scope: real_runtime
runtime_backed: true
deterministic_only: false
transcript_only: false
report_only: false
false_green_risk: LOW
claim_risk: LOW
real_llm_backed: true
fallback_demo_only: false
scanner_actual_read_count: 5
provider_invocation_count: 4
provider: minimax
model_ref: MiniMax-M2.1
provider_config_source: .env.local
evidence_refs:
- local-document-workflow-result.json
- evidence_chain.json
- quality_report.json
- artifacts/
missing_evidence:
- none

notes: UX-12 is real LLM-backed only when provider_invocation_count > 0 and generated_by=llm_provider artifacts exist.
