# V3.0 Final Acceptance Report

status: passed  
date: 2026-05-20  
scope: tested local Codex session scenarios on macOS-first local app  

## Summary

V3.0 upgrades `agent-desktop-pet` from a single default status cat to a multi-instance Codex working partner system.

The accepted V3.0 workflow is:

```text
Codex terminal/session
  -> petctl attach codex
  -> PetInstance
  -> petctl notify --instance <instanceId>
  -> target desktop cat only
```

V3.0 final acceptance passed for tested local Codex session scenarios. It does not claim OS-level Codex window binding, all Codex workflows, Windows, MCP, USB, production signing, or richer renderer readiness.

## Evidence

| Evidence | Path | Status | Notes |
| --- | --- | --- | --- |
| Performance hardening + final acceptance | `docs/V3.0/evidence/performance-hardening-final-acceptance-2026-05-20.md` | passed | `engineeringStatus=passed`, `finalVisualStatus=passed`, `twoCodexSessionStatus=passed`, `v3ReadyDecision=ready`. |
| Operator final visual checklist | `docs/V3.0/v3_0-final-visual-acceptance-checklist.md` | passed | A-I, J1 and J2 were marked passed by operator. |
| Claim matrix | `docs/V3.0/v3_0-claim-matrix.md` | passed scope recorded | V3.0 ready claim is limited to tested local Codex session scenarios. |
| Evidence index | `docs/V3.0/v3_0-evidence-index.md` | updated | Points to the frozen V3.0 evidence sources. |

## Accepted Capabilities

- Multiple independent pet windows in one Tauri app.
- Per-instance `instanceId`, display name, window label, position, visible state and cat profile.
- Instance-aware event routing via `POST /api/instances/:instanceId/events`.
- Legacy `/api/events` and legacy `petctl notify` route to the default pet.
- `petctl attach codex`, `petctl list`, `petctl notify --instance`, and `AGENT_DESKTOP_PET_INSTANCE_ID` routing.
- Multi-pet Manager UI for rename, show/hide, reset position, detach, copy env export, copy notify template and appearance selection.
- Built-in CSS cat profiles: `default-cat`, `black-cat`, `orange-tabby`, `white-cat`.
- Multi-pet runtime hardening: soft limit, hard limit, hidden pet downgrade, sound cooldown and event storm guard under the current global queue model.

## Allowed Claims

```text
V3.0 ready: multi-instance Codex desktop pet workflow ready for tested local Codex session scenarios.
Phase 3.7 engineering hardening complete: multi-pet runtime limits and stability guards ready.
```

## Forbidden Claims

```text
all Codex workflows verified
OS-level Codex window binding ready
per-instance queue ready
Claude Code integration verified
MCP ready
Windows ready
cross-platform ready
USB ready
Rive / Live2D / 3D ready
photo customization ready
user asset upload ready
production signed release ready
auto update ready
```

## Residual Risks

- Current ingress queue is still a global queue model; per-instance queue is not implemented or claimed.
- V3.0 validates local Codex session workflows, not every possible Codex workflow or all terminals.
- The app remains a macOS-first unsigned local app.
- Claude Code hook verification, MCP, Windows, USB and production release remain future backlog.

