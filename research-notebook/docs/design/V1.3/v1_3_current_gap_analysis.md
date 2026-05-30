# ResearchNotebook V1.3 当前差距分析

文档状态：V1.3 完整开发计划已落盘，并加入规格漂移 / 虚假验收强制门禁。V1.3-RC 真实浏览器验收已通过；V1.3 受限核心路径完成。

更新：V1.3 剩余手工验收、summary 质量验收、异常边界验收和最终文档同步已按产品决策后移到 V1.4-RC，与 PRD Phase 1 MVP 验收合并执行。

## 一句话结论

ResearchNotebook 已有知识来源、预览、DocumentUnit 和 EvidenceSpan 证据回跳基础，但还缺少 Agent Workflow 产品层：

```text
Agent 入口 -> workflow draft -> 用户授权 -> 本地文件夹扫描 -> 子文件夹总结 -> summary citation 回跳
```

当前可以声明受限 Agent Folder Summary Workflow ready；不能声明任意 Agent、全格式摄入或全类型证据回跳 ready。

## 当前基线

| 能力 | 状态 | 说明 |
| --- | --- | --- |
| Source Preview | PASS | 继承 V1.1/V1.2。 |
| DocumentUnit Navigation | PASS | 继承 V1.1/V1.2。 |
| EvidenceSpan Highlight | PASS_LIMITED | text/markdown/json 受限路径已通过 smoke。 |
| V1.2 Manual Acceptance | SKIPPED_BY_PRODUCT_DECISION | 传统 UI 手工验收不再作为最终入口。 |
| Agent Workflow | PASS_LIMITED | V1.3-F 已支持自然语言生成已注册 `folder_summary_v1` 草案；不代表自由 Agent ready。 |
| Local Folder Connector | PASS_LIMITED | V1.3-B 后端 route、focused tests、adapter tests、真实 HTTP smoke 已完成；范围仅限 md/txt dry-run manifest。 |
| Folder Summary Artifact | PASS_LIMITED | V1.3-G 已支持 confirmed md/txt run 的 `source_unit_span` evidence_refs 和回跳。 |
| Agent Entry Browser Acceptance | PASS_LIMITED | V1.3-RC Chrome/Browser path 已通过 `Desktop/技术分享`。 |

## 阶段拆分

| 阶段 | 状态 | 目标 |
| --- | --- | --- |
| V1.3-0 Governance Gate Update | PASS | 规格漂移 / 虚假验收门禁已写入 full plan、gap、feature matrix、drawio。 |
| V1.3-A Agent Workflow Contract Discovery | DISABLED_READY | DTO、adapter shell、disabled UI 已完成；不会读取目录或执行 workflow。 |
| V1.3-B Local Folder Connector Backend | PASS_LIMITED | permission / dry-run / folder tree / symlink 合同已实现；`Desktop/技术分享` real HTTP smoke 通过。 |
| V1.3-C Deterministic Folder Summary Workflow Runtime | PASS_LIMITED | dry-run runtime、step timeline、run report 已通过；不生成 SummaryArtifact。 |
| V1.3-D Folder Summary Generator | PASS_LIMITED | confirm_extract 后生成 SummaryArtifact；evidence_refs 仅 relative_path_only。 |
| V1.3-E Workflow UI | PASS_LIMITED | 工作区内可运行 folder_summary_v1，展示 step timeline / artifacts。 |
| V1.3-F Agent Planner | PASS_LIMITED | 用户自然语言生成已注册 workflow template draft；用户确认前不运行、不读取目录。 |
| V1.3-G Evidence-backed Summary | PASS_LIMITED | SummaryArtifact citation 可回跳 SourcePreview / DocumentUnit / EvidenceSpan；仅限 confirmed md/txt folder_summary_v1。 |
| V1.3-RC Agent Entry Acceptance | PASS_LIMITED | Chrome CLI / browser 走完整 Agent 入口验收通过。 |

## 验收主线

V1.3 的最终验收不再沿用 V1.2 的传统页面手工验收，而是以 Agent 入口为准：

```text
打开 Agent 入口
-> 输入“递归总结 Desktop/技术分享，每个子文件夹生成一份总结”
-> 查看 workflow draft
-> 用户授权目录
-> 运行 folder_summary_v1
-> 查看 step logs / skipped files / artifacts
-> 打开每个子文件夹 summary
-> 点击 summary citation 回跳证据
```

完整阶段计划和逐项验收标准见：

```text
docs/design/V1.3/v1_3_full_development_plan.md
```

## 强制治理门禁

每个开发子阶段完成后，必须先完成以下评估，才允许进入下一阶段：

| 评估项 | 等级 | 停止规则 |
| --- | --- | --- |
| 规格漂移评估 | LOW / MEDIUM / HIGH / BLOCKING | HIGH 或 BLOCKING 时停止，由用户主导下一步。 |
| 虚假验收评估 | LOW / MEDIUM / HIGH / BLOCKING | HIGH 或 BLOCKING 时停止，由用户主导下一步。 |

MEDIUM 风险允许继续前，必须把收敛措施写入下一阶段计划。

阶段报告必须记录：

- 完成内容。
- 未完成内容。
- 测试结果。
- 规格漂移评估和证据。
- 虚假验收评估和证据。
- 是否允许进入下一阶段。
- 下一阶段计划修正。

## 仍不能声明

- Agent ready。
- Workflow ready。
- Local folder connector ready。
- Folder summary ready。
- PDF/PPTX/DOCX/video/audio 原生正文摄入 ready。
- Assessment / Governance / Cloud collaboration ready。

## V1.3-A 阶段评估

| 评估项 | 结果 | 说明 |
| --- | --- | --- |
| 规格漂移评估 | LOW | 未读取本地目录，未执行 workflow，未实现 Agent Planner。 |
| 虚假验收评估 | MEDIUM | Agent Workflow 入口已出现，可能被误读为 Agent ready。 |
| 收敛措施 | PASS | UI 明确显示 disabled / contract required / no local folder access before authorization。 |
| 是否允许进入 V1.3-B | YES | `npm run check` 已通过。 |

## V1.3-B 阶段评估

| 评估项 | 结果 | 说明 |
| --- | --- | --- |
| Backend focused tests | PASS | `tests/test_target_http_folder_collections.py` 通过。 |
| Backend regression tests | PASS | Source Preview / DocumentUnit / EvidenceSpan focused tests 通过。 |
| Frontend adapter tests | PASS | `dataServiceClient.test.ts` 通过。 |
| Real HTTP smoke | PASS_LIMITED | `RN_DATA_SERVICE_BASE_URL=http://127.0.0.1:8013 npm run smoke:v1.3-b-folder-connector` 通过。 |
| 规格漂移评估 | LOW | 未执行 workflow，未读取文件正文，未实现 Agent Planner，未扩大 md/txt MVP。 |
| 虚假验收评估 | LOW | smoke 明确是 dry-run manifest，不包含 workflow、正文抽取或 summary。 |
| 收敛措施 | PASS | V1.3-C 计划必须只消费 V1.3-B manifest，不得实现自由 Agent Planner 或 evidence-backed summary。 |
| 是否允许进入 V1.3-C | YES | 未触发 HIGH/BLOCKING 停止规则。 |

V1.3-B 可声明的范围仅限：

```text
Local Folder Connector dry-run manifest is PASS_LIMITED for md/txt under Desktop/技术分享.
```

不能扩大为 Workflow ready 或 Folder Summary ready。

## V1.3-C 阶段评估

| 评估项 | 结果 | 说明 |
| --- | --- | --- |
| Backend focused tests | PASS | `test_target_http_folder_summary_workflow.py` 通过。 |
| Backend regression tests | PASS | Folder Connector / Source Preview / DocumentUnit / EvidenceSpan focused tests 通过。 |
| Frontend adapter tests | PASS | `dataServiceClient.test.ts` 通过。 |
| Real HTTP smoke | PASS_LIMITED | `RN_DATA_SERVICE_BASE_URL=http://127.0.0.1:8013 npm run smoke:v1.3-c-workflow-runtime` 通过。 |
| 规格漂移评估 | LOW | 未抽取正文、未生成 summary artifact、未实现 Agent Planner。 |
| 虚假验收评估 | LOW | `summarize_folder` 和 `write_artifacts` 明确为 skipped，`generated_artifact_count=0`。 |
| 是否允许进入 V1.3-D | YES | 未触发 HIGH/BLOCKING 停止规则。 |

V1.3-C 可声明的范围仅限：

```text
Deterministic folder_summary_v1 dry-run runtime is PASS_LIMITED for Desktop/技术分享 md/txt manifest.
```

不能扩大为 Folder Summary ready 或 Agent ready。

## V1.3-D 阶段评估

| 评估项 | 结果 | 说明 |
| --- | --- | --- |
| Backend focused tests | PASS | Summary generator tests 通过。 |
| Backend regression tests | PASS | Folder Connector / Source Preview / DocumentUnit / EvidenceSpan focused tests 通过。 |
| Frontend adapter tests | PASS | `dataServiceClient.test.ts` 通过。 |
| Real HTTP smoke | PASS_LIMITED | `RN_DATA_SERVICE_BASE_URL=http://127.0.0.1:8013 npm run smoke:v1.3-d-summary-generator` 通过。 |
| 规格漂移评估 | LOW | 只支持 md/txt，需要 confirm_extract=true，不实现 Agent Planner / Workflow UI / citation click。 |
| 虚假验收评估 | MEDIUM | SummaryArtifact 已生成，但 evidence_refs 仍是 relative_path_only。 |
| 收敛措施 | PASS | V1.3-G 前不得声明 evidence-backed summary citation ready。 |
| 是否允许进入 V1.3-E | YES | 未触发 HIGH/BLOCKING 停止规则。 |

V1.3-D 可声明的范围仅限：

```text
Folder SummaryArtifact generation is PASS_LIMITED for confirmed md/txt runs under Desktop/技术分享.
```

不能扩大为 evidence-backed summary citation ready。

## V1.3-E 阶段评估

| 评估项 | 结果 | 说明 |
| --- | --- | --- |
| Workflow UI tests | PASS | WorkspacePage 工作流 UI smoke 通过。 |
| Adapter tests | PASS | `dataServiceClient.test.ts` 通过。 |
| npm run check | PASS | boundary、lint、tests、build 均通过。 |
| 规格漂移评估 | LOW | 未实现 Agent Planner、citation click 或多格式支持。 |
| 虚假验收评估 | MEDIUM | UI 可运行 workflow，但仍不是自然语言 Agent ready。 |
| 收敛措施 | PASS | UI 和文档明确 Agent Planner 未启用。 |
| 是否允许进入 V1.3-F | YES | 未触发 HIGH/BLOCKING 停止规则。 |

V1.3-E 可声明的范围仅限：

```text
Workflow UI is PASS_LIMITED for manual folder_summary_v1 runs.
```

不能扩大为 Agent ready。

## V1.3-F 阶段评估

| 评估项 | 结果 | 说明 |
| --- | --- | --- |
| Backend focused tests | PASS | `test_target_http_agent_workflows.py` 通过。 |
| Frontend adapter/UI tests | PASS | `dataServiceClient.test.ts`、`WorkspacePage.test.tsx` 通过。 |
| Real HTTP smoke | PASS_LIMITED | `RN_DATA_SERVICE_BASE_URL=http://127.0.0.1:8013 npm run smoke:v1.3-f-agent-planner` 通过。 |
| unsupported goal | PASS | 非注册目标返回 HTTP 422。 |
| 规格漂移评估 | LOW | 只生成 `folder_summary_v1` 草案，不自动运行、不读取目录、不开放任意工具调用。 |
| 虚假验收评估 | MEDIUM | “Agent Planner” 入口可能被误读为完整 Agent ready。 |
| 收敛措施 | PASS | UI 和文档明确草案等待用户确认；`getDraft/startRun` 仍未作为完整 Agent route 启用。 |
| 是否允许进入 V1.3-G | YES | 未触发 HIGH/BLOCKING 停止规则。 |

V1.3-F 可声明的范围仅限：

```text
Agent Planner is PASS_LIMITED for generating a registered folder_summary_v1 draft from the supported Desktop/技术分享 goal.
```

不能扩大为 arbitrary Agent tool execution ready。

## V1.3-G 阶段评估

| 评估项 | 结果 | 说明 |
| --- | --- | --- |
| Backend focused tests | PASS | Folder summary / folder collection / Agent draft / V1.1 preview-unit-evidence focused tests 通过。 |
| Frontend UI tests | PASS | WorkspacePage 已覆盖 SummaryArtifact source_unit_span citation 回跳。 |
| Real HTTP smoke | PASS_LIMITED | `RN_DATA_SERVICE_BASE_URL=http://127.0.0.1:8013 npm run smoke:v1.3-g-evidence-backed-summary` 通过。 |
| Unit detail resolution | PASS | Summary evidence 的 `source_id + unit_id` 可解析。 |
| EvidenceSpan resolution | PASS | Summary evidence 的 `source_id + unit_id + evidence_id` 可解析。 |
| 规格漂移评估 | LOW | 仍只支持 md/txt，不开放任意工具调用，不解析 artifact_ref 或绝对路径。 |
| 虚假验收评估 | MEDIUM | citation 已能回跳，可能被误读为全量多格式 summary citation ready。 |
| 收敛措施 | PASS | 文档限定为 confirmed md/txt folder_summary_v1；relative_path_only 证据仍不可跳转。 |
| 是否允许进入 V1.3-RC | YES | 未触发 HIGH/BLOCKING 停止规则。 |

V1.3-G 可声明的范围仅限：

```text
Evidence-backed Summary is PASS_LIMITED for confirmed md/txt folder_summary_v1 runs.
```

不能扩大为 all-source-type summary citation ready。

## V1.3-RC 阶段评估

| 评估项 | 结果 | 说明 |
| --- | --- | --- |
| Browser smoke | PASS_LIMITED | `RN_DATA_SERVICE_BASE_URL=http://127.0.0.1:8013 RN_BROWSER_APP_URL=http://127.0.0.1:5173 npm run smoke:v1.3-rc-agent-entry` 通过。 |
| Agent entry | PASS | 浏览器打开工作区后可见“文件夹总结工作流 / 智能研究助手”入口。 |
| Workflow draft | PASS | 自然语言目标生成 `folder_summary_v1` 草案。 |
| Confirmed run | PASS | 用户确认后生成 summary artifacts。 |
| Summary citation | PASS | SummaryArtifact evidence citation 可点击。 |
| EvidenceSpan highlight | PASS | SourcePreviewDrawer 内 EvidenceSpan 高亮可见。 |
| 规格漂移评估 | LOW | 仅声明 authorized md/txt local folder summary workflow。 |
| 虚假验收评估 | MEDIUM | 真实目录已验收，但不能扩大为任意 Agent 或全格式 ready。 |
| 收敛措施 | PASS | 最终声明保留所有 NOT_READY 边界。 |

V1.3-RC 可声明的范围：

```text
ResearchNotebook V1.3 Agent Folder Summary Workflow is browser-acceptance-ready for authorized md/txt local folders validated on Desktop/技术分享.
```

## V1.3 仍未覆盖的后续方向

这些内容不属于 V1.3 受限完成范围：

- 任意 Agent 工具调用。
- PDF/PPTX/DOCX/video/audio/image 原生正文摄入。
- all-folder / all-source-type summary citation。
- Assessment / mastery。
- Quality / Governance console。
- Graph editing / governance。
- Cloud sync / collaboration。

## PRD 对齐改造记录

| 阶段 | 状态 | 说明 |
| --- | --- | --- |
| PRD-A PRD 对齐基线 | PASS | 已新增 PRD alignment plan，并保留 PRD 原文不可读风险。 |
| PRD-B 中文化和开发态文案清理 | PASS_LIMITED | Agent 主流程已清理版本号、阶段状态和工程态 ready 文案。 |
| PRD-C 视觉与信息架构对齐 | PASS_LIMITED | Agent 入口改为低噪音任务导向布局；像素级 Stitch parity 仍待单独审计。 |
| PRD-D Agent 工作流体验强化 | PASS_LIMITED | 目标输入、草案、预览扫描、确认生成总结形成用户路径。 |
| PRD-E 来源和证据阅读体验强化 | PASS_LIMITED | Summary citation 与来源预览抽屉文案更清晰，仍不扩大精确回跳范围。 |

PRD 对齐文档：

```text
docs/design/V1.3/v1_3_prd_alignment_plan.md
docs/design/V1.3/v1_3_prd_alignment_acceptance_report.md
```

## No False Green

- Chrome CLI 手工导入脚本不等于 Local Folder Connector。
- workflow draft 不等于 workflow run。
- Agent draft 不得未确认就读取本地目录。
- summary 普通文本不等于 evidence-backed summary。
- relative_path 是唯一可展示路径；不得展示 `/Users` 绝对路径。
- V1.3 MVP 只支持 md/txt；PDF/PPTX/DOCX/video/audio/image 仍不是 ready 能力。
- 任一阶段的风险评估为 HIGH 或 BLOCKING 时，不得继续自动推进。
