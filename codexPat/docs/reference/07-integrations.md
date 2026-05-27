# Integrations Reference

文档状态：V3.7 integration reference。

当前已有本地 HTTP API、`petctl notify` CLI、safe sound feedback、多实例路由、最小 MCP adapter、Codex session wrapper 和 V3.7 `codex exec --json` JSONL monitor。V3.7 JSONL monitor 是当前推荐的 Codex exec 监听路径。MCP adapter 和 JSONL monitor 都只能通过 localhost HTTP/Event Bridge 写入结构化 PetEvent，不能直接控制 UI，也不能绕过 PetEvent schema、token、白名单、rate limit 或 diagnostics。

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

## Codex Wrapper and JSONL Monitor

Wrapper-first Codex binding：

```bash
petctl codex launch --name "Review Cat" -- exec --help
```

JSONL monitor for wrapper-launched `codex exec --json`，当前推荐 Codex exec 监听路径：

```bash
petctl codex launch --monitor jsonl --name "Review Cat" -- exec --json "summarize this repository"
```

等价显式命令形态：

```bash
petctl codex launch --monitor jsonl --name "Review Cat" -- codex exec --json "summarize this repository"
```

规则：

- 默认 `--monitor none` 保持旧 wrapper 行为：根据子进程 exit code 发送最终 `success` / `error`。
- `--monitor jsonl` 只适用于 wrapper-launched `codex exec --json`。
- JSONL monitor 只解析结构化 `type` / `event.type`。
- 不解析人类可读终端文本。
- 不读取或依赖 `transcript_path`。
- 不记录 raw JSONL、prompt 原文、tool command 原文、token、Authorization、完整本地路径、workspace path 或 config path。

初始状态映射：

| JSONL event type | Pet state |
| --- | --- |
| `thread.started` | marker-only |
| `turn.started` | `thinking` |
| `item.started` | `running` |
| `item.completed` | marker / keep current |
| `turn.completed` | `success` only if no current-turn error |
| `turn.failed` | `error` |
| `error` | `error` |

Allowed scoped claim after V3.7 acceptance:

```text
V3.7 Codex exec JSONL monitor state mapping passed for tested local wrapper-launched codex exec --json scenarios.
```

Forbidden expansions:

```text
V3.6 selected Codex workflow hook coverage smoke passed
PostToolUse failure hook evidence passed
all Codex workflows verified
Codex internal reasoning exact mapping ready
OS-level Codex window binding ready
```

V3.6 hook-only monitoring remains historical blocked evidence and is deprecated as the active strategy. Do not describe V3.7 as official `PostToolUse` failure hook evidence.

## HTTP API

```text
POST http://127.0.0.1:17321/api/events
POST http://127.0.0.1:17321/api/instances/:instanceId/events
Authorization: Bearer <local-token>
Content-Type: application/json
```

`/api/events` 是 legacy default route，只影响 default pet。`/api/instances/:instanceId/events` 是 V3 multi-instance route，只影响目标 pet。

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

## V3.2 MCP Adapter Tools

工具列表：

```text
pet_notify
pet_list_instances
pet_get_capabilities
pet_get_state
```

所有 MCP 工具都必须通过 localhost HTTP/Event Bridge。工具不得直接控制桌宠 UI、窗口、状态机、资源加载或声音文件。

`pet_notify` 参数：

```json
{
  "instanceId": "codex_123",
  "event": {
    "source": {
      "id": "mcp-agent.local",
      "kind": "custom",
      "name": "MCP Agent"
    },
    "level": "running",
    "title": "正在分析代码",
    "message": "扫描项目结构。",
    "action": "running",
    "sound": "none",
    "durationMs": 5000,
    "metadata": {
      "task": "repo-analysis"
    }
  },
}
```

规则：

- `instanceId` 可选；省略时走 legacy default route。
- `instanceId` 存在时走 `/api/instances/:instanceId/events`。
- payload 不能包含 `via`；transport 由 bridge 记录。
- payload 必须符合 PetEvent schema。

`pet_list_instances`：

- 读取 `GET /api/instances`。
- 返回 sanitized instance list。
- 不返回 token、Authorization header、raw payload、完整本地路径、`position`、`workspaceLabel` 或 `workspaceHash`。

`pet_get_capabilities`：

- 读取 `GET /api/capabilities`。
- 可接受 `instanceId` 参数以保持工具调用形状一致，但当前返回全局 capabilities。

`pet_get_state`：

- 读取 sanitized instance state。
- `instanceId` 可选；省略时返回所有实例的 sanitized state。
- unknown instance 返回 `instance_not_found`。

Deferred tools：

```text
pet_set_status
pet_clear_status
```

这两个工具不是 V3.2 MCP adapter 的已验收工具。长任务状态应通过 `pet_notify` 发送 `thinking` / `running` / `sleeping` 等结构化事件；清空状态应通过后续 `idle` 或其他状态事件表达。

V3.2 允许声明 `V3.2 MCP adapter minimal smoke passed for localhost bridge routing.`，但不得声明 `MCP ready`。

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
