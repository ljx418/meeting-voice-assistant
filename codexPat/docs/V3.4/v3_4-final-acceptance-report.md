# V3.4 Final Acceptance Report

status: passed

date: 2026-05-25

commit: 9c9cd634

## Scope

V3.4 implements Codex hook wrapper and fixture mapping, then verifies real Codex hook lifecycle state sync to the desktop pet through operator acceptance.

## Current Decision

V3.4 final acceptance passed for tested local Codex hook state mapping scenarios.

Reason:

- Hook wrapper implementation is present.
- Fixture smoke passed.
- `.codex/hooks.json` schema was fixed to the Codex 0.131 matcher group shape.
- Operator completed `/hooks` review/trust.
- Operator confirmed Codex currently syncs status to the desktop pet.

## Evidence Results

| Evidence | Result |
| --- | --- |
| `scripts/v3_4_codex_hook_fixture_smoke.mjs` | passed |
| `scripts/v3_4_codex_hook_real_lifecycle_smoke.mjs` | passed by operator acceptance |
| `docs/V3.4/evidence/codex-hook-redaction-scan-2026-05-24.md` | passed for fixture smoke |

## Automatic Checks

| Command | Result |
| --- | --- |
| `pnpm --filter @agent-desktop-pet/petctl build` | passed |
| `node --check scripts/codex-pet-hook.mjs` | passed |
| `node --check scripts/v3_4_codex_hook_fixture_smoke.mjs` | passed |
| `node --check scripts/v3_4_codex_hook_real_lifecycle_smoke.mjs` | passed |
| `pnpm --filter @agent-desktop-pet/petctl check` | passed |
| `pnpm --filter @agent-desktop-pet/petctl test` | passed |
| `.codex/hooks.json` parse check | passed |
| `node scripts/v3_3_codex_window_binding_smoke.mjs` | passed |

## Real Lifecycle Result

Passed.

Confirmed:

- hooks installed after `.codex/hooks.json` schema fix.
- hooks trusted through `/hooks`.
- bound Codex session routes through `AGENT_DESKTOP_PET_INSTANCE_ID`.
- Codex state syncs to the desktop pet.

## Allowed Claim

The following claims are allowed:

```text
V3.4 Codex hook wrapper fixture smoke passed.
V3.4 Codex hooks state mapping smoke passed for tested local Codex hook scenarios.
```

## Forbidden Claims

```text
Codex internal reasoning exact mapping ready
ModelThinkingStart / ModelThinkingEnd verified
OS-level Codex window binding ready
all Codex workflows verified
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

V3.4 final acceptance passed for scoped Codex Hooks State Mapping.

This does not claim Codex internal reasoning exact mapping, ModelThinkingStart / ModelThinkingEnd, OS-level Codex window binding, or all Codex workflows verified.
