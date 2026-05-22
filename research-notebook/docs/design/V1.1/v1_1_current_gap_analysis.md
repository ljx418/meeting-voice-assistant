# ResearchNotebook V1.1 当前差距分析

文档状态：V1.1-D-RC 浏览器可视化 smoke 已通过；RC4 source trace backend fix 和 re-smoke 已通过，source trace integration 进入受限 PASS。
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
| Source Trace route | LIMITED PASS | V1.1-RC4 backend fix 后重新验证：source create/list/get 返回的 registry `source_id` 可以 direct trace HTTP 200，并返回 trace/provenance；范围仅限 RC4 smoke 覆盖的 registry source_id-backed 文本源。 |

## 仍然不能声明

| 能力 | 状态 | 原因 |
| --- | --- | --- |
| source trace integration beyond RC4 scoped registry text path | NOT_READY | 当前只证明了 RC4 smoke 覆盖的 registry source_id-backed 文本源 direct trace；不能扩大到所有 source type 或 session precision。 |
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
| V1.1-RC4 | Source Trace Contract Fix / Re-Smoke | data_service 已修复 target trace contract；registry `source_id` direct trace 返回 HTTP 200；source trace integration 对 RC4 smoke 覆盖范围进入受限 PASS。 |

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
| source trace route | registry `source_id` trace 已在 RC4 rerun 中证明成功 | 只允许声明 RC4 smoke 覆盖范围内的 scoped source trace integration。 |

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

下一阶段应执行：

```text
V1.1-RC5 Final Evidence Navigation Release Sync
```

原因：

- V1.1-RC1 release handoff、RC2 live experience smoke、RC3 scoped commit / remote sync 已完成；
- data_service Source Trace Backend Contract Fix 已完成；
- V1.1-RC4 已重新验证 source trace contract；
- RC4 结论是 registry `source_id` direct trace 返回 HTTP 200；
- ResearchNotebook 可以声明受限 source trace integration：仅限 RC4 smoke 覆盖的 registry source_id-backed 文本源。

下一步不应新增功能，而应做最终 release sync、scoped commit、push，并记录 hash / branch / remote。

## V1.1 还剩多少开发阶段

如果严格按 V1.1 release hardening 口径计算，当前还剩 **1 个阶段**：

| 顺序 | 阶段 | 类型 | 是否新增产品能力 | 当前状态 |
| --- | --- | --- | --- | --- |
| 1 | V1.1-RC5 Final Evidence Navigation Release Sync | release sync / repository handoff | 否，只做最终文档、check、commit、push | 等待本次文档同步和 scoped repository sync |

如果把 V1.1 之后的产品扩展也算入路线图，则还有 **7 个后续产品阶段**，但它们不应回填为 V1.1 ready：

| 顺序 | 阶段 | 建议归属 | 说明 |
| --- | --- | --- | --- |
| 1 | Session Precise Navigation Smoke | V1.1.x 或 V1.2 entry | 把 workspace query 的 EvidenceSpan 精确导航扩展到 session query。 |
| 2 | All-Source-Type Preview Contract Discovery | V1.2-A | 明确 PDF/PPT/JSON/video/audio 等格式的 preview / locator 合同。 |
| 3 | Multi-format Ingestion Integration | V1.2 | 做多格式摄入和状态展示。 |
| 4 | Assessment / Mastery | V1.3+ | 做题目、评分和掌握度。 |
| 5 | Quality / Governance Console | V1.3+ | 从 lightweight feedback 升级到治理台。 |
| 6 | Graph Editing / Governance | V1.4+ | 从 read-only graph context 升级为可编辑图谱。 |
| 7 | Cloud Sync / Collaboration | V2.0+ | 做账号、权限、同步、协作和冲突处理。 |

当前推荐先完成前 3 个 V1.1 hardening 阶段，再决定是否进入 V1.2。

## 过往开发计划完成度评估

| 计划块 | 完成度 | 证据 | 评价 |
| --- | --- | --- | --- |
| V1.0 M0-M4 主链路 | 100% | Workspace / Source / Build / Ask / Session / Graph / Feedback smoke 已完成 | MVP 主链路已具备集成烟测级可用性。 |
| V1.0 RC6 source trace re-smoke | 100% | `v1_0_rc6_source_trace_resmoke_report.md` | 验证工作完成，但结果是 trace 404，因此能力未 ready。 |
| V1.0 RC7/RC8 handoff / remote sync | 100% | `v1_0_rc7_release_handoff.md`、remote sync status | 仓库同步和 No False Green 口径已完成。 |
| V1.1-A Contract Discovery / Disabled Shell | 100% | contract docs、adapter shell、disabled states | 阶段边界清楚，没有提前声明后端未提供能力。 |
| V1.1-B Source Preview | 100% | source preview smoke report | 文本源 source-level preview 已 integration-ready。 |
| V1.1-C DocumentUnit Navigation | 100% | unit navigation smoke report | 文本源 manual unit navigation 已 integration-ready。 |
| V1.1-D EvidenceSpan Highlight | 100% | HTTP smoke、browser smoke、RC2 live experience smoke | 文本源 workspace query citation 的 EvidenceSpan 高亮已 browser-smoke-ready。 |
| V1.1-RC1/RC2/RC3 release handoff | 100% | release checklist、RC2 report、git remote sync status | V1.1 已完成 release handoff 和 scoped remote sync。 |
| Source Trace Backend Contract Fix | 100% | data_service target trace contract tests；ResearchNotebook RC4 re-smoke | registry `source_id` direct trace 已从 404 修复为 HTTP 200。 |
| V1.1-RC4 source trace re-smoke | 100% 验证完成；受限能力升级完成 | RC4 report 和 source-trace fixtures | 验证证明 trace route 对 RC4 smoke 覆盖的 registry source_id-backed 文本源可用。 |
| 全 session 精确导航 | 0% | 无 session EvidenceSpan smoke | 未开始，不能声明 ready。 |
| 全 source type 精确回跳 | 0% | 仅文本源 smoke | 未开始，不能声明 ready。 |
| V1.2+ 多格式 / Assessment / Governance / Cloud | 0% | 明确不在 V1.1 范围 | 应保持未来阶段，不应污染 V1.1 声明。 |

总体完成度判断：

```text
V1.1 核心证据导航链路完成度：高
V1.1 release hardening 完成度：中高
source trace integration 完成度：受限 ready，仅覆盖 RC4 smoke 的 registry source_id-backed 文本源
V1.2+ 产品扩展完成度：未开始
```

## 项目风险评估

| 风险 | 等级 | 当前表现 | 影响 | 应对策略 |
| --- | --- | --- | --- | --- |
| source trace scope 可能被过度扩大 | 中高 | RC4 只证明 registry source_id-backed 文本源 direct trace | 若误称所有 source type/session trace ready，会形成 No False Green 风险 | 声明限定为 RC4 smoke 覆盖范围；全 source type/session 另开 smoke。 |
| 能力声明被过度扩大 | 高 | V1.1-D 只覆盖文本源 workspace query citation | 若误称 all-session / all-source-type ready，会形成 No False Green 风险 | 文档继续保留 LIMITED PASS / NOT_READY；release checklist 必须写明范围。 |
| 前后端合同漂移 | 中高 | V1.1-B/C/D 依赖 capability manifest、DocumentUnit、EvidenceSpan | backend route shape 变化会破坏 adapter smoke | route shape 只放 `dataServiceClient.ts`；每个 backend contract change 必须配 smoke fixtures。 |
| 多格式支持误判 | 中高 | 当前只 smoke 文本源 | 用户可能误以为 PDF/PPT/video/audio 已完整支持 | UI 不按扩展名硬猜；manifest 未声明时显示 unsupported。 |
| fixtures / smoke artifacts 泄漏本地路径 | 中 | 多次真实 smoke 会生成 fixtures 和 artifacts | 可能泄漏本地路径、cache path、artifact physical path | 保持 fixture path hygiene 检查；`.smoke-artifacts/` 不提交。 |
| session query 精确导航缺口 | 中 | session EvidenceSpan shape 未 smoke | session 体验弱于 workspace 体验 | 单独执行 Session Precise Navigation Smoke，不复用 workspace 结论。 |
| graph 仍是 read-only | 中 | V1.0/M4 只做 graph context | 用户可能期待编辑/治理图谱 | 文档明确 graph editing/governance 是未来阶段。 |
| data_service 单点依赖 | 中 | 关键能力都由 data_service contract 决定 | 前端无法独立完成 trace / unit / span 能力 | backend contract readiness 文档和 smoke gate 必须先行。 |
| 用户体验仍偏验证路径 | 中 | 当前多为 smoke-ready / browser-smoke-ready | 距离长期生产质量还有稳定性和大量边界场景缺口 | 后续需要真实用户路径回归、错误路径覆盖和性能检查。 |

## SWOT 分析矩阵

| 维度 | 内容 |
| --- | --- |
| Strengths 优势 | 已有清晰的分层架构：前端 UI、adapter、data_service contract 边界明确；V1.1-B/C/D 已跑通 source preview、unit navigation、EvidenceSpan highlight；真实 HTTP smoke、browser smoke、live experience smoke 证据链完整；No False Green 纪律较强，未把未完成能力伪装成 ready。 |
| Weaknesses 劣势 | 当前精确证据导航和 source trace 仍只覆盖文本源 workspace query / RC4 registry source 路径；session query、全来源类型、多格式摄入都未 ready；项目文档和阶段较多，维护成本高；后端 contract 一旦漂移，前端 smoke 容易失效。 |
| Opportunities 机会 | source trace backend contract 已补齐最大声明缺口之一；session precise navigation 可以复用 V1.1-D 的 Drawer / unit / span 基础；多格式 preview 可以基于 capability manifest 渐进开放；未来 Assessment / Governance / Graph editing 可在已有 source-grounded evidence 基础上扩展。 |
| Threats 威胁 | 若继续前端先行而 backend contract 未冻结，容易出现 route 虚构或假 ready；多格式、Assessment、Governance 同时推进会扩大风险面；如果忽视路径脱敏和 artifact_ref 边界，可能产生隐私/安全风险；如果用户把 browser-smoke-ready 当作 full production ready，期望管理会失控。 |
| 战略建议 | 短期先完成 V1.1-RC5 final release sync；中期做 Session Precise Navigation Smoke；长期另开 V1.2 处理多格式，并坚持 capability manifest gating。 |

## 未来仍需执行的开发阶段

下面这些是 V1.1 hardening 和 V1.1 之后仍然需要执行的阶段。它们不是当前 V1.1 已完成能力，不能提前写成 ready。

| 顺序 | 阶段 | 目标 | Entry Gate / 前置条件 | 验收重点 |
| --- | --- | --- | --- | --- |
| 1 | V1.1-RC5 Final Evidence Navigation Release Sync | 固化最终 evidence navigation release 状态 | `npm run check`、RC4 rerun、文档/drawio/checklist 同步 | scoped commit/push；记录 hash/branch/remote；不提交 `.smoke-artifacts/` |
| 2 | Session Precise Navigation Smoke | 把 EvidenceSpan 精确导航扩展到 session query | session query 返回与 workspace query 兼容的 `source_id + unit_id + evidence_id` | session answer citation 可打开 Drawer、选择 unit、显示 EvidenceSpan 高亮 |
| 3 | All-Source-Type Preview Contract Discovery | 明确 PDF/PPT/JSON/video/audio 等格式的 preview / unit / locator 合同 | data_service capability manifest 声明每种 source type 的 preview 级别和 locator 模型 | 只对真实支持的格式开放 UI，不按文件扩展名硬猜 |
| 4 | Multi-format Ingestion Integration | 做多格式摄入和状态展示 | 后端摄入合同、parser 支持范围、错误语义、artifact 隐私规则已冻结 | 导入状态可见；失败可解释；不把 artifact_ref 解析为路径 |
| 5 | Assessment / Mastery | 生成题目、尝试、评分、掌握度 | 后端 assessment contract、scoring semantics、source grounding 合同完成 | 题目可追溯来源；评分可解释；不影响 notebook 主链路 |
| 6 | Quality / Governance Console | 质量治理、反馈归档、规则/纠错工作流 | 后端 governance/correction rules contract 完成 | 不再只是 lightweight feedback；需正式审计状态和权限模型 |
| 7 | Graph Editing / Governance | 从 read-only graph context 升级为可编辑/治理图谱 | 后端 graph mutation/merge/delete/rebuild 合同完成 | 图谱写操作可审计、可回滚；不破坏 V1.0 read-only 路径 |
| 8 | Cloud Sync / Collaboration | 多设备同步和协作 | identity、权限、同步冲突、审计日志合同完成 | 数据隔离、冲突处理、离线/在线状态可靠 |

优先级建议：

1. 下一步应做 `V1.1-RC5 Final Evidence Navigation Release Sync`，固化本次 source trace 修复后的最终状态。
2. RC5 完成后再考虑 `Session Precise Navigation Smoke`，把 V1.1-D 的能力从 workspace query 扩展到 session query。
3. 多格式、Assessment、Governance、Graph editing 和 Cloud sync 都应进入 V1.2+ 或更后阶段，不应塞回 V1.1。

如果继续产品开发，应另开 V1.2，并且不得把 V1.2 能力回填成 V1.1 ready。
