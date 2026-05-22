# V3.1 Final Acceptance Report

status: passed

date: 2026-05-22

commit: 96b6a393
auditRecheckedAt: 2026-05-22 Asia/Shanghai

## V3.1 Scope

V3.1 是 V3.0 多实例 Codex 桌宠工作流之后的稳定化与用户上手收口阶段。它覆盖文档收口、多 Codex 用户流程、Manager UI usability polish、runtime regression harness、本地迁移和备份说明。

本阶段不新增产品功能，不修改 PetEvent schema，不重写 Rust bridge、CatStateMachine 或 `petctl` 参数语义。

## Completed Phases

| Phase | Scope | Evidence | Result |
| --- | --- | --- | --- |
| V3.0 baseline | Multi-instance Codex desktop pet workflow final acceptance | `docs/V3.0/v3_0-final-acceptance-report.md` | passed |
| V3.1 Phase 1 | V3.0 Release Freeze & Documentation Cleanup | active docs state | passed |
| V3.1 Phase 2 | Multi-Codex User Workflow Guide | `docs/reference/multi-codex-workflow.md` and active docs state | passed |
| V3.1 Phase 3 | Manager UI Usability Polish | `docs/V3.1/evidence/manager-ui-polish-2026-05-20.md` | passed |
| V3.1 Phase 4 | Runtime Regression Harness | `docs/V3.1/evidence/runtime-regression-harness-2026-05-21.md` | passed |
| V3.1 Phase 5 | Local App Migration and Backup | `docs/V3.1/evidence/local-app-migration-backup-2026-05-21.md` | passed |

## Evidence Gate

| Evidence | Status | Notes |
| --- | --- | --- |
| `docs/V3.0/v3_0-final-acceptance-report.md` | passed | V3.0 ready is limited to tested local Codex session scenarios. |
| V3.1 Phase 1 active docs | passed | README/docs map and V3.0 release evidence references are present. |
| V3.1 Phase 2 active docs / workflow guide | passed | Multi-Codex workflow guide exists and active acceptance marks the phase passed. |
| `docs/V3.1/evidence/manager-ui-polish-2026-05-20.md` | passed | Operator confirmed Manager UI checklist passed on 2026-05-22. |
| `docs/V3.1/evidence/runtime-regression-harness-2026-05-21.md` | passed | Freeze audit re-run passed on 2026-05-22, run id `1779438063505-3601c8`. |
| `docs/V3.1/evidence/local-app-migration-backup-2026-05-21.md` | passed | Freeze audit config audit re-run passed on 2026-05-22. |

## Automatic Checks

| Command | Result | Notes |
| --- | --- | --- |
| `pnpm run doctor` | pass-with-warn | No hard failure. WARN: rustup missing; network probes unreachable; sandbox local dev server listen EPERM. |
| `pnpm --filter @agent-desktop-pet/pet-protocol check` | passed | TypeScript check passed. |
| `pnpm --filter @agent-desktop-pet/pet-protocol test` | passed | 3 tests passed. |
| `pnpm --filter @agent-desktop-pet/petctl check` | passed | TypeScript check passed. |
| `pnpm --filter @agent-desktop-pet/petctl test` | passed | 18 tests passed. |
| `pnpm --filter desktop check` | passed | `tsc --noEmit` passed. |
| `cargo check --manifest-path apps/desktop/src-tauri/Cargo.toml` | passed | Rust check passed. |
| `pnpm --filter desktop build` | passed | Vite production build passed. |
| `pnpm --filter desktop tauri build -b app` | passed | `.app` generated at `apps/desktop/src-tauri/target/release/bundle/macos/Agent Desktop Pet.app`. |

## Runtime Smoke Result

| Item | Result | Notes |
| --- | --- | --- |
| `node scripts/v3_1_runtime_smoke.mjs` | passed | Freeze audit run id `1779438063505-3601c8`. |
| preExistingInstanceCount | 3 | Existing user instances were preserved. |
| createdSmokeInstances | 9 | Temporary Smoke instances were created for A/B and hard limit coverage. |
| cleanupResult | passed | All temporary Smoke instances were detached. |
| legacy route | passed | Legacy notify routed to default only. |
| instance route | passed | A/B instance routes remained isolated. |
| unknown / invalid instance | passed | Returned safe 404 / 400 errors. |
| invalid sound redaction | passed | Sensitive path input was not echoed in script summary. |
| hard limit | passed | 13th pet was rejected with `instance_limit_reached`. |

## Config Audit Result

| Command | Result | Notes |
| --- | --- | --- |
| `node scripts/v3_1_config_audit.mjs` | passed | Printed redacted config summary only. |
| `node scripts/v3_1_config_audit.mjs --json` | passed | JSON output remained redacted. |

Observed summary:

| Field | Value |
| --- | --- |
| configDir | `~/Library/Application Support/com.agentdesktoppet.desktop` |
| settings.exists | true |
| settings.petInstanceCount | 2 |
| settings.hasMuted | true |
| settings.hasProfiles | true |
| tokenFile.exists | true |
| tokenValuePrinted | false |
| rawSettingsPrinted | false |
| fullUserPathPrinted | false |
| authorizationHeaderPrinted | false |

## Manager UI Acceptance Result

| Item | Result | Notes |
| --- | --- | --- |
| Manager UI manual acceptance | passed | Operator confirmed the full V3.1 final manual acceptance checklist passed. |
| V3.1 ready gate | passed | All required evidence is passed. |

## Documentation Consistency Result

| Area | Result | Notes |
| --- | --- | --- |
| README | passed | Declares V3.1 ready based on this passed final report and links to the report. |
| active docs | passed | Current gap marks V3.1 final acceptance passed and preserves forbidden claims. |
| drawio | passed | Diagram marks V3.1 ready and preserves forbidden claims. |
| migration docs | passed | Config path and local unsigned app boundaries are consistent. |
| multi-codex workflow guide | passed | Guide exists and matches final V3.1 scope. |

## Claim Consistency Result

V3.1 ready is allowed because this report is `passed`.

2026-05-22 Freeze Evidence Audit scan result:

| Scan target | Result | Notes |
| --- | --- | --- |
| `Windows ready` | passed | Only appears in forbidden / deferred / non-goal contexts. |
| `cross-platform ready` | passed | Only appears in forbidden / deferred / non-goal contexts. |
| `MCP ready` | passed | Only appears in forbidden / research / non-goal contexts. |
| `USB ready` | passed | Only appears in forbidden / deferred / non-goal contexts. |
| `production signed release ready` | passed | Only appears in forbidden / non-goal contexts. |
| `notarized release ready` | passed | Only appears in forbidden / non-goal contexts. |
| `auto update ready` | passed | Only appears in forbidden / non-goal contexts. |
| `OS-level Codex window binding ready` | passed | Only appears in forbidden / non-goal contexts. |
| `all Codex workflows verified` | passed | Only appears in forbidden / non-goal contexts. |
| `Claude Code integration verified` | passed | Only appears in forbidden / deferred contexts. |
| `per-instance queue ready` | passed | Only appears in forbidden / non-goal contexts. |
| `Rive / Live2D / 3D ready` | passed | Only appears in forbidden / deferred contexts. |
| `photo customization ready` | passed | Only appears in forbidden / deferred contexts. |

Allowed current claims remain:

```text
macOS-first MVP ready: local desktop agent status pet with HTTP + petctl integration and safe sound feedback.
V2.0 ready: local agent workflow integration and developer usability polish complete.
Third-party local HTTP contract smoke passed.
Codex local workflow integration verified for tested local Codex CLI smoke scenarios.
V3.0 ready: multi-instance Codex desktop pet workflow ready for tested local Codex session scenarios.
V3.1 planning ready: stabilization, onboarding, runtime smoke, and migration cleanup can start from the V3.0 accepted baseline.
V3.1 Phase 4 complete: repeatable runtime regression smoke ready.
V3.1 Phase 5 complete: local app migration and backup guidance ready.
V3.1 ready: multi-instance Codex pet workflow stabilized with user onboarding, manager polish, repeatable runtime smoke, and migration guidance.
```

## Forbidden Claims

```text
Windows ready
cross-platform ready
MCP ready
USB ready
production signed release ready
notarized release ready
auto update ready
OS-level Codex window binding ready
all Codex workflows verified
Claude Code integration verified
per-instance queue ready
Rive / Live2D / 3D ready
photo customization ready
```

## Remaining Risks

- Phase 1 and Phase 2 are passed through active docs and guide review, but do not have separate evidence files.
- Runtime smoke does not replace GUI visual acceptance.
- Windows, production signing, notarization, MCP and Claude Code full verification remain outside this release.

## Final Decision

V3.1 final acceptance passed.

All required evidence for V3.1 final acceptance is passed. Automatic checks, runtime smoke, config audit, Phase 1 docs cleanup, Phase 2 workflow guide review and Manager UI operator acceptance passed.

Allowed final claim:

```text
V3.1 ready: multi-instance Codex pet workflow stabilized with user onboarding, manager polish, repeatable runtime smoke, and migration guidance.
```
