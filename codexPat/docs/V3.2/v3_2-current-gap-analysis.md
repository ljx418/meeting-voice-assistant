# V3.2 Current vs Target Gap

文档状态：active draft；Agent Integration Readiness。

## Current State

当前已完成并验收：

- V3.1 final acceptance passed。
- 多实例 Codex 桌宠工作流、Manager polish、runtime smoke、本地迁移说明已收口。
- 当前三方 HTTP 合同仍主要来自 V2.1 `/api/events` 语境。
- MCP adapter 之前仅为 research-only，未实现 `packages/pet-mcp`。
- Claude Code hook 完整真实验证尚未通过。

## Target State

V3.2 目标：

- 外部 agent 接入能力有明确 claim matrix。
- MCP adapter 最小实现只作为 HTTP/Event Bridge adapter。
- Claude Code hook 至少完成真实 `Notification -> need_input` 验证，或者明确 blocked。
- Third-party agent contract 升级到 V3 multi-instance。
- 所有新 claim 都有 evidence，不产生 false-green。

## Gap Matrix

| Gap | Current | Target | Status |
| --- | --- | --- | --- |
| Integration claims | V3.2 claim matrix 已存在。 | V3.2 final report 统一收口。 | passed |
| MCP adapter | `packages/pet-mcp` 已实现并通过 check/test/build。 | runtime smoke passed 后才允许 scoped claim。 | passed |
| MCP routing | 工具实现已存在。 | `pet_notify` 支持 default 与 `instanceId` route，并通过 runtime smoke。 | passed |
| MCP state reads | 工具实现已存在。 | `pet_list_instances` / `pet_get_state` 返回 sanitized state，并通过 runtime smoke。 | passed |
| Claude Code hook | 不得声明 verified。 | 真实 hook lifecycle evidence 或 deferred。 | deferred |
| Third-party contract | V3 contract doc 已刷新。 | curl / Node / Python contract smoke passed。 | passed |
| Regression gate | V3.1 smoke 已存在。 | V3.2 收口时复跑 V3.1 smoke 和 checks。 | passed |

## Allowed V3.2 Claims

```text
V3.2 Phase 1 complete: integration scope and claim matrix frozen.
V3.2 MCP adapter minimal smoke passed for localhost bridge routing.
V3.2 Claude Code hook Notification -> need_input smoke passed.
V3.2 third-party contract v3 smoke passed.
```

这些声明只有对应 evidence passed 后才允许使用。

## Forbidden V3.2 Claims

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
