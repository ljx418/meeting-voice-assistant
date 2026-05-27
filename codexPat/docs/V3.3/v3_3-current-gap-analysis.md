# V3.3 Current vs Target Gap

文档状态：final；V3.3 reset gap closed for scoped Codex binding.

## Scope Reset

早期 V3.3 以 Claude Code hook `Notification -> need_input` 为目标，但真实 hook lifecycle 未产生 accepted `need_input` evidence。

2026-05-24 后，V3.3 目标改为 Codex window/session-to-pet binding。本项目暂时放弃 Claude Code 适配要求。旧 Claude evidence 只作为 historical / superseded blocker 记录。

## Gap Matrix

| Area | Previous state | V3.3 target | Current result |
| --- | --- | --- | --- |
| Codex session attach | `petctl attach codex` 手动 attach | wrapper 自动 attach + env binding | closed |
| Per-window routing | 手动复制 `instanceId` 或 shell env | `petctl codex launch` 注入 env | closed |
| Lifecycle state | 需要手动 notify | wrapper maps child running/success/error | closed |
| Session explicit state | `petctl notify --instance` | session内 notify 默认用 env instance | closed |
| OS-level inference | not ready | out of scope | deferred |
| Claude Code hook | failed in earlier V3.3 | abandoned for now | historical / superseded |

## Remaining Gaps

- V3.3 不从 macOS 窗口内容自动推断 Codex 是否“正在思考”。精细状态仍需 Codex 会话内显式发事件。
- V3.3 不证明所有 Codex workflows。
- V3.3 不证明无 wrapper 的任意 OS-level Codex window binding。
- V3.3 不恢复 Claude Code hook 验证。

## Evidence

- `scripts/v3_3_codex_window_binding_smoke.mjs`
- `docs/V3.3/evidence/codex-window-binding-smoke-2026-05-24.md`
- `docs/V3.3/v3_3-final-acceptance-report.md`

## Claim Boundary

Allowed:

```text
V3.3 Codex window/session-to-pet binding smoke passed for tested local macOS terminal scenarios.
```

Forbidden as ready:

```text
OS-level Codex window binding ready
all Codex workflows verified
Claude Code integration verified
Claude Code all workflows verified
MCP ready
Third-party agent integration verified
Windows ready
cross-platform ready
USB ready
production signed release ready
per-instance queue ready
```
