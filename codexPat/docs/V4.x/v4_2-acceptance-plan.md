# V4.2 Acceptance Plan

status: planned-audit-ready

date: 2026-05-26

## Acceptance Principle

V4.2 can only pass as a Terminal.app-only user-confirmed binding UX. It cannot pass by proving lifecycle monitoring, routing, auto-detection readiness, or all-terminal support.

## Required Commands

```bash
petctl codex bind active-window --terminal terminal --preview --json
petctl codex bind confirm --candidate <candidateId> --name "<cat name>" --json
```

## Required Cases

| Case | Expected Result |
| --- | --- |
| preview with focused Terminal.app Codex TUI | returns sanitized candidate with `bindingStatus=candidate` and no binding |
| preview with non-Terminal.app focused app | fails safely with `unsupported_terminal` |
| preview with Terminal.app but no Codex process | fails safely with `codex_process_not_found` |
| confirm with valid candidate | creates/links PetInstance and stores binding |
| confirm with expired candidate | fails with `candidate_expired` |
| confirm after terminal/Codex candidate is inactive | fails with `candidate_not_active` |
| confirm missing name | uses safe default display name |
| confirm invalid name | fails with `display_name_invalid` |
| output/evidence scan | no forbidden fields |

## Non-negotiable Gates

- `preview` must not create binding.
- `confirm` must create binding only after explicit candidate id.
- V4.2 must not send PetEvent.
- V4.2 must not call `/api/events` or `/api/instances/:id/events`.
- V4.2 must not route state to any pet.
- V4.2 must not claim lifecycle monitoring.

## Automatic Checks

Required:

```bash
pnpm --filter @agent-desktop-pet/petctl check
pnpm --filter @agent-desktop-pet/petctl test
pnpm --filter @agent-desktop-pet/petctl build
```

Focused regression:

```bash
node packages/petctl/dist/cli.js codex bind active-window --terminal terminal --preview --json
node packages/petctl/dist/cli.js codex bind confirm --candidate <candidateId> --name "V4.2 Cat" --json
```

Runtime acceptance may only be counted passed when the focused Terminal.app Codex TUI scenario produces a candidate and the explicit confirm produces a binding without leaking forbidden fields.

## Allowed Claim

```text
V4.2 user-confirmed Terminal.app Codex candidate-to-PetInstance binding UX passed for tested local environment.
```

## Forbidden Claims

```text
OS-level Codex window binding ready
interactive Codex TUI monitoring ready
already-open Codex window auto-detection ready
state lifecycle routing ready
lifecycle event routing from OS discovery
iTerm2 support passed
all terminal apps supported
```
