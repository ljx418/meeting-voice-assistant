# V3.0 Backlog

文档状态：new mainline backlog。

## Phase 3.2 Multi-instance Foundation

- current status: complete for engineering closure; manual visual acceptance completed in V3.0 final acceptance.
- why not completed: not applicable.
- entry condition: V2.x baseline frozen; no regression in default pet.
- acceptance criteria: default pet plus two extra PetInstance windows visible; independent names, positions and local debug state; restart restores windows; legacy `/api/events` and `petctl notify` still affect default pet.
- allowed claim: `Phase 3.2 complete: multi-instance pet foundation ready.`
- forbidden claim: claims beyond foundation unless later evidence is cited; `multi-instance Codex verified` remains forbidden.

## Phase 3.3 Instance-aware Event Routing

- current status: complete.
- why not completed: not applicable.
- entry condition: Phase 3.2 passed.
- acceptance criteria: `POST /api/instances/:instanceId/events` routes only to target instance; unknown instance returns `404 instance_not_found`; default `/api/events` remains compatible.
- allowed claim: `Phase 3.3 complete: instance-aware event routing ready.`
- forbidden claim: Codex quick attach or multi-session Codex verified.

## Phase 3.4 Codex Quick Attach

- current status: complete for CLI/HTTP quick attach; real two-Codex-session visual smoke completed in V3.0 final acceptance.
- why not completed: not applicable.
- entry condition: Phase 3.3 passed.
- acceptance criteria: `POST /api/instances`, `petctl attach codex --name <pet-name>`, `petctl list`, `AGENT_DESKTOP_PET_INSTANCE_ID`, `--instance`, explicit override, JSON stdin and legacy default routing smoke pass.
- allowed claim: `Phase 3.4 complete: Codex quick attach and instance-scoped petctl routing ready.`
- forbidden claim: all Codex workflows verified or OS-level Codex window binding.

## Phase 3.5 Multi-pet Manager UI

- current status: complete for implementation and runtime smoke; direct click visual acceptance completed in V3.0 final acceptance.
- why not completed: not applicable for Phase 3.5 scoped implementation.
- entry condition: Phase 3.4 passed or stable enough for user management.
- acceptance criteria: settings page supports rename, show/hide, reset position, detach and copy attach/export commands without executing shell.
- allowed claim: `Phase 3.5 complete: multi-pet manager UI ready.`
- forbidden claim: notification center or command-execution dashboard.

## Phase 3.6 Asset Pack v1

- current status: complete for built-in CSS profiles and per-instance appearance selection; direct visual acceptance completed in V3.0 final acceptance.
- why not completed: not applicable for built-in profile scope; richer asset formats remain explicitly deferred.
- entry condition: manager can select per-instance profile.
- acceptance criteria: at least four built-in CSS cat profiles; per-instance profile persists; state animation, transparency and drag priority do not regress.
- allowed claim: `Phase 3.6 complete: built-in asset pack v1 and per-instance appearance selection ready.`
- forbidden claim: Rive/Live2D/3D/photo customization ready, user asset upload ready, remote asset download ready, custom asset pack import ready, asset marketplace ready.

## Phase 3.7 Performance Hardening

- current status: engineering hardening complete; final visual acceptance and two-Codex-session smoke passed for tested local scenarios.
- why not completed: not applicable for tested local scenarios.
- entry condition: Phase 3.3+ passed.
- acceptance criteria: six active pets remain responsive; one instance event storm does not affect others; multi-instance sound cooldown prevents audio spam.
- allowed claim: `Phase 3.7 engineering hardening complete: multi-pet runtime limits and stability guards ready.`
- forbidden claim: all Codex workflows verified, per-instance queue ready, cross-platform or production release ready.

## V3.0 Final Acceptance

- current status: passed for tested local Codex session scenarios.
- why not completed: not applicable.
- entry condition: Phase 3.7 engineering hardening complete.
- acceptance criteria: final visual table passed; two Codex sessions attach and drive separate cats; diagnostics show distinct targetInstanceId; no false-green claims.
- allowed claim if passed: `V3.0 ready: multi-instance Codex desktop pet workflow ready for tested local Codex session scenarios.`
- forbidden claim: all Codex workflows verified, OS-level window binding, Windows/cross-platform/MCP/USB/production ready.

## Deferred Complex Integrations

### Claude Code Skill / Hook Real Verification

- current status: skill runtime accepted diagnostics evidence captured; full visual + hook verification is not complete.
- why not completed: V3.0 mainline changed to multi-instance Codex.
- entry condition: after multi-instance Codex foundation or separate V3.x decision.
- acceptance criteria: diagnostics shows `sourceId=claude-code.local`; skill visual acceptance passes; `Notification -> need_input` hook produces accepted event; no token/payload/path leakage.
- allowed claim: scoped Claude Code skill or hook claim only after passed evidence.
- forbidden claim: `Claude Code integration verified` from template or partial runtime evidence.

### Real Third-party Product Integration

- current status: local HTTP contract smoke passed using curl / Node / Python examples.
- why not completed: no real third-party agent product was selected and tested.
- entry condition: choose a real product or agent runtime with stable lifecycle events.
- acceptance criteria: real product emits success/error/need_input through HTTP or `petctl`; diagnostics evidence exists.
- allowed claim: product-specific integration claim.
- forbidden claim: generic `Third-party agent integration verified` for untested products.

### MCP Adapter

- current status: research-only; no `packages/pet-mcp` implementation.
- why not completed: V3.0 mainline is multi-instance Codex via CLI/HTTP first.
- entry condition: decide implement/defer based on Codex/Claude MCP runtime requirements.
- acceptance criteria: if implemented, `pet_notify`, `pet_get_capabilities`, and `pet_get_state` pass real Codex/Claude MCP smoke.
- allowed claim: `MCP adapter decision complete` after decision; `MCP ready` only after implementation + smoke.
- forbidden claim: `MCP ready` from research docs alone.

### Windows, USB, High-fidelity Assets, Production Release

- current status: not implemented or not smoke-tested.
- why not completed: outside current multi-instance Codex mainline.
- entry condition: explicit scope approval and test environment.
- acceptance criteria: each must pass its own implementation and smoke plan.
- allowed claim: scoped only to tested capability.
- forbidden claim: Windows ready, cross-platform ready, USB ready, Rive/Live2D/3D ready, photo customization ready, production signed release ready, auto update ready.
