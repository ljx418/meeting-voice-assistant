# V2.0 Baseline

文档状态：V2.0 planning baseline。  
基线来源：V1.0 macOS-first MVP。

## 1. V1.0 已实现能力

V1.0 已实现一只可常驻桌面的开发者猫，用于把本地 AI Agent 或脚本状态转译为低打扰桌面反馈。

已完成：

- Tauri 2 + Rust + Vite + TypeScript 桌面应用。
- macOS-first 透明、无边框、置顶、小尺寸宠物窗口。
- 鼠标拖拽、位置持久化、出屏恢复。
- 系统托盘：设置、静音、显示/隐藏、重置位置、退出。
- 设置页：静音、位置、当前状态、队列、API diagnostics、sound diagnostics。
- CSS 占位猫：idle、thinking、running、success、warning、error、need_input、sleeping。
- 前端 `CatStateMachine` 和 Behavior Queue。
- Rust Local Event Bridge：`127.0.0.1:17321`。
- HTTP API：`GET /api/health`、`GET /api/capabilities`、`POST /api/events`、`GET /api/diagnostics`。
- `packages/pet-protocol`：PetEvent JSON Schema、TypeScript 类型、capabilities、fixtures、测试。
- token 鉴权、JSON Schema 校验、白名单校验、rate limit。
- Rust Ingress Queue、accepted/rejected event summary ring buffer。
- `packages/petctl`：`petctl notify` 参数模式和 `--json` stdin。
- 安全声音反馈：内置 sound ID、静音联动、cooldown、diagnostics sound 字段。

## 2. V1.0 安全边界

- 本地 API 只监听 `127.0.0.1`。
- 外部 agent 只能写入结构化 PetEvent。
- agent 不能直接控制 UI。
- agent 不能执行本地脚本。
- agent 不能传入任意本地文件路径或 URL 作为声音或资源。
- `source.kind`、`level`、`action`、`sound`、`hardware.light.effect` 使用白名单或枚举。
- `PetEvent.sound` 只是请求意图，桌面端根据 level、mute、cooldown 和低打扰策略决定是否播放。
- diagnostics 不暴露 token、原始 payload、metadata 全量、message 全文、声音文件路径、非法 sound 原文、URL、本地路径或非法 `source.id`。

## 3. 当前可声明

```text
Phase 1 complete: desktop shell and placeholder pet window ready.
Phase 2 complete: local low-interruption state machine and placeholder state animations ready.
Phase 3 complete: local PetEvent protocol and localhost HTTP event bridge ready.
Phase 4 complete: observable event runtime and settings diagnostics ready.
Phase 5 complete: petctl CLI can notify the local desktop pet through localhost HTTP API.
Phase 6 complete: safe sound feedback implemented.
macOS-first MVP ready: local desktop agent status pet with HTTP + petctl integration and safe sound feedback.
```

## 4. 当前不可声明

```text
Windows ready
cross-platform ready
MCP server ready
Codex / Claude Code Skill ready
USB ready
production signed release ready
auto update ready
Live2D/Rive/3D ready
photo customization ready
team collaboration hub ready
```

## 5. V2.0 进入点

V2.0 不改变 V1.0 核心架构，重点补齐真实开发工作流接入和用户可理解性：

- Codex / Claude Code instruction template。
- `petctl` recipes。
- shell / Node 示例。
- 设置页 diagnostics 可读性优化。
- README、doctor、troubleshoot、macOS 分发准备。
- CSS 猫咪体验 polish。
