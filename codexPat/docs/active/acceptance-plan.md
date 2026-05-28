# Active Acceptance Plan

文档状态：active acceptance index；V4.x OS-level Codex binding feasibility line。  
当前日期：2026-05-28。

## Current Acceptance Status

| Phase | Status | Evidence |
| --- | --- | --- |
| V3.1 | passed | `docs/V3.1/v3_1-final-acceptance-report.md` |
| V3.2 | passed scoped | `docs/V3.2/v3_2-final-acceptance-report.md` |
| V3.3 | passed scoped | `docs/V3.3/v3_3-final-acceptance-report.md` |
| V3.4 | passed scoped | `docs/V3.4/v3_4-final-acceptance-report.md` |
| V3.5 | passed scoped | `docs/V3.5/v3_5-final-acceptance-report.md` |
| V3.6 | historical blocked / deprecated active strategy | `docs/V3.6/v3_6-final-acceptance-report.md` |
| V3.7 | passed scoped / current Codex exec monitoring strategy | `docs/V3.7/v3_7-final-acceptance-report.md` |
| V3.x Final | passed scoped / closed baseline | `docs/V3.x/v3_x-final-acceptance-report.md` |
| V4.0 | accepted feasibility review / no readiness claim | `docs/V4.x/v4_0-os-binding-feasibility-review.md` |
| V4.4 | passed scoped managed exec JSONL | `docs/V4.x/v4_4-final-acceptance-report.md` |
| V4.5 | passed scoped real TUI hook lifecycle / PermissionRequest not observed | `docs/V4.x/v4_5-final-acceptance-report.md` |
| V4.6 | passed startup diagnostics | `docs/V4.x/evidence/v4_6-startup-diagnostics-smoke-2026-05-27.md` |
| V4.7 | passed sanitized session status | `docs/V4.x/evidence/v4_7-session-status-smoke-2026-05-27.md` |
| V4.x Final | passed scoped | `docs/V4.x/v4_x-final-acceptance-report.md` |
| V5.0 | passed scoped asset system freeze | `docs/V5.x/v5_0-final-acceptance-report.md` |
| V5.1 | passed scoped bundled 2D sprite smoke | `docs/V5.x/v5_1-final-acceptance-report.md` |
| V5.2 | passed scoped renderer plugin interface | `docs/V5.x/v5_2-final-acceptance-report.md` |
| V5.3 | passed scoped bundled GLTF prototype | `docs/V5.x/v5_3-final-acceptance-report.md` |
| V5.4 | passed scoped bundled 3D action pack smoke | `docs/V5.x/v5_4-final-acceptance-report.md` |
| V5.5 | passed scoped local renderer selection smoke | `docs/V5.x/v5_5-final-acceptance-report.md` |
| V5.6 | passed scoped privacy and claim boundary | `docs/V5.x/v5_6-photo-personalization-claim-matrix.md` |
| V5.7 | passed prompt pack generator | `docs/V5.x/v5_7-prompt-pack-final-acceptance-report.md` |
| V5.8 | passed scoped local personalized import | `docs/V5.x/v5_8-local-asset-import-final-acceptance-report.md` |
| V5.9 | passed scoped CLI activation mapping | `docs/V5.x/v5_9-dynamic-action-pack-final-acceptance-report.md` |
| V5.10 | completed scoped provider feasibility | `docs/V5.x/v5_10-provider-feasibility-report.md` |
| V5.x Final | passed scoped bundled renderer / asset system and personalized CLI pipeline | `docs/V5.x/v5_personalized_asset_pipeline_final_report.md` |

## Closed V3.x Acceptance

V3.x Final passed on 2026-05-26 because:

- PRD conformance scan passed for the scoped V3.x local workflow baseline.
- V3.6 remains historical blocked / deprecated as active strategy.
- V3.7 remains scoped JSONL monitor and current Codex exec monitoring path.
- V3.4 real Codex hook lifecycle evidence remains operator-accepted, with trust/manual lifecycle requirements documented.
- required smoke and automatic checks had no hard failure.
- security scan passed.
- claim scan passed.
- git artifact check confirmed generated `dist/`, `target/`, and `node_modules/` are not staged as source changes.

Allowed closed baseline claim:

```text
V3.x scoped Codex local workflow acceptance passed with documented evidence and claim boundaries.
```

## V3.7 Regression Baseline

V3.7 remains the current accepted Codex monitoring fallback:

```text
V3.7 Codex exec JSONL monitor state mapping passed for tested local wrapper-launched codex exec --json scenarios.
```

Required evidence:

- `docs/V3.7/evidence/codex-exec-jsonl-monitor-smoke-2026-05-25.md`
- `docs/V3.7/v3_7-final-acceptance-report.md`

Required regression smoke:

```bash
node scripts/v3_7_codex_exec_jsonl_monitor_smoke.mjs
```

Unsupported by this claim:

- interactive Codex TUI monitoring.
- already-open Codex terminal window discovery.
- OS-level Codex window binding.
- official `PostToolUse failure` hook evidence.
- all Codex workflows verification.

## V4.0 Acceptance Gate

V4.0 is a strict feasibility and claim-boundary phase. It has passed as feasibility review only and does not claim readiness or implementation.

Required V4.0 evidence:

- terminal app feasibility matrix covering Terminal.app, iTerm2, VS Code integrated terminal, Warp, and Ghostty.
- permission model for Accessibility, Automation, shell integration, and any local helper process.
- privacy and redaction model for process metadata, window identifiers, TTY identifiers, session identifiers, permissions, and forbidden fields.
- safe identity field list.
- state event source analysis for already-running Codex sessions.
- analysis of whether `AGENT_DESKTOP_PET_INSTANCE_ID` can be injected into already-running sessions; if not, relaunch-through-wrapper fallback must be stated.
- event ownership proof analysis for any future selected-terminal routing.
- no-go list for unsupported terminal / Codex scenarios.
- go / no-go decision for implementation.
- claim scan proving forbidden claims are not used as ready / passed.

V4.0 explicitly does not include active window probe, explicit binding UX, selected-terminal routing, or runtime smoke.

Allowed V4.0 scoped claim:

```text
V4.0 OS-level Codex window/session binding feasibility review completed with scoped go/no-go decision.
```

V4.0 decision:

- Go for V4.1 planning for Terminal.app and iTerm2 safe-field probe only.
- No-go for V4.3 selected-terminal routing from OS-level discovery alone.
- No-go for interactive Codex TUI monitoring ready.

V4.0 may not claim:

```text
OS-level Codex window binding ready
interactive Codex TUI monitoring ready
already-open Codex window auto-detection ready
all Codex workflows verified
Codex internal reasoning exact mapping ready
```

## V4.1-V4.3 Acceptance Split

| Phase | Earliest Allowed Work | Maximum Allowed Claim |
| --- | --- | --- |
| V4.1 | active window safe-field probe prototype | `V4.1 macOS active window safe-field probe completed for <terminal app> on tested local environment.` |
| V4.2 | explicit user-confirmed binding UX | no auto-bind or monitoring claim |
| V4.3 | selected-terminal routing prototype | `V4.3 user-confirmed binding prototype passed for <terminal app>/<macOS>/<Codex version> tested local scenario.` |

V4.3 may pass only if events can be proven to belong to the user-confirmed bound session. If event ownership cannot be proven, V4.3 must be blocked.

## V4.x Final Gate

V4.x Final must not add features. It may only consolidate regression, evidence, security, artifact, and claim scans for whatever V4.x scope was actually implemented.

Required final checks:

- all V4.x scoped runtime smokes, if implementation exists.
- V3.7 regression smoke remains passing unless explicitly superseded with accepted evidence.
- no security leakage in V4.x evidence.
- no forbidden claim used as ready.
- generated `dist/`, `target/`, and `node_modules/` are not committed as source changes.

## V4.4 Managed Session Acceptance

V4.4 adds a managed user entry for state mapping:

```bash
node packages/petctl/dist/cli.js codex session start \
  --mode exec \
  --monitor jsonl \
  --name "Review Cat" \
  -- codex exec --json "task"
```

Accepted V4.4 scope:

```text
V4.4 managed Codex exec JSONL state mapping passed for tested local wrapper-launched scenario.
```

Evidence:

- `docs/V4.x/v4_4-development-plan.md`
- `docs/V4.x/v4_4-acceptance-plan.md`
- `docs/V4.x/v4_4-prd-spec-review.md`
- `docs/V4.x/v4_4-plan-audit.md`
- `docs/V4.x/evidence/v4_4-managed-exec-jsonl-smoke-2026-05-27.md`
- `docs/V4.x/evidence/v4_4-managed-tui-hooks-smoke-2026-05-27.md`
- `docs/V4.x/v4_4-final-acceptance-report.md`

Managed TUI hooks remain not-run. No interactive TUI monitoring ready claim is allowed.

## V4.5 Managed TUI Hook Acceptance

Current allowed claim:

```text
V4.5 managed Codex TUI hook state mapping passed for UserPromptSubmit, PreToolUse, and Stop in tested local wrapper-launched scenario; PermissionRequest remains blocked by local policy.
```

Required real manual acceptance:

- start `node packages/petctl/dist/cli.js codex session start --mode tui --monitor hooks --name "V4.5 TUI Cat" -- codex`.
- run `/hooks` inside Codex TUI.
- review/trust project hooks.
- submit real prompt.
- trigger tool use.
- trigger permission request if local policy allows.
- let turn stop.
- confirm target cat changes.
- confirm default and unrelated pets unchanged.

Required evidence:

- `UserPromptSubmit -> thinking`.
- `PreToolUse -> running`.
- `Stop -> success` / idle marker.
- `PermissionRequest -> need_input`, or blocked by local policy.
- no curl.
- no manual `petctl notify`.
- no fixture smoke as lifecycle evidence.
- no terminal text parsing.
- no `transcript_path`.
- no raw hook payload.
- no prompt text.
- no tool command text.

If only preflight passes, status remains `pending-manual-hook-lifecycle`. The 2026-05-27 local run passed scoped real lifecycle acceptance for `UserPromptSubmit`, `PreToolUse`, and `Stop`; `PermissionRequest` was not observed and is not claimed passed.

## V4.6 UX Hardening Acceptance

Status: passed on 2026-05-27.

Allowed scope:

- desktop health preflight.
- hooks config check.
- wrapper script check.
- Codex CLI check.
- clear "run `/hooks` and trust hooks" instruction.
- stable reasonCode.

Recommended reasonCode:

```text
desktop_not_running
hook_config_missing
hook_wrapper_missing
hook_trust_required
hook_lifecycle_not_observed
codex_not_found
pet_instance_create_failed
binding_env_missing
```

Allowed claim:

```text
V4.6 managed session startup diagnostics and UX hardening passed for tested local wrapper-launched scenarios.
```

Evidence:

- `docs/V4.x/evidence/v4_6-startup-diagnostics-smoke-2026-05-27.md`

Forbidden expansion:

- TUI hook mapping passed.
- interactive Codex TUI monitoring ready.
- OS-level binding ready.

## V4.7 Session Status Acceptance

Status: passed on 2026-05-27.

Allowed command:

```bash
petctl codex session status --json
```

Allowed fields:

- `instanceId`
- redacted `bindingId`
- `mode`
- `monitor`
- `status` as `active` / `stale` / `unknown`
- `lastEventKind`
- `lastSeenAt`

Forbidden fields:

- raw TTY
- raw args
- window title
- path
- prompt
- tool command
- raw hook payload
- token
- Authorization

Allowed claim:

```text
V4.7 managed session status and stale-binding diagnostics passed for tested local wrapper-launched scenarios.
```

Evidence:

- `docs/V4.x/evidence/v4_7-session-status-smoke-2026-05-27.md`

## V4.x Final Boundary

V4.x Final status: passed on 2026-05-27.

```text
V4.x managed Codex session-to-PetInstance state mapping passed for tested local wrapper-launched exec JSONL and scoped managed TUI hook scenarios, with Terminal.app candidate binding and manual route-test prototype accepted.
```

## V5.x Acceptance Boundary

V5.x is renderer, 3D, and action asset work. V5.0-V5.10 have passed scoped acceptance through bundled renderer/assets and the personalized CLI import pipeline. V5.11-V5.15 remain planned for productized personalized asset UX, runtime imported rendering, guided photo-to-asset workflow, provider consent review, and visual QA.

V5.x acceptance is defined in `docs/V5.x/v5_x-acceptance-plan.md`. V5.11-V5.15 must not move from planned to passed without phase-specific evidence and final acceptance reports.

V5.11 automated implementation smoke passed, but final acceptance is blocked pending manual Desktop Manager UI validation. See `docs/V5.x/v5_11-final-acceptance-report.md` and `docs/V5.x/v5_11-manual-ui-acceptance-steps.md`.

Planned V5 productization acceptance docs:

- `docs/V5.x/v5_11-import-ui-acceptance-plan.md`
- `docs/V5.x/v5_12-runtime-imported-pack-rendering-acceptance-plan.md`
- `docs/V5.x/v5_13-photo-to-asset-guided-workflow-privacy-review.md`
- `docs/V5.x/v5_14-provider-adapter-feasibility-and-consent-plan.md`
- `docs/V5.x/v5_15-visual-quality-action-qa-plan.md`
- `docs/V5.x/v5_x-productization-gate-plan.md`

## Security Gate

Acceptance evidence must not contain:

```text
token
Authorization
raw JSONL payload
raw hook payload
prompt text
tool command text
shell history
screen contents
clipboard contents
transcript_path
full /Users path
workspace path
config path
api-token.json
```

## Claim Gate

Forbidden as ready / passed:

```text
OS-level Codex window binding ready
interactive Codex TUI monitoring ready
already-open Codex window auto-detection ready
already-open Codex window auto-monitoring ready
V3.6 selected Codex workflow hook coverage smoke passed
PostToolUse failure hook evidence passed
all Codex workflows verified
Codex internal reasoning exact mapping ready
ModelThinkingStart / ModelThinkingEnd verified
MCP ready
Third-party agent integration verified
Claude Code integration verified
Windows ready
cross-platform ready
USB ready
production signed release ready
per-instance queue ready
Rive / Live2D / 3D ready
custom asset pack import ready
user asset upload ready
asset marketplace ready
automatic photo-to-3D ready
provider integration verified
remote asset loading ready
```
