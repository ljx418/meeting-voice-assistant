# V4.1 Development Plan

status: planned-audit-ready

date: 2026-05-26

## Scope

V4.1 plans a macOS active window safe-field probe for Terminal.app and iTerm2 only.

V4.1 does not implement:

- user-confirmed binding UX.
- selected-terminal routing.
- Codex lifecycle state monitoring.
- PetEvent emission.
- `PetInstance` creation or mutation.
- desktop UI integration.
- VS Code terminal, Warp, or Ghostty support.

V4.1 must remain a probe. A probe result is a candidate identity summary, not a binding and not lifecycle evidence.

## Proposed CLI Shape

Future implementation should live in `petctl`, not desktop UI:

```bash
petctl codex probe active-window --terminal terminal --json
petctl codex probe active-window --terminal iterm2 --json
```

The command must be read-only and must not call `notify`, `attach`, `detach`, or any HTTP Event Bridge write endpoint.

## Allowed Output Fields

The JSON output may include only:

```text
ok
terminalAppName
terminalBundleId
windowSummary
processId
processName
codexCliVersion
ttySummary
sessionSummary
permissionState
verdict
reasonCode
```

`windowSummary`, `ttySummary`, and `sessionSummary` must be redacted summaries. They must not contain terminal text, local paths, workspace names, prompts, commands, or raw OS output.

## Forbidden Data

V4.1 must not collect, store, print, or include in evidence:

```text
terminal text
prompt text
tool command text
shell history
screen contents
clipboard contents
token
Authorization
raw payload
raw OS probe output
transcript_path
full /Users path
workspace path
config path
api-token.json
```

## Subphase Plan

| Subphase | Goal | Output | Stop Condition |
| --- | --- | --- | --- |
| V4.1.1 Scope Freeze | Freeze Terminal.app/iTerm2 probe-only scope | scope section | any binding/routing/event work appears |
| V4.1.2 PRD Review | Compare V4.1 with PRD and V4.0 | `v4_1-prd-spec-review.md` | major/critical mismatch |
| V4.1.3 Probe Interface Design | Define CLI and output fields | command/output section | output includes forbidden fields |
| V4.1.4 Permission Design | Define permission denied/unavailable behavior | permission section | broad permission request without safe fields |
| V4.1.5 Acceptance Design | Define future smoke and manual checks | `v4_1-acceptance-plan.md` | probe evidence could be mistaken for binding |
| V4.1.6 Plan Audit | Close audit findings | `v4_1-plan-audit.md` | High false-green risk |

## Required Decisions Before Implementation

Before implementation starts, V4.1 must have:

- no critical or major PRD mismatch.
- no High false-green risk.
- accepted CLI command shape.
- accepted redaction boundary.
- accepted terminal-by-terminal scope.
- accepted failure behavior for permission denied, terminal unavailable, Codex process not found, and unsupported terminal.

## Current Decision

go / no-go: go for V4.1 planning only.

No implementation may start until `v4_1-plan-audit.md` closes all critical / major findings and confirms no High false-green risk.
