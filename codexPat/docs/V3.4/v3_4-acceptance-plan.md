# V3.4 Acceptance Plan

文档状态：active.

## Acceptance Gates

### Gate 1：Fixture Hook Wrapper Smoke

Command:

```bash
node scripts/v3_4_codex_hook_fixture_smoke.mjs
```

Must pass:

- `SessionStart -> running`
- `UserPromptSubmit -> thinking`
- `PreToolUse -> running`
- `PermissionRequest -> need_input`
- `PostToolUse` failure -> `error`
- `Stop -> success`
- missing `AGENT_DESKTOP_PET_INSTANCE_ID` no-ops safely
- no raw hook stdin or sensitive output

Allowed claim after this gate only:

```text
V3.4 Codex hook wrapper fixture smoke passed.
```

### Gate 2：Real Codex Hook Lifecycle Smoke

Command:

```bash
node scripts/v3_4_codex_hook_real_lifecycle_smoke.mjs
```

Preconditions:

- desktop app running.
- `petctl` built.
- `.codex/hooks.json` present.
- operator reviewed and trusted hooks through `/hooks`.

If hook trust is missing, this gate must be `blocked`, not passed.

Allowed claim after this gate passes:

```text
V3.4 Codex hooks state mapping smoke passed for tested local Codex hook scenarios.
```

## Regression Gates

Run before final closure:

```bash
node scripts/v3_3_codex_window_binding_smoke.mjs
node scripts/v3_1_runtime_smoke.mjs
node scripts/v3_2_mcp_adapter_smoke.mjs
node scripts/v3_2_third_party_contract_smoke.mjs
pnpm --filter @agent-desktop-pet/pet-protocol check
pnpm --filter @agent-desktop-pet/pet-protocol test
pnpm --filter @agent-desktop-pet/petctl check
pnpm --filter @agent-desktop-pet/petctl test
pnpm --filter @agent-desktop-pet/pet-mcp check
pnpm --filter @agent-desktop-pet/pet-mcp test
pnpm --filter desktop check
cargo check --manifest-path apps/desktop/src-tauri/Cargo.toml
pnpm --filter desktop build
```

## Security Gate

Evidence and smoke output must not include:

- token.
- Authorization header.
- raw hook stdin.
- raw payload.
- prompt text.
- tool input command.
- transcript path.
- config path.
- workspace path.
- full local path.

## Pass Rule

V3.4 final acceptance can pass only if real Codex hook lifecycle evidence passes. Fixture smoke alone is not enough.
