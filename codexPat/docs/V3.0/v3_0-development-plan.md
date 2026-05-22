# V3.0 Development Plan

文档状态：new mainline；V3.0 final acceptance passed for tested local Codex session scenarios。

## Goal

V3.0 的新目标是从单实例 Agent 状态猫升级为多实例 Codex 工作伙伴系统。

用户可能同时打开多个 Codex 窗口、终端会话或 workspace instance。每个 Codex 会话都应该能拥有一只独立桌面猫，每只猫有自己的名字、位置、状态、外观，并且只响应对应 Codex 会话的状态事件。

## Product Boundary

V3.0 不做 OS 级窗口句柄读取。Codex 窗口在本项目中定义为本地 Codex session / terminal tab / workspace instance。

V3.0 仍不做：

- Claude Code verification。
- MCP。
- Windows ready。
- USB。
- Rive / Live2D / 3D。
- Photo customization。
- Production signing / notarization。
- Auto update。

## Architecture

```text
Codex session / terminal tab / workspace instance
  -> petctl attach codex --name <pet-name>
  -> PetInstance registry
  -> instanceId + export AGENT_DESKTOP_PET_INSTANCE_ID=...

Codex status event
  -> petctl notify --instance <instanceId>
     or AGENT_DESKTOP_PET_INSTANCE_ID=<instanceId>
     or POST /api/instances/:instanceId/events
  -> Rust Local Event Bridge
  -> instance-aware event router
  -> target PetInstance runtime
  -> independent Behavior Queue / CatStateMachine
  -> target pet window
```

Legacy path remains:

```text
POST /api/events
petctl notify --level success
  -> default global pet
```

## Phase Plan

### Phase 3.1：V2.x Baseline Freeze

状态：passed。

证据：`v3_0-baseline-freeze-report.md`。

### Phase 3.2：Multi-instance Foundation

状态：complete for engineering closure；manual visual acceptance completed in V3.0 final acceptance。

目标：

- 引入 `PetInstance` registry。
- 支持一个 Tauri app 内多个独立透明猫窗口。
- 每只猫有独立位置和本地状态 runtime。
- 保持旧 `POST /api/events` 和旧 `petctl notify` 驱动 default pet。

主要任务：

- 增加 `PetInstance` 数据模型。
- 持久化 instance registry 到 `settings.json`。
- 新增创建、列出、重命名、detach instance 的 Tauri command。
- 设置页显示最小实例列表。
- 额外实例窗口可拖拽、位置持久化、重启恢复。
- 额外实例先不接外部事件，外部路由进入 Phase 3.3。

验收标准：

- 启动后 default pet 仍可用。
- 能创建两个额外 PetInstance。
- 三只猫可同时显示。
- 每只猫位置独立、重启可恢复。
- 每只猫本地 debug 状态独立。
- 旧 HTTP / petctl success smoke 不回归。

### Phase 3.3：Instance-aware Event Routing

状态：complete。

目标：

- 外部事件可以指定目标实例。

主要任务：

- 新增 `POST /api/instances/:instanceId/events`。
- 新增 `GET /api/instances`。
- Rust bridge 增加 instance-aware event router。
- 前端只让目标 PetInstance 响应对应事件。
- 保留旧 `/api/events` 到 default pet。

验收标准：

- 发给 instance A 的事件只改变猫 A。
- 发给 instance B 的事件只改变猫 B。
- unknown instance 返回 `404 instance_not_found`。
- default path 不回归。

### Phase 3.4：Codex Quick Attach

状态：complete for CLI/HTTP quick attach；real two-Codex-session visual verification completed in V3.0 final acceptance.

目标：

- 让多个 Codex session 通过 CLI 快速绑定自己的猫。

主要任务：

- `petctl attach codex --name <pet-name>`。
- `petctl notify --instance <instanceId>`。
- `AGENT_DESKTOP_PET_INSTANCE_ID` 环境变量路由。
- `petctl list`。
- `POST /api/instances` server-generated instance creation。
- Codex `SKILL.md` 升级为 instance-aware。

验收标准：

- attach A/B 返回独立 `instanceId` 和 `windowLabel`。
- `petctl list` 返回 default + A/B。
- `--instance`、`AGENT_DESKTOP_PET_INSTANCE_ID`、JSON stdin 均能路由到目标实例。
- explicit `--instance` 优先于 env。
- legacy notify 仍进入 default。
- 不读取 OS 级终端窗口句柄。
- 真实双 Codex session smoke 已在 Phase 3.7 final acceptance 中通过；声明仅限 tested local Codex session scenarios。

### Phase 3.5：Multi-pet Manager UI

状态：complete for manager UI implementation；direct click visual smoke completed in V3.0 final acceptance。

目标：

- 提供用户可理解的多猫管理页面，不变成通知中心。

主要任务：

- 设置页显示所有 PetInstance。
- 支持 rename、show/hide、reset position、detach。
- 支持 copy-only env export / notify command templates。
- 只读显示 `catProfileId`；不做外观切换。

验收标准：

- 用户能管理每只猫。
- UI 不执行 shell。
- 不显示 token、raw payload、full workspace path 或 metadata full dump。
- Copy buttons 只写剪贴板，不执行命令。

### Phase 3.6：Asset Pack v1

状态：complete for built-in CSS profiles and per-instance appearance selection；direct visual acceptance completed in V3.0 final acceptance。

目标：

- 让不同实例有可区分外观。

主要任务：

- 内置 CSS cat profiles。
- `catProfileId` per instance。
- 设置页可切换 profile。
- `list_cat_profiles` 和 `set_pet_instance_profile` Tauri commands。
- 不做外部 asset upload。

验收标准：

- 至少 4 个内置 cat profiles。
- 不同实例能显示不同外观。
- 状态动画、透明窗口和拖拽不回归。
- 不提供用户上传、远程下载、URL 输入或自定义资产包导入。

### Phase 3.7：Performance Hardening + Final Visual Acceptance

状态：engineering hardening and final acceptance complete for tested local Codex session scenarios。

目标：

- 多个 Codex session 同时运行时仍稳定、低打扰。
- 统一完成前序阶段延后的人工视觉验收。

主要任务：

- soft limit 6 pets，hard limit 12 pets。
- event storm guard under current global queue model。
- hidden pet 降低动画资源。
- 多实例声音 cooldown 策略。
- 多猫可见性、拖拽、重启恢复、debug 隔离、托盘多实例范围人工验收。

已完成：

- soft limit 6 total pets，hard limit 12 total pets。
- hard limit 返回 `instance_limit_reached`。
- Manager 显示 count / soft warning / hard-limit create disabled。
- hidden pet 仍接收 routed event，更新 registry，并以 `hidden_target` 跳过声音。
- rate-limit key 包含 target instance，单实例事件风暴不阻断另一个实例普通事件。
- operator final visual acceptance passed。
- real/equivalent two-Codex-session smoke passed。

未完成：

- per-instance queue；当前仍是 global ingress queue model。

验收标准：

- 6 只猫同时活跃仍响应流畅。
- 单实例事件风暴不影响其他实例。
- 多实例声音不轰炸。

## Exit Criteria

V3.0 完成后才允许声明：

```text
V3.0 ready: multi-instance Codex desktop pet workflow ready for tested local Codex session scenarios.
```

仍禁止声明：

```text
OS-level Codex window binding ready
Claude Code integration verified
MCP ready
Windows ready
cross-platform ready
USB ready
Rive/Live2D/3D ready
photo customization ready
user asset upload ready
custom asset pack import ready
per-instance queue ready
production signed release ready
```
