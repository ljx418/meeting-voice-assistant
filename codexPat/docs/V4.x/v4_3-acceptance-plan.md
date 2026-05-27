# V4.3 Acceptance Plan

status: planned-audit-ready

date: 2026-05-27

## Acceptance Principle

V4.3 can only pass as a manual route-test prototype for a validated Terminal.app binding. It cannot pass as lifecycle routing, interactive TUI monitoring, or OS-level binding readiness.

## Required Command

```bash
petctl codex route test --binding <bindingId> --level running --json
```

## Required Cases

| Case | Expected Result |
| --- | --- |
| valid active binding | sends one manual test event to bound PetInstance |
| default pet | unchanged |
| other Codex pets | unchanged |
| unknown binding | `binding_not_found` |
| stale/expired binding | `binding_stale` |
| inactive candidate process | `candidate_not_active` |
| terminal mismatch | `terminal_mismatch` |
| missing PetInstance | `pet_instance_not_found` |
| output/evidence scan | no forbidden fields |

## Non-negotiable Gates

- Route-test must revalidate binding before delivery.
- Route-test must never fall back to default.
- Route-test must use `/api/instances/:instanceId/events`, not `/api/events`.
- Route-test must mark metadata as manual route-test, not lifecycle evidence.
- Route-test must not parse terminal text, prompt text, command text, or screen contents.

## Automatic Checks

Required:

```bash
pnpm --filter @agent-desktop-pet/petctl check
pnpm --filter @agent-desktop-pet/petctl test
pnpm --filter @agent-desktop-pet/petctl build
```

Runtime acceptance:

```bash
node packages/petctl/dist/cli.js codex route test --binding <bindingId> --level running --json
node packages/petctl/dist/cli.js list --json
```

The `list` result must show only the bound PetInstance changed to the manual test level. Default and unrelated Codex pets must remain unchanged.

## Allowed Claim

```text
V4.3 user-confirmed Terminal.app binding manual route-test prototype passed for tested local environment.
```

## Forbidden Claims

```text
interactive Codex TUI monitoring ready
state lifecycle routing ready
OS-level Codex window binding ready
already-open Codex window auto-detection ready
all Codex workflows verified
```
