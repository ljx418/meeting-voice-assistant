# V1.3-A Agent Workflow Contract Discovery 阶段报告

文档状态：阶段完成报告。
日期：2026-05-25。

## 阶段

V1.3-A Agent Workflow Contract Discovery。

## 目标

定义 Agent Workflow 的最小合同，补强 DTO、adapter shell 和 disabled UI。当前不执行真实 workflow，不读取本地目录。

## 执行范围

- 补强 `AgentTask`、`Workflow`、`WorkflowRun`、`WorkflowStep`、`FolderCollection`、`FolderNode`、`FolderFile`、`SkippedFile`、`SummaryArtifact`、`EvidenceRef` 类型。
- 增加 `agentWorkflows` adapter shell。
- 增加 Agent Workflow disabled UI。
- 补充 V1.3-A/B 合同文档。

## 完成内容

- `src/shared/types/api.ts` 已增加 V1.3-A 合同类型。
- `src/shared/api/dataServiceClient.ts` 已增加 `agentWorkflows.createDraft/getDraft/startRun` shell，统一返回 `capability_missing`。
- `src/shared/components/AgentWorkflowDisabledPanel.tsx` 已增加禁用入口。
- 工作区页面已显示 Agent Workflow disabled panel。
- 单元测试覆盖 adapter shell 不访问任何 route。
- UI smoke 覆盖 disabled / contract required / no local folder access before authorization。

## 未完成内容

- 未实现真实 Agent Planner。
- 未实现 workflow run。
- 未实现 folder scan。
- 未读取 `Desktop/技术分享`。
- 未声明 Agent ready / Workflow ready / Local Folder Connector ready。

## 测试结果

已通过：

```bash
npm run check
```

结果：

- boundary checks passed。
- lint passed。
- tests passed：105 tests。
- build passed。

## fixtures / artifacts

本阶段不产生真实 fixtures。V1.3-B 后端合同阶段才允许生成 `fixtures/real/v1_3/folder-collections/`。

## 文档更新

- `docs/design/V1.3/v1_3_agent_workflow_contract.md`
- `docs/design/V1.3/v1_3_local_folder_connector_contract.md`
- `docs/design/V1.3/v1_3_a_agent_workflow_contract_discovery_report.md`

## 规格漂移评估

LOW。

证据：

- 没有读取本地目录。
- 没有执行 workflow。
- 没有实现 Agent Planner。
- 没有新增真实 Agent route。

## 虚假验收评估

MEDIUM。

证据：

- Agent Workflow 入口已经出现在工作区页面，可能被误解为 Agent ready。

收敛措施：

- UI 明确显示 disabled / contract required。
- UI 明确说明用户授权前不会访问 `Desktop/技术分享` 或任何本地目录。
- adapter shell 返回 `capability_missing`，且测试确认不会发起 fetch。

## 是否允许进入下一阶段

YES。

## 下一阶段计划修正

V1.3-B 只能先执行 Local Folder Connector Backend 合同和 smoke。必须保留：

- 第一次 scan 使用 `dry_run=true`。
- `permission_grant_id` 必填。
- `follow_symlinks=false`。
- response / fixture / report 不得包含 `authorized_root` 或本地绝对路径。
- `.md` / `.txt` 是唯一默认 supported extensions。

## 仍不能声明

- Agent ready。
- Workflow ready。
- Local Folder Connector ready。
- Folder Summary ready。
- PDF/PPTX/DOCX/video/audio ready。
- arbitrary Agent tool execution ready。
