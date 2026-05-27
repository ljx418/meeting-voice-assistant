# V3.4 Codex Hooks Design

文档状态：implemented for wrapper and fixture smoke.

## Hook Configuration

Project config:

```text
.codex/hooks.json
```

Registered hooks:

- `SessionStart`
- `UserPromptSubmit`
- `PreToolUse`
- `PermissionRequest`
- `PostToolUse`
- `Stop`

`PreCompact`, `PostCompact`, `SubagentStart`, and `SubagentStop` are recognized by the wrapper as safe no-op events but are not part of the V3.4 ready claim.

Codex 0.131 expects each event entry to contain a matcher group with a nested `hooks` array. A direct event-to-command object is not installed and will show `Installed 0 / Active 0` in `/hooks`.

Expected shape:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": ".*",
        "hooks": [
          {
            "type": "command",
            "command": "node scripts/codex-pet-hook.mjs PreToolUse",
            "timeout": 5
          }
        ]
      }
    ]
  }
}
```

## Wrapper

Wrapper:

```text
scripts/codex-pet-hook.mjs
```

Behavior:

- reads event name from argv.
- reads stdin JSON but never prints raw stdin.
- no-ops if `AGENT_DESKTOP_PET_INSTANCE_ID` is missing or invalid.
- calls `node packages/petctl/dist/cli.js notify`.
- relies on env instance routing.
- emits only `{}` on stdout.
- emits redacted debug only when `CODEX_PET_HOOK_DEBUG=1`.

## Mapping

| Hook | Level | Title |
| --- | --- | --- |
| `SessionStart` | `running` | `Codex session started` |
| `UserPromptSubmit` | `thinking` | `Codex thinking` |
| `PreToolUse` | `running` | `Codex tool running` |
| `PermissionRequest` | `need_input` | `Codex needs approval` |
| `PostToolUse` failure | `error` | `Codex tool failed` |
| `Stop` | `success` | `Codex turn completed` |

## Failure Detection

`PostToolUse` maps to `error` only when a stable failure signal exists:

- nonzero `exitCode` or `exit_code`.
- `success === false`.
- `status` is `error`, `failed`, or `failure`.
- non-empty `error` field.

If failure cannot be determined, the wrapper no-ops.

## Cooldown / Dedupe

Cooldown key:

```text
instanceId + hookEvent + level
```

Default windows:

| Event | Cooldown |
| --- | --- |
| `SessionStart` | 1000ms |
| `UserPromptSubmit` | 500ms |
| `PreToolUse` | 1500ms |
| `PermissionRequest` | 0ms |
| `PostToolUse` | 0ms |
| `Stop` | 800ms |

Cooldown state is stored in the OS temp directory and is never printed in evidence.

## Security

The wrapper never sends prompt text, tool command, transcript path, config path, workspace path, URL, token, Authorization header, or raw payload in PetEvent metadata.

Allowed metadata:

- `hookEvent`
- `codexBinding=hooks`
- `mappingVersion=v3.4`
- `failureDetected=true/false`
