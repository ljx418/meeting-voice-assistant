# Active Development Plan

文档状态：active index；V4.x OS-level Codex binding feasibility line。  
当前日期：2026-05-26。

## Current Active Line

V3.x 已完成 scoped acceptance，作为当前可复用基线关闭。V3.6 hook-only strategy 保留为 historical blocked evidence，不再作为 active strategy 推进。V3.7 Codex Exec JSONL Monitor 是当前已验收的可靠监听路径，但只覆盖 wrapper-launched `codex exec --json` sessions。

当前 active development line 是 V4.x：已经完成 Terminal.app scoped candidate discovery / user-confirmed binding / manual route-test prototype，并新增 V4.4 managed exec JSONL session state mapping。V4.x 仍不声明任意 already-open Codex TUI 自动监听或 OS-level binding ready。

V5.x 是后续 renderer / 3D / action asset line，不属于 V4.x OS-level binding 主线。

## Audit Sources

- `docs/active/current-vs-target-gap.md`
- `docs/active/current-vs-target-gap.drawio`
- `docs/active/acceptance-plan.md`
- `docs/V3.x/v3_x-development-plan.md`
- `docs/V3.x/v3_x-final-acceptance-report.md`
- `docs/V3.x/v3_x-codex-monitoring-strategy.md`
- `docs/V3.6/v3_6-final-acceptance-report.md`
- `docs/V3.7/v3_7-final-acceptance-report.md`
- `docs/V4.x/v4_x-development-plan.md`
- `docs/V4.x/v4_x-acceptance-plan.md`
- `docs/V4.x/v4_x-current-gap-analysis.md`
- `docs/V4.x/v4_x-claim-matrix.md`
- `docs/V4.x/v4_4-final-acceptance-report.md`
- `docs/V5.x/v5_x-development-plan.md`
- `docs/V5.x/v5_x-acceptance-plan.md`
- `docs/V5.x/v5_x-current-gap-analysis.md`
- `docs/V5.x/v5_x-claim-matrix.md`

## Closed Baseline Claims

These claims are closed V3.x baseline claims, not new V4.x readiness claims:

```text
V3.1 ready: multi-instance Codex pet workflow stabilized with user onboarding, manager polish, repeatable runtime smoke, and migration guidance.
V3.2 MCP adapter minimal smoke passed for localhost bridge routing.
V3.2 third-party contract v3 smoke passed.
V3.3 Codex window/session-to-pet binding smoke passed for tested local macOS terminal scenarios.
V3.4 Codex hook wrapper fixture smoke passed.
V3.4 Codex hooks state mapping smoke passed for tested local Codex hook scenarios.
V3.5 Codex hook diagnostics and recovery smoke passed for tested local diagnostics scenarios.
V3.6 final acceptance blocked on real PostToolUse failure evidence.
V3.6 hook-only monitoring is deprecated as an active strategy and superseded by V3.7 JSONL monitoring for supported wrapper-launched codex exec --json sessions.
V3.7 Codex exec JSONL monitor state mapping passed for tested local wrapper-launched codex exec --json scenarios.
V3.x scoped Codex local workflow acceptance passed with documented evidence and claim boundaries.
```

## Active Planning Claims

Allowed planning claims:

```text
V5.x Cat Renderer & Asset System is planned for high-quality 2D, 3D, and action asset development.
```

V4.x is no longer a planning-only line; it has scoped final acceptance evidence. V5.x remains planning-only and does not imply readiness, user distribution readiness, or OS-level binding acceptance.

## Forbidden Claims

The following remain forbidden as ready / verified / passed claims unless a later scoped phase produces explicit evidence and final acceptance:

```text
OS-level Codex window binding ready
interactive Codex TUI monitoring ready
already-open Codex window auto-detection ready
already-open Codex window auto-monitoring ready
all Codex workflows verified
Codex internal reasoning exact mapping ready
ModelThinkingStart / ModelThinkingEnd verified
V3.6 selected Codex workflow hook coverage smoke passed
PostToolUse failure hook evidence passed
Claude Code integration verified
MCP ready
Third-party agent integration verified
Windows ready
cross-platform ready
USB ready
production signed release ready
per-instance queue ready
Rive / Live2D / 3D ready
custom asset pack import ready
user asset upload ready
asset marketplace ready
```

## Current Implementation Direction

The product-supported reliable Codex monitoring path is now the managed exec JSONL wrapper entry:

```bash
node packages/petctl/dist/cli.js codex session start \
  --mode exec \
  --monitor jsonl \
  --name "Review Cat" \
  -- codex exec --json "summarize this repository"
```

This monitor:

- applies only to wrapper-launched `codex exec --json`.
- parses structured JSONL event types only.
- maps `turn.started -> thinking`, `item.started -> running`, `turn.completed -> success` if no error, and `turn.failed` / `error -> error`.
- does not parse terminal text.
- does not read `transcript_path`.
- does not record raw JSONL, prompt text, tool command text, token, Authorization, workspace path, config path, or full local paths.

Managed TUI hooks are available as a planned/manual path:

```bash
node packages/petctl/dist/cli.js codex session start \
  --mode tui \
  --monitor hooks \
  --name "TUI Cat" \
  -- codex
```

This path requires real hook trust/lifecycle evidence before any TUI state mapping claim. It is not currently accepted as ready.

## V4.5-V4.x Development Rule

V4.5 current status:

```text
V4.5 managed Codex TUI hook state mapping passed for UserPromptSubmit, PreToolUse, and Stop in tested local wrapper-launched scenario; PermissionRequest remains blocked by local policy.
```

V4.5 real managed TUI hook acceptance must continue to require:

- wrapper-launched Codex TUI.
- `/hooks` review/trust.
- real prompt submission.
- real tool use.
- real Stop event.
- permission request if local policy emits it.
- target cat changes.
- default and unrelated pets unchanged.

Preflight is not real lifecycle evidence and cannot be used to claim TUI hook state mapping passed. The accepted V4.5 claim is based on the separate real lifecycle evidence file and remains scoped to the observed hook events only.

V4.6 has implemented startup diagnostics and UX hardening:

- desktop health preflight.
- hooks config check.
- wrapper script check.
- Codex CLI check.
- clear `/hooks` trust instruction.
- stable reasonCode.

V4.7 has implemented sanitized session status:

```bash
petctl codex session status --json
```

It must not expose raw TTY, raw args, window title, path, prompt, tool command, raw hook payload, token, or Authorization.

V4.x Final must not run until V4.6 and V4.7 are accepted. Final claims must keep the V4.5 lifecycle scope explicit and must not include `PermissionRequest` unless a future local policy emits it and evidence passes.

## V5.x Development Rule

V5.x may start only after it is explicitly selected as the active line. It should own high-quality Sprite / 2D Asset Pack v2, Renderer Plugin Interface, GLTF / Three.js 3D Cat Prototype, 3D Action Asset Pack, and manifest-validated custom asset import.

V5.x work must not be mixed into V4.x feasibility evidence.
