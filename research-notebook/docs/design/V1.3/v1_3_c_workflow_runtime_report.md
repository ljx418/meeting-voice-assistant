# V1.3-C Deterministic Folder Summary Workflow Runtime Report

日期：2026-05-25

## 阶段

V1.3-C Deterministic Folder Summary Workflow Runtime。

## 目标

实现确定性 `folder_summary_v1` dry-run runtime，生成可审计的 WorkflowRun、Step timeline 和 run report。

## 执行范围

- 后端新增 `POST /api/workspaces/{workspace_id}/workflows/folder-summary/runs`。
- ResearchNotebook adapter 新增 `dataServiceClient.folderSummaryWorkflows.startRun`。
- 新增 V1.3-C real HTTP smoke。
- 当前只做 dry-run runtime，不抽取正文、不生成 SummaryArtifact、不写 artifacts。

## 完成内容

- Workflow template：`folder_summary_v1`。
- Step timeline：
  - `scan_folder`: completed
  - `extract_text`: skipped
  - `group_by_subfolder`: completed
  - `create_sources`: skipped
  - `summarize_folder`: skipped
  - `generate_index_report`: skipped
  - `write_artifacts`: skipped
- WorkflowRun run report：
  - scanned file count
  - manifest file count
  - skipped file count
  - folder count
  - generated artifact count = 0
- Guardrails：
  - `dry_run=false` rejected。
  - 非 md/txt include 继续被拒绝。
  - logs 不含绝对路径。

## 未完成内容

- 未抽取文件正文。
- 未生成 SummaryArtifact。
- 未创建 source。
- 未实现 retry API。
- 未实现 Workflow UI。
- 未实现 Agent Planner。
- 未实现 evidence-backed summary citation。

## 测试结果

| 验收项 | 结果 | 说明 |
| --- | --- | --- |
| Backend focused tests | PASS | `test_target_http_folder_summary_workflow.py` 通过。 |
| Backend regression tests | PASS | Folder Connector / Source Preview / DocumentUnit / EvidenceSpan focused tests 通过。 |
| Frontend adapter tests | PASS | `dataServiceClient.test.ts` 通过。 |
| Real HTTP smoke | PASS_LIMITED | `Desktop/技术分享` dry-run workflow 通过。 |
| Fixture hygiene | PASS | workflow-runtime fixtures 无本地绝对路径/cache path/artifact path。 |
| npm run check | PASS | boundary、lint、tests、build 均通过。 |

已执行命令：

```text
python3 -m pytest tests/test_target_http_folder_summary_workflow.py tests/test_target_http_folder_collections.py -q
python3 -m pytest tests/test_target_http_folder_summary_workflow.py tests/test_target_http_folder_collections.py tests/test_target_http_source_preview.py tests/test_target_http_document_units.py tests/test_target_http_evidence_spans.py -q
npm run test -- dataServiceClient.test.ts
RN_DATA_SERVICE_BASE_URL=http://127.0.0.1:8013 npm run smoke:v1.3-c-workflow-runtime
npm run check
```

Smoke 结果：

```text
steps=7 files=110 skipped=1018
final_decision=PASS_LIMITED
```

## Fixtures / Artifacts

已保存脱敏 fixtures：

```text
fixtures/real/v1_3/workflow-runtime/
```

文件：

- `workflow-runtime-dry-run-success.json`
- `workflow-runtime-non-dry-run-rejected.json`
- `v1-3-c-workflow-runtime-result.json`

脱敏检查：

```text
rg -n "/Users|file://|cache_path|artifact_path|physical_path|/private/tmp|/tmp/|authorized_root" fixtures/real/v1_3/workflow-runtime
```

结果：无命中。

## 规格漂移评估

等级：LOW

证据：

- 未实现自由 Agent Planner。
- 未执行正文抽取。
- 未生成 SummaryArtifact。
- 未创建 evidence-backed citation。
- `dry_run=false` 仍被拒绝。

## 虚假验收评估

等级：LOW

证据：

- 报告明确 V1.3-C 只是 dry-run runtime。
- `generated_artifact_count=0`，不会误写为 Folder Summary ready。
- `summarize_folder` 和 `write_artifacts` 均为 skipped。

## 是否允许进入下一阶段

当前：YES。

原因：规格漂移 LOW、虚假验收 LOW，未触发 HIGH/BLOCKING 停止规则。

## 下一阶段计划修正

下一步进入 V1.3-D Folder Summary Generator，但必须收窄为：

1. 只有用户确认 extract/run 后才能读取 md/txt 正文。
2. 只生成结构化 SummaryArtifact。
3. 不实现 Agent Planner。
4. 不实现 Workflow UI。
5. 不实现 evidence-backed citation click。
6. 不声明 arbitrary Agent ready。

## 仍不能声明

- Agent ready。
- Workflow UI ready。
- Evidence-backed summary citation ready。
- PDF/PPTX/DOCX/video/audio 原生正文摄入 ready。
- Assessment / Governance / Cloud collaboration ready。
