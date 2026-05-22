# V4.0-G Editing Hardening Completion Note

文档状态：complete。  
对应计划：`docs/design/V4.0/v4_0_g_editing_hardening_plan.md`。

当前允许声明：

```text
V4.0-G complete: governed patch apply/reject/publish editing hardening ready for dev/local Workflow Console.
```

仍不能声明：

```text
complete Workflow Studio ready
complete AgentTalkWindow ready
production-ready external app support
full low-code canvas editing ready
distributed workflow engine ready
enterprise auth/OAuth/SSO ready
```

## 1. Implemented Scope

已完成：

- BFF structured patch list / apply / reject / publish routes。
- Apply / Reject / Publish 均要求 `user_confirmed=true`。
- `source=agent` 或缺少 confirmation 会被 BFF 拒绝。
- Apply 前 BFF 读取 Patch Diff；`requires_approval=true` 默认拒绝，不新增复杂 approval flow。
- Patch ownership guard 覆盖 template / draft / instance binding。
- Publish 要求 explicit version string 和 expected draft revision。
- Frontend WorkflowEditingPanel 暴露 Apply to Draft、Reject Patch、Publish New Version，但必须用户确认。
- Apply / Reject / Publish 后重新拉 BFF truth，不从 event payload 自建 runtime truth。
- Playwright 新增 editing browser smoke，保留 V4.0-F browser smoke。

未完成且不声明：

- Node drag -> Station runtime 写入。
- Edge drag -> WorkflowEdge runtime 写入。
- Inspector 表单 -> Draft 直接写入。
- 完整 Workflow Studio。
- 完整 AgentTalkWindow。

## 2. Evidence

测试结果：

```text
cd apps/workflow-console && npm test
21 passed

cd apps/workflow-console && npm run build
passed

cd apps/workflow-console && npm run test:e2e
2 passed

./.venv/bin/python -m pytest tests/test_v4_0_*.py -q
54 passed

./.venv/bin/python -m pytest tests/test_v3_6_*.py -q
86 passed

./.venv/bin/python -m pytest tests/test_v3_5_*.py -q
146 passed

./.venv/bin/python -m pytest -q
495 passed, 3 skipped

cd sdk/typescript && npm test
23 passed

xmllint --noout docs/design/V4.0/v4_0_current_gap_analysis.drawio
passed
```

## 3. Test Files

新增 / 扩展：

```text
tests/test_v4_0_editing_hardening_bff_routes.py
apps/workflow-console/src/__tests__/workflowEditingHardening.test.tsx
apps/workflow-console/e2e/workflow-editing-smoke.spec.ts
```

继续覆盖：

```text
tests/test_v4_0_frontend_no_direct_core_calls.py
tests/test_v4_0_contract_doc_alignment.py
apps/workflow-console/e2e/workflow-console-smoke.spec.ts
```

## 4. No False Green Boundary

当前只证明：

```text
governed patch apply/reject/publish editing hardening is ready for dev/local Workflow Console.
```

它不证明：

```text
complete canvas-to-runtime editing
complete Workflow Studio
complete AgentTalkWindow
production auth / SSO / multi-tenant readiness
```

## 5. Next Phase

建议进入：

```text
V4.0-H Canvas-to-runtime bridge
```

H 阶段应把 canvas / inspector 操作转换成受控 WorkflowPatch propose/diff/apply 流程，而不是直接写 WorkflowStore、Station 或 WorkflowEdge。
