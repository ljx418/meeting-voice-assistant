# V3.1 Phase 5：Local App Migration and Backup

文档状态：active phase guide and acceptance。

## 目标

说明本地 app 的迁移、备份、恢复和故障排查路径，让用户换目录、换机器、重装依赖或重新构建 app 时，知道哪些东西需要保留、哪些可以重建、哪些不能公开分享。

当前 `Agent Desktop Pet.app` 是 macOS unsigned local app，不是 production release，不是正式签名安装包，也没有 notarization 或自动更新。

## 真实配置路径

desktop 端使用 Tauri `app_config_dir()`。当前 app identifier：

```text
com.agentdesktoppet.desktop
```

macOS 当前配置目录：

```text
~/Library/Application Support/com.agentdesktoppet.desktop
```

配置文件：

```text
~/Library/Application Support/com.agentdesktoppet.desktop/settings.json
~/Library/Application Support/com.agentdesktoppet.desktop/api-token.json
```

`petctl` 当前也会在同一 app identifier 下查找 `api-token.json`。

可以用只读脚本确认当前机器上的配置摘要：

```bash
node scripts/v3_1_config_audit.mjs
node scripts/v3_1_config_audit.mjs --json
```

该脚本不打印 token、不打印 `api-token.json` 内容、不打印完整 `settings.json`。

## 配置内容

`settings.json` 可能包含：

- 静音状态。
- default pet 位置和显示状态。
- default cat profile。
- 多猫实例 registry。
- 每只实例猫的名称、窗口标签、位置、显示状态、当前状态、外观 profile、最近事件时间等摘要字段。

`api-token.json` 包含本地 HTTP API token。它只应该用于个人本地备份，不应提交 git，不应写进公开脚本，不应发给他人。

如果 `api-token.json` 迁移失败，`petctl` 可能报：

- `token_missing`
- `unauthorized`

如果 `settings.json` 迁移失败，多猫实例、名称、位置、显示状态和外观可能回到默认状态。

## 推荐备份清单

建议备份：

- 项目源码目录。
- `pnpm-lock.yaml`。
- `Cargo.lock`。
- `docs/`。
- app config 目录中的 `settings.json`。
- app config 目录中的 `api-token.json`，仅限个人安全备份。

不需要备份：

- `node_modules`。
- `apps/desktop/src-tauri/target`。
- `packages/*/dist`。
- Vite dist。
- 临时日志。
- Smoke 测试产生的临时实例，前提是 smoke 已 cleanup。

## 迁移流程

旧机器：

1. 从托盘退出 app。
2. 备份项目目录。
3. 备份 app config 目录：

   ```text
   ~/Library/Application Support/com.agentdesktoppet.desktop
   ```

新机器：

1. 安装 Node、pnpm、Rust、Xcode Command Line Tools。
2. 还原项目目录。
3. 还原 app config 目录到同一位置。
4. 安装依赖：

   ```bash
   pnpm install
   ```

5. 构建 `petctl`：

   ```bash
   pnpm --filter @agent-desktop-pet/petctl build
   ```

6. 构建 `.app`：

   ```bash
   pnpm --filter desktop tauri build -b app
   ```

7. 启动 `.app`：

   ```bash
   open "apps/desktop/src-tauri/target/release/bundle/macos/Agent Desktop Pet.app"
   ```

8. 验证 health：

   ```bash
   curl -sS http://127.0.0.1:17321/api/health
   ```

9. 验证 `petctl list`：

   ```bash
   node packages/petctl/dist/cli.js list
   ```

10. 验证通知：

   ```bash
   node packages/petctl/dist/cli.js notify --level success --title "migration smoke"
   ```

11. 打开设置页 Multi-pet Manager，检查实例、名字、外观、位置。

## 恢复与排障

优先参考 [Troubleshooting](../ops/troubleshooting.md)。

常见情况：

- app 启动但猫不见：检查托盘显示状态、重置位置，确认窗口没有被隐藏或出屏。
- 多猫实例丢失：检查 `settings.json` 是否迁移到正确 config 目录。
- 位置出屏：使用 Manager UI 重置位置。
- `petctl token_missing`：确认 `api-token.json` 是否存在，或使用 `--token` / `AGENT_DESKTOP_PET_TOKEN`。
- `petctl unauthorized`：token 不匹配，重新确认 desktop app 与 petctl 使用同一 config。
- `127.0.0.1:17321` 被占用：从托盘退出旧 app，或查看端口占用。
- app config 损坏：先备份损坏文件，再根据排障文档处理；本阶段不提供自动修复。
- `settings.json` 不兼容：先保留备份，再回到默认配置启动。
- `api-token.json` 丢失：需要重新获取或重新创建本地 token；当前没有 token reset UI。
- 重新构建后 `.app` 路径找不到：重新运行 `pnpm --filter desktop tauri build -b app`。
- unsigned app 被 Gatekeeper 拦截：按 [macOS Local Distribution](../ops/macos-local-distribution.md) 的 First Open 流程打开。

## 边界

本阶段不做：

- 自动备份或自动恢复。
- token reset UI。
- config 修复逻辑。
- 正式签名、公证、自动更新。
- Windows ready 或 cross-platform ready。
- MCP、USB、3D、照片自定义。

完成后最多声明：

```text
V3.1 Phase 5 complete: local app migration and backup guidance ready.
```
