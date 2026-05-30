# ResearchNotebook V1.3 完整开发计划

文档状态：V1.3-0 PASS，V1.3-A DISABLED_READY，V1.3-B/C/D/E/F/G/RC PASS_LIMITED。已加入规格漂移和虚假验收强制门禁。
日期：2026-05-25。

## 1. 总目标

V1.3 的目标是把 ResearchNotebook 从“知识来源预览和证据导航工具”推进到“可由 Agent 入口驱动的本地文件夹总结工作流”。

核心验收用例：

```text
用户输入：递归总结 Desktop/技术分享，每个子文件夹生成一份总结。
系统行为：Agent 生成工作流草案，用户授权目录，后端递归扫描 md/txt 文件，按子文件夹生成结构化总结，并保留 evidence refs。
```

V1.3 完成后，用户应能：

- 通过 Agent 入口提出文件夹总结任务。
- 查看并确认 workflow draft。
- 授权读取本地目录。
- 运行确定性 folder summary workflow。
- 查看步骤日志、跳过文件、失败原因和产物。
- 打开每个子文件夹 summary 和根目录总览。
- 从 summary citation 回跳到 Source Preview / DocumentUnit / EvidenceSpan。

## 2. 当前基线

| 能力 | 当前状态 | 说明 |
| --- | --- | --- |
| Source Preview | PASS | V1.1/V1.2 已完成。 |
| DocumentUnit Navigation | PASS | V1.1/V1.2 已完成。 |
| EvidenceSpan Highlight | PASS_LIMITED | 受限文本路径已完成。 |
| Source Trace | LIMITED_PASS | registry source_id-backed sources 的受限路径已完成。 |
| V1.2 Manual Acceptance | SKIPPED_BY_PRODUCT_DECISION | 手工验收迁移到 V1.3 Agent 入口。 |
| Agent Workflow | PASS_LIMITED | V1.3-F 可生成 registered `folder_summary_v1` draft；不代表自由 Agent ready。 |
| Local Folder Connector | PASS_LIMITED | V1.3-B 已支持 md/txt dry-run manifest。 |
| Folder Summary Artifact | PASS_LIMITED | V1.3-D 可在 confirm_extract 后生成 SummaryArtifact；citation 仍未回跳。 |

## 3. 总体约束

- V1.3 MVP 只支持 md/txt。
- PDF、PPTX、DOCX、video、audio、image 不声明 ready。
- 本地目录读取必须有显式用户授权。
- Agent Planner 第一版只能生成已注册 workflow template。
- 用户确认前不得执行本地文件操作。
- 只展示 relative_path，不展示 `/Users`、`file://`、cache path、artifact physical path。
- 不把 artifact_ref 当 filesystem path。
- 不新增 `/api/v1/knowledge/*` 功能调用。
- 前端 feature modules 不 direct fetch。
- 真实 route shape 只能在 `src/shared/api/dataServiceClient.ts`。
- Summary 必须是结构化 artifact，不是普通 answer。
- Summary citation 必须引用真实 evidence refs，不得伪造。

## 4. 强制治理门禁

V1.3 每个开发子阶段都必须按以下闭环推进：

```text
阶段实现
-> 阶段验收
-> 规格漂移评估
-> 虚假验收评估
-> 下一阶段计划审计和修正
-> 判断是否允许进入下一阶段
```

每个阶段验收报告必须包含：

- 规格漂移评估：LOW / MEDIUM / HIGH / BLOCKING。
- 规格漂移证据。
- 虚假验收评估：LOW / MEDIUM / HIGH / BLOCKING。
- 虚假验收证据。
- 是否允许进入下一阶段：YES / NO。
- 下一阶段计划修正。

强制停止规则：

- 任一风险为 HIGH 或 BLOCKING，停止继续实现下一阶段，由用户主导下一步开发。
- 任一风险为 MEDIUM，必须先把收敛措施写入下一阶段计划，才能继续。
- 两项风险均为 LOW，才允许自动进入下一阶段执行准备。

规格漂移重点检查：

- 是否越过当前阶段边界，提前实现后续阶段能力。
- 是否把 md/txt MVP 扩大成 PDF/PPTX/DOCX/video/audio ready。
- 是否让 Agent 自由调用未注册工具。
- 是否绕过用户授权读取本地目录。
- 是否在前端实现 parser 或 direct fetch。
- 是否把普通 summary 当成 SummaryArtifact。
- 是否把普通 citation 当成 evidence-backed citation。

虚假验收重点检查：

- workflow draft 成功是否被误写为 workflow run 成功。
- ChromeCLI 手工导入是否被误写为 Local Folder Connector ready。
- mock / dry run 成功是否被误写为真实 data_service ready。
- 普通 summary 是否被误写为 evidence-backed summary。
- Source Preview 成功是否被误写为 EvidenceSpan precise navigation。
- 单一路径 smoke 是否被误写为 all-source-type ready。

统一阶段报告模板：

```text
阶段：
目标：
执行范围：
完成内容：
未完成内容：
测试结果：
fixtures / artifacts：
文档更新：
规格漂移评估：LOW / MEDIUM / HIGH / BLOCKING
规格漂移证据：
虚假验收评估：LOW / MEDIUM / HIGH / BLOCKING
虚假验收证据：
是否允许进入下一阶段：YES / NO
下一阶段计划修正：
仍不能声明：
```

## 5. 子阶段计划和验收标准

### V1.3-0 Governance Gate Update

目标：

将规格漂移和虚假验收评估写入 V1.3 文档体系，作为所有后续阶段的强制门禁。

交付内容：

- 更新 V1.3 完整开发计划。
- 更新 gap markdown。
- 更新 drawio。
- 更新 feature route matrix。
- 明确阶段报告模板。

验收标准：

1. 总计划明确 HIGH / BLOCKING 必须停止。
2. gap 文档明确每阶段后必须做风险评估。
3. feature matrix 记录 governance gate。
4. drawio 显示治理门禁。
5. 不修改业务代码。
6. drawio XML 可解析。

规格漂移评估重点：

- 是否把治理文档阶段误写成开发完成。
- 是否提前声明 Agent / Workflow ready。

虚假验收评估重点：

- 是否把“门禁规则已写入”误写成“V1.3 能力已通过”。

当前结果：

- 状态：PASS。
- 规格漂移评估：LOW。
- 虚假验收评估：LOW。
- 允许进入 V1.3-A：YES。

### V1.3-A Agent Workflow Contract Discovery

目标：

定义 Agent Workflow 的最小合同，不实现真实运行。

交付内容：

- AgentTask DTO。
- Workflow DTO。
- WorkflowRun DTO。
- WorkflowStep DTO。
- Tool DTO。
- FolderCollection DTO。
- SummaryArtifact DTO。
- EvidenceRef DTO。
- adapter shell。
- disabled Agent Workflow UI。

允许：

- 更新合同文档。
- 增加 DTO 和 mapper shell。
- 增加 disabled UI 状态。
- 增加测试覆盖 disabled / capability missing。

禁止：

- 不读取真实文件夹。
- 不执行 workflow。
- 不声明 Agent ready。
- 不声明 Workflow ready。

验收标准：

1. `v1_3_agent_workflow_contract.md` 明确 DTO 和状态机。
2. Agent 入口显示 contract required / disabled 状态。
3. workflow draft 和 workflow run 状态区分清楚。
4. 用户确认前不会触发本地文件访问。
5. adapter shell 返回稳定 `capability_missing` 或 `not_implemented`。
6. `npm run check` 通过。
7. gap 文档显示 V1.3-A complete，V1.3-B next。

规格漂移评估重点：

- 是否提前实现 workflow run。
- 是否提前读取本地目录。
- 是否提前做 Agent Planner。
- 是否将 disabled shell 写成 Agent ready。

虚假验收评估重点：

- 是否把 DTO / shell 通过误写成 workflow ready。
- 是否把 Agent 入口出现误写成 Agent 可用。

当前结果：

- 状态：DISABLED_READY。
- `npm run check`：PASS。
- 规格漂移评估：LOW。
- 虚假验收评估：MEDIUM。
- 收敛措施：UI 明确显示 disabled / contract required / no local folder access before authorization。
- 允许进入 V1.3-B：YES。

### V1.3-B Local Folder Connector Backend

目标：

后端提供受控本地文件夹扫描合同，第一版只支持 md/txt dry-run manifest。

当前进入条件：

- 状态：PASS_LIMITED。
- permission / dry-run / folder tree / symlink 合同已实现。
- 后端 focused tests 和 ResearchNotebook adapter tests 已通过。
- 可声明范围仅限 md/txt dry-run manifest；不得声明 Workflow ready 或 Folder Summary ready。

建议 route：

```text
POST /api/workspaces/{workspace_id}/folder-collections/scan
```

核心能力：

- 接收用户授权目录。
- 递归扫描文件夹。
- 记录 md/txt manifest。
- 返回 folder/file manifest。
- 返回 skipped files 和 skipped_reason。
- 只返回 relative_path。

默认排除：

- 隐藏文件和隐藏目录。
- `.env`。
- secret/key/token/cert 类文件。
- `.git`。
- `node_modules`。
- `dist`。
- `build`。
- cache 目录。
- 大型二进制。
- pdf/pptx/docx/video/audio/image。

验收标准：

1. 扫描 `Desktop/技术分享` 成功。
2. response 不包含 `/Users`、`file://`、cache path、artifact physical path。
3. md/txt 文件进入 `files`。
4. 不支持文件进入 `skipped_files`。
5. 每个 skipped file 都有 `skipped_reason`。
6. `.env`、secret/key/token/cert 不被读取。
7. source preview / DocumentUnit / EvidenceSpan 后端回归不失败。
8. OpenAPI/schema 或等价机器可读合同已更新。
9. sanitized fixtures 保存到 `fixtures/real/v1_3/folder-collections/`。
10. ResearchNotebook 文档同步更新。

当前结果：

- Backend focused tests：PASS。
- Backend regression tests：PASS。
- Frontend adapter tests：PASS。
- Real HTTP smoke：PASS_LIMITED。
- 规格漂移评估：LOW。
- 虚假验收评估：LOW。
- 收敛措施：V1.3-C 只消费 V1.3-B manifest，不实现自由 Agent Planner 或 evidence-backed summary。
- 允许进入 V1.3-C：YES。

下一步：

```text
V1.3-C Deterministic Folder Summary Workflow Runtime
```

规格漂移评估重点：

- 是否支持了 md/txt 以外格式并声明 ready。
- 是否绕过用户授权。
- 是否暴露绝对路径。
- 是否把 ChromeCLI 手工导入当成后端 connector。

虚假验收评估重点：

- 是否只用 mock 数据却声明真实 connector ready。
- 是否扫描成功但没有验证 skipped 文件。
- 是否只验证单文件而声明递归扫描 ready。

### V1.3-C Deterministic Folder Summary Workflow Runtime

目标：

先做确定性 workflow template，不做自由 Agent Planner。

固定模板：

```text
folder_summary_v1
```

步骤：

1. `scan_folder`
2. `extract_text`
3. `group_by_subfolder`
4. `create_sources`
5. `summarize_folder`
6. `generate_index_report`
7. `write_artifacts`

验收标准：

1. 可以创建 WorkflowRun。
2. 每个 WorkflowStep 有 status、input_ref、output_ref、logs。
3. 支持 pending、running、completed、failed、skipped。
4. 支持 dry run。
5. 支持失败 step retry。
6. workflow 失败不会清空已生成 artifacts。
7. `Desktop/技术分享` 可跑完整模板。
8. run report 记录 scanned files、skipped files、generated artifacts。
9. `npm run check` 通过。

当前结果：

- 状态：PASS_LIMITED。
- Backend focused tests：PASS。
- Backend regression tests：PASS。
- Frontend adapter tests：PASS。
- Real HTTP smoke：PASS_LIMITED。
- `npm run check`：PASS。
- 规格漂移评估：LOW。
- 虚假验收评估：LOW。
- 允许进入 V1.3-D：YES。

规格漂移评估重点：

- 是否提前加入自由 Agent 工具调用。
- 是否跳过 Local Folder Connector 直接读文件。
- 是否把 runtime 成功写成 Agent ready。

虚假验收评估重点：

- 是否只创建 WorkflowRun 但没有实际跑步骤。
- 是否 step logs 为空仍声明 runtime ready。
- 是否 dry run 被误写成真实 run。

### V1.3-D Folder Summary Generator

目标：

为每个子文件夹生成结构化 summary artifact，并生成根目录总览。

Summary schema：

- overview
- key_topics
- key_files
- technical_points
- reusable_materials
- risks_or_gaps
- evidence_refs

验收标准：

1. 每个一级子文件夹至少生成一份 summary。
2. 根目录生成 index summary。
3. 每份 summary 是结构化 artifact。
4. 每份 summary 至少保留部分 evidence_refs。
5. evidence_refs 只引用 registry source_id、unit_id、evidence_id、relative_path。
6. 不显示本地绝对路径。
7. 空文件夹生成 empty summary 或 skipped summary。
8. unsupported 文件不阻塞同目录可支持文件总结。
9. fixtures 保存到 `fixtures/real/v1_3/folder-summary/`。

规格漂移评估重点：

- 是否把普通 answer 当 SummaryArtifact。
- 是否伪造 evidence_refs。
- 是否把 unsupported 文件当成已总结。
- 是否扩大到全格式总结。

虚假验收评估重点：

- 是否只生成一个总览却声明每个子文件夹完成。
- 是否 summary 无 evidence_refs 却声明 evidence-backed。
- 是否 artifact 没有稳定 id / schema。

当前结果：

- 状态：PASS_LIMITED。
- Backend focused tests：PASS。
- Backend regression tests：PASS。
- Frontend adapter tests：PASS。
- Real HTTP smoke：PASS_LIMITED。
- `npm run check`：PASS。
- 规格漂移评估：LOW。
- 虚假验收评估：MEDIUM。
- 收敛措施：V1.3-G 前不得声明 evidence-backed summary citation ready。
- 允许进入 V1.3-E：YES。

### V1.3-E Workflow UI

目标：

用户可以在前端查看、运行、调试 workflow。

UI 能力：

- Agent 入口。
- Workflow draft view。
- Run 按钮。
- Step timeline。
- 日志面板。
- artifact 面板。
- skipped files 面板。
- retry。
- dry run。
- summary 查看、复制、下载。

验收标准：

1. 用户能看到 workflow draft。
2. 用户必须确认授权目录后才能运行。
3. 运行中能看到 step 进度。
4. 失败 step 显示局部错误，不导致整页崩溃。
5. skipped files 可查看原因。
6. summary artifacts 可打开。
7. retry 不会重复生成已完成 artifact，除非用户明确 rerun。
8. feature modules 无 direct fetch。
9. route shape 仍只在 `dataServiceClient.ts`。
10. `npm run check` 通过。

规格漂移评估重点：

- 是否 UI 直接 fetch。
- 是否前端实现文件 parser。
- 是否 UI 绕过授权直接触发扫描。
- 是否把 workflow UI 可见写成 Agent ready。

虚假验收评估重点：

- 是否只用 mock UI 却声明真实 workflow 可运行。
- 是否 artifact 面板能打开但数据不是真实 run 产物。
- 是否未测失败 / 重试却声明 workflow debug ready。

### V1.3-F Agent Planner

当前状态：PASS_LIMITED。

阶段报告：`docs/design/V1.3/v1_3_f_agent_planner_report.md`。

目标：

用户用自然语言生成 workflow draft。

示例输入：

```text
递归总结 Desktop/技术分享，每个子文件夹生成一份总结。
```

预期输出：

- workflow draft。
- 目标目录。
- 排除规则。
- 执行步骤。
- 权限要求。
- 预计产物。

限制：

- Agent 只能选择已注册 workflow template。
- Agent 不允许自由调用任意工具。
- Agent 不允许未确认就运行本地文件操作。

验收标准：

1. Agent 能识别 folder summary 意图。
2. Agent 生成 `folder_summary_v1` draft。
3. draft 清楚显示目录授权要求。
4. 用户确认前不执行扫描。
5. Agent 不读取未授权路径。
6. Agent 不声明 pdf/ppt/video/audio ready。
7. Agent 不能生成未注册工具调用。
8. prompt injection 文本不能绕过授权。
9. `npm run check` 通过。

规格漂移评估重点：

- 是否允许任意工具调用。
- 是否 Agent 自动执行本地文件操作。
- 是否把 draft 当成 run。
- 是否绕过用户确认。

虚假验收评估重点：

- 是否只靠规则匹配就声明 Agent ready。
- 是否没有真实运行后续 workflow 却声明端到端 ready。
- 是否单一 prompt 成功被扩大成通用 Agent ready。

### V1.3-G Evidence-backed Summary

当前状态：PASS_LIMITED。

阶段报告：`docs/design/V1.3/v1_3_g_evidence_backed_summary_report.md`。

目标：

summary citation 能回跳到 SourcePreviewDrawer、DocumentUnit、EvidenceSpan。

验收标准：

1. summary 中 citation 可点击。
2. citation 携带 source_id。
3. 可用时携带 unit_id 和 evidence_id。
4. 点击 citation 打开 SourcePreviewDrawer。
5. 支持 source-level preview。
6. 支持 unit-level preview。
7. 支持 EvidenceSpan highlight。
8. citation 失败时显示 citation unavailable。
9. 不伪造 evidence。
10. artifact_ref 不被解析为 filesystem path。
11. workspace query EvidenceSpan 路径不回退。
12. `npm run check` 通过。

规格漂移评估重点：

- 是否伪造 source_id / unit_id / evidence_id。
- 是否把 source preview 成功当 span highlight 成功。
- 是否把部分 citation ready 写成 all-source-type precise backjump ready。

虚假验收评估重点：

- 是否 summary 有链接样式但不能真实回跳。
- 是否只回跳 source-level 却声明 EvidenceSpan ready。
- 是否失败状态未测却声明 citation robust。

### V1.3-RC Agent Entry ChromeCLI / Manual Acceptance

当前状态：PASS_LIMITED。

阶段报告：`docs/design/V1.3/v1_3_rc_agent_entry_acceptance_report.md`。

目标：

用真实浏览器像普通用户一样完成完整验收。

验收路径：

1. 打开 ResearchNotebook。
2. 进入 Agent 入口。
3. 输入“递归总结 Desktop/技术分享，每个子文件夹生成一份总结”。
4. Agent 生成 workflow draft。
5. 用户确认目录授权。
6. workflow 开始运行。
7. 查看 step timeline。
8. 查看 skipped files。
9. 查看每个子文件夹 summary。
10. 查看根目录总览 summary。
11. 点击 summary citation。
12. SourcePreviewDrawer 打开。
13. DocumentUnit / EvidenceSpan 可用时完成定位和高亮。
14. 导出或复制 summary。
15. cleanup 测试 workspace / artifacts。

RC 通过标准：

1. ChromeCLI browser smoke 通过。
2. manual acceptance report 落盘。
3. `Desktop/技术分享` 路径完成端到端验收。
4. artifacts 不包含本地绝对路径。
5. `.smoke-artifacts/` 不提交。
6. fixtures 已脱敏。
7. `npm run check` 通过。
8. gap markdown / drawio 显示 V1.3 browser/manual acceptance passed。
9. 仍明确 NOT_READY：
   - pdf/ppt/docx/video/audio 多格式总结。
   - Assessment。
   - Quality/Governance console。
   - Graph editing/governance。
   - Cloud sync/collaboration。
   - arbitrary agent tool execution。

规格漂移评估重点：

- 是否把单目录通过扩大成任意目录 ready。
- 是否把 md/txt ready 扩大成多格式 ready。
- 是否把 registered template Agent 扩大成 arbitrary Agent tool execution ready。

虚假验收评估重点：

- 是否没有真实浏览器路径却声明 manual ready。
- 是否没有点击 citation 却声明 evidence-backed summary ready。
- 是否没有 cleanup 却声明 RC pass。
- 是否失败项被记录为 PASS。

## 6. 测试计划

每阶段必须执行：

```bash
npm run check
```

后端阶段额外执行：

- folder connector focused backend tests。
- workflow runtime backend tests。
- schema/OpenAPI 检查。
- fixture 脱敏检查。

前端阶段额外执行：

- adapter tests。
- UI smoke tests。
- ChromeCLI browser smoke。

边界检查：

```bash
rg -n "/api/v1/knowledge" src scripts docs/design/V1.3
rg -n "fetch\\(" src/features src/shared/components
rg -n "/api/" src
rg -n "/Users|file://|cache_path|artifact_path|physical_path|/private/tmp|/tmp/" fixtures/real/v1_3
git status --short -- .smoke-artifacts
```

验收：

- `/api/v1/knowledge` 不新增功能调用。
- feature/components 无 direct fetch。
- 真实 route string 只在 `src/shared/api/dataServiceClient.ts`。
- fixtures 不含本地绝对路径或物理 artifact path。
- `.smoke-artifacts/` 不进入 git。

## 7. 需要审计的 V1.3 设计文档

- `docs/design/V1.3/00_README.md`
- `docs/design/V1.3/v1_3_full_development_plan.md`
- `docs/design/V1.3/v1_3_current_gap_analysis.md`
- `docs/design/V1.3/v1_3_current_gap_analysis.drawio`
- `docs/design/V1.3/v1_3_agent_workflow_contract.md`
- `docs/design/V1.3/v1_3_local_folder_connector_contract.md`
- `docs/design/V1.3/feature-route-matrix.md`

## 8. 完成声明口径

如果 V1.3-RC 通过，可以声明：

```text
ResearchNotebook V1.3 Agent Folder Summary Workflow is browser/manual-acceptance-ready for authorized md/txt local folders, validated on Desktop/技术分享.
```

必须同时保留限制：

- 不代表 PDF/PPTX/DOCX/video/audio ready。
- 不代表 arbitrary Agent tool execution ready。
- 不代表 Assessment ready。
- 不代表 Quality/Governance console ready。
- 不代表 Graph editing/governance ready。
- 不代表 Cloud sync/collaboration ready。
