# ResearchNotebook V1.1 Design Docs

文档状态：V1.1-D-RC browser visual smoke passed；RC4 source trace backend fix 和 re-smoke passed；S1-FIX/S1-FE session precise navigation passed；S2 all-source-type contract discovery completed；S3 markdown/json backend contract API smoke passed；S4 markdown/json frontend browser smoke passed。
日期：2026-05-24。

## Positioning

ResearchNotebook V1.1 的目标是把 V1.0 的 source-level evidence metadata 升级为 NotebookLM-like 的来源预览和证据导航体验：

```text
answer -> citation -> source preview -> evidence locator -> source context
```

V1.1 不进入 multi-format ingestion、Assessment、Quality/Governance console、graph editing 或 cloud collaboration。

## Current Slice

当前状态：

- `V1.1-A Contract Discovery / Disabled Shell` 已完成：DTO fallback、adapter wrapper shell、Source Preview drawer disabled state、capability missing / unsupported UI 和 V1.1 contract docs 已落地；
- `V1.1-BE Backend Contract Enablement` 已在本地 `data_service/` 工作区完成：capability manifest route 与 source-level preview route 已加入后端合同并通过聚焦测试；
- `V1.1-B Source-Level Preview frontend integration` 已完成：capability manifest、source-level preview route、drawer rendering、安全文本渲染和 real data_service smoke 已通过；
- `V1.1-C-A DocumentUnit Navigation Contract Discovery / Disabled Shell` 已完成：DocumentUnit DTO、adapter shell、disabled Document Units section 和 metadata-only unit display 已落地；
- `V1.1-C-BE DocumentUnit Backend Contract Enablement` 已在本地 `data_service/` 工作区完成：DocumentUnit manifest、unit list/detail route、pagination、fixtures 和后端聚焦测试已通过；
- `V1.1-C Frontend Unit-Level Navigation Integration` 已完成 API-adapter/UI 接入：Source Preview Drawer 可加载 unit outline、选择 unit、加载 unit detail，并渲染 unit-level preview；
- `V1.1-D-BE EvidenceSpan Backend Contract Enablement` 已在本地 `data_service/` 工作区完成：EvidenceSpan route、workspace query evidence ids、offset/text basis、fixtures、backend tests 和 backend-only smoke 已通过；
- `V1.1-D Frontend EvidenceSpan Highlight / Precise Navigation Integration` 已完成 API-adapter/UI 接入：workspace answer citation 可打开 Source Preview Drawer、加载 unit detail、加载 EvidenceSpan detail，并对支持的 text offset 做安全高亮；
- `V1.1-D real data_service HTTP smoke` 已通过：workspace query 返回 `source_id + unit_id + evidence_id`，EvidenceSpan route 返回 `normalized_text / half_open / document_unit_text` offset contract；
- `V1.1-D-RC browser visual smoke` 已通过：真实浏览器打开 app、创建 workspace/source、打开 Source Preview、加载 DocumentUnit、提交 workspace query、点击 jumpable citation，并看到 EvidenceSpan 高亮；
- `V1.1-RC4 Source Trace Re-Smoke` 已执行：source create/list/get 返回 registry `source_id`，workspace query evidence 也观察到 registry source id，direct `sources.trace` 返回 HTTP 200；
- `V1.1-S1 Session Precise Navigation Smoke` 已重新执行：S1-FIX 后 session query 返回可解析的 `source_id + unit_id + evidence_id` evidence item，unit detail 和 EvidenceSpan detail 均可解析；
- `V1.1-S1-FE Session Browser Smoke` 已通过：session answer citation 在浏览器中打开 Source Preview Drawer、选中 DocumentUnit 并显示 EvidenceSpan 高亮；
- `V1.1-S2 All-Source-Type Contract Discovery` 已执行：完成 text/pdf/pptx/json/markdown/html/video/audio 的合同发现；
- `V1.1-S3 Multi-Format Backend Contract Enablement` 已完成第一批格式：`markdown/json` 的 preview、DocumentUnit、workspace query evidence 和 EvidenceSpan 后端/API smoke 已通过；
- `V1.1-S4 Multi-Format Frontend Integration` 已完成第一批格式：`markdown/json` 的 Preview、DocumentUnit、workspace query citation 和 EvidenceSpan highlight 浏览器 smoke 已通过；
- 可以声明 Source Preview ready for data_service-supported source-level text sources；
- 可以声明 DocumentUnit navigation disabled shell ready；
- 可以声明 data_service DocumentUnit backend contract ready for frontend integration after backend change review；
- 可以声明 ResearchNotebook Unit-Level Source Navigation integration-ready for data_service-supported text sources；
- 可以声明 data_service EvidenceSpan backend contract ready for ResearchNotebook V1.1-D frontend integration after backend change review；
- 可以声明 ResearchNotebook V1.1-D EvidenceSpan Highlight browser-smoke-ready for data_service-supported text-source workspace query citations；
- 可以声明 ResearchNotebook V1.1 precise evidence navigation browser-smoke-ready for the same supported workspace query path；
- 可以声明 source trace integration ready for registry source_id-backed sources covered by RC4 smoke。

## Manual Acceptance Distance

如果手动验收目标是当前已经完成的 workspace query 文本源证据导航路径，则还剩 0 个开发阶段。

如果手动验收目标是 session precise navigation，则还剩 0 个开发阶段。S1-FE 已用浏览器路径证明 session answer citation 能打开 Drawer、选择正确 unit、显示 EvidenceSpan 高亮。

## Documents

| 文件 | 用途 |
| --- | --- |
| `v1_1_current_gap_analysis.md` | V1.1 当前 gap、阶段切片和声明边界。 |
| `v1_1_current_gap_analysis.drawio` | V1.1-A 到 V1.1-RC 的可视化进度图。 |
| `capability-manifest-contract.md` | data_service capability/version manifest 合同。 |
| `source-preview-contract.md` | SourcePreview / DocumentUnit / preview route 合同。 |
| `document-unit-navigation-contract.md` | DocumentUnit navigation backend gate、DTO、disabled shell 和 No False Green 规则。 |
| `evidence-navigation-contract.md` | EvidenceSpan / locator / citation navigation 合同。 |
| `feature-route-matrix.md` | V1.1 feature route / adapter shell / unsupported / future backend matrix。 |
| `v1_1_b_source_level_preview_plan.md` | V1.1-B conditional plan and original blocked entry-gate result before V1.1-BE。 |
| `v1_1_backend_contract_readiness.md` | V1.1-BE data_service backend contract readiness, fixtures, test results and frontend entry decision。 |
| `v1_1_source_preview_smoke_report.md` | V1.1-B real data_service smoke report for source-level preview integration。 |
| `v1_1_c_document_unit_navigation_plan.md` | V1.1-C-A disabled shell implementation plan and declaration boundary。 |
| `v1_1_document_unit_backend_readiness.md` | V1.1-C-BE DocumentUnit backend contract readiness, fixtures, tests and frontend entry decision。 |
| `v1_1_c_frontend_unit_navigation_plan.md` | V1.1-C frontend unit navigation implementation scope and verification。 |
| `v1_1_unit_navigation_smoke_report.md` | V1.1-C frontend smoke result and real data_service smoke status。 |
| `v1_1_d_evidence_span_backend_readiness.md` | V1.1-D-BE EvidenceSpan backend contract readiness, offset semantics, fixtures and frontend entry decision。 |
| `v1_1_d_frontend_evidence_navigation_plan.md` | V1.1-D frontend EvidenceSpan highlight implementation scope and verification。 |
| `v1_1_d_frontend_evidence_navigation_smoke_report.md` | V1.1-D frontend mocked/API-adapter smoke result, real HTTP smoke result, accepted degraded states and browser-visual-smoke gap。 |
| `v1_1_d_rc_browser_visual_smoke_report.md` | V1.1-D-RC real browser visual smoke result, screenshot/log artifact locations and declaration decision。 |
| `v1_1_release_readiness_checklist.md` | V1.1 release readiness status table and No False Green statements。 |
| `v1_1_rc1_release_handoff.md` | V1.1-RC1 final handoff summary, scoped sync rules, accepted degraded states and next phase pointer。 |
| `v1_1_rc2_live_experience_smoke_report.md` | V1.1-RC2 live experience smoke report using already-running local frontend/backend services。 |
| `v1_1_rc4_source_trace_resmoke_report.md` | V1.1-RC4 source trace direct route re-smoke result；records scoped source trace integration PASS。 |
| `v1_1_rc5_final_release_sync.md` | V1.1-RC5 final release sync scope, verification evidence, still-not-ready boundaries, and scoped commit/push rules。 |
| `v1_1_s1_session_precise_navigation_smoke_report.md` | V1.1-S1 session precise navigation smoke result；records historical `GRAPH_ONLY_NO_EVIDENCE`, S1-FIX `HAS_EVIDENCE_SPAN_IDS`, and API-smoke-ready decision。 |
| `v1_1_s1_fe_session_browser_smoke_report.md` | V1.1-S1-FE browser smoke result；records session citation click, Drawer navigation, selected unit, EvidenceSpan highlight, and browser-smoke-ready decision。 |
| `v1_1_s1_fe_sync_status.md` | V1.1-S1-FE sync status；records latest S1 API/browser smoke evidence and the audited S2 entry direction。 |
| `v1_1_s2_all_source_type_contract_discovery.md` | V1.1-S2 all-source-type contract discovery；records per-source-type backend capability baseline and blockers。 |
| `v1_1_s3_multi_format_backend_readiness.md` | V1.1-S3 markdown/json backend contract readiness；records manifest, preview, DocumentUnit, query evidence and EvidenceSpan API smoke。 |
| `v1_1_s4_multi_format_frontend_smoke_report.md` | V1.1-S4 markdown/json frontend browser smoke；records Preview, DocumentUnit and EvidenceSpan highlight result。 |
| `v1_1_final_manual_acceptance_and_sync.md` | V1.1 FINAL 收口文档；records final acceptance scope, command evidence, fixture hygiene and scoped sync scope。 |
| `v1_1_manual_acceptance_report.md` | V1.1 manual acceptance report；records manually acceptable workspace/session text-source scope, checklist, and fill-in fields。 |
| `v1_1_manual_validation_cases.md` | V1.1 手工验证用例；records text/session/markdown/json/source trace/fallback/cleanup 的逐项验收表。 |
| `v1_1_usage_guide_image_prompts.md` | V1.1 使用指南图像 prompts；records GPT Image 2 prompt set and combined guide prompt。 |

## Entry Gate

V1.1 正式实现 Source Preview / Evidence Navigation 前，`data_service` 必须冻结：

- capability/version manifest；
- source preview route；
- `DocumentUnit` model；
- `EvidenceSpan` model；
- citation locator model；
- source trace / source preview relationship；
- supported source formats manifest。

Source-level preview 后端合同已在本地 `data_service/` 工作区完成，ResearchNotebook 前端 V1.1-B 已完成真实 route 适配、mapper、UI smoke 和 readiness 文档。

V1.1-C-BE 已完成 DocumentUnit backend contract enablement，提供 `document_units=true`、`unit_level_navigation=true`、unit list/detail route、pagination、fixtures 和后端聚焦测试。

ResearchNotebook V1.1-C frontend integration 已完成 API-adapter/UI 接入并通过 `npm run check`。V1.1-C-RC real data_service HTTP smoke 已执行并通过，覆盖 capability manifest、source preview 回归、unit list、unit detail、pagination、unknown unit 404、artifact-like unit id 422 和 workspace cleanup。

EvidenceSpan backend contract 已在 V1.1-D-BE 完成，包含 unit-scoped EvidenceSpan route、workspace query evidence ids、`offset_basis=normalized_text`、`offset_range=half_open`、`text_basis=document_unit_text`。

ResearchNotebook V1.1-D frontend API-adapter/UI 接入已完成并通过 `npm run check`。真实 data_service HTTP smoke 已执行并通过 route/evidence contract：capability flags、unit list/detail、workspace query jumpable evidence、EvidenceSpan detail 和 offset contract 均通过。浏览器视觉级 smoke 已通过，覆盖 citation click、drawer/unit loading 和 visible highlight。

## Current V1.1-B Decision

V1.1-BE has now added the required source-level preview backend contract in the local `data_service/` working tree. Therefore:

```text
V1.1-A Source Preview shell: READY
V1.1-BE backend contract: READY_FOR_FRONTEND_INTEGRATION_AFTER_BACKEND_CHANGE_REVIEW
V1.1-B frontend integration: INTEGRATION_SMOKE_READY_FOR_TEXT_SOURCE
V1.1-C-A DocumentUnit shell: READY_DISABLED_SHELL
V1.1-C-BE DocumentUnit backend contract: READY_FOR_FRONTEND_INTEGRATION_AFTER_BACKEND_CHANGE_REVIEW
V1.1-C frontend unit navigation: INTEGRATION_READY_FOR_SUPPORTED_TEXT_SOURCES
V1.1-C real data_service smoke: PASS
V1.1-D-BE EvidenceSpan backend contract: READY_FOR_FRONTEND_INTEGRATION_AFTER_BACKEND_CHANGE_REVIEW
V1.1-D frontend EvidenceSpan highlight: BROWSER_SMOKE_READY_FOR_SUPPORTED_TEXT_WORKSPACE_QUERY
V1.1-D real data_service HTTP smoke: PASS_WITH_ACCEPTED_DEGRADED_STATES
V1.1-D browser visual smoke: PASS
V1.1-RC4 source trace re-smoke: PASS_SCOPED_REGISTRY_SOURCE_TRACE
V1.1-S1 session precise navigation smoke: API_SMOKE_READY_HAS_EVIDENCE_SPAN_IDS
V1.1-S1-FE session browser smoke: BROWSER_SMOKE_READY_FOR_SUPPORTED_TEXT_SESSION_QUERY
V1.1-S2 all-source-type contract discovery: COMPLETE
V1.1-S3 markdown/json backend contract: API_SMOKE_READY
V1.1-S4 markdown/json frontend smoke: BROWSER_SMOKE_READY
V1.1-FINAL manual acceptance / sync: READY_FOR_SCOPED_COMMIT
```

Do not generalize this to all sessions or all source types. Source trace integration is scoped to registry source_id-backed sources covered by RC4 smoke. Session precise navigation is scoped to data_service-supported text-source session query citations carrying `source_id + unit_id + evidence_id`. S4 confirms markdown/json frontend browser paths for workspace query citations, but PDF/PPTX/HTML/video/audio remain NOT_READY.
