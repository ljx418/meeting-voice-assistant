# V2.0 Development Plan

文档状态：V2.0 planning baseline。  
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

## 3. Phase 2.1：Integration Templates

目标：

- 让真实本地开发工作流可以按模板稳定接入桌宠。

主要任务：

- 新增 Codex instruction template。
- 新增 Claude Code instruction template。
- 新增 `petctl` recipes。
- 新增 shell 示例，用于包裹测试、构建、脚本任务。
- 新增 Node 示例，用于 Node 项目中触发 `petctl notify`。
- 编写 agent 接入指南，强调 agent 只能写结构化事件，不能直接控制 UI。

验收标准：

- 用户可以复制命令，将本地脚本状态发送给桌宠。
- Codex / Claude Code 模板只使用 `petctl` 或 HTTP，不引入 MCP。
- 示例覆盖 `running`、`success`、`warning`、`error`、`need_input`。
- 示例不暴露 token，不传本地声音路径或 URL。
- 高频状态示例遵守低打扰策略，不鼓励循环刷事件。

风险：

- 模板过度自动化导致事件风暴。
- instruction template 暗示 agent 可以控制 UI、执行任意脚本或绕过 PetEvent。

Codex prompt：

```text
请实现 V2.0 Phase 2.1 Integration Templates。新增 Codex 和 Claude Code instruction template、petctl recipes、shell 示例、Node 示例和 agent 接入指南。所有示例只能通过 petctl 或 localhost HTTP 写入 PetEvent，不得实现 MCP、USB、声音资源上传、自动发现或后台 daemon。示例必须覆盖 running、success、warning、error、need_input，并保持 V1.0 安全边界。
```

## 4. Phase 2.2：Settings & Diagnostics Polish

目标：

- 提升设置页和 diagnostics 的可读性，让用户知道事件是否进入、为什么被拒绝、声音为什么没播放。

主要任务：

- 优化设置页 diagnostics 展示。
- 增加 API URL、token 来源说明、`petctl` 示例命令展示。
- 展示最近 accepted/rejected 摘要与 reasonCode。
- 展示 sound decision：muted、cooldown、playbackAvailable、lastDecision。
- 保持主窗口低打扰，不做通知中心式 UI。

验收标准：

- 用户能在设置页判断 desktop 是否可接收事件。
- 用户能看到最近事件成功或失败原因。
- 用户能快速复制本地测试命令。
- 设置页不显示 token 全量、原始 payload、metadata 全量、message 全文或声音文件路径。
- 主猫窗口体验不被设置页增强影响。

风险：

- 设置页膨胀成通知中心。
- 诊断信息泄露敏感数据。

Codex prompt：

```text
请实现 V2.0 Phase 2.2 Settings & Diagnostics Polish。优化设置页只读 diagnostics 展示，显示 API enabled、listen address、queue、accepted/rejected 摘要、reasonCode、sound decision 和 petctl 示例命令。不得显示完整 token、原始 payload、metadata 全量、message 全文或声音文件路径。不要实现日志搜索、分页、导出、清空或通知中心式 UI。
```

## 5. Phase 2.3：Cat Experience Polish

目标：

- 在不引入 Rive/Live2D/3D 的前提下，提升 CSS 占位猫的开发者桌宠体验。

主要任务：

- 打磨 idle、thinking、running、success、warning、error、need_input、sleeping 动画区分度。
- 降低 thinking/running 的视觉打扰。
- 强化 need_input/error 的可感知性，但保持 cooldown。
- 避免透明窗口黑框、尺寸抖动和拖拽冲突。
- 保持现有 CatStateMachine 和 Behavior Queue，不重写状态机。

验收标准：

- 8 种状态肉眼可区分。
- thinking/running 仍低打扰。
- error/need_input 明显但不持续轰炸。
- 动画不改变窗口尺寸。
- 拖拽、托盘、透明窗口不回归。

风险：

- CSS 动效导致窗口边界、阴影或透明区域异常。
- 动画 polish 引入状态机回归。

Codex prompt：

```text
请实现 V2.0 Phase 2.3 Cat Experience Polish。只打磨现有 CSS 占位猫动画和视觉状态，不引入 Rive、Live2D、3D、照片自定义或资产包系统。保持 CatStateMachine 行为不重写，确保透明窗口无黑框、动画不抖动窗口尺寸、拖拽优先级不回归。
```

## 6. Phase 2.4：Distribution Readiness

目标：

- 让 macOS 用户可以更快部署、迁移和排障，但不做正式签名发布。

主要任务：

- 更新 README quick start。
- 增加 doctor/troubleshoot 文档。
- 增加 macOS 本地打包与启动说明。
- 增加 token/config 位置说明。
- 增加迁移说明：如何迁移配置、如何重新生成 token、如何验证 HTTP/petctl。
- 明确未签名 app 的 Gatekeeper 处理说明。

验收标准：

- 新用户能按文档在 macOS 上完成安装、启动、`petctl notify`。
- 常见失败场景有排障路径：端口占用、token 缺失、desktop 未启动、声音不可用。
- 文档明确不声明正式签名、自动更新或 Windows ready。
- V1.0 自动检查和 macOS smoke 不回归。

风险：

- 分发说明被误解为 production signed release。
- 网络依赖和系统权限导致快速部署体验不稳定。

Codex prompt：

```text
请实现 V2.0 Phase 2.4 Distribution Readiness。更新 README quick start、doctor/troubleshoot、macOS 本地打包启动说明、token/config 位置说明和迁移说明。不得声明正式签名、自动更新、Windows ready 或 cross-platform ready。保持 V1.0 验收命令和 smoke 流程可执行。
```

