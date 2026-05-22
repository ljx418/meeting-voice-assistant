# V3.0 Current Gap Analysis

文档状态：new mainline；V3.0 final acceptance passed for tested local Codex session scenarios。

## Current State

Current baseline:

- macOS-first MVP ready.
- HTTP API / PetEvent / diagnostics / `petctl` / safe sound complete.
- Codex local workflow integration verified for tested local Codex CLI smoke scenarios.
- V3.0 Phase 3.1 baseline freeze passed.

Phase 3.2 added the initial PetInstance registry and multi-window foundation. Engineering closure has passed; manual visual acceptance is deferred to V3.0 final acceptance.

## Implemented Baseline Checklist

The following capabilities are already accepted. ✅ means accepted only within the documented scope and does not expand to untested platforms or integrations.

| Version / phase | Implemented capability | Evidence / notes |
| --- | --- | --- |
| ✅ V1.0 / macOS-first MVP | Tauri desktop shell, transparent frameless always-on-top window, drag, position persistence, tray, settings page. | macOS-first only; Windows is not accepted. |
| ✅ V1.0 / State Runtime | CSS placeholder cat, eight low-interruption states, CatStateMachine and Behavior Queue. | Phase 2 visual acceptance passed. |
| ✅ V1.0 / Local Event Bridge | PetEvent JSON Schema, localhost HTTP API, token, whitelist, rate limit, diagnostics and rejected reason sanitization. | HTTP / diagnostics smoke passed. |
| ✅ V1.0 / CLI & Sound | `petctl notify`, JSON stdin, bundled sound whitelist, mute and cooldown. | CLI and safe sound smoke passed. |
| ✅ V2.0 / Workflow Templates | Codex / Claude Code instruction templates, integration guide, petctl recipes, shell and Node examples. | Templates and recipes ready only; not Claude Code verified. |
| ✅ V2.0 / User Diagnostics | Settings diagnostics polish for runtime health, sound, accepted/rejected events and quick commands. | Read-only; no command execution or sensitive data display. |
| ✅ V2.0 / Cat Polish | CSS placeholder cat polish with clearer eight-state expression. | Does not imply Rive/Live2D/3D ready. |
| ✅ V2.0 / Distribution Readiness | README quick start, macOS unsigned local app distribution, developer setup and troubleshooting docs. | Does not imply production signed release ready. |
| ✅ V2.0 Final Acceptance | V2.0 final acceptance report passed. | Allows `V2.0 ready: local agent workflow integration and developer usability polish complete.` |
| ✅ V2.1-A | Third-party local HTTP contract smoke passed. | curl / Node / Python contract smoke only; no real third-party product claim. |
| ✅ V2.1-B | Codex local workflow integration verified for tested local Codex CLI smoke scenarios. | Does not imply all Codex workflows, MCP or cross-platform verification. |
| ✅ V3.0 Phase 3.1 | V2.x baseline freeze and complex backlog alignment. | `docs/V3.0/v3_0-baseline-freeze-report.md` status passed. |
| ✅ V3.0 Phase 3.2 | Multi-instance Foundation engineering closure. | `docs/V3.0/evidence/multi-instance-foundation-2026-05-19.md` status passed; manual visual acceptance is deferred to V3.0 final acceptance. |
| ✅ V3.0 Phase 3.3 | Instance-aware Event Routing. | `docs/V3.0/evidence/instance-aware-routing-2026-05-20.md` status passed; does not imply petctl attach or multi-instance Codex verification. |
| ✅ V3.0 Phase 3.4 | Codex Quick Attach. | `docs/V3.0/evidence/codex-quick-attach-2026-05-20.md` status passed; does not imply real two-Codex-session visual verified. |
| ✅ V3.0 Phase 3.5 | Multi-pet Manager UI. | `docs/V3.0/evidence/multi-pet-manager-ui-2026-05-20.md` status passed; copy-only UI, no command execution or notification center. |
| ✅ V3.0 Phase 3.6 | Built-in Asset Pack v1. | `docs/V3.0/evidence/asset-pack-v1-2026-05-20.md` status passed; built-in CSS profiles and per-instance appearance selection only. |
| ✅ V3.0 Final Acceptance | Multi-pet Performance Hardening + final visual + two-Codex-session smoke. | `docs/V3.0/evidence/performance-hardening-final-acceptance-2026-05-20.md` status passed; V3.0 ready only for tested local Codex session scenarios. |

## Target State

V3.0 target:

- Multiple Codex session pets in one Tauri app.
- Each pet has independent name, position, state runtime, and appearance profile.
- Events can route by instance.
- `petctl attach codex` gives each terminal/session an instance.
- Multi-pet manager UI handles common instance operations.

## V3.0 Stage Goal Checklist

Only goals that have passed acceptance and are allowed to be claimed are marked with ✅.

| Stage goal | Status | Evidence / notes |
| --- | --- | --- |
| ✅ V3.0 Phase 3.1: V2.x Baseline Freeze & Backlog Alignment | Passed | `docs/V3.0/v3_0-baseline-freeze-report.md` status passed. |
| ✅ Phase 3.2: Multi-instance Foundation | Engineering closure passed; manual visual acceptance completed in V3.0 final acceptance | `docs/V3.0/evidence/multi-instance-foundation-2026-05-19.md` status passed; final visual evidence is in Phase 3.7 final acceptance. |
| ✅ Phase 3.3: Instance-aware Event Routing | Passed | `POST /api/instances/:instanceId/events`, `GET /api/instances`, target metadata diagnostics, auth/invalid/unknown rejection smoke passed. |
| ✅ Phase 3.4: Codex Quick Attach | Passed | `POST /api/instances`, `petctl attach codex`, `petctl list`, env routing, `--instance`, explicit override, JSON stdin and legacy default smoke passed. |
| ✅ Phase 3.5: Multi-pet Manager UI | Passed | Settings manager shows instances and provides rename/show/hide/reset/detach/copy-only command templates without executing shell. |
| ✅ Phase 3.6: Asset Pack v1 | Passed for implementation and automatic checks; direct visual smoke completed in V3.0 final acceptance | Built-in CSS cat profiles with per-instance appearance selection. |
| ✅ Phase 3.7: Engineering Hardening + Final Acceptance | Passed | soft/hard limits, hidden downgrade, hidden sound skip, event storm guard, operator final visual acceptance and two-Codex-session smoke passed. |

## Gap Matrix

| Gap | Current | Target | Status |
| --- | --- | --- | --- |
| PetInstance registry | Phase 3.2 foundation implemented and engineering-accepted. | Full persisted registry with default pet and lifecycle operations. | ✅ Phase 3.2 |
| Multiple pet windows | Phase 3.2 foundation implemented and engineering-accepted; visual final passed. | Multiple visible draggable pet windows, restored on restart. | ✅ Phase 3.2 / final visual |
| Independent runtime | Extra windows have local CatStateMachine runtime foundation. | Per-instance queue/state integrated with router. | ✅ Phase 3.2 / Phase 3.3 |
| Instance event routing | Implemented instance-scoped HTTP endpoint and frontend target filtering. Legacy `/api/events` routes to default pet. | `/api/instances/:instanceId/events` routes to target pet. | ✅ Phase 3.3 |
| Codex quick attach | Implemented for CLI/HTTP quick attach and instance-scoped petctl routing. | Real two-Codex-session visual verification for tested local scenarios. | ✅ Phase 3.4 / final visual |
| Manager UI | Implemented settings Multi-pet Manager with rename/show/hide/reset/detach/copy-only command templates. | Final visual acceptance passed; later per-instance diagnostics polish remains optional backlog. | ✅ Phase 3.5 / final visual |
| Asset Pack v1 | Built-in CSS profiles implemented; Manager can switch and persist per-instance `catProfileId`. | Final visual acceptance passed; richer asset formats remain backlog. | ✅ Phase 3.6 / final visual |
| Performance | Engineering hardening passed under current global queue model. | Final visual acceptance and two-Codex final smoke passed for tested local scenarios. | ✅ V3.0 final acceptance |

## Allowed Current Claims

```text
macOS-first MVP ready: local desktop agent status pet with HTTP + petctl integration and safe sound feedback.
V2.0 ready: local agent workflow integration and developer usability polish complete.
Codex local workflow integration verified for tested local Codex CLI smoke scenarios.
V3.0 Phase 3.1 complete: V2.x baseline frozen and complex integration backlog aligned.
Phase 3.2 complete: multi-instance pet foundation ready.
Phase 3.3 complete: instance-aware event routing ready.
Phase 3.4 complete: Codex quick attach and instance-scoped petctl routing ready.
Phase 3.5 complete: multi-pet manager UI ready.
Phase 3.6 complete: built-in asset pack v1 and per-instance appearance selection ready.
Phase 3.7 engineering hardening complete: multi-pet runtime limits and stability guards ready.
V3.0 ready: multi-instance Codex desktop pet workflow ready for tested local Codex session scenarios.
```

## Forbidden Current Claims

```text
unqualified multi-instance Codex verified beyond tested local scenarios
all Codex workflows verified
OS-level Codex window binding ready
per-instance queue ready
Claude Code integration verified
MCP ready
Windows ready
cross-platform ready
USB ready
Rive/Live2D/3D ready
photo customization ready
user asset upload ready
remote asset download ready
custom asset pack import ready
production signed release ready
```
