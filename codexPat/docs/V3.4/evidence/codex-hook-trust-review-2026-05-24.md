# Codex Hook Trust Review Evidence

date: 2026-05-24

status: blocked

## Required Operator Steps

1. Start a Codex session in this repository.
2. Run `/hooks`.
3. Review `.codex/hooks.json`.
4. Trust the project hooks if the command points to `node scripts/codex-pet-hook.mjs`.
5. Do not approve unexpected hook commands.

## Notes

`--dangerously-bypass-hook-trust` is not the normal user path. It may only be used for explicit local smoke and must be recorded as such.
