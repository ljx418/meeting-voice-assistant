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

## Rustup 镜像

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

## Cargo 镜像

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

## 项目原则

- 不提交个人 `.cargo/config.toml`。
- 不提交 `node_modules`、`dist`、`target`。
- 提交 `pnpm-lock.yaml`。
- 应用型 Rust crate 在首次成功解析后提交 `apps/desktop/src-tauri/Cargo.lock`。
- 普通用户不走源码安装，直接下载发布产物。
