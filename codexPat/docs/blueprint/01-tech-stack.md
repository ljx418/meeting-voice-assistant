# 技术选型

## 桌面框架

选择：Tauri 2 + Rust + TypeScript。

原因：

- Tauri 对透明窗口、无边框窗口、托盘、原生设置存储和打包有直接支持。
- Rust 适合实现本地 HTTP、Rust Ingress Queue、token 鉴权和安全校验。
- 相比 Electron，包体更小，系统资源占用更低。

收益：

- 跨平台路线明确，覆盖 macOS 和 Windows。
- 安全边界可以集中在 Rust 端。
- 后续 USB 串口适配更自然，但 USB 真实或 mock 硬件不进入 MVP。

风险：

- 透明窗口、点击穿透、多显示器行为仍需分别在 macOS 和 Windows 验证。
- Tauri 某些窗口能力在不同系统上行为不完全一致。

替代方案：

- Electron：生态成熟，窗口能力强，但包体和资源占用更高。
- Flutter Desktop：UI 一致性好，但桌宠式系统窗口控制不如 Tauri 直接。
- 原生 Swift + C#：体验最好，但维护成本最高。

## 前端渲染

选择：Vite + TypeScript。

原因：

- 启动快，Tauri 集成成熟。
- 可以先做轻量桌宠和设置页。
- 后续接 PixiJS、Rive、Live2D、Three.js 都方便；MVP 只做 CSS/sprite/PixiJS 占位。

## 动画方案

MVP：sprite 动画，优先支持 PixiJS 或 CSS sprite。

建议：

- 先定义 `CatRenderer` 抽象。
- MVP 实现 `SpriteRenderer`。
- Rive、Live2D、GLTF/GLB 作为后续 renderer 插件扩展。

风险：

- 动画资源生产可能比技术实现更慢。
- Live2D 和 3D 模型制作链复杂，且可能涉及授权。

## 后端本地服务

选择：Tauri Rust 端内嵌 HTTP API。

要求：

- 只监听 `127.0.0.1`。
- 默认端口建议 `17321`，允许用户配置。
- 使用本地 token。
- 所有事件基于 JSON Schema 或等价跨语言 schema 校验。

建议 Rust 库：

- `axum` 或等价轻量 HTTP 服务。
- Tauri event channel 将事件推送给前端。

## CLI 工具

MVP 选择：TypeScript CLI。

原因：

- 可复用 `packages/pet-protocol` 的 JSON Schema、类型和 capabilities。
- npm/pnpm 开发效率高。

后续替代：

- 如果需要单文件二进制分发，可以迁移或补充 Rust CLI。

## MCP server

Post-MVP 选择：TypeScript MCP server。

原因：

- MCP TypeScript SDK 生态成熟。
- 与 CLI 和协议包共享代码。
- 适合 Claude Code、Codex 和自定义 MCP client。

## USB 串口

MVP：不实现 USB 真实硬件，也不实现 USB mock adapter。

Post-MVP 真实实现：Rust 端使用 `serialport` crate。

原因：

- 硬件访问属于桌面 App 本地能力。
- Rust 端更适合做设备白名单、重连和错误隔离。

替代方案：

- Node `serialport`：开发快，但打包和 sidecar 管理更复杂。
- Web Serial：跨平台桌面 WebView 支持不可控，不建议作为主方案。

## 打包和部署

选择：Tauri bundler。

目标：

- macOS：`.app` 和 `.dmg`。
- Windows：`.msi` 或 `.exe`。
- 后续通过 GitHub Actions 做构建矩阵。

MVP：

- 先支持本地开发和本地打包。
- 公开分发前再处理代码签名、公证、自动更新。
