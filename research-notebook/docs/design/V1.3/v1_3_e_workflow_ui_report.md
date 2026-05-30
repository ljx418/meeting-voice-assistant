# V1.3-E Workflow UI Report

日期：2026-05-25

## 阶段

V1.3-E Workflow UI。

## 目标

让用户在工作区页面直接运行 `folder_summary_v1`，查看 step timeline、run report 和 SummaryArtifact。

## 完成内容

- Agent 工作流面板从 disabled shell 升级为工作流 UI。
- 支持填写授权目录。
- 支持模拟运行工作流。
- 支持确认并生成总结。
- 展示 WorkflowRun 状态。
- 展示 step timeline。
- 展示 run report。
- 展示 SummaryArtifact markdown。
- 明确提示：
  - 当前只支持 md/txt。
  - Agent Planner 未启用。
  - summary citation 回跳未启用。

## 未完成内容

- 未实现自然语言 Agent Planner。
- 未实现 Workflow draft 生成。
- 未实现 retry API。
- 未实现 summary citation click。
- 未实现 evidence-backed summary navigation。

## 测试结果

| 验收项 | 结果 | 说明 |
| --- | --- | --- |
| Workflow UI tests | PASS | WorkspacePage 新增工作流 UI smoke。 |
| Adapter tests | PASS | dataServiceClient 64 tests。 |
| npm run check | PASS | boundary、lint、tests、build 均通过。 |

已执行命令：

```text
npm run test -- WorkspacePage.test.tsx dataServiceClient.test.ts
npm run check
```

## 规格漂移评估

等级：LOW

证据：

- UI 只调用 dataServiceClient wrapper。
- feature 层无 direct fetch。
- 未实现 Agent Planner。
- 未实现 citation click。
- 未扩大文件格式支持。

## 虚假验收评估

等级：MEDIUM

证据：

- 前端出现“Agent 工作流”入口并且能运行 workflow，容易被误读为自然语言 Agent ready。
- 当前仍需要用户手动填写授权目录，不是自然语言 planner。

收敛措施：

- UI 文案明确 Agent Planner 未启用。
- V1.3-F 前不得声明 Agent ready。
- V1.3-RC 前不得声明最终手工验收完成。

## 是否允许进入下一阶段

当前：YES。

原因：规格漂移 LOW，虚假验收 MEDIUM 且已写入收敛措施，未触发 HIGH/BLOCKING。

## 下一阶段计划修正

下一步进入 V1.3-F Agent Planner：

1. 只允许将自然语言转换为 registered template draft。
2. 不允许任意工具调用。
3. 用户确认前不得运行。
4. draft 必须展示目录、排除规则、权限要求和步骤。
5. 不声明 arbitrary Agent ready。

## 仍不能声明

- Agent Planner ready。
- arbitrary Agent tool execution ready。
- evidence-backed summary citation ready。
- PDF/PPTX/DOCX/video/audio 原生正文摄入 ready。
