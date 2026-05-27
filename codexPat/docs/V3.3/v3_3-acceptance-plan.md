# V3.3 Acceptance Plan

文档状态：final；Codex window/session binding acceptance.

## Acceptance Scope

V3.3 只验收 tested local macOS terminal scenarios 下的 Codex window/session-to-pet binding。

不验收：

- Claude Code hook。
- 第三方产品集成。
- MCP ready。
- Windows / cross-platform。
- production signed release。
- 未受控 OS 级窗口句柄绑定。

## Required Evidence

必须有：

- `docs/V3.3/v3_3-codex-window-binding-design.md`
- `scripts/v3_3_codex_window_binding_smoke.mjs`
- `docs/V3.3/evidence/codex-window-binding-smoke-2026-05-24.md`
- `docs/V3.3/v3_3-final-acceptance-report.md`

## Runtime Gate

`node scripts/v3_3_codex_window_binding_smoke.mjs` 必须通过。

必测：

- `GET /api/health` returns `ok`。
- `petctl codex launch` 创建 Codex instance。
- wrapper 注入 `AGENT_DESKTOP_PET_INSTANCE_ID`。
- 子进程内 `petctl notify` 默认走 env instance route。
- 成功子进程最终进入 `success`。
- 失败子进程最终进入 `error`。
- 两个会话互不串猫。
- cleanup detach smoke instances。

如果 desktop app 未运行，status 必须是 `blocked`，不能写成 passed。

## Security Gate

evidence / smoke output 不得包含：

- token。
- Authorization header。
- raw payload。
- config path。
- workspace path。
- 完整 `/Users/...` 本地路径。
- `/dev/ttys...` 原始 tty path。
- `api-token.json`。

## Regression Gate

V3.3 scoped implementation gate：

```bash
pnpm --filter @agent-desktop-pet/petctl check
pnpm --filter @agent-desktop-pet/petctl test
pnpm --filter @agent-desktop-pet/petctl build
node scripts/v3_3_codex_window_binding_smoke.mjs
```

Release closure 前仍需复跑：

```bash
node scripts/v3_1_runtime_smoke.mjs
node scripts/v3_2_mcp_adapter_smoke.mjs
node scripts/v3_2_third_party_contract_smoke.mjs
pnpm run doctor
pnpm --filter @agent-desktop-pet/pet-protocol check
pnpm --filter @agent-desktop-pet/pet-protocol test
pnpm --filter @agent-desktop-pet/pet-mcp check
pnpm --filter @agent-desktop-pet/pet-mcp test
pnpm --filter desktop check
cargo check --manifest-path apps/desktop/src-tauri/Cargo.toml
pnpm --filter desktop build
pnpm --filter desktop tauri build -b app
```

## Pass Rule

V3.3 scoped acceptance 可通过，当且仅当：

- Codex binding smoke passed。
- `petctl` check/test/build passed。
- no security leakage。
- no forbidden claim used as ready。

Allowed claim:

```text
V3.3 Codex window/session-to-pet binding smoke passed for tested local macOS terminal scenarios.
```
