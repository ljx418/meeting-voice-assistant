# V1.3-RC Agent Entry Acceptance Report

日期：2026-05-26。

## 阶段范围

V1.3-RC Agent Entry ChromeCLI / Browser Acceptance。

本阶段目标是通过真实浏览器路径验证 V1.3 核心用例：

```text
递归总结 Desktop/技术分享，每个子文件夹生成一份总结。
```

## 环境

| 项 | 值 |
| --- | --- |
| Frontend URL | `http://127.0.0.1:5173` |
| data_service URL | `http://127.0.0.1:8013` |
| 浏览器 | Chrome / Chromium DevTools Protocol |
| 目录输入 | `Desktop/技术分享` |
| Smoke script | `npm run smoke:v1.3-rc-agent-entry` |

## 验收结果

| 验收项 | 状态 | 说明 |
| --- | --- | --- |
| data_service probe | PASS | `/api/workspaces` 可访问。 |
| workspace create | PASS | smoke 创建独立测试 workspace。 |
| Agent entry visible | PASS | 浏览器打开工作区后可见“文件夹总结工作流 / 智能研究助手”入口。 |
| workflow draft | PASS | 点击“生成工作流草案”后显示等待用户确认。 |
| confirmed summary run | PASS | 点击“确认并生成总结”后显示总结产物。 |
| summary evidence citation | PASS | SummaryArtifact evidence citation 可见。 |
| SourcePreviewDrawer | PASS | 点击 summary citation 后打开来源预览抽屉。 |
| DocumentUnit selection | PASS | 选中对应 DocumentUnit。 |
| EvidenceSpan highlight | PASS | 高亮元素可见且文本非空。 |
| browser console/network guard | PASS | 未观察到 `/api/v1/knowledge/*` 请求；无阻塞 pageerror。 |
| cleanup | PASS | 测试 workspace 已归档。 |

## Artifacts

- JSON fixture：`fixtures/real/v1_3/agent-entry-acceptance/agent-entry-browser-result.json`
- 截图 artifact：`.smoke-artifacts/v1_3_rc_agent_entry/.../agent-entry-summary-highlight.png`

说明：`.smoke-artifacts/` 不提交；fixture 只保留脱敏 JSON summary。

## 规格漂移评估

结果：LOW。

证据：

- 验收路径只覆盖 md/txt。
- Agent Planner 只生成 registered `folder_summary_v1` draft。
- 用户确认前不执行本地文件读取。
- summary citation 只在后端返回真实 `source_id + unit_id + evidence_id` 时可点击。
- 未开放任意工具调用。

## 虚假验收评估

结果：MEDIUM。

原因：

- 本阶段验证了一个真实目录和受限路径，但不是所有目录、所有文件类型或任意 Agent 能力。

收敛措施：

- 最终声明限定为 authorized md/txt local folder summary workflow。
- PDF/PPTX/DOCX/video/audio/image 仍不声明 ready。
- arbitrary Agent tool execution 仍不声明 ready。

## 最终声明

ResearchNotebook V1.3 Agent Folder Summary Workflow is browser-acceptance-ready for authorized md/txt local folders validated on `Desktop/技术分享`.

可声明的受限能力：

- Agent 入口可生成 registered `folder_summary_v1` draft。
- 用户确认后可运行 folder summary workflow。
- 后端可递归扫描授权目录中的 md/txt。
- 可生成每个子文件夹 summary artifact 和根目录总览。
- SummaryArtifact evidence citation 可回跳 SourcePreview / DocumentUnit / EvidenceSpan。

仍不能声明：

- arbitrary Agent tool execution ready。
- PDF/PPTX/DOCX/video/audio/image 原生正文摄入 ready。
- all-folder / all-source-type summary citation ready。
- Assessment ready。
- Quality/Governance console ready。
- Graph editing/governance ready。
- Cloud sync/collaboration ready。
