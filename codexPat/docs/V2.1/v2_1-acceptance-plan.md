# V2.1 Acceptance Plan

文档状态：V2.1 planning baseline。

## Acceptance Matrix

| Track | Required scenarios | Required evidence | Allowed claim after pass |
| --- | --- | --- | --- |
| Codex | 真实 Codex CLI 任务触发 `thinking`、`running`、`success`、`error`、`need_input`。 | diagnostics 出现 `sourceId=codex.local`；人工确认猫状态变化；报告 status=`passed`。 | `Codex local workflow integration verified.` |
| Claude Code skill | 真实 Claude Code skill 任务触发 `running`、`success`、`error`、`need_input`。 | diagnostics 出现 `sourceId=claude-code.local`；人工确认猫状态变化。 | `Claude Code skill workflow verified.` |
| Claude Code hook | `settings-hooks.example.json` 在真实 Claude Code hook 流程触发事件。 | 不泄露 token；diagnostics 出现 `sourceId=claude-code.local`。 | `Claude Code hook workflow verified.` |
| shell | `examples/shell/task-with-pet.sh -- true/false`。 | success/error 均出现，exit code 保留。 | `Shell workflow example verified.` |
| Node | `node examples/node/notify-pet.mjs success`。 | diagnostics 出现 `sourceId=node.local`。 | `Node workflow example verified.` |
| Generic HTTP | curl / Node / optional Python 直接 POST。 | accepted/rejected/error 语义符合合同，diagnostics 不显示 sound 路径、URL 或非法 source 原文。 | `Third-party local HTTP contract smoke passed.` |

当前 V2.1-A 结果：

- curl / Node / Python success smoke：通过。
- missing token、invalid level、invalid sound path、invalid sound URL、invalid source id、rate limit：通过。
- HTTP error response 和 diagnostics rejected summary 均使用 `reasonCode`、`reasonField` 和泛化 `reason`，不回显非法路径、URL 或非法 source 原文。
- V2.1-A 可声明 `Third-party local HTTP contract smoke passed`，但仍不得声明真实第三方 agent 产品集成已验证。

## Automatic Checks

每轮 V2.1 验收执行：

```bash
pnpm run doctor
pnpm --filter @agent-desktop-pet/pet-protocol check
pnpm --filter @agent-desktop-pet/pet-protocol test
pnpm --filter @agent-desktop-pet/petctl check
pnpm --filter @agent-desktop-pet/petctl test
pnpm --filter desktop check
pnpm --filter desktop build
cargo check --manifest-path apps/desktop/src-tauri/Cargo.toml
pnpm --filter desktop tauri build -b app
```

## Manual Smoke

1. 启动 `.app`。
2. 确认桌宠窗口可见、透明、无黑框、可拖拽。
3. 运行 Codex real smoke。
4. 运行 Claude Code skill smoke。
5. 运行 Claude Code hook smoke。
6. 运行 shell / Node / generic HTTP smoke。
7. 打开 settings diagnostics，确认 accepted/rejected/source/sound decision。
8. 切换静音，确认声音策略不回归。
9. 退出 app 后确认 `127.0.0.1:17321` 不再监听。

## No False-Green

不得声明：

- `Codex integration verified`，除非真实 Codex CLI smoke 通过并有报告。
- `Claude Code integration verified`，除非真实 Claude Code skill/hook smoke 通过并有报告。
- `Third-party agent integration verified`，除非后续真实 third-party agent 产品 smoke 通过并有报告；V2.1-A local HTTP contract smoke 通过不等于产品集成 verified。
- `MCP ready`，除非后续 `packages/pet-mcp` 实现并通过 Codex/Claude MCP smoke。
- `Windows ready`、`cross-platform ready`、`USB ready`、`production signed release ready`。
