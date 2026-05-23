# ResearchNotebook V1.1-S2 All-Source-Type Contract Discovery

文档状态：S2 contract discovery 已执行；当前 data_service 只对 `text` 声明 unit-level preview，非文本 source type 仍为 NOT_READY / UNSUPPORTED。
日期：2026-05-23。

## Summary

S2 的目标是发现全来源类型合同，不实现多格式 UI，也不声明 multi-format ready。

执行命令：

```text
npm run smoke:v1.1-s2-discovery
```

结果：

```text
S2_ALL_SOURCE_TYPE_DISCOVERY_DECISION CONTRACT_DISCOVERY_COMPLETE
```

## Environment

| Item | Value |
| --- | --- |
| backend URL | `http://127.0.0.1:8003` |
| workspace_id | `rn-v11-s2-discovery-1779552792409-workspace` |
| fixture root | `fixtures/real/v1_1/all-source-type-discovery/` |

## Capability Manifest

data_service 当前 manifest 只声明：

```text
supported_source_types = text:unit
```

这意味着：

- `text` 支持 source preview、DocumentUnit、EvidenceSpan 当前路径；
- `pdf` / `pptx` / `json` / `markdown` / `html` / `video` / `audio` 未在 manifest 中声明 ready；
- 非文本 source type 不得被前端显示为 ready；
- 不能把 source trace metadata provenance 成功扩大成 full preview/unit/evidence ready。

## Discovery Matrix

| source_type | capability manifest | create registry source | native ingestion | source preview | DocumentUnit | EvidenceSpan | source trace | Decision |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| text | PASS, preview=`unit` | PASS | PASS_TEXT_SOURCE | PASS | PASS | PASS_TEXT_ROUTE_AVAILABLE | LIMITED_PASS | READY_FOR_EXISTING_V1.1_TEXT_PATH |
| pdf | NOT_READY | PASS | NOT_VERIFIED_METADATA_ONLY | UNSUPPORTED | UNSUPPORTED | NOT_READY_NOT_SMOKED | LIMITED_PASS | BLOCKED_BY_BACKEND_CONTRACT |
| pptx | NOT_READY | PASS | NOT_VERIFIED_METADATA_ONLY | UNSUPPORTED | UNSUPPORTED | NOT_READY_NOT_SMOKED | LIMITED_PASS | BLOCKED_BY_BACKEND_CONTRACT |
| json | NOT_READY | PASS | NOT_VERIFIED_METADATA_ONLY | UNSUPPORTED | UNSUPPORTED | NOT_READY_NOT_SMOKED | LIMITED_PASS | BLOCKED_BY_BACKEND_CONTRACT |
| markdown | NOT_READY | PASS | NOT_VERIFIED_METADATA_ONLY | UNSUPPORTED | UNSUPPORTED | NOT_READY_NOT_SMOKED | LIMITED_PASS | BLOCKED_BY_BACKEND_CONTRACT |
| html | NOT_READY | PASS | NOT_VERIFIED_METADATA_ONLY | UNSUPPORTED | UNSUPPORTED | NOT_READY_NOT_SMOKED | LIMITED_PASS | BLOCKED_BY_BACKEND_CONTRACT |
| video | NOT_READY | PASS | NOT_VERIFIED_METADATA_ONLY | UNSUPPORTED | UNSUPPORTED | NOT_READY_NOT_SMOKED | LIMITED_PASS | BLOCKED_BY_BACKEND_CONTRACT |
| audio | NOT_READY | PASS | NOT_VERIFIED_METADATA_ONLY | UNSUPPORTED | UNSUPPORTED | NOT_READY_NOT_SMOKED | LIMITED_PASS | BLOCKED_BY_BACKEND_CONTRACT |

## Interpretation

S2 discovered that data_service accepts registry source creation with `source_type` metadata for non-text candidates, but that is not native ingestion support. The preview and unit routes still return `source_type_not_supported` for non-text source types.

Source trace returned HTTP 200 limited provenance for the synthetic registry sources. This is useful provenance metadata, but it does not prove multi-format preview, DocumentUnit, EvidenceSpan, native file ingestion, or precise backjump support.

## Fixtures

Saved fixtures:

```text
fixtures/real/v1_1/all-source-type-discovery/
```

Per source type, the smoke saved:

- `<source_type>-source-detail.json`
- `<source_type>-preview.json`
- `<source_type>-units.json`
- `<source_type>-trace.json`

Summary:

- `capability-manifest.json`
- `s2-all-source-type-discovery-result.json`

Fixtures were sanitized. They must not contain raw filesystem paths, cache paths, artifact physical paths, stack traces, or private storage filenames.

## Next Stage Audit

S3 cannot proceed as a frontend implementation stage. S2 found no non-text source type with preview/unit/evidence backend contract ready.

Correct next stage:

```text
V1.1-S3 Multi-Format Backend Contract Enablement
```

S3 must be a data_service backend contract stage. It must choose explicit source types and implement backend contracts before ResearchNotebook can do S4 frontend integration.

Recommended S3 source type priority:

1. `markdown` or `json`, because they can plausibly produce text/section/json_node units without binary parsing.
2. `pdf`, only if data_service has a parser/extractor available.
3. `pptx`, `audio`, and `video` only after locator semantics are frozen.

## Declaration Decision

Allowed:

```text
V1.1-S2 all-source-type contract discovery is complete.
Non-text source types remain blocked by data_service backend contract for preview/unit/evidence navigation.
```

Still NOT_READY:

- all-source-type precise backjump
- all-source-type source preview
- all-source-type DocumentUnit navigation
- all-source-type EvidenceSpan highlight
- multi-format ingestion ready
- assessment / mastery
- quality governance console
- graph editing/governance
- cloud sync/collaboration
