# Developer Setup

本文面向源码开发和本地构建。普通用户不应依赖源码安装；当前 macOS 产物仍是 local unsigned app，不是 production release。

## Required Tools

项目当前工具链来源：

- Node：`.nvmrc`，当前 `22`。
- pnpm：根 `package.json` 的 `packageManager`，当前 `pnpm@10.32.1`。
- Rust：`rust-toolchain.toml`，当前 `1.95.0`。
- Tauri CLI：workspace dependency，通过 `pnpm --filter desktop tauri ...` 使用。
- macOS：Xcode Command Line Tools。

检查：

```bash
node --version
pnpm --version
rustc --version
cargo --version
xcode-select -p
```

## macOS Setup

安装 Xcode Command Line Tools：

```bash
xcode-select --install
```

推荐使用 rustup，让 `rust-toolchain.toml` 自动选择项目工具链：

```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source "$HOME/.cargo/env"
```

如果使用 Homebrew Rust，也可以构建当前项目，但 `rust-toolchain.toml` 不会自动切换工具链。

## Install And Build

```bash
pnpm install
pnpm run doctor
pnpm --filter desktop check
pnpm --filter desktop build
cargo check --manifest-path apps/desktop/src-tauri/Cargo.toml
pnpm --filter desktop tauri dev
```

迁移或重建本地 app 前，可先参考 [V3.1 Local App Migration and Backup](../V3.1/v3_1-local-app-migration-backup.md) 确认哪些配置需要保留，哪些构建产物可以重建。

构建 macOS local `.app`：

```bash
pnpm --filter desktop tauri build -b app
```

输出路径：

```text
apps/desktop/src-tauri/target/release/bundle/macos/Agent Desktop Pet.app
```

## Doctor

运行：

```bash
pnpm run doctor
```

`doctor` 只做检查和提示，不会安装工具链，不会修改系统权限，不会修复环境。

结果分级：

- `OK`：检查通过。
- `WARN`：可能影响首次安装或首次构建，但不一定阻塞已有缓存的构建。
- `FAIL`：阻塞启动或构建，需要先修复。

网络 WARN 常见于受限网络环境。若依赖已缓存，后续 check/build 仍可能通过。

## Windows

Windows 仍是后续目标，但当前不做 Windows smoke，不声明 Windows ready 或 cross-platform ready。

后续验证前至少需要：

- Node.js LTS。
- pnpm。
- Rustup。
- Microsoft C++ Build Tools。
- WebView2 Runtime。

## No False-Green

仅完成源码构建不等于 production release。当前最多声明 macOS-first local workflow 和 V2.0 阶段性能力；未完成 Windows smoke、签名、notarization 和自动更新前，不得声明 cross-platform ready 或 production signed release ready。
