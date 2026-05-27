# V3.5 Development Plan

文档状态：implemented

日期：2026-05-25

## Goal

V3.5 adds Codex hook diagnostics and recovery support. It does not add new hook mappings, MCP features, third-party product integration, OS-level window binding, or production release work.

## Implementation

- Add `petctl codex doctor`.
- Report sanitized diagnostics for:
  - Codex CLI version availability.
  - `.codex/hooks.json` presence and supported schema.
  - `scripts/codex-pet-hook.mjs` presence and syntax check.
  - `AGENT_DESKTOP_PET_INSTANCE_ID` presence and validity.
  - token presence by source only.
  - desktop health reachability.
- Add `scripts/v3_5_hook_diagnostics_smoke.mjs`.

## Boundaries

- No raw hook stdin or raw payload output.
- No token, Authorization header, config path, workspace path, or full local path output.
- Missing instance env and unavailable desktop are diagnostics warnings, not hook smoke pass claims.
- Invalid instance env and missing hook config are hard failures.

## Acceptance

V3.5 passes only if:

- `petctl codex doctor` reports hook config, hook wrapper, instance env, desktop health, token, and Codex CLI diagnostics.
- diagnostics output is redacted.
- missing instance env and desktop unavailable cases are visible.
- invalid instance env and missing hook config fail safely.
- `pnpm --filter @agent-desktop-pet/petctl check` passes.
- `pnpm --filter @agent-desktop-pet/petctl test` passes.
- `node scripts/v3_5_hook_diagnostics_smoke.mjs` passes.
