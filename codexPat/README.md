# agent-desktop-pet

`agent-desktop-pet` 是一只可常驻桌面的开发者猫，用来把 Codex、Claude Code 和自定义 AI Agent 的后台状态转译为低打扰、可感知的桌面反馈。

它不是通用桌面宠物，不是通知中心，也不是聊天机器人。

## Current Status

当前可以声明：

- `macOS-first MVP ready: local desktop agent status pet with HTTP + petctl integration and safe sound feedback.`
- `V2.0 Phase 2.1 complete: local workflow integration templates and petctl recipes ready.`
- `V2.0 Phase 2.2 complete: settings diagnostics polish ready.`
- `V2.0 Phase 2.3 complete: CSS placeholder cat experience polish ready.`
- `V2.0 Phase 2.4 complete: macOS distribution readiness and user onboarding docs ready.`
- `V2.0 ready: local agent workflow integration and developer usability polish complete.`
- `Codex and Claude Code local workflow templates ready.`
- `V2.1 planning baseline ready: real agent integration verification docs and third-party contract draft ready.`
- `V2.1-A complete: integration baseline audit and local third-party HTTP contract smoke ready.`
- `Third-party local HTTP contract smoke passed.`

当前不能声明：

- `Codex integration verified`
- `Claude Code integration verified`
- `Third-party agent integration verified`
- `Windows ready`
- `cross-platform ready`
- `production signed release ready`
- `auto update ready`
- `MCP ready`
- `USB ready`
- `Rive/Live2D/3D ready`
- `photo customization ready`

V2.0 final acceptance report: [docs/V2.0/v2_0-final-acceptance-report.md](docs/V2.0/v2_0-final-acceptance-report.md).

## macOS Quick Start

环境要求：

- Node：见 `.nvmrc`，当前为 Node 22。
- pnpm：见 `package.json`，当前为 `pnpm@10.32.1`。
- Rust：见 `rust-toolchain.toml`，当前为 `1.95.0`。
- macOS 需要 Xcode Command Line Tools。

安装依赖：

```bash
pnpm install
```

启动开发版：

```bash
pnpm --filter desktop tauri dev
```

构建本地 `.app`：

```bash
pnpm --filter desktop tauri build -b app
```

构建产物路径：

```text
apps/desktop/src-tauri/target/release/bundle/macos/Agent Desktop Pet.app
```

启动已构建 `.app`：

```bash
open "apps/desktop/src-tauri/target/release/bundle/macos/Agent Desktop Pet.app"
```

当前 `.app` 是 unsigned local app，不是正式签名发布版。首次打开和迁移说明见 [macOS Local Distribution](docs/ops/macos-local-distribution.md)。

## Verify

确认桌面猫已启动后，验证本地 HTTP API：

```bash
curl -sS http://127.0.0.1:17321/api/health
```

用构建后的 CLI 触发状态：

```bash
node packages/petctl/dist/cli.js notify --level success --title "distribution smoke"
```

开发环境可用时，也可以使用：

```bash
pnpm --filter @agent-desktop-pet/petctl petctl -- notify --level success --title "distribution smoke"
```

然后打开托盘菜单中的设置页，检查 diagnostics 中是否出现 accepted event。

## Workflow Examples

Shell 示例必须用 `--` 分隔用户命令：

```bash
examples/shell/task-with-pet.sh -- pnpm test
examples/shell/task-with-pet.sh -- pnpm --filter desktop build
examples/shell/task-with-pet.sh -- false
```

Node 示例：

```bash
node examples/node/notify-pet.mjs running
node examples/node/notify-pet.mjs success
node examples/node/notify-pet.mjs error
node examples/node/notify-pet.mjs need_input
```

更多接入方式：

- [Agent 接入指南](docs/reference/agent-integration-guide.md)
- [petctl Recipes](docs/reference/petctl-recipes.md)
- [Third-party Agent Contract](docs/reference/third-party-agent-contract.md)
- [Codex instruction template](skills/codex-agent-pet/SKILL.md)
- [Claude Code instruction template](skills/claude-agent-pet/SKILL.md)

## Docs

- [Docs Map](docs/README.md)
- [V1.0 archive](docs/V1.0/README.md)
- [V2.0 baseline](docs/V2.0/README.md)
- [V2.1 real agent integration verification](docs/V2.1/README.md)
- [Current development plan](docs/active/development-plan.md)
- [Current acceptance plan](docs/active/acceptance-plan.md)
- [Current gap analysis](docs/active/current-vs-target-gap.md)

Ops:

- [Developer Setup](docs/ops/developer-setup.md)
- [Network Mirrors](docs/ops/network-mirrors.md)
- [Troubleshooting](docs/ops/troubleshooting.md)
- [macOS Local Distribution](docs/ops/macos-local-distribution.md)
- [Release and Distribution](docs/ops/release-and-distribution.md)

Blueprint:

- [Product Experience](docs/blueprint/00-product-experience.md)
- [Target Architecture](docs/blueprint/target-architecture.md)
- [PetEvent Protocol](docs/blueprint/03-pet-event-protocol.md)
- [Cat State Machine](docs/blueprint/04-cat-state-machine.md)

## Security Boundaries

- Local API only listens on `127.0.0.1:17321`.
- `POST /api/events` requires `Authorization: Bearer <token>`.
- Agent integrations can only send structured PetEvent payloads.
- Agents cannot directly control UI, execute desktop scripts, or pass local paths/URLs as sounds.
- Sound IDs are whitelist-only and map to bundled assets.
- diagnostics does not expose full token, raw payload, full metadata, full message text, or sound file paths.

Token lookup for `petctl`:

1. `--token`
2. `AGENT_DESKTOP_PET_TOKEN`
3. desktop app config `api-token.json`

On macOS the current config location is:

```text
~/Library/Application Support/com.agentdesktoppet.desktop/api-token.json
~/Library/Application Support/com.agentdesktoppet.desktop/settings.json
```

Do not commit tokens into scripts or public repositories.

## No False-Green

This repository currently supports a macOS-first local workflow. Windows validation, production signing, notarization, auto update, MCP, USB, Rive/Live2D/3D, and photo customization are future work unless separately implemented and accepted.
