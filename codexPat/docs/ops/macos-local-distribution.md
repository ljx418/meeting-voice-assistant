# macOS Local Distribution

本文说明如何在 macOS 上构建和迁移本地 unsigned app。

当前产物是 local unsigned app，不是 production release，不是官方安装包，也没有完成 notarization。

## Build

安装依赖：

```bash
pnpm install
```

构建 `.app`：

```bash
pnpm --filter desktop tauri build -b app
```

输出路径：

```text
apps/desktop/src-tauri/target/release/bundle/macos/Agent Desktop Pet.app
```

启动：

```bash
open "apps/desktop/src-tauri/target/release/bundle/macos/Agent Desktop Pet.app"
```

## First Open

因为当前 `.app` 未签名，macOS Gatekeeper 可能提示无法验证开发者。

本地开发验证时可用以下方式打开：

1. 在 Finder 中找到 `Agent Desktop Pet.app`。
2. 右键或 Control-click。
3. 选择 Open。
4. 在提示框中再次确认 Open。

不要把这个本地 unsigned app 描述为正式发布版、正式安装包或 production release。

## What Is Not Implemented

当前不做：

- 正式签名。
- notarization。
- 自动更新。
- 安装器。
- GitHub Release 自动发布。
- Windows release。
- cross-platform ready 声明。

## Migration

完整迁移、备份和恢复指南见 [V3.1 Local App Migration and Backup](../V3.1/v3_1-local-app-migration-backup.md)。本节只保留 macOS local unsigned app 的分发摘要。

源码迁移到新机器时建议携带：

- 项目目录。
- Git 历史或远端仓库。
- 必要时携带本地 app config，但不要提交 token。

不建议携带：

- `node_modules`。
- `dist`。
- `target`。
- 个人 Cargo registry/cache。

新机器通常需要重新执行：

```bash
pnpm install
pnpm --filter desktop tauri build -b app
```

Rust/Cargo artifacts 通常需要重新构建；如果网络慢，先参考 [Network Mirrors](network-mirrors.md)。

## Config Files

desktop 端使用 Tauri `app_config_dir()`。当前 app identifier 是：

```text
com.agentdesktoppet.desktop
```

macOS 当前路径：

```text
~/Library/Application Support/com.agentdesktoppet.desktop/api-token.json
~/Library/Application Support/com.agentdesktoppet.desktop/settings.json
```

`api-token.json` 供本地 HTTP API 和 `petctl` 鉴权使用。不要把它提交到公开仓库，不要在公共脚本中明文写入 token。

只读配置审计：

```bash
node scripts/v3_1_config_audit.mjs
node scripts/v3_1_config_audit.mjs --json
```

该脚本只输出脱敏摘要，不打印 token 或完整 settings。

## Smoke Test

启动 `.app` 后：

```bash
curl -sS http://127.0.0.1:17321/api/health
node packages/petctl/dist/cli.js notify --level success --title "distribution smoke"
```

期望：

- 桌宠窗口可见。
- `health` 返回 ok。
- 猫进入 success。
- 设置页 diagnostics 出现 accepted event。
- 退出 app 后 `127.0.0.1:17321` 不再监听。
