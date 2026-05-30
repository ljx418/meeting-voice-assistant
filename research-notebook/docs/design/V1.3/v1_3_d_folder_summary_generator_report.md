# V1.3-D Folder Summary Generator Report

日期：2026-05-25

## 阶段

V1.3-D Folder Summary Generator。

## 目标

在用户显式确认 extract/run 后，为 md/txt 文件夹生成结构化 SummaryArtifact。

## 执行范围

- 后端在 `POST /api/workspaces/{workspace_id}/workflows/folder-summary/runs` 中支持：
  - `dry_run=false`
  - `confirm_extract=true`
- 生成 deterministic SummaryArtifact。
- ResearchNotebook adapter 支持返回 SummaryArtifact。
- 新增 V1.3-D real HTTP smoke。

## 完成内容

- 根目录总览 SummaryArtifact。
- 每个有 md/txt 文件的一级子文件夹 SummaryArtifact。
- Summary schema 包含：
  - overview
  - key topics
  - key files
  - technical points
  - reusable materials
  - risks/gaps
- coverage：
  - file_count
  - extracted_file_count
  - skipped_file_count
  - evidence_ref_count
- evidence_refs：
  - 当前为 `relative_path_only`
  - 不伪造 `source_id`
  - 不伪造 `unit_id`
  - 不伪造 `evidence_id`

## 未完成内容

- 未实现 Workflow UI。
- 未实现 Agent Planner。
- 未实现 citation click。
- 未将 evidence_refs 解析为 SourcePreview / DocumentUnit / EvidenceSpan。
- 未支持 PDF/PPTX/DOCX/video/audio/image 正文抽取。

## 测试结果

| 验收项 | 结果 | 说明 |
| --- | --- | --- |
| Backend focused tests | PASS | Summary generator confirm_extract tests 通过。 |
| Backend regression tests | PASS | Folder Connector / Source Preview / DocumentUnit / EvidenceSpan focused tests 通过。 |
| Frontend adapter tests | PASS | `dataServiceClient.test.ts` 通过。 |
| Real HTTP smoke | PASS_LIMITED | `Desktop/技术分享` 生成 11 个 SummaryArtifact。 |
| Fixture hygiene | PASS | summary markdown 已脱敏，fixtures 无本地绝对路径/cache path/artifact path。 |
| npm run check | PASS | boundary、lint、tests、build 均通过。 |

已执行命令：

```text
python3 -m pytest tests/test_target_http_folder_summary_workflow.py tests/test_target_http_folder_collections.py tests/test_target_http_source_preview.py tests/test_target_http_document_units.py tests/test_target_http_evidence_spans.py -q
npm run test -- dataServiceClient.test.ts
RN_DATA_SERVICE_BASE_URL=http://127.0.0.1:8013 npm run smoke:v1.3-d-summary-generator
npm run check
```

Smoke 结果：

```text
artifacts=11 extracted=110
final_decision=PASS_LIMITED
```

## Fixtures / Artifacts

已保存脱敏 fixtures：

```text
fixtures/real/v1_3/summary-generator/
```

文件：

- `summary-generator-success.json`
- `summary-generator-confirm-extract-rejected.json`
- `v1-3-d-summary-generator-result.json`

脱敏检查：

```text
rg -n "/Users|file://|cache_path|artifact_path|physical_path|/private/tmp|/tmp/|authorized_root" fixtures/real/v1_3/summary-generator
```

结果：无命中。

## 规格漂移评估

等级：LOW

证据：

- 只支持 md/txt。
- 需要 `confirm_extract=true` 才能读取正文。
- 不生成 source/unit/evidence id。
- 不实现 Agent Planner。
- 不实现 Workflow UI。
- 不实现 citation click。

## 虚假验收评估

等级：MEDIUM

证据：

- SummaryArtifact 已经生成，容易被误读为完整 evidence-backed summary ready。
- 当前 evidence_refs 只是 `relative_path_only`，不能点击回跳 SourcePreview / DocumentUnit / EvidenceSpan。

收敛措施：

- feature matrix 和 gap 必须明确 V1.3-D 只是 SummaryArtifact PASS_LIMITED。
- V1.3-G 前不得声明 evidence-backed summary citation ready。
- V1.3-E 只能做 Workflow UI，不得把 relative_path_only evidence_refs 伪装成 precise citation。

## 是否允许进入下一阶段

当前：YES。

原因：规格漂移 LOW，虚假验收 MEDIUM 但已有收敛措施，未触发 HIGH/BLOCKING。

## 下一阶段计划修正

下一步进入 V1.3-E Workflow UI，但必须收窄为：

1. 展示 workflow run、step timeline、logs、artifacts。
2. 支持 dry-run 和 confirmed run 两种状态。
3. 不实现 Agent Planner。
4. 不实现 citation click。
5. 不声明 arbitrary Agent ready。

## 仍不能声明

- Agent ready。
- Evidence-backed summary citation ready。
- PDF/PPTX/DOCX/video/audio 原生正文摄入 ready。
- Assessment / Governance / Cloud collaboration ready。
