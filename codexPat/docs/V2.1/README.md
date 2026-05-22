# V2.1 Real Agent Integration Verification

文档状态：V2.1-A complete；V2.1-B passed；complex integrations deferred to V3.0。

V2.1 的目标是把 V2.0 已完成的 local workflow templates、`petctl`、HTTP API 和 diagnostics，先完成本地接入基线与 Codex 真实工作流验收。Claude Code hook、真实第三方产品、Windows 和 MCP 等复杂接入迁移到 V3.0。

V2.1 不新增桌宠运行时能力，不实现 MCP server，不做 USB、Windows ready、3D、照片自定义、签名发布或自动更新。

## 当前 V2.1-A 结果

V2.1-A 已执行 baseline audit 和 third-party HTTP smoke。curl / Node / Python success 示例、401、400、429、invalid sound path / URL redaction 和 invalid source id redaction 均按预期工作。

## 当前 V2.1-B 结果

真实 `codex exec` 已触发 `sourceId=codex.local` 的 `thinking`、`running`、`success`、`error`、`need_input` accepted events。证据见 `docs/V2.1/evidence/codex-smoke-2026-05-19.md`。

operator 已确认人工视觉验收通过。V2.1-B 当前可声明：

```text
V2.1-B complete: Codex local workflow integration smoke passed.
Codex local workflow integration verified for tested local Codex CLI smoke scenarios.
```

当前可以声明：

```text
V2.1-A complete: integration baseline audit and local third-party HTTP contract smoke ready.
Third-party local HTTP contract smoke passed.
V2.1-B complete: Codex local workflow integration smoke passed.
Codex local workflow integration verified for tested local Codex CLI smoke scenarios.
```

## V2.1-C 迁移到 V3.0

真实 Claude Code CLI skill runtime smoke 已触发 `sourceId=claude-code.local` 的 accepted events：

- `thinking`
- `running`
- `success`
- `error`
- `need_input`

证据见 `docs/V2.1/evidence/claude-code-smoke-2026-05-19.md`。

但当前仍有两个未完成项：

- operator 视觉验收尚未记录。
- Claude Code hook smoke 尚未通过；hook 示例已补齐 `Notification -> need_input`，但真实 `Notification` event 尚未在非交互 smoke 中触发。

这些复杂接入验证迁移到 [V3.0](../V3.0/README.md)。当前不得声明 Claude Code workflow verified，也不把它作为 V2.1-B Codex 适配声明的阻塞项。

## 当前允许声明

```text
V2.0 ready: local agent workflow integration and developer usability polish complete.
Codex and Claude Code local workflow templates ready.
V2.1-A complete: integration baseline audit and local third-party HTTP contract smoke ready.
Third-party local HTTP contract smoke passed.
V2.1-B complete: Codex local workflow integration smoke passed.
Codex local workflow integration verified for tested local Codex CLI smoke scenarios.
```

## 当前仍禁止声明

```text
Claude Code integration verified
Third-party agent integration verified
MCP ready
Windows ready
cross-platform ready
USB ready
production signed release ready
```

## 文档索引

- [V2.1 Baseline Audit](v2_1-baseline-audit.md)
- [V2.1 Acceptance Plan](v2_1-acceptance-plan.md)
- [V2.1 Current Gap Analysis](v2_1-current-gap-analysis.md)
- [Codex Real Integration Verification](codex-real-integration-verification.md)
- [Claude Code Real Integration Verification](claude-code-real-integration-verification.md)
- [Third-party Agent Contract Report](third-party-agent-contract-report.md)
- [Codex Smoke Evidence Template](evidence/codex-smoke-template.md)
- [Claude Code Smoke Evidence Template](evidence/claude-code-smoke-template.md)
- [Claude Code Smoke Evidence 2026-05-19](evidence/claude-code-smoke-2026-05-19.md)
- [V2.2 MCP Adapter Research](../V2.2/mcp-adapter-research.md)
- [V3.0 Complex Integration and Platform Migration](../V3.0/README.md)
