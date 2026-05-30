# ResearchNotebook V1.5-E ChromeCLI / Manual E2E Report

日期：2026-05-28

## 执行状态

PASS_LIMITED。

V1.5-E 已使用 Chrome DevTools Protocol 走通真实浏览器路径。该验收使用真实 MiniMax provider 和数字人 P0 数据集，覆盖 Guide、引用问答、EvidenceSpan 高亮、Studio 四类轻量输出、资料外拒答和 cleanup。

## 环境

- 前端：`http://127.0.0.1:5173`
- 后端：`http://127.0.0.1:8003`
- 浏览器：本地 Chrome / Chromium，headless 模式
- 数据：`Desktop/技术分享/11-数字人`

## 验收结果

| 项目 | 状态 |
| --- | --- |
| 启动前端和后端 | PASS |
| 创建 Notebook | PASS |
| 导入数字人 Markdown / PDF | PASS |
| 工作区构建 | PASS |
| AI Guide 可见 | PASS |
| 引用问答可见 | PASS |
| jumpable citation 可见 | PASS |
| EvidenceSpan 高亮可见 | PASS |
| Notes 生成 | PASS |
| Study Guide 生成 | PASS |
| Briefing Doc 生成 | PASS |
| FAQ 生成 | PASS |
| 资料外问题拒答 | PASS |
| cleanup | PASS |
| blocking console/pageerror | PASS，未发现阻塞错误 |
| `/api/v1/knowledge/*` 请求 | PASS，未发现 |

## 命令证据

- `npm run smoke:v1.5-e-e2e`
  - 结果：PASS。
- `npm run check`
  - 结果：boundary checks、lint、tests、build 均通过。

## Artifacts

脱敏 JSON summary：

- `fixtures/real/v1_5/chromecli-manual-e2e/v1_5_e_chromecli_manual_e2e_result.json`

截图保存于 `.smoke-artifacts/`，不提交：

- `01-guide.png`
- `02-qa-answer.png`
- `03-citation-highlight.png`
- `04-studio-1.png`
- `04-studio-2.png`
- `04-studio-3.png`
- `04-studio-4.png`
- `05-refusal.png`

脱敏检查：

- fixture 未发现 `/Users`
- fixture 未发现 `file://`
- fixture 未发现 `cache_path`
- fixture 未发现 `artifact_path`
- fixture 未发现 `physical_path`
- fixture 未发现 API key / Authorization / Bearer

## PRD 规格检视

已覆盖：

- 导入资料后展示 Notebook Guide。
- 基于来源进行引用问答。
- citation 可跳转并高亮到来源片段。
- Studio 轻量输出 Notes / Study Guide / Briefing Doc / FAQ。
- 资料不足时拒答并显示添加来源入口。
- 3 列布局主路径可用。

未覆盖 / 不声明 ready：

- URL 正文抽取。
- Audio Overview。
- PPT 生成。
- 思维导图。
- 文档对比。
- OCR / 扫描 PDF。
- Word / PPT / 音视频原生摄入。
- all-source-type ready。

## 风险评估

- 规格漂移风险：LOW。
- 虚假验收风险：MEDIUM。

原因：

- 浏览器路径已真实通过，但验收数据仍限定为数字人 P0 数据集。
- 内容质量仍建议人工抽查，不把一次 smoke 结果扩大为所有行业和所有资料类型 ready。

收敛措施：

- V1.5-RC 仅声明 “AI digital human P0 dataset quality-smoke-ready”。
- V1.6 或后续阶段再处理 URL、OCR、多格式、重输出和更大评测集。

## 完成声明

ResearchNotebook V1.5 ChromeCLI / Manual E2E is PASS_LIMITED for the AI digital human P0 dataset.
