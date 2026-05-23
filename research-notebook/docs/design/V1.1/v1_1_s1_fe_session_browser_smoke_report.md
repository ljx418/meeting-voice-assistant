# ResearchNotebook V1.1-S1-FE Session Browser Smoke Report

文档状态：S1-FE browser smoke 已通过；session precise evidence navigation 对 data_service-supported text-source session query citation path 进入 browser-smoke-ready。
日期：2026-05-23。

## Environment

| Item | Value |
| --- | --- |
| frontend URL | `http://127.0.0.1:5173` |
| backend URL | `http://127.0.0.1:8003` |
| browser engine | local Chrome via CDP |
| command | `npm run smoke:v1.1-s1-fe-browser` |
| frontend commit | current working tree |
| data_service commit | current working tree |

Vite was started with `VITE_DATA_SERVICE_BASE_URL=http://127.0.0.1:8003` so browser-side API calls used the target data_service service.

## Workspace / Source / Session

| Item | Value |
| --- | --- |
| workspace_id | `rn-v11-s1-fe-session-1779552117975-workspace` |
| source_id | `src_730f2fb42bc6a574` |
| session_id | `ksess_369913602193cc25` |
| unit_id | `unit_5b52cd7d1a9a762b` |
| evidence_id | `ev_f4b88ee55adf37a5` |

The smoke created a text source, created a session, ingested session content, built the session graph, opened the Workbench in a browser, ran a session query, clicked the jumpable session citation, and verified the shared Source Preview Drawer EvidenceSpan path.

## Result Table

| Check | Result | Notes |
| --- | --- | --- |
| data_service target route probe | PASS | `http://127.0.0.1:8003` |
| workspace create | PASS | Smoke workspace archived during cleanup. |
| source create | PASS | Registry `source_id` captured. |
| session create | PASS | Session selected in Workbench. |
| session ingest | PASS | Text session snippet ingested. |
| session build polling | PASS | Final status `succeeded`. |
| session citation UI render | PASS | Jumpable citation rendered from session answer. |
| SourcePreviewDrawer opens | PASS | Drawer opened after citation click. |
| unit selection | PASS | Correct unit selected and detail rendered. |
| EvidenceSpan highlight | PASS | Highlight visible inside selected unit detail. |
| console/network guard | PASS | No blocking console/page error; no `/api/v1/knowledge/*` network request. |
| cleanup | PASS | Session close and workspace archive completed. |

## EvidenceSpan Highlight

Highlighted text:

```text
Session precise navigation should preserve source id, unit id, and evidence id so the notebook can open a highlighted source span from a session answer.
```

The highlight was rendered through React text rendering inside the selected DocumentUnit detail. No `dangerouslySetInnerHTML` path was introduced.

## Fixtures / Artifacts

Sanitized JSON fixtures:

```text
fixtures/real/v1_1/session-precise-navigation-browser/
```

Files:

- `session-browser-smoke-result.json`
- `session-browser-query-evidence.json`
- `session-browser-highlight-result.json`
- `session-browser-error-locality-result.json`

Screenshot/log artifact:

```text
.smoke-artifacts/v1_1_s1_fe_session_browser/1779552117975/session-evidence-highlight.png
```

The screenshot remains under `.smoke-artifacts/` and must not be committed.

## Declaration Decision

```text
ResearchNotebook session precise evidence navigation is browser-smoke-ready for data_service-supported text-source session query citations carrying source_id + unit_id + evidence_id.
```

## Still NOT_READY

- all-session precise navigation
- all-source-type precise backjump
- all-source-type source trace
- multi-format ingestion
- assessment / mastery
- quality governance console
- graph editing/governance
- cloud sync/collaboration

## Recommended Next Phase

```text
V1.1-S2 All-Source-Type Contract Discovery
```

S2 should only discover and document capability contracts for non-text source types. It must not declare multi-format UI ready until backend contracts, fixtures, and smoke evidence exist.
