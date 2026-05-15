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
- diagnostics 不包含声音文件路径或 bundle 路径。
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
- Windows 不进入第一阶段 MVP 验收；未完成 Windows 启动、托盘、HTTP API、petctl smoke test，不得声明 cross-platform ready。
