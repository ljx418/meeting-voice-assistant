# ResearchNotebook V1.1-RC1 Release Handoff

文档状态：V1.1-RC1 handoff ready for scoped repository sync.
日期：2026-05-21。

## 1. Release Candidate Summary

ResearchNotebook V1.1 已完成 Source Preview、DocumentUnit 导航和 EvidenceSpan 高亮的受限路径验收：

- V1.1-B Source Preview：`PASS`；
- V1.1-C Unit-Level Source Navigation：`PASS`；
- V1.1-D EvidenceSpan Highlight：`PASS`，已通过真实 HTTP smoke 和浏览器可视化 smoke；
- 精确证据导航当前只限 `data_service` 支持的文本源 workspace query citation；
- citation 必须携带 `source_id + unit_id + evidence_id`；
- Source Trace integration 仍为 `NOT_READY`。

## 2. Current Claimable Scope

可以声明：

```text
ResearchNotebook V1.1-D EvidenceSpan Highlight 已对 data_service 支持的文本源 workspace query citation 完成 browser-smoke-ready 验收。

ResearchNotebook V1.1 精确证据导航已在同一条受限路径完成 browser-smoke-ready 验收：citation 必须携带 source_id + unit_id + evidence_id。
```

不能扩大声明到：

- session query；
- 所有 source type；
- Source Trace route；
- multi-format ingestion；
- assessment；
- quality governance console；
- graph editing/governance；
- cloud sync/collaboration。

## 3. Verified Commands

本阶段记录的验证命令：

```text
npm run check
npm run smoke:v1.1-d-http
npm run smoke:v1.1-d-browser
```

最近一次 `npm run check` 结果：

```text
PASS
Boundary checks passed
94 tests passed
production build passed
```

## 4. Smoke Evidence

HTTP smoke 覆盖：

- target route probe：`PASS`；
- workspace create/archive：`PASS`；
- source create：`PASS`；
- capability manifest evidence flags：`PASS`；
- unit list/detail：`PASS`；
- workspace query 返回 `source_id + unit_id + evidence_id`：`PASS`；
- EvidenceSpan detail 返回 `normalized_text / half_open / document_unit_text`：`PASS`；
- unknown evidence 404：`PASS`；
- fixtures saved：`PASS`；
- cleanup：`PASS`。

Browser smoke 覆盖：

- browser opened app：`PASS`；
- no blank screen：`PASS`；
- workspace create and enter：`PASS`；
- source import visible：`PASS`；
- Source Preview Drawer opens：`PASS`；
- Document Units visible：`PASS`；
- unit detail visible：`PASS`；
- workspace query jumpable citation visible：`PASS`；
- citation click shows EvidenceSpan highlight：`PASS`；
- `data-testid="evidence-highlight"` exists：`PASS`；
- highlighted text non-empty：`PASS`；
- no blocking console/pageerror：`PASS`；
- no `/api/v1/knowledge/*` network request：`PASS`；
- cleanup archive workspace：`PASS`。

Smoke artifacts are written under `.smoke-artifacts/`, which is gitignored and must not be committed.

## 5. Accepted Degraded States

| Item | Status | Notes |
| --- | --- | --- |
| artifact-like evidence id error semantics | `DEGRADED_ACCEPTED` | Latest HTTP smoke observed 404 instead of preferred 422. This does not block the valid citation highlight path. |
| source trace integration | `NOT_READY` | V1.0 RC6 trace route remained 404 for registry `source_id`. |
| session precise navigation | `NOT_READY` | Session query EvidenceSpan shape has not been real-smoked. |
| all-source-type precise backjump | `NOT_READY` | Only text-source workspace query path has been smoked. |

## 6. Not-Ready Capabilities

These capabilities must remain `NOT_READY` in V1.1-RC1:

- source trace integration ready；
- all-session precise navigation ready；
- all-source-type precise backjump ready；
- multi-format ingestion ready；
- assessment ready；
- quality governance console ready；
- graph editing/governance ready；
- cloud sync/collaboration ready。

## 7. Boundary Checks

Required boundary rules:

- feature modules do not directly `fetch` backend routes；
- route strings remain isolated in `src/shared/api/dataServiceClient.ts`；
- `artifact_ref` remains metadata only and is never parsed as a filesystem path；
- no new `/api/v1/knowledge/*` functionality；
- backend HTML/Markdown preview content is not rendered with `dangerouslySetInnerHTML`；
- source preview success is not treated as source trace success。

## 8. Fixture / Artifact Hygiene

Fixtures under `fixtures/real/v1_1/` must not contain:

- local absolute paths；
- `file://`；
- `cache_path`；
- `artifact_path`；
- `physical_path`；
- raw filesystem paths；
- private source content；
- backend stack traces。

Runtime screenshots and logs stay under `.smoke-artifacts/` and are not committed.

## 9. Git Sync Scope

Current repository context:

```text
branch: main
remote: origin https://github.com/ljx418/meeting-voice-assistant.git
sync scope: research-notebook working tree only
```

Commit must be scoped. Do not use `git add .` from a parent workspace. Do not include `data_service/` or other sibling project changes.

## 10. Final Handoff Statement

If scoped commit and push succeed:

```text
ResearchNotebook V1.1 release handoff is repository-ready.
ResearchNotebook V1.1-D EvidenceSpan Highlight is browser-smoke-ready for data_service-supported text-source workspace query citations carrying source_id + unit_id + evidence_id.
ResearchNotebook V1.1 precise evidence navigation is browser-smoke-ready for the same supported workspace query citation path.
```

## 11. Recommended Next Phase

Recommended order after RC1:

1. Source Trace Contract Fix / Re-Smoke；
2. Session Precise Navigation Smoke；
3. All-Source-Type Preview Contract Discovery；
4. V1.2+ multi-format ingestion / assessment / governance / graph editing / cloud sync planning。

Future capabilities must not be backfilled into V1.1 ready statements.
