# V2.20 Phase 86 MCP Tool Discovery & Workflow Guide Acceptance Plan

## 1. 验收门槛

- Catalog tool count 必须等于当前 `len(all_tool_specs())`。
- 每个 tool 必须有 group。
- 每个 tool 必须列出 required / optional inputs。
- Workflow guides 至少包含 project_reading、coding_task_preparation、architecture_review。
- Workflow guide 中所有 tools 必须存在于 catalog。
- HTTP/MCP/CLI 三端读取 stable fields 一致。
- 真实 data_service E2E 通过。
- public payload 不泄露绝对路径。

## 2. 自动化测试

新增测试：

```text
backend/tests/test_v2_20_tool_catalog.py
```

覆盖：

- service build/read。
- count == `len(all_tool_specs())`。
- workflow guide tool refs 完整性。
- HTTP/MCP/CLI parity。
- no fake missing tool。

## 3. 回归命令

```text
PYTHONPATH=backend python3 -m pytest backend/tests/test_v2_20_tool_catalog.py -q
PYTHONPATH=backend python3 -m pytest backend/tests/test_v2_19_artifact_contracts.py -q
PYTHONPATH=backend python3 -m pytest backend/tests/test_public_surface_guard.py -q
cd frontend && npm run build
PYTHONPATH=backend python3 -m pytest backend/tests -q
git diff --check -- .
```

## 4. False-Green 拒绝项

- tool count 小于 registry count 仍算通过。
- workflow guide 推荐不存在 tool。
- 空 preconditions/outputs 全部伪造通过。
- HTTP 通过但 MCP/CLI 未测。
- public output 泄露路径。
