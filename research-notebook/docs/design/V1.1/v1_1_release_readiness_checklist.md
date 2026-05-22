# ResearchNotebook V1.1 Release Readiness Checklist

文档状态：V1.1-D-RC browser visual smoke passed for supported text-source workspace query EvidenceSpan navigation.
日期：2026-05-21.
RC1 最终验证时间：2026-05-21T03:05:33Z.
RC2 live experience smoke 时间：2026-05-21T03:42:19Z.
RC4 source trace re-smoke 时间：2026-05-22.
RC5 final release sync 验证时间：2026-05-22T03:55:48Z.

## Status Table

| Item | Status | Evidence |
| --- | --- | --- |
| V1.1-B Source Preview | PASS | `v1_1_source_preview_smoke_report.md` |
| V1.1-C Unit Navigation | PASS | `v1_1_unit_navigation_smoke_report.md` |
| V1.1-D real HTTP smoke | PASS | `v1_1_d_frontend_evidence_navigation_smoke_report.md` |
| V1.1-D browser visual smoke | PASS | `v1_1_d_rc_browser_visual_smoke_report.md` |
| V1.1-RC1 release handoff | PASS | `v1_1_rc1_release_handoff.md` |
| V1.1-RC2 live experience smoke | PASS | `v1_1_rc2_live_experience_smoke_report.md` |
| V1.1-RC4 source trace re-smoke | PASS | `v1_1_rc4_source_trace_resmoke_report.md`; registry `source_id` trace returned HTTP 200 |
| V1.1-RC5 final release sync | PASS_READY_FOR_SCOPED_COMMIT | `v1_1_rc5_final_release_sync.md` |
| EvidenceSpan highlight visible | PASS | browser smoke artifact under `.smoke-artifacts/` |
| Precise evidence navigation browser-release-ready | PASS | limited to supported text-source workspace query citations carrying `source_id + unit_id + evidence_id` |
| Source trace integration | LIMITED PASS | Only for registry source_id-backed sources covered by RC4 smoke |
| all-source-type source trace | NOT_READY | RC4 only covers registry source_id-backed text source trace |
| trace-unavailable fallback | DEGRADED_ACCEPTED | Still accepted for unsupported or failing trace cases |
| all-session precise navigation | NOT_READY | session query EvidenceSpan shape not smoked |
| all-source-type precise backjump | NOT_READY | only text-source workspace query path smoked |
| Multi-format ingestion | NOT_READY | not in V1.1 scope |
| Assessment | NOT_READY | not in V1.1 scope |
| Quality/Governance console | NOT_READY | not in V1.1 scope |
| Graph editing/governance | NOT_READY | not in V1.1 scope |
| Cloud sync/collaboration | NOT_READY | not in V1.1 scope |

## Verified Commands

```text
npm run check
npm run smoke:v1.1-d-http
npm run smoke:v1.1-d-browser
npm run smoke:v1.1-rc4-trace
```

Latest RC1 check:

```text
npm run check: PASS
Boundary checks passed
94 tests passed
production build passed
```

Latest RC4 source trace re-smoke:

```text
npm run smoke:v1.1-rc4-trace: completed
workspace_id: rn-v11-rc4-trace-1779422315630-workspace
source_id: src_cce80f0ca6dad217
direct source trace: HTTP 200
decision: source trace integration is LIMITED PASS for RC4-covered registry source_id-backed sources
```

## Boundary Checks

```text
no /api/v1/knowledge new functionality
no direct fetch in feature modules
route strings remain isolated in src/shared/api/dataServiceClient.ts
artifact_ref remains metadata only
no frontend parser logic
no dangerous HTML rendering
```

## Final Declaration

Allowed:

```text
ResearchNotebook V1.1-D EvidenceSpan Highlight is browser-smoke-ready for data_service-supported text-source workspace query citations carrying source_id + unit_id + evidence_id.

ResearchNotebook V1.1 precise evidence navigation is browser-smoke-ready for the same supported workspace query citation path.

ResearchNotebook source trace integration is ready for registry source_id-backed sources covered by RC4 smoke.
```

Not allowed:

```text
all-source-type source trace integration ready
all-session precise navigation ready
all-source-type precise backjump ready
multi-format ingestion ready
assessment ready
quality governance console ready
graph editing/governance ready
cloud sync/collaboration ready
```
