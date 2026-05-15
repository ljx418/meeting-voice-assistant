# V2.0 Scope Boundaries

文档状态：V2.0 planning baseline。

## 1. V2.0 做什么

V2.0 聚焦真实本地开发工作流接入和可用性打磨：

- Codex / Claude Code instruction template。
- `petctl` recipes。
- shell / Node 示例。
- settings 与 diagnostics 可读性优化。
- README、doctor、troubleshoot、macOS 分发准备。
- 现有 CSS 猫咪体验 polish。
- V1.0 安全边界和回归不破坏。

## 2. V2.0 不做什么

V2.0 不做：

- MCP server。
- USB。
- Windows ready 声明。
- cross-platform ready 声明。
- Live2D / Rive / 3D。
- 照片自定义。
- 自动更新。
- 正式签名。
- 团队协作中枢。
- 复杂通知中心。
- 持久化日志数据库。

## 3. 安全边界

V2.0 必须继承 V1.0 的安全边界：

- Agent 只能写入结构化 PetEvent。
- Agent 不能直接控制 UI。
- Agent 不能执行任意本地脚本。
- Agent 不能传入本地文件路径、相对路径、绝对路径或 URL 作为 sound/resource。
- sound 只能是内置白名单 ID。
- hardware effect 只能是白名单 ID；V2.0 不控制 USB 硬件。
- diagnostics 不暴露 token、原始 payload、metadata 全量、message 全文或声音路径。
- 高频事件必须受 rate limit、queue 和 cooldown 约束。

## 4. 架构边界

V2.0 继续使用 V1.0 架构：

```text
local workflow / agent template / script
  -> petctl or localhost HTTP
  -> Rust Local Event Bridge
  -> PetEvent schema / whitelist / token / rate limit
  -> diagnostics / ingress queue
  -> Tauri event
  -> TypeScript CatStateMachine
  -> low-interruption cat feedback
```

不改变：

- Rust Local Event Bridge 仍内嵌在 Tauri desktop app。
- `petctl` 仍是 CLI client，不是 event bridge。
- Codex / Claude Code template 仍是 instruction layer，不是 MCP server。
- USB、MCP、Rive/Live2D/3D 仍是后续扩展。

## 5. 声明边界

允许声明：

```text
V2.0 ready: local agent workflow integration and developer usability polish complete.
Codex and Claude Code local workflow templates ready.
```

禁止声明：

```text
MCP server ready
USB hardware ready
Windows ready
cross-platform ready
production signed release ready
auto update ready
Live2D/Rive/3D ready
photo customization ready
team collaboration hub ready
```

