# V4.0 Development Plan

status: go-for-v4-0-feasibility-review-only

date: 2026-05-26

## Scope

V4.0 is a strict feasibility review for OS-level Codex window/session binding.

V4.0 does not implement:

- active window probe.
- user-confirmed binding UX.
- selected-terminal routing.
- interactive Codex TUI monitoring.
- renderer, asset, packaging, or productization work.

V4.0 must decide whether V4.1-V4.3 can safely start, and under which terminal / macOS / Codex version limits.

## Source Of Truth

V4.0 must be checked against:

- `docs/active/agent_desktop_pet_prd_v3x.md`
- `docs/V4.x/v4_x-development-plan.md`
- `docs/V4.x/v4_x-acceptance-plan.md`
- `docs/V4.x/v4_x-current-gap-analysis.md`
- `docs/V4.x/v4_x-claim-matrix.md`
- `docs/active/development-plan.md`
- `docs/active/acceptance-plan.md`
- `docs/active/current-vs-target-gap.md`
- `docs/active/current-vs-target-gap.drawio`

## Subphase Plan

| Subphase | Goal | Output | End-to-end Acceptance | PRD Review |
| --- | --- | --- | --- | --- |
| V4.0.1 Scope Freeze | Freeze V4.0 as feasibility-only | scope boundary section in feasibility report | no implementation tasks included | PRD does not require V4.0 implementation |
| V4.0.2 PRD Spec Review | Compare V4.0 plan with PRD | `v4_0-prd-spec-review.md` | deviations classified as none/minor/major/critical | major/critical blocks execution |
| V4.0.3 Terminal Matrix Design | Define matrix for Terminal.app, iTerm2, VS Code terminal, Warp, Ghostty | matrix template and required fields | every terminal has all required fields | matrix covers product user scenario |
| V4.0.4 Permission / Privacy Model | Define permission and field boundaries | permission/privacy sections | allowed/forbidden fields match claim matrix | no PRD privacy regression |
| V4.0.5 State Event Source Analysis | Separate discovery from lifecycle events | event source analysis | answers route key, env injection, event ownership | no TUI monitoring false-green |
| V4.0.6 Go / No-go | Decide whether V4.1 may start | go/no-go section | high risk or open major issue stops | PRD and plan are aligned |
| V4.0.7 Final Feasibility Acceptance | Close V4.0 evidence | `v4_0-os-binding-feasibility-review.md` | claim/security scans pass | no major PRD drift remains |

## Stop Rules

Stop and ask for confirmation if any subphase finds:

- critical or major PRD mismatch.
- high false-green risk.
- evidence that window discovery is being treated as state monitoring.
- reliance on terminal text, prompt text, command text, `transcript_path`, workspace path, config path, or full local paths.
- unclear event source for an already-running Codex session.
- inability to prove event ownership for a bound session.

## Required V4.0 Questions

V4.0 must answer:

- Where do state events come from for already-running Codex sessions?
- Is there a safe `session_id`, TTY identity, hook registry, or route key?
- Can `AGENT_DESKTOP_PET_INSTANCE_ID` be injected into an already-running session?
- If not, must the product prompt the user to relaunch through V3.7?
- How can future events prove they belong to the bound session?
- Which terminal / Codex / macOS combinations are unsupported or no-go?

## Current Gate Result

Current gate result: go for V4.0 feasibility review only.

Reason:

- PRD section 13.6 has been revised so asset, renderer, packaging, license / attribution, release artifact asset integrity, and productization work are V5.x or later productization work.
- V4.x planning now consistently excludes bundled assets, renderer, and productization assets from V4.0-V4.3 gates.
- No major PRD mismatch remains for starting V4.0 feasibility review.

No V4.1 probe, V4.2 binding UX, or V4.3 routing work may start until V4.0 feasibility review is completed and accepted.
