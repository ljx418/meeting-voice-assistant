# V4.0-F Browser Smoke Baseline Plan

文档状态：implemented。  
前置状态：`V4.0 dev/local Workflow Console integration baseline ready` 已认可。  
阶段目标：固定使用 Playwright 补最小 browser-level smoke，证明当前 component-level + BFF integration E2E 在真实浏览器中可打开、可操作、可刷新。完成证据见 `v4_0_f_browser_smoke_completion_note.md`。

## 1. 阶段定位

V4.0-F 不是完整 Workflow Studio，也不是完整 AgentTalkWindow。它是 V4.0-E integration baseline 之后的浏览器级验收补强。

完成后只能声明：

```text
V4.0 dev/local Workflow Console browser smoke baseline ready.
```

仍不能声明：

```text
complete Workflow Studio ready
complete AgentTalkWindow ready
production-ready external app support
distributed workflow engine ready
enterprise auth/OAuth/SSO ready
full browser E2E ready
```

## 2. 目标

V4.0-F 需要验证：

- Workflow Console 可以在真实浏览器中打开。
- 页面通过 BFF structured routes 消费真实 V3.6/V4.0 fixture DTO。
- Board、station、artifact、approval、quality、trace summary 可见。
- ApprovalPanel 可以通过用户显式点击触发 workflow-bound `approval.respond`。
- ContextPanel 可以受控写入 `context.business`。
- EventBridge refresh 只触发重新拉取事实源，不从 event payload 自建 runtime truth。
- 前端不直接调用 `/v1/rpc` 或 `/v1/events/subscribe`。
- DOM 不泄露 token、Authorization、subscription token、raw trace payload、raw artifact content 或 raw connector payload。
- Patch apply / reject / publish UI action 在 F 阶段仍不暴露。

## 3. PR Slices

### F-PR1 Playwright Browser Smoke Scaffold

交付：

```text
apps/workflow-console/playwright.config.ts
apps/workflow-console/e2e/workflow-console-smoke.spec.ts
```

要求：

- 本阶段固定使用 Playwright，不再保留其他 browser smoke runner 选项。
- `apps/workflow-console/package.json` 增加 `npm run test:e2e`。
- Browser smoke 使用 `npm run build` 后的 Vite preview；本地调试可以使用 dev server，但 CI smoke 必须使用 preview。
- 测试 harness 必须连接真实 BFF/API server，不能 silent fallback 到 `demoData`。
- E2E mode 下显式设置 `VITE_HARNESSOS_DEMO_MODE=false`。
- 页面不得显示 `Demo / Fixture` badge。

### F-PR2 Real Fixture Server Harness

交付：

- Browser smoke fixture server。
- 复用当前 V4.0-E reference fixture / Gateway / BFF route。
- Test BFF server 内部持有 seeded `GatewayService` / V3.6 runtime fixture。
- Playwright 访问 frontend，frontend 访问同一个 test BFF。

要求 fixture 至少包含：

```text
WorkflowTemplate
WorkflowVersion
WorkflowInstance
StationRun
Job
Artifact
Approval
QualityEvaluation
WorkflowContext
Trace summary
EventBridge events
```

要求：

- BFF 不可用时测试必须失败，不能 fallback demoData。
- Browser smoke 不能全 mock；必须通过 test BFF 读取 board/status/output/artifact metadata/lineage/approval/quality/context DTO。

### F-PR3 Stable Test Selectors

交付：在 `apps/workflow-console` 增加稳定 `data-testid`。

必须包含：

```text
workflow-console
workflow-instance-selector
station-board
station-card
artifact-panel
approval-panel
approval-approve-button
quality-panel
context-panel
context-update-button
event-feed
```

要求：

- Playwright 尽量使用 `data-testid`，不依赖易变中文文案。
- `data-testid` 只用于测试稳定性，不改变 runtime contract。

### F-PR4 Browser Interaction Smoke

覆盖：

1. open workflow console
2. select workflow instance
3. render board
4. render station / artifact / approval / quality / trace summary
5. approve via ApprovalPanel
6. update context.business
7. receive EventBridge refresh
8. assert UI refreshed from board/status/context truth

要求：

- Approval 必须来自用户点击，不允许 Agent shell 自动触发。
- Context update 只能写 `business.*`。
- UI 收到 EventBridge event 后必须重新拉 board/status/context/approval DTO。
- Board/status refresh 后必须能在 DOM 中观察到真实 DTO 变化。

### F-PR5 Controlled EventBridge Trigger

覆盖：

- EventBridge refresh 不能依赖 sleep 或真实时间。
- 提供 test harness 可控触发方式，例如 test-only event emit 或 fixture 内部触发。
- 收到 event 后 UI 重新拉 board/status/context。
- UI 不从 event payload 构造 runtime state。
- 增加 fake event status payload 测试，确保 UI 不采信 event payload 的伪造状态。

要求：

- EventBridge event 只作为 refresh/display signal。
- `quality.evaluated` 仍不是 V4.0-F live 出门条件。

### F-PR6 No False Green Guards

覆盖：

- Playwright route intercept 断言 browser 不直接请求 `/v1/rpc`。
- Playwright route intercept 断言 browser 不直接请求 `/v1/events/subscribe`。
- BFF server 内部调用 Gateway/RPC 是允许的。
- DOM 不包含敏感字段。
- UI 不出现 patch apply / reject / publish 行为。
- 如可行，拦截 BFF response body 检查敏感字段。

禁止 DOM / network 出现：

```text
capability_token
subscription_token
Authorization
Bearer 
raw_trace_payload
raw_artifact_content
raw_connector_payload
secret-token-value
/v1/rpc
/v1/events/subscribe
workflow.patch.apply
workflow.patch.reject
workflow.template.publish
自动应用
自动发布
已帮你修改并发布
Apply Patch
Publish Version
```

### F-PR7 Docs / Evidence Sync

更新：

```text
docs/design/V4.0/00_README.md
docs/design/V4.0/v4_0_current_gap_analysis.md
docs/design/V4.0/v4_0_current_gap_analysis.drawio
docs/design/V4.0/v4_0_completion_audit_report.md
docs/design/V4.0/v4_0_e_reference_console_completion_note.md
```

新增：

```text
docs/design/V4.0/v4_0_f_browser_smoke_completion_note.md
```

## 4. 测试计划

新增：

```text
apps/workflow-console/e2e/workflow-console-smoke.spec.ts
apps/workflow-console/playwright.config.ts
```

建议命令：

```bash
cd apps/workflow-console && npm run test:e2e
cd apps/workflow-console && npm test
cd apps/workflow-console && npm run build
./.venv/bin/python -m pytest tests/test_v4_0_*.py -q
./.venv/bin/python -m pytest tests/test_v3_6_*.py -q
./.venv/bin/python -m pytest tests/test_v3_5_*.py -q
./.venv/bin/python -m pytest -q
cd sdk/typescript && npm test
xmllint --noout docs/design/V4.0/v4_0_current_gap_analysis.drawio
```

## 5. Acceptance Criteria

V4.0-F 完成必须满足：

- Browser 可以打开 Workflow Console。
- Browser smoke 使用 build 后的 Vite preview，不以 dev server 作为 CI smoke 依据。
- Real mode 下 BFF/API 不可用时测试失败，不能 fallback demoData。
- DOM 不显示 `Demo / Fixture` badge。
- Board / station / artifact / approval / quality / trace summary 可见。
- ApprovalPanel 用户点击后 workflow-bound approval side effect 可见。
- ContextPanel 写入 `context.business` 后 UI 可刷新显示新值。
- EventBridge refresh 能触发 UI 重新拉事实源。
- Fake event status payload 不被 UI 采信。
- Browser network 不直接调用 `/v1/rpc` 或 `/v1/events/subscribe`。
- DOM 和 `page.content()` 不泄露 token/raw payload。
- UI 不暴露 patch apply / reject / publish。
- Playwright 主要使用 `data-testid`。
- V4.0/V3.6/V3.5/full regression 继续通过。

## 6. Risks

| 风险 | 控制策略 |
| --- | --- |
| Browser smoke harness 启动不稳定 | 使用固定端口探测、失败即退出；CI smoke 使用 build + Vite preview，不 silent fallback。 |
| In-memory Gateway fixture 与 browser server 不共享 | 由同一测试进程创建 API app 和 fixture，前端只连该 server。 |
| EventBridge refresh 依赖真实时间 | 使用 test harness 可控触发或 fixture 内部触发，并在测试中等待 DTO reload 后的 UI 状态。 |
| Demo mode 误判为真实 E2E | E2E 环境禁用 `VITE_HARNESSOS_DEMO_MODE`，并断言 DOM 无 `Demo / Fixture`。 |
| No False Green 被弱化 | network intercept、DOM redaction、source scan 与 existing V4 tests 同时保留。 |
| 选择器因中文文案变化失效 | 使用固定 `data-testid`，中文文案只作为辅助断言。 |

## 7. Next Phases

V4.0-F 完成后，再进入：

```text
V4.0-G Editing hardening: workflow.patch.apply/reject/publish BFF/UI E2E.
V4.0-H Canvas-to-runtime bridge: node drag -> Station, edge -> WorkflowEdge, Inspector -> WorkflowPatch.
V4.0-I AgentTalkWindow stateful assistant: governed Agent workflow assistant.
```
