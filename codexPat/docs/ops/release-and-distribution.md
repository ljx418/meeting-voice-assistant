# Release and Distribution

目标：最终用户不需要安装 Node、pnpm、Rust、Cargo 或 Tauri CLI。

## 用户安装路径

用户路径应保持简单：

```text
下载安装包 -> 打开应用 -> 托盘常驻 -> 使用桌面猫
```

推荐产物：

- macOS：`.dmg` 或 `.app.zip`。
- Windows：`.msi`、`.exe` installer 或 portable `.zip`。

## 构建职责

源码构建只属于维护者和贡献者。发布产物由 CI 或维护者构建机生成：

```text
tag release
-> macOS build
-> Windows build
-> smoke test
-> upload GitHub Releases
-> optional sync to domestic mirror
```

## 下载镜像

建议同时提供：

- GitHub Releases。
- 国内对象存储镜像，例如 OSS、COS、七牛云或 R2 自定义域名。

发布说明必须标注：

- 平台。
- 架构。
- 是否签名。
- 是否完成 smoke test。
- 已知限制。

## Phase 1 发布限制

Phase 1 只允许声明：

```text
Phase 1 complete: desktop shell and placeholder pet window ready.
```

不得声明：

- MVP ready。
- Agent integration ready。
- HTTP API ready。
- PetEvent ready。
- petctl ready。
- MCP/Skill ready。
- USB ready。
- cross-platform ready，除非 Windows 已完成真实 smoke test。

## Phase 6 / macOS-first MVP 发布限制

Phase 6 自动检查、端到端 smoke 和文档同步完成后，可以声明：

```text
Phase 6 complete: safe sound feedback implemented.
macOS-first MVP ready: local desktop agent status pet with HTTP + petctl integration and safe sound feedback.
```

可以说明：

- macOS 本地构建路径已验证。
- 本地 HTTP API 只监听 `127.0.0.1:17321`。
- `pet-protocol` JSON Schema、token、白名单和 rate limit 已落地。
- `petctl notify` 参数模式和 JSON stdin 已落地。
- 内置 sound ID、静音联动和 cooldown 已落地。
- Windows 不进入第一阶段 MVP 验收。

不得声明：

- MCP/Skill ready。
- USB ready。
- Windows ready。
- cross-platform ready。
- production signed release ready。

## 后续 CI 建议

优先建立以下任务：

- Install dependencies。
- TypeScript check。
- Vite build。
- Cargo check。
- Tauri build on macOS。
- Tauri build on Windows。
- 上传构建产物。

如果 GitHub Actions 下载不稳定，可以增加自建 runner 或国内构建机。
