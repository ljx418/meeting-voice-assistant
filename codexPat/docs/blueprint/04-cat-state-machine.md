# 猫咪状态机

## 设计目标

状态机的首要目标是保持猫咪可常驻、自然、低打扰。事件到达顺序不是唯一依据，桌面端可以为了体验合并、延迟或忽略低价值事件。

当前实现状态：

- Phase 2 已在 `apps/desktop/src/state-machine.ts` 实现前端 `CatStateMachine`。
- Phase 2 已在 `apps/desktop/src/pet-states.ts` 实现状态配置。
- Phase 3 已接入 Rust side 推送的合法 HTTP PetEvent，并将 `level` 映射到前端状态。
- Phase 5 已通过 `petctl` 复用同一个 HTTP 入站入口。
- Phase 6 已实现 Rust side safe sound feedback；MCP 和 USB 仍是后续阶段。
- Phase 4 已实现轻量 Rust Ingress Queue 和 diagnostics；它是 admission/backpressure queue，不是 animation scheduler。

状态机分两层队列：

- Rust Ingress Queue：位于 Tauri Rust side，负责安全校验之后的入站背压、thinking/running 同 source 合并、容量控制和事件摘要。
- TypeScript Behavior Queue：位于前端，负责动画优先级、打断、冷却、建议时长和低打扰展示；Phase 2 已实现本地版本。

`PetEvent.durationMs` 进入 Behavior Queue 后只是建议展示时长，不是强制动画控制。

## 状态表

```text
state       priority duration     lock       cooldown next
need_input  100      8000ms       3000ms     3000ms   idle
error       90       6000ms       2500ms     3000ms   idle
warning     70       4000ms       0          2000ms   idle
success     60       3000ms       0          2000ms   idle
running     40       8000ms       0          2000ms   idle
thinking    35       7000ms       0          2000ms   idle
idle        10       indefinite   0          0        idle
sleeping    5        indefinite   0          5000ms   idle
```

`tease` 和 `walk` 仍是后续交互/资产动作，不进入 Phase 2 当前实现状态集合。

## 外部事件映射

```text
thinking   -> state thinking  -> action thinking
running    -> state running   -> action running
success    -> state success   -> action success
warning    -> state warning   -> action warning
error      -> state error     -> action error
need_input -> state need_input -> action need_input
idle       -> state idle      -> action idle
sleeping   -> state sleeping  -> action sleeping
```

命名约定：

- `warning` 是外部 level、内部状态名和 Phase 3 action ID。
- `alert` 可作为后续资产动作名，但不是 Phase 3 PetEvent action 白名单 ID。
- 文档和代码中不要把 `warning` level 与 `alert` state/action 混用。

如果事件显式传入 `action`，必须先经过白名单校验。合法 `action` 可以覆盖默认动作映射，但仍受状态机优先级、冷却和锁定规则约束。

## 优先级规则

- 高优先级状态可以打断低优先级状态。
- 同优先级事件进入 Behavior Queue 或合并。
- 低优先级事件不能打断高优先级状态，除非当前状态已完成或可打断。
- `error` 前 2.5 秒不可被 `thinking` / `running` 等低优先级背景状态打断。
- `need_input` 前 3 秒不可打断。
- 用户拖拽窗口优先于所有动画移动。
- `tease` 可以打断 `thinking` 和 `running`。
- `tease` 不能打断 `error` 和 `need_input` 的锁定期。

## Rust Ingress Queue

职责：

- 接收通过 HTTP 写入的合法事件；petctl 已复用同一入口。
- 在 schema、白名单、鉴权、限流之后入队。
- 保留入站顺序。
- 控制最大长度，当前容量 32。
- 对 `thinking` / `running` 同 source pending 事件做入站合并。
- 写入合法事件和非法事件摘要日志，合法/非法各保留最近 50 条。

不负责：

- 选择最终动画。
- 决定文本是否展示。
- 直接控制动画；声音由 Phase 6 Rust Sound service 按 level、mute 和 cooldown 独立决策。
- 直接控制 UI。

## TypeScript Behavior Queue

职责：

- Phase 2 接收本地 debug 入口生成的状态请求。
- Phase 3 已接收 Rust side 推送的合法 HTTP 事件。
- 将 `level/action/durationMs` 转换为行为状态。
- 执行优先级、冷却、打断、最短播放时长。
- 执行低打扰展示策略。
- 决定是否播放白名单声音或显示短文本。

规则：

- `thinking` 和 `running` 是背景状态，高频事件只保留最新一条，不连续打断当前自然动作。
- Behavior Queue 最大长度为 8。
- 队列满时，低优先级重复状态会被丢弃；高优先级状态可以挤掉最低优先级项。
- `success`、`error`、`need_input` 默认不合并，除非 payload 完全相同且在 2 秒内重复。
- Phase 6 已播放白名单 sound ID；声音播放和全局声音冷却由 Rust Sound service 处理，不由 Behavior Queue 处理。
- 状态完成后进入 `next`，通常回到 `idle`，再消费队列。
- 拖拽期间状态可以入队或记录，但影响位置/运动的动画 class 延后到拖拽结束。

## Phase 2 CSS 状态映射

```text
idle        -> .cat-state-idle
thinking    -> .cat-state-thinking
running     -> .cat-state-running
success     -> .cat-state-success
warning     -> .cat-state-warning
error       -> .cat-state-error
need_input  -> .cat-state-need-input
sleeping    -> .cat-state-sleeping
```

约束：

- 不恢复窗口级 shadow。
- 不恢复 `.cat-shadow` 黑色椭圆外阴影。
- 动画只改变猫内部元素的 transform、opacity 或形态，不改变窗口尺寸。
- 不显示通知中心式气泡。

## 用户逗猫

MVP 规则：

- 鼠标进入猫咪 hitbox，猫进入关注行为。
- 鼠标快速移动或启用玩具时进入 `tease`。
- `tease` 可以打断 `idle`、`walk`、`sleeping`、`thinking`、`running`。
- `tease` 不打断 `error` 和 `need_input` 锁定期。
- 逗猫结束后回到 `idle` 或继续消费 Behavior Queue。

## 空闲行为

- 无事件且无用户交互时进入 `idle`。
- 空闲超过 5 分钟可进入 `sleeping`。
- 新事件到来时，如果 `sleeping` 可打断，则唤醒并执行事件状态。
- 即使没有 Agent 事件，猫咪也应周期性出现轻微动作，避免像静态贴图。
