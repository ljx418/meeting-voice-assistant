# Developer Setup

本文面向参与源码开发的人。普通用户不应该安装 Node、pnpm、Rust 或 Tauri CLI；普通用户应使用发布页提供的 `.dmg`、`.app.zip`、`.msi`、`.exe` 或 portable zip。

## 目标

一台新机器应能通过以下命令完成本地开发验证：

```bash
git clone <repo>
cd agent-desktop-pet
pnpm install
pnpm run doctor
pnpm --filter desktop check
pnpm --filter desktop build
cargo check --manifest-path apps/desktop/src-tauri/Cargo.toml
pnpm --filter desktop tauri dev
```

## 推荐版本

- Node：使用 `.nvmrc`，推荐 Node 22 LTS。
- pnpm：根 `package.json` 使用 `packageManager` 固定。
- Rust：`rust-toolchain.toml` 固定到项目推荐版本。
- macOS：需要 Xcode Command Line Tools。

检查：

```bash
node --version
pnpm --version
rustc --version
cargo --version
xcode-select -p
```

## macOS

安装 Xcode Command Line Tools：

```bash
xcode-select --install
```

安装 Rust，优先使用 rustup：

```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source "$HOME/.cargo/env"
```

如果使用 Homebrew：

```bash
brew install rust
```

如果 Homebrew 报 `/usr/local` 或 cache 不可写，需要在用户自己的终端中修复 Homebrew 权限；项目脚本不会自动 sudo 修改系统目录。

## Windows

建议安装：

- Node.js LTS。
- pnpm。
- Rustup。
- Microsoft C++ Build Tools，选择 Desktop development with C++、Windows SDK、MSVC。

验证：

```powershell
node --version
pnpm --version
rustc --version
cargo --version
pnpm install
pnpm --filter desktop check
cargo check --manifest-path apps/desktop/src-tauri/Cargo.toml
pnpm --filter desktop tauri dev
```

## 诊断

运行：

```bash
pnpm run doctor
```

`doctor` 只做检查和提示，不会修改系统权限，不会安装工具链，不会实现业务功能。

## No False-Green

只有完成自动检查和实际 GUI smoke test 后，才允许声明：

```text
Phase 1 complete: desktop shell and placeholder pet window ready.
```

如果只完成 `pnpm check/build`，不能声明 Phase 1 complete。
