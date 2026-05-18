# V2.0 Development Plan

文档状态：V2.0 planning baseline；Phase 2.1 complete；Phase 2.2 complete；Phase 2.3 complete；Phase 2.4 complete；final acceptance passed。  
版本定位：Developer Workflow Integration Release。

## 1. 一句话定位

V2.0 将 agent-desktop-pet 从“本地可用的 Agent 状态桌宠 MVP”升级为“可被真实开发工作流稳定接入的 Agent 状态伙伴”。

## 2. Phase 2.0：V1.0 Baseline Freeze

目标：

- 固化 V1.0 macOS-first MVP 的实现边界、验收结论和不可回归能力。

主要任务：

- 将当前活动文档整理到 `docs/V2.0/`。
- 明确 V1.0 已实现能力和不可声明能力。
- 明确 V2.0 不重写 V1.0 架构。
- 更新 V2.0 gap 文档和 drawio。

验收标准：

- `docs/V2.0` 可独立说明 V1.0 当前状态和 V2.0 目标。
- README 链接 V1.0 归档和 V2.0 基线。
- 文档中没有把 MCP、USB、Windows ready 写成 V2.0 已实现能力。

风险：

- 将规划内容误写成已实现能力。

## 3. Phase 2.1：Workflow Integration Templates

目标：

- 让真实本地开发工作流可以按模板稳定接入桌宠。

状态：

- 已完成。完成后最多声明：`V2.0 Phase 2.1 complete: local workflow integration templates and petctl recipes ready.`

主要任务：

- 已新增 Codex instruction template：`skills/codex-agent-pet/SKILL.md`。
- 已新增 Claude Code instruction template：`skills/claude-agent-pet/SKILL.md`。
- 已新增 `petctl` recipes：`docs/reference/petctl-recipes.md`。
- 已新增 shell 示例：`examples/shell/task-with-pet.sh`。
- 已新增 Node 示例：`examples/node/notify-pet.mjs`。
- 已新增 agent 接入指南：`docs/reference/agent-integration-guide.md`。
- 已同步 README、active 文档、V2.0 文档和配套 drawio。

验收标准：

- 用户可以复制命令，将本地脚本状态发送给桌宠。
- Codex / Claude Code 模板只使用 `petctl` 或 HTTP，不引入 MCP。
- 示例覆盖 `running`、`success`、`warning`、`error`、`need_input`。
- 示例不暴露 token，不传本地声音路径或 URL。
- 高频状态示例遵守低打扰策略，不鼓励循环刷事件。
- shell 示例必须使用 `--` 分隔用户命令，不使用 `eval`，使用 `"$@"` 或等价安全方式执行命令，并保留原 exit code。
- Node 示例必须使用 `child_process.spawnSync` 参数数组调用 `petctl notify`，不得使用 `shell: true` 拼接命令字符串。

风险：

- 模板过度自动化导致事件风暴。
- instruction template 暗示 agent 可以控制 UI、执行任意脚本或绕过 PetEvent。
- 用户把 instruction template 误认为 Codex / Claude Code 集成已验证；文档已明确不得声明 Codex integration verified 或 Claude Code integration verified。

## 4. Phase 2.2：Settings & Diagnostics Polish

目标：

- 提升设置页和 diagnostics 的可读性，让用户知道事件是否进入、为什么被拒绝、声音为什么没播放。

状态：

- 已完成。完成后最多声明：`V2.0 Phase 2.2 complete: settings diagnostics polish ready.`

主要任务：

- 已优化设置页 diagnostics 展示。
- 已增加 Runtime health：API enabled、listen address、queue、hardware light、token status、last refresh time。
- 已展示最近 accepted/rejected 摘要与 reasonCode。
- 已展示 sound decision：muted、cooldown、playbackAvailable、acceptedIds、lastDecision。
- 已提供 Quick commands 复制按钮；设置页不执行 shell、petctl、node 或 curl。
- 保持主窗口低打扰，不做通知中心式 UI。

验收标准：

- 用户能在设置页判断 desktop 是否可接收事件。
- 用户能看到最近事件成功或失败原因。
- 用户能快速复制本地测试命令。
- 设置页不显示 token 全量、原始 payload、metadata 全量、message 全文或声音文件路径。
- 主猫窗口体验不被设置页增强影响。
- 不提供 token 重置、日志清空、导出、搜索、分页。

风险：

- 设置页膨胀成通知中心。
- 诊断信息泄露敏感数据。

## 5. Phase 2.3：Cat Experience Polish

目标：

- 在不引入 Rive/Live2D/3D 的前提下，提升 CSS 占位猫的开发者桌宠体验。

状态：

- 已完成。完成后最多声明：`V2.0 Phase 2.3 complete: CSS placeholder cat experience polish ready.`

主要任务：

- 已打磨 idle、thinking、running、success、warning、error、need_input、sleeping 动画区分度。
- 已降低 thinking/running 的视觉打扰。
- 已强化 warning、error、need_input 的可感知性，但仍依赖现有 lock/cooldown 控制打扰强度。
- 已避免窗口级阴影、黑框、尺寸抖动和拖拽冲突。
- 已增加 `prefers-reduced-motion` 兜底。
- 保持现有 CatStateMachine 和 Behavior Queue，未重写状态机。

验收标准：

- 8 种状态肉眼可区分。
- thinking/running 仍低打扰。
- error/need_input 明显但不持续轰炸。
- 动画不改变窗口尺寸。
- 拖拽、托盘、透明窗口不回归。

风险：

- CSS 动效导致窗口边界、阴影或透明区域异常。
- 动画 polish 引入状态机回归。

## 6. Phase 2.4：Distribution Readiness

目标：

- 让 macOS 用户可以更快部署、迁移和排障，但不做正式签名发布。

状态：

- 已完成。完成后最多声明：`V2.0 Phase 2.4 complete: macOS distribution readiness and user onboarding docs ready.`

主要任务：

- 已更新 README quick start。
- 已新增 `docs/ops/macos-local-distribution.md`。
- 已新增 `docs/ops/troubleshooting.md`。
- 已更新 doctor、developer setup、network mirrors 和 release boundary 文档。
- 已增加 macOS 本地打包、启动、Gatekeeper 和迁移说明。
- 已增加 token/config 位置说明，基于当前实现的 Tauri `app_config_dir()` 和 `api-token.json`。
- 已明确当前是 local unsigned app，不是正式签名发布、notarized release 或 production release。

验收标准：

- 新用户能按文档在 macOS 上完成安装、启动、`petctl notify`。
- 常见失败场景有排障路径：端口占用、token 缺失、desktop 未启动、声音不可用。
- 文档明确不声明正式签名、自动更新或 Windows ready。
- V1.0 自动检查和 macOS smoke 不回归。
- Phase 2.4 complete 不自动等于 V2.0 ready；当前 final acceptance report 已通过，因此允许声明 V2.0 ready。

风险：

- 分发说明被误解为 production signed release。
- 网络依赖和系统权限导致快速部署体验不稳定。

## 7. Final Acceptance & Release Closure

状态：

- 已完成。`docs/V2.0/v2_0-final-acceptance-report.md` status 为 `passed`。

允许声明：

```text
V2.0 ready: local agent workflow integration and developer usability polish complete.
Codex and Claude Code local workflow templates ready.
```

仍不能声明 Codex integration verified、Claude Code integration verified、Windows ready、cross-platform ready、production signed release ready、MCP ready、USB ready、Rive/Live2D/3D ready 或 photo customization ready。
