# ResearchNotebook V1.2 Feature Route Matrix

文档状态：V1.2 markdown/json 产品化基线。

| Feature | Route / Wrapper | 当前状态 | 说明 |
| --- | --- | --- | --- |
| Capability manifest | `capabilities.get(workspaceId)` | PASS | 继续使用 V1.1 capability contract。 |
| Source preview | `sources.preview(workspaceId, sourceId)` | PASS_TEXT_MARKDOWN_JSON | text/markdown/json 已验证；其他格式不能声明 ready。 |
| DocumentUnit list | `sources.listUnits(workspaceId, sourceId)` | PASS_TEXT_MARKDOWN_JSON | markdown/json 已由 V1.1-S3/S4 验证。 |
| DocumentUnit detail | `sources.getUnit(workspaceId, sourceId, unitId)` | PASS_TEXT_MARKDOWN_JSON | unit_id 必须来自后端 response。 |
| EvidenceSpan detail | `sources.getEvidenceSpan(workspaceId, sourceId, unitId, evidenceId)` | PASS_TEXT_MARKDOWN_JSON | 仅支持已冻结 offset contract。 |
| Source trace | `sources.trace(workspaceId, sourceId)` | LIMITED_PASS_TEXT | RC4 scoped source trace，不扩大到所有格式。 |
| PDF/PPTX/HTML/video/audio | 同上，需 manifest 支持 | NOT_READY | 后端合同、fixtures、smoke 均未完成。 |

## Route 约束

- 真实 route shape 只允许在 `src/shared/api/dataServiceClient.ts`。
- feature modules 不 direct fetch。
- feature modules 不拼 `/api/...` route string。
- artifact_ref 只作为 metadata。
