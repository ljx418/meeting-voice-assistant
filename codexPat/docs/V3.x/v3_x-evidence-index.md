# V3.x Evidence Index

status: passed

date: 2026-05-26

## Evidence Summary

| Area | Status | Evidence |
| --- | --- | --- |
| V3.1 stabilization | passed | `docs/V3.1/v3_1-final-acceptance-report.md` |
| V3.2 MCP adapter minimal bridge | passed scoped | `docs/V3.2/evidence/mcp-adapter-smoke-2026-05-23.md` |
| V3.2 third-party contract v3 | passed scoped | `docs/V3.2/evidence/third-party-contract-v3-smoke-2026-05-23.md` |
| V3.3 Codex window/session binding | passed scoped | `docs/V3.3/evidence/codex-window-binding-smoke-2026-05-24.md` |
| V3.4 hook fixture | passed | `docs/V3.4/evidence/codex-hook-fixture-smoke-2026-05-24.md` |
| V3.4 real hook lifecycle | passed scoped | `docs/V3.4/evidence/codex-hook-real-lifecycle-smoke-2026-05-24.md` |
| V3.5 hook diagnostics | passed scoped | `docs/V3.5/evidence/hook-diagnostics-smoke-2026-05-25.md` |
| V3.6 hook-only real workflow coverage | historical blocked / deprecated active strategy | `docs/V3.6/v3_6-final-acceptance-report.md` |
| V3.7 Codex exec JSONL monitor | passed scoped / current Codex exec monitoring strategy | `docs/V3.7/evidence/codex-exec-jsonl-monitor-smoke-2026-05-25.md` |
| V3.7 current gap | passed | `docs/V3.7/v3_7-current-gap-analysis.md` |
| V3.x Codex monitoring strategy | active | `docs/V3.x/v3_x-codex-monitoring-strategy.md` |
| V3.x final acceptance | passed scoped | `docs/V3.x/v3_x-final-acceptance-report.md` |

## Runtime Smoke Commands

Executed for V3.x Final:

```bash
node scripts/v3_1_runtime_smoke.mjs
node scripts/v3_2_mcp_adapter_smoke.mjs
node scripts/v3_2_third_party_contract_smoke.mjs
node scripts/v3_3_codex_window_binding_smoke.mjs
node scripts/v3_4_codex_hook_fixture_smoke.mjs
node scripts/v3_7_codex_exec_jsonl_monitor_smoke.mjs
```

## Security Evidence Boundary

Evidence must not record:

```text
token
Authorization
raw payload
raw JSONL payload
prompt text
tool command text
transcript_path
full /Users path
workspace path
config path
api-token.json
```

## Claim Boundary

V3.x Final may include V3.7 scoped JSONL monitor evidence as the current Codex exec monitoring strategy, but it must not convert V3.6 into passed.

Allowed final claim:

```text
V3.x scoped Codex local workflow acceptance passed with documented evidence and claim boundaries.
```
