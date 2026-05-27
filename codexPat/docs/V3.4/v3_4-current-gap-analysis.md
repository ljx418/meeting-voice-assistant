# V3.4 Current vs Target Gap

文档状态：final.

## Current State

V3.3 provides wrapper-first Codex session binding:

- `petctl codex launch` creates a pet instance.
- child process gets `AGENT_DESKTOP_PET_INSTANCE_ID`.
- wrapper maps process lifecycle to `running / success / error`.

V3.4 adds hook-phase mapping. Fixture evidence passed and real Codex hook lifecycle was accepted by operator validation on 2026-05-25.

## Gap Matrix

| Area | Current | Target | Status |
| --- | --- | --- | --- |
| Hook config | `.codex/hooks.json` added | project hooks available | closed |
| Hook wrapper | `scripts/codex-pet-hook.mjs` added | safe PetEvent writer | closed |
| Fixture mapping | fixture smoke added | all target mappings verified | closed |
| Real lifecycle | requires Codex `/hooks` trust | observed hook lifecycle | closed for tested local scenario |
| Internal reasoning | not available | exact model thinking states | out of scope |
| OS-level binding | wrapper-first only | arbitrary OS window detection | out of scope |

## Remaining Work

- Keep future regressions for `PermissionRequest -> need_input` and `PostToolUse failure -> error` because they depend on local Codex approval policy and stable failure payload fields.
- Do not broaden the claim to exact internal reasoning or all Codex workflows.
