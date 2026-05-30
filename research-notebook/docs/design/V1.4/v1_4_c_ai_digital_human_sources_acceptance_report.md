# ResearchNotebook V1.4-C AI 数字人资料包 Sources P0 验收报告

日期：2026-05-26

## 验收结论

最终决策：PASS_LIMITED。

AI 数字人资料包已用于 V1.4-C Sources P0 验收：

- Markdown：PASS。
- TXT 派生样本：PASS。
- PDF 真实样本：PASS_LIMITED，当前前端/脚本可通过浏览器式 base64 文件上传合同创建 PDF source，并完成正文抽取、preview 和 citation。

因此，V1.4-C 可以声明 Markdown / TXT / 可抽取文本 PDF 的 Sources P0 后端 smoke 通过。仍不能声明完整浏览器本地上传 UX、扫描版 PDF、OCR 或 PRD Phase 1 全量 ready。

## 验收材料

资料包标签：`技术分享/11-数字人/AI数字人资料包`

使用文件：

- `01_industry_overview.md`
- `02_technology_trends.md`
- `05_policy_and_risks.md`
- `sources_index.md`

派生样本：

- `fixtures/manual/v1_4/sources-p0/ai-digital-human-sample.txt`
- `fixtures/manual/v1_4/sources-p0/ai-digital-human-real-sample.pdf`
- `fixtures/manual/v1_4/sources-p0/material-manifest.json`

说明：PDF 样本来自用户提供的 `AI数字人产业发展报告_2026-05-26.pdf`，已复制到 manual fixtures。当前验收证明该可抽取文本 PDF 能完成后端登记、正文抽取、preview 和 citation。

## Smoke 结果

命令：

```bash
npm run smoke:v1.4-sources-p0
```

结果：

| 验收项 | 结果 | 说明 |
| --- | --- | --- |
| material preparation | PASS | 数字人 Markdown/TXT/PDF 样本已准备。 |
| target route probe | PASS | data_service 可访问。 |
| workspace create | PASS | 创建 smoke workspace。 |
| markdown import | PASS | 返回 `source_id`。 |
| txt import | PASS | 返回 `source_id`。 |
| pdf browser upload import | PASS | 通过 base64 文件上传合同返回 `source_id`。 |
| source list | PASS | source list 可用。 |
| workspace build | PASS | build completed。 |
| markdown preview | PASS | preview 有文本。 |
| txt preview | PASS | preview 有文本。 |
| markdown query citation | PASS | query 返回 citation-like evidence。 |
| txt query citation | PASS | query 返回 citation-like evidence。 |
| pdf preview | PASS | HTTP 200，`preview_available=true`，分类 `PDF_EXTRACTED`。 |
| pdf query citation | PASS | query 返回 citation-like evidence。 |
| fixture hygiene | DEGRADED | 保存 fixture 已脱敏；原始 payload 有 path-like 值被 redacted。 |
| cleanup | PASS | workspace 已归档清理。 |

PDF 分类：PDF_EXTRACTED。

## Fixtures

保存位置：`fixtures/real/v1_4/sources-p0/`

核心文件：

- `markdown-import-success.json`
- `txt-import-success.json`
- `pdf-import-attempt.json`
- `pdf-preview-attempt.json`
- `markdown-preview.json`
- `txt-preview.json`
- `markdown-query-citation.json`
- `txt-query-citation.json`
- `pdf-query-citation.json`
- `v1_4_sources_p0_result.json`
- `workspace-build-result.json`
- `workspace-cleanup.json`

敏感路径检查：

```bash
rg -n "/Users|file://|cache_path|artifact_path|physical_path|/private/tmp|/tmp/" fixtures/manual/v1_4/sources-p0 fixtures/real/v1_4/sources-p0
```

结果：无命中。

## 规格漂移评估

风险等级：MEDIUM。

原因：Markdown/TXT/PDF 浏览器式上传 smoke 已通过，但不能扩大成 OCR、扫描版 PDF、PPT、音视频或图片 ready。

收敛措施：状态使用 `PASS_LIMITED`，下一阶段进入 V1.4-D Notebook Guide，不扩大到扫描版 PDF/OCR/多格式 ready。

## 虚假验收评估

风险等级：MEDIUM。

原因：真实 PDF 已有正文抽取、preview 和 citation 能力，但还不能代表扫描版 PDF、原版页面定位、完整浏览器上传 UX 或 PRD Phase 1 全量 ready。

推进决策：没有 HIGH 风险，可以进入 V1.4-D Notebook Guide。

## 下一阶段建议

V1.4-D Notebook Guide。

最低要求：

- 基于当前 Notebook sources 生成 Overview / Key Topics / Suggested Questions。
- Suggested Questions 能进入 Chat 提问路径。
- 资料不足时不伪造 Guide。
- TXT / Markdown 回归保持通过。
- smoke 保存脱敏 fixtures。
