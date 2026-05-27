# V3.2 Evidence Index

文档状态：active draft。

## Baseline Evidence

| Evidence | Required | Status |
| --- | --- | --- |
| `docs/V3.1/v3_1-final-acceptance-report.md` | yes | passed baseline |
| `docs/V3.1/evidence/runtime-regression-harness-2026-05-21.md` | yes | passed baseline |
| `docs/V3.1/evidence/local-app-migration-backup-2026-05-21.md` | yes | passed baseline |

## V3.2 Evidence

| Evidence | Purpose | Status |
| --- | --- | --- |
| `docs/V3.2/evidence/mcp-adapter-smoke-2026-05-23.md` | MCP adapter minimal smoke. | passed |
| `docs/V3.2/evidence/mcp-adapter-smoke-YYYY-MM-DD.md` | Template for future MCP adapter runtime smoke. | template |
| `docs/V3.2/evidence/third-party-contract-v3-smoke-2026-05-23.md` | V3 third-party contract smoke. | passed |
| `docs/V3.2/evidence/claude-code-hook-smoke-2026-05-23.md` | Real Claude Code hook lifecycle smoke. | deferred |
| `docs/V3.2/v3_2-final-acceptance-report.md` | Final V3.2 closure. | passed |

## Evidence Requirements

- Evidence files must record command, date, environment, result, and residual risk.
- Evidence must not contain token, Authorization header, raw payload, full local path, config path, or workspace path.
- Blocked real-environment checks must be marked `blocked`, not `passed`.
