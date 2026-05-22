# V4.0-F Browser Smoke Baseline Completion Note

文档状态：complete。  
对应计划：`docs/design/V4.0/v4_0_f_browser_smoke_plan.md`。  
当前阶段允许声明：

```text
V4.0 dev/local Workflow Console browser smoke baseline ready.
```

## 1. Allowed Claim After Completion

本阶段通过后，允许声明：

```text
V4.0 dev/local Workflow Console browser smoke baseline ready.
```

仍不能声明：

```text
complete Workflow Studio ready
complete AgentTalkWindow ready
production-ready external app support
full browser E2E ready
distributed workflow engine ready
enterprise auth/OAuth/SSO ready
```

## 2. Browser Smoke Evidence

V4.0-F 固定使用 Playwright，不再保留其他 browser smoke runner 选项。已落地：

```text
apps/workflow-console/playwright.config.ts
apps/workflow-console/e2e/workflow-console-smoke.spec.ts
apps/workflow-console/package.json -> npm run test:e2e
```

Browser smoke 必须使用：

```text
npm run build
Vite preview
test BFF server
seeded GatewayService / V3.6 runtime fixture
VITE_HARNESSOS_DEMO_MODE=false
```

已验证：

- Browser 打开 Workflow Console。
- Browser 选择 workflow instance。
- Board / station / artifact / approval / quality / trace summary 渲染成功。
- ApprovalPanel 用户显式点击 approve 后，board/status 刷新并反映 workflow-bound side effect。
- ContextPanel 更新 `context.business` 后，context 重新拉取并显示新值。
- EventBridge 可控触发 refresh，UI 重新拉 board/status/context/approval。
- Fake event status payload 不被 UI 采信。
- 页面不显示 `Demo / Fixture` badge。
- BFF 不可用时测试失败，不能 fallback demoData。

## 3. Network And Redaction Evidence

Playwright 只检查浏览器发出的请求。已验证：

- Browser request 不得访问 `/v1/rpc`。
- Browser request 不得访问 `/v1/events/subscribe`。
- Browser request 允许访问 `/bff/*` 和 frontend assets。
- BFF 后端内部调用 Gateway/RPC 允许，不作为 browser network violation。

DOM / HTML 检查必须覆盖 `document.body.textContent` 和 `page.content()`，不得出现：

```text
capability_token
subscription_token
Authorization
Bearer
raw_trace_payload
raw_artifact_content
raw_connector_payload
secret-token-value
```

本阶段以 browser request + DOM / HTML redaction 为出门证据；BFF DTO redaction 继续由 V4.0-A2/D/E focused tests 覆盖。

## 4. Forbidden UI Action Evidence

V4.0-F 仍不得暴露 editing / publish action。Browser smoke 和 existing source scan 证明 UI 不出现：

```text
workflow.patch.apply
workflow.patch.reject
workflow.template.publish
自动应用
自动发布
已帮你修改并发布
Apply Patch
Publish Version
```

Patch Diff 可以展示，但不可执行 apply / reject / publish。

## 5. Stable Selector Evidence

Playwright 使用稳定 `data-testid`。已覆盖：

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

## 6. Regression Commands

本阶段记录以下命令结果：

```bash
cd apps/workflow-console && npm run test:e2e
1 passed

cd apps/workflow-console && npm test
18 passed

cd apps/workflow-console && npm run build
passed

./.venv/bin/python -m pytest tests/test_v4_0_*.py -q
50 passed

./.venv/bin/python -m pytest tests/test_v3_6_*.py -q
86 passed

./.venv/bin/python -m pytest tests/test_v3_5_*.py -q
146 passed

./.venv/bin/python -m pytest -q
491 passed, 3 skipped

cd sdk/typescript && npm test
23 passed

xmllint --noout docs/design/V4.0/v4_0_current_gap_analysis.drawio
passed
```

## 7. Completion Status

当前状态：

```text
V4.0-F complete: Browser Smoke Baseline ready.
```

仍未完成，且不能声明：

- complete Workflow Studio ready
- complete AgentTalkWindow ready
- production-ready external app support
- full browser E2E ready
- distributed workflow engine ready
- enterprise auth/OAuth/SSO ready
