# Release and Distribution

本文定义分发声明边界。当前项目只有 macOS local unsigned app 构建路径，不是 production release。

## Current Distribution State

当前可以说明：

- macOS local `.app` 可通过 Tauri 构建。
- 本地 HTTP API、`petctl`、diagnostics 和 safe sound 已在 macOS-first MVP 中完成。
- V2.0 Phase 2.4 提供 macOS 本地部署、排障和迁移文档。

当前不能说明：

- production signed release ready。
- notarized release ready。
- auto update ready。
- Windows ready。
- cross-platform ready。

## macOS Local App

本地构建：

```bash
pnpm --filter desktop tauri build -b app
```

输出路径：

```text
apps/desktop/src-tauri/target/release/bundle/macos/Agent Desktop Pet.app
```

详细打开、Gatekeeper 和迁移说明见 [macOS Local Distribution](macos-local-distribution.md)。

## Future Production Release

正式发布需要单独完成：

- macOS signing。
- macOS notarization。
- Windows installer 或 portable package。
- Windows smoke test。
- Release artifact upload。
- 版本说明和已知限制。
- 可选自动更新。

推荐未来 CI：

```text
tag release
-> install dependencies
-> TypeScript check
-> pet-protocol tests
-> petctl tests
-> Cargo check
-> Tauri macOS build
-> Tauri Windows build
-> platform smoke tests
-> upload artifacts
```

如果 GitHub Actions 下载不稳定，可以考虑自建 runner 或国内构建机。

## No False-Green

V2.0 final acceptance report 通过后允许声明：

```text
V2.0 ready: local agent workflow integration and developer usability polish complete.
Codex and Claude Code local workflow templates ready.
V2.0 Phase 2.4 complete: macOS distribution readiness and user onboarding docs ready.
```

仍不得声明：

```text
Windows ready
cross-platform ready
production signed release ready
auto update ready
MCP ready
USB ready
Rive/Live2D/3D ready
photo customization ready
```

`V2.0 ready` 的依据是 `docs/V2.0/v2_0-final-acceptance-report.md`，其 status 为 `passed`。
