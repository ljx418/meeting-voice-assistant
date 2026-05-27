# Codex Hook Real Lifecycle Smoke Evidence

date: 2026-05-25

status: passed

## Command

```bash
node scripts/v3_4_codex_hook_real_lifecycle_smoke.mjs
```

## Observed Result

| Case | Result | Notes |
| --- | --- | --- |
| Codex CLI available | passed | `codex-cli 0.131.0` |
| petctl dist exists | passed | present |
| project hook config exists | passed | present |
| Codex hook config installed | passed | `/hooks` no longer shows Installed 0 / Active 0 after `.codex/hooks.json` schema fix |
| Codex hook trust review | passed | operator reviewed and trusted hooks through `/hooks` |
| Bound Codex session | passed | session launched through `petctl codex launch`; hooks routed through `AGENT_DESKTOP_PET_INSTANCE_ID` |
| Hook-driven desktop pet state sync | passed | operator confirmed Codex can sync status to the desktop pet |

## State Mapping Evidence

Operator acceptance confirmed that Codex currently syncs state to the desktop pet through project hooks.

Observed mapping scope:

| Mapping | Result |
| --- | --- |
| `UserPromptSubmit -> thinking` | passed |
| `PreToolUse -> running` | passed |
| `Stop -> success` | passed |
| hook routing to bound cat instance | passed |
| no cross-instance routing observed | passed |

`PermissionRequest -> need_input` and `PostToolUse failure -> error` remain within V3.4 supported mapping, but should be rechecked in future regression if the local Codex approval policy or tool failure payload changes.

## Security

Operator acceptance did not report token, Authorization header, raw hook stdin, raw payload, tool input command, transcript path, config path, workspace path, or full local path leakage from the hook wrapper.

## Allowed Claim

```text
V3.4 Codex hooks state mapping smoke passed for tested local Codex hook scenarios.
```
