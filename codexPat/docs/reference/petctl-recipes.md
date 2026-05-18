# petctl Recipes

文档状态：V2.0 Phase 2.1 command cookbook。

本文只提供可复制的 `petctl notify` 命令示例。完整接入边界见 `docs/reference/agent-integration-guide.md`。

## 1. 环境变量

```bash
export AGENT_DESKTOP_PET_URL="http://127.0.0.1:17321"
export AGENT_DESKTOP_PET_TOKEN="<local-token>"
```

不要在日志、CI 输出或聊天消息中打印完整 token。

## 2. 测试任务

测试开始：

```bash
petctl notify \
  --source-id script.local \
  --source-kind custom \
  --source-name "Local Script" \
  --level running \
  --title "测试正在运行"
```

测试通过：

```bash
petctl notify \
  --source-id script.local \
  --source-kind custom \
  --source-name "Local Script" \
  --level success \
  --title "测试通过" \
  --sound success_chime
```

测试失败：

```bash
petctl notify \
  --source-id script.local \
  --source-kind custom \
  --source-name "Local Script" \
  --level error \
  --title "测试失败" \
  --message "请查看终端输出" \
  --sound error_chime
```

## 3. 构建任务

构建开始：

```bash
petctl notify \
  --source-id script.local \
  --source-kind custom \
  --source-name "Local Script" \
  --level running \
  --title "构建正在运行"
```

构建通过：

```bash
petctl notify \
  --source-id script.local \
  --source-kind custom \
  --source-name "Local Script" \
  --level success \
  --title "构建通过" \
  --sound success_chime
```

构建失败：

```bash
petctl notify \
  --source-id script.local \
  --source-kind custom \
  --source-name "Local Script" \
  --level error \
  --title "构建失败" \
  --message "请查看终端输出" \
  --sound error_chime
```

## 4. 长任务 running

```bash
petctl notify \
  --source-id script.local \
  --source-kind custom \
  --source-name "Local Script" \
  --level running \
  --title "长任务正在执行" \
  --message "完成后会发送结果"
```

不要在循环内持续发送 `running`。同一个任务阶段只发送一次即可。

## 5. 需要用户确认

```bash
petctl notify \
  --source-id codex.local \
  --source-kind codex \
  --source-name Codex \
  --level need_input \
  --title "需要用户确认" \
  --message "有命令需要授权或实现方向需要确认" \
  --sound need_input_chime
```

## 6. warning 非阻塞问题

```bash
petctl notify \
  --source-id claude-code.local \
  --source-kind claude_code \
  --source-name "Claude Code" \
  --level warning \
  --title "发现非阻塞问题" \
  --message "任务可继续，但建议稍后处理" \
  --sound warning_chime
```

## 7. JSON stdin

```bash
petctl notify --json <<'JSON'
{
  "source": {
    "id": "script.local",
    "kind": "custom",
    "name": "Local Script"
  },
  "level": "success",
  "title": "脚本完成",
  "message": "本地任务已结束",
  "sound": "success_chime"
}
JSON
```

## 8. 常见错误排查

`desktop_not_running`：

- 桌面 App 未启动。
- 检查 `GET http://127.0.0.1:17321/api/health`。

`token_missing`：

- 未提供 token。
- 设置 `AGENT_DESKTOP_PET_TOKEN`，或确认 desktop app config token 文件存在。

`unauthorized`：

- token 错误或过期。
- 不要在日志中打印完整 token，只确认 token 来源。

`rate_limited`：

- 事件过于频繁。
- 只在阶段变化时发送事件，不要对每个文件、日志行、小步骤发送事件。

`invalid sound`：

- `sound` 不是白名单 ID，或传入了路径/URL。
- 只使用：`none`、`success_chime`、`warning_chime`、`error_chime`、`need_input_chime`。
- 桌面端不会在 diagnostics 或 HTTP error response 中回显非法路径/URL；请根据 `reasonCode=whitelist_invalid` 和 `reasonField=sound` 排查。

`schema_invalid`：

- payload 不符合 PetEvent JSON Schema。
- 检查 `source.id`、`source.kind`、`level`、`durationMs`、`title/message` 长度和 `metadata` 大小。
