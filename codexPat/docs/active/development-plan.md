# Development Plan

文档状态：MVP planning baseline；Phase 1 complete；Phase 2 complete；Phase 3 complete；Phase 4 complete；Phase 5 complete；Phase 6 complete；V2.0 final acceptance passed；V2.1 planning baseline ready；V2.1-A complete。  
执行范围：后续代码实施入口；当前仓库已有 `apps/desktop` 桌面壳、占位猫、低打扰状态机、本地调试入口、状态动画、`pet-protocol`、Rust localhost HTTP event bridge、observable diagnostics runtime、`petctl notify` CLI、safe sound feedback、V2.0 本地工作流接入模板和示例、设置页 diagnostics polish、CSS 占位猫体验 polish、macOS 本地分发和用户 onboarding 文档、V2.0 final acceptance report，以及 V2.1 真实 Agent 接入验证文档和 third-party contract draft。V2.1-A third-party local HTTP contract smoke 已通过；Codex / Claude Code 真实集成仍待后续验证。

## 1. Goal

MVP 的目标是做出一个可运行、可演示、可验证的本地桌面宠物反馈层：

```text
Agent 产生状态事件
  -> 本地事件桥接收 PetEvent
  -> schema 校验与白名单过滤
  -> 状态机处理优先级、冷却、打断和队列
  -> 桌宠播放动作和必要声音
  -> 开发者通过桌面余光感知状态
```

第一版只验证 macOS 个人开发者工作台场景，不进入 Windows 验收、团队协作中枢、完整 MCP、USB 硬件、Rive/Live2D/3D 或照片动态生成。Windows 支持仍是产品目标，但移到后续跨平台硬化阶段，不阻塞第一阶段 MVP。

## 2. Scope

MVP 包含：

- Tauri 2 + Vite + TypeScript 桌面应用。
- 透明、无边框、置顶、可拖拽占位猫窗口。
- 系统托盘：设置、静音、显示/隐藏、退出。
- 占位动画：idle、thinking/walk、sleeping/sleep、running、success、warning、error、need_input。
- Rust 本地 HTTP API，只监听 `127.0.0.1`。
- `pet-protocol`：PetEvent JSON Schema、TypeScript/Rust 校验合同、白名单、capabilities。
- 事件队列、速率限制、冷却、非法事件日志。
- `petctl notify` CLI。
- 基础设置页：静音、显示/隐藏、猫咪大小、事件日志。
- 基础声音白名单。

MVP 不包含：

- 完整 MCP server。
- Codex / Claude Code Skill 完整包。
- USB 氛围灯真实或 mock 实现。
- Rive / Live2D / Spine。
- Three.js + GLTF / GLB。
- 照片一键生成完整动态猫。
- 团队协作状态中枢。
- 多只猫。
- 自动更新和正式签名发布。

## 3. Phase Plan

### Phase 1：桌面壳与占位猫

状态：已完成并验收。

目标：

- 做出可运行、可演示的桌宠窗口。

主要任务：

- 初始化最小 Tauri 2 + Vite + TypeScript 应用。
- 创建透明、无边框、置顶小窗口。
- 显示占位猫 sprite 或 CSS 图形。
- 支持拖拽和位置持久化。
- 实现系统托盘：设置、静音、显示/隐藏、退出。
- 设置页先做占位，能打开即可。

验收标准：

- 启动后 10 秒内看到猫。
- 窗口透明、无边框、置顶、可拖拽。
- 托盘菜单可静音、显示/隐藏、退出。
- 不实现 HTTP、MCP、USB、3D、照片生成。

风险：

- Tauri 透明窗口和置顶行为跨平台不一致。

Codex prompt：

```text
请在当前仓库实现 agent-desktop-pet 的第一阶段 MVP 桌面壳。创建最小 Tauri 2 + Vite + TypeScript 应用，只实现：透明无边框置顶小窗口、可拖拽占位猫、位置持久化、系统托盘（设置、静音、显示/隐藏、退出）和占位设置页。不要实现 HTTP API、pet-protocol、petctl、MCP、USB、3D、Live2D、Rive、照片生成或任何 agent 接入逻辑。
```

### Phase 2：占位动画与低打扰状态机

状态：已完成；自动验证通过；人工视觉验收已通过。

目标：

- 让猫能表达基础 agent 状态，并避免动画乱跳。

主要任务：

- 已实现 `apps/desktop/src/state-machine.ts`。
- 已实现 `apps/desktop/src/pet-states.ts`。
- 支持 idle、thinking、running、success、warning、error、need_input、sleeping。
- 实现 priority、durationMs、interruptible、lockMs、cooldownMs、next。
- 实现本地 Behavior Queue，最大长度 8。
- 增加主窗口本地调试触发器，模拟各状态。
- 设置页显示当前状态和队列长度快照。
- 普通状态默认不弹气泡、不播放声音；need_input/error 明显提醒。
- 本阶段不接 HTTP、不创建 PetEvent、不创建 pet-protocol、不创建 petctl。

验收标准：

- 连续 running 不频繁跳动画。
- need_input 可打断 running/thinking。
- error 和 need_input 有最短不可打断时长。
- success 短促反馈后回到 idle。
- 状态切换后透明窗口不出现黑框。
- 拖拽仍优先于动画。
- 托盘、设置页、显示/隐藏、重置位置、退出不回归。
- `pnpm --filter desktop check`、`pnpm --filter desktop build`、`cargo check`、`tauri build -b app` 通过。
- 2026-05-15 已完成视觉验收：低打扰状态动画、透明窗口、拖拽、托盘和设置页回归通过。

风险：

- 状态机过早复杂化；Phase 2 仅保留本地 debug 入口和前端队列，不接真实 Agent 事件。

Codex prompt：

```text
请在桌面前端实现 CatStateMachine 和开发调试触发器，支持 idle、thinking、running、success、warning、error、need_input、sleeping 的占位动画映射，包含 priority、durationMs、interruptible、cooldownMs、next、队列和低打扰展示规则。不要接外部 HTTP。
```

### Phase 3：pet-protocol 与本地 HTTP API

状态：已完成；自动验证和 HTTP smoke 已通过。

目标：

- 建立 MVP 核心链路：外部事件进入桌宠并驱动状态机。

主要任务：

- 已创建 `packages/pet-protocol`。
- 已以 `packages/pet-protocol/schemas/pet-event.schema.json` 作为 PetEvent 单一事实来源。
- 已提供 TypeScript 类型、白名单 capabilities、合法/非法 fixtures 和协议测试。
- 已实现 Rust Local Event Bridge，监听 `127.0.0.1:17321`。
- 已实现 `GET /api/health`、`POST /api/events`、`GET /api/capabilities`。
- 已加入 token 鉴权、JSON Schema 校验、白名单校验、metadata 4KB 校验、基础速率限制和最近合法/非法摘要。
- 已将合法事件通过 Tauri event 转发给前端 CatStateMachine。

验收标准：

- API 只监听 `127.0.0.1`。
- 非法 schema 返回 `400`，不执行。
- 未授权返回 `401`。
- 速率超限返回 `429`。
- 合法 success/error/need_input 能驱动猫咪动作。
- action、sound、hardware.effect 必须白名单。
- TypeScript 与 Rust 使用同一 JSON Schema 或同一批合法/非法 fixtures 校验结果一致。
- Phase 3 不播放声音、不控制硬件、不创建 petctl。

风险：

- Rust HTTP server 生命周期和 Tauri 生命周期耦合不当。

Codex prompt：

```text
请实现 packages/pet-protocol 和桌面端 Rust 本地 HTTP 事件桥。PetEvent 协议以 JSON Schema 或等价跨语言 schema 为单一事实来源，TypeScript 和 Rust 都必须基于同一协议校验。API 只监听 127.0.0.1，包含 health、events、capabilities；events 必须 token 鉴权、schema 校验、白名单校验、速率限制和事件日志；合法事件通过 Tauri event 推送给前端 CatStateMachine。
```

### Phase 4：事件队列、日志和设置页

状态：已实现；自动验证和 HTTP smoke 以最新验收记录为准。

目标：

- 让 MVP 可观察、可调试、可长期运行。

主要任务：

- 已实现 Rust side 轻量 Ingress Queue，容量 32。
- 已实现 `thinking` / `running` 同 source pending 事件合并。
- 已实现合法/非法事件 ring buffer，各保留最近 50 条摘要。
- 已实现 `GET /api/diagnostics`，必须 Bearer token。
- Phase 4 当时设置页展示 API 状态、监听地址、队列长度、最近合法/非法事件、sound playback=false、hardware light=false。
- Phase 6 已将 diagnostics 升级为结构化 `sound` 字段并实现声音播放。
- 本阶段不实现日志清空、日志导出、搜索、分页或 token 重置。

验收标准：

- 事件风暴返回 `429 rate_limited` 或 `429 queue_full`，不会导致动画失控。
- 设置页能查看最近合法/非法事件摘要。
- 非法事件有 rejected summary 但不执行。
- diagnostics 不暴露 token、原始 payload、metadata 全量或 message 全文。

风险：

- 日志、队列和 UI 状态分散，导致调试困难。

Codex prompt：

```text
请完善事件队列、事件日志和基础设置页：队列支持最大长度、同类合并、过期丢弃；设置页支持静音、显示/隐藏、猫咪大小、最近事件日志和清空日志；非法事件只记录摘要不执行。
```

### Phase 5：petctl CLI

状态：已完成；自动验证和 CLI smoke 已通过。

目标：

- 让自定义 agent 能通过命令行写入桌宠状态。

主要任务：

- 已创建 `packages/petctl`。
- 已实现 `petctl notify`。
- 已支持参数模式和 `--json` stdin。
- 已复用 `packages/pet-protocol` 本地校验。
- 已支持 token：`--token`、`AGENT_DESKTOP_PET_TOKEN`、desktop app config `api-token.json`。
- 已支持 URL：`--url`、`AGENT_DESKTOP_PET_URL`、默认 localhost。
- 错误信息区分未启动、未授权、schema 错误、速率限制和 bridge unavailable。

验收标准：

- `petctl notify --level running --title "正在测试"` 能触发 running。
- `petctl notify --level success --title "测试通过"` 能触发 success。
- 非法 sound ID 被拒绝并提示原因。
- 桌面 App 未运行时 CLI 返回可理解错误。
- CLI 不接受任意本地声音路径。
- 本地校验失败不发送 HTTP 请求。
- CLI 不打印完整 token。
- 2026-05-15 已完成 macOS 本地 CLI smoke：参数模式、JSON stdin、非法 level、非法 sound、限流和 desktop_not_running 均符合预期。

风险：

- 跨平台配置路径处理不一致。

Codex prompt：

```text
请实现 packages/petctl 的 notify 命令，支持命令行参数和 --json stdin，复用 pet-protocol 校验，读取本地 API token/port 配置，并调用 127.0.0.1 的桌面 HTTP API。错误输出要区分未启动、未授权、schema 错误和速率限制。
```

### Phase 6：声音白名单与低打扰打磨

状态：已完成；自动验证和 macOS sound smoke 已通过。

目标：

- 完成 MVP 声音体验，不让声音变成噪音源。

主要任务：

- 已实现内置 sound ID：none、success_chime、warning_chime、error_chime、need_input_chime。
- 已将 sound ID 映射到 Tauri bundle 内置 WAV 资源。
- 已禁止外部传入文件路径或 URL。
- 已加入声音冷却。
- thinking/running/idle/sleeping 默认无声音。
- success/warning/error/need_input 按低打扰策略播放内置短提示音。
- 设置页和托盘静音覆盖全部声音。
- diagnostics 已返回结构化 `sound` 字段，不暴露文件路径。

验收标准：

- 所有声音只能通过 sound ID 播放。
- 高频事件不会连续播放声音。
- 静音时无任何声音。
- need_input 声音可感知但不循环轰炸。
- 本地路径、URL、未知 sound ID 均被拒绝。
- `GET /api/diagnostics` 返回 `sound.playbackAvailable`、`sound.muted`、`sound.cooldownMs`、`sound.acceptedIds` 和 `sound.lastDecision`。

风险：

- 声音资源过多或过响，破坏低打扰体验。

Codex prompt：

```text
请实现基础声音白名单和低打扰播放策略：只允许内置 sound ID，禁止本地路径和 URL；thinking/running 默认静音；success 轻提示；warning/error/need_input 受全局 cooldown 控制；设置页静音覆盖所有声音。
```

### Phase 7：macOS MVP 打包验证与收口

状态：已并入 Phase 6 的 macOS-first MVP Acceptance Closure 执行。

目标：

- 形成 macOS-first、可演示、可验证的第一阶段 MVP。

主要任务：

- 整理 macOS 本地运行脚本和说明。
- 执行 Tauri build 验证。
- 检查窗口、托盘、API、CLI、日志、声音。
- 更新 README 的 MVP 使用说明。
- 记录点击穿透、签名、公证、置顶边界等已知限制。
- 明确 Windows 不进入第一阶段验收，只记录后续待测清单。

验收标准：

- macOS 可本地运行并打包。
- HTTP API 与 petctl 闭环可演示。
- 低打扰验收场景通过。
- README 有最小使用说明和安全边界说明。
- Windows smoke test 不作为第一阶段 MVP 验收项。

风险：

- macOS 打包签名和系统权限导致发布阻塞。

Codex prompt：

```text
请对 macOS-first MVP 做收口验证：补充 macOS 本地运行和构建脚本/说明，验证桌面窗口、托盘、HTTP API、petctl、事件摘要、声音白名单和低打扰场景；Windows 只记录待测项，不作为本阶段验收阻塞。不要加入 MCP、USB、3D、照片生成或自动更新。
```

### Phase 8：Windows 跨平台验证与硬化

目标：

- 在第一阶段 MVP 稳定后，再单独完成 Windows 运行、打包和 smoke test。

主要任务：

- 在 Windows 环境安装 Node、pnpm、Rust、Tauri 依赖、WebView2 和 C++ Build Tools。
- 验证透明、无边框、置顶窗口和托盘行为。
- 验证 app config 路径、token 文件、HTTP API 和 petctl。
- 记录 Windows 置顶、透明、托盘和安全软件兼容性问题。

验收标准：

- Windows 上应用能启动并显示占位猫。
- Windows 托盘菜单可用。
- Windows 上 `GET /api/health` 正常。
- Windows 上 `petctl notify --level success --title "测试通过"` 能触发状态变化。
- 完成后才允许声明 cross-platform ready。

风险：

- Windows WebView2、置顶窗口、透明窗口、托盘和 Defender 行为与 macOS 不一致。

Codex prompt：

```text
请在 Windows 环境对 agent-desktop-pet 做跨平台验证与硬化：验证 Tauri 启动、透明无边框置顶窗口、托盘、设置页、HTTP API、diagnostics 和 petctl notify；修复 Windows 专属问题。不要改变 macOS 已通过的 MVP 行为。
```

## 4. V2.0 Phase Plan

### Phase 2.1：Workflow Integration Templates

状态：已完成；自动检查已执行；人工 smoke 需在桌面 App 运行时完成。

目标：

- 让真实本地开发工作流可以通过现有 `petctl notify`、HTTP API、diagnostics 和安全声音能力稳定接入桌宠。

主要任务：

- 已新增 `skills/codex-agent-pet/SKILL.md`。
- 已新增 `skills/claude-agent-pet/SKILL.md`。
- 已新增 `docs/reference/agent-integration-guide.md`。
- 已新增 `docs/reference/petctl-recipes.md`。
- 已新增 `examples/shell/task-with-pet.sh`。
- 已新增 `examples/node/notify-pet.mjs`。
- 已同步 README、active 文档、V2.0 文档和 gap drawio。

验收标准：

- Codex / Claude Code 模板只通过 `petctl` 或 localhost HTTP 写入 PetEvent。
- shell 示例使用 `--` 分隔用户命令，不使用 `eval`，使用 `"$@"` 执行命令，并保留原 exit code。
- Node 示例使用 `child_process.spawnSync` 参数数组调用 `petctl notify`，不使用 `shell: true` 拼接命令。
- recipes 覆盖测试开始/通过/失败、构建开始/通过/失败、长任务、need_input、warning、JSON stdin 和常见错误排查。
- 示例不打印完整 token，不发送路径或 URL 作为 sound。
- 不声明 Codex integration verified、Claude Code integration verified、MCP server ready、USB ready、Windows ready、cross-platform ready 或 production signed release ready。

风险：

- 模板被误用为高频事件日志；文档已明确只在状态阶段变化时发送事件。

### Phase 2.2：Settings & Diagnostics Polish

状态：已完成；自动检查已执行；人工 smoke 以当前验收记录为准。

目标：

- 把 diagnostics 从工程调试数据打磨成用户能理解的运行状态面板。

主要任务：

- 已将设置页 diagnostics 分为 Runtime health、Sound、Recent accepted events、Recent rejected events 和 Quick commands。
- Runtime health 显示 API enabled、listen address、queue length/capacity、hardware light disabled、token status 和 last refresh time。
- Sound 显示 playbackAvailable、muted、cooldownMs、acceptedIds 和 lastDecision。
- accepted/rejected events 最多显示 10 条后端摘要。
- Quick commands 仅提供复制按钮，不执行 shell、petctl、node 或 curl。

验收标准：

- 设置页打开时自动加载 diagnostics。
- 刷新按钮可重新拉取 diagnostics。
- 拉取失败显示简短错误，不影响主宠物窗口。
- 页面不显示完整 token、token 文件绝对路径、原始 payload、metadata 全量、message 全文或声音文件路径。
- 不提供 token 重置、日志清空、导出、搜索、分页。
- 不改 PetEvent schema，不重写 CatStateMachine 或 Rust Ingress Queue。

风险：

- 设置页膨胀成通知中心；本阶段只保留紧凑只读面板。

### Phase 2.3：Cat Experience Polish

状态：已完成；自动检查和人工 smoke 以当前验收记录为准。

目标：

- 在不引入 Rive、Live2D、Spine、Three.js、GLTF/GLB 或照片自定义的前提下，打磨现有 CSS 占位猫体验。

主要任务：

- 已增强 idle、thinking、running、success、warning、error、need_input、sleeping 的视觉区分度。
- thinking/running 保持低打扰；success 保持短反馈。
- warning、error、need_input 的可感知程度递进，但仍由现有 lock/cooldown 控制打扰强度。
- 动画只作用于猫内部元素，不动画窗口、stage、根容器或布局尺寸。
- 拖拽期间暂停或降级猫咪内部动画，拖拽优先。
- 已增加 `prefers-reduced-motion` 兜底。

验收标准：

- 8 个状态肉眼可区分。
- 透明窗口不出现黑框、白底、阴影错位或明显脏边。
- 连续状态切换不改变 `.pet-stage` 尺寸或主窗口 outer size。
- 拖拽仍可用，拖拽期间动画不抢控制。
- Phase 1-6、V2.0 Phase 2.1、V2.0 Phase 2.2 不回归。
- 不声明 Rive、Live2D、3D、照片自定义、Windows ready 或 cross-platform ready。

风险：

- CSS 动效可能污染透明窗口边缘；因此继续禁用 `.cat-shadow`，不使用窗口级阴影或 `drop-shadow`。

### Phase 2.4：Distribution Readiness

状态：已完成；自动检查和 macOS smoke 以当前验收记录为准。

目标：

- 把 macOS-first MVP + V2.0 workflow polish 从“开发者本机能跑”整理成“新用户可以按文档快速部署、启动、验证、排障和迁移”的状态。

主要任务：

- 已重构 README 为快速入口，只保留启动、构建、验证和文档导航。
- 已新增 `docs/ops/macos-local-distribution.md`，明确当前是 local unsigned app，不是 production release。
- 已新增 `docs/ops/troubleshooting.md`，覆盖 doctor、端口、petctl、tsx IPC、unsigned app 和 token/config 问题。
- 已更新 `docs/ops/developer-setup.md`、`docs/ops/network-mirrors.md`、`docs/ops/release-and-distribution.md`。
- 已固化 token/config 说明：Tauri `app_config_dir()` 下 `api-token.json` 和 `settings.json`。
- 已同步 active、V2.0 和 drawio 状态。

验收标准：

- README 能指导新用户完成依赖安装、dev 启动、`.app` 构建、`.app` 打开、health 验证和 `petctl notify`。
- ops 文档解释环境安装、网络慢、doctor warning、token 配置、unsigned app 和常见 `petctl` 错误。
- 文档明确不声明正式签名、notarization、自动更新、Windows ready 或 cross-platform ready。
- Phase 2.4 complete 不自动等于 V2.0 ready；当前 final acceptance report 已通过，允许声明 `V2.0 ready: local agent workflow integration and developer usability polish complete.`

### V2.0 Final Acceptance & Release Closure

状态：已完成；`docs/V2.0/v2_0-final-acceptance-report.md` status 为 `passed`。

目标：

- 固化 V2.0 Phase 2.1-2.4 的交付、自动检查、macOS smoke、人工验收和声明边界。

验收结果：

- 自动 check/test/build 无 hard failure。
- `.app` bundle 可生成。
- macOS smoke 覆盖 health、petctl、unauthorized write、invalid sound、shell/Node 示例、diagnostics 和端口退出。
- 用户已确认视觉验收通过。
- README、active、V2.0、gap markdown 和 drawio 已同步。

允许声明：

```text
V2.0 ready: local agent workflow integration and developer usability polish complete.
Codex and Claude Code local workflow templates ready.
```

仍禁止声明：

```text
Codex integration verified
Claude Code integration verified
Windows ready
cross-platform ready
production signed release ready
auto update ready
MCP ready
USB ready
Rive/Live2D/3D ready
photo customization ready
```

风险：

- 用户误以为 unsigned local app 是正式发布版；README 和 release 文档已明确不是 production signed release。

## 5. V2.1 Real Agent Integration Verification

状态：planning baseline ready；V2.1-A complete；真实 Codex / Claude Code smoke 尚未执行。

目标：

- 将 Codex、Claude Code 和自定义 Agent 的接入从“模板可复制”升级为“真实可安装、可触发、可验收、可声明”。

主要任务：

- V2.1-A：Integration Baseline Audit，确认 `petctl`、HTTP API、diagnostics、templates、shell/Node examples 的当前基线。
- V2.1-B：Codex Real Integration，在真实 Codex CLI 任务中验证 `sourceId=codex.local` 的 `thinking/running/success/error/need_input`。
- V2.1-C：Claude Code Real Integration，验证 Claude Code skill 和 `settings-hooks.example.json` hook 示例，source 固定为 `claude-code.local`。
- V2.1-D：Third-party Agent Contract，补齐 `third-party-agent-contract.md`、curl/Node/Python HTTP smoke 示例和错误处理合同。
- V2.2：MCP Adapter 只做预研，不创建 `packages/pet-mcp`。

当前已落地：

- `docs/V2.1/README.md`
- `docs/V2.1/v2_1-baseline-audit.md`
- `docs/V2.1/v2_1-acceptance-plan.md`
- `docs/V2.1/v2_1-current-gap-analysis.md`
- `docs/V2.1/codex-real-integration-verification.md`
- `docs/V2.1/claude-code-real-integration-verification.md`
- `docs/V2.1/evidence/*`
- `docs/reference/third-party-agent-contract.md`
- `examples/http/*`
- `skills/claude-agent-pet/settings-hooks.example.json`
- `docs/V2.2/mcp-adapter-research.md`

允许声明：

```text
V2.1 planning baseline ready: real agent integration verification docs and third-party contract draft ready.
V2.1-A complete: integration baseline audit and local third-party HTTP contract smoke ready.
Third-party local HTTP contract smoke passed.
```

V2.1-A 验收结果：

- curl / Node / Python success smoke 已通过。
- missing token、invalid level、invalid sound path / URL、invalid source id、rate limit 均符合预期。
- diagnostics rejected summary 和 HTTP error response 不回显非法路径、URL 或非法 source 原文。
- 这只证明 third-party local HTTP contract smoke 通过，不等于真实第三方 agent 产品集成已验证。

仍禁止声明：

```text
Codex integration verified
Claude Code integration verified
Third-party agent integration verified
MCP ready
Windows ready
cross-platform ready
USB ready
production signed release ready
```
