# V3.0 Baseline Freeze Report

status: passed  
timestamp: 2026-05-19 15:06 CST  
phase: V3.0 Phase 3.1 - V2.x Baseline Freeze & V3.0 Backlog Alignment

## Current V2.x Baseline

The current baseline is stable enough to enter V3.0 planning without changing runtime code:

- V2.0 final acceptance passed.
- macOS-first MVP remains available as a local unsigned app.
- Local HTTP API, PetEvent validation, diagnostics, `petctl notify`, safe sound feedback, workflow templates, and onboarding docs are present.
- V2.1-A local third-party HTTP contract smoke passed.
- V2.1-B real Codex CLI smoke passed with operator visual acceptance.
- Claude Code skill runtime evidence exists, but full Claude Code verification is not passed and is moved to V3.0 backlog.

## Automatic Check Evidence

| Command | Result | Notes |
| --- | --- | --- |
| `pnpm run doctor` | warn | No hard failures. WARN: no rustup, external network checks unreachable, sandbox cannot listen on `127.0.0.1:1420`. |
| `pnpm --filter @agent-desktop-pet/pet-protocol check` | pass | TypeScript check passed. |
| `pnpm --filter @agent-desktop-pet/pet-protocol test` | pass | 3 tests passed. |
| `pnpm --filter @agent-desktop-pet/petctl check` | pass | TypeScript check passed. |
| `pnpm --filter @agent-desktop-pet/petctl test` | pass | 6 tests passed. |
| `pnpm --filter desktop check` | pass | TypeScript check passed. |
| `cargo check --manifest-path apps/desktop/src-tauri/Cargo.toml` | pass | Rust check passed. |
| `pnpm --filter desktop build` | pass | Vite build passed. |
| `pnpm --filter desktop tauri build -b app` | pass | `.app` bundle generated. |

## macOS Runtime Smoke Evidence

| Scenario | Result | Notes |
| --- | --- | --- |
| Launch `.app` | pass | `open "apps/desktop/src-tauri/target/release/bundle/macos/Agent Desktop Pet.app"` returned success. |
| Health endpoint | pass | `GET /api/health` returned `ok=true`. |
| `petctl notify --level success` | pass | Accepted `eventId=evt_1779174320224_1`. |
| Diagnostics with token | pass | Returned enabled runtime, queue 0/32, accepted event, sound decision. |
| Quit app | pass | `osascript` quit succeeded; `lsof -iTCP:17321 -sTCP:LISTEN` found no listener. |
| Visual pet / drag / tray | carried forward | Previously user-confirmed in V2.0/V2.1 acceptance. This Phase 3.1 run did not add new visual smoke. |

## HTTP / PetEvent / Diagnostics Smoke Evidence

| Scenario | Result | Notes |
| --- | --- | --- |
| `GET /api/health` | pass | Returned `{"ok":true,...}`. |
| `POST /api/events` via `petctl` | pass | Success event accepted and appeared in diagnostics. |
| Diagnostics accepted summary | pass | `sourceId=custom.local`, `level=success`, title `v3 baseline freeze smoke`. |
| Diagnostics sound status | pass | `playbackAvailable=true`, `muted=false`, accepted sound IDs visible, no file paths exposed. |

## Security Boundary Smoke Evidence

| Scenario | Result | Notes |
| --- | --- | --- |
| No-token POST | pass | Returned `401 auth_missing`, generic reason, no token printed. |
| Invalid sound path | pass | Raw HTTP `sound="../../x.wav"` returned `400 whitelist_invalid`, `reasonField=sound`, generic reason. |
| Invalid sound URL | pass | Raw HTTP `sound="https://example.com/x.wav"` returned `400 whitelist_invalid`, `reasonField=sound`, generic reason. |
| Rejected diagnostics redaction | pass | Latest rejected summaries did not contain submitted path, URL, token path, `/Users/`, `/tmp/`, or `api-token.json`. |
| High-frequency requests | pass | 14 rapid requests yielded 10 accepted and 4 `429 rate_limited`. |

## Third-party HTTP Contract Regression Evidence

V2.1-A remains valid:

- `docs/V2.1/v2_1-baseline-audit.md`: `status: passed`.
- `docs/V2.1/third-party-agent-contract-report.md`: `status: passed`.
- Local HTTP examples validated curl / Node / Python success paths.
- Error paths validated 401, 400, 429, invalid sound path/URL redaction, and invalid source redaction.

This allows only:

```text
Third-party local HTTP contract smoke passed.
```

It does not allow:

```text
Third-party agent integration verified.
```

## Codex Evidence Review

Codex evidence file:

- `docs/V2.1/evidence/codex-smoke-2026-05-19.md`
- `status: passed`
- includes real `codex exec` transcript evidence.
- includes accepted diagnostics for `sourceId=codex.local`.
- covers `thinking`, `running`, `success`, `error`, and `need_input`.
- includes operator visual acceptance.

Allowed claim:

```text
V2.1-B complete: Codex local workflow integration smoke passed.
Codex local workflow integration verified for tested local Codex CLI smoke scenarios.
```

Forbidden expansion:

```text
All Codex workflows verified.
Codex MCP ready.
cross-platform Codex integration verified.
```

## Claude Code Evidence Review

Claude Code evidence file:

- `docs/V2.1/evidence/claude-code-smoke-2026-05-19.md`
- `status: blocked`
- skill runtime accepted diagnostics evidence exists for `sourceId=claude-code.local`.
- operator visual acceptance is not recorded.
- Notification hook did not trigger in tested non-interactive flows.

Allowed current statement:

```text
Claude Code skill runtime smoke produced accepted diagnostics evidence for tested local scenarios.
```

Forbidden claims:

```text
Claude Code skill workflow verified.
Claude Code hook workflow verified.
Claude Code integration verified.
```

Claude Code verification is moved to V3.0 backlog.

## Allowed Claims

```text
macOS-first MVP ready: local desktop agent status pet with HTTP + petctl integration and safe sound feedback.
V2.0 ready: local agent workflow integration and developer usability polish complete.
Codex and Claude Code local workflow templates ready.
V2.1-A complete: integration baseline audit and local third-party HTTP contract smoke ready.
Third-party local HTTP contract smoke passed.
V2.1-B complete: Codex local workflow integration smoke passed.
Codex local workflow integration verified for tested local Codex CLI smoke scenarios.
V3.0 Phase 3.1 complete: V2.x baseline frozen and complex integration backlog aligned.
```

## Forbidden Claims

```text
Claude Code integration verified
Claude Code skill workflow verified
Claude Code hook workflow verified
Third-party agent integration verified
MCP ready
Windows ready
cross-platform ready
USB ready
Rive/Live2D/3D ready
photo customization ready
production signed release ready
auto update ready
```

## Residual Risks

- Phase 3.1 visual smoke was not newly observed by the agent; it relies on previous user-confirmed visual acceptance.
- Claude Code hook behavior may require interactive Claude Code flows or version-specific configuration.
- Windows remains untested.
- MCP remains research-only.
- Local app is unsigned and not notarized.
- Network warnings can still affect first-time setup on a clean machine.

## V3.0 Backlog Summary

See `docs/V3.0/v3_0-backlog.md`.

V3.0 backlog categories:

- Claude Code skill/hook real verification.
- Real third-party product integration.
- Windows smoke / hardening.
- MCP adapter decision and possible implementation.
- USB hardware.
- Rive / Live2D / 3D.
- Photo customization.
- Production signing / notarization.
- Auto update.

## Final Go / No-go Decision

Decision: go for V3.0 planning.

The V2.x baseline is stable, the allowed/forbidden claims are frozen, and unresolved complex integrations are explicitly moved to V3.0 backlog. This does not authorize runtime development by itself; it only closes Phase 3.1 baseline freeze.
