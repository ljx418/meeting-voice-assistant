# V3.0 Acceptance Plan

文档状态：new mainline；V3.0 final acceptance passed for tested local Codex session scenarios。

## Acceptance Matrix

| Phase | Required evidence | Pass condition | Allowed claim |
| --- | --- | --- | --- |
| Phase 3.2 Multi-instance Foundation | automatic checks, `.app` build, health, legacy petctl/raw HTTP smoke | engineering closure passed; manual visual checks completed in final V3.0 acceptance | `Phase 3.2 complete: multi-instance pet foundation ready.` |
| ✅ Phase 3.3 Instance-aware Event Routing | HTTP smoke and diagnostics | instance endpoint, auth, invalid/unknown instance rejection, target metadata diagnostics and default `/api/events` compatibility passed | `Phase 3.3 complete: instance-aware event routing ready.` |
| ✅ Phase 3.4 Codex Quick Attach | CLI/HTTP smoke | `POST /api/instances`, `petctl attach codex`, env routing, `--instance`, explicit override, JSON stdin and legacy default routing passed | `Phase 3.4 complete: Codex quick attach and instance-scoped petctl routing ready.` |
| ✅ Phase 3.4 final two-Codex session smoke | real two-terminal Codex smoke + operator visual acceptance | passed in Phase 3.7 final acceptance | `V3.0 ready: multi-instance Codex desktop pet workflow ready for tested local Codex session scenarios.` |
| ✅ Phase 3.5 Multi-pet Manager UI | implementation + runtime smoke | rename/show/hide/reset/detach/copy-only commands implemented; manager list and routing registry sync passed; direct click visual smoke completed in final acceptance | `Phase 3.5 complete: multi-pet manager UI ready.` |
| ✅ Phase 3.6 Asset Pack v1 | implementation + automatic checks | built-in CSS profiles and per-instance profile selection implemented; direct visual smoke completed in final acceptance | `Phase 3.6 complete: built-in asset pack v1 and per-instance appearance selection ready.` |
| ✅ Phase 3.7 Engineering Hardening | automatic checks + runtime smoke | soft/hard limits, hidden downgrade, hidden sound skip, event storm guard and Manager count/warning passed | `Phase 3.7 engineering hardening complete: multi-pet runtime limits and stability guards ready.` |
| ✅ Phase 3.7 Final Visual Acceptance | operator visual | passed | visual acceptance complete |
| ✅ Phase 3.7 Two-Codex-session Smoke | real/equivalent Codex sessions | passed | tested local Codex session scenarios complete |
| ✅ Phase 3.7 Performance Hardening + Final Visual Acceptance | load smoke, full manual visual acceptance and real/equivalent two-Codex-session smoke | passed | `V3.0 ready: multi-instance Codex desktop pet workflow ready for tested local Codex session scenarios.` |

## Deferred Manual Smoke

Manual visual smoke has been completed in V3.0 final acceptance. Phase 3.2 remains scoped to engineering closure, while final visual evidence is recorded in Phase 3.7 final acceptance.

Operator checklist: [V3.0 Final Visual Acceptance Checklist](v3_0-final-visual-acceptance-checklist.md).

- Launch app.
- Confirm default cat appears.
- Open settings.
- Create two Codex cats.
- Confirm three cat windows are visible.
- Drag each cat to a different position.
- Trigger debug states in each extra cat and confirm states do not affect the others.
- Restart app and confirm extra cats and positions restore.
- Run old `petctl notify --level success --title "legacy smoke"` and confirm only default cat responds.

## No False-Green

Do not claim beyond tested scope:

```text
all Codex workflows verified
unqualified Codex multi-instance verified beyond tested local scenarios
OS-level window binding ready
Claude Code integration verified
MCP ready
Windows ready
cross-platform ready
USB ready
production signed release ready
```

V3.0 ready is allowed only in the exact tested-scope wording:

```text
V3.0 ready: multi-instance Codex desktop pet workflow ready for tested local Codex session scenarios.
```
