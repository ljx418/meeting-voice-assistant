# Integrations Reference

文档状态：Phase 6 complete；MCP/Skill reference。

当前 Phase 6 已完成本地 HTTP API、`petctl notify` CLI 和 safe sound feedback 闭环。MCP server、Codex Skill、Claude Code Skill 都是 Post-MVP adapter / instruction layer，不能作为当前验收项。

## petctl CLI

标准命令：

```bash
petctl notify \
  --level need_input \
  --title "Codex 需要确认" \
  --message "命令需要用户授权" \
  --source-id codex.local \
  --source-kind codex \
  --action need_input \
  --sound need_input_chime \
  --duration-ms 8000 \
  --light-effect need_input_purple
```

简化命令：

```bash
petctl notify --level running --title "正在执行测试"
petctl notify --level success --title "任务完成" --sound success_chime
petctl notify --level error --title "构建失败" --message "npm run build 返回非零状态" --sound error_chime
```

声音规则：

- `sound` 只能是白名单 ID：`none`、`success_chime`、`warning_chime`、`error_chime`、`need_input_chime`。
- `thinking` / `running` 默认静默。
- `success` / `warning` / `error` / `need_input` 由桌面端按低打扰策略和 cooldown 决定是否播放。
- `sound` 不接受路径、URL 或用户上传资源。

JSON stdin：

```bash
petctl notify --json <<'JSON'
{
  "source": {
    "id": "custom.agent",
    "kind": "custom"
  },
  "level": "warning",
  "title": "发现潜在问题",
  "message": "测试覆盖率下降。",
  "action": "warning",
  "sound": "warning_chime"
}
JSON
```

开发期运行：

```bash
pnpm --filter @agent-desktop-pet/petctl petctl -- notify --level success --title "任务完成"
```

token 读取优先级：

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

## HTTP API

```text
POST http://127.0.0.1:17321/api/events
Authorization: Bearer <local-token>
Content-Type: application/json
```

示例：

```json
{
  "source": {
    "id": "claude-code.local",
    "name": "Claude Code",
    "kind": "claude_code"
  },
  "level": "running",
  "title": "Claude Code 正在修改文件",
  "message": "正在执行实现阶段。",
  "durationMs": 5000
}
```

curl：

```bash
curl -X POST http://127.0.0.1:17321/api/events \
  -H "Authorization: Bearer $AGENT_PET_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "source": { "id": "my-agent", "kind": "custom" },
    "level": "success",
    "title": "自定义 agent 完成任务",
    "message": "报告已经生成。"
  }'
```

## Post-MVP MCP tools

工具列表：

```text
pet_notify
pet_set_status
pet_clear_status
pet_get_capabilities
pet_get_state
```

`pet_notify` 参数：

```json
{
  "level": "running",
  "title": "正在分析代码",
  "message": "扫描项目结构。",
  "action": "running",
  "sound": "none",
  "durationMs": 5000,
  "hardware": {
    "light": {
      "effect": "running_flow"
    }
  },
  "metadata": {
    "task": "repo-analysis"
  }
}
```

`pet_set_status`：

- 用于较长任务状态，例如 `thinking`、`running`、`sleeping`。
- 可以被后续状态覆盖。

`pet_clear_status`：

- 清空当前来自某 source 的状态。
- 猫咪回到 `idle` 或继续消费队列。

## Post-MVP Codex Skill

`skills/codex-agent-pet/SKILL.md` 应包含：

```text
# Codex Agent Pet

Use this skill when working in a local project and the user wants desktop pet status updates.

Rules:
- Never control UI directly.
- Only send structured PetEvent through petctl or local HTTP API.
- Use whitelisted level/action/sound IDs.
- Do not pass local file paths as sound or asset.
- Send running when starting meaningful work.
- Send need_input when user approval or clarification is required.
- Send success when task is completed.
- Send error when blocked by a command or implementation failure.
- Keep messages short.

Preferred command:
petctl notify --level <level> --title "<title>" --message "<message>"

Examples:
petctl notify --level running --title "Codex 正在检查项目"
petctl notify --level need_input --title "需要授权执行命令"
petctl notify --level success --title "实现完成"
```

## Post-MVP Claude Code Skill

`skills/claude-agent-pet/SKILL.md` 应包含：

```text
# Claude Code Agent Pet

Use this skill to report Claude Code task status to Agent Desktop Pet.

Rules:
- Emit events only through petctl, MCP, or local HTTP.
- Do not send arbitrary scripts, file paths, URLs, or resource names.
- Use need_input before asking the user for a decision.
- Use error only for actual blockers or failed commands.
- Use success only after verification or clear completion.

Recommended events:
- thinking: reading or planning
- running: editing, testing, building
- warning: non-blocking issue
- error: blocked or failed
- need_input: user decision required
- success: completed
```
