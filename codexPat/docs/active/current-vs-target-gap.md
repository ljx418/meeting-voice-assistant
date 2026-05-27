# Current vs Target Gap

文档状态：active gap；V4.x OS-level Codex binding feasibility line。  
配套图：`current-vs-target-gap.drawio`。  
当前日期：2026-05-26。

## Active Line

```text
Current active line: V4.x OS-level Codex window/session binding feasibility.
V3.x status: closed scoped baseline.
V5.x status: planned future renderer / asset line.
```

V3.x 不再是当前开发主线。V3.x 只作为已验收基线和回归约束存在。

## Closed Baseline Summary

| Baseline | Status | Notes |
| --- | --- | --- |
| macOS-first desktop pet | passed | Tauri 桌面猫、透明窗口、拖拽、托盘、设置页。 |
| PetEvent / HTTP / petctl | passed | token、白名单、rate limit、diagnostics、safe sound。 |
| V3.1 stabilization | passed | onboarding、Manager polish、runtime smoke、migration guidance。 |
| V3.2 scoped integration | passed scoped | MCP adapter minimal smoke、third-party contract v3；不代表 MCP ready。 |
| V3.3 Codex binding | passed scoped | wrapper-first `petctl codex launch` binding；不代表 OS-level binding。 |
| V3.4 hooks mapping | passed scoped | tested local Codex hook scenarios；不代表 exact internal reasoning。 |
| V3.5 diagnostics | passed scoped | `petctl codex doctor` 和 recovery smoke。 |
| V3.6 hook-only failure mapping | historical blocked / deprecated | `PostToolUse` payload 无稳定 failure fields；不再作为 active strategy。 |
| V3.7 JSONL monitor | passed scoped / current recommended exec path | wrapper-launched `codex exec --json`；不覆盖 interactive TUI 或 OS-level window binding。 |
| V3.x final | passed scoped | evidence / claim / PRD / security / regression 收口。 |

V3.x 允许的核心声明：

```text
V3.x scoped Codex local workflow acceptance passed with documented evidence and claim boundaries.
V3.7 Codex exec JSONL monitor state mapping passed for tested local wrapper-launched codex exec --json scenarios.
V3.6 hook-only monitoring is deprecated as an active strategy and superseded by V3.7 JSONL monitoring for supported wrapper-launched codex exec --json sessions.
```

## V4.x Active Gap

V4.x 处理 V3.x 明确不覆盖的用户诉求：

```text
Already-running or active Codex terminal window -> explicit user-confirmed pet binding.
```

| Gap | Current | Target | Status |
| --- | --- | --- | --- |
| Already-running Codex discovery | Not implemented. V3.7 requires wrapper-launched `codex exec --json`. | Feasibility audit for active window / session candidate discovery only. | V4.0 accepted feasibility |
| State event source for already-running sessions | OS-level discovery does not provide lifecycle events. | Hooks/registry/wrapper relaunch are the only plausible safe sources; discovery alone is no-go for routing. | V4.0 accepted feasibility |
| Existing session env injection | Not supported. | If `AGENT_DESKTOP_PET_INSTANCE_ID` cannot be injected, user must relaunch through V3.7 wrapper or future registry path. | V4.0 accepted feasibility |
| macOS permission model | Feasibility model documented. | Accessibility / automation permissions must be opt-in and scoped before V4.1. | V4.0 accepted feasibility |
| Terminal app matrix | Feasibility matrix completed. | Terminal.app and iTerm2 are first V4.1 safe-field probe candidates; VS Code/Warp/Ghostty remain deferred/no-go without app-specific support. | V4.0 accepted feasibility |
| Safe identity fields | Field boundary defined. | Only safe session hints; no terminal text, prompt, command, workspace path, full local path. | V4.0 accepted feasibility |
| Active window probe | CLI implementation built and unit-tested, including Node-packaged Codex CLI detection. Terminal.app runtime evidence passed in the tested local environment. | V4.2 may plan from Terminal.app-only evidence; iTerm2/all-terminal support remains unproven. | V4.1 passed-terminal-app |
| User-confirmed binding | CLI implementation built, unit-tested, and runtime accepted for Terminal.app candidate-to-PetInstance binding UX. | Two-step preview / confirm flow, stale-aware binding record, Terminal.app-only candidate-to-PetInstance association. | V4.2 passed Terminal.app-only |
| Manual route-test | CLI implementation built, unit-tested, and runtime accepted for Terminal.app manual route-test. | Revalidated binding can send an explicit manual test event only to the bound PetInstance. | V4.3 passed Terminal.app-only |
| Managed exec JSONL state mapping | `petctl codex session start --mode exec --monitor jsonl` implemented and runtime accepted. | Wrapper-launched Codex exec session can create one cat and map structured state to that cat. | V4.4 passed scoped exec JSONL |
| Managed TUI hooks state mapping | V4.5 wrapper preflight passed. Real Codex TUI hook lifecycle passed for `UserPromptSubmit -> thinking`, `PreToolUse -> running`, and `Stop -> success` in the tested wrapper-launched local scenario. `PermissionRequest` was not observed because local policy did not emit it. | Requires managed wrapper launch and trusted project hooks. Does not cover already-open Codex windows, OS-level lifecycle monitoring, or all hook events. | V4.5 passed scoped / PermissionRequest not observed |
| V4.6 UX hardening | Implemented and accepted for startup diagnostics. | Desktop health preflight, hook config check, wrapper check, Codex CLI check, stable reasonCode, and clear `/hooks` trust instruction. | V4.6 passed |
| V4.7 session status | Implemented and accepted for managed wrapper-launched sessions. | Sanitized `petctl codex session status --json` with redacted binding/session fields only. | V4.7 passed |
| Lifecycle routing | Not implemented. OS discovery is not an event source. | Remains unsupported unless a trusted event source is added later; use V3.7 wrapper path for reliable monitoring. | no-go from OS discovery alone |
| Unsupported terminal handling | Not implemented. | Unsupported apps fail safely and are not counted as passed. | planned |
| V4.x final acceptance | V4.0-V4.7 scoped final completed. | Managed session mapping and Terminal.app binding prototype accepted with scoped claims and no OS-level or all-workflow expansion. | V4.x final passed scoped |

V4.x must not treat candidate window discovery as Codex lifecycle monitoring. If no safe event source exists for an already-running Codex session, the accepted fallback is to prompt the user to relaunch through the managed wrapper path.

V4.5 preflight is not real hook lifecycle evidence. The scoped V4.5 lifecycle acceptance used a real wrapper-launched Codex TUI session after `/hooks` review/trust and observed real hook-driven state changes. `PermissionRequest` remains not-passed for this local run.

## V5.x Future Gap

V5.x is a separate future line, not the active V4.x binding work.

| Gap | Current | Target | Status |
| --- | --- | --- | --- |
| Asset system freeze | Reference design only. | Manifest, action mapping, fallback, security rules. | planned V5.0 |
| High-quality 2D actions | CSS profiles / Asset Pack v1 only. | Sprite / 2D Asset Pack v2 for core states. | planned V5.1 |
| Renderer plugin interface | Not implemented. | CSS / sprite / GLTF / Rive / Live2D abstraction. | planned V5.2 |
| GLTF / Three.js 3D prototype | Not implemented. | Bundled GLB/GLTF renderer prototype. | planned V5.3 |
| 3D action clips | Not implemented. | Bundled clips for core pet states. | planned V5.4 |
| Custom asset import | Forbidden today. | Manifest-validated local import after bundled assets pass. | future V5.5 |

## Planning Claims

Allowed planning claims:

```text
V4.x OS-level Codex window/session binding is planned for feasibility review.
V4.6 managed session startup diagnostics and UX hardening passed for tested local wrapper-launched scenarios.
V4.7 managed session status and stale-binding diagnostics passed for tested local wrapper-launched scenarios.
V5.x Cat Renderer & Asset System is planned for high-quality 2D, 3D, and action asset development.
```

## Forbidden Claims

Forbidden as ready / passed:

```text
OS-level Codex window binding ready
interactive Codex TUI monitoring ready
already-open Codex window auto-detection ready
already-open Codex window auto-monitoring ready
all Codex workflows verified
Codex internal reasoning exact mapping ready
MCP ready
Third-party agent integration verified
Claude Code integration verified
Windows ready
cross-platform ready
USB ready
production signed release ready
per-instance queue ready
Rive / Live2D / 3D ready
photo customization ready
user asset upload ready
remote asset download ready
custom asset pack import ready
asset marketplace ready
```

## Audit Files

Current active docs:

- `docs/active/development-plan.md`
- `docs/active/acceptance-plan.md`
- `docs/active/current-vs-target-gap.md`
- `docs/active/current-vs-target-gap.drawio`

V4.x planning:

- `docs/V4.x/v4_x-development-plan.md`
- `docs/V4.x/v4_x-acceptance-plan.md`
- `docs/V4.x/v4_x-current-gap-analysis.md`
- `docs/V4.x/v4_x-claim-matrix.md`
- `docs/V4.x/v4_0-development-plan.md`
- `docs/V4.x/v4_0-acceptance-plan.md`
- `docs/V4.x/v4_0-prd-spec-review.md`
- `docs/V4.x/v4_0-plan-audit.md`
- `docs/V4.x/v4_0-os-binding-feasibility-review.md`
- `docs/V4.x/v4_1-development-plan.md`
- `docs/V4.x/v4_1-acceptance-plan.md`
- `docs/V4.x/v4_1-prd-spec-review.md`
- `docs/V4.x/v4_1-plan-audit.md`
- `docs/V4.x/evidence/v4_1-safe-field-probe-2026-05-26.md`
- `docs/V4.x/v4_1-final-acceptance-report.md`

V5.x future planning:

- `docs/V5.x/v5_x-development-plan.md`
- `docs/V5.x/v5_x-acceptance-plan.md`
- `docs/V5.x/v5_x-current-gap-analysis.md`
- `docs/V5.x/v5_x-claim-matrix.md`

V3.x closed baseline:

- `docs/V3.x/v3_x-final-acceptance-report.md`
- `docs/V3.x/v3_x-codex-monitoring-strategy.md`
- `docs/V3.7/v3_7-final-acceptance-report.md`
- `docs/V3.6/v3_6-final-acceptance-report.md`
