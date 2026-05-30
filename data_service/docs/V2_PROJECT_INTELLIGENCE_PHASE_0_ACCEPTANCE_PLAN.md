# V2 Phase 0 Acceptance Plan: Preparation and Audit Closure

## Summary

Phase 0 验收只验证开发前置条件，不验证 V2 业务能力。验收目标是判断是否可以安全进入 PR1 实质开发。

## Real Data Scope

真实数据样例为当前仓库：

```text
/Users/Zhuanz/Desktop/workspace/data_service
```

必须用当前真实 repo 验证以下事实：

- V2 baseline、PRD、development/acceptance plan 已存在。
- HTTP router bootstrap 存在并可新增独立 router。
- MCP tool registry 存在并可新增 V2 code tools。
- CLI parser 存在并可新增 `knowledge code ...` group。
- 当前 repo 有 backend、frontend、docs、tests，可作为 PR1-PR7 自举样例。

## Acceptance Checks

### Check 1：V2 文档输入存在

命令：

```bash
test -f docs/V2_PROJECT_BASELINE.md
test -f docs/V2_PROJECT_INTELLIGENCE_PRD.md
test -f docs/V2_PROJECT_INTELLIGENCE_DEVELOPMENT_ACCEPTANCE_PLAN.md
test -f docs/V2_PROJECT_INTELLIGENCE_REMAINING_GOVERNANCE_PLAN.md
```

通过标准：四份文档均存在。

### Check 2：架构接入点存在

命令：

```bash
sed -n '1,120p' backend/app/api/__init__.py
sed -n '1,180p' backend/data_service/mcp_tool_registry.py
rg "def _build_knowledge_parser|subparsers" backend/data_service/__main__.py
```

通过标准：

- HTTP API bootstrap 使用 `api_router.include_router(...)`。
- MCP tool registry 通过 `all_tool_specs()` 聚合 tool specs。
- CLI 存在 `knowledge` parser，可新增 `code` command group。

### Check 3：工作区风险识别

命令：

```bash
git status --short -- docs/V2_PROJECT_BASELINE.md docs/V2_PROJECT_INTELLIGENCE_PRD.md docs/V2_PROJECT_INTELLIGENCE_DEVELOPMENT_ACCEPTANCE_PLAN.md backend/app/api/v1/data_service.py backend/data_service backend/tests
```

通过标准：

- 已识别所有影响 PR1 的既有变更。
- 若存在 unrelated business/test changes，必须在审计报告中标记并给出闭环策略。

### Check 4：PR1 文件边界确认

通过标准：

- PR1 不需要修改 `backend/app/api/v1/data_service.py`。
- PR1 不需要修改 `backend/data_service/service.py`。
- PR1 只需新增 V2 模块并修改最小注册点。

## Failure Handling

以下任一项失败时，不得进入 PR1：

- V2 文档缺失。
- HTTP/MCP/CLI 接入点无法确认。
- 当前工作区存在无法隔离的冲突。
- PR1 必须修改 V1 大文件才能实现。

