# V3.6-I Completion Note

文档状态：V3.6-I complete: Safe workflow patch contract ready.

当前下一阶段：V3.6-J Dummy Pipeline E2E / V4.0 Gate.

## Scope

V3.6-I 完成的是 Workflow Patch / Agent Editing Contract，不是 dummy pipeline E2E、完整 Workflow Studio 或 AgentTalkWindow。

本阶段冻结能力：

- `workflow.patch.propose`
- `workflow.patch.diff`
- `workflow.patch.apply`
- `workflow.patch.reject`
- Patch 状态机：`proposed -> applied`、`proposed -> rejected`
- repeated apply / repeated reject idempotent
- rejected patch apply 与 applied patch reject 返回 `WORKFLOW_PATCH_CONFLICT`
- patch 绑定 `workflow_template_id`、`workflow_draft_id`、`base_revision`、`base_version_id`、`operation`、`proposed_by`、`actor_type`、`actor_id`
- apply 只修改 WorkflowDraft.draft，不修改 WorkflowVersion.snapshot
- apply 成功后记录 `applied_revision` 与 `resulting_draft_revision`
- controlled operation payload schemas
- resulting draft validation 与 invalid rollback
- agent propose/diff allowed，agent apply denied
- redacted diff summary、risk_flags、requires_approval
- live EventBridge events：`workflow.patch.proposed`、`workflow.patch.applied`、`workflow.patch.rejected`

## Verification

Focused I 测试入口：

```text
tests/test_v3_6_workflow_patch.py
```

当前 focused regression：

```text
./.venv/bin/python -m pytest tests/test_v3_6_*.py -q
71 passed
```

V3.5 / full / SDK regression：

```text
./.venv/bin/python -m pytest tests/test_v3_5_*.py -q
144 passed

./.venv/bin/python -m pytest -q
421 passed, 3 skipped

cd sdk/typescript && npm test
23 passed

drawio XML validation
passed
```

该测试覆盖：

- propose creates patch record
- diff stable redacted summary
- apply only changes draft
- published version immutable
- publish after apply creates new version
- reject prevents apply
- repeated apply/reject behavior
- concurrent apply single mutation
- stale draft revision conflict
- archived template patch denied
- unsupported / invalid operation denied
- operation payload schema validation
- UI-only / token / raw trace / raw connector / raw artifact content rejected
- agent propose/diff allowed
- agent apply denied even with capability
- scope isolation
- capability denied
- workflow_patch EventBridge SSE schema
- no runtime mutation creep
- no SDK default exposure

## No False Green

V3.6-I 完成后只能声明：

```text
V3.6-I complete: Safe workflow patch contract ready.
```

仍不能声明：

```text
dummy pipeline E2E ready
V3.6 complete
V4.0 ready
Workflow Studio ready
AgentTalkWindow ready
production workflow automation ready
```
