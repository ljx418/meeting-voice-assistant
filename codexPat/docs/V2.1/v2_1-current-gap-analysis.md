# V2.1 Current Gap Analysis

文档状态：V2.1-A complete；third-party local HTTP contract smoke passed。

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

V2.1 目标是完成真实接入验证：

- Codex CLI 真实任务可触发桌宠状态。
- Claude Code skill 真实任务可触发桌宠状态。
- Claude Code hooks 示例在真实 hook 流程中可触发桌宠状态。
- third-party agent HTTP contract 可按文档接入并处理错误。

## Gap Matrix

| Gap | Current | Target | Status |
| --- | --- | --- | --- |
| Codex real smoke | 只有 instruction template。 | 真实 Codex CLI smoke 通过。 | pending |
| Claude Code skill smoke | 只有 instruction template。 | 真实 Claude Code skill smoke 通过。 | pending |
| Claude Code hook smoke | 尚无 hook example。 | `settings-hooks.example.json` 可按文档验证。 | planned |
| Third-party contract | 已新增 contract 和 curl/Node/Python 示例；success、auth、level、sound redaction、source redaction、rate-limit smoke 通过。 | 真实第三方 agent 产品集成验证仍需后续单独执行。 | smoke passed |
| MCP | 未实现。 | V2.2 预研，不进入 V2.1 实现。 | research-only |

## Allowed Claims Now

```text
V2.0 ready: local agent workflow integration and developer usability polish complete.
Codex and Claude Code local workflow templates ready.
V2.1-A complete: integration baseline audit and local third-party HTTP contract smoke ready.
Third-party local HTTP contract smoke passed.
```

## Forbidden Until Verified

```text
Codex integration verified
Claude Code integration verified
Third-party agent integration verified
MCP ready
Windows ready
cross-platform ready
USB ready
production signed release ready
```
