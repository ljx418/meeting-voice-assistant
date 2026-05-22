# Troubleshooting

本文记录本地开发、macOS unsigned app 和 `petctl` 常见问题。

## Doctor Result Levels

运行：

```bash
pnpm run doctor
```

结果分级：

- `OK` / PASS：必须通过或已满足。
- `WARN`：可能影响首次安装或首次构建，但不一定阻塞已有缓存的本地构建。
- `FAIL`：通常阻塞启动、检查或构建，需要先修复。

常见 WARN：

- npm registry、crates.io 或 rustup 网络不可达。
- `rustup` 未安装，但 Homebrew Rust 已可用。
- 沙箱环境不能监听本地端口。

网络 WARN 不一定阻塞已经下载好依赖的本地构建。

## Port 17321 Is Occupied

本地 HTTP API 使用：

```text
127.0.0.1:17321
```

查看占用：

```bash
lsof -iTCP:17321 -sTCP:LISTEN
```

如果是旧的 `agent-desktop-pet` 进程，先从托盘退出应用。必要时再结束旧进程。

## petctl Errors

`desktop_not_running`

- desktop app 未启动。
- `127.0.0.1:17321` 未监听。
- 先启动 `.app` 或 `pnpm --filter desktop tauri dev`。

`token_missing`

- `petctl` 找不到 token。
- 使用 `--token`、`AGENT_DESKTOP_PET_TOKEN`，或先启动 desktop app 让它创建 config token 文件。

`unauthorized`

- token 不匹配。
- 不要打印完整 token；重新确认 `--token`、环境变量或 `api-token.json`。

`rate_limited`

- 写入事件太频繁。
- 只在状态阶段变化时发送事件，不要对每行日志发送事件。

`schema_invalid`

- payload 不符合 PetEvent JSON Schema。
- 检查 `source.id`、`source.kind`、`level`、`durationMs`、`title/message` 长度等字段。

invalid sound

- sound 只能是白名单 ID。
- 不允许本地路径、相对路径、绝对路径或 URL。
- 当前接受：`none`、`success_chime`、`warning_chime`、`error_chime`、`need_input_chime`。
- HTTP error response 和 diagnostics 只会显示 `reasonField=sound` 和 `sound is not an accepted ID`，不会回显你提交的路径或 URL。

## tsx IPC EPERM

在受限终端或沙箱中，开发态命令可能因为 `tsx` 创建 IPC pipe 失败：

```text
listen EPERM ... /tmp/tsx-*.pipe
```

这不代表 `petctl` 功能失败。可先构建包，再用 dist CLI 验证：

```bash
pnpm --filter @agent-desktop-pet/petctl build
node packages/petctl/dist/cli.js notify --level success --title "distribution smoke"
```

## Unsigned macOS App Cannot Open

当前 `.app` 是 unsigned local app，不是 production signed release。

如果 macOS 提示无法验证开发者：

1. 在 Finder 中找到 app。
2. 右键或 Control-click。
3. 选择 Open。
4. 再次确认 Open。

更多说明见 [macOS Local Distribution](macos-local-distribution.md)。

## Token And Config

迁移、备份和恢复说明见 [V3.1 Local App Migration and Backup](../V3.1/v3_1-local-app-migration-backup.md)。

HTTP API 需要：

```text
Authorization: Bearer <token>
```

`petctl` token 读取顺序：

1. `--token`
2. `AGENT_DESKTOP_PET_TOKEN`
3. desktop app config `api-token.json`

macOS 当前 config 路径：

```text
~/Library/Application Support/com.agentdesktoppet.desktop/api-token.json
~/Library/Application Support/com.agentdesktoppet.desktop/settings.json
```

当前不提供 token reset UI。不要把 token 写进公开脚本或提交到仓库。
