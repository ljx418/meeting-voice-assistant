# ResearchNotebook V1.1-RC2 Live Experience Smoke Report

文档状态：RC2 live experience smoke passed for the supported text-source workspace evidence navigation path.
日期：2026-05-21。

## 1. Environment

RC2 使用已经启动的本地服务完成验证，不是全新隔离环境。

| Item | Value |
| --- | --- |
| frontend URL | `http://127.0.0.1:5173/` |
| backend URL | `http://127.0.0.1:8003` |
| data_service workspace root | `/private/tmp/research-notebook-local-dev` |
| manual smoke timestamp | `2026-05-21T03:42:19Z` |
| frontend branch / base commit | `main` / `8872bf82` |
| data_service route probe | `GET /api/workspaces` returned `status: ok` |

## 2. Service Status

Observed local services:

```text
frontend: Vite dev server on 127.0.0.1:5173
backend: data_service on 127.0.0.1:8003
```

The app was also opened in the system browser at `http://127.0.0.1:5173/` for local operator inspection.

## 3. Workspace / Source / Query Used

HTTP smoke workspace:

```text
workspace_id = rn-v11d-1779334896772-workspace
source_id = src_255a571fc7ee11e7
unit_id = unit_325a5a7bd3379019
evidence_id = ev_de80f5196a74dcdd
```

Browser live smoke workspace:

```text
workspace_id = rn-v11d-browser-1779334910631-workspace
source title = rn-v11d-browser-1779334910631 EvidenceSpan source
source_id = src_255a571fc7ee11e7
unit_id = unit_325a5a7bd3379019
evidence_id = ev_de80f5196a74dcdd
```

Question used:

```text
What should the notebook keep visible when evidence navigation is used?
```

Source content used:

```text
Queues absorb burst traffic during release validation.
EvidenceSpan navigation should highlight this sentence after query evidence resolves to a source id, unit id, and evidence id.
The notebook should keep answer, preview, and unit detail visible when evidence navigation is used.
```

## 4. Source Preview Result

| Check | Result |
| --- | --- |
| app opened without blank screen | PASS |
| workspace create and enter | PASS |
| source import visible | PASS |
| Source Preview Drawer opens | PASS |
| source preview visible | PASS |
| artifact refs displayed as metadata only | PASS |
| raw filesystem/cache/artifact physical path visible | PASS, none observed |

## 5. DocumentUnit Result

| Check | Result |
| --- | --- |
| Document Units section visible | PASS |
| unit list loaded | PASS |
| selected unit detail visible | PASS |
| source-level preview remains visible | PASS |
| unit navigation uses backend `unit_id` | PASS |

## 6. EvidenceSpan Highlight Result

| Check | Result |
| --- | --- |
| workspace query answer visible | PASS |
| jumpable evidence citation visible | PASS |
| citation carries `source_id + unit_id + evidence_id` | PASS |
| click citation opens/focuses SourcePreviewDrawer | PASS |
| EvidenceSpan detail loads | PASS |
| highlight visible | PASS |
| highlighted text non-empty | PASS |
| highlight located inside selected unit detail | PASS |
| answer/source preview/unit detail remain visible | PASS |
| no blocking console/pageerror | PASS |
| no `/api/v1/knowledge/*` browser network request | PASS |

Highlighted text:

```text
Queues absorb burst traffic during release validation. EvidenceSpan navigation should highlight this sentence after query evidence resolves to a source id, unit id, and evidence id.
```

Smoke artifact locations are under `.smoke-artifacts/` and must not be committed:

```text
.smoke-artifacts/v1_1_d_browser/1779334910631/browser-smoke-result.json
.smoke-artifacts/v1_1_d_browser/1779334910631/evidence-highlight.png
```

## 7. Graph / Feedback Regression Result

RC2 did not perform a destructive or governance graph workflow. The regression boundary remains:

| Check | Result |
| --- | --- |
| graph editing / merge / delete / governance actions | NOT_READY, not present as V1.1 ready capability |
| graph unavailable / missing artifact behavior | NOT_BLOCKING for ask/evidence path |
| lightweight feedback behavior | NOT_BLOCKING for answer/evidence path |

## 8. Accepted Degraded States

| Item | Status | Notes |
| --- | --- | --- |
| artifact-like evidence id | DEGRADED_ACCEPTED | Latest HTTP smoke observed 404 instead of preferred 422. Valid citation highlight path is unaffected. |
| source trace integration | NOT_READY | Source Preview / EvidenceSpan success does not prove Source Trace route readiness. |
| all-session precise navigation | NOT_READY | Session query EvidenceSpan shape has not been separately smoked. |
| all-source-type precise backjump | NOT_READY | Only text-source workspace query path has been smoked. |

## 9. Cleanup Result

| Workspace | Cleanup |
| --- | --- |
| `rn-v11d-1779334896772-workspace` | archived |
| `rn-v11d-browser-1779334910631-workspace` | archived |

No smoke-created workspace is intended to remain active. Cleanup failures were not observed.

## 10. Final Declaration

Allowed after RC2:

```text
ResearchNotebook V1.1 live experience smoke is pass for the supported text-source workspace evidence navigation path.

ResearchNotebook V1.1-D EvidenceSpan Highlight remains browser-smoke-ready for data_service-supported text-source workspace query citations carrying source_id + unit_id + evidence_id.
```

## 11. Still Not Ready

- source trace integration ready；
- all-session precise navigation ready；
- all-source-type precise backjump ready；
- multi-format ingestion ready；
- assessment ready；
- quality governance console ready；
- graph editing/governance ready；
- cloud sync/collaboration ready。
