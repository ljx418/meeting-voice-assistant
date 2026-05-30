# V1.3-G Evidence-backed Summary 阶段报告

日期：2026-05-25。

## 阶段范围

V1.3-G Evidence-backed Summary。

本阶段目标是让 SummaryArtifact 中的 evidence_refs 从 `relative_path_only` 升级为可解析的 `source_unit_span`，并允许前端点击 summary citation 回跳到 SourcePreviewDrawer / DocumentUnit / EvidenceSpan。

## 完成内容

- data_service 在 confirmed folder summary run 中注册 md/txt 文件为 workspace source。
- SummaryArtifact `evidence_refs` 返回：
  - `source_id`
  - `source_title`
  - `unit_id`
  - `evidence_id`
  - `snippet`
  - `evidence_status=source_unit_span`
- `source_id + unit_id` 可解析 DocumentUnit detail route。
- `source_id + unit_id + evidence_id` 可解析 EvidenceSpan detail route。
- ResearchNotebook SummaryArtifact UI 已显示可回跳 evidence citation。
- 点击 summary evidence citation 会复用 SourcePreviewDrawer，加载 unit detail，并显示 EvidenceSpan highlight。
- 新增真实 HTTP smoke：`npm run smoke:v1.3-g-evidence-backed-summary`。
- 新增脱敏 fixtures：`fixtures/real/v1_3/evidence-backed-summary/`。

## 未完成内容

- 未做 ChromeCLI / manual 全流程验收。
- 未声明 PDF/PPTX/DOCX/video/audio 原生正文摄入 ready。
- 未声明 arbitrary Agent tool execution ready。
- 未声明 Assessment / Governance / Cloud collaboration ready。

## 验证结果

| 验证项 | 状态 | 说明 |
| --- | --- | --- |
| backend focused tests | PASS | Folder summary / folder collection / Agent draft / V1.1 preview-unit-evidence focused tests 通过。 |
| frontend tests | PASS | SummaryArtifact citation UI 已由 WorkspacePage smoke 覆盖。 |
| real HTTP smoke | PASS_LIMITED | `RN_DATA_SERVICE_BASE_URL=http://127.0.0.1:8013 npm run smoke:v1.3-g-evidence-backed-summary` 通过。 |
| unit detail resolution | PASS | Summary evidence 的 `source_id + unit_id` 可解析。 |
| EvidenceSpan resolution | PASS | Summary evidence 的 `source_id + unit_id + evidence_id` 可解析。 |
| path hygiene | PASS | fixtures 不保存本地绝对路径、cache path 或 artifact physical path。 |

## 规格漂移评估

结果：LOW。

证据：

- 仍只支持 md/txt。
- 不解析 PDF/PPTX/DOCX/video/audio/image。
- 不把 `relative_path` 当作 filesystem path。
- 不开放任意 Agent 工具调用。
- citation 只在后端返回真实 `source_id + unit_id + evidence_id` 时启用。

## 虚假验收评估

结果：MEDIUM。

原因：

- Summary citation 已能回跳，容易被误解为全量多格式 evidence-backed summary ready。

收敛措施：

- 文档和 UI 保持范围限定：仅 data_service 支持的 md/txt folder_summary_v1 confirmed run。
- `relative_path_only` evidence 仍显示为不可跳转，不伪造 source/unit/evidence id。
- V1.3-RC 必须用 ChromeCLI / manual 跑完整 Agent 入口后，才可声明最终验收通过。

## 是否允许进入下一阶段

允许进入 V1.3-RC。

理由：

- 规格漂移 LOW。
- 虚假验收 MEDIUM，但已有收敛措施。
- 未触发 HIGH / BLOCKING 停止规则。

## 下一阶段计划修正

V1.3-RC 需要用真实浏览器路径完成：

1. 打开 ResearchNotebook。
2. 进入 Agent 工作流入口。
3. 输入“递归总结 Desktop/技术分享，每个子文件夹生成一份总结”。
4. 生成工作流草案。
5. 用户确认并生成总结。
6. 查看 step timeline、skipped files、summary artifacts。
7. 点击 summary evidence citation。
8. 验证 SourcePreviewDrawer 打开、unit 选中、EvidenceSpan 高亮可见。

V1.3-RC 仍不得声明：

- all-source-type summary citation ready。
- arbitrary Agent tool execution ready。
- PDF/PPTX/DOCX/video/audio 原生摄入 ready。
- Assessment / Governance / Cloud collaboration ready。

## 阶段声明

ResearchNotebook V1.3 Evidence-backed Summary is PASS_LIMITED for confirmed md/txt folder_summary_v1 runs under the supported local folder connector path.

仍不能声明：

- V1.3 final manual/browser acceptance ready。
- arbitrary Agent tool execution ready。
- all-source-type summary citation ready。
- PDF/PPTX/DOCX/video/audio 原生摄入 ready。
- Assessment / Governance / Cloud collaboration ready。
