# V4.1 Plan Audit

status: passed-terminal-app

date: 2026-05-26

## Audit Scope

This audit checks whether V4.1 may enter implementation under the project rule:

```text
Before implementation, create development and acceptance plans from the PRD, complete PRD review, close audit findings, and stop if critical/major drift or High false-green risk appears.
```

## Audit Findings

| ID | Severity | Finding | Required Action | Status |
| --- | --- | --- | --- | --- |
| AUDIT-V4.1-001 | Medium | Probe output could be mistaken for binding or lifecycle monitoring. | CLI help, output docs, and evidence must call it `safe-field probe` only. | closed in plan |
| AUDIT-V4.1-002 | Medium | Window/session summaries may include sensitive names if raw titles are printed. | Output only redacted summaries; never print raw window title/session title. | closed in plan |
| AUDIT-V4.1-003 | Medium | Terminal.app result could be generalized to iTerm2 or all terminals. | Claims must include `<terminal app>` and tested environment. | closed in plan |
| AUDIT-V4.1-004 | Medium | Permission denied behavior could leak OS error details. | Map to safe `permission_denied` reason without raw OS output. | closed in plan |

No critical or major findings remain open.

## False-green Risk Assessment

| Risk | Level | Mitigation |
| --- | --- | --- |
| Probe counted as binding | Medium | V4.1 forbids `PetInstance` mutation and PetEvent emission. |
| Probe counted as lifecycle monitoring | Medium | V4.1 forbids state event claims and routing. |
| Sensitive OS metadata leakage | Medium | Output allow-list and redacted summaries required. |
| Terminal evidence overgeneralized | Medium | Terminal-specific claims only. |
| Scope drift into V4.2/V4.3 | Medium | V4.1 excludes binding UX and routing. |
| Node-wrapper Codex overmatched as ordinary Node | Medium | Same-TTY Node candidates require Codex-specific args signatures; raw args are classifier-only and never emitted. |

Overall risk: Medium.

No High false-green risk remains after the current scope restrictions.

## Implementation Decision

go / no-go: V4.1 implementation completed; runtime acceptance blocked.

Allowed implementation:

- CLI-side read-only safe-field probe.
- Terminal.app and iTerm2 only.
- JSON output with allowed fields only.
- safe failure for permission denied, unsupported terminal, Codex process not found, and session identity unavailable.
- tests for parser/output redaction behavior.

Not allowed:

- desktop UI.
- Tauri command integration.
- `PetInstance` creation or mutation.
- `notify` / PetEvent emission.
- selected-terminal routing.
- lifecycle state monitoring.
- VS Code / Warp / Ghostty implementation.

## Required Post-implementation Acceptance

After implementation, V4.1 must produce:

- runtime smoke evidence for Terminal.app and/or iTerm2, or blocked evidence if local permission/environment prevents runtime verification.
- PRD review refresh.
- claim scan.
- security scan.
- final V4.1 acceptance decision.

If runtime evidence is blocked, V4.1 must not claim a passed safe-field probe.

## Post-implementation Audit

Runtime evidence:

- `docs/V4.x/evidence/v4_1-safe-field-probe-2026-05-26.md`
- `docs/V4.x/v4_1-final-acceptance-report.md`

Result:

- implementation built and unit-tested.
- Node-packaged Codex CLI process detection regression was fixed and unit-tested.
- runtime acceptance passed for Terminal.app in the current local environment.
- iTerm2 remains blocked and must not be generalized from Terminal.app evidence.
- V4.2 may be planned from Terminal.app-only evidence, but must not claim binding, routing, lifecycle monitoring, iTerm2 support, or all-terminal support.
