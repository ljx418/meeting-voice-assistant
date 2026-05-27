# V3.x Final Acceptance Report

status: passed

date: 2026-05-26

commit: 9c9cd634

## Scope

V3.x Final consolidates V3.1 through V3.7 evidence, PRD conformance, claim boundaries, security scan, and regression checks.

This phase does not add new product capability.

## Baseline

Passed / accepted scoped baselines:

- V3.1 stabilization.
- V3.2 scoped integration closure.
- V3.3 Codex window/session binding.
- V3.4 Codex hooks mapping.
- V3.5 hook diagnostics.
- V3.7 Codex exec JSONL monitor as current recommended Codex exec monitoring strategy.

Blocked baseline:

```text
V3.6 final acceptance blocked on real PostToolUse failure evidence.
```

## PRD Conformance

Current result: passed.

- PRD matches active gap and final evidence.
- V3.6 remains historical blocked evidence and is deprecated as the active strategy.
- V3.7 remains scoped JSONL monitor, current recommended Codex exec monitoring path, and not hook-only evidence.
- `thread.started` is marker-only.
- `raw.monitor` is recorded as sanitized summary naming risk, not raw JSONL leakage.

## Regression Results

| Command | Result |
| --- | --- |
| `node scripts/v3_1_runtime_smoke.mjs` | passed |
| `node scripts/v3_2_mcp_adapter_smoke.mjs` | passed |
| `node scripts/v3_2_third_party_contract_smoke.mjs` | passed |
| `node scripts/v3_3_codex_window_binding_smoke.mjs` | passed |
| `node scripts/v3_4_codex_hook_fixture_smoke.mjs` | passed |
| V3.4 real Codex hook lifecycle evidence review | passed by existing operator evidence; helper script still blocks without a fresh manual trusted lifecycle run |
| `node scripts/v3_7_codex_exec_jsonl_monitor_smoke.mjs` | passed |
| `pnpm run doctor` | passed with warnings; no hard failure |
| `pnpm --filter @agent-desktop-pet/pet-protocol check` | passed |
| `pnpm --filter @agent-desktop-pet/pet-protocol test` | passed |
| `pnpm --filter @agent-desktop-pet/petctl check` | passed |
| `pnpm --filter @agent-desktop-pet/petctl test` | passed |
| `pnpm --filter @agent-desktop-pet/pet-mcp check` | passed |
| `pnpm --filter @agent-desktop-pet/pet-mcp test` | passed |
| `pnpm --filter desktop check` | passed |
| `cargo check --manifest-path apps/desktop/src-tauri/Cargo.toml` | passed |
| `pnpm --filter desktop build` | passed |
| `pnpm --filter desktop tauri build -b app` | passed |
| `git status --short` | passed for artifact boundary |

## Security Scan

status: passed

Must not contain:

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

Scan result: policy/example terms appear only as redaction requirements, allowlists, or documented generic path examples. No secret values, raw hook payloads, raw JSONL payloads, prompt text, tool command text, or evidence-local full user paths were accepted as leakage.

## Claim Scan

status: passed

Forbidden claims must appear only in forbidden / blocked / deferred / not-ready contexts.

Scan result: forbidden claims remain constrained to forbidden, blocked, deferred, historical, or not-ready contexts.

## V3.4 Real Hook Lifecycle Gate

status: passed by prior operator evidence

Reviewed:

- `docs/V3.4/evidence/codex-hook-real-lifecycle-smoke-2026-05-24.md`
- `docs/V3.4/v3_4-final-acceptance-report.md`

During V3.x final, `scripts/v3_4_codex_hook_real_lifecycle_smoke.mjs` was also probed. It correctly returned `blocked` without a fresh manual trusted lifecycle run, even after hook trust confirmation, because the script is designed as a no-false-green guard and cannot itself prove a live Codex lifecycle event. This does not create a new V3.4 claim; it preserves the existing operator-accepted scoped V3.4 evidence.

## Git Artifact Check

status: passed

`git status --short` was reviewed. Generated `dist/`, `target/`, and `node_modules/` artifacts are not treated as source changes for this acceptance. The working tree contains unrelated pre-existing dirty files outside this V3.x final documentation scope; they were not reverted.

## Plan Drift And False-Green Risk

overall risk: Medium

go / no-go: go for scoped V3.x closure; no-go for expanding V3.6 or claiming broader readiness.

Assessment:

- Plan drift risk: Low. V3.x Final only changed evidence, PRD conformance, claim, and active gap documents; no new capability was added.
- False-green risk: Medium. V3.4 real lifecycle helper blocks without a fresh manual lifecycle trigger, so the final report relies on prior operator evidence and records the helper result explicitly.
- Claim expansion risk: Low. V3.6 remains historical blocked evidence and V3.7 is scoped to wrapper-launched `codex exec --json`.
- Security redaction risk: Low. Scan findings are policy/example mentions, not accepted leakage.
- Regression coverage risk: Medium. Runtime and build checks passed, but V3.4 live hook lifecycle remains operator-evidence based rather than a fully automated smoke.

## Allowed Claim

Allowed because this report is `status: passed`:

```text
V3.x scoped Codex local workflow acceptance passed with documented evidence and claim boundaries.
```

## Forbidden Claims

The following remain forbidden as ready / passed claims:

```text
V3.6 selected Codex workflow hook coverage smoke passed
PostToolUse failure hook evidence passed
all Codex workflows verified
Codex internal reasoning exact mapping ready
ModelThinkingStart / ModelThinkingEnd verified
OS-level Codex window binding ready
Claude Code integration verified
MCP ready
Third-party agent integration verified
Windows ready
cross-platform ready
USB ready
production signed release ready
per-instance queue ready
```

## Final Decision

V3.x final acceptance passed for scoped Codex local workflow acceptance.

This decision preserves V3.6 as historical blocked evidence: V3.6 final acceptance remains blocked on real PostToolUse failure evidence. V3.7 is the current recommended project-owned JSONL monitor for wrapper-launched `codex exec --json` sessions and does not count as official hook lifecycle evidence.

Post-final strategy update: V3.6 hook-only monitoring is deprecated as an active strategy. V3.7 JSONL monitoring is the current recommended Codex exec monitoring path for supported wrapper-launched `codex exec --json` sessions. This does not add interactive Codex TUI coverage, OS-level window binding, or all-workflow verification.
