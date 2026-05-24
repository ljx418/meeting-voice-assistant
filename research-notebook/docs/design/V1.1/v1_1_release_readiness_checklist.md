# ResearchNotebook V1.1 Release Readiness Checklist

文档状态：V1.1-D-RC browser visual smoke passed for supported text-source workspace query EvidenceSpan navigation.
日期：2026-05-21.
RC1 最终验证时间：2026-05-21T03:05:33Z.
RC2 live experience smoke 时间：2026-05-21T03:42:19Z.
RC4 source trace re-smoke 时间：2026-05-22.
RC5 final release sync 验证时间：2026-05-22T03:55:48Z.
S1-FIX session precise navigation re-smoke 时间：2026-05-23.
S1-FE session browser smoke 时间：2026-05-23.
S2 all-source-type contract discovery 时间：2026-05-23.
S3 markdown/json backend contract smoke 时间：2026-05-24.
S4 markdown/json frontend browser smoke 时间：2026-05-24.

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
| V1.1-S1 session precise navigation API smoke | API_SMOKE_READY | `v1_1_s1_session_precise_navigation_smoke_report.md`; S1-FIX returned `HAS_EVIDENCE_SPAN_IDS`, unit detail and EvidenceSpan detail resolved |
| V1.1-S1-FE session citation browser smoke | PASS | `v1_1_s1_fe_session_browser_smoke_report.md`; session citation click opened Drawer, selected DocumentUnit, and rendered EvidenceSpan highlight |
| V1.1-S2 all-source-type contract discovery | COMPLETE | `v1_1_s2_all_source_type_contract_discovery.md`; discovery baseline before S3 |
| V1.1-S3 markdown/json backend contract | API_SMOKE_READY | `v1_1_s3_multi_format_backend_readiness.md`; manifest declares `markdown:unit` and `json:unit`; preview, DocumentUnit, query evidence and EvidenceSpan resolved |
| V1.1-S4 markdown/json frontend browser smoke | PASS | `v1_1_s4_multi_format_frontend_smoke_report.md`; markdown/json Preview, DocumentUnit and EvidenceSpan highlight visible |
| EvidenceSpan highlight visible | PASS | browser smoke artifact under `.smoke-artifacts/` |
| Precise evidence navigation browser-release-ready | PASS | limited to supported text-source workspace query citations carrying `source_id + unit_id + evidence_id` |
| Source trace integration | LIMITED PASS | Only for registry source_id-backed sources covered by RC4 smoke |
| all-source-type source trace | NOT_READY | RC4 only covers registry source_id-backed text source trace |
| trace-unavailable fallback | DEGRADED_ACCEPTED | Still accepted for unsupported or failing trace cases |
| all-session precise navigation | NOT_READY | S1-FE covers only data_service-supported text-source session query citations carrying resolvable ids; all-session scope remains unverified |
| all-source-type precise backjump | NOT_READY | text/markdown/json have supported smoke paths; PDF/PPTX/HTML/video/audio are still not ready |
| Multi-format ingestion | NOT_READY | S4 covers markdown/json UI paths only; native PDF/PPTX/video/audio ingestion is not verified |
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

Latest S1-FIX session precise navigation smoke:

```text
npm run smoke:v1.1-s1-session: completed
workspace_id: rn-v11-s1-session-1779552117955-workspace
source_id: src_103b26d7f9363bae
session_id: ksess_a92bf2adc1fe348a
session build: succeeded
session query evidence shape: HAS_EVIDENCE_SPAN_IDS
unit detail resolution: PASS
EvidenceSpan resolution: PASS
decision: session precise navigation is API_SMOKE_READY; S1-FE browser smoke later verified the UI click path
```

Latest S1-FE session browser smoke:

```text
npm run smoke:v1.1-s1-fe-browser: completed
workspace_id: rn-v11-s1-fe-session-1779552117975-workspace
source_id: src_730f2fb42bc6a574
session_id: ksess_369913602193cc25
session citation render: PASS
EvidenceSpan highlight visible: PASS
decision: session precise navigation is BROWSER_SMOKE_READY for supported text-source session query citations
```

Latest S2 all-source-type discovery:

```text
npm run smoke:v1.1-s2-discovery: completed
workspace_id: rn-v11-s2-discovery-1779595137369-workspace
capability manifest: text:unit, markdown:unit, json:unit
text preview/unit/evidence: PASS
markdown preview/unit: PASS
json preview/unit: PASS
pdf/pptx/html/video/audio preview/units: UNSUPPORTED
decision: CONTRACT_DISCOVERY_COMPLETE; S3 later proves markdown/json backend contracts
```

Latest S3 markdown/json backend contract smoke:

```text
npm run smoke:v1.1-s3-multiformat: completed
workspace_id: rn-v11-s3-multiformat-1779595456314-workspace
capability manifest: text:unit, markdown:unit, json:unit
markdown preview/unit/query evidence/EvidenceSpan: PASS
json preview/unit/query evidence/EvidenceSpan: PASS
decision: READY_MARKDOWN_JSON
```

Latest S4 markdown/json frontend browser smoke:

```text
npm run smoke:v1.1-s4-multiformat-browser: completed
workspace_id: rn-v11-s4-multiformat-1779596647207-workspace
markdown preview/unit/highlight: PASS
json preview/unit/highlight: PASS
no /api/v1/knowledge request: PASS
decision: BROWSER_SMOKE_READY_MARKDOWN_JSON
```

Visible Chrome user E2E:

```text
npm run smoke:v1.1-visible-user-e2e: completed
workspace_id: rn-v11-visible-user-1779602822347-workspace
text/markdown/json workspace citation highlight: PASS
source trace drawer: PASS
session citation highlight: PASS
no /api/v1/knowledge request: PASS
decision: VISIBLE_USER_E2E_PASS
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

## Manual Acceptance Distance

| Acceptance target | Remaining stages | Current basis | Next action |
| --- | --- | --- | --- |
| Workspace text-source EvidenceSpan navigation | 0 | HTTP smoke, browser visual smoke, and RC2 live experience smoke passed | Manual acceptance can run on the supported workspace query path |
| Registry source_id source trace | 0 | RC4 direct trace returned HTTP 200 for covered text source | Manual acceptance can run on the scoped RC4 path |
| Session precise navigation | 0 | S1-FIX returned `HAS_EVIDENCE_SPAN_IDS`; S1-FE clicked the session citation and rendered EvidenceSpan highlight | Manual acceptance can run on the supported session query path |
| Markdown/JSON source preview + unit/evidence backend | 0 | S3 backend/API smoke passed for markdown/json | Frontend/browser acceptance still requires S4 |
| Markdown/JSON frontend precise navigation | 0 | S4 browser smoke passed | Manual acceptance can run on markdown/json workspace query path |
| All-source-type precise backjump | Not in current acceptance scope | PDF/PPTX/HTML/video/audio preview/unit/evidence backend contracts are missing | Keep blocked until per-format backend contracts and browser smoke pass |

Session precise navigation has reached manual acceptance for the supported text-source session query path. Do not generalize this result to all sessions or all source types.

## Final Declaration

Allowed:

```text
ResearchNotebook V1.1-D EvidenceSpan Highlight is browser-smoke-ready for data_service-supported text-source workspace query citations carrying source_id + unit_id + evidence_id.

ResearchNotebook V1.1 precise evidence navigation is browser-smoke-ready for the same supported workspace query citation path.

ResearchNotebook source trace integration is ready for registry source_id-backed sources covered by RC4 smoke.

ResearchNotebook session precise evidence navigation is API-smoke-ready for data_service-supported text-source session query citations carrying source_id + unit_id + evidence_id.

ResearchNotebook session precise evidence navigation is browser-smoke-ready for data_service-supported text-source session query citations carrying source_id + unit_id + evidence_id.

data_service markdown/json source preview, DocumentUnit, query evidence, and EvidenceSpan backend contracts are API-smoke-ready.

ResearchNotebook markdown/json source preview, DocumentUnit navigation, and EvidenceSpan highlight are browser-smoke-ready for data_service-supported markdown/json workspace query citations carrying source_id + unit_id + evidence_id.
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
