# V1.3-B Local Folder Connector Backend Report

日期：2026-05-25

## 阶段

V1.3-B Local Folder Connector Backend。

## 目标

提供受控的本地文件夹 dry-run manifest 扫描合同，为后续 deterministic folder summary workflow 提供稳定输入。

## 执行范围

- 后端新增 `POST /api/workspaces/{workspace_id}/folder-collections/scan`。
- ResearchNotebook adapter 新增 `dataServiceClient.folderCollections.scan`。
- 新增 V1.3-B smoke 脚本。
- 当前只做目录 manifest，不做正文抽取、不执行 workflow、不生成 summary。

## 完成内容

- Folder scan request 支持：
  - `authorized_root`
  - `permission_grant_id`
  - `dry_run=true`
  - `exclude_globs`
  - `max_depth`
  - `follow_symlinks=false`
- Response 返回：
  - `FolderCollection`
  - `FolderNode[]`
  - `FolderFile[]`
  - `SkippedFile[]`
  - `PermissionGrant`
- 路径卫生：
  - response 只返回 `relative_path`。
  - response 不返回 `authorized_root`。
  - dry-run 文件不返回正文。
- 支持范围：
  - `.md`
  - `.txt`
- 明确拒绝：
  - `dry_run=false`
  - `follow_symlinks=true`
  - 非 `.md` / `.txt` 的 `include_extensions`

## 未完成内容

- 未实现真实正文 extract。
- 未实现 Folder Summary Workflow Runtime。
- 未实现 Agent Planner。
- 未实现 Workflow UI。
- 未实现 SummaryArtifact 生成。
- 未实现 evidence-backed summary citation。

## 测试结果

| 验收项 | 结果 | 说明 |
| --- | --- | --- |
| Backend focused tests | PASS | `tests/test_target_http_folder_collections.py` 通过。 |
| Backend regression tests | PASS | Source Preview / DocumentUnit / EvidenceSpan focused tests 通过。 |
| Frontend adapter tests | PASS | `dataServiceClient.test.ts` 通过。 |
| Real HTTP smoke | PASS_LIMITED | 临时 data_service `http://127.0.0.1:8013` 扫描 `Desktop/技术分享` 通过。 |

已执行命令：

```text
python3 -m pytest tests/test_target_http_folder_collections.py -q
python3 -m pytest tests/test_target_http_folder_collections.py tests/test_target_http_source_preview.py tests/test_target_http_document_units.py tests/test_target_http_evidence_spans.py -q
npm run test -- dataServiceClient.test.ts
RN_DATA_SERVICE_BASE_URL=http://127.0.0.1:8013 npm run smoke:v1.3-b-folder-connector
npm run check
```

## Fixtures / Artifacts

已保存脱敏 fixtures：

```text
fixtures/real/v1_3/folder-collections/
```

文件：

- `folder-scan-success.json`
- `folder-scan-extract-rejected.json`
- `folder-scan-unsupported-extension-rejected.json`
- `v1-3-b-folder-connector-result.json`

脱敏检查：

```text
rg -n "/Users|file://|cache_path|artifact_path|physical_path|/private/tmp|/tmp/|authorized_root" fixtures/real/v1_3/folder-collections
```

结果：无命中。

## 文档更新

- `docs/design/V1.3/v1_3_current_gap_analysis.md`
- `docs/design/V1.3/v1_3_current_gap_analysis.drawio`
- `docs/design/V1.3/feature-route-matrix.md`
- `docs/design/V1.3/v1_3_local_folder_connector_contract.md`
- `docs/design/V1.3/00_README.md`

## 规格漂移评估

等级：LOW

证据：

- 未执行 workflow。
- 未读取或返回文件正文。
- 未实现 Agent Planner。
- 未扩大 md/txt MVP 到多格式。
- `dry_run=false` 被拒绝。

## 虚假验收评估

等级：LOW

证据：

- 当前能力仍是 manifest dry-run，不是完整 Local Folder Connector ready，更不是 Workflow ready。
- Real HTTP smoke 已扫描 `Desktop/技术分享`，返回 folders/files/skipped_files，并验证 dry_run=false 与非 md/txt include 被拒绝。
- fixtures 已脱敏保存。

收敛措施：

- V1.3-C 计划必须明确只消费 V1.3-B dry-run manifest；正文 extract / source creation / summary artifacts 均要通过 workflow runtime 合同显式实现。
- 不得把 V1.3-B dry-run manifest 写成 Workflow ready 或 Folder Summary ready。

## 是否允许进入下一阶段

当前：YES。

原因：规格漂移 LOW、虚假验收 LOW，未触发 HIGH/BLOCKING 停止规则。

## 下一阶段计划修正

下一步进入 V1.3-C Deterministic Folder Summary Workflow Runtime，但必须收窄为：

1. 只实现 deterministic template `folder_summary_v1` 的运行时合同。
2. 只允许基于 V1.3-B `FolderCollection` manifest。
3. 不实现自由 Agent Planner。
4. 不实现 evidence-backed summary citation。
5. 不声明 Agent ready。
6. 不声明 Folder Summary ready，直到 SummaryArtifact 阶段完成。

## 仍不能声明

- Local Folder Connector ready。
- Workflow ready。
- Agent ready。
- Folder Summary ready。
- PDF/PPTX/DOCX/video/audio 原生正文摄入 ready。
- Assessment / Governance / Cloud collaboration ready。
