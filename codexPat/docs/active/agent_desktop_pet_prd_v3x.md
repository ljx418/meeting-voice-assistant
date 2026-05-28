# PRD：agent-desktop-pet 产品规格总结与未来规划

版本：PRD v1.0  
日期：2026-05-26  
适用范围：V1.0 - V3.7 已验收基线，以及 V3.x 后续规划  
文档用途：面向产品经理、技术负责人、内部团队、后续规划与审计  
当前状态：V3.7 scoped passed；V3.6 hook-only 路线保留为 historical blocked evidence，当前 Codex exec 监听主线改为 V3.7 JSONL monitor

---

## 1. 一句话定位

`agent-desktop-pet` 是一个面向本地开发者的低打扰 AI Agent 状态桌宠。它通过桌面猫的动作、状态、少量声音和多实例管理，把 Codex / Agent 的 workflow phase 转译为用户可感知的桌面反馈。

它不是通用桌面宠物，不是通知中心，不是聊天机器人，也不是 OS 级窗口识别系统。

---

## 2. 产品背景

随着 Codex、Claude Code、自定义 Agent 和本地脚本逐渐承担更长时间的开发任务，用户面临一个典型问题：Agent 在后台运行时，终端里有大量文本，但用户很难用余光判断当前状态。

本项目的核心出发点是：

- 不要求用户一直盯终端。
- 不通过强通知打断用户。
- 不让 Agent 直接控制 UI。
- 只把 Agent 的结构化状态意图转译为桌面猫的低打扰行为。

最终目标是形成一个本地的 Agent 状态感知层：用户在桌面上看到一只猫，就能知道某个 Codex session 当前是在思考、执行、等待输入、成功还是失败。

---

## 3. 产品目标

### 3.1 当前阶段目标

当前阶段已经从“本地桌面猫 MVP”推进到 “V3.7 scoped passed”。项目目标已经从单只桌面猫扩展为多实例 Codex 工作伙伴系统：

- 一个 Codex session / terminal tab 可以绑定一只猫。
- 多个 Codex session 可以同时拥有不同猫。
- 每只猫可以独立显示状态、名称、位置、外观和路由信息。
- Codex wrapper、official hooks、JSONL monitor 等不同来源的状态都必须通过 PetEvent / HTTP Event Bridge / petctl 体系进入桌宠，不得绕过安全边界。

### 3.2 未来目标

后续目标不是无边界地堆功能，而是继续围绕“本地 Codex 工作流状态感知”做稳定化：

1. 保持 V3.1 - V3.7 已验收能力不回退。
2. 对 official hook 无法覆盖的场景，用 V3.7 project-owned JSONL monitor 作为当前推荐监听方案。
3. 明确每条能力声明的证据边界。
4. 持续避免 false-green：blocked 项不能被后续 scope-change 偷换成 passed。

---

## 4. 目标用户

### 4.1 个人开发者

典型用户是使用 Codex / 本地脚本完成代码修改、测试、总结、重构的开发者。他们希望减少切屏和终端监控成本。

### 4.2 Agent 重度用户

这类用户会同时打开多个 Codex session 或多个终端 tab，希望每个 session 有独立可视反馈。

### 4.3 项目维护者 / 内部团队

维护者关注的是：功能是否真的验收、claim 是否有 evidence、smoke 是否可复跑、文档是否没有 false-green。

---

## 5. 核心使用场景

### 场景 A：一个 Codex session 一只猫

用户通过 wrapper 启动 Codex：

```bash
node packages/petctl/dist/cli.js codex launch --name "Review Cat" -- --help
```

系统创建或绑定一个 PetInstance，注入 `AGENT_DESKTOP_PET_INSTANCE_ID`，并将该 Codex session 的状态路由到对应猫。

### 场景 B：两个 Codex session 分别对应两只猫

用户启动两个 Codex session：

```bash
node packages/petctl/dist/cli.js codex launch --name "Codex A" -- --help
node packages/petctl/dist/cli.js codex launch --name "Codex B" -- --help
```

期望：

- A 的事件只影响 A 的猫。
- B 的事件只影响 B 的猫。
- 默认猫不响应 A/B 的 `--instance` 事件。

### 场景 C：Codex official hooks 状态映射（保留能力）

项目通过 `.codex/hooks.json` 和 `scripts/codex-pet-hook.mjs` 将 Codex lifecycle 事件映射为猫状态，例如：

| Codex hook | Pet state | 说明 |
|---|---|---|
| `UserPromptSubmit` | `thinking` | 用户提交 prompt 后进入处理阶段 |
| `PreToolUse` | `running` | Codex 准备调用工具 |
| `PermissionRequest` | `need_input` | 需要用户批准或授权 |
| `Stop` | `success` / `idle` | 仅作为 turn completion marker，不得无条件覆盖 error |

### 场景 D：Codex exec JSONL monitor（当前推荐监听路径）

V3.7 引入 project-owned JSONL monitor，用于 wrapper-launched `codex exec --json` 场景。该路径是当前项目推荐的 Codex exec 状态监听方案：

```bash
node packages/petctl/dist/cli.js codex launch \
  --monitor jsonl \
  --name "Review Cat" \
  -- exec --json "summarize this repository"
```

系统只解析结构化 JSONL event type，不解析终端文本，不读取 `transcript_path`。

---

## 6. 当前已实现能力

### 6.1 本地桌宠基础能力

| 能力 | 当前状态 |
|---|---|
| macOS-first Tauri 桌面 app | 已完成 |
| 透明、无边框、置顶窗口 | 已完成 |
| 拖拽、位置持久化 | 已完成 |
| 系统托盘 | 已完成 |
| 设置页 | 已完成 |
| 多猫管理 UI | 已完成 |
| 内置 CSS 猫状态动画 | 已完成 |
| 内置外观 profile | 已完成 |

### 6.2 事件接入能力

| 能力 | 当前状态 |
|---|---|
| PetEvent schema | 已落地 |
| 本地 HTTP Event Bridge | 已落地 |
| `127.0.0.1:17321` | 已落地 |
| token auth | 已落地 |
| action / sound 白名单 | 已落地 |
| rate limit | 已落地 |
| diagnostics accepted/rejected summary | 已落地 |
| rejected reason sanitization | 已落地 |
| safe sound / mute / cooldown | 已落地 |
| `petctl notify` | 已落地 |

### 6.3 多实例能力

| 能力 | 当前状态 |
|---|---|
| default pet legacy route | 已完成 |
| `POST /api/instances/:instanceId/events` | 已完成 |
| `petctl attach codex` | 已完成 |
| `petctl notify --instance` | 已完成 |
| `AGENT_DESKTOP_PET_INSTANCE_ID` | 已完成 |
| `petctl list` | 已完成 |
| `petctl detach` | 已完成 |
| Manager UI 管理多猫 | 已完成 |

### 6.4 Codex 能力

| 能力 | 当前状态 | 允许声明 |
|---|---|---|
| Codex local CLI smoke | 已验收 | tested local Codex CLI smoke scenarios |
| Multi-instance Codex workflow | 已验收 | tested local Codex session scenarios |
| `petctl codex launch` wrapper-first binding | 已验收 | tested local macOS terminal scenarios |
| Codex official hooks state mapping | 已验收 scoped | tested local Codex hook scenarios |
| Codex hook diagnostics | 已验收 | tested local diagnostics scenarios |
| V3.6 real PostToolUse failure hook mapping | historical blocked / deprecated active strategy | 仅可声明 blocked / deprecated，不可声明 passed |
| V3.7 JSONL monitor | 已验收 scoped / 当前推荐 Codex exec 监听路径 | tested local wrapper-launched `codex exec --json` scenarios |

### 6.5 Agent integration scoped 能力

| 能力 | 当前状态 | 边界 |
|---|---|---|
| MCP adapter minimal bridge smoke | passed scoped | 不能声明 MCP ready |
| Third-party contract v3 smoke | passed scoped | 不能声明第三方产品集成 verified |
| Claude Code instruction template | 存在 | 不能声明 Claude Code integration verified |
| Claude Code hook verification | 未通过 / deferred | 不能声明 verified |

---

## 7. 非目标与 forbidden claims

本项目当前不得声明以下能力已完成：

```text
all Codex workflows verified
unqualified multi-instance Codex verified beyond tested local scenarios
Codex internal reasoning exact mapping ready
ModelThinkingStart / ModelThinkingEnd verified
OS-level Codex window binding ready
PostToolUse failure hook evidence passed
V3.6 selected Codex workflow hook coverage smoke passed
Claude Code integration verified
Third-party agent integration verified
MCP ready
Windows ready
cross-platform ready
USB ready
Rive / Live2D / 3D ready
photo customization ready
user asset upload ready
remote asset download ready
custom asset pack import ready
production signed release ready
auto update ready
per-instance queue ready
```

这些 forbidden claims 只能出现在 forbidden、deferred、blocked、not-ready 或 backlog 语境里，不能作为 ready / passed / verified 结论出现。

---

## 8. Codex 绑定模型

### 8.1 绑定定义

本项目不做 OS 级窗口识别。这里的“一只 Codex 窗口 / 会话一只猫”指：

- 通过 `petctl codex launch` 启动的本地 Codex session。
- 或用户手动 `attach codex` 后在当前 shell 中使用 `--instance` / `AGENT_DESKTOP_PET_INSTANCE_ID` 路由。

未通过 wrapper 启动的任意系统窗口，不会被自动识别。

### 8.2 推荐路径

```bash
node packages/petctl/dist/cli.js codex launch --name "Review Cat" -- --help
```

V3.7 JSONL monitor 路径：

```bash
node packages/petctl/dist/cli.js codex launch \
  --monitor jsonl \
  --name "Review Cat" \
  -- exec --json "summarize this repository"
```

### 8.3 手动路径

```bash
node packages/petctl/dist/cli.js attach codex --name "Review Cat" --json
node packages/petctl/dist/cli.js notify --instance <instanceId> --level running --title "Codex running"
```

### 8.4 环境变量路径

```bash
eval "$(node packages/petctl/dist/cli.js attach codex --name 'Review Cat' --print-env)"
node packages/petctl/dist/cli.js notify --level running --title "Codex running"
```

该方式只影响当前 shell，不会注入已运行 Codex 进程。

---

## 9. 状态映射模型

### 9.1 标准 PetEvent 状态

| Level | 产品含义 | 默认交互策略 |
|---|---|---|
| `thinking` | Agent 正在分析、规划、阅读 | 低打扰，不播放声音 |
| `running` | Agent 正在执行、测试、构建、调用工具 | 低打扰，不播放声音 |
| `success` | 任务完成 | 短反馈，可轻提示 |
| `warning` | 非阻塞问题 | 短文本 / 受 cooldown 控制 |
| `error` | 命令失败、实现阻塞、不可恢复问题 | 明显反馈，受 cooldown 控制 |
| `need_input` | 需要用户确认、授权、凭据或决策 | 明显反馈，受 cooldown 控制 |
| `idle` | 空闲 | 不打扰 |
| `sleeping` | 休息 | 不打扰 |

### 9.2 Codex official hooks 映射

| Hook | Pet state | 边界 |
|---|---|---|
| `UserPromptSubmit` | `thinking` | 近似表示用户提交后进入处理 |
| `PreToolUse` | `running` | 工具调用前 |
| `PermissionRequest` | `need_input` | 需要用户授权或批准 |
| `PostToolUse` success | `running` / marker | 不等于整轮完成 |
| `PostToolUse` failure | `error` | 当前真实失败 payload 缺稳定字段，V3.6 blocked |
| `Stop` | `success` / `idle` | 仅 turn completion marker，不得无条件覆盖 error |

### 9.3 JSONL monitor 映射

| JSONL event type | Pet state | 边界 |
|---|---|---|
| `thread.started` | marker-only | 会话 marker，不发送 pet state |
| `turn.started` | `thinking` | 新 turn 开始 |
| `item.started` | `running` | item / tool 开始 |
| `item.completed` | marker / keep current | 单项完成，不等于任务成功 |
| `turn.completed` | `success` | 仅限本轮没有 error |
| `turn.failed` | `error` | 结构化失败 |
| `error` | `error` | 错误事件 |

JSONL monitor 是 project-owned structured monitor，不是 official Codex hook lifecycle evidence。它已经替代 V3.6 hook-only 作为当前推荐的 Codex exec 监听方案，但只覆盖 wrapper-launched `codex exec --json`，不覆盖 interactive Codex TUI 或 OS-level window binding。

### 9.4 PRD 与当前实现一致性审计

2026-05-26 审计结论：当前实现与 PRD 主规格一致，无重大产品方向偏差。

已确认一致：

- V3.6 hook-only 路线保持 historical blocked，并从 active strategy 中废弃。
- V3.7 是当前推荐的 project-owned JSONL monitor，不是 official hook lifecycle evidence。
- `petctl codex launch --monitor jsonl` 仅覆盖 wrapper-launched `codex exec --json`。
- JSONL monitor 只解析结构化 event type，不解析终端文本，不读取 `transcript_path`。
- security / claim 边界与 active gap、V3.7 final report 一致。

已发现并记录的非阻塞偏差 / 风险：

| 项 | 结论 | 处理 |
|---|---|---|
| V3.7 current gap 文档 | 原先缺失 | 已规划补齐为 `docs/V3.7/v3_7-current-gap-analysis.md` |
| `thread.started` 映射 | 实现为 marker-only，不发送 `idle` | PRD 改为 marker-only |
| `raw.monitor` 字段名 | 内容是 sanitized monitor summary，但 `raw` 命名有审计歧义 | 记录为未来兼容性重命名候选，不作为当前安全泄露 |

---

## 10. 安全边界

### 10.1 Agent 权限边界

Agent 只能发送结构化 PetEvent，不得：

- 直接控制 UI。
- 执行桌宠内部脚本。
- 传入本地路径、相对路径、绝对路径或 URL 作为 sound/profile/resource。
- 绕过 HTTP/Event Bridge。
- 读取 token、settings、workspace path 或 config path。

### 10.2 本地 API 边界

- API 只监听 `127.0.0.1`。
- 写接口必须带 Bearer token。
- `sound` / `action` / `hardware.light.effect` 必须是白名单 ID。
- 错误响应必须使用安全化 `reasonCode` / `reasonField` / 泛化 `reason`。
- diagnostics 不保存 raw payload、metadata 全量或 message 全文。

### 10.3 Evidence redaction 边界

所有 smoke / evidence / final report 不得包含：

```text
token
Authorization header
raw payload
raw JSONL payload
prompt text
tool command text
transcript_path
full /Users path
workspace path
config path
api-token.json
invalid sound 原文
```

---

## 11. 验收体系

### 11.1 每个阶段必须具备

```text
development-plan
acceptance-plan
current-gap-analysis
claim-matrix
evidence
final-acceptance-report
```

### 11.2 典型自动检查

```bash
pnpm run doctor
pnpm --filter @agent-desktop-pet/pet-protocol check
pnpm --filter @agent-desktop-pet/pet-protocol test
pnpm --filter @agent-desktop-pet/petctl check
pnpm --filter @agent-desktop-pet/petctl test
pnpm --filter @agent-desktop-pet/pet-mcp check
pnpm --filter @agent-desktop-pet/pet-mcp test
pnpm --filter desktop check
cargo check --manifest-path apps/desktop/src-tauri/Cargo.toml
pnpm --filter desktop build
pnpm --filter desktop tauri build -b app
git status --short
```

### 11.3 当前关键回归

```bash
node scripts/v3_1_runtime_smoke.mjs
node scripts/v3_2_mcp_adapter_smoke.mjs
node scripts/v3_2_third_party_contract_smoke.mjs
node scripts/v3_3_codex_window_binding_smoke.mjs
node scripts/v3_4_codex_hook_fixture_smoke.mjs
node scripts/v3_7_codex_exec_jsonl_monitor_smoke.mjs
```

### 11.4 No False-Green 原则

- scoped smoke 不能写成 ready / verified。
- blocked 项不能被后续 scope-change 偷换成 passed。
- fixture evidence 不能替代真实 lifecycle evidence。
- terminal text 不能替代 official hook payload。
- JSONL monitor 不把 V3.6 hook-only evidence 改写为 passed；它作为新的主策略替代 V3.6 hook-only 路线覆盖 wrapper-launched `codex exec --json` 场景。

---

## 12. 当前版本状态

### 12.1 已通过

| 阶段 | 状态 | 说明 |
|---|---|---|
| V3.1 | passed | 稳定化、用户上手、runtime smoke、迁移指导 |
| V3.2 | passed scoped | MCP adapter minimal、third-party contract v3 |
| V3.3 | passed scoped | Codex window/session-to-pet binding |
| V3.4 | passed scoped | Codex hooks state mapping |
| V3.5 | passed scoped | hook diagnostics and recovery |
| V3.7 | passed scoped | Codex exec JSONL monitor |

### 12.2 阻塞项

| 阶段 | 状态 | 原因 |
|---|---|---|
| V3.6 | historical blocked / deprecated active strategy | 真实 `PostToolUse` failure hook payload 未暴露稳定失败字段；当前不再继续该 hook-only 路线 |

---

## 13. 后续路线图

### 13.1 V3.x Final Consolidation

状态：passed scoped。

目标：把 V3.1 到 V3.7 的证据、声明和用户文档统一收口，形成 V3.x scoped Codex local workflow acceptance。

已完成：

- 汇总 V3.x evidence index。
- 更新 V3.x claim matrix。
- 复跑关键 smoke。
- 执行 security scan。
- 执行 claim consistency scan。
- 执行 git artifact check。
- 更新 README、docs map、multi-codex workflow、integrations、troubleshooting。

允许声明：

```text
V3.x scoped Codex local workflow acceptance passed with documented evidence and claim boundaries.
```

禁止扩展为：

```text
all Codex workflows verified
OS-level Codex window binding ready
Codex internal reasoning exact mapping ready
MCP ready
Windows ready
production signed release ready
```

### 13.2 Claude Code 后续验证

当前不允许声明 Claude Code integration verified。后续如重启，应独立规划：

- Claude Code skill workflow。
- Claude Code hook lifecycle。
- Claude Code MCP path。
- 版本升级后的 hook 行为复测。

通过条件必须包含真实 Claude Code lifecycle、diagnostics accepted、sourceId=claude-code.local、目标猫状态变化。

### 13.3 MCP 深化

当前只允许声明 MCP adapter minimal smoke passed，不允许 MCP ready。后续可做：

- Codex MCP client smoke。
- Claude Code MCP client smoke。
- MCP capabilities/state/error redaction。

### 13.4 Windows / Cross-platform

后续独立立项：

- Windows 透明窗口。
- Windows 托盘。
- Windows config path。
- Windows petctl。
- Windows build and smoke。

不允许从 macOS smoke 推导 cross-platform ready。

### 13.5 Production Distribution

后续独立立项：

- macOS signing。
- notarization。
- updater。
- release artifact。
- Gatekeeper 首次打开体验。

### 13.6 高级猫咪体验

后续独立立项，并归入 V5.x Cat Renderer & Asset System 或更后续的独立 productization track。该方向不属于 V4.x OS-level Codex window/session binding feasibility，也不得进入 V4.0-V4.3 acceptance gates。

- 高质量 sprite。
- Rive / Live2D / 3D 调研。
- 照片自定义。
- 用户资产包。
- 皮肤市场。
- license / attribution。
- release artifact asset integrity。
- bundled asset packaging checks。

V4.x 不包含资产、renderer、3D、照片自定义、用户资产包、皮肤市场、license / attribution、release artifact asset integrity 或 productization packaging 验收。完整 3D、动作资产、Rive / Live2D / GLTF renderer、自定义资产包导入均属于 V5.x 或更后续阶段。

### 13.7 Codex 监听策略

当前 Codex exec 监听策略已经从 V3.6 hook-only failure mapping 切换到 V3.7 JSONL monitor。

推荐路径：

```bash
node packages/petctl/dist/cli.js codex launch \
  --monitor jsonl \
  --name "Review Cat" \
  -- exec --json "summarize this repository"
```

保留边界：

- V3.6 不改写为 passed。
- V3.7 不代表 official hook lifecycle evidence。
- V3.7 不覆盖 interactive Codex TUI。
- V3.7 不覆盖 OS-level Codex window binding。
- V3.7 不代表 all Codex workflows verified。

### 13.8 V4.x：已打开 Codex 活动窗口绑定

V4.x 承接一个新的产品诉求：

```text
用户已经打开了 Codex 终端窗口，希望不重新通过 wrapper 启动，也能把当前活动 Codex 窗口绑定到一只猫。
```

该能力不属于 V3.x。V3.x 当前只能保证 wrapper-launched `codex exec --json` 的 V3.7 JSONL monitor 路径。

V4.x 先做 feasibility review，不直接声明 ready：

- macOS Accessibility / active window discovery。
- shell / TTY session registry。
- Terminal.app / iTerm2 / VS Code terminal adapter 可行性。
- 显式用户确认绑定。
- 不读取 raw terminal text、prompt text、command text、workspace path、full local path。

V4.x 必须区分候选窗口 / session discovery 与 Codex lifecycle state event source。能发现窗口不等于能监控 interactive Codex TUI 状态。V4.0 只做 feasibility review；V4.1 才可能做 safe-field probe；V4.2 才可能做 user-confirmed binding UX；V4.3 才可能做 selected-terminal routing prototype。

V4.x 不包含 asset、renderer 或 productization packaging 工作。这些高级体验和资产产品化内容归入 V5.x 或后续独立 productization track。

V4.x 规划文档：

- `docs/V4.x/v4_x-development-plan.md`
- `docs/V4.x/v4_x-acceptance-plan.md`
- `docs/V4.x/v4_x-current-gap-analysis.md`
- `docs/V4.x/v4_x-claim-matrix.md`

### 13.9 V5.x：3D 化和动作资产系统

V5.x 承接高级猫咪体验和 renderer / asset system：

```text
Cat Renderer & Asset System
```

建议阶段：

- V5.0 Asset System Freeze：资产包 manifest、action 映射、fallback、安全边界。
- V5.1 Sprite / 2D Asset Pack v2：先补高质量 2D 动作资产。
- V5.2 Renderer Plugin Interface：抽象 CSS / sprite / GLTF / Rive / Live2D renderer。
- V5.3 GLTF / Three.js 3D Cat Prototype：仅 bundled GLB/GLTF，不做用户上传。
- V5.4 3D Action Asset Pack：核心状态动作 clip。
- V5.5 Asset Import / Custom Pack：manifest 校验后的本地导入。
- 后续独立 productization track：license / attribution、release artifact asset integrity、signed / notarized app asset checks。

上述后续 productization track 不代表 `production signed release ready`，也不代表 `Rive / Live2D / 3D ready` 或 `custom asset pack import ready`。

### 13.10 V5.6+：个性化猫资产生成与导入管线

V5.6+ 承接新的个性化桌宠诉求：

```text
用户提供猫照片或特征描述 -> 标准化资产生成需求 -> 外部生成式 AI 生成素材 -> 本地 manifest 校验导入 -> 动作映射与管理
```

阶段规划：

- V5.6 Photo Personalization Scope Freeze：照片隐私、claim 边界、provider 边界。
- V5.7 AI Prompt Pack Generator：生成 2D / GLTF / action clip 标准提示词包。
- V5.8 Standardized Local Asset Import：导入用户生成的 sprite / GLTF 资产包，必须复制到 app-managed storage。
- V5.9 Dynamic Action Pack Builder：将导入资产映射到 `idle`、`thinking`、`running`、`success`、`warning`、`error`、`need_input`、`sleeping`。
- V5.10 External Generation Provider Feasibility：仅做 provider adapter 可行性，不默认上传照片。

默认策略：

- 用户照片是敏感输入，默认不上传到第三方服务。
- 如果本项目不能本地生成 3D 资产，先降级为输出标准化 prompt pack，由用户自行使用外部生成式 AI。
- 外部生成结果必须通过本项目 manifest 校验和本地导入，不能绕过 renderer 安全边界。
- provider adapter 必须另做隐私、费用、license、用户授权和真实 smoke 验收。

V5.6+ 允许 scoped 声明：

```text
V5.7 personalized cat AI prompt pack generated for standardized external asset creation.
V5.8 manifest-validated local personalized asset import passed for tested sprite and GLTF asset packs.
V5.9 personalized asset action mapping passed for imported local asset packs in tested CLI activation path.
V5.10 external asset generation provider feasibility completed with scoped adapter boundary.
```

V5.6+ 仍不得声明：

```text
automatic photo-to-3D ready
provider integration verified
remote asset loading ready
asset marketplace ready
production signed release ready
```

V5.x 规划文档：

- `docs/V5.x/v5_x-development-plan.md`
- `docs/V5.x/v5_x-acceptance-plan.md`
- `docs/V5.x/v5_x-current-gap-analysis.md`
- `docs/V5.x/v5_x-claim-matrix.md`

V5.11+ 产品化计划文档：

- `docs/V5.x/v5_11-import-ui-development-plan.md`
- `docs/V5.x/v5_11-import-ui-acceptance-plan.md`
- `docs/V5.x/v5_12-runtime-imported-pack-rendering-development-plan.md`
- `docs/V5.x/v5_12-runtime-imported-pack-rendering-acceptance-plan.md`
- `docs/V5.x/v5_13-photo-to-asset-guided-workflow-development-plan.md`
- `docs/V5.x/v5_13-photo-to-asset-guided-workflow-privacy-review.md`
- `docs/V5.x/v5_14-provider-adapter-feasibility-and-consent-plan.md`
- `docs/V5.x/v5_15-visual-quality-action-qa-plan.md`
- `docs/V5.x/v5_x-productization-gate-plan.md`

V5.x 前仍不得声明：

```text
Rive / Live2D / 3D ready
photo customization ready
user asset upload ready
remote asset download ready
custom asset pack import ready
asset marketplace ready
```

---

## 14. 成功指标

### 14.1 产品成功指标

- 用户能在 10 分钟内启动 app 并绑定一个 Codex session。
- 用户能创建两个 Codex session，各自对应一只猫。
- 用户能通过 Manager UI 识别哪只猫属于哪个 session。
- 普通状态不造成通知轰炸。
- `error` / `need_input` 能被用户及时感知。

### 14.2 工程成功指标

- 每条新 claim 都有 evidence。
- smoke 可复跑。
- evidence 不泄露敏感信息。
- blocked 不被写成 passed。
- forbidden claims 只出现在 forbidden / deferred / not-ready 语境。

### 14.3 集成成功指标

- `petctl codex launch` 绑定稳定。
- Codex hooks mapping 在 tested local scenarios 作为保留能力可靠。
- JSONL monitor 是当前推荐 Codex exec 监听路径，并在 tested local `codex exec --json` 场景中能捕获 structured error。
- MCP / third-party contract 维持 scoped claim，不扩大为 ready。

---

## 15. 文档路径索引

### 当前状态与 gap

- `docs/active/current-vs-target-gap.md`
- `docs/active/current-vs-target-gap.drawio`
- `docs/active/development-plan.md`
- `docs/active/acceptance-plan.md`

### 总体规划

- `docs/V3.x/v3_x-development-plan.md`
- `README.md`
- `docs/README.md`

### 架构与协议

- `docs/blueprint/target-architecture.md`
- `docs/blueprint/03-pet-event-protocol.md`
- `docs/blueprint/04-cat-state-machine.md`
- `docs/blueprint/05-desktop-window.md`
- `docs/blueprint/10-risks-and-decisions.md`

### 用户与集成参考

- `docs/reference/multi-codex-workflow.md`
- `docs/reference/07-integrations.md`
- `docs/reference/third-party-agent-contract.md`
- `docs/reference/agent-integration-guide.md`
- `docs/reference/petctl-recipes.md`

### V3.6 historical blocked / deprecated 证据

- `docs/V3.6/v3_6-final-acceptance-report.md`
- `docs/V3.6/v3_6-claim-matrix.md`
- `docs/V3.6/v3_6-workflow-coverage-matrix.md`
- `docs/V3.6/evidence/codex-real-workflow-smoke-2026-05-25.md`

### V3.7 JSONL Monitor 证据

- `docs/V3.7/v3_7-development-plan.md`
- `docs/V3.7/v3_7-acceptance-plan.md`
- `docs/V3.7/v3_7-claim-matrix.md`
- `docs/V3.7/v3_7-final-acceptance-report.md`
- `docs/V3.7/evidence/codex-exec-jsonl-monitor-smoke-2026-05-25.md`

### 历史验收基线

- `docs/V3.1/v3_1-final-acceptance-report.md`
- `docs/V3.2/v3_2-final-acceptance-report.md`
- `docs/V3.3/v3_3-final-acceptance-report.md`
- `docs/V3.4/v3_4-final-acceptance-report.md`
- `docs/V3.5/v3_5-final-acceptance-report.md`

---

## 16. 最终 PRD 结论

`agent-desktop-pet` 当前已经具备一个稳定的 macOS-first、多实例 Codex 状态桌宠基线。项目已经不再只是一个桌面猫 MVP，而是具备 PetEvent 协议、本地 HTTP Event Bridge、petctl、多实例路由、Manager UI、Codex wrapper、Codex hooks、Codex JSONL monitor 和完整 evidence/claim 体系的本地 Agent 状态反馈产品。

当前最重要的产品边界是：

```text
V3.6 hook-only 路线是 historical blocked，并已从当前 active strategy 中废弃。
V3.7 JSONL monitor 是当前推荐的 Codex exec 监听方案。
V3.7 不能用于声明 V3.6 hook-only acceptance passed，也不覆盖 interactive Codex TUI / OS-level window binding。
所有能力声明必须和 evidence 对齐。
```

V3.x Final Consolidation 已完成，当前结论是一个严格 scoped 的 Codex local workflow acceptance。下一步不应默认扩展更多 Agent 或平台；如继续开发，应优先选择与当前边界一致的补强项，并单独制定 evidence、claim 和 false-green 风险门禁。
