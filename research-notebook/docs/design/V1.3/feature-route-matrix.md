# ResearchNotebook V1.3 Feature Route Matrix

文档状态：V1.3-A/B 计划阶段。

| Feature | Route / Wrapper | 状态 | 说明 |
| --- | --- | --- | --- |
| Agent task draft | TBD | NOT_READY | V1.3-A 仅定义合同。 |
| Workflow draft | TBD | NOT_READY | 只允许 registered template draft。 |
| Workflow run | TBD | NOT_READY | V1.3-C 后才实现。 |
| Folder scan | `POST /api/workspaces/{workspace_id}/folder-collections/scan` | PLANNED_V1.3_B | 第一版只支持 md/txt。 |
| Folder summary artifact | TBD | NOT_READY | V1.3-D 后才实现。 |
| Evidence-backed summary citation | Existing SourcePreview / DocumentUnit / EvidenceSpan wrappers | NOT_READY | V1.3-G 后才接入。 |

## 约束

- route shape 只允许在 `src/shared/api/dataServiceClient.ts`。
- feature modules 不 direct fetch。
- 不新增 `/api/v1/knowledge/*` 功能调用。
- 不展示本地绝对路径。
