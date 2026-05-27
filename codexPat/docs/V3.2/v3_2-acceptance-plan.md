# V3.2 Acceptance Plan

文档状态：active draft；Agent Integration Readiness。

## Baseline Gate

V3.2 只能从 V3.1 final acceptance passed 开始。

必须存在：

- `docs/V3.1/v3_1-final-acceptance-report.md`：`status: passed`。
- `docs/V3.1/evidence/runtime-regression-harness-2026-05-21.md`。
- `docs/V3.1/evidence/local-app-migration-backup-2026-05-21.md`。

## Phase 1 Acceptance：Scope Freeze & Integration Claim Matrix

通过标准：

- V3.2 claim matrix 存在。
- forbidden claims 明确列出。
- 每个 allowed claim 都有对应 evidence gate。
- 文档不把 MCP、Claude Code、third-party product integration 写成 ready。

当前结果：passed。

## Phase 2 Acceptance：MCP Adapter Minimal Implementation

通过标准：

- `packages/pet-mcp` 存在。
- MCP tools 包含 `pet_notify`、`pet_list_instances`、`pet_get_capabilities`、`pet_get_state`。
- `pet_notify` 通过 localhost HTTP/Event Bridge 调用 `/api/events` 或 `/api/instances/:instanceId/events`。
- `pet_notify` 本地拒绝非法 `instanceId` 和带 `via` 的 payload。
- 工具响应不包含 token、Authorization header、raw payload、完整本地路径、config path 或 workspace path。
- `pet_list_instances` / `pet_get_state` 只返回 sanitized instance state，不返回 `position`、`workspaceLabel`、`workspaceHash`。
- MCP smoke evidence 存在。

当前结果：passed。

## Phase 3 Acceptance：Claude Code Hook Real Verification

通过标准：

- evidence 来自真实 Claude Code hook lifecycle。
- 最低路径 `Notification -> need_input` passed。
- evidence 中出现 `sourceId=claude-code.local` 或等价可审计字段。
- 不用 curl mock 或普通 shell `petctl` 冒充。
- 不打印 token、Authorization header、raw payload、本地路径。

如果没有真实 Claude Code hook 环境，本阶段必须标记 `blocked`，不能标记 `passed`。

当前结果：deferred；未声明 Claude Code hook smoke passed。

## Phase 4 Acceptance：Third-party Agent Contract v3 Refresh

通过标准：

- `docs/reference/third-party-agent-contract.md` 覆盖 V3 multi-instance。
- 文档区分 legacy default `/api/events` 和 instance route。
- 文档包含 `petctl attach`、`petctl list`、`petctl notify --instance`、`AGENT_DESKTOP_PET_INSTANCE_ID`。
- 错误码覆盖 `instance_not_found`、`instance_id_invalid`、`instance_limit_reached`、rate limit 和 redaction。
- curl / Node / Python examples 继续作为 local contract smoke，不声明真实第三方产品集成。

当前结果：passed。

## Phase 5 Acceptance：Security & Regression Final Acceptance

通过标准：

- V3.1 runtime smoke 复跑通过或记录环境阻塞。
- pet-protocol、petctl、pet-mcp、desktop TypeScript checks 通过。
- pet-protocol、petctl、pet-mcp tests 通过。
- Rust `cargo check` 通过。
- desktop build 和 Tauri `.app` build 通过。
- final acceptance report 记录每个命令的真实结果。
- final report 不写 forbidden claims。

当前结果：passed。

## No False-Green

V3.2 不得声明：

```text
MCP ready
Claude Code integration verified
Third-party agent integration verified
Windows ready
cross-platform ready
USB ready
production signed release ready
all Codex workflows verified
OS-level Codex window binding ready
per-instance queue ready
```
