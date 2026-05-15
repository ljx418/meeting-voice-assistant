# agent-desktop-pet

`agent-desktop-pet` 是一只可常驻桌面的开发者猫，用来把 Claude Code、Codex 和自定义 AI Agent 的后台状态转译为低干扰、可感知的桌面反馈。它不是通用桌面宠物，也不是通知中心或聊天机器人。

## 文档导航

- [Docs Map：文档分层与维护规则](docs/README.md)
- [V1.0 归档：macOS-first MVP baseline](docs/V1.0/README.md)
- [V2.0 基线：Developer Workflow Integration Release](docs/V2.0/README.md)
- 当前阶段执行文档：
  - [开发计划](docs/active/development-plan.md)
  - [验收计划](docs/active/acceptance-plan.md)
  - [当前实现与目标差距](docs/active/current-vs-target-gap.md)
- 长期蓝图：
  - [产品体验北极星](docs/blueprint/00-product-experience.md)
  - [总体架构](docs/blueprint/00-overview.md)
  - [目标架构](docs/blueprint/target-architecture.md)
  - [技术选型](docs/blueprint/01-tech-stack.md)
  - [Monorepo 结构](docs/blueprint/02-monorepo-structure.md)
  - [PetEvent 协议](docs/blueprint/03-pet-event-protocol.md)
  - [猫咪状态机](docs/blueprint/04-cat-state-machine.md)
  - [桌面窗口设计](docs/blueprint/05-desktop-window.md)
  - [风险与技术决策](docs/blueprint/10-risks-and-decisions.md)
- 后续参考：
  - [猫咪资产包](docs/reference/06-cat-pack.md)
  - [Integrations Reference：petctl MVP，MCP/Skill Post-MVP](docs/reference/07-integrations.md)
  - [USB 氛围灯扩展：Post-MVP](docs/reference/08-hardware-light.md)
  - [Post-MVP Roadmap](docs/reference/post-mvp-roadmap.md)
- 工程运维：
  - [开发环境配置](docs/ops/developer-setup.md)
  - [网络镜像与下载加速](docs/ops/network-mirrors.md)
  - [发布与快速部署](docs/ops/release-and-distribution.md)

## MVP 固定范围

第一版应该实现：

- Tauri 2 + Rust + Vite + TypeScript 桌面 App。
- 透明、无边框、置顶、可拖拽猫咪窗口。
- 默认 2D sprite 猫咪。
- 系统托盘：显示设置、静音、暂停事件、退出。
- 低打扰状态机：idle、thinking、running、success、warning、error、need_input、sleeping。
- 本地 HTTP API，只监听 `127.0.0.1`。
- `PetEvent` schema 校验、token 鉴权、速率限制、事件队列。
- `petctl notify` CLI。
- 基础声音白名单。
- 基础设置页：静音、显示/隐藏、猫咪大小、事件日志。

第一版不做：

- 照片直接生成完整动态 3D 猫。
- Live2D 自动绑定或编辑器。
- 默认点击穿透。
- 全局鼠标 hook。
- USB 真实或 mock 硬件。
- 完整 MCP server。
- Codex / Claude Code Skill 完整包。
- 照片自定义猫咪。
- 团队协作中枢。
- 自动更新和正式签名发布。
- 强状态仪表盘或通知中心。
- agent 直接控制 UI、执行脚本、传入本地资源路径。

## 第一条实现 Prompt

```text
请在当前仓库实现 agent-desktop-pet 的第一阶段 MVP 桌面壳。创建最小 Tauri 2 + Vite + TypeScript 应用，只实现：透明无边框置顶小窗口、可拖拽占位猫、位置持久化、系统托盘（设置、静音、显示/隐藏、退出）和占位设置页。不要实现 HTTP API、pet-protocol、petctl、MCP、USB、3D、Live2D、Rive、照片生成或任何 agent 接入逻辑。
```

## Phase 1：桌面壳与占位猫

Phase 1 的目标是验证第一体验：一只可常驻桌面的开发者猫，能以透明、无边框、置顶的小窗口形式运行，可拖拽，并可通过系统托盘控制。

### 开发启动命令

```bash
pnpm install
pnpm --filter desktop tauri dev
```

前端静态检查：

```bash
pnpm --filter desktop check
```

开发环境诊断：

```bash
pnpm run doctor
```

Tauri 构建检查：

```bash
pnpm --filter desktop tauri build -b app
```

Phase 1 只要求 macOS `.app` bundle 构建通过；`.dmg` 属于后续正式发布打包验证。

### Phase 1 已实现

- 最小 `apps/desktop` Tauri 2 + Vite + TypeScript 应用。
- 透明、无边框、置顶、小尺寸占位猫窗口。
- CSS 占位猫，默认 idle，带轻微呼吸、浮动、眨眼和尾巴摆动动画。
- 鼠标按住猫咪区域拖拽窗口。
- 使用跨平台 app config 目录持久化窗口位置、静音状态和显示状态。
- 启动时恢复位置；保存位置不可见时重置到主屏幕安全区域。
- Tauri 2 tray/menu API 系统托盘：显示设置、静音/取消静音、显示/隐藏猫咪、重置位置、退出。
- 占位设置页：静音状态、当前窗口位置、猫咪大小入口、事件日志空状态。

### Phase 1 明确未实现

- HTTP API。
- PetEvent。
- `pet-protocol`。
- Rust Local Event Bridge。
- Rust Ingress Queue。
- TypeScript Behavior Queue。
- `petctl` CLI。
- MCP server。
- Codex / Claude Code Skill。
- USB 真实或 mock 硬件。
- Rive / Live2D / 3D。
- 照片自定义猫咪。
- 自动更新。
- 正式签名发布。
- 点击穿透。
- 全局鼠标监听。
- 跨屏自动游走。
- 复杂状态机。

### macOS smoke test 清单

只有实际运行并观察到窗口后，才能声明 macOS smoke test 通过。

- 启动后 10 秒内看到占位猫。
- 主窗口透明、无边框、置顶、小尺寸。
- idle 动画可见，且不会造成窗口尺寸抖动。
- 鼠标按住猫咪区域可以拖拽窗口。
- 拖拽后重启，位置被恢复。
- 保存位置超出当前显示器可见区域时，自动回到主屏幕安全区域。
- 托盘图标出现。
- 托盘菜单能打开设置、静音/取消静音、显示/隐藏猫咪、重置位置、退出。
- 设置窗口关闭不影响猫咪主窗口。
- 退出后应用完整关闭。

### Windows smoke test 后续清单

Windows 不进入第一阶段 MVP 验收，不阻塞当前 macOS-first 目标。后续声明 cross-platform ready 前，必须在 Windows 完成以下检查：

- 应用能启动并显示占位猫。
- 透明、无边框、置顶窗口行为正常。
- 拖拽正常。
- 托盘菜单可用。
- 设置窗口可用。
- 配置写入 Windows app config 目录，而不是 macOS 路径。
- 退出无残留进程。

### No False-Green

Phase 1 完成后最多只能声明：

```text
Phase 1 complete: desktop shell and placeholder pet window ready.
```

不得声明：

- MVP ready。
- Agent integration ready。
- HTTP API ready。
- PetEvent ready。
- petctl ready。
- MCP/Skill ready。
- USB ready。
- cross-platform ready，除非 Windows 已实际 smoke test。

## Phase 2：低打扰状态机与占位状态动画

Phase 2 的目标是在不接入真实 Agent 的前提下，让猫能通过本地状态机表达开发者可感知的低打扰状态。

### Phase 2 已实现

- `CatStateMachine`：位于 `apps/desktop/src/state-machine.ts`。
- 状态配置：位于 `apps/desktop/src/pet-states.ts`。
- 本地 Behavior Queue，最大长度 8。
- 支持状态：idle、thinking、running、success、warning、error、need_input、sleeping。
- 主窗口 hover 后显示本地 debug 触发入口。
- CSS class 占位状态动画。
- 设置页显示当前状态和队列长度。
- 拖拽期间动画暂停/延后，拖拽优先于状态动画。

### Phase 2 明确未实现

- HTTP API。
- PetEvent。
- `pet-protocol`。
- Rust Local Event Bridge。
- `petctl` CLI。
- MCP / Skill。
- USB。
- 声音系统。
- 真实事件日志。
- Rive / Live2D / 3D。

### Phase 2 验收

已通过自动检查：

```bash
pnpm run doctor
pnpm --filter desktop check
pnpm --filter desktop build
cargo check --manifest-path apps/desktop/src-tauri/Cargo.toml
pnpm --filter desktop tauri build -b app
pnpm --filter desktop tauri dev
```

2026-05-15 人工视觉验收已通过：

- debug 入口能触发全部 8 个状态。
- 各状态动画可区分且低打扰。
- success 短反馈后回 idle。
- error / need_input 锁定期不被 running / thinking 打断。
- 拖拽、托盘、设置页不回归。
- 透明窗口无黑框。

Phase 2 完成后最多只能声明：

```text
Phase 2 complete: local low-interruption state machine and placeholder state animations ready.
```

## Phase 3：pet-protocol 与本地 HTTP API

Phase 3 的目标是打通第一条真实本地写入链路：HTTP -> Rust Local Event Bridge -> schema / 白名单 / token / rate limit -> Tauri event -> 前端 CatStateMachine。

### Phase 3 已实现

- `packages/pet-protocol`：以 `schemas/pet-event.schema.json` 作为 PetEvent 单一事实来源。
- TypeScript 类型、capabilities、合法/非法 fixtures 和 schema 一致性测试。
- Rust Local Event Bridge 内嵌在 Tauri Rust side，只监听 `127.0.0.1:17321`。
- `GET /api/health`、`GET /api/capabilities`、`POST /api/events`。
- `POST /api/events` 执行 Bearer token、JSON Schema、白名单、metadata 4KB 和基础 rate limit 校验。
- 合法事件通过 `pet-event:accepted` Tauri event 推送给前端状态机。
- 设置页显示 API enabled、监听地址、最近合法事件摘要和最近非法事件摘要。

### Phase 3 明确未实现

- `petctl` CLI。
- MCP server。
- Codex / Claude Code Skill。
- USB 真实或 mock 硬件。
- 声音播放。
- Rive / Live2D / 3D。
- 照片自定义。
- 自动更新和正式签名发布。
- 完整事件日志 UI 和事件日志清空。

### Phase 3 本地验证

```bash
pnpm --filter @agent-desktop-pet/pet-protocol check
pnpm --filter @agent-desktop-pet/pet-protocol test
pnpm --filter desktop check
pnpm --filter desktop build
cargo check --manifest-path apps/desktop/src-tauri/Cargo.toml
pnpm --filter desktop tauri build -b app
```

HTTP smoke：

```bash
curl http://127.0.0.1:17321/api/health
curl http://127.0.0.1:17321/api/capabilities
```

写入事件必须携带本地 token：

```bash
curl -X POST http://127.0.0.1:17321/api/events \
  -H "Authorization: Bearer <local-token>" \
  -H "Content-Type: application/json" \
  -d '{"source":{"id":"custom.local","kind":"custom"},"level":"success","title":"测试通过","action":"success","sound":"success_chime","durationMs":3000}'
```

Phase 3 完成后最多只能声明：

```text
Phase 3 complete: local PetEvent protocol and localhost HTTP event bridge ready.
```

## Phase 4：事件可观察性与运行稳定性

Phase 4 的目标是把 Phase 3 HTTP 写入链路做成可观察、可调试、可验收的 runtime。

### Phase 4 已实现

- Rust side 轻量 Ingress Queue，容量 32。
- `thinking` / `running` 同 source pending 事件合并。
- 合法事件和非法事件内存 ring buffer，各保留最近 50 条摘要。
- `EventSummary` 只保存摘要：id、receivedAt、sourceId、level、titlePreview、messagePreview、status、accepted、reasonCode、reason。
- 不保存原始 payload，不保存 metadata 全量，不保存 message 全文。
- 新增 `GET /api/diagnostics`，必须 Bearer token。
- 设置页展示 API enabled、listen address、queue length/capacity、最近合法/非法事件、sound playback=false、hardware light=false。

### Phase 4 明确未实现

- `petctl` CLI。
- MCP / Skill。
- USB。
- 声音播放。
- 日志持久化数据库。
- 日志清空、导出、搜索、分页。
- token 重置 UI。
- Windows ready 声明。

Phase 4 完成后最多只能声明：

```text
Phase 4 complete: observable event runtime and settings diagnostics ready.
```

## Phase 5：petctl CLI 接入

Phase 5 的目标是让自定义 agent 或 shell script 通过命令行写入桌宠状态。

### Phase 5 已实现

- `packages/petctl`。
- `petctl notify` 参数模式。
- `petctl notify --json` stdin 模式。
- 复用 `packages/pet-protocol` 的 TypeScript 类型、capabilities 和 JSON Schema 校验。
- 默认 POST 到 `http://127.0.0.1:17321/api/events`。
- URL 读取优先级：`--url`、`AGENT_DESKTOP_PET_URL`、默认 localhost。
- token 读取优先级：`--token`、`AGENT_DESKTOP_PET_TOKEN`、desktop app config `api-token.json`。
- 成功输出 `eventId`，失败输出 `reasonCode` 和 `reason`。
- 本地校验失败不会发送 HTTP 请求。

### Phase 5 使用示例

```bash
pnpm --filter @agent-desktop-pet/petctl build
pnpm --filter @agent-desktop-pet/petctl petctl -- notify --level success --title "CLI 测试通过"
```

JSON stdin：

```bash
cat <<'JSON' | pnpm --filter @agent-desktop-pet/petctl petctl -- notify --json
{
  "source": {
    "id": "script.local",
    "kind": "custom",
    "name": "Script"
  },
  "level": "running",
  "title": "脚本正在执行",
  "durationMs": 3000
}
JSON
```

Phase 5 完成后最多只能声明：

```text
Phase 5 complete: petctl CLI can notify the local desktop pet through localhost HTTP API.
```

### Phase 5 验收记录

2026-05-15 已完成：

- `pnpm --filter @agent-desktop-pet/petctl check`。
- `pnpm --filter @agent-desktop-pet/petctl test`。
- 参数模式 `petctl notify --level success --title "CLI 测试通过"` 写入成功。
- JSON stdin 模式写入成功。
- 非法 level 和非法 sound 在本地校验阶段被拒绝，不发送 HTTP。
- 高频 running 请求触发 `rate_limited`，diagnostics 中出现 rejected summary。
- 桌面 App 未启动时返回 `desktop_not_running`。

## Phase 6：Safe Sound Feedback + macOS-first MVP 收口

Phase 6 的目标是补齐第一阶段 macOS-first MVP 的最后体验闭环：内置、低打扰、可静音、受 cooldown 控制的声音反馈。

### Phase 6 已实现

- 内置 sound ID：`none`、`success_chime`、`warning_chime`、`error_chime`、`need_input_chime`。
- 声音资源位于 Tauri bundle 内，只通过 sound ID 映射访问。
- `thinking` / `running` / `idle` / `sleeping` 默认不播放声音。
- `success`、`warning`、`error`、`need_input` 按低打扰策略播放内置短提示音。
- `need_input` 等高频提示受 cooldown 控制。
- 托盘和设置页静音状态会跳过所有声音。
- diagnostics 返回结构化 `sound` 字段，不暴露声音文件路径。
- 非法 sound 路径、URL、未知 ID 仍会被 schema/白名单拒绝。

### Phase 6 使用示例

```bash
pnpm --filter @agent-desktop-pet/petctl petctl -- notify \
  --level success \
  --sound success_chime \
  --title "声音测试通过"
```

静默状态示例：

```bash
pnpm --filter @agent-desktop-pet/petctl petctl -- notify --level running
```

Phase 6 完成后，自动检查、端到端 smoke、文档同步未全部完成前最多只能声明：

```text
Phase 6 complete: safe sound feedback implemented.
```

全部验收通过后可以声明：

```text
macOS-first MVP ready: local desktop agent status pet with HTTP + petctl integration and safe sound feedback.
```

仍不能声明：

- cross-platform ready。
- MCP/Skill ready。
- USB ready。
- production signed release ready。
- Windows ready。
