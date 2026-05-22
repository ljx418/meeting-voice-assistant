# ResearchNotebook V1.1-RC4 Source Trace Re-Smoke Report

文档状态：RC4 source trace backend fix 后 re-smoke complete；source trace integration is scoped `LIMITED PASS`。
日期：2026-05-22。

## 1. Environment

| Item | Value |
| --- | --- |
| frontend branch | `main` |
| frontend commit | `26101b87` |
| data_service branch | `main` |
| data_service commit | `26101b87` |
| frontend URL | `http://127.0.0.1:5173/` |
| backend URL | `http://127.0.0.1:8003` |
| data_service workspace root | `[tmp]/research-notebook-local-dev` |
| smoke command | `npm run smoke:v1.1-rc4-trace` |

RC4 reused local frontend/backend services started for this validation pass. The Node smoke needed local-network permission because sandboxed Node fetch could not connect to `127.0.0.1:8003`.

## 2. Workspace And Source

| Field | Value |
| --- | --- |
| workspace_id | `rn-v11-rc4-trace-1779422315630-workspace` |
| source_id | `src_cce80f0ca6dad217` |
| source_id class | registry source id |
| source title | `rn-v11-rc4-trace-1779422315630 Source Trace Source` |

The smoke verified that the observed `source_id` came from source create/list/get. It was not an `artifact_ref`, slug, sourceRef, or raw path.

## 3. Direct Source Trace Request

Request:

```text
GET /api/workspaces/rn-v11-rc4-trace-1779422315630-workspace/sources/src_cce80f0ca6dad217/trace
```

Result:

```text
HTTP 200
Trace/provenance payload returned for registry source_id.
```

Decision:

```text
source trace integration: LIMITED PASS
scope: registry source_id-backed text sources covered by RC4 smoke
```

RC4 observed a successful source trace/provenance payload for the registry `source_id` returned by source create/list/get.

## 4. Query Evidence Mapping

Workspace query evidence mapping passed:

```text
workspace query evidence mapping: PASS
registry source id observed
```

This proves the query path can now expose a registry source id for the smoke text source. It does not prove the source trace route accepts that id.

## 5. Fixture Evidence

Saved sanitized fixtures:

| Fixture | Purpose |
| --- | --- |
| `fixtures/real/v1_1/source-trace/source-list.json` | Source list containing the registry source id. |
| `fixtures/real/v1_1/source-trace/source-detail.json` | Source detail for the registry source id. |
| `fixtures/real/v1_1/source-trace/source-trace-success.json` | Direct trace route 200 result. |
| `fixtures/real/v1_1/source-trace/source-trace-404.json` | Historical direct trace route 404 fixture retained for fallback/error regression. |
| `fixtures/real/v1_1/source-trace/query-evidence-traceable-source-id.json` | Query evidence with registry source id observed. |
| `fixtures/real/v1_1/source-trace/rc4-source-trace-result.json` | RC4 smoke summary and final decision. |

Fixture hygiene:

```text
No raw filesystem path, cache path, artifact physical path, backend stack trace, or private local file path is intentionally stored.
```

## 6. Declaration Decision

Final RC4 decision:

```text
PASS
```

Reason:

```text
sources.list/get returned the registry source id, and sources.trace returned HTTP 200 with a trace/provenance payload for that same id.
```

ResearchNotebook may declare source trace integration ready only for registry source_id-backed sources covered by RC4 smoke.

## 7. Accepted Degraded States

Accepted:

- source trace success is scoped to the RC4 registry source id path;
- source trace route failure for unsupported or missing sources remains drawer-local;
- answer/evidence should remain visible when trace is unavailable;
- Source Preview / DocumentUnit / EvidenceSpan success remains separate from Source Trace success.

Not accepted:

- treating Source Preview success as Source Trace success;
- treating EvidenceSpan success as Source Trace success;
- using `sourceRef`, slug, `hit.source`, or `artifact_ref` as a fake registry source id.

## 8. Backend Contract Decision

`data_service` now provides a stable source trace contract for the RC4 target path:

```text
GET /api/workspaces/{workspace_id}/sources/{registry_source_id}/trace
```

Observed behavior:

- accepts the same registry `source_id` returned by source create/list/get;
- returns trace/provenance payload, not source preview metadata;
- keeps artifact refs as metadata;
- does not expose raw filesystem path, cache path, artifact physical path, storage filename, or stack trace in saved fixtures.

## 9. Still Not Ready

- all-source-type source trace integration;
- all-session precise navigation ready;
- all-source-type precise backjump ready;
- multi-format ingestion ready;
- assessment ready;
- quality governance console ready;
- graph editing/governance ready;
- cloud sync/collaboration ready.

## 10. Next Phase

Because RC4 re-smoke now passes, the next phase should be:

```text
V1.1-RC5 Final Evidence Navigation Release Sync
```

That phase should finalize readiness docs, run `npm run check`, perform scoped commit/push, and record commit hash / branch / remote without adding new product functionality.
