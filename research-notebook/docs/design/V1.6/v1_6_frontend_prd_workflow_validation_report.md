# ResearchNotebook V1.6 Frontend PRD Workflow Validation Report

日期：2026-05-29

## 结论

本次针对用户反馈的“新建工作区时报 404”“点击问答后无明显反馈”“来源库只能选择单个文件”进行了复现、修复和 ChromeCLI 验收。

当前结论：

```text
CREATE_WORKSPACE_404_FIXED
SOURCE_IMPORT_422_FIXED
MULTI_FILE_IMPORT_UX_ADDED
QUESTION_PENDING_FEEDBACK_ADDED
FRONTEND_PRD_WORKFLOW_SMOKE_PASS
V1.6_RC_MANUAL_ACCEPTANCE_STILL_PENDING
```

这份报告只记录前端页面描述、来源导入、问答反馈和主工作流 smoke 结果，不能替代 V1.6-RC 人工质量验收。

## 环境

| 项 | 值 |
| --- | --- |
| frontend URL | `http://127.0.0.1:5173/` |
| data_service URL | `http://127.0.0.1:8003` |
| frontend branch / commit | `main` / `13c1f49b` |
| data_service branch / commit | `main` / `13c1f49b` |
| browser path | ChromeCLI / Chrome DevTools Protocol |

## 问题复现与根因

用户现象：

```text
Data service request failed with status 404.
```

复现判断：

- 直接调用 `POST http://127.0.0.1:8003/api/workspaces` 返回 `200 OK`。
- 前端普通 `npm run dev` 启动时，浏览器请求同源 `/api/workspaces`。
- Vite dev server 之前没有 `/api` proxy，导致请求落到 `http://127.0.0.1:5173/api/workspaces` 并返回 404。

根因：

```text
dev server missing API proxy when VITE_DATA_SERVICE_BASE_URL is not provided.
```

修复：

- 在 `vite.config.ts` 中增加 `/api` dev proxy。
- 默认转发到 `http://127.0.0.1:8003`。
- 如设置 `VITE_DATA_SERVICE_BASE_URL`，proxy target 使用该环境变量。

修复后验证：

```text
POST http://127.0.0.1:5173/api/workspaces -> 200 OK
```

## UX 修复记录

### 1. 来源导入合同兼容

问题：

- ChromeCLI 用户路径进入工作区后，文本来源导入返回 `422 Unprocessable Content`。
- 根因是前端把 `source_type` / `content_format` 放进了 `texts[0]`，当前 data_service 文本导入 schema 禁止这些字段。

修复：

- `src/shared/api/dataServiceClient.ts` 的文本导入分支只提交 `title`、`content`、`metadata`。
- `source_type` 仅作为 metadata 保留，不再污染后端 text item schema。

### 2. 多文件导入 UX

修复：

- 来源库文件输入支持 `multiple`。
- 多文件选择后显示“将按顺序导入 N 个文件”。
- 提交按钮显示“导入 N 个来源”。
- 批量导入时逐个上传并显示完成数、失败数和当前文件。
- TXT / Markdown / PDF 根据文件扩展名自动推断来源类型。

边界：

- 该能力只改善导入 UX，不代表所有文件格式解析 ready。
- 仍只声明 TXT / Markdown / 可抽取文本 PDF / limited URL 的限定支持。

### 3. 问答反馈 UX

修复：

- 点击 Suggested Question 或提交问题后，问答区域会滚动到可见位置。
- 请求中显示“正在基于来源生成回答”。
- 回答区域使用局部 `aria-live`，避免用户误以为点击无反应。

边界：

- 该修复解决交互反馈，不替代 QA 内容质量验收。

## ChromeCLI 验收结果

### 1. 创建工作区

命令：

```text
RN_VISIBLE_E2E_KEEP_BROWSER_OPEN=0 RN_VISIBLE_E2E_STEP_DELAY_MS=0 npm run smoke:v1.1-visible-user-e2e
```

结果：

```text
PASS visible Chrome opened app
PASS workspace create and enter
```

说明：

- 浏览器打开前端成功。
- 通过页面表单填写工作区名称成功。
- 点击创建后成功进入 `/workspaces/{workspace_id}`。
- 原 404 已修复。

完整可见用户路径结果：

```text
PASS visible Chrome opened app
PASS workspace create and enter
PASS text source import visible
PASS text preview and unit visible
PASS text evidence highlight visible
PASS markdown source import visible
PASS markdown preview and unit visible
PASS markdown evidence highlight visible
PASS json source import visible
PASS json preview and unit visible
PASS json evidence highlight visible
PASS source trace drawer visible
PASS session create visible
PASS session ingest visible
PASS session build visible
PASS session evidence highlight visible
PASS browser console/network guard
V1_1_VISIBLE_USER_E2E_DECISION PASS
PASS workspace archive cleanup
```

说明：

- 该路径模拟普通用户从首页创建工作区、导入来源、预览、提问、点击 citation、查看高亮、使用会话问答。
- 旧的“进入工作区后 Uncaught / 来源导入 422”问题已修复。

### 2. PRD 主路径 smoke

命令：

```text
npm run smoke:v1.5-e-e2e
```

结果：

```text
PASS startup
PASS seed workspace/source/build
PASS browser guide visible
PASS browser qa citation visible
PASS browser citation highlight
PASS browser studio Notes
PASS browser studio Study Guide
PASS browser studio Briefing Doc
PASS browser studio FAQ
PASS browser refusal visible
PASS cleanup
```

说明：

- Guide-first 路径可见。
- 基于来源的引用问答可见。
- citation 可回跳并高亮。
- Studio 四类轻量输出可生成。
- 资料外问题拒答可见。

限制：

- 该脚本通过后端预置 workspace/source/build，再进入浏览器验收，不完全等同于用户从空白首页手工导入全路径。
- 该结果不能替代 V1.6-RC 人工质量评分。

## PRD 页面描述与工作流检查

| PRD 要求 | 当前前端观察 | 状态 | 备注 |
| --- | --- | --- | --- |
| 创建 / 列表 / 打开 Notebook | 首页提供创建工作区、工作区列表和打开入口 | PASS_WITH_NAMING_GAP | UI 中文使用“工作区”，PRD 使用 Notebook；建议后续统一为“笔记本 / Notebook”。 |
| Guide-first | 工作区内可展示 Notebook Guide | PASS | ChromeCLI 已验证 Guide 可见。 |
| Sources 导入与来源列表 | 来源库、导入来源、状态、预览入口存在 | PASS_LIMITED | 支持 TXT / Markdown / 可抽取文本 PDF / limited URL；不代表全格式 ready。 |
| 多文件选择 | 来源导入文件控件支持一次选择多个文件并顺序导入 | PASS_LIMITED | 改善 P0 批量导入体验；不扩大格式 ready 范围。 |
| Chat / 引用问答 | 工作区提问、回答、evidence citation 存在 | PASS | ChromeCLI 已验证 citation 可见。 |
| 问答点击反馈 | 提问后显示局部 loading 并滚动到问答区域 | PASS | 解决“点击问答后无任何反应”的可见反馈问题。 |
| citation 跳转定位 | SourcePreview / DocumentUnit / EvidenceSpan 路径可用 | PASS_LIMITED | 当前限定 data_service 支持的来源和 evidence span。 |
| Studio 轻量输出 | Notes / Study Guide / Briefing Doc / FAQ 可生成 | PASS_LIMITED | 需要人工检查导出文件和输出质量。 |
| 资料不足拒答 | 资料外问题拒答可见 | PASS_LIMITED | 仍需人工抽样评分拒答正确性。 |
| Phase 2/3 输出 | Audio / PPT / Mindmap / Compare 应保持 disabled | NEED_MANUAL_CHECK | 本次 ChromeCLI 未覆盖所有 disabled shell 的后端请求拦截。 |
| 三列 IA | 页面具备 Sources / Chat / Studio 功能区 | PASS_WITH_UX_REVIEW_NEEDED | 需要人工确认视觉布局是否符合 PRD 预期的 3 列阅读体验。 |

## 仍需人工验收

以下项目仍必须按 V1.6-RC 计划由人工检查：

- 数字人 P0 Markdown / PDF 从空白 Notebook 手工导入，并人工确认多文件选择体验。
- Notebook Guide 内容质量。
- QA citation 正确性与可定位率。
- Studio Markdown / JSON 导出文件人工打开检查。
- 多数据集质量评分。
- Research report 的 supported_conclusions / inferences / missing_evidence。
- Phase 2/3 disabled shell 不发起生成请求。

## 风险评估

| 风险 | 等级 | 说明 |
| --- | --- | --- |
| 规格漂移 | MEDIUM | 页面主路径已贴近 PRD，但 Notebook 命名仍显示为“工作区”，且三列布局体验仍需人工确认。 |
| 虚假验收 | HIGH | ChromeCLI smoke 不能证明内容质量，仍不能自动声明 V1.6 完成。 |

## 最终声明边界

本次可以声明：

```text
Frontend create workspace 404 is fixed for local Vite dev startup.
ChromeCLI visible-user smoke confirms workspace/source/question/citation/session paths are browser-reachable.
ChromeCLI PRD smoke confirms the Guide / QA / Studio path is browser-reachable.
```

仍不能声明：

```text
ResearchNotebook V1.6 completed.
V1.6 final acceptance passed.
all websites URL extraction ready.
OCR ready.
Audio / PPT / Mindmap / Document comparison ready.
all-domain Research ready.
```
