# V2.16 Phase 76 验收审计报告：Provider Capability Registry

## 1. 审计结论

结论：Phase 76 通过。

本阶段完成 Provider Capability Registry 的 service、HTTP、MCP、CLI 和测试保护。验收范围仅限 Phase 76，不声明 Phase 77-82 已完成。

## 2. 已实现能力

- 新增 V2.16 provider capability registry 构建与读取能力。
- 输出 `capability_registry.json` 和 provider decision records。
- 明确 `python_ast` 为 mandatory baseline provider。
- 明确 tree-sitter、Jedi、LSP 在无 adapter 或未配置时为 unavailable / unsupported。
- 明确 provider health / known name 不等于 execution-ready。
- HTTP / MCP / CLI 三端提供 build/read。
- public payload 不输出 repo/workspace 绝对路径，不输出 secret/raw traceback。

## 3. 关键文件

实现：

- `backend/data_service/code_assets/coding_agent_v2_16/provider_registry.py`
- `backend/data_service/code_assets/coding_agent_v2_16/persistence.py`
- `backend/data_service/code_assets/coding_agent/service.py`
- `backend/app/api/v1/code_assets_coding_agent.py`
- `backend/data_service/mcp_code_coding_agent_tools.py`
- `backend/data_service/cli_code_coding_agent.py`

测试：

- `backend/tests/test_v2_16_provider_registry.py`
- `backend/tests/test_public_surface_guard.py`

阶段文档：

- `docs/V2.x/V2_16_PHASE_76_DEVELOPMENT_PLAN.md`
- `docs/V2.x/V2_16_PHASE_76_ACCEPTANCE_PLAN.md`
- `docs/V2.x/V2_16_PHASE_76_PRE_IMPLEMENTATION_AUDIT_REPORT.md`

## 4. 自动化验收结果

### 4.1 Focused + regression tests

命令：

```text
PYTHONPATH=backend pytest backend/tests/test_v2_16_provider_registry.py backend/tests/test_v2_11_coding_agent_actionability.py backend/tests/test_v2_12_safe_patch_planning.py backend/tests/test_v2_13_15_coding_agent_remaining.py backend/tests/test_public_surface_guard.py -q
```

结果：

```text
13 passed
```

### 4.2 真实 data_service 仓库 E2E

流程：

1. 在 `/private/tmp` 创建临时 workspace。
2. 导入当前 `data_service` 仓库为 codebase。
3. 生成真实 repo snapshot。
4. 构建 provider registry。
5. 检查 artifact 落盘、summary、available provider count、路径脱敏。

结果：

```json
{
  "codebase_id": "codebase_data_service_real",
  "provider_count": 7,
  "available_count": 3,
  "artifact": "workspace/assets/codebase/codebase_data_service_real/coding_agent/v2_16/providers/capability_registry.json"
}
```

### 4.3 格式检查

命令：

```text
git diff --check -- .
```

结果：通过。

## 5. PRD 规格检视

| 检视项 | 结论 |
| --- | --- |
| 是否只完成 Phase 76 范围 | 通过 |
| 是否将 optional provider 伪装成 accepted | 未发现 |
| 是否把 health / known name 当作 execution-ready | 未发现 |
| 是否污染 source registry | 未发现 |
| 是否改写 V2.0-V2.15 artifacts | 未发现 |
| 是否泄露绝对路径 / secret / traceback | 未发现 |
| 是否声明 full call graph / data flow / type inference | 未发现 |

## 6. 剩余风险

- tree-sitter、Jedi、LSP 仍只是 known optional provider，尚未实现执行 adapter；这是 Phase 77 或后续阶段范围。
- patch apply 仍被阻塞，需要 Phase 81 human-gated sandbox 才能进入 preview/apply 合同。
- 本报告不构成 V2.16 closure，Phase 82 前不得声明 V2.16 完整完成。

## 7. 审计意见

- Fatal findings：0
- Major findings：0
- Minor findings：0

Phase 76 可以关闭。允许进入 Phase 77 前置开发/验收/审计文档阶段。
