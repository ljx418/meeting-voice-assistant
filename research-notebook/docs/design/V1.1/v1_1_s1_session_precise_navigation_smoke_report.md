# ResearchNotebook V1.1-S1 Session Precise Navigation Smoke Report

文档状态：S1-FIX 后已重新执行；session precise navigation API-smoke-ready。S1-FE 后续浏览器 smoke 已通过，UI/browser readiness 见 `v1_1_s1_fe_session_browser_smoke_report.md`。
日期：2026-05-23。

## Environment

| Item | Value |
| --- | --- |
| frontend branch | main |
| frontend commit | current working tree |
| data_service branch | main |
| data_service commit | current working tree |
| backend base URL | `http://127.0.0.1:8003` |
| smoke command | `npm run smoke:v1.1-s1-session` |
| smoke timestamp | 2026-05-23 S1-FIX re-smoke |

## Workspace / Source / Session

| Item | Value |
| --- | --- |
| workspace_id | `rn-v11-s1-session-1779552117955-workspace` |
| source_id | `src_103b26d7f9363bae` |
| session_id | `ksess_a92bf2adc1fe348a` |
| session build required | yes |
| session build operation_id | `sop_fa3a8c340cdb` |
| session build final status | succeeded |

The smoke created a text source, created a session, ingested a text snippet into the session, started the session build, waited for the build to complete, and then called the session query route.

## Session Query Response Shape

| Check | Result |
| --- | --- |
| session query HTTP 200 | PASS |
| answer text exists | PASS |
| session graph nodes/edges returned | PASS |
| evidence item with `source_id + unit_id + evidence_id` | PASS |
| raw filesystem/cache/artifact physical path leakage | PASS, none observed in sanitized fixtures |

Before S1-FIX classification:

```text
GRAPH_ONLY_NO_EVIDENCE
```

After S1-FIX classification:

```text
HAS_EVIDENCE_SPAN_IDS
```

The session query now returns graph nodes/edges and a resolvable evidence item carrying `source_id + unit_id + evidence_id`. This is sufficient for API-level precise navigation smoke. Browser/manual readiness was later validated by S1-FE.

## Evidence Id Decision

| Capability | Result | Reason |
| --- | --- | --- |
| Unit detail resolution | PASS | Session evidence `unit_id` resolved through DocumentUnit detail route. |
| EvidenceSpan resolution | PASS | Session evidence `evidence_id` resolved through EvidenceSpan detail route. |
| UI citation path | PASS_AFTER_S1_FE | S1-FIX is backend/API smoke only; S1-FE later validated browser/manual citation navigation. |
| Session precise navigation declaration | API_SMOKE_READY | Session query now provides resolvable EvidenceSpan ids for the supported text-source path. |

## Fixtures Saved

Fixtures are stored under:

```text
fixtures/real/v1_1/session-precise-navigation/
```

Saved fixtures:

- `capability-manifest.json`
- `source-list.json`
- `source-detail.json`
- `session-create.json`
- `session-ingest.json`
- `session-build-operation.json`
- `session-query-with-evidence-span.json`
- `session-query-no-evidence.json` from the historical pre-fix run, if retained
- `session-evidence-unit-detail.json`
- `session-evidence-span-detail.json`
- `s1-session-precise-navigation-result.json`

Fixtures were sanitized by the smoke script. They must not contain raw filesystem paths, cache paths, artifact physical paths, stack traces, or private storage filenames.

## Cleanup Result

| Cleanup step | Result |
| --- | --- |
| session close | PASS |
| workspace archive | PASS |

## Declaration Decision

```text
ResearchNotebook session precise evidence navigation is API-smoke-ready for data_service-supported text-source session query citations carrying source_id + unit_id + evidence_id.
```

Workspace precise evidence navigation remains browser-smoke-ready for the supported text-source workspace query path.

Session precise citation UI/browser readiness was later validated by S1-FE for the supported text-source session query path.

## Still NOT_READY

- all-source-type precise backjump
- all-source-type source trace
- multi-format ingestion
- assessment / mastery
- quality governance console
- graph editing/governance
- cloud sync/collaboration

## Follow-up Browser Smoke

```text
V1.1-S1-FE Session Citation Browser / Manual Smoke: PASS
```

The backend/API contract is smoke-ready, and S1-FE has now validated that a session answer citation opens SourcePreviewDrawer, selects the correct unit, and displays EvidenceSpan highlight. See `docs/design/V1.1/v1_1_s1_fe_session_browser_smoke_report.md`.

## Distance To Manual Acceptance

For the already supported workspace query text-source EvidenceSpan path, the distance to manual acceptance is:

```text
0 remaining development stages
```

For session precise navigation, the distance to manual acceptance is now:

```text
0 remaining development stages for the supported text-source session query path
```

| Step | Stage | Acceptance condition |
| --- | --- | --- |
| 1 | Completed: Session Precise Navigation Browser / Manual Smoke | A session answer citation can be clicked in the UI, opens Source Preview Drawer, selects the correct unit, and shows EvidenceSpan highlight. |
