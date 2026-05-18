# Acceptance Plan

文档状态：MVP acceptance baseline。  
适用范围：agent-desktop-pet MVP，不包含 MCP、Codex/Claude Code Skill 完整包、USB 真实或 mock 硬件、3D、Live2D/Rive、照片自定义或动态生成、团队协作中枢、自动更新和正式签名发布。

## 1. Phase Acceptance

| Phase | 验收项 |
| --- | --- |
| Phase 1 | 已完成：桌面应用可启动；透明无边框置顶小窗口可见；占位猫可拖拽；位置持久化；系统托盘支持设置、静音、显示/隐藏、退出。 |
| Phase 2 | 已完成：状态机可通过开发触发器模拟 idle/thinking/running/success/warning/error/need_input/sleeping；优先级、冷却、队列和低打扰规则生效；2026-05-15 人工视觉验收通过。 |
| Phase 3 | 已完成：本地 HTTP API 只监听 127.0.0.1:17321；PetEvent JSON Schema 单一事实源、token 鉴权、白名单、速率限制和最近非法事件摘要生效；合法事件驱动前端 CatStateMachine。 |
| Phase 4 | 已完成：轻量 Rust Ingress Queue、合法/非法事件 ring buffer、token-protected diagnostics API、设置页只读诊断信息；自动检查和 HTTP smoke 已通过。 |
| Phase 5 | 已完成：petctl CLI 可通过参数或 JSON stdin 写入事件；复用 pet-protocol 本地校验；错误场景反馈清晰；2026-05-15 macOS 本地 CLI smoke 通过。 |
| Phase 6 | 已完成：内置声音白名单和声音冷却生效；禁止本地路径、URL 和未知 sound ID；静音联动生效；2026-05-15 macOS sound smoke 通过。 |
| Phase 7 | 已并入 Phase 6：macOS-first MVP 收口、macOS 本地运行与打包、README 使用说明和安全边界；Windows 不作为第一阶段验收阻塞。 |
| Phase 8 | Windows 跨平台验证与硬化：启动、托盘、HTTP API、petctl smoke test 通过后，才允许声明 cross-platform ready。 |
| V2.0 Phase 2.1 | 已完成：Codex / Claude Code instruction template、agent 接入指南、petctl recipes、shell 示例和 Node 示例已落地；只声明模板和 recipes ready，不声明 Codex/Claude 集成已验证。 |
| V2.0 Phase 2.2 | 已完成：设置页 diagnostics polish，分区展示 runtime health、sound、accepted/rejected events 和 quick commands；只读，不执行命令，不显示敏感信息。 |
| V2.0 Phase 2.3 | 已完成：CSS 占位猫体验 polish，8 个状态更可区分；拖拽优先、窗口尺寸稳定、透明窗口无黑框。 |
| V2.0 Phase 2.4 | 已完成：README 快速入口、macOS local unsigned app 分发说明、doctor/troubleshooting、token/config 和迁移文档已落地。 |
| V2.0 Final Acceptance | 已完成：`docs/V2.0/v2_0-final-acceptance-report.md` status 为 `passed`，允许声明 V2.0 ready，但不扩大到 Codex/Claude 真实集成验证、Windows、签名发布、MCP 或 USB。 |
| V2.1-A Baseline Audit | 已完成：自动检查通过，third-party HTTP success/auth/level/sound redaction/source redaction/rate-limit smoke 通过。 |
| V2.1-B Codex Real Integration | pending：真实 Codex CLI smoke 通过前，不得声明 Codex integration verified。 |
| V2.1-C Claude Code Real Integration | pending：真实 Claude Code skill/hook smoke 通过前，不得声明 Claude Code integration verified。 |
| V2.1-D Third-party Agent Contract | baseline smoke passed：curl/Node/Python 示例成功事件通过；401/400/429 和 rejected reason sanitization 通过。真实第三方 agent 产品集成仍待后续单独验证。 |

## 2. MVP Exit Standard

MVP 完成必须满足：

1. macOS 可运行并可打包；第一阶段 MVP 不验收 Windows 场景。
2. 主窗口透明、无边框、置顶、小尺寸、可拖拽。
3. 系统托盘支持设置、静音、显示/隐藏、退出。
4. 占位猫能表达 idle、thinking、running、success、warning、error、need_input、sleeping。
5. 本地 HTTP API 只监听 `127.0.0.1`。
6. `GET /api/health`、`POST /api/events`、`GET /api/capabilities` 可用。
7. PetEvent schema 校验覆盖 source、via、level、action、sound、durationMs、title/message 长度和 hardware.effect。
8. TypeScript 与 Rust 基于同一 JSON Schema 或同一批合法/非法 fixtures 校验 PetEvent。
9. 非法事件写入日志但不执行。
10. 状态机优先级生效：need_input > error > warning > success > running > thinking > tease > walk > idle > sleeping。
11. 事件队列可防止连续事件导致动画乱跳。
12. `petctl notify` 可触发桌宠状态变化。
13. 声音只能通过白名单 sound ID 播放。
14. 静音设置全局生效。
15. 事件摘要日志可查看；MVP 不要求日志清空、导出、搜索或分页。
16. 普通 thinking/running 不弹气泡、不播放声音。
17. error/need_input 有明显但受控的提醒。

通过后可声明：

```text
macOS-first MVP ready: local desktop agent status pet with HTTP + petctl integration and safe sound feedback.
```

仍不能声明：

```text
MCP integration ready
Codex/Claude Code skill ready
USB hardware ready
USB mock hardware ready
Rive/Live2D/3D cat ready
production signed release ready
team collaboration hub ready
cross-platform ready
```

## 3. Manual Scenarios

Phase 2 smoke test：2026-05-15 已通过。

- 启动后默认进入 `idle`。
- hover 主窗口后 debug 入口可触发全部 8 个状态。
- 每个状态动画可区分且不改变窗口尺寸。
- 状态切换后透明窗口不出现黑框。
- `success` 短反馈后回到 `idle`。
- `thinking` / `running` 不弹通知气泡、不播放声音。
- `error` / `need_input` 明显但克制。
- 连续点击 `running` 不会频繁重启动画。
- `need_input` 可打断 `running` / `thinking`。
- `running` / `thinking` 不能打断 `error` / `need_input` 锁定期。
- `sleeping` 可被任意主动状态唤醒。
- 拖拽仍优先于动画。
- 托盘、设置页、显示/隐藏、重置位置、退出不回归。
- 设置页显示当前状态和队列长度。
- Phase 2 验收时不要求 HTTP API、PetEvent、petctl、MCP、USB、声音系统或真实事件日志。

桌面窗口：

- 启动应用后 10 秒内看到猫。
- 拖拽猫到屏幕边缘后重启，位置仍在可见区域。
- 点击托盘隐藏，再点击显示，窗口状态正确。
- 静音开关状态能持久化。

Windows smoke test（后续 Phase 8，不阻塞第一阶段 MVP）：

- Windows 上应用能启动并显示占位猫。
- Windows 托盘菜单能打开设置、静音、显示/隐藏、退出。
- Windows 上 `GET /api/health` 正常。
- Windows 上 `petctl notify --level success --title "测试通过"` 能触发状态变化。

HTTP API：

- `GET /api/health` 返回正常。
- 无 token 调用 `POST /api/events` 返回 401。
- 非法 level 返回 400。
- 非法 `source.id` 返回 400。
- 非法 sound 路径或 URL 返回 400。
- TypeScript 与 Rust 对同一批合法/非法 PetEvent fixtures 的校验结论一致。
- 高频调用返回 429。
- 合法 success/error/need_input 驱动猫咪动作。

Diagnostics：

- `GET /api/diagnostics` 无 token 返回 401。
- `GET /api/diagnostics` 有 token 返回 enabled、listenAddress、queue length/capacity、acceptedEvents、rejectedEvents、sound、hardwareLight=false。
- `sound` 返回 playbackAvailable、muted、cooldownMs、acceptedIds 和 lastDecision。
- diagnostics 不包含 token、原始 payload、metadata 全量或 message 全文。
- diagnostics 不包含声音文件路径、bundle 路径、非法 sound 原文、URL、本地路径或非法 `source.id`。
- rejectedEvents 包含 `reasonCode`、`reasonField` 和泛化 `reason`，不得直接显示 JSON Schema 库原始错误。
- 合法事件出现在 acceptedEvents。
- 非法事件、限流和队列拒绝出现在 rejectedEvents。

petctl：

- 桌面 App 启动时，`petctl notify --level success --title "测试通过"` 成功。
- 桌面 App 未启动时，CLI 输出明确错误。
- 未知 sound ID 被拒绝。
- `petctl notify --json` 从 stdin 读取完整 PetEvent。
- `--json` 不能与 payload 参数混用。
- token 读取支持 `--token`、`AGENT_DESKTOP_PET_TOKEN` 和 desktop app config token 文件。
- URL 读取支持 `--url`、`AGENT_DESKTOP_PET_URL` 和默认 localhost。
- CLI 输出不得包含完整 token。

V2.0 Phase 2.1 workflow templates：

- `skills/codex-agent-pet/SKILL.md` 存在，source 固定为 `codex.local` / `codex` / `Codex`。
- `skills/claude-agent-pet/SKILL.md` 存在，source 固定为 `claude-code.local` / `claude_code` / `Claude Code`。
- `docs/reference/agent-integration-guide.md` 明确 agent 只能写结构化 PetEvent，不能直接控制 UI、执行桌宠脚本或传本地路径/URL。
- `docs/reference/petctl-recipes.md` 覆盖测试、构建、长任务、need_input、warning、JSON stdin 和常见错误排查。
- `examples/shell/task-with-pet.sh -- <command>` 会先发送 running，成功发送 success，失败发送 error，并保留原 exit code。
- shell 示例不使用 `eval`。
- `examples/node/notify-pet.mjs` 使用 `child_process.spawnSync` 调用 `petctl notify`，不使用 `shell: true`。
- 示例不打印完整 token。
- 示例不发送路径或 URL 作为 sound。

V2.0 Phase 2.2 settings diagnostics：

- 设置页打开时自动加载 diagnostics。
- Runtime health 显示 API enabled、listen address、queue length/capacity、hardware light disabled、token status 和 last refresh time。
- Sound 显示 playbackAvailable、muted、cooldownMs、acceptedIds 和 lastDecision；无 lastDecision 时显示暂无声音决策。
- Recent accepted events 最多显示 10 条，只显示 receivedAt、sourceId、level、titlePreview、messagePreview、status。
- Recent rejected events 最多显示 10 条，只显示 receivedAt、sourceId、level、status、reasonCode、reasonField、reason。
- Quick commands 只显示文本和复制按钮，不执行 shell、petctl、node 或 curl。
- 页面不显示完整 token、token 文件绝对路径、原始 payload、metadata 全量、message 全文或声音文件路径。
- 不提供 token 重置、日志清空、导出、搜索、分页。

V2.0 Phase 2.3 cat experience polish：

- idle、thinking、running、success、warning、error、need_input、sleeping 肉眼可区分。
- thinking/running 保持低打扰，不弹通知气泡，不额外播放声音。
- success 是短反馈。
- warning、error、need_input 的明显程度递进。
- sleeping 明显低活跃。
- 动画只作用于猫内部元素，不改变窗口、stage 或根容器尺寸。
- 透明窗口不出现黑框、白底、阴影错位或明显脏边。
- 拖拽仍然可用，拖拽期间动画不抢控制。
- `prefers-reduced-motion` 可降级非必要动画。

V2.0 Phase 2.4 distribution readiness：

- README 可以指导新用户安装依赖、启动 dev app、构建 `.app`、打开 `.app`、验证 `/api/health` 和用 `petctl notify` 触发状态。
- `docs/ops/macos-local-distribution.md` 明确当前是 unsigned local app，不是 production release。
- `docs/ops/troubleshooting.md` 覆盖 doctor warning、端口占用、token、常见 petctl 错误、tsx IPC EPERM 和 unsigned app 打开失败。
- `docs/ops/developer-setup.md` 和 `docs/ops/network-mirrors.md` 覆盖 Node/pnpm/Rust/Tauri/Xcode 与下载慢问题。
- 文档明确 token/config 文件来自当前实现，不发明不存在路径。
- drawio 与 markdown gap 一致。
- Phase 2.4 complete 不自动等于 V2.0 ready；当前 V2.0 ready 的依据是 final acceptance report status=`passed`。

低打扰体验：

- 连续 running 不弹气泡、不连续播放声音。
- success 只短促反馈。
- error/need_input 明显但不持续轰炸。
- 连续 need_input 在 cooldown 内不重复播放声音。
- 静音开启时所有事件都不播放声音。

安全：

- sound 传入本地路径被拒绝。
- sound 传入 URL 被拒绝。
- hardware effect 未知 ID 被拒绝或忽略并记录。
- message 超长被拒绝或截断并记录。

## 4. Suggested Automated Checks

后续代码阶段建议补充：

- `packages/pet-protocol` schema 单元测试。
- TypeScript/Rust 共用 PetEvent fixtures 一致性测试。
- Rust HTTP API handler 测试。
- 状态机优先级、队列、冷却单元测试。
- petctl CLI 参数解析和错误处理测试。
- 声音白名单校验测试。
- 设置持久化测试。

建议命令由实际工程落地后确定，例如：

```bash
pnpm test
pnpm lint
pnpm --filter @agent-desktop-pet/petctl test
cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml
pnpm --filter desktop tauri build -b app
```

## 5. No False-Green Rule

- 只完成文档，不得声明 MVP ready。
- 只完成 Tauri 窗口，不得声明 agent event integration ready。
- 只完成 HTTP API，不得声明 CLI ready。
- Phase 3/4 不播放声音、不控制硬件、不实现完整事件日志 UI。
- 未完成 schema 校验和白名单，不得开放 agent 写入入口。Phase 3 已满足 HTTP 写入入口的最低安全条件。
- Phase 6 已完成声音播放和 macOS MVP 收口验收，可声明 macOS-first MVP ready。
- V2.0 Phase 2.1 完成后最多声明 local workflow integration templates and petctl recipes ready，不得声明 Codex integration verified 或 Claude Code integration verified。
- V2.0 Phase 2.2 完成后最多声明 settings diagnostics polish ready。
- V2.0 Phase 2.3 完成后最多声明 CSS placeholder cat experience polish ready。
- V2.0 Phase 2.4 完成后最多声明 macOS distribution readiness and user onboarding docs ready。
- V2.0 final acceptance report 已通过，当前可以声明 `V2.0 ready: local agent workflow integration and developer usability polish complete.`
- V2.1 只完成 planning baseline 时，不得声明 Codex integration verified、Claude Code integration verified 或 third-party agent integration verified。
- V2.1-A 已通过，可声明 V2.1-A complete 和 Third-party local HTTP contract smoke passed；但不得声明 Third-party agent integration verified。
- Windows 不进入第一阶段 MVP 验收；未完成 Windows 启动、托盘、HTTP API、petctl smoke test，不得声明 cross-platform ready。
