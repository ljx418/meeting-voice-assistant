# V4.0-O Governed Canvas Proposal Workflow Plan

文档状态：V4.0-O planned。本文细化 V4.0-N 后的项目风险，并据此修订下一阶段开发计划。V4.0-O 仍是 dev/local Workflow Console 的治理型 proposal workflow hardening，不是完整 Workflow Studio、完整 AgentTalkWindow、controlled executor 或 production readiness。

允许完成声明：

```text
V4.0-O complete: governed canvas proposal workflow ready for expanded dev/local Workflow Console validation.
```

禁止完成声明：

```text
complete Workflow Studio ready
full low-code canvas editing ready
complete AgentTalkWindow ready
controlled executor ready
Agent executor ready
autonomous workflow editing ready
direct canvas-to-runtime mutation ready
production-ready external app support
```

## 1. 风险细化

| 风险 ID | 风险 | 严重度 | 概率 | 触发信号 | V4.0-O 控制措施 | 审计证据 |
| --- | --- | --- | --- | --- | --- | --- |
| O-R1 | Canvas 越界写 runtime truth | critical | medium | Canvas drag、edge drag 或 Inspector 直接写 WorkflowDraft、WorkflowStore、WorkflowEdge | proposal-only validator、前端 source scan、BFF route allowlist | Node/edge/Inspector proposal tests、no direct store tests |
| O-R2 | Patch 多状态竞态 | high | high | 多个 pending patch、apply/reject 后 UI 仍指向旧 diff | PatchQueueDTO、selected_patch_id、draft_revision guard、stale state UI | patch queue BFF/UI/browser tests |
| O-R3 | 高风险 patch 治理绕过 | critical | medium | requires_approval=true 被直接 apply 或 publish | 复用 V4.0-G governed apply guard、UI 禁用、BFF 拒绝 | high-risk apply blocked tests |
| O-R4 | Agent 权限扩张为 executor | critical | medium | Agent route 增加 apply/publish/respond/update/emit/start/rerun | action policy denylist、handoff-only contract、forbidden copy scan | Agent forbidden action tests |
| O-R5 | CanvasProjection freshness 不清晰 | high | medium | UI 展示 stale board/status/draft，但用户误以为已刷新 | source_refs、generated_at、draft_revision、freshness badge | projection freshness tests |
| O-R6 | EventBridge payload 被误作事实源 | high | medium | UI 从 event payload 构造 station、edge、evidence 或 canvas truth | event-only-refresh rule、fake payload browser smoke | fake event payload rejection tests |
| O-R7 | Inspector payload 注入 | high | medium | raw trace、secret、layout、connector payload 被提交到 proposal | per-operation field allowlist、schema validator、redaction | inspector mapping and redaction tests |
| O-R8 | Edge contract 误接收 | high | medium | 自环、重复边、缺失 station、cycle 或 artifact kind 不兼容仍生成 proposal | edge contract validator V2、schema_ref MVP check | edge contract tests |
| O-R9 | Node catalog 语义漂移 | high | medium | 前端 catalog 私自定义 station_kind、skill_refs、connector_refs | BFF controlled catalog endpoint、catalog_version、catalog diff | catalog versioning tests |
| O-R10 | E2E fixture 污染 | medium | high | 浏览器测试依赖执行顺序或共享 patch/draft 状态 | per-spec seed/reset、isolated template/draft ids | fixture isolation smoke |
| O-R11 | Redaction 回归 | high | medium | DTO、DOM、error response 泄露 token、Authorization、raw payload | centralized redaction assertions、DOM scan | redaction regression tests |
| O-R12 | 文档过度声明 | medium | high | 文档把 dev/local baseline 写成 complete Studio 或 production ready | allowed/forbidden claim audit、README/gap sync | contract doc alignment tests |
| O-R13 | production boundary 被误解 | high | medium | 外部接入、auth、multi-tenant 被当作已完成能力 | explicit non-goals、V4.0-R preflight only | audit report non-goal section |
| O-R14 | 前端异步状态覆盖 | medium | high | Event refresh 覆盖 active panel、selected patch、dirty Inspector | explicit UI state model、stale dirty guard | frontend state tests |
| O-R15 | 兼容路径被提前移除 | medium | medium | Claude/OpenHarness compatibility path 被删除但 replacement 未验证 | compatibility inventory、source scan | compatibility regression tests |

## 2. 修订后的 V4.0-O 开发计划

V4.0-O 不再优先推进 AgentTalkWindow Interaction E2E。下一阶段应先处理 V4.0-N 后暴露出的 canvas proposal workflow 风险，把 proposal queue、projection freshness、catalog versioning、Inspector mapping、edge contract、fixture isolation 和声明审计做成可验证基线。

| PR | 目标 | 主要工作 | 覆盖风险 |
| --- | --- | --- | --- |
| O-PR1 | Risk Register and Claim Guard Baseline | 将本风险表纳入 V4.0 文档审计；新增 allowed/forbidden claim source scan。 | O-R12, O-R13 |
| O-PR2 | PatchQueueDTO and Selection State | 定义 pending/applied/rejected/stale patch queue read model；UI 只通过 selected_patch_id 展示当前 diff。 | O-R2, O-R14 |
| O-PR3 | Projection Freshness Contract | CanvasDraftProjection 增加 source_refs、generated_at、draft_revision、board/status freshness marker 和 stale reason。 | O-R5, O-R6 |
| O-PR4 | Catalog Source-of-Truth and Versioning | controlled node catalog 从 BFF 输出；前端只渲染 catalog；新增 catalog_version mismatch / diff 提示。 | O-R9 |
| O-PR5 | Inspector Schema Mapping V2 | 每个 Inspector operation 固定字段 allowlist；typing 只改 local dirty state；生成 Patch 时拒绝 secret/raw/layout fields。 | O-R7, O-R14 |
| O-PR6 | Edge Contract Validation V2 | 增强 update_edge add/remove/update 校验：same draft、missing station、自环、重复边、cycle、artifact direction/schema_ref MVP。 | O-R8 |
| O-PR7 | Proposal Apply UX and State Race Hardening | apply/reject/publish 后强制从 BFF truth refresh；dirty Inspector 与 stale patch 显示明确阻断态。 | O-R2, O-R3, O-R14 |
| O-PR8 | E2E Fixture Isolation | 每个 browser smoke 使用独立 workflow_template_id、draft_revision、patch_id；测试结束不依赖共享状态。 | O-R10 |
| O-PR9 | Redaction and Event Truth Regression | 统一检查 DTO、DOM、error response、event payload；EventBridge 只触发 refresh。 | O-R6, O-R11 |
| O-PR10 | Compatibility and Documentation Sync | 更新 README、gap、audit、UI contract、event map、mock checklist 和 low-code baseline；保留 compatibility path。 | O-R12, O-R15 |

## 2.1 P0 总体边界

```text
CanvasDraftProjection、PatchQueueDTO、catalog versioning 均是 BFF/UI read model。
它们不能写入 WorkflowTemplate / WorkflowDraft / WorkflowVersion / WorkflowStore。
Node / Edge / Inspector 只能生成 WorkflowPatch proposal。
Apply / Reject / Publish 继续复用 V4.0-G user_confirmed path。
EventBridge 只触发 refresh，UI 必须重新拉 canvas projection、patch queue、catalog、board/status 和 patch diff DTO。
Agent 仍不能 apply / publish / approval.respond / context.update / business.event.emit / start workflow / rerun station。
```

## 2.2 Required DTO Contracts

PatchQueueDTO 必须包含：

```text
patch_id
workflow_template_id
workflow_draft_id
base_revision
current_draft_revision
status
risk_flags
requires_approval
selected
stale_reason
conflict_reason
created_at
updated_at
```

PatchQueueDTO status 固定为：

```text
proposed
selected
applied
rejected
stale
blocked
conflicted
```

CanvasDraftProjection freshness 必须包含：

```text
source_refs
generated_at
draft_revision
board_status_timestamp or status_updated_at
patch_queue_revision
freshness_state
stale_reasons[]
```

freshness_state 固定为：

```text
fresh
stale_draft
stale_board
stale_patch
unknown
```

BFF catalog DTO 必须包含：

```text
catalog_id
catalog_version
node_template_id
station_kind
schema_version
allowed_skill_refs
allowed_connector_refs
allowed_artifact_kinds
allowed_quality_rules
allowed_approval_policies
```

Inspector operation allowlist 固定为：

```text
update_station_prompt: station_id, prompt_patch, prompt_ref
update_connector: station_id, connector_refs, connector_patch
update_artifact_contract: station_id, contract_id, contract_patch
update_quality_rule: quality_contract_id, quality_patch
update_approval_point: station_id, approval_required, approval_policy
```

必须拒绝：

```text
unknown fields
x / y / zoom / viewport / selectedNode / panelCollapsed / activeTab
token
Authorization
raw_trace_payload
raw_artifact_content
raw_connector_payload
secret
```

## 2.3 Event Truth Rule

EventBridge event payload 不得构造以下 truth：

```text
canvas truth
patch queue truth
catalog truth
edge truth
evidence truth
```

收到事件后，UI 只能触发 refresh，并重新拉取：

```text
canvas projection
patch queue
catalog
board/status
patch diff DTO
```

## 3. 后续阶段顺序

| 阶段 | 修订后定位 | 进入条件 |
| --- | --- | --- |
| V4.0-O | Governed Canvas Proposal Workflow | N 完成后先收敛 proposal queue、projection freshness、catalog/version、Inspector/edge validation 和 E2E fixture isolation。 |
| V4.0-P | AgentTalkWindow Interaction E2E | O 通过后再推进 Agent explain/summarize/suggest/handoff/evidence review 交互闭环；仍无 executor。 |
| V4.0-Q | Controlled Executor Design Gate | P 通过后只做受控执行器设计门禁：policy、approval、capability、sandbox、rollback、kill switch。 |
| V4.0-R | Production Readiness Preflight | Q 之后再审计 auth/SSO/multi-tenant/observability/security/secret management。 |

## 4. 测试计划

后端和合同测试：

```text
tests/test_v4_0_canvas_patch_queue_bff.py
tests/test_v4_0_canvas_projection_freshness.py
tests/test_v4_0_canvas_edge_contracts.py
tests/test_v4_0_inspector_mapping_v2.py
tests/test_v4_0_node_catalog_versioning.py
tests/test_v4_0_canvas_proposal_scope_redaction.py
tests/test_v4_0_claim_guard.py
```

前端测试：

```text
apps/workflow-console/src/__tests__/canvasPatchQueue.test.tsx
apps/workflow-console/src/__tests__/canvasProjectionFreshness.test.tsx
apps/workflow-console/src/__tests__/inspectorMappingV2.test.tsx
apps/workflow-console/src/__tests__/nodeCatalogVersioning.test.tsx
```

浏览器 smoke：

```text
apps/workflow-console/e2e/workflow-canvas-patch-queue-smoke.spec.ts
apps/workflow-console/e2e/workflow-inspector-mapping-smoke.spec.ts
apps/workflow-console/e2e/workflow-catalog-versioning-smoke.spec.ts
```

必测断言：

```text
Node drag creates proposal only
Edge drag uses update_edge only
Inspector typing sends no network request
Generate Patch sends exactly one proposal request
Apply/reject/publish refreshes from BFF truth
PatchQueue selected_patch_id cannot point to stale diff silently
CanvasProjection contains source_refs and freshness markers
Event payload cannot create canvas truth
Catalog mismatch is visible and blocks proposal
Secret/raw/layout fields are rejected
High-risk patch cannot be directly applied
No direct /v1/rpc browser request
No direct /v1/events/subscribe browser request
No forbidden copy such as 自动应用 or 自动发布
```

回归命令：

```bash
./.venv/bin/python -m pytest tests/test_v4_0_canvas_patch_queue_bff.py tests/test_v4_0_canvas_projection_freshness.py tests/test_v4_0_canvas_edge_contracts.py tests/test_v4_0_inspector_mapping_v2.py tests/test_v4_0_node_catalog_versioning.py tests/test_v4_0_canvas_proposal_scope_redaction.py tests/test_v4_0_claim_guard.py -q
./.venv/bin/python -m pytest tests/test_v4_0_*.py -q
./.venv/bin/python -m pytest tests/test_v3_6_*.py -q
./.venv/bin/python -m pytest tests/test_v3_5_*.py -q
./.venv/bin/python -m pytest -q
cd apps/workflow-console && npm test
cd apps/workflow-console && npm run build
cd apps/workflow-console && npm run test:e2e
cd sdk/typescript && npm test
xmllint --noout docs/design/V4.0/v4_0_current_gap_analysis.drawio
```

## 5. 文档同步范围

V4.0-O 实施时必须同步审计以下文档：

```text
docs/design/V4.0/00_README.md
docs/design/V4.0/v4_0_current_gap_analysis.md
docs/design/V4.0/v4_0_current_gap_analysis.drawio
docs/design/V4.0/v4_0_completion_audit_report.md
docs/design/V4.0/v4_0_ui_contract_map.md
docs/design/V4.0/v4_0_event_contract_map.md
docs/design/V4.0/v4_0_mock_to_real_contract_checklist.md
docs/design/V4.0/v4_0_stitch_prototype_mapping.md
docs/design/V4.0/v4_0_workflow_studio_low_code_baseline.md
```

V4.0-O completion note 需要新增：

```text
docs/design/V4.0/v4_0_o_governed_canvas_proposal_workflow_completion_note.md
```
