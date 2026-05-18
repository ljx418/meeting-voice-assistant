# Third-party Agent Contract Report

status: passed  
date: 2026-05-18 17:20:16 CST

## Purpose

记录 third-party local agent contract 的 smoke 结果。正式验收依据见 `docs/reference/third-party-agent-contract.md`。

## Evidence Table

| Scenario | Command | Expected | Actual | Result | Notes |
| --- | --- | --- | --- | --- | --- |
| Baseline doctor | `pnpm run doctor` | no hard failure | completed with WARN only | warn | WARN: no rustup, external network checks unreachable, sandbox cannot listen on `127.0.0.1:1420`; not blocking cached local build path. |
| pet-protocol check | `pnpm --filter @agent-desktop-pet/pet-protocol check` | pass | pass | pass | TypeScript check passed. |
| pet-protocol test | `pnpm --filter @agent-desktop-pet/pet-protocol test` | pass | pass | pass | 3 tests passed. |
| petctl check | `pnpm --filter @agent-desktop-pet/petctl check` | pass | pass | pass | TypeScript check passed. |
| petctl test | `pnpm --filter @agent-desktop-pet/petctl test` | pass | pass | pass | 6 tests passed. |
| desktop check | `pnpm --filter desktop check` | pass | pass | pass | TypeScript check passed. |
| Rust check | `cargo check --manifest-path apps/desktop/src-tauri/Cargo.toml` | pass | pass | pass | Rust check passed. |
| desktop build | `pnpm --filter desktop build` | pass | pass | pass | Vite build passed. |
| app launch | `open "apps/desktop/src-tauri/target/release/bundle/macos/Agent Desktop Pet.app"` | bridge listens on 127.0.0.1:17321 | `agent-des` listened on port 17321 | pass | GUI visual confirmation still requires user observation. |
| health | `curl -sS http://127.0.0.1:17321/api/health` | `ok=true` | returned `ok=true` | pass | Health endpoint reachable. |
| diagnostics without token | `curl -i -sS /api/diagnostics` | 401 `auth_missing` | 401 `auth_missing` | pass | Token not printed. |
| curl success event | `examples/http/curl-agent-smoke.sh success` | 202 accepted and `curl.local` appears | 202 accepted, diagnostics source includes `curl.local` | pass | Uses `source.kind=custom`. |
| Node HTTP success event | `node examples/http/node-http-agent-smoke.mjs success` | 202 accepted and `http-node.local` appears | 202 accepted, diagnostics source includes `http-node.local` | pass | Uses direct HTTP, not SDK. |
| Python HTTP success event | `python3 examples/http/python_http_agent_smoke.py success` | 202 accepted and `http-python.local` appears | 202 accepted, diagnostics source includes `http-python.local` | pass | Uses Python standard library. |
| missing token POST | direct `POST /api/events` without auth | 401 `auth_missing` | 401 `auth_missing` | pass | No token printed. |
| example missing token | `AGENT_DESKTOP_PET_TOKEN= examples/http/curl-agent-smoke.sh success` | local refusal, no token printed | exit 2, token not printed | pass | Example fails before sending HTTP. |
| invalid level | direct HTTP with `level=nope` | 400 schema/whitelist invalid | 400 `whitelist_invalid` | pass | Event not accepted. |
| invalid sound path rejection | direct HTTP with `sound=../../x.wav` | rejected and not accepted | 400 `whitelist_invalid`, `reasonField=sound`, `reason=sound is not an accepted ID` | pass | Event not accepted; submitted path was not echoed. |
| invalid sound URL rejection | direct HTTP with `sound=https://example.com/x.wav` | rejected and not accepted | 400 `whitelist_invalid`, `reasonField=sound`, `reason=sound is not an accepted ID` | pass | Event not accepted; submitted URL was not echoed. |
| invalid source id redaction | direct HTTP with invalid `source.id` | rejected and not accepted; diagnostics must not echo source | 400 `schema_invalid`, diagnostics `sourceId=invalid_source` | pass | Submitted invalid source id was not echoed. |
| high frequency events | 20 rapid `running` POSTs from `load.local` | 429 or queue rejection, diagnostics rejected summary | first 10 accepted, later requests returned 429 `rate_limited` | pass | Rate limit behaved as expected. |
| diagnostics summary | token-protected diagnostics | accepted/rejected/source/sound visible; no token/raw payload/metadata/sound path | sources and reason codes visible; token/raw payload absent; redaction scan returned no hits | pass | Rejected summaries use `reasonCode`, `reasonField`, and generic `reason`. |

## Claim Boundary

This report allows claiming `Third-party local HTTP contract smoke passed`.

Do not claim `Third-party agent integration verified`; V2.1-A validates the local HTTP contract smoke, not a real third-party agent product integration.

## Diagnostics Evidence Summary

Accepted sources observed:

- `curl.local`
- `http-node.local`
- `http-python.local`
- `load.local`

Rejected reason codes observed:

- `auth_missing`
- `whitelist_invalid`
- `rate_limited`

Rejected reason fields observed:

- `auth`
- `level`
- `sound`
- `source.id`
- `rate_limit`

Diagnostics redaction check:

- token: not present
- token file path: not present
- raw payload key: not present
- metadata key: not present
- invalid sound path: not present
- invalid sound URL: not present
- invalid source id: not echoed; diagnostics uses `sourceId=invalid_source`

## Resolved Blocker

The previous V2.1-A run failed because the Rust diagnostics rejected summary stored a JSON Schema error string for invalid `sound`, and that error included the submitted path-like value.

The bridge now maps validation failures to sanitized user-visible reasons. HTTP error responses and diagnostics rejected summaries use `reasonCode`, `reasonField`, and generic `reason` values such as `sound is not an accepted ID`, without echoing submitted paths, URLs, or invalid source IDs.

## Result

V2.1-A third-party local HTTP contract smoke passed after rejected reason sanitization.
