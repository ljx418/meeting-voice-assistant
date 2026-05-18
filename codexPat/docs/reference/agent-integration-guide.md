# Agent Integration Guide

文档状态：V2.0 Phase 2.1 workflow integration reference。

本文说明如何把真实本地开发工作流接入 agent-desktop-pet。V2.0 只提供 `petctl`、HTTP、instruction template 和示例，不实现 MCP server、USB、Windows ready、后台 daemon、自动发现或新 SDK。

## 1. 核心原则

桌宠是低打扰状态反馈层，不是 Agent 控制器。

- Agent 只能写入结构化 PetEvent。
- Agent 不能直接控制 UI。
- Agent 不能执行桌宠内脚本。
- Agent 不能传入本地路径、相对路径、绝对路径或 URL 作为 sound/resource。
- `sound` 只能使用白名单 ID：`none`、`success_chime`、`warning_chime`、`error_chime`、`need_input_chime`。
- 只在状态阶段变化时发送事件，不对每个文件、每行日志、每个小步骤发送事件。
- `thinking` / `running` 默认低打扰，通常不播放声音。

## 2. 环境变量

统一使用：

```text
AGENT_DESKTOP_PET_TOKEN
AGENT_DESKTOP_PET_URL
```

默认 URL：

```text
http://127.0.0.1:17321
```

`petctl` token 读取优先级：

```text
--token
AGENT_DESKTOP_PET_TOKEN
desktop app config api-token.json
```

URL 读取优先级：

```text
--url
AGENT_DESKTOP_PET_URL
http://127.0.0.1:17321
```

## 3. 推荐 source

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

Shell：

```text
source.id = script.local
source.kind = custom
source.name = Local Script
```

Node：

```text
source.id = node.local
source.kind = custom
source.name = Node Script
```

## 4. 状态映射

```text
thinking   -> 分析、规划、阅读代码
running    -> 编辑、测试、构建、执行长任务
success    -> 完成并验证通过
warning    -> 非阻塞问题或残余风险
error      -> 命令失败、实现阻塞、不可恢复问题
need_input -> 需要用户授权、确认、凭据或决策
```

## 5. Codex 接入

Codex instruction template 位于：

```text
skills/codex-agent-pet/SKILL.md
```

示例：

```bash
petctl notify \
  --source-id codex.local \
  --source-kind codex \
  --source-name Codex \
  --level running \
  --title "Codex 正在执行任务"
```

完成且验证通过：

```bash
petctl notify \
  --source-id codex.local \
  --source-kind codex \
  --source-name Codex \
  --level success \
  --title "Codex 任务完成" \
  --message "已完成并通过验证" \
  --sound success_chime
```

## 6. Claude Code 接入

Claude Code instruction template 位于：

```text
skills/claude-agent-pet/SKILL.md
```

示例：

```bash
petctl notify \
  --source-id claude-code.local \
  --source-kind claude_code \
  --source-name "Claude Code" \
  --level thinking \
  --title "Claude Code 正在分析代码"
```

构建或测试失败：

```bash
petctl notify \
  --source-id claude-code.local \
  --source-kind claude_code \
  --source-name "Claude Code" \
  --level error \
  --title "Claude Code 执行失败" \
  --message "请查看终端输出" \
  --sound error_chime
```

## 7. Shell 接入

示例脚本：

```text
examples/shell/task-with-pet.sh
```

用法必须使用 `--` 分隔用户命令：

```bash
examples/shell/task-with-pet.sh -- pnpm test
examples/shell/task-with-pet.sh -- pnpm --filter desktop build
examples/shell/task-with-pet.sh -- false
```

脚本要求：

- 不使用 `eval`。
- 使用 `"$@"` 执行用户命令。
- 命令开始前发送 `running`。
- 命令成功后发送 `success`。
- 命令失败后发送 `error`。
- 保留原命令 exit code。
- 不打印完整 token。

## 8. Node 接入

示例脚本：

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

Node 示例使用 `child_process.spawnSync` 调用 `petctl notify`，不使用 `shell: true` 拼接命令字符串，不引入新 SDK。

## 9. 声明边界

本指南只说明 local workflow templates 和 `petctl` 接入方式。V2.0 final acceptance 通过后可以声明 templates ready，但仍不得声明：

```text
Codex integration verified
Claude Code integration verified
MCP server ready
USB ready
Windows ready
cross-platform ready
production signed release ready
```
