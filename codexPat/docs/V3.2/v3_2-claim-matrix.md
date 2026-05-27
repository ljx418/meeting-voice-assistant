# V3.2 Claim Matrix

文档状态：active draft。

## Rule

V3.2 的所有声明必须有 evidence。没有真实 smoke 或 acceptance 证据时，只能写 planned、blocked 或 research。

## Claims

| Claim | Allowed when | Evidence |
| --- | --- | --- |
| `V3.2 Phase 1 complete: integration scope and claim matrix frozen.` | V3.2 docs and claim matrix reviewed. | `docs/V3.2/v3_2-claim-matrix.md` |
| `V3.2 MCP adapter minimal smoke passed for localhost bridge routing.` | `packages/pet-mcp` check/test pass and MCP smoke passed. | `docs/V3.2/evidence/mcp-adapter-smoke-YYYY-MM-DD.md` |
| `V3.2 Claude Code hook Notification -> need_input smoke passed.` | Real Claude Code hook lifecycle evidence passed. | `docs/V3.2/evidence/claude-code-hook-smoke-YYYY-MM-DD.md` |
| `V3.2 third-party contract v3 smoke passed.` | V3 contract docs and curl/Node/Python local smoke passed. | `docs/V3.2/evidence/third-party-contract-v3-smoke-YYYY-MM-DD.md` |
| `V3.2 final acceptance passed.` | Phase evidence and regression gate passed. | `docs/V3.2/v3_2-final-acceptance-report.md` |

## Forbidden Claims

The following remain forbidden in V3.2 unless a later version creates stronger evidence and updates this matrix:

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

## Wording Guidance

- Say `MCP adapter minimal smoke passed` instead of `MCP ready`.
- Say `Claude Code hook Notification -> need_input smoke passed` instead of `Claude Code integration verified`.
- Say `third-party contract v3 smoke passed` instead of `Third-party agent integration verified`.
- Say `tested local scenarios` when a claim depends on local smoke only.
