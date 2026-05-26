# V4.0 Acceptance Plan

status: accepted-feasibility-review

date: 2026-05-26

## Acceptance Principle

V4.0 can pass only as a feasibility review. It cannot pass by implementing a probe, binding UX, routing prototype, or asset/productization work.

V4.0 must keep these concepts separate:

- OS-level discovery / binding candidate.
- Codex lifecycle state event source.
- route key / event ownership proof.

Window discovery is not state monitoring.

## Required Evidence Files

V4.0 requires:

- `docs/V4.x/v4_0-development-plan.md`
- `docs/V4.x/v4_0-acceptance-plan.md`
- `docs/V4.x/v4_0-prd-spec-review.md`
- `docs/V4.x/v4_0-plan-audit.md`
- `docs/V4.x/v4_0-os-binding-feasibility-review.md`

The final feasibility review file must not be created as passed while any major or critical audit issue remains open.

## End-to-end Acceptance Per Subphase

| Subphase | Acceptance Standard | Blocking Condition |
| --- | --- | --- |
| V4.0.1 Scope Freeze | V4.0 states feasibility-only and excludes implementation | any implementation task remains in V4.0 |
| V4.0.2 PRD Spec Review | PRD and V4.0 scope are aligned or deviations are accepted | major/critical mismatch remains open |
| V4.0.3 Terminal Matrix Design | Matrix fields cover every required terminal | missing required terminal or field |
| V4.0.4 Permission / Privacy Model | allowed/forbidden fields are explicit and safe | terminal text, prompt, command, paths, token, screen, clipboard, or raw payload allowed |
| V4.0.5 State Event Source Analysis | event source, route key, env injection, and ownership proof are answered | discovery is used as lifecycle evidence |
| V4.0.6 Go / No-go | scoped decision is documented | high false-green risk without user confirmation |
| V4.0.7 Final Acceptance | PRD, plan, claim, security scans pass | forbidden claim appears as ready/passed |

## Terminal Matrix Acceptance

Terminal matrix must cover:

- Terminal.app
- iTerm2
- VS Code integrated terminal
- Warp
- Ghostty

Each row must include:

| Field | Required |
| --- | --- |
| active window detection | yes |
| Codex process identification | yes |
| TTY/session identity | yes |
| event source availability | yes |
| privacy risk | yes |
| permission requirement | yes |
| verdict | yes |

## Field Redaction Acceptance

Allowed:

```text
terminal app name / bundle id
window id or redacted summary
process id
process name
Codex CLI version
TTY id redacted summary
session id redacted summary
permission granted/denied
```

Forbidden:

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
transcript_path
full /Users path
workspace path
config path
api-token.json
```

## Claim Acceptance

Only allowed V4.0 claim after acceptance:

```text
V4.0 OS-level Codex window/session binding feasibility review completed with scoped go/no-go decision.
```

Forbidden as ready / passed:

```text
OS-level Codex window binding ready
interactive Codex TUI monitoring ready
already-open Codex window auto-detection ready
all Codex workflows verified
Codex internal reasoning exact mapping ready
MCP ready
Windows ready
cross-platform ready
production signed release ready
```

## Current Acceptance Decision

status: accepted-feasibility-review

Reason:

- PRD spec mismatch around V4.x productization asset packaging has been closed.
- `docs/V4.x/v4_0-os-binding-feasibility-review.md` completed V4.0 feasibility review.
- V4.0 still cannot claim OS-level binding ready, interactive Codex TUI monitoring, already-open window auto-detection, binding UX, routing prototype, or asset/productization work.
- V4.0 allows planning V4.1 safe-field probe for Terminal.app and iTerm2 only.
- V4.0 blocks V4.3 selected-terminal routing from OS-level discovery alone unless a later phase proves event ownership.

Required before V4.1 implementation/probe can start:

- create V4.1 development plan and acceptance plan from PRD.
- confirm no major/critical PRD mismatch.
- confirm no High false-green risk.
- pass claim/security scans.
- close all V4.1 audit findings before implementation.
