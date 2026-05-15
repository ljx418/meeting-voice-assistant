# V1.0 Architecture

## 目标体验

V1.0 的第一体验是可常驻桌面的开发者猫。它通过动作、状态和安全提示音表达本地 Agent 状态，核心价值是低打扰状态感知，而不是通用桌宠或通知中心。

核心链路：

```text
custom agent / script
  -> petctl or localhost HTTP
  -> Rust Local Event Bridge
  -> schema / whitelist / token / rate limit
  -> Rust Ingress Queue + diagnostics
  -> TypeScript CatStateMachine
  -> transparent desktop cat + safe sound feedback
```

## 已实现模块

Tauri Desktop App：

- macOS-first Tauri 2 桌面应用。
- 透明、无边框、置顶、小尺寸桌宠窗口。
- 鼠标拖拽、位置持久化、出屏恢复。
- 系统托盘：显示设置、静音、显示/隐藏猫咪、重置位置、退出。
- 设置页：静音状态、窗口位置、当前状态、API diagnostics、sound diagnostics。

TypeScript Frontend：

- `CatStateMachine`。
- 本地 Behavior Queue。
- idle、thinking、running、success、warning、error、need_input、sleeping 占位动画。
- 本地 debug 状态触发器。
- 接收 Rust side 推送的合法事件。

Rust Local Event Bridge：

- 只监听 `127.0.0.1:17321`。
- `GET /api/health`。
- `GET /api/capabilities`。
- `POST /api/events`。
- `GET /api/diagnostics`。
- Bearer token 鉴权。
- JSON Schema 校验。
- 白名单校验。
- rate limit。
- Rust Ingress Queue。
- accepted/rejected summary ring buffer。

Safe Sound Service：

- 只播放应用 bundle 内置声音资源。
- 只接受 sound ID，不接受路径或 URL。
- 支持静音联动。
- 支持 cooldown。
- `thinking` / `running` / `idle` / `sleeping` 默认静默。
- diagnostics 暴露播放能力和决策，不暴露文件路径。

Packages：

- `packages/pet-protocol`：PetEvent JSON Schema、TypeScript 类型、capabilities、fixtures 和协议测试。
- `packages/petctl`：CLI client，通过 localhost HTTP API 写入 PetEvent。

## V1.0 架构边界

V1.0 不包含：

- MCP server。
- Codex / Claude Code Skill 完整包。
- USB serial hardware。
- Rive / Live2D / 3D。
- 照片自定义猫咪。
- Windows smoke。
- 自动更新。
- 正式签名发布。

这些能力必须在后续阶段复用 V1.0 的协议、安全边界和低打扰体验原则。
