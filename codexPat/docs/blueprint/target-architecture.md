# Target Architecture

文档状态：macOS-first MVP architecture synced；Phase 6 implementation synced。  
目标：明确第一版技术边界，避免把后续 MCP、skills、USB、Rive/Live2D/3D、照片自定义混入 MVP。

## 1. MVP Architecture

```text
+--------------------+      +--------------------+
| Custom Agent       |      | Developer Scripts  |
| local process      |      | shell / npm / etc  |
+---------+----------+      +----------+---------+
          |                            |
          | HTTP caller                | petctl CLI client
          v                            v
+------------------------------------------------+
|     Tauri Rust Side: Rust Local Event Bridge    |
|                                                |
| - HTTP 127.0.0.1 only                          |
| - token auth                                   |
| - JSON Schema PetEvent validation              |
| - action/sound/hardware whitelist              |
| - rate limit                                   |
| - Rust Ingress Queue                           |
| - accepted/rejected summaries                  |
| - Safe Sound service                           |
+----------------------+-------------------------+
                       |
                       | Tauri event / command
                       v
+------------------------------------------------+
|              TypeScript Frontend               |
|                                                |
| - CatStateMachine                              |
| - Behavior Queue                               |
| - placeholder sprite/CSS/Pixi renderer         |
| - low interruption display rules               |
| - settings page                                |
| - tray-driven visibility/mute state            |
| - diagnostics display                          |
+----------------------+-------------------------+
                       |
                       v
+------------------------------------------------+
|                 Desktop Window                 |
| transparent / frameless / always-on-top        |
| draggable small pet window + tray              |
+------------------------------------------------+

+-------------------+        +-------------------+
| pet-protocol      |        | petctl CLI client |
| JSON Schema       |        | notify -> HTTP    |
| TS/Rust contract  |        |                   |
+-------------------+        +-------------------+
```

## 2. Module Responsibilities

Tauri desktop app：

- 管理透明窗口、置顶、拖拽、托盘、设置页。
- 宿主 Rust Local Event Bridge。
- 宿主前端状态机和动画渲染。

Rust Local Event Bridge：

- Tauri Rust side 内嵌模块。
- 监听 `127.0.0.1`。
- 执行 token 鉴权。
- 基于同一份 JSON Schema 或等价跨语言 schema 校验 PetEvent。
- 执行动作、声音、硬件 effect 白名单。
- 执行速率限制并记录最近合法/非法摘要。
- 维护轻量 Rust Ingress Queue。
- 将合法事件推送给前端。
- 将合法事件交给 Sound service 做白名单、静音和 cooldown 决策。

TypeScript frontend：

- 实现 `CatStateMachine`。
- 实现 Behavior Queue、占位动画和低打扰展示策略。
- 设置页展示 API、queue、accepted/rejected summaries 和 sound diagnostics。
- rejected summaries 只展示后端安全摘要；schema/白名单错误必须使用 `reasonCode`、`reasonField` 和泛化 `reason`，不得回显非法路径、URL、非法 sound 原文或非法 `source.id`。
- 猫咪大小调整是后续目标。

Rust Sound service：

- 只播放应用 bundle 内置声音资源。
- 只接受白名单 sound ID，不接受路径或 URL。
- 按 level、静音状态和 cooldown 决定是否播放。
- `thinking` / `running` / `idle` / `sleeping` 默认静默。
- diagnostics 只暴露 sound ID 和播放决策，不暴露文件路径。

`packages/pet-protocol`：

- 定义 PetEvent JSON Schema 作为协议事实源。
- 已定义 TypeScript 类型、JSON Schema、level/action/sound/hardware capabilities 和 fixtures。
- 不依赖 desktop、CLI 或 future adapters。

`packages/petctl`：

- CLI client，不是 Event Bridge 的组成部分。
- 复用 pet-protocol 校验。
- 通过 HTTP 写入桌面 App。

## 3. Future Architecture

阶段 2：

```text
Codex / Claude Code / MCP clients
  -> future skills / future pet-mcp adapter
  -> same HTTP event bridge
  -> same CatStateMachine
```

阶段 3：

```text
CatStateMachine
  -> future serial hardware adapter
  -> USB ambient light

Cat renderer
  -> future Rive / Live2D / Spine / GLTF renderers
```

所有后续模块必须复用同一安全边界：

- Agent 只能发送结构化事件。
- Agent 不能直接控制 UI。
- Agent 不能执行本地脚本。
- Agent 不能传入本地资源路径。
- 动作、声音、硬件效果必须白名单。
- 本地 API 只监听 `127.0.0.1`。

## 4. Runtime Flow

```text
1. Agent 或脚本产生状态事件。
2. HTTP caller 或 petctl CLI client 将事件提交到 Rust Local Event Bridge。
3. Event Bridge 鉴权、JSON Schema 校验、过滤和限流。
4. 合法事件进入 Rust Ingress Queue，并更新最近合法摘要；非法事件更新最近拒绝摘要且不执行。
5. CatStateMachine 的 Behavior Queue 处理优先级、冷却、打断和 next state。
6. Renderer 播放占位动作。
7. Sound service 按白名单、level、静音和 cooldown 播放必要声音。
8. Settings 展示 API 状态、最近合法/非法事件摘要和 sound diagnostics。
```

## 5. Explicit Non-Goals For MVP

- 不实现 MCP server。
- 不实现 Codex / Claude Code Skill 完整包。
- 不实现 USB serial adapter 或 mock hardware。
- 不实现 Rive / Live2D / Spine / GLTF。
- 不实现照片自定义或动态猫生成。
- 不实现团队协作中枢。
- 不实现自动更新和正式签名发布。
- 不声明 cross-platform ready；Windows smoke test 后续 Phase 8 单独完成。
