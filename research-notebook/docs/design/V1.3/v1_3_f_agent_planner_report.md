# V1.3-F Agent Planner 阶段报告

日期：2026-05-25。

## 阶段范围

V1.3-F Agent Planner。

本阶段只实现受限 Agent Planner：

- 用户自然语言目标生成 `folder_summary_v1` 工作流草案。
- 草案状态为 `awaiting_approval`。
- 草案只包含已注册模板、权限要求、目录提示和步骤。
- 用户确认前不运行 workflow。
- 用户确认前不扫描或读取本地目录。
- 不开放任意工具调用。

## 完成内容

- data_service 新增 `POST /api/workspaces/{workspace_id}/agent-workflows/draft`。
- 后端新增 `agent_workflow_contract.py`，仅匹配 `Desktop/技术分享` folder summary 用例。
- 后端 focused tests 覆盖：
  - registered folder summary goal 成功。
  - unsupported goal 返回 422。
  - route 暴露且不新增 `/api/v1/knowledge/*`。
- ResearchNotebook adapter 新增真实 `agentWorkflows.createDraft` 调用。
- `AgentWorkflowPanel` 增加任务指令输入和“生成工作流草案”按钮。
- UI 展示 workflow draft、权限要求、目录提示和等待用户确认状态。
- `agentWorkflows.getDraft/startRun` 仍保持 `capability_missing`，避免误导为完整 Agent runtime。
- 新增真实 HTTP smoke：`npm run smoke:v1.3-f-agent-planner`。
- 新增脱敏 fixtures：`fixtures/real/v1_3/agent-planner/`。

## 未完成内容

- 未实现自由 Agent Planner。
- 未实现任意工具调用。
- 未实现自动运行 workflow。
- 未实现 summary citation 回跳。
- 未实现 browser/manual Agent 入口最终验收。

## 验证结果

| 验证项 | 状态 | 说明 |
| --- | --- | --- |
| backend focused tests | PASS | `tests/test_target_http_agent_workflows.py` 通过。 |
| frontend adapter/UI tests | PASS | `dataServiceClient.test.ts`、`WorkspacePage.test.tsx` 通过。 |
| real HTTP smoke | PASS_LIMITED | `RN_DATA_SERVICE_BASE_URL=http://127.0.0.1:8013 npm run smoke:v1.3-f-agent-planner` 通过。 |
| unsupported goal | PASS | 非注册目标返回 HTTP 422。 |
| path hygiene | PASS | fixture 不保存本地绝对路径。 |

## 规格漂移评估

结果：LOW。

证据：

- Planner 只允许生成 `folder_summary_v1`。
- 不支持自由工具调用。
- 不读取目录、不抽取正文、不自动运行。
- unsupported goal 被 422 拒绝。

## 虚假验收评估

结果：MEDIUM。

原因：

- UI 已出现“生成工作流草案”，容易被误解为完整 Agent ready。

收敛措施：

- UI 文案明确“草案生成不会读取本地目录”和“等待用户确认”。
- `startRun` 仍不走 Agent route，只允许手动确认后的 deterministic workflow。
- 文档继续禁止声明 arbitrary Agent tool execution ready。

## 是否允许进入下一阶段

允许进入 V1.3-G。

理由：

- 规格漂移 LOW。
- 虚假验收 MEDIUM，但已有收敛措施。
- 未触发 HIGH / BLOCKING 停止规则。

## 下一阶段计划修正

V1.3-G 只能接入 SummaryArtifact 的 evidence-backed citation。

V1.3-G 必须保持以下边界：

- 只处理 summary artifact 中真实携带 `source_id + unit_id + evidence_id` 的 evidence_refs。
- 当前 `relative_path_only` evidence_refs 只能显示为不可跳转。
- 不得伪造 source/unit/evidence id。
- 不得把 relative_path 当作 filesystem path。
- 如果后端还没有 source-backed summary evidence，则 V1.3-G 应声明 NOT_READY 或 PARTIAL_READY，不得伪装 PASS。

## 阶段声明

ResearchNotebook V1.3-F Agent Planner is PASS_LIMITED for generating a registered `folder_summary_v1` workflow draft from the supported Desktop/技术分享 goal.

仍不能声明：

- Agent ready。
- arbitrary Agent tool execution ready。
- Workflow fully ready。
- Evidence-backed summary citation ready。
- PDF/PPTX/DOCX/video/audio 原生摄入 ready。
- Assessment / Governance / Cloud collaboration ready。
