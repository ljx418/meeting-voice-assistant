# V2.1 Current Gap Analysis

文档状态：V2.1-A complete；V2.1-B passed；complex integrations deferred to V3.0。

## Current State

V2.0 已完成：

- macOS-first MVP。
- `petctl notify`。
- localhost HTTP API。
- diagnostics。
- safe sound feedback。
- Codex / Claude Code local workflow templates。
- shell / Node examples。
- README、ops 和分发文档。

## Target State

V2.1 目标是完成本地接入基线与 Codex 真实工作流验收：

- Codex CLI 真实任务可触发桌宠状态。
- third-party agent HTTP contract 可按文档接入并处理错误。

Claude Code skill/hook 完整验收、真实第三方产品接入、Windows smoke 和 MCP adapter decision 迁移到 V3.0。

## Gap Matrix

| Gap | Current | Target | Status |
| --- | --- | --- | --- |
| Codex real smoke | 真实 `codex exec` 已触发 `codex.local` 的 thinking/running/success/error/need_input accepted events；operator 已确认猫状态变化。 | 已通过 tested local Codex CLI smoke scenarios。 | passed |
| Claude Code skill smoke | 真实 Claude Code CLI 已触发 `claude-code.local` 的 thinking/running/success/error/need_input accepted events，但 operator visual 未收口。 | V3.0 中完成真实 Claude Code skill visual acceptance。 | deferred to V3.0 |
| Claude Code hook smoke | `settings-hooks.example.json` 已补齐默认 `Notification -> need_input`，wrapper 已落地；非交互 `claude -p` smoke 未稳定触发 `Notification` event。 | V3.0 中完成真实 hook lifecycle 注册、触发和 diagnostics 证据。 | deferred to V3.0 |
| Third-party contract | 已新增 contract 和 curl/Node/Python 示例；success、auth、level、sound redaction、source redaction、rate-limit smoke 通过。 | V3.0 中选择真实第三方 agent 产品进行接入 smoke。 | local contract passed, product verification deferred |
| MCP | 未实现。 | V3.0 中做 adapter decision；只有实现并通过 smoke 后才允许声明 MCP ready。 | deferred to V3.0 decision |

## Allowed Claims Now

```text
V2.0 ready: local agent workflow integration and developer usability polish complete.
Codex and Claude Code local workflow templates ready.
V2.1-A complete: integration baseline audit and local third-party HTTP contract smoke ready.
Third-party local HTTP contract smoke passed.
V2.1-B complete: Codex local workflow integration smoke passed.
Codex local workflow integration verified for tested local Codex CLI smoke scenarios.
```

## Forbidden Until Verified

```text
Claude Code integration verified
Third-party agent integration verified
MCP ready
Windows ready
cross-platform ready
USB ready
production signed release ready
```
