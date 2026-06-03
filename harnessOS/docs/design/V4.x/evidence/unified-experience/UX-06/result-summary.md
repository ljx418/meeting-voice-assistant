# UX-06 局部失败修复与重跑 Evidence Summary

ux_id: UX-06
status: PASS
evidence_scope: deterministic_devlocal
runtime_backed: true
deterministic_only: true
transcript_only: false
report_only: false
false_green_risk: MEDIUM
claim_risk: MEDIUM
evidence_refs:
- docs/design/V4.2/evidence/controlled-runtime/attempt-history.json
- docs/design/V4.2/evidence/controlled-runtime/downstream-stale.json
- docs/design/V4.2/evidence/controlled-runtime/station-rerun-result.json
- docs/design/V4.2/evidence/controlled-runtime/tui-transcript.txt
- docs/design/V4.2/evidence/controlled-runtime/runtime-evidence.json
missing_evidence:
- none

notes: Rerun evidence is dev/local controlled runtime evidence and must not be overclaimed as controlled executor readiness.
