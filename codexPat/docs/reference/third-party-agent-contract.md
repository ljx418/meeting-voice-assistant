# Third-party Agent Contract

文档状态：V2.1-A local HTTP contract smoke passed。

本文说明自定义本地 agent 如何安全接入 agent-desktop-pet。第三方 agent 只能写入结构化事件，不能控制 UI、执行桌宠脚本或传入本地资源路径。

## Endpoint

```text
POST http://127.0.0.1:17321/api/events
Authorization: Bearer <local-token>
Content-Type: application/json
```

推荐先检查：

```bash
curl -sS http://127.0.0.1:17321/api/health
curl -sS http://127.0.0.1:17321/api/capabilities
```

## Source

推荐：

```json
{
  "source": {
    "id": "my-agent.local",
    "kind": "custom",
    "name": "My Agent"
  }
}
```

`source.id` 应稳定、短小，只使用字母、数字、点、短横线和下划线。

## Minimal Event

```json
{
  "source": {
    "id": "my-agent.local",
    "kind": "custom",
    "name": "My Agent"
  },
  "level": "success",
  "title": "任务完成",
  "sound": "success_chime"
}
```

## Security Boundaries

- API 只接受 localhost 调用。
- 必须带 Bearer token。
- `sound` 只能是白名单 ID：`none`、`success_chime`、`warning_chime`、`error_chime`、`need_input_chime`。
- 禁止传本地路径、相对路径、绝对路径、URL 或任意资源名作为 sound。
- Agent 不能直接控制桌宠 UI。
- Agent 不能执行桌宠内部脚本。
- 高频事件必须节流，只在状态阶段变化时发送。

## Error Handling

| Status | Meaning | Agent behavior |
| --- | --- | --- |
| 400 | schema invalid、whitelist invalid、payload too large | 修正 payload，不要盲目重试。 |
| 401 | missing/invalid token | 提示配置 token，不打印完整 token。 |
| 429 | rate limited 或 queue full | 退避 2-5 秒后重试，不循环刷。 |
| 503 | bridge unavailable | 提示启动桌宠或检查端口。 |
| connection refused | desktop app 未运行 | 提示用户启动 app。 |

错误响应格式：

```json
{
  "ok": false,
  "accepted": false,
  "reasonCode": "whitelist_invalid",
  "reasonField": "sound",
  "reason": "sound is not an accepted ID"
}
```

`reason` 是安全化后的泛化文案，不会回显提交的非法 sound、路径、URL、token、原始 payload 或非法 `source.id`。第三方 agent 应根据 `reasonCode` 和 `reasonField` 做分支处理，不要依赖 `reason` 中包含原始输入值。

常见 `reasonField`：

- `auth`
- `payload`
- `source.id`
- `level`
- `action`
- `sound`
- `hardware.light.effect`
- `rate_limit`
- `queue`
- `bridge`

## Rate-limit Guidance

- `thinking` / `running` 只在阶段开始或状态变化时发送。
- 不要按日志行、文件、测试用例或 tool call 发送事件。
- `success` / `warning` / `error` / `need_input` 只在任务状态发生明确变化时发送。
- 429 后至少等待 2 秒再试。

## Examples

- `examples/http/curl-agent-smoke.sh`
- `examples/http/node-http-agent-smoke.mjs`
- `examples/http/python_http_agent_smoke.py`

这些示例只用于本地 smoke，不是 SDK。

V2.1-A 已验证 curl / Node / Python success、401、400、429、invalid sound path / URL redaction 和 invalid source id redaction。该结论只允许声明 `Third-party local HTTP contract smoke passed`，不等于真实第三方 agent 产品集成已验证。
