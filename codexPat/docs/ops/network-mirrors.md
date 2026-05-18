# Network Mirrors

本文解决开发环境下载慢或 DNS 不稳定的问题。镜像配置属于开发者机器配置，不应把个人镜像写死进项目源码。

## npm / pnpm

官方源：

```bash
pnpm config set registry https://registry.npmjs.org
pnpm config get registry
```

国内源：

```bash
pnpm config set registry https://registry.npmmirror.com
pnpm config get registry
```

验证：

```bash
curl -I https://registry.npmjs.org/typescript
curl -I https://registry.npmmirror.com/typescript
pnpm install
```

## Rustup

官方：

```bash
curl -I https://sh.rustup.rs
```

国内镜像示例：

```bash
export RUSTUP_DIST_SERVER=https://rsproxy.cn
export RUSTUP_UPDATE_ROOT=https://rsproxy.cn/rustup
curl --proto '=https' --tlsv1.2 -sSf https://rsproxy.cn/rustup-init.sh | sh
```

## Cargo

用户级配置示例，写入 `~/.cargo/config.toml`：

```toml
[source.crates-io]
replace-with = "rsproxy-sparse"

[source.rsproxy-sparse]
registry = "sparse+https://rsproxy.cn/index/"
```

验证：

```bash
cargo check --manifest-path apps/desktop/src-tauri/Cargo.toml
```

## Tauri Dependencies

Tauri 首次构建会下载 Rust crates 和平台相关依赖。网络慢时先确保：

- `pnpm install` 已完成。
- Cargo registry 可访问。
- `apps/desktop/src-tauri/Cargo.lock` 存在。
- `pnpm run doctor` 没有 hard failure。

如果 `doctor` 只有网络 WARN，而 `node_modules`、`pnpm-lock.yaml`、`Cargo.lock` 和 Cargo cache 已存在，本地构建可能仍然可通过。

## Project Rules

- 不提交个人 `.cargo/config.toml`。
- 不提交 `node_modules`、`dist`、`target`。
- 提交 `pnpm-lock.yaml`。
- 应用型 Rust crate 提交 `apps/desktop/src-tauri/Cargo.lock`。
- 普通用户不走源码安装；当前 macOS 本地分发见 [macOS Local Distribution](macos-local-distribution.md)。
