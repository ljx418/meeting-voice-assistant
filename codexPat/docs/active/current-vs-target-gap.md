# Current vs Target Gap

文档状态：docs baseline ready；Phase 1 complete；Phase 2 complete；Phase 3 complete；Phase 4 complete；Phase 5 complete；Phase 6 complete。  
配套图：`current-vs-target-gap.drawio`。
V1.0 归档：`docs/V1.0/`。
V2.0 基线：`docs/V2.0/`。

本文与 drawio 图是后续开发、验收和范围控制的核心维护文件。本文承载文字合同，drawio 承载同一套当前状态、目标架构、差距矩阵、开发计划摘要和验收计划。

## 1. 文档定位

本文只描述 agent-desktop-pet 从当前 Phase 6 实现状态到后续跨平台硬化状态之间的差距。

MVP 不是：

- 完整 MCP server。
- Codex / Claude Code Skill 完整包。
- USB 氛围灯真实实现。
- USB mock 硬件。
- Rive / Live2D / 3D 猫。
- 照片自定义或一键生成完整动态猫。
- 团队协作状态中枢。
- 正式签名发布。

第一阶段 MVP 要回答的问题是：

> 开发者能否通过一个低打扰桌面猫，感知本地 AI Agent 的后台状态、异常和待处理事项。

第一阶段 MVP 采用 macOS-first 验收口径。Windows 仍是产品方向，但不作为第一阶段验收阻塞项；Windows 启动、托盘、HTTP API 和 petctl smoke test 移到后续跨平台硬化阶段。

## 2. 当前状态

当前仓库事实：

- 已有 README 和 docs 设计文档。
- 已有产品体验北极星、总体架构、技术选型、协议、状态机、窗口、资产、集成、硬件、风险等文档草案。
- 已有 `apps/desktop` Tauri 2 + Vite + TypeScript Phase 1 桌面壳实现。
- 已有透明、无边框、置顶、小尺寸占位猫窗口配置。
- 已有 CSS 占位猫 idle 动画、窗口拖拽、位置/静音/显示状态持久化。
- 已有 Tauri 2 tray/menu 托盘、显示设置、静音、显示/隐藏、重置位置、退出。
- 已有占位设置页，包含静音状态、窗口位置、猫咪大小占位和事件日志空状态。
- 已有 Phase 2 前端 `CatStateMachine` 和本地 Behavior Queue。
- 已有本地 debug 状态触发入口。
- 已有 idle、thinking、running、success、warning、error、need_input、sleeping 的 CSS 占位动画。
- 设置页可显示当前状态和队列长度快照。
- Phase 1/2 自动检查已通过：`pnpm check/build`、`cargo check`、`tauri build -b app`。
- `tauri dev` 已可启动；2026-05-15 Phase 2 视觉验收已通过。
- Phase 3 已有 Rust Local Event Bridge，监听 `127.0.0.1:17321`。
- Phase 4 已有轻量 Rust Ingress Queue、事件摘要 ring buffer 和 diagnostics API。
- `packages/pet-protocol` 已实现，包含 JSON Schema、TypeScript 类型、capabilities 和 fixtures。
- Phase 5 已完成 `packages/petctl` 和 `petctl notify`，支持参数模式、JSON stdin、本地校验、token/url 读取和 localhost HTTP 写入。
- 尚无真实事件日志；Phase 6 已实现内置声音播放、静音联动、cooldown 和 diagnostics sound 字段。

当前可以声明：

```text
agent-desktop-pet docs baseline ready.
Phase 1 complete: desktop shell and placeholder pet window ready.
Phase 2 complete: local low-interruption state machine and placeholder state animations ready.
Phase 3 complete: local PetEvent protocol and localhost HTTP event bridge ready.
Phase 4 complete: observable event runtime and settings diagnostics ready.
Phase 5 complete: petctl CLI can notify the local desktop pet through localhost HTTP API.
Phase 6 complete: safe sound feedback implemented.
macOS-first MVP ready: local desktop agent status pet with HTTP + petctl integration and safe sound feedback.
```

当前不能声明：

```text
MCP/Skill ready
cross-platform build ready
cross-platform MVP ready
```

## 3. 目标状态

第一阶段 MVP 完成后应具备：

- macOS 可运行并可打包的 Tauri 桌面应用。
- 透明、无边框、置顶、可拖拽占位猫窗口。
- 系统托盘：设置、静音、显示/隐藏、退出。
- 占位动画与低打扰状态机。
- 本地 HTTP API，只监听 `127.0.0.1`。
- PetEvent schema 校验、白名单过滤、速率限制、事件队列、事件日志。
- TypeScript 和 Rust 基于同一 JSON Schema 或等价跨语言 schema 校验 PetEvent。
- `petctl notify` CLI。
- 基础声音白名单。
- 基础设置页。

当前 macOS-first MVP 可声明：

```text
macOS-first MVP ready: local desktop agent status pet with HTTP + petctl integration and safe sound feedback.
```

## 4. 当前实现架构

```text
+------------------------+
| README + docs          |
| apps/desktop           |
| - Tauri shell          |
| - transparent pet win  |
| - placeholder cat CSS  |
| - local state machine  |
| - tray/settings        |
+-----------+------------+
            |
            v
+------------------------+
| Phase 5 local runtime  |
| - Rust HTTP bridge     |
| - pet-protocol schema  |
| - diagnostics logs     |
| - petctl CLI client    |
| - sound ID whitelist   |
+------------------------+
```

## 5. 目标项目架构

```text
Custom Agent / Scripts
  -> HTTP caller or petctl CLI client
  -> Rust Local Event Bridge
  -> JSON Schema PetEvent validation / whitelist / queue / logs
  -> TypeScript CatStateMachine
  -> placeholder cat renderer + sound whitelist
  -> transparent Tauri desktop pet window
```

后续扩展：

```text
future pet-mcp / future skills / serial hardware / Rive-Live2D-3D
  -> reuse same PetEvent and event bridge
```

## 6. Gap Matrix

| Gap | 当前状态 | MVP 目标 | 阶段 |
| --- | --- | --- | --- |
| Desktop shell | Phase 1 已完成；透明、无边框、置顶、拖拽、托盘、设置页可用。 | 保持回归不破坏。 | Phase 1 |
| State machine | Phase 2 已完成；本地 TS runtime、Behavior Queue、debug 入口、状态 CSS 动画和人工视觉验收通过。 | 后续接入真实 PetEvent 后继续复用。 | Phase 2 |
| PetEvent protocol | Phase 3 已实现 JSON Schema、TypeScript 类型、白名单和 fixtures。 | 后续由 petctl/MCP/Skill 复用同一协议。 | Phase 3 |
| Cross-language schema | Phase 3 已以 JSON Schema 作为单一事实源，Rust 直接加载同一 schema。 | 后续补充更多一致性测试。 | Phase 3 |
| Local HTTP API | Phase 3 已实现 `127.0.0.1:17321` health/capabilities/events；Phase 5 已由 petctl 复用。 | 后续给 MCP/Skill adapter 复用。 | Phase 3/5 |
| Security boundary | Phase 4 已实现 token、schema、白名单、限流、queue_full 和 rejected summary；Phase 5 petctl 复用同一边界。 | 后续接入仍保持同一边界。 | Phase 3/4/5 |
| Event queue/logs | 已有前端 Behavior Queue；Phase 4 已实现轻量 Rust Ingress Queue 和内存事件摘要。 | 后续可继续增强但不引入通知中心。 | Phase 4 |
| Settings page | 已显示静音、位置、当前状态、队列长度、API diagnostics、sound diagnostics 和最近事件摘要。 | 后续做 macOS MVP 使用说明收口。 | Phase 4/6 |
| petctl CLI | Phase 5 已实现参数模式和 JSON stdin。 | 后续可给 MCP/Skill 复用。 | Phase 5 |
| Sound whitelist | Phase 6 已实现内置 sound ID、冷却、静音联动播放；仍禁止路径/URL。 | 后续保持回归不破坏。 | Phase 6 |
| macOS MVP exit | Phase 6 已完成 macOS build、HTTP + petctl + sound 的低打扰闭环验证和使用说明更新。 | 后续保持回归不破坏。 | Phase 6 |
| Windows hardening | 尚未做 Windows smoke。 | 后续完成 Windows 启动、托盘、HTTP API、petctl smoke test 后，才允许声明 cross-platform ready。 | Phase 8 |

## 7. 开发计划摘要

| Phase | 目标 | 完成后可声明 |
| --- | --- | --- |
| Phase 1 | 桌面壳与占位猫。 | Phase 1 complete。 |
| Phase 2 | 占位动画与低打扰状态机。 | Phase 2 complete。 |
| Phase 3 | pet-protocol 与本地 HTTP API。 | Phase 3 complete。 |
| Phase 4 | 事件队列、日志和设置页。 | Phase 4 complete。 |
| Phase 5 | petctl CLI。 | Phase 5 complete。 |
| Phase 6 | 声音白名单与低打扰打磨。 | Phase 6 complete。 |
| Phase 7 | macOS MVP 打包验证与收口。 | 已并入 Phase 6。 |
| Phase 8 | Windows 跨平台验证与硬化。 | cross-platform ready。 |

## 8. 验收计划摘要

MVP 出门验收：

- 窗口：透明、无边框、置顶、可拖拽、位置持久化。
- 托盘：设置、静音、显示/隐藏、退出。
- API：只监听 `127.0.0.1`，health/events/capabilities 可用。
- 安全：token、schema、白名单、限流、非法事件日志。
- 协议：TypeScript 与 Rust 基于同一 JSON Schema 或同一批 fixtures 校验。
- 状态机：优先级、冷却、打断、队列、低打扰规则。
- CLI：petctl 可写入事件，错误反馈清晰；Phase 5 已完成 macOS 本地 smoke。
- 声音：只允许 sound ID，静音全局生效。
- 日志：合法事件和非法事件摘要可查看。
- 体验：thinking/running 低打扰，error/need_input 明显但克制。

## 9. 下一步第一条编码任务

```text
请在当前仓库实现 agent-desktop-pet 的第一阶段 MVP 桌面壳。创建最小 Tauri 2 + Vite + TypeScript 应用，只实现：透明无边框置顶小窗口、可拖拽占位猫、位置持久化、系统托盘（设置、静音、显示/隐藏、退出）和占位设置页。不要实现 HTTP API、pet-protocol、petctl、MCP、USB、3D、Live2D、Rive、照片生成或任何 agent 接入逻辑。
```
