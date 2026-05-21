# ResearchNotebook V1.1 当前差距分析

文档状态：V1.1-D-RC 浏览器可视化 smoke 已通过；精确证据导航仅限已联调的文本源 workspace query 路径。
配套图：`v1_1_current_gap_analysis.drawio`。

## 一句话结论

ResearchNotebook V1.1 已经把 V1.0 的“答案旁边显示来源证据”推进到：

```text
答案 -> citation -> Source Preview Drawer -> DocumentUnit -> EvidenceSpan 高亮
```

这条链路已经通过真实 `data_service` HTTP smoke 和真实浏览器 smoke。当前可声明范围很窄：

- 只覆盖 `data_service` 支持的文本源；
- 只覆盖 workspace query 返回的 citation；
- citation 必须携带 `source_id + unit_id + evidence_id`；
- 高亮只支持后端已冻结的 `normalized_text / half_open / document_unit_text` offset 合同。

不能把这个结果扩大解释为“所有来源类型、所有 session、所有 citation 都支持精确回跳”。

阅读提示：

- `PASS` 表示该项已通过对应 smoke 或验收；
- `LIMITED PASS` 表示已通过，但只在文档写明的受限范围内成立；
- `NOT_READY` 表示不能对外声明 ready；
- `DEGRADED_ACCEPTED` 表示真实联调存在降级项，但不阻塞当前受限路径发布。

## 当前可声明状态

| 模块 | 当前状态 | 说明 |
| --- | --- | --- |
| V1.0 M0-M4 主链路 | PASS | Workspace、Source、Build、Ask、Session、Graph、Feedback 已完成 integration-smoke-ready。 |
| V1.1-B Source Preview | PASS | Source Library / Source Detail 可以打开 Source Preview Drawer；文本源 source-level preview 已真实联调通过。 |
| V1.1-C DocumentUnit 导航 | PASS | Drawer 内可以加载 DocumentUnit 列表、选择 unit、加载 unit detail；文本源真实联调通过。 |
| V1.1-D EvidenceSpan 高亮 | PASS | workspace answer citation 可以打开 Drawer、定位 unit、加载 EvidenceSpan 并显示高亮；浏览器 smoke 已通过。 |
| V1.1-RC2 Live Experience Smoke | PASS | 使用已启动的本地前后端服务完成 live experience smoke；用户可打开浏览器体验受限文本源证据导航路径。 |
| 精确证据导航 | LIMITED PASS | 仅限文本源 workspace query citation，且 citation 必须包含 `source_id + unit_id + evidence_id`。 |
| Source Trace route | NOT_READY | V1.0 RC6 中 registry `source_id` 调 trace 仍是 404；Source Preview 成功不等于 Source Trace 成功。 |

## 仍然不能声明

| 能力 | 状态 | 原因 |
| --- | --- | --- |
| source trace integration ready | NOT_READY | trace route 合同仍未修复或重新 smoke。 |
| all-session precise navigation ready | NOT_READY | session query 的 EvidenceSpan 形状未单独真实 smoke。 |
| all-source-type precise backjump ready | NOT_READY | 目前只 smoke 了文本源。 |
| multi-format ingestion ready | NOT_READY | V1.1 未实现 JSON/PPT/video/audio parser UI 或多格式摄入声明。 |
| assessment / mastery ready | NOT_READY | 不在 V1.1 范围。 |
| quality governance console ready | NOT_READY | 不在 V1.1 范围。 |
| graph editing/governance ready | NOT_READY | V1.0/M4 只做 read-only graph context。 |
| cloud sync/collaboration ready | NOT_READY | 不在 V1.1 范围。 |

## 分阶段结果

| 阶段 | 做了什么 | 当前结论 |
| --- | --- | --- |
| V1.1-A | 合同发现、DTO shell、disabled Source Preview shell | shell ready，仅作为后端未就绪时的降级状态。 |
| V1.1-BE | data_service 增加 capability manifest 和 source preview route | 后端合同已可供前端接入。 |
| V1.1-B | 前端接入 source-level preview | 文本源 Source Preview integration-ready。 |
| V1.1-C-A | DocumentUnit 合同发现、disabled shell、metadata-only 显示 | shell ready，禁止声明 unit navigation ready。 |
| V1.1-C-BE | data_service 增加 DocumentUnit list/detail/pagination 合同 | 后端合同已可供前端接入。 |
| V1.1-C | 前端接入 DocumentUnit outline 和 unit detail | 文本源 Unit-Level Source Navigation integration-ready。 |
| V1.1-D-BE | data_service 增加 EvidenceSpan route、query evidence id、offset 合同 | 后端合同已可供前端接入。 |
| V1.1-D | 前端接入 EvidenceSpan 高亮和 citation 跳转 | 文本源 workspace query 路径 browser-smoke-ready。 |
| V1.1-D-RC | 真实浏览器可视化 smoke 和 release readiness 文档 | PASS。 |

## 当前前端实现边界

前端通过 `src/shared/api/dataServiceClient.ts` 统一访问后端，feature 层不拼 route string，也不直接 `fetch`。

当前已接入的 wrapper：

- `capabilities.get(workspaceId)` -> `GET /api/workspaces/{workspace_id}/capabilities`
- `sources.preview(workspaceId, sourceId)` -> `GET /api/workspaces/{workspace_id}/sources/{source_id}/preview`
- `sources.listUnits(workspaceId, sourceId, request?)` -> `GET /api/workspaces/{workspace_id}/sources/{source_id}/units`
- `sources.getUnit(workspaceId, sourceId, unitId)` -> `GET /api/workspaces/{workspace_id}/sources/{source_id}/units/{unit_id}`
- `sources.getEvidenceSpan(workspaceId, sourceId, unitId, evidenceId)` -> `GET /api/workspaces/{workspace_id}/sources/{source_id}/units/{unit_id}/evidence/{evidence_id}`

UI 行为：

- Source Preview Drawer 会先看 capability manifest，再决定是否调用 preview / units / evidence route。
- `artifact_ref` 只作为元数据展示，永远不解析成本地路径。
- `text/html` 和 `text/markdown` 仍按 escaped text 渲染，不使用 `dangerouslySetInnerHTML`。
- source-level preview、unit outline、unit detail、EvidenceSpan highlight 都是局部状态；某一块失败不会清空 answer 或其他已加载内容。
- 当 capability 不支持或 citation 缺少必要 id 时，UI 显示降级状态，不伪造高亮。

## V1.1-B：Source Preview 结果

已完成：

- capability manifest 接入；
- source-level preview route 接入；
- Source Library / Source Detail 的 Preview button；
- Source Preview Drawer；
- 安全文本渲染；
- unsupported / unavailable / backend unavailable / schema mismatch 状态；
- 真实 `data_service` smoke。

当前可声明：

```text
ResearchNotebook V1.1 Source Preview 已对 data_service 支持的文本源完成 integration-ready 验收。
```

## V1.1-C：DocumentUnit 导航结果

已完成：

- DocumentUnit list/detail adapter wrapper；
- Source Preview Drawer 内的 DocumentUnit outline；
- unit 选择状态；
- unit detail 加载；
- pagination / load more；
- 局部错误状态；
- 真实 `data_service` smoke。

真实 HTTP smoke 覆盖：

- workspace create/get/archive；
- 文本 source create/list/get；
- capability manifest: `document_units=true`, `unit_level_navigation=true`；
- source-level preview regression；
- unit list 至少返回一个后端生成的 `unit_id`；
- selected unit detail 可以加载；
- pagination 不重复 append；
- unknown unit 返回 404；
- artifact-like unit id 返回 422。

当前可声明：

```text
ResearchNotebook V1.1 Unit-Level Source Navigation 已对 data_service 支持的文本源完成 integration-ready 验收。
```

## V1.1-D：EvidenceSpan 高亮结果

已完成：

- EvidenceSpan route wrapper；
- workspace query evidence mapper 扩展；
- EvidenceList 中的 jumpable citation；
- citation 点击打开 / 聚焦 Source Preview Drawer；
- 自动加载 source preview、unit detail、EvidenceSpan detail；
- 支持 offset 高亮；
- highlight unavailable / schema mismatch / evidence not found 等局部状态；
- 真实 HTTP smoke；
- 真实浏览器 smoke。

高亮只在以下条件全部满足时启用：

- citation 有 `sourceId`；
- citation 有 `unitId`；
- citation 有 `evidenceId`；
- manifest 中 `evidence_spans=true`；
- manifest 中 `precise_span_highlight=true`；
- manifest 中 `citation_backjump=true`；
- EvidenceSpan 返回 `offset_basis=normalized_text`；
- EvidenceSpan 返回 `offset_range=half_open`；
- EvidenceSpan 返回 `text_basis=document_unit_text`；
- offset 在当前可渲染 unit text 范围内。

真实 HTTP smoke 结果：

- target route probe: PASS；
- workspace create/archive cleanup: PASS；
- text source create: PASS；
- capability manifest evidence flags: PASS；
- unit list/detail: PASS；
- workspace query 返回 `source_id + unit_id + evidence_id`: PASS；
- EvidenceSpan detail 返回 `normalized_text / half_open / document_unit_text`: PASS；
- unknown evidence 返回 404: PASS；
- artifact-like evidence id 返回 404，而不是首选 422：`DEGRADED_ACCEPTED`。

真实浏览器 smoke 结果：

- 浏览器打开 Vite app: PASS；
- 创建并进入 workspace: PASS；
- 创建 source: PASS；
- Source Preview Drawer 打开: PASS；
- Document Units 和 selected unit detail 可见: PASS；
- workspace query 生成 jumpable citation: PASS；
- 点击 citation 后 EvidenceSpan 高亮可见: PASS；
- 高亮位于 selected unit detail 内: PASS；
- 无阻塞 console/pageerror: PASS；
- 未观察到 `/api/v1/knowledge/*` 请求: PASS；
- smoke workspace 已 archive cleanup: PASS。

当前可声明：

```text
ResearchNotebook V1.1-D EvidenceSpan Highlight 已对 data_service 支持的文本源 workspace query citation 完成 browser-smoke-ready 验收。

ResearchNotebook V1.1 精确证据导航已在同一条受限路径完成 browser-smoke-ready 验收：citation 必须携带 source_id + unit_id + evidence_id。
```

## 当前已知降级项

| 项目 | 当前行为 | 影响 |
| --- | --- | --- |
| artifact-like evidence id 错误语义 | 当前 HTTP smoke 观察到 404，不是首选 422 | 记录为 `DEGRADED_ACCEPTED`；不影响正常 citation 高亮路径。 |
| session query precise navigation | 未单独真实 smoke | 不允许声明 all-session ready。 |
| source trace route | registry `source_id` trace 仍未重新证明成功 | 不允许声明 source trace integration ready。 |

## No False Green 规则

为了避免“看起来完成但实际没完成”的误报，当前文档必须继续保持这些边界：

- Source Preview 成功不等于 Source Trace 成功。
- 文本源成功不等于多格式成功。
- workspace query 成功不等于 session query 成功。
- EvidenceSpan 高亮成功不等于所有 source type 的 precise backjump 成功。
- `artifact_ref` 永远不是本地 path。
- route string 只允许出现在 `src/shared/api/dataServiceClient.ts`。
- feature modules 不直接 `fetch`。
- 不新增 `/api/v1/knowledge/*` 调用。

## 下一阶段建议

下一阶段应先执行：

```text
ResearchNotebook V1.1-RC1 Release Handoff / Scoped Commit
```

目标不是继续加功能，而是：

- 固化 V1.1-B/C/D 的 smoke 证据；
- 确认文档、drawio、release checklist 一致；
- 确认 fixtures 脱敏；
- 确认 `.smoke-artifacts/` 不提交；
- 复跑 `npm run check`；
- scoped commit / push。

## 未来仍需执行的开发阶段

下面这些是 V1.1 之后仍然需要执行的阶段。它们不是当前 V1.1 已完成能力，不能提前写成 ready。

| 顺序 | 阶段 | 目标 | Entry Gate / 前置条件 | 验收重点 |
| --- | --- | --- | --- | --- |
| 1 | V1.1-RC1 Release Handoff / Scoped Commit | 固化当前 V1.1-B/C/D 证据并同步仓库 | `npm run check`、HTTP smoke、browser smoke 均通过；文档/drawio/checklist 同步 | scoped commit/push；不提交 `.smoke-artifacts/`；不混入 data_service 改动 |
| 2 | Source Trace Contract Fix / Re-Smoke | 修复 V1.0 遗留的 source trace 404 | data_service trace route 明确接受 registry `source_id` | citation 或 Source Detail 能稳定打开 source trace；trace 失败仍局部降级 |
| 3 | Session Precise Navigation Smoke | 把 EvidenceSpan 精确导航扩展到 session query | session query 返回与 workspace query 兼容的 `source_id + unit_id + evidence_id` | session answer citation 可打开 Drawer、选择 unit、显示 EvidenceSpan 高亮 |
| 4 | All-Source-Type Preview Contract Discovery | 明确 PDF/PPT/JSON/video/audio 等格式的 preview / unit / locator 合同 | data_service capability manifest 声明每种 source type 的 preview 级别和 locator 模型 | 只对真实支持的格式开放 UI，不按文件扩展名硬猜 |
| 5 | Multi-format Ingestion Integration | 做多格式摄入和状态展示 | 后端摄入合同、parser 支持范围、错误语义、artifact 隐私规则已冻结 | 导入状态可见；失败可解释；不把 artifact_ref 解析为路径 |
| 6 | Assessment / Mastery | 生成题目、尝试、评分、掌握度 | 后端 assessment contract、scoring semantics、source grounding 合同完成 | 题目可追溯来源；评分可解释；不影响 notebook 主链路 |
| 7 | Quality / Governance Console | 质量治理、反馈归档、规则/纠错工作流 | 后端 governance/correction rules contract 完成 | 不再只是 lightweight feedback；需正式审计状态和权限模型 |
| 8 | Graph Editing / Governance | 从 read-only graph context 升级为可编辑/治理图谱 | 后端 graph mutation/merge/delete/rebuild 合同完成 | 图谱写操作可审计、可回滚；不破坏 V1.0 read-only 路径 |
| 9 | Cloud Sync / Collaboration | 多设备同步和协作 | identity、权限、同步冲突、审计日志合同完成 | 数据隔离、冲突处理、离线/在线状态可靠 |

优先级建议：

1. 先做 `V1.1-RC1 Release Handoff / Scoped Commit`，把当前已完成成果收口。
2. 再做 `Source Trace Contract Fix / Re-Smoke`，因为它是 V1.0 到 V1.1 一直保留的声明边界缺口。
3. 然后做 `Session Precise Navigation Smoke`，把 V1.1-D 的能力从 workspace query 扩展到 session query。
4. 多格式、Assessment、Governance、Graph editing 和 Cloud sync 都应进入 V1.2+ 或更后阶段，不应塞回 V1.1。

如果继续产品开发，应另开 V1.2，并且不得把 V1.2 能力回填成 V1.1 ready。
