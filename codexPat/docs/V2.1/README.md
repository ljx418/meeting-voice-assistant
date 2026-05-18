# V2.1 Real Agent Integration Verification

文档状态：V2.1-A complete；third-party local HTTP contract smoke passed。

V2.1 的目标是把 V2.0 已完成的 local workflow templates、`petctl`、HTTP API 和 diagnostics，从“可复制模板”升级为“真实 Agent 工作流可安装、可触发、可验收、可声明”。

V2.1 不新增桌宠运行时能力，不实现 MCP server，不做 USB、Windows ready、3D、照片自定义、签名发布或自动更新。

## 当前 V2.1-A 结果

V2.1-A 已执行 baseline audit 和 third-party HTTP smoke。curl / Node / Python success 示例、401、400、429、invalid sound path / URL redaction 和 invalid source id redaction 均按预期工作。

当前可以声明：

```text
V2.1-A complete: integration baseline audit and local third-party HTTP contract smoke ready.
Third-party local HTTP contract smoke passed.
```

## 当前允许声明

```text
V2.0 ready: local agent workflow integration and developer usability polish complete.
Codex and Claude Code local workflow templates ready.
V2.1-A complete: integration baseline audit and local third-party HTTP contract smoke ready.
Third-party local HTTP contract smoke passed.
```

## 当前仍禁止声明

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

## 文档索引

- [V2.1 Baseline Audit](v2_1-baseline-audit.md)
- [V2.1 Acceptance Plan](v2_1-acceptance-plan.md)
- [V2.1 Current Gap Analysis](v2_1-current-gap-analysis.md)
- [Codex Real Integration Verification](codex-real-integration-verification.md)
- [Claude Code Real Integration Verification](claude-code-real-integration-verification.md)
- [Third-party Agent Contract Report](third-party-agent-contract-report.md)
- [Codex Smoke Evidence Template](evidence/codex-smoke-template.md)
- [Claude Code Smoke Evidence Template](evidence/claude-code-smoke-template.md)
- [V2.2 MCP Adapter Research](../V2.2/mcp-adapter-research.md)
