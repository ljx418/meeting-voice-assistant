# V2.1 Acceptance Plan

文档状态：V2.1 Codex acceptance passed；complex integrations deferred to V3.0。

## Acceptance Matrix

| Track | Required scenarios | Required evidence | Allowed claim after pass |
| --- | --- | --- | --- |
| Codex | 真实 Codex CLI 任务触发 `thinking`、`running`、`success`、`error`、`need_input`。 | diagnostics 出现 `sourceId=codex.local`；人工确认猫状态变化；报告 status=`passed`。 | `Codex local workflow integration verified.` |
| Claude Code skill | 真实 Claude Code skill 任务触发 `running`、`success`、`error`、`need_input`。 | diagnostics 出现 `sourceId=claude-code.local`；人工确认猫状态变化。 | 迁移到 V3.0，当前不得声明。 |
| Claude Code hook | `settings-hooks.example.json` 在真实 Claude Code hook 流程触发事件。 | 不泄露 token；diagnostics 出现 `sourceId=claude-code.local`。 | 迁移到 V3.0，当前不得声明。 |
| shell | `examples/shell/task-with-pet.sh -- true/false`。 | success/error 均出现，exit code 保留。 | `Shell workflow example verified.` |
| Node | `node examples/node/notify-pet.mjs success`。 | diagnostics 出现 `sourceId=node.local`。 | `Node workflow example verified.` |
| Generic HTTP | curl / Node / optional Python 直接 POST。 | accepted/rejected/error 语义符合合同，diagnostics 不显示 sound 路径、URL 或非法 source 原文。 | `Third-party local HTTP contract smoke passed.` |

当前 V2.1-A 结果：

- curl / Node / Python success smoke：通过。
- missing token、invalid level、invalid sound path、invalid sound URL、invalid source id、rate limit：通过。
- HTTP error response 和 diagnostics rejected summary 均使用 `reasonCode`、`reasonField` 和泛化 `reason`，不回显非法路径、URL 或非法 source 原文。
- V2.1-A 可声明 `Third-party local HTTP contract smoke passed`，但仍不得声明真实第三方 agent 产品集成已验证。

当前 V2.1-B 结果：

- 真实 `codex exec` 已触发 `sourceId=codex.local` 的 `thinking`、`running`、`success`、`error`、`need_input` accepted events。
- 自动检查和 `.app` 构建通过。
- 证据文件：`docs/V2.1/evidence/codex-smoke-2026-05-19.md`。
- operator 已确认人工视觉验收通过，V2.1-B 可声明 `Codex local workflow integration verified for tested local Codex CLI smoke scenarios`。

当前 V2.1-C 迁移结果：

- C1 Claude Code skill runtime smoke 已触发 `sourceId=claude-code.local` 的 `thinking`、`running`、`success`、`error`、`need_input` accepted events。
- C1 仍缺少 operator 视觉验收记录，因此不得声明 `Claude Code skill workflow verified`。
- C2 Claude Code hook smoke 当前 blocked：`settings-hooks.example.json` 已补齐 `Notification -> need_input`，但真实 Claude Code `Notification` event 尚未在本轮非交互 smoke 中触发；diagnostics 未出现 hook-caused `need_input` event。
- 证据文件：`docs/V2.1/evidence/claude-code-smoke-2026-05-19.md`。
- 上述复杂接入不再作为 V2.1-B Codex 适配声明的阻塞项，统一迁移到 V3.0。

V2.1-C2 hook 验收补充：

- `Notification` 是当前 Claude Code 2.1.114 本地文档列出的 hook event。
- 未发现 `PostToolUseFailure` event；失败 hook 可在后续基于 `PostToolUse` 结果解析预研，但不阻塞 Notification hook 验收。
- `UserPromptSubmit`、`PreToolUse` 和 `Stop` 不作为默认强验收 hook。前两者如启用必须节流，`Stop` 不等同任务成功。

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

- `Codex integration verified` 超出本地已测 Codex CLI smoke 场景的泛化声明；当前只允许声明 `Codex local workflow integration verified for tested local Codex CLI smoke scenarios`。
- `Claude Code integration verified`，除非真实 Claude Code skill/hook smoke 通过并有报告。
- `Claude Code skill workflow verified`，除非 C1 runtime smoke 和 operator 视觉验收均通过并有报告。
- `Claude Code hook workflow verified`，除非真实 hook 注册、触发、diagnostics 和安全检查均通过并有报告。
- `Third-party agent integration verified`，除非后续真实 third-party agent 产品 smoke 通过并有报告；V2.1-A local HTTP contract smoke 通过不等于产品集成 verified。
- `MCP ready`，除非后续 `packages/pet-mcp` 实现并通过 Codex/Claude MCP smoke。
- `Windows ready`、`cross-platform ready`、`USB ready`、`production signed release ready`。
