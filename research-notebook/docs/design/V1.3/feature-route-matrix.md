# ResearchNotebook V1.3 Feature Route Matrix

文档状态：V1.3 完整开发计划已落盘，route 仍按阶段冻结。

| Feature | Route / Wrapper | 状态 | 说明 |
| --- | --- | --- | --- |
| Governance gate | Docs / stage reports | PASS | 每阶段必须评估规格漂移和虚假验收。 |
| Agent task draft | `POST /api/workspaces/{workspace_id}/agent-workflows/draft` / `dataServiceClient.agentWorkflows.createDraft` | PASS_LIMITED | 只允许 supported Desktop/技术分享 goal 生成 `folder_summary_v1` draft；unsupported goal 返回 422。 |
| Workflow draft follow-up | `dataServiceClient.agentWorkflows.getDraft` | DISABLED_READY | 后续 draft 查询 route 未启用；当前 createDraft response 已包含 draft。 |
| Workflow run | `POST /api/workspaces/{workspace_id}/workflows/folder-summary/runs` / `dataServiceClient.folderSummaryWorkflows.startRun` | PASS_LIMITED | 仅 dry-run runtime；step timeline 和 run report 通过，不生成 SummaryArtifact。 |
| Folder scan | `POST /api/workspaces/{workspace_id}/folder-collections/scan` / `dataServiceClient.folderCollections.scan` | PASS_LIMITED | 第一版只支持 md/txt dry-run manifest；后端 focused tests、adapter tests、`Desktop/技术分享` real HTTP smoke 已通过。 |
| Folder summary artifact | `POST /api/workspaces/{workspace_id}/workflows/folder-summary/runs` with `dry_run=false` and `confirm_extract=true` | PASS_LIMITED | 生成 SummaryArtifact；evidence_refs 仅 `relative_path_only`，不可声明 precise citation ready。 |
| Workflow UI | `AgentWorkflowPanel` -> `agentWorkflows.createDraft` + `folderSummaryWorkflows.startRun` | PASS_LIMITED | 支持生成 registered draft、手动目录输入、dry-run、confirmed run、step timeline、artifact panel；不代表自由 Agent ready。 |
| Evidence-backed summary citation | SummaryArtifact `source_unit_span` -> existing SourcePreview / DocumentUnit / EvidenceSpan wrappers | PASS_LIMITED | confirmed md/txt `folder_summary_v1` run 可回跳；`relative_path_only` 仍不可跳转。 |
| Agent entry browser acceptance | `npm run smoke:v1.3-rc-agent-entry` | PASS_LIMITED | Chrome/Browser 走通 Agent 入口、draft、confirmed run、summary citation highlight；仅限 authorized md/txt local folder。 |
| PRD alignment UX | Existing V1.3 UI routes | PASS_LIMITED | 用户可见 Agent 主流程清理开发态文案，并对齐低噪音研究工作台体验；不新增 route。 |

## 约束

- route shape 只允许在 `src/shared/api/dataServiceClient.ts`。
- feature modules 不 direct fetch。
- 不新增 `/api/v1/knowledge/*` 功能调用。
- 不展示本地绝对路径。
- 任一阶段规格漂移或虚假验收风险为 HIGH / BLOCKING 时，停止进入下一阶段。
- V1.3-C 只能消费 V1.3-B dry-run manifest；不得直接实现自由 Agent Planner 或 evidence-backed summary。
- V1.3-F 只允许 registered template draft；不得开放任意工具调用或自动读取本地目录。
- V1.3-G 只允许真实 `source_id + unit_id + evidence_id` 的 SummaryArtifact evidence_refs 回跳；不得伪造 citation。
