# V2 Phase 0 Audit Report: Preparation and Audit Closure

## Summary

Phase 0 已完成只读审计。V2 文档输入和主要接入点已确认存在，但当前工作区存在多处既有业务/测试变更。该风险需要在进入 PR1 前闭环，否则存在混入无关改动和虚假验收风险。

## Evidence

### V2 文档输入

已确认存在：

- `docs/V2.x/V2_PROJECT_BASELINE.md`
- `docs/V2.x/V2_PROJECT_INTELLIGENCE_PRD.md`
- `docs/V2.x/V2_PROJECT_INTELLIGENCE_DEVELOPMENT_ACCEPTANCE_PLAN.md`
- `docs/V2.x/V2_PROJECT_INTELLIGENCE_REMAINING_GOVERNANCE_PLAN.md`

### HTTP 接入点

`backend/app/api/__init__.py` 使用 `api_router.include_router(...)` 注册 target router 与 v1 router。PR1 可新增独立 `code_assets.py` router，并在 bootstrap 中注册。

### MCP 接入点

`backend/data_service/mcp_tool_registry.py` 通过 `all_tool_specs()` 聚合 MCP tool specs。PR1 可新增 `mcp_code_tools.py` 并在 registry 中追加 code tool specs。

### CLI 接入点

`backend/data_service/__main__.py` 存在 `knowledge` parser 和多个 command group。PR1 可新增 `knowledge code import`，但应尽量拆出 helper，避免继续扩大 CLI 主文件。

## Audit Findings

| Severity | Finding | Impact | Required Closure |
|---|---|---|---|
| major | 当前工作区存在多处既有业务/测试变更，包括 `backend/app/api/v1/data_service.py` 和多个 `backend/tests/*`。 | PR1 开发可能混入无关改动，真实验收结果难以归因。 | 进入 PR1 前必须隔离：提交/暂存既有变更，或明确 PR1 只允许改 V2 文件和注册点，并在最终 diff 中逐项证明。 |
| major | 多个 V2 文档当前为未跟踪文件。 | 后续阶段可能基于未纳入版本控制的计划执行，导致审计输入不可追踪。 | 进入 PR1 前应将 V2 文档纳入版本控制，或用户明确允许在未提交状态下继续。 |
| minor | CLI 当前集中在 `backend/data_service/__main__.py`，后续新增 `knowledge code ...` 可能继续扩大文件。 | 可维护性风险。 | PR1 应优先新增 `cli_code.py` helper，只在 `__main__.py` 做最小注册。 |
| note | PR1 不需要修改 `backend/app/api/v1/data_service.py` 或 `backend/data_service/service.py`。 | 符合 V2 架构边界。 | 开发阶段必须保持该边界。 |

## PRD Spec Review

PRD 要求 codebase asset 独立于 source registry、支持 MCP/HTTP 导入、返回 codebase_id、记录 metadata，并避免把代码仓库当普通 source 混入 source registry。Phase 0 结论：PR1 范围与 PRD 一致。

PRD 同时要求 V2 不继续扩大旧大文件。Phase 0 结论：PR1 可通过新增独立 router、MCP module、code_assets package 实现，不需要扩大旧 HTTP 大文件或 `DataService`。

## False Acceptance Risk Review

当前最大虚假验收风险来自 dirty worktree：如果不隔离既有改动，PR1 失败或通过都可能被 unrelated changes 影响。该风险标记为 `major`。

PR1 真实数据验收必须使用当前 repo 路径导入 codebase，并检查 source registry 未变化。只跑单元测试或 mock import 不足以通过验收。

## Decision

当前不建议直接进入 PR1 实质开发。需要先闭环两个 `major` 审计意见：

1. 隔离当前既有业务/测试变更，或明确采用路径级变更控制并在每轮 diff 中证明。
2. 将 V2 文档纳入版本控制，或由用户确认可在未跟踪文档状态下继续。

在上述意见闭环前，Phase 0 未通过，PR1 不应开始。

## Closure Attempt

2026-05-30 更新：用户确认本项目可在受控情况下推送到远端 git 仓库。Phase 0 采用以下闭环策略：

- 对 V2 文档执行单独 stage / commit / push，只纳入 `docs/V2.x/V2_*.md`，不纳入任何业务代码或测试变更。
- 对当前既有业务/测试变更采用路径级隔离策略：PR1 只允许修改 V2 新增模块与最小注册点，后续每轮提交前必须用 path-limited `git status` 和 staged diff 证明未混入 unrelated changes。

如果上述提交和推送成功，则第二个 `major` 问题闭环；第一个 `major` 问题降级为 PR1 阶段持续门禁，要求每轮开发都做路径级 diff 审计。

## Closure Result

2026-05-30 受控提交和推送已完成：

- Commit：`2d9f593a docs: add V2 project intelligence planning`
- Remote：`origin/main`
- 范围：仅包含 7 份 `data_service/docs/V2.x/V2_*.md` 文档。

审计结论更新：

- V2 文档未跟踪问题已闭环。
- 既有业务/测试变更未被提交，保持隔离。
- 既有工作区变更风险降级为 PR1 持续门禁：PR1 每次提交前必须证明 staged diff 只包含 V2 新增模块、最小注册点和对应测试。
- Phase 0 可判定通过；允许进入 PR1 实质开发，但不得越过 PR1 范围。
