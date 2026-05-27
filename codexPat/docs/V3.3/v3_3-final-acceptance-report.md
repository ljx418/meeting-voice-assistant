# V3.3 Final Acceptance Report

status: passed

date: 2026-05-24

commit: a09eaf3d

## Scope

V3.3 final acceptance passed for scoped Codex window/session-to-pet binding.

This supersedes the earlier V3.3 Claude Code hook attempt. Claude Code adaptation is temporarily abandoned for this project stage, and no Claude Code claim is made.

## Evidence Gate

Passed:

- `docs/V3.3/v3_3-codex-window-binding-design.md`
- `scripts/v3_3_codex_window_binding_smoke.mjs`
- `docs/V3.3/evidence/codex-window-binding-smoke-2026-05-24.md`

## Codex Binding Smoke Result

Result: passed.

Command:

```bash
node scripts/v3_3_codex_window_binding_smoke.mjs
```

Observed:

- desktop health passed。
- rate limit window settled before burst smoke。
- success launch exited `0`。
- success launch created an instance。
- success launch final state was `success`。
- failure launch exited nonzero with `codex_process_failed`。
- failure launch created an instance。
- failure launch final state was `error`。
- session B did not alter session A。
- smoke instances were detached。
- security redaction scan passed。

## Automatic Checks

| Command | Result |
| --- | --- |
| `node scripts/v3_1_runtime_smoke.mjs` | passed |
| `node scripts/v3_2_mcp_adapter_smoke.mjs` | passed |
| `node scripts/v3_2_third_party_contract_smoke.mjs` | passed |
| `pnpm --filter @agent-desktop-pet/petctl check` | passed |
| `pnpm --filter @agent-desktop-pet/petctl test` | passed |
| `pnpm --filter @agent-desktop-pet/petctl build` | passed |
| `pnpm --filter @agent-desktop-pet/pet-protocol check` | passed |
| `pnpm --filter @agent-desktop-pet/pet-protocol test` | passed |
| `pnpm --filter @agent-desktop-pet/pet-mcp check` | passed |
| `pnpm --filter @agent-desktop-pet/pet-mcp test` | passed |
| `pnpm --filter desktop check` | passed |
| `cargo check --manifest-path apps/desktop/src-tauri/Cargo.toml` | passed |
| `pnpm run doctor` | passed with environmental warnings only |
| `pnpm --filter desktop build` | passed |
| `pnpm --filter desktop tauri build -b app` | passed |

Doctor warnings were network/listen environment warnings, not hard failures.

## Security Scan

Result: passed for V3.3 scoped smoke summary and evidence.

No token, Authorization header, raw payload, config path, workspace path, full local path, raw tty path, or token file content is included.

## Claim Scan

Result: passed.

Forbidden claims appear only in forbidden, non-goal, historical, or not-ready contexts.

`git status --short` was run. The worktree already contains unrelated dirty files outside this V3.3 scope; they were not changed or reverted. Generated `dist/`, `target/`, and `node_modules/` artifacts are not staged or committed by this report.

## Allowed Claim

```text
V3.3 Codex window/session-to-pet binding smoke passed for tested local macOS terminal scenarios.
```

## Forbidden Claims

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

## Final Decision

V3.3 scoped final acceptance passed.

The project now has a tested wrapper-first Codex window/session binding path. It does not have unqualified OS-level Codex window binding, all Codex workflow coverage, or Claude Code verification.
