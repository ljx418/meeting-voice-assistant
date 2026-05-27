# V4.5 Managed TUI Preflight Smoke Evidence

status: passed

date: 2026-05-27

## Scope

This evidence covers only the managed TUI wrapper preflight:

```bash
node scripts/v4_5_managed_tui_preflight_smoke.mjs
```

It does not prove real Codex hook lifecycle mapping.

## Result

The preflight passed after restarting the desktop app and confirming desktop bridge health.

```text
desktop health: passed
managed TUI preflight exits 0
managed TUI instance created
sessionMode=tui
mode=hooks
bindingId=bind_managed_*
managed TUI final state success
cleanup passed
security redaction scan passed
claim scan passed
```

## Already Completed Before Block

The V4.5 plan and audit gates are complete:

- `docs/V4.x/v4_5-development-plan.md`
- `docs/V4.x/v4_5-acceptance-plan.md`
- `docs/V4.x/v4_5-prd-spec-review.md`
- `docs/V4.x/v4_5-plan-audit.md`
- `docs/V4.x/v4_5-claim-matrix.md`

Automatic checks completed before this runtime smoke:

```text
pnpm --filter @agent-desktop-pet/petctl check: passed
pnpm --filter @agent-desktop-pet/petctl test: passed, 46 tests
pnpm --filter @agent-desktop-pet/petctl build: passed
node scripts/v4_4_managed_session_smoke.mjs: passed
node scripts/v4_5_managed_tui_preflight_smoke.mjs: passed
```

## Remaining User Action

The preflight proves wrapper readiness only. Real Codex hook lifecycle acceptance still requires user action in Codex TUI.

## Forbidden Conclusion

Do not claim yet:

```text
V4.5 managed Codex TUI hook state mapping passed
interactive Codex TUI monitoring ready
OS-level Codex window binding ready
```
