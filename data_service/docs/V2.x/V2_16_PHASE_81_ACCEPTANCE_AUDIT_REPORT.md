# V2.16 Phase 81 验收审计报告：Human-Gated Patch Sandbox

## 1. 审计结论

结论：Phase 81 通过。

本阶段完成 read-only patch sandbox preview。系统可以生成 preview、diff、rollback 和 approval state；未获人工审批时 apply 必须 blocked，且不会修改源码。

## 2. 已实现能力

- 生成 `patch_sandbox/previews/{preview_id}.json`。
- 生成 `patch_sandbox/diffs/{preview_id}.diff`。
- preview 标记 `mutates_source=false`。
- approval state 为 `approval_required`。
- apply without approval 返回 `PATCH_APPLY_REQUIRES_HUMAN_APPROVAL`。
- HTTP / MCP / CLI 三端 create/read/apply-blocked。

## 3. 自动化验收结果

### 3.1 Focused + regression tests

命令：

```text
PYTHONPATH=backend pytest backend/tests/test_v2_16_provider_registry.py backend/tests/test_v2_16_semantic_orchestrator.py backend/tests/test_v2_16_runtime_profiles.py backend/tests/test_v2_16_workbench_v2.py backend/tests/test_v2_16_large_project_advisor.py backend/tests/test_v2_16_patch_sandbox.py backend/tests/test_v2_11_coding_agent_actionability.py backend/tests/test_v2_12_safe_patch_planning.py backend/tests/test_v2_13_15_coding_agent_remaining.py backend/tests/test_public_surface_guard.py -q
```

结果：

```text
23 passed
```

### 3.2 真实 data_service 仓库 E2E

结果摘要：

```json
{
  "codebase_id": "codebase_data_service_real",
  "preview_id": "preview_6300c479c79458f895ba",
  "apply_status": "blocked",
  "source_hash_unchanged": true,
  "artifact": "workspace/assets/codebase/codebase_data_service_real/coding_agent/v2_16/patch_sandbox/previews/preview_6300c479c79458f895ba.json"
}
```

### 3.3 格式检查

命令：

```text
git diff --check -- .
```

结果：通过。

## 4. PRD 规格检视

| 检视项 | 结论 |
| --- | --- |
| preview artifact 是否落盘 | 通过 |
| diff artifact 是否落盘 | 通过 |
| preview 是否修改源码 | 未发现 |
| apply without approval 是否 blocked | 通过 |
| apply without approval 是否修改源码 | 未发现 |
| 是否调用 git commit/push/reset/restore | 未发现 |
| rollback plan 是否存在 | 通过 |

## 5. 剩余风险

- 本阶段不实现真实 apply。真实 apply 需要单独的人类高风险审批流程和更严格 sandbox。
- 本报告不构成 V2.16 closure。

## 6. 审计意见

- Fatal findings：0
- Major findings：0
- Minor findings：0

Phase 81 可以关闭。允许进入 Phase 82 closure acceptance。
