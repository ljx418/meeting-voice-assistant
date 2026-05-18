# V2.0 Final Acceptance Report

status: passed  
timestamp: 2026-05-18 11:14:34 CST  
version: V2.0 Developer Workflow Integration Release

## 1. V2.0 Positioning

V2.0 upgrades agent-desktop-pet from a macOS-first local Agent status pet MVP into a developer workflow integration release that can be used by local scripts, `petctl`, and instruction templates while preserving the V1.0 safety boundary.

It remains a low-interruption desktop feedback layer. It is not a notification center, chat bot, production signed release, Windows-ready release, MCP server, USB hardware release, or high-fidelity animation/runtime release.

## 2. Completed Phases

| Phase | Name | Status | Deliverables |
| --- | --- | --- | --- |
| Phase 2.1 | Workflow Integration Templates | passed | Codex template, Claude Code template, agent integration guide, `petctl` recipes, shell example, Node example. |
| Phase 2.2 | Settings & Diagnostics Polish | passed | Runtime health, sound diagnostics, accepted/rejected summaries, quick commands, no sensitive payload display. |
| Phase 2.3 | Cat Experience Polish | passed | CSS placeholder cat state polish for idle/thinking/running/success/warning/error/need_input/sleeping. |
| Phase 2.4 | Distribution Readiness | passed | README quick start, macOS local unsigned app guide, troubleshooting, network/setup docs, token/config docs. |

## 3. Acceptance Evidence Table

| Command / scenario | Result | Timestamp | Notes |
| --- | --- | --- | --- |
| `pnpm run doctor` | warn | 2026-05-18 11:14 CST | No hard failures. WARN: rustup missing, external network checks failed, sandbox could not listen on 127.0.0.1:1420. Existing cached build path was not blocked. |
| `pnpm --filter @agent-desktop-pet/pet-protocol check` | pass | 2026-05-18 11:14 CST | TypeScript check passed. |
| `pnpm --filter @agent-desktop-pet/pet-protocol test` | pass | 2026-05-18 11:14 CST | 3 tests passed. |
| `pnpm --filter @agent-desktop-pet/petctl check` | pass | 2026-05-18 11:14 CST | TypeScript check passed. |
| `pnpm --filter @agent-desktop-pet/petctl test` | pass | 2026-05-18 11:14 CST | 6 tests passed. |
| `pnpm --filter desktop check` | pass | 2026-05-18 11:14 CST | TypeScript check passed. |
| `pnpm --filter desktop build` | pass | 2026-05-18 11:14 CST | Vite build passed. |
| `cargo check --manifest-path apps/desktop/src-tauri/Cargo.toml` | pass | 2026-05-18 11:14 CST | Rust check passed. |
| `pnpm --filter desktop tauri build -b app` | pass | 2026-05-18 11:14 CST | `.app` bundle generated. |
| Start `.app` | pass | 2026-05-18 11:14 CST | App started; `127.0.0.1:17321` was listening. |
| Desktop cat visible / transparent / draggable / tray settings | pass | 2026-05-18 11:14 CST | User-confirmed during Phase 2.4 acceptance. |
| `curl -sS http://127.0.0.1:17321/api/health` | pass | 2026-05-18 11:14 CST | Returned `ok: true`. |
| `node packages/petctl/dist/cli.js notify --level success --title "v2 final smoke"` | pass | 2026-05-18 11:14 CST | Accepted with eventId. |
| Cat entered success | pass | 2026-05-18 11:14 CST | User-confirmed visual behavior in current acceptance flow. |
| Diagnostics accepted event | pass | 2026-05-18 11:14 CST | Diagnostics showed `custom.local`, `node.local`, and `script.local` accepted summaries. |
| No-token `POST /api/events` | pass | 2026-05-18 11:14 CST | Returned `401 auth_missing`. |
| Invalid sound path | pass | 2026-05-18 11:14 CST | `../../x.wav` rejected locally; no accepted event. V2.1-A later verified HTTP response and diagnostics redaction with `reasonField=sound`. |
| Shell example success | pass | 2026-05-18 11:14 CST | `examples/shell/task-with-pet.sh -- true` exited 0 and diagnostics showed `script.local` success. |
| Shell example failure | pass | 2026-05-18 11:14 CST | `examples/shell/task-with-pet.sh -- false` exited 1 and diagnostics showed `script.local` error. |
| Node example success | pass | 2026-05-18 11:14 CST | Passed when `petctl` bin was available on PATH through temporary smoke wrapper; diagnostics showed `node.local`. |
| Settings diagnostics queue / accepted / rejected / sound decision | pass | 2026-05-18 11:14 CST | Diagnostics returned queue 0/32, accepted/rejected summaries, sound decision. |
| CSS states running/success/error/need_input | pass | 2026-05-18 11:14 CST | User-confirmed no black frame and no visible size jitter during Phase 2.3/2.4 acceptance. |
| Quit app and confirm port closed | pass | 2026-05-18 11:14 CST | `lsof -iTCP:17321 -sTCP:LISTEN` returned no listener. |
| README / active / V2.0 docs consistency | pass | 2026-05-18 11:14 CST | Updated in this closure. |
| Markdown gap and drawio sync | pass | 2026-05-18 11:14 CST | Active and V2.0 gap drawio updated. |

## 4. Automatic Check Results

All hard check/test/build commands passed.

`pnpm run doctor` completed with no hard failures. The remaining WARN items are environment-related and non-blocking for the cached local build path:

- `rustup` is not installed; current Homebrew Rust matches the required `1.95.0`.
- External network checks for npm, crates.io, and rustup were not reachable from this environment.
- The sandbox could not listen on `127.0.0.1:1420`; the built `.app` and API smoke were not blocked.

## 5. macOS Smoke Results

macOS smoke passed for the final acceptance scope:

- `.app` launched.
- Local API listened on `127.0.0.1:17321`.
- Health endpoint returned ok.
- `petctl` success event was accepted.
- Unauthorized write was rejected with 401.
- Invalid sound path was rejected.
- V2.1-A follow-up verified rejected reason sanitization: diagnostics and HTTP errors do not echo illegal sound paths, URLs, or invalid source IDs.
- Shell and Node examples produced accepted summaries.
- Diagnostics showed queue, accepted/rejected events, and sound decision.
- App exit removed the `17321` listener.

The visual desktop cat checks were confirmed by the user during Phase 2.3/2.4 acceptance.

## 6. User Acceptance

User acceptance for Phase 2.4 was explicitly confirmed with: “验收ok”.

The final closure uses that acceptance together with the fresh automatic checks and smoke tests in this report.

## 7. Documentation Consistency

The following documentation sets are aligned:

- README quick entry.
- `docs/active/*`.
- `docs/V2.0/*`.
- Active gap markdown and drawio.
- V2.0 gap markdown and drawio.
- Docs map.

No false-green claim was added for Windows, cross-platform readiness, production signing, MCP, USB, Rive/Live2D/3D, or photo customization.

## 8. Not Implemented

V2.0 does not implement:

- Codex integration verified.
- Claude Code integration verified.
- Windows ready.
- cross-platform ready.
- production signed release.
- notarization.
- auto update.
- MCP server.
- USB.
- Rive / Live2D / 3D.
- photo customization.
- new SDK.
- new PetEvent protocol fields.
- new CatStateMachine behavior.
- new petctl parameters.

## 9. Allowed Claims

The following claims are now allowed:

```text
V2.0 ready: local agent workflow integration and developer usability polish complete.
Codex and Claude Code local workflow templates ready.
```

## 10. Forbidden Claims

The following claims remain forbidden:

```text
Codex integration verified
Claude Code integration verified
Windows ready
cross-platform ready
production signed release ready
auto update ready
MCP ready
USB ready
Rive/Live2D/3D ready
photo customization ready
```

## 11. Residual Risks

- Codex and Claude Code templates are ready, but real tool-specific integration has not been independently verified.
- The macOS app is a local unsigned app; it is not signed, notarized, or production-distributed.
- Windows remains unvalidated.
- Node example assumes a `petctl` executable is available on `PATH`; local smoke used a temporary wrapper around the built CLI.
- Network access can still affect first-time setup on a clean machine.

## 12. Next Version Recommendations

Recommended next planning tracks:

- V2.1 / V3.0 Windows hardening and smoke.
- Production signing, notarization, and release packaging.
- Optional MCP server adapter.
- Optional real Codex / Claude Code integration verification.
- Optional richer cat renderer track: Rive / Live2D / 3D.
- Optional USB hardware integration track.
