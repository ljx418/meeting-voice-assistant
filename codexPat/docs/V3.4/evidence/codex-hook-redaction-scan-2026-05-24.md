# Codex Hook Redaction Scan Evidence

date: 2026-05-24

status: passed for fixture smoke

## Forbidden Output

Evidence and smoke output must not include:

- token
- Authorization header
- raw hook stdin
- raw payload
- prompt text
- tool input command
- transcript path
- config path
- workspace path
- full local path

## Current Design

`scripts/codex-pet-hook.mjs` emits only `{}` on stdout and redacted debug summaries only when `CODEX_PET_HOOK_DEBUG=1`.

## Fixture Smoke Result

The V3.4 fixture smoke security redaction scan passed.

Observed smoke summary did not include forbidden output.
