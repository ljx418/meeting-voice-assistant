# 总体架构

## 产品目标

`agent-desktop-pet` 是一只可常驻桌面的开发者猫。它把 Codex、Claude Code 和自定义 AI Agent 的后台状态转译为低打扰桌面反馈，让开发者不用频繁切屏或盯终端，也能通过余光感知任务进度、异常和待处理事项。

设计原则：

- 第一体验是可常驻的桌面猫，不是通用桌面宠物，也不是通知中心。
- 外部 Agent 只能写入结构化事件，不能直接控制 UI。
- Tauri Rust side 内嵌 `Rust Local Event Bridge`，负责本地 HTTP、鉴权、校验、限流、Ingress Queue 和入站摘要。
- `petctl` 是 CLI client，不是 Event Bridge 的组成部分。
- `pet-mcp` 是未来 adapter，skills 是未来 agent instruction layer，均不进入 MVP。
- 声音、动作、硬件效果全部使用白名单 ID。
- 本地 API 只监听 `127.0.0.1`。
- 协议事实源使用 JSON Schema 或等价跨语言 schema，TypeScript 和 Rust 都必须基于同一协议校验。

## MVP 架构图

```text
+--------------------+       +--------------------+
| Custom Agent       |       | Developer Scripts  |
| local process      |       | shell / npm / etc  |
+---------+----------+       +----------+---------+
          |                             |
          | HTTP                        | petctl CLI client
          v                             v
+-------------------------------------------------+
|        Tauri Rust Side: Local Event Bridge       |
|                                                 |
| - HTTP API 127.0.0.1 only                       |
| - token auth                                    |
| - JSON Schema PetEvent validation               |
| - action / sound / hardware effect whitelist    |
| - rate limit                                    |
| - Rust Ingress Queue                            |
| - latest accepted/rejected summaries            |
| - Safe Sound service                            |
+-----------------------+-------------------------+
                        |
                        | Tauri event / command
                        v
+-------------------------------------------------+
|           Tauri WebView: TypeScript Frontend     |
|                                                 |
| - CatStateMachine                               |
| - Behavior Queue                                |
| - placeholder cat renderer                      |
| - local state animation                         |
| - low interruption display rules                |
| - settings page / diagnostics summary           |
+-----------------------+-------------------------+
                        |
                        v
+-------------------------------------------------+
|        Desktop Pet Window + System Tray          |
| transparent / frameless / always-on-top          |
| draggable small pet window                       |
+-------------------------------------------------+
```

## Post-MVP 扩展关系

```text
Future pet-mcp adapter
  -> same HTTP/Event Bridge contract

Future Codex / Claude Code skills
  -> instruction layer that calls petctl or HTTP

Future serial hardware module
  -> consumes validated behavior/hardware intent

Future Rive / Live2D / GLTF renderers
  -> replace renderer only, not event bridge or protocol
```

## 事件流

1. Agent 或脚本产生状态事件。
2. 事件通过 HTTP caller 或 `petctl` CLI 提交。
3. Tauri Rust side 的 Local Event Bridge 执行 token 鉴权、JSON Schema 校验、白名单校验、速率限制和日志记录。
4. 合法事件更新最近合法摘要；非法事件更新最近拒绝摘要且不执行。
5. Rust side 将合法事件推送到 TypeScript 前端。
6. TypeScript Behavior Queue 根据优先级、冷却、打断规则和低打扰策略决定动作。
7. 前端渲染猫咪动作。
8. Rust Sound service 根据 level、sound ID、静音和 cooldown 决定是否播放内置短提示音。

## MVP 明确不包含

- MCP server。
- Codex / Claude Code Skill 完整包。
- USB 真实或 mock 硬件。
- Rive / Live2D / Spine / GLTF / GLB。
- 照片自定义猫咪。
- 团队协作中枢。
- 自动更新和正式签名发布。
