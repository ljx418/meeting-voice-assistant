# V2.16 Phase 78 验收审计报告：Runtime Profile Manager

## 1. 审计结论

结论：Phase 78 通过。

本阶段在 V2.13 allowlisted runtime command 之上增加 Runtime Profile Manager。系统现在要求通过 profile_id 运行受控 profile，未知 profile 会被 blocked，不开放任意命令执行。

## 2. 已实现能力

- 生成 `runtime_profiles/profiles.json`。
- 每个 profile 绑定已验收 allowlisted command。
- profile policy 明确 `default=deny`、`requires_profile_id=true`、`writes_source=false`、`network=disabled_by_policy`。
- profile run 委托 V2.13 allowlisted runtime，并生成 V2.16 profile run artifact。
- 未注册 profile 返回 `RUNTIME_PROFILE_NOT_REGISTERED`。
- HTTP / MCP / CLI 三端 build/read/run/result。

## 3. 自动化验收结果

### 3.1 Focused + regression tests

命令：

```text
PYTHONPATH=backend pytest backend/tests/test_v2_16_provider_registry.py backend/tests/test_v2_16_semantic_orchestrator.py backend/tests/test_v2_16_runtime_profiles.py backend/tests/test_v2_11_coding_agent_actionability.py backend/tests/test_v2_12_safe_patch_planning.py backend/tests/test_v2_13_15_coding_agent_remaining.py backend/tests/test_public_surface_guard.py -q
```

结果：

```text
17 passed
```

### 3.2 真实 data_service 仓库 E2E

结果摘要：

```json
{
  "codebase_id": "codebase_data_service_real",
  "profile_count": 12,
  "blocked_status": "blocked",
  "sample_run_status": "failed",
  "artifact": "workspace/assets/codebase/codebase_data_service_real/coding_agent/v2_16/runtime_profiles/profiles.json"
}
```

说明：样例 profile 运行结果为 `failed`，系统如实记录为 failed，没有伪装成 passed，符合 Phase 78 的结果分类要求。

### 3.3 格式检查

命令：

```text
git diff --check -- .
```

结果：通过。

## 4. PRD 规格检视

| 检视项 | 结论 |
| --- | --- |
| profile registry 是否落盘 | 通过 |
| 未注册 profile 是否 blocked | 通过 |
| 是否允许任意命令执行 | 未发现 |
| 是否修改源码 | 未发现 |
| failed/timeout 是否被包装成 passed | 未发现 |
| logs 是否脱敏 | 通过 |
| HTTP/MCP/CLI parity 是否通过 | 通过 |

## 5. 剩余风险

- 当前 profile 来源于 V2.13 allowlisted commands，尚未引入更复杂的参数模板和审批 profile。这属于后续扩展，不影响 Phase 78 closure。
- 本报告不构成 V2.16 closure。

## 6. 审计意见

- Fatal findings：0
- Major findings：0
- Minor findings：0

Phase 78 可以关闭。允许进入 Phase 79 前置开发/验收/审计文档阶段。
