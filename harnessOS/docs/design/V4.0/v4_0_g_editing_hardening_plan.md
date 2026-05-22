# V4.0-G Editing Hardening Plan

文档状态：implemented。  
前置基线：V4.0-F Browser Smoke Baseline complete。  
本阶段只做 governed editing hardening，不做完整 Workflow Studio。

## 1. 阶段定位

V4.0-G 的目标是把 V4.0-B/C/E/F 中已经可展示的 Patch Diff / Risk 信息推进到受治理的编辑闭环：

```text
Patch Diff / Risk Flags
  -> user-confirmed Apply to Draft
  -> user-confirmed Reject Patch
  -> user-confirmed Publish New Version
  -> refresh draft/version/patch/status/board from BFF truth
```

完成后最多声明：

```text
V4.0-G complete: governed patch apply/reject/publish editing hardening ready for dev/local Workflow Console.
```

仍不能声明：

```text
complete Workflow Studio ready
complete AgentTalkWindow ready
production-ready external app support
full low-code canvas editing ready
```

## 2. P0 Boundaries

- `requires_approval=true` 的 Patch 默认不能 apply。
- V4.0-G 不新增复杂 workflow patch approval flow。
- BFF apply route 在调用 `workflow.patch.apply` 前先读取 diff 并检查 `requires_approval`。
- Apply / Reject / Publish 必须带 `user_confirmed=true`。
- `source=agent` 或缺少 user confirmation 必须拒绝。
- Agent 不能自动 apply / publish。
- Node drag 不创建 Station。
- Edge drag 不写 WorkflowEdge。
- Inspector 表单不直接写 draft。
- 所有写动作只能走 BFF structured route -> Gateway RPC -> V3.6 contract。
- 不直接访问 WorkflowStore / WorkflowVersion snapshot。

## 3. BFF Routes

新增 / 补齐：

```text
GET  /bff/instances/{workflow_instance_id}/patches
POST /bff/workflows/{workflow_template_id}/patches/{workflow_patch_id}/apply
POST /bff/workflows/{workflow_template_id}/patches/{workflow_patch_id}/reject
POST /bff/workflows/{workflow_template_id}/publish
```

继续使用：

```text
GET /bff/workflows/{workflow_template_id}/patches/{workflow_patch_id}/diff
GET /bff/instances/{workflow_instance_id}/patches/{workflow_patch_id}/diff
GET /bff/workflows/{workflow_template_id}/versions
```

## 4. DTO

BFF 返回 redacted DTO：

```text
WorkflowPatchProposalDTO
PatchDiffDTO
PatchApplyResultDTO
PatchRejectResultDTO
PublishVersionDTO
```

DTO 不得包含：

```text
capability_token
subscription_token
Authorization
Bearer
secret
raw_trace_payload
raw_artifact_content
raw_connector_payload
upstream signed URL
```

## 5. Ownership And Capability

必须校验：

- `patch_id` 属于 route `workflow_template_id`。
- `patch.workflow_draft_id` 属于 template latest draft。
- proposed patch 的 `base_revision` 与 current draft revision 匹配。
- repeated applied patch 可以 idempotent apply，不重复修改 draft。
- patch metadata 绑定 `workflow_instance_id` 时必须与 selected instance 一致。
- same-scope wrong-template / wrong-draft / wrong-patch 必须拒绝。
- missing capability 返回 `CAPABILITY_DENIED`。
- cross-scope 返回 `SCOPE_MISMATCH`。

Capability：

```text
workflow.patch.apply/reject -> workflow_patches.write
workflow.patch.diff/list -> workflow_patches.read
workflow.template.publish -> workflow_versions.publish
workflow.version.list -> workflows.read
```

## 6. Frontend

Workflow Console 新增受控编辑动作：

- Patch Diff 面板展示 before / after / risk_flags / requires_approval。
- Apply to Draft 需要浏览器确认。
- Reject Patch 需要浏览器确认。
- Publish New Version 需要显式 version string 和 expected draft revision。
- Apply / Reject / Publish 成功后 refresh runtime truth，不从 event payload 自建事实。

禁止：

- Agent 自动 apply。
- Agent 自动 publish。
- `自动应用` / `自动发布` / `已帮你修改并发布` 等误导文案。
- Canvas drag / Edge drag / Inspector form 直接写 runtime。

## 7. Tests

新增 / 扩展：

```text
tests/test_v4_0_editing_hardening_bff_routes.py
apps/workflow-console/src/__tests__/workflowEditingHardening.test.tsx
apps/workflow-console/e2e/workflow-editing-smoke.spec.ts
```

回归：

```bash
cd apps/workflow-console && npm test
cd apps/workflow-console && npm run build
cd apps/workflow-console && npm run test:e2e
./.venv/bin/python -m pytest tests/test_v4_0_*.py -q
./.venv/bin/python -m pytest tests/test_v3_6_*.py -q
./.venv/bin/python -m pytest tests/test_v3_5_*.py -q
./.venv/bin/python -m pytest -q
cd sdk/typescript && npm test
xmllint --noout docs/design/V4.0/v4_0_current_gap_analysis.drawio
```

## 8. Next Phase

V4.0-H Canvas-to-runtime bridge：

- node drag -> propose Station patch
- edge drag -> propose WorkflowEdge patch
- Inspector form -> propose controlled WorkflowPatch
- no direct draft/store write
