# V1.0 Acceptance

## 验收口径

V1.0 是 macOS-first MVP。Windows 不进入 V1.0 验收，后续 Phase 8 单独做 Windows smoke 和 cross-platform hardening。

V1.0 通过后可声明：

```text
macOS-first MVP ready: local desktop agent status pet with HTTP + petctl integration and safe sound feedback.
```

V1.0 仍不可声明：

```text
cross-platform ready
Windows ready
MCP/Skill ready
USB ready
production signed release ready
auto update ready
```

## 自动检查

V1.0 最终检查已覆盖：

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

已知非阻塞项：

- `doctor` 在沙箱内可能报告网络和本地端口 warning。
- 这些 warning 不等同于 V1.0 功能失败。

## 端到端 Smoke

V1.0 smoke 覆盖：

- macOS Tauri app 可启动。
- 桌宠窗口透明、无边框、置顶、可拖拽。
- 托盘可打开设置、静音、显示/隐藏、重置位置、退出。
- `GET /api/health` 正常。
- `GET /api/capabilities` 正常。
- `GET /api/diagnostics` 无 token 返回 401。
- `GET /api/diagnostics` 有 token 返回 diagnostics。
- `petctl notify --level success` 可驱动 success 状态。
- `petctl notify --json` 可写入事件。
- 非法 level、非法 source、非法 sound 路径或 URL 被拒绝。
- 高频事件触发 rate limit。
- diagnostics 显示 accepted/rejected summaries。
- Safe sound feedback 可播放内置 sound ID。
- 静音时所有声音跳过。
- `thinking` / `running` 默认静默。
- `need_input` 高频声音受 cooldown 控制。
- macOS `.app` bundle 可生成。

## No False-Green

- 只完成 macOS-first V1.0，不得声明 cross-platform ready。
- 未做 Windows smoke，不得声明 Windows ready。
- 未做 MCP server，不得声明 MCP ready。
- 未做 Skill 完整包，不得声明 Codex/Claude Code Skill ready。
- 未做 USB，不得声明 hardware ready。
- 未签名发布，不得声明 production signed release ready。
