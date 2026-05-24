# ResearchNotebook V1.1 Final Manual Acceptance / Repository Sync

文档状态：FINAL 收口记录。
日期：2026-05-24。

## Final Summary

V1.1 的当前可声明范围已经完成：

- 文本源 workspace query EvidenceSpan navigation: PASS
- 文本源 session query EvidenceSpan navigation: PASS
- registry source_id source trace: LIMITED PASS
- markdown workspace query EvidenceSpan navigation: BROWSER_SMOKE_READY
- json workspace query EvidenceSpan navigation: BROWSER_SMOKE_READY

V1.1 不声明：

- all-session precise navigation ready
- all-source-type precise backjump ready
- all-source-type source trace ready
- native PDF/PPTX/HTML/video/audio ingestion ready
- Assessment / Mastery ready
- Quality/Governance console ready
- Graph editing/governance ready
- Cloud sync/collaboration ready

## Verified Commands

ResearchNotebook:

```text
npm run check
npm run smoke:v1.1-s2-discovery
npm run smoke:v1.1-s3-multiformat
npm run smoke:v1.1-s4-multiformat-browser
```

Latest observed results:

```text
npm run check: PASS
npm run smoke:v1.1-s2-discovery: PASS
npm run smoke:v1.1-s3-multiformat: READY_MARKDOWN_JSON
npm run smoke:v1.1-s4-multiformat-browser: BROWSER_SMOKE_READY_MARKDOWN_JSON
```

data_service focused tests:

```text
python3 -m pytest tests/test_target_http_source_preview.py tests/test_target_http_document_units.py tests/test_target_http_evidence_spans.py tests/test_target_http_multi_format.py -q
```

Latest observed result:

```text
20 passed
```

## Source Type Status

| source type | backend preview/unit/evidence | frontend browser path | declaration |
| --- | --- | --- | --- |
| text | PASS | PASS | ready for scoped workspace/session text-source paths |
| markdown | PASS | PASS | browser-smoke-ready for workspace query citation path |
| json | PASS | PASS | browser-smoke-ready for workspace query citation path |
| pdf | NOT_READY | NOT_READY | backend contract missing |
| pptx | NOT_READY | NOT_READY | backend contract missing |
| html | NOT_READY | NOT_READY | backend contract missing |
| video | NOT_READY | NOT_READY | backend contract missing |
| audio | NOT_READY | NOT_READY | backend contract missing |

## Fixture Hygiene

Validated fixture roots:

```text
fixtures/real/v1_1/all-source-type-discovery/
fixtures/real/v1_1/multi-format-backend/
fixtures/real/v1_1/multi-format-frontend/
```

No forbidden local path fragments were found in the checked fixture roots:

```text
/Users
file://
cache_path
artifact_path
physical_path
/private/tmp
/tmp/
```

Screenshots and browser logs remain under `.smoke-artifacts/` and are not staged for git.

## Boundary Checks

Maintained:

- no new `/api/v1/knowledge/*` functionality
- no feature-layer direct HTTP fetch
- route shape remains isolated to `src/shared/api/dataServiceClient.ts`
- `artifact_ref` remains metadata only
- no frontend parser for markdown/json
- no `dangerouslySetInnerHTML`

## Scoped Git Sync

Repository root:

```text
<workspace-root>
```

Branch:

```text
main
```

Remote:

```text
origin https://github.com/ljx418/meeting-voice-assistant.git
```

Pre-sync base commit:

```text
a09eaf3d
```

Final pushed commit:

```text
240b6d8f
```

Push result:

```text
main -> origin/main
```

Sync scope:

- `research-notebook` V1.1 docs, fixtures, smoke scripts, package scripts
- `data_service` source preview / DocumentUnit / multi-format focused tests

Known pre-existing dirty files in sibling `data_service` were not staged unless they were part of the scoped V1.1 multi-format backend contract files.

## Final Declaration

Allowed after scoped commit / push:

```text
ResearchNotebook V1.1 release handoff is committed and pushed.
ResearchNotebook V1.1 text-source workspace/session evidence navigation is browser-smoke-ready for citations carrying source_id + unit_id + evidence_id.
ResearchNotebook markdown/json workspace evidence navigation is browser-smoke-ready for citations carrying source_id + unit_id + evidence_id.
ResearchNotebook source trace integration is ready for registry source_id-backed sources covered by RC4 smoke.
```

Still not allowed:

```text
all-session precise navigation ready
all-source-type precise backjump ready
all-source-type source trace ready
native PDF/PPTX/HTML/video/audio ingestion ready
assessment ready
quality governance console ready
graph editing/governance ready
cloud sync/collaboration ready
```
