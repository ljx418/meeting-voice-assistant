# agent-desktop-pet V1.0 Archive

文档状态：V1.0 macOS-first MVP baseline archived。

V1.0 对应原 Phase 1-7 范围；Phase 7 已并入 Phase 6 的 macOS-first MVP Acceptance Closure。本文档夹是 V1.0 设计、架构、协议和验收的压缩归档，后续阶段以此作为不可回退的产品与技术基线。

## V1.0 定位

`agent-desktop-pet` 是一只可常驻桌面的开发者猫。它把本地 AI Agent 的后台状态转译为低打扰桌面反馈，让开发者不用频繁切屏或盯终端，也能通过余光感知任务进度、异常和待处理事项。

V1.0 不是：

- 通用桌面宠物。
- 通知中心。
- 聊天机器人。
- MCP server。
- Codex / Claude Code Skill 完整包。
- USB 硬件联动系统。
- Windows 已验收版本。
- 正式签名发布版本。

## V1.0 可声明

```text
Phase 1 complete: desktop shell and placeholder pet window ready.
Phase 2 complete: local low-interruption state machine and placeholder state animations ready.
Phase 3 complete: local PetEvent protocol and localhost HTTP event bridge ready.
Phase 4 complete: observable event runtime and settings diagnostics ready.
Phase 5 complete: petctl CLI can notify the local desktop pet through localhost HTTP API.
Phase 6 complete: safe sound feedback implemented.
macOS-first MVP ready: local desktop agent status pet with HTTP + petctl integration and safe sound feedback.
```

## V1.0 不可声明

```text
cross-platform ready
Windows ready
MCP/Skill ready
USB ready
production signed release ready
auto update ready
```

## 归档文件

- `v1_0-architecture.md`：压缩后的目标体验、模块职责和运行架构。
- `v1_0-protocol-and-security.md`：PetEvent、HTTP API、petctl、安全边界。
- `v1_0-acceptance.md`：V1.0 自动检查、端到端 smoke 和验收口径。
- `v1_0-roadmap.md`：V1.0 之外的后续阶段。
- `v1_0_current_gap_analysis.drawio`：V1.0 当前实现与后续差距图。

## 固化原则

- V1.0 代码基线不再混入 MCP、USB、3D、照片生成、Windows smoke 或签名发布。
- 后续功能必须复用 PetEvent、Rust Local Event Bridge、diagnostics 和低打扰状态机。
- Agent 只能写入结构化事件，不能直接控制 UI、执行脚本或传入本地资源路径。
