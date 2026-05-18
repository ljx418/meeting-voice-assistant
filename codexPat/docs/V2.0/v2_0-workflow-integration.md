# V2.0 Workflow Integration

文档状态：V2.0 planning baseline；Phase 2.1 complete；Phase 2.2 complete；Phase 2.3 complete。

## 1. 集成目标

V2.0 的集成目标是让真实本地开发工作流可以通过 `petctl` 或 localhost HTTP 将状态写入桌宠，同时保持 V1.0 的低打扰和安全边界。

## 2. 推荐 source

Codex：

```text
source.id = codex.local
source.kind = codex
source.name = Codex
```

Claude Code：

```text
source.id = claude-code.local
source.kind = claude_code
source.name = Claude Code
```

自定义脚本：

```text
source.id = script.local
source.kind = custom
source.name = Local Script
```

Node 示例：

```text
source.id = node.local
source.kind = custom
source.name = Node Script
```

## 3. petctl recipes

任务开始：

```bash
petctl notify \
  --source-id script.local \
  --source-kind custom \
  --source-name "Local Script" \
  --level running \
  --title "任务正在执行"
```

任务成功：

```bash
petctl notify \
  --source-id script.local \
  --source-kind custom \
  --source-name "Local Script" \
  --level success \
  --title "任务完成" \
  --sound success_chime
```

任务失败：

```bash
petctl notify \
  --source-id script.local \
  --source-kind custom \
  --source-name "Local Script" \
  --level error \
  --title "任务失败" \
  --message "请查看终端输出" \
  --sound error_chime
```

需要用户输入：

```bash
petctl notify \
  --source-id codex.local \
  --source-kind codex \
  --source-name Codex \
  --level need_input \
  --title "需要用户确认" \
  --message "有命令需要授权或有实现方向需要确认" \
  --sound need_input_chime
```

## 4. shell 示例目标

V2.0 shell 示例已落地：

```text
examples/shell/task-with-pet.sh
```

用法必须使用 `--` 分隔用户命令：

```bash
examples/shell/task-with-pet.sh -- pnpm test
examples/shell/task-with-pet.sh -- pnpm --filter desktop build
examples/shell/task-with-pet.sh -- false
```

shell 示例满足：

- 接收任意命令作为 `--` 后的参数。
- 命令开始前发送 `running`。
- 命令成功后发送 `success`。
- 命令失败后发送 `error`。
- 保留原命令退出码。
- 不使用 `eval`。
- 使用 `"$@"` 执行用户命令。
- 不打印完整 token。
- 不要求 MCP、USB 或后台 daemon。

## 5. Node 示例目标

V2.0 Node 示例已落地：

```text
examples/node/notify-pet.mjs
```

用法：

```bash
node examples/node/notify-pet.mjs running
node examples/node/notify-pet.mjs success
node examples/node/notify-pet.mjs error
node examples/node/notify-pet.mjs need_input
```

Node 示例满足：

- 不引入额外 SDK 作为强依赖。
- 使用 `child_process.spawnSync` 调用 `petctl notify`。
- 不使用 `shell: true` 拼接命令字符串。
- 不打印完整 token。
- 不发送路径或 URL 作为 sound。

## 6. Codex instruction template 目标

Codex template 应要求：

- 只通过 `petctl` 或 localhost HTTP 写入事件。
- 任务开始发送 `running` 或 `thinking`。
- 任务完成并验证后发送 `success`。
- 需要用户授权或决策时发送 `need_input`。
- 命令失败或阻塞时发送 `error`。
- 不直接控制 UI。
- 不执行桌宠内脚本。
- 不传本地文件路径、URL 或任意资源名作为 sound。
- 避免高频循环通知。
- 只在状态阶段变化时发送事件，不对每个文件、每行日志、每个小步骤发送事件。

## 7. Claude Code instruction template 目标

Claude Code template 应要求：

- 只通过 `petctl` 或 localhost HTTP 写入事件。
- 分析阶段可发送 `thinking`。
- 编辑、测试、构建阶段可发送 `running`。
- 非阻塞风险发送 `warning`。
- 阻塞或失败发送 `error`。
- 需要用户选择发送 `need_input`。
- 完成并验证后发送 `success`。
- 不绕过 PetEvent 协议。
- 只在分析、编辑、测试、构建、完成、失败、需要输入等阶段变化时发送事件。

## 8. petctl recipes

V2.0 Phase 2.1 已新增：

```text
docs/reference/petctl-recipes.md
```

recipes 覆盖：

- 测试开始 / 测试通过 / 测试失败。
- 构建开始 / 构建通过 / 构建失败。
- 长任务 `running`。
- 需要用户确认 `need_input`。
- `warning` 非阻塞问题。
- JSON stdin 示例。
- 常见错误排查：`desktop_not_running`、`token_missing`、`unauthorized`、`rate_limited`、invalid sound、`schema_invalid`。

## 9. 不在 V2.0 实现

- MCP server。
- Agent SDK。
- USB 硬件。
- 后台 daemon。
- 自动发现 desktop app。
- 持久化日志数据库。
- Windows ready / cross-platform ready。
- production signed release ready。

## 10. Phase 2.1 可声明内容

完成后最多声明：

```text
V2.0 Phase 2.1 complete: local workflow integration templates and petctl recipes ready.
```

Phase 2.1 完成时不得声明；当前 final acceptance passed 后，仍不得声明：

```text
Codex integration verified
Claude Code integration verified
MCP server ready
USB ready
Windows ready
cross-platform ready
production signed release ready
```

## 11. Phase 2.2 Settings Diagnostics

Phase 2.2 已将设置页 diagnostics 打磨为只读运行状态面板：

- Runtime health：API enabled、listen address、queue length/capacity、hardware light disabled、token status、last refresh time。
- Sound：playbackAvailable、muted、cooldownMs、acceptedIds、lastDecision。
- Recent accepted events：最多 10 条后端摘要。
- Recent rejected events：最多 10 条后端摘要，包含 reasonCode、reasonField 和简短安全 reason。
- Quick commands：只显示文本和复制按钮。

安全边界：

- 不显示完整 token。
- 不显示 token 文件绝对路径。
- 不显示原始 payload。
- 不显示 metadata 全量。
- 不显示 message 全文。
- 不显示声音文件路径。
- 不显示非法 sound 原文、URL、本地路径或非法 `source.id`。
- 不从设置页执行 shell、petctl、node 或 curl。
- 不提供 token 重置、日志清空、导出、搜索、分页。

完成后最多声明：

```text
V2.0 Phase 2.2 complete: settings diagnostics polish ready.
```

## 12. Phase 2.3 Cat Experience Polish

Phase 2.3 已打磨现有 CSS 占位猫体验：

- idle、thinking、running、success、warning、error、need_input、sleeping 8 个状态更可区分。
- thinking/running 仍保持低打扰，不把工作流状态变成通知中心。
- warning、error、need_input 的明显程度递进，但不绕过现有状态机 lock/cooldown。
- 动画只作用于猫内部元素，窗口、stage 和根容器尺寸不参与动画。
- 拖拽期间动画暂停或降级，拖拽优先。

Phase 2.3 不引入 Rive、Live2D、3D、照片自定义、MCP、USB 或 Windows ready 声明。

完成后最多声明：

```text
V2.0 Phase 2.3 complete: CSS placeholder cat experience polish ready.
```
