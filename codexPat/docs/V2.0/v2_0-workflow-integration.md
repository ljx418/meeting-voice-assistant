# V2.0 Workflow Integration

文档状态：V2.0 planning baseline。

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

V2.0 shell 示例应满足：

- 接收任意命令作为参数。
- 命令开始前发送 `running`。
- 命令成功后发送 `success`。
- 命令失败后发送 `error`。
- 保留原命令退出码。
- 不打印完整 token。
- 不要求 MCP、USB 或后台 daemon。

## 5. Node 示例目标

V2.0 Node 示例应满足：

- 不引入额外 SDK 作为强依赖。
- 可以调用 `petctl notify`。
- 或通过 HTTP POST localhost API。
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

## 8. 不在 V2.0 实现

- MCP server。
- Agent SDK。
- USB 硬件。
- 后台 daemon。
- 自动发现 desktop app。
- 持久化日志数据库。

