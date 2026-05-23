# ResearchNotebook V1.1 Manual Acceptance Report

文档状态：已生成手动验收报告；workspace query 文本源证据导航可进入人工验收；S1-FIX 和 S1-FE 后 session precise navigation 也可在受限文本源 session path 上进入人工验收。
日期：2026-05-23。

## 1. 验收结论

| 验收目标 | 当前结论 | 是否可手动验收 | 说明 |
| --- | --- | --- | --- |
| Workspace query 文本源 EvidenceSpan 高亮 | PASS_READY_FOR_MANUAL_ACCEPTANCE | 是 | 已通过真实 HTTP smoke、浏览器 smoke、RC2 live experience smoke。 |
| Registry `source_id` source trace | LIMITED_PASS_READY_FOR_MANUAL_ACCEPTANCE | 是，受限范围 | RC4 direct trace 返回 HTTP 200，仅限 RC4 smoke 覆盖的 registry source_id-backed 文本源。 |
| Session precise navigation | BROWSER_SMOKE_READY | 是，受限范围 | S1-FIX 后 session query 返回 `source_id + unit_id + evidence_id`；S1-FE 已验证 UI/browser citation click、Drawer unit selection 和 EvidenceSpan highlight。 |
| All-source-type precise backjump | NOT_READY | 否 | 当前只覆盖文本源 workspace query citation。 |
| Multi-format ingestion | NOT_READY | 否 | 不在 V1.1 范围。 |
| Assessment / Mastery | NOT_READY | 否 | 不在 V1.1 范围。 |
| Quality / Governance console | NOT_READY | 否 | 不在 V1.1 范围。 |
| Graph editing / governance | NOT_READY | 否 | V1.0/M4 只支持 read-only graph context。 |
| Cloud sync / collaboration | NOT_READY | 否 | 不在 V1.1 范围。 |

## 2. 可手动验收范围

当前可以手动验收的路径是：

```text
Workspace -> Source Library -> Preview -> Source Preview Drawer
Workspace query -> answer citation -> Source Preview Drawer -> DocumentUnit -> EvidenceSpan highlight
Session query -> answer citation -> Source Preview Drawer -> DocumentUnit -> EvidenceSpan highlight
Source Detail / Source Library -> Source Trace for RC4-covered registry source_id-backed text source
```

允许声明：

```text
ResearchNotebook V1.1-D EvidenceSpan Highlight is browser-smoke-ready for data_service-supported text-source workspace query citations carrying source_id + unit_id + evidence_id.

ResearchNotebook V1.1 precise evidence navigation is browser-smoke-ready for the same supported workspace query citation path.

ResearchNotebook source trace integration is ready for registry source_id-backed sources covered by RC4 smoke.

ResearchNotebook session precise evidence navigation is browser-smoke-ready for data_service-supported text-source session query citations carrying source_id + unit_id + evidence_id.
```

## 3. 手动验收前置条件

| 条件 | 期望 |
| --- | --- |
| 前端服务 | `http://127.0.0.1:5173/` 可访问 |
| 后端服务 | `http://127.0.0.1:8003` 可访问 |
| `npm run check` | PASS |
| `npm run smoke:v1.1-d-http` | PASS |
| `npm run smoke:v1.1-d-browser` | PASS |
| `npm run smoke:v1.1-rc4-trace` | PASS |
| V1.1 gap markdown / drawio | 已同步当前状态 |
| fixtures | 已脱敏，无本地路径/cache path/artifact physical path |
| `.smoke-artifacts/` | 不进入 git |

## 4. 手动验收步骤

### 4.1 启动检查

| 步骤 | 验收点 | 结果 |
| --- | --- | --- |
| 打开前端 URL | 页面不是空白，没有 crash overlay | 待人工填写 |
| 检查后端连接 | 不显示 backend unavailable | 待人工填写 |
| 检查控制台 | 无阻塞 console error / pageerror | 待人工填写 |

### 4.2 Workspace 和 Source

建议 workspace 名称：

```text
rn-v11-manual-<timestamp>
```

建议 source title：

```text
V1.1 Manual Acceptance Evidence Source
```

建议 source content：

```text
Manual acceptance should keep the answer, source preview, document unit, and highlighted evidence span visible during evidence navigation.
```

| 步骤 | 验收点 | 结果 |
| --- | --- | --- |
| 创建 workspace | workspace 出现在列表中 | 待人工填写 |
| 进入 workspace | Source Library / Ask 区域可见 | 待人工填写 |
| 创建 text source | source 出现在 Source Library | 待人工填写 |
| 打开 Source Detail | Preview / Trace 入口可见 | 待人工填写 |

### 4.3 Source Preview

| 步骤 | 验收点 | 结果 |
| --- | --- | --- |
| 点击 Preview | Source Preview Drawer 打开 | 待人工填写 |
| 查看 source metadata | title / source_id / source_type 可见 | 待人工填写 |
| 查看 text preview | 文本按 escaped text 渲染 | 待人工填写 |
| 查看 artifact refs | 只作为 metadata 展示，不解析为本地路径 | 待人工填写 |
| 检查隐私边界 | 不显示 raw filesystem path / cache path / artifact physical path | 待人工填写 |

### 4.4 DocumentUnit Navigation

| 步骤 | 验收点 | 结果 |
| --- | --- | --- |
| 查看 Document Units | unit list 可见 | 待人工填写 |
| 点击第一个 unit | selected unit 有 active state | 待人工填写 |
| 查看 unit detail | unit text preview 可见 | 待人工填写 |
| 切换 unit | source-level preview 不被清空 | 待人工填写 |

### 4.5 Workspace Query EvidenceSpan Highlight

建议问题：

```text
What should manual acceptance keep visible during evidence navigation?
```

| 步骤 | 验收点 | 结果 |
| --- | --- | --- |
| 提交 workspace query | answer 可见 | 待人工填写 |
| 查看 evidence citation | citation 可见且为 jumpable | 待人工填写 |
| 点击 citation | Source Preview Drawer 打开或聚焦 | 待人工填写 |
| 检查 selected unit | 正确 unit 被选中 | 待人工填写 |
| 检查 EvidenceSpan | 高亮文本可见且非空 | 待人工填写 |
| 检查局部状态 | answer / source preview / unit detail 仍可见 | 待人工填写 |
| 检查安全渲染 | 不依赖 raw HTML / `dangerouslySetInnerHTML` | 待人工填写 |

### 4.6 Session Precise Navigation

建议 session 名称：

```text
V1.1 Manual Session Acceptance
```

建议 session question：

```text
What should session precise navigation preserve?
```

| 步骤 | 验收点 | 结果 |
| --- | --- | --- |
| 创建 session | session 出现在 Workbench session list | 待人工填写 |
| ingest session text | session build 可完成或显示可 query 状态 | 待人工填写 |
| 提交 session query | session answer 可见 | 待人工填写 |
| 查看 session evidence citation | citation 可见且为 jumpable | 待人工填写 |
| 点击 session citation | Source Preview Drawer 打开或聚焦 | 待人工填写 |
| 检查 selected unit | 正确 unit 被选中 | 待人工填写 |
| 检查 EvidenceSpan | 高亮文本可见且非空 | 待人工填写 |
| 检查局部状态 | session answer / source preview / unit detail 仍可见 | 待人工填写 |

### 4.7 Source Trace

| 步骤 | 验收点 | 结果 |
| --- | --- | --- |
| 点击 source trace 入口 | Source Trace Drawer 打开 | 待人工填写 |
| 查看 trace/provenance | trace summary 或 provenance 可见 | 待人工填写 |
| 检查 source_id | 使用 registry `source_id`，不是 sourceRef / slug / artifact_ref | 待人工填写 |
| 检查隐私边界 | 不显示 raw path / cache path / physical artifact path | 待人工填写 |

### 4.8 Cleanup

| 步骤 | 验收点 | 结果 |
| --- | --- | --- |
| 归档 workspace | 测试 workspace 不再作为活跃 workspace 留存 | 待人工填写 |
| 记录失败项 | 如 cleanup 失败，记录 workspace id/name | 待人工填写 |

## 5. 当前不可手动验收项

### Session precise navigation

当前可进入受限范围人工验收，原因：

```text
V1.1-S1-FIX session precise navigation smoke completed.
Session build passed.
Session query returned HAS_EVIDENCE_SPAN_IDS.
Unit detail resolution passed.
EvidenceSpan resolution passed.
V1.1-S1-FE browser smoke completed.
Session citation click opened SourcePreviewDrawer.
Correct unit was selected.
EvidenceSpan highlight was visible.
```

距离 session precise navigation 手动验收还剩 0 个开发阶段。人工验收仍必须限定为 data_service-supported text-source session query citation path。

| 顺序 | 阶段 | 验收条件 |
| --- | --- | --- |
| 1 | 已完成：Session Precise Navigation Browser / Manual Smoke | UI 中点击 session answer citation 后能打开 Drawer、选中 unit、显示 EvidenceSpan 高亮 |

## 6. No False Green 边界

不得声明：

- all-session precise navigation ready
- all-source-type source trace ready
- all-source-type precise backjump ready
- multi-format ingestion ready
- assessment ready
- quality governance console ready
- graph editing/governance ready
- cloud sync/collaboration ready

不得把以下内容当作 ready 证据：

- workspace query 通过不等于所有 session query 通过；
- Source Preview 成功不等于 Source Trace 全量成功；
- 文本源成功不等于 all-source-type 成功；
- S1-FE 文本源 session browser smoke 不等于 all-session 或 all-source-type ready；
- `artifact_ref`、sourceRef、slug、raw path 都不能伪装成 registry `source_id`。

## 7. 相关审计文档

- `docs/design/V1.1/v1_1_current_gap_analysis.md`
- `docs/design/V1.1/v1_1_current_gap_analysis.drawio`
- `docs/design/V1.1/v1_1_release_readiness_checklist.md`
- `docs/design/V1.1/v1_1_s1_session_precise_navigation_smoke_report.md`
- `docs/design/V1.1/v1_1_s1_fe_session_browser_smoke_report.md`
- `docs/design/V1.1/v1_1_d_rc_browser_visual_smoke_report.md`
- `docs/design/V1.1/v1_1_d_frontend_evidence_navigation_smoke_report.md`
- `docs/design/V1.1/v1_1_rc4_source_trace_resmoke_report.md`
- `docs/design/V1.1/feature-route-matrix.md`
- `docs/design/V1.1/evidence-navigation-contract.md`
- `docs/design/V1.1/00_README.md`

## 8. 人工填写区

| 字段 | 值 |
| --- | --- |
| 验收人 | 待填写 |
| 验收时间 | 待填写 |
| 前端 URL | 待填写 |
| 后端 URL | 待填写 |
| workspace id/name | 待填写 |
| source id/title | 待填写 |
| unit id | 待填写 |
| evidence id | 待填写 |
| source trace result | 待填写 |
| EvidenceSpan highlight result | 待填写 |
| cleanup result | 待填写 |
| 最终结论 | PASS / FAIL / PARTIAL_PASS |
