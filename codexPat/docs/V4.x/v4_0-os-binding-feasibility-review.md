# V4.0 OS Binding Feasibility Review

status: accepted-feasibility-review

date: 2026-05-26

## Scope Freeze

V4.0 is a feasibility review only.

V4.0 does not implement:

- active window probe.
- Accessibility / Automation code.
- shell helper code.
- user-confirmed binding UX.
- selected-terminal routing.
- interactive Codex TUI monitoring.
- asset, renderer, packaging, or productization work.

V4.0 evaluates whether later phases may safely attempt these capabilities:

- V4.1 active window safe-field probe.
- V4.2 explicit user-confirmed binding UX.
- V4.3 selected-terminal routing prototype.

## PRD Spec Review

PRD review result: no major or critical mismatch.

Reviewed source:

- `docs/active/agent_desktop_pet_prd_v3x.md`
- `docs/V4.x/v4_0-development-plan.md`
- `docs/V4.x/v4_0-acceptance-plan.md`
- `docs/V4.x/v4_0-prd-spec-review.md`
- `docs/V4.x/v4_0-plan-audit.md`
- `docs/V4.x/v4_x-claim-matrix.md`

PRD alignment:

- V4.x is OS-level Codex window/session binding feasibility.
- V4.x must not claim OS-level binding ready.
- V4.x does not include asset, renderer, packaging, or productization acceptance gates.
- V3.7 remains the default reliable path for wrapper-launched `codex exec --json`.
- V3.7 is not OS-level evidence and does not cover interactive Codex TUI monitoring.

## Terminal Matrix

This is a feasibility matrix, not runtime evidence.

| Terminal | active window detection | Codex process identification | TTY/session identity | event source availability | privacy risk | permission requirement | verdict |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Terminal.app | Prototype candidate. Focused window can likely be discovered through macOS Accessibility / Automation, but V4.1 must verify safe fields. | Prototype candidate. Process tree may identify shell / Codex process, but V4.1 must verify without terminal text. | Prototype candidate. TTY may be derivable from process metadata, but only redacted summary may be stored. | No reliable lifecycle event source from OS discovery alone. Requires preconfigured hook/registry or wrapper relaunch. | Medium. Window title and process metadata may expose names or paths if not redacted. | Accessibility and possibly Automation. | Go for V4.1 safe-field probe only; no-go for V4.3 routing without event source proof. |
| iTerm2 | Prototype candidate. App-specific APIs and Accessibility may expose focused session/window, but V4.1 must verify. | Prototype candidate. Process identity may be available through app/session/process metadata. | Prototype candidate. Session and TTY identity may be available but must be redacted. | No reliable lifecycle event source from discovery alone. Requires preconfigured hook/registry or wrapper relaunch. | Medium. Session titles and profile metadata may expose sensitive names. | Accessibility, Automation, or iTerm2-specific integration. | Go for V4.1 safe-field probe only; no-go for V4.3 routing without event source proof. |
| VS Code integrated terminal | High-risk candidate. Active editor/window can be detected, but terminal pane/session identity is not safely available from OS-level window discovery alone. | Unclear without VS Code extension or shell registry. | Unclear without extension or shell registry. | No reliable lifecycle event source from OS discovery alone. | High. UI/title metadata may be ambiguous and workspace-associated. | Accessibility or VS Code extension/shell integration. | No-go for pure OS-level binding; possible future extension/shell-registry track only. |
| Warp | High-risk candidate. Terminal UI abstraction may not expose stable safe fields through OS-level discovery. | Unclear without app-specific support or shell registry. | Unclear without app-specific support or shell registry. | No reliable lifecycle event source from OS discovery alone. | High. App metadata may be insufficient or ambiguous. | Accessibility or app-specific integration if available. | No-go for V4.1 default probe; reassess only with explicit app-specific support. |
| Ghostty | Prototype/unknown candidate. Window detection may be possible through Accessibility, but session/process mapping must be verified. | Unclear without process/TTY probe. | Unclear without process/TTY probe. | No reliable lifecycle event source from OS discovery alone. | Medium. Process and title metadata must be redacted. | Accessibility and process metadata probe. | Defer V4.1 until Terminal.app/iTerm2 are proven; no-go for V4.3 routing without event source proof. |

## Permission Model

Potential permission sources:

- macOS Accessibility: active app/window and UI metadata discovery.
- macOS Automation: terminal-specific scripted access, if used.
- terminal-specific API: iTerm2 / VS Code extension / app-supported integration, if separately accepted later.
- shell helper / session registry: only for future sessions or shells where user explicitly installs the helper.
- local helper process: only if a later phase proves it can operate without reading forbidden fields.

V4.0 decision:

- Permission prompts must be opt-in and user-visible.
- V4.1 must not request broad permissions before documenting the exact safe fields it needs.
- V4.x must not silently bind a focused window.

## Privacy Model

Allowed fields:

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

Forbidden fields:

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

Evidence rule:

- Record only safe field names, redacted summaries, verdicts, permission states, and acceptance decisions.
- Do not record raw OS probe output.

## State Event Source Analysis

OS-level discovery can identify a candidate window/session. It cannot by itself provide Codex lifecycle state events.

Potential event sources:

| Source | Applies to already-running Codex session | Can prove event ownership | V4.0 decision |
| --- | --- | --- | --- |
| V3.7 wrapper JSONL monitor | No, unless user relaunches through wrapper. | Yes for wrapper-launched `codex exec --json`. | Keep as default reliable fallback, not OS-level evidence. |
| Codex hooks | Only if hooks were configured before the Codex session started and include safe route context. | Possible only with pre-established route key. | Not sufficient for arbitrary already-running sessions. |
| Shell/TTY session registry | Only if registry was installed before session start or can be manually associated by user. | Possible for future sessions, not guaranteed for existing sessions. | Candidate for later planning; not V4.0 implementation. |
| Process/TTY metadata only | Yes for discovery. | No lifecycle proof. | Discovery-only; cannot pass V4.3 routing. |
| Terminal text parsing | Technically possible in some terminals. | Not allowed. | Forbidden. |
| `transcript_path` | May exist in some Codex contexts. | Not a stable interface. | Forbidden as route/source evidence. |

V4.0 answer:

- State events for already-running interactive Codex sessions are not available from OS-level discovery alone.
- If no hook/registry route key already exists, event ownership cannot be proven.
- If `AGENT_DESKTOP_PET_INSTANCE_ID` cannot be injected into the already-running session, the product must prompt the user to relaunch through the V3.7 wrapper path or install a future explicit registry before starting Codex.

## Event Ownership Decision

V4.3 selected-terminal routing may only proceed if a future phase proves all of these:

- the candidate session has a safe route key.
- lifecycle events include that route key or another accepted ownership proof.
- the route key maps to exactly one user-confirmed `PetInstance`.
- another Codex terminal cannot affect the selected pet.

If any item is missing, V4.3 must remain blocked or no-go for that terminal.

## Subphase End-to-end Acceptance

| Subphase | Result | PRD review | Risk result |
| --- | --- | --- | --- |
| V4.0.1 Scope Freeze | passed | aligned | no implementation included |
| V4.0.2 PRD Spec Review | passed | no major/critical mismatch | asset/productization drift closed |
| V4.0.3 Terminal Matrix Design | passed | covers user scenario | no runtime evidence claim |
| V4.0.4 Permission / Privacy Model | passed | no privacy regression | forbidden fields retained |
| V4.0.5 State Event Source Analysis | passed with no-go for routing from discovery alone | aligned | discovery not treated as state monitoring |
| V4.0.6 Go / No-go | passed | aligned | no High false-green risk after scoped no-go |
| V4.0.7 Final Feasibility Acceptance | passed as feasibility only | aligned | no ready claim |

## False-green Risk Assessment

| Risk | Level | Mitigation |
| --- | --- | --- |
| Window discovery counted as TUI monitoring | Medium | V4.0 explicitly says discovery does not provide lifecycle events. |
| Single terminal candidate treated as general support | Medium | V4.1 may start only for scoped terminal(s), not all terminals. |
| V3.7 evidence reused as OS-level evidence | Medium | V3.7 is documented only as fallback. |
| Event ownership assumed without route key | Medium | V4.3 is no-go unless ownership proof exists. |
| Asset/productization scope drift | Low | PRD moved this work to V5.x/later tracks. |

Overall risk: Medium.

No High risk remains after scoping V4.0 as feasibility-only and marking routing from discovery alone as no-go.

## Go / No-go Decision

V4.0 decision:

```text
V4.0 OS-level Codex window/session binding feasibility review completed with scoped go/no-go decision.
```

Scoped go:

- Go to plan V4.1 active window safe-field probe for Terminal.app and iTerm2 first.
- V4.1 must be planned and audited separately before implementation.
- V4.1 may collect only allowed safe fields and must not claim binding or state monitoring.

Scoped no-go:

- No-go for V4.3 selected-terminal routing from OS-level discovery alone.
- No-go for interactive Codex TUI monitoring ready.
- No-go for already-open Codex window auto-detection ready.
- No-go for all-terminal or all-Codex workflow claims.

Fallback:

- If a safe event source or route key is unavailable, prompt the user to relaunch with the V3.7 wrapper path.

## Claim Scan

Allowed V4.0 claim:

```text
V4.0 OS-level Codex window/session binding feasibility review completed with scoped go/no-go decision.
```

Forbidden claims remain not-ready:

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

## Security Scan

This document does not contain:

```text
token
Authorization
raw payload
terminal text
prompt text
tool command text
shell history
screen contents
clipboard contents
transcript_path value
full /Users path
workspace path
config path
api-token.json
```
