# Third-party Agent Contract v3

文档状态：V3.2 multi-instance contract draft。

本文说明自定义本地 agent 如何安全接入 agent-desktop-pet。第三方 agent 只能写入结构化 `PetEvent`，不能控制 UI、执行桌宠脚本、读取本地配置、传入本地资源路径，或绕过 HTTP/Event Bridge。

## Contract Shape

V3 contract 有两种事件入口：

```text
POST http://127.0.0.1:17321/api/events
POST http://127.0.0.1:17321/api/instances/:instanceId/events
Authorization: Bearer <local-token>
Content-Type: application/json
```

- `/api/events` 是 legacy default route，只影响 default pet。
- `/api/instances/:instanceId/events` 是 V3 multi-instance route，只影响目标 pet。
- unknown instance 返回 `404 instance_not_found`。
- invalid instance id 返回 `400 instance_id_invalid`。

推荐先检查：

```bash
curl -sS http://127.0.0.1:17321/api/health
curl -sS http://127.0.0.1:17321/api/capabilities
```

需要读取实例列表时：

```text
GET http://127.0.0.1:17321/api/instances
Authorization: Bearer <local-token>
```

## PetEvent

推荐 source：

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

最小事件：

```json
{
  "source": {
    "id": "my-agent.local",
    "kind": "custom",
    "name": "My Agent"
  },
  "level": "success",
  "title": "Task complete",
  "sound": "success_chime"
}
```

第三方 agent 不应提交 `via`。transport 由 bridge 侧记录。

## CLI Contract

如果 agent 不想直接写 HTTP，可以使用 `petctl`：

```bash
petctl attach codex --name "Codex A" --print-env
petctl list
petctl notify --instance <instanceId> --level success --title "Task complete"
```

也可以通过环境变量让当前进程固定路由到某只猫：

```bash
export AGENT_DESKTOP_PET_INSTANCE_ID=<instanceId>
petctl notify --level need_input --title "Input needed"
```

规则：

- 显式 `--instance` 优先于 `AGENT_DESKTOP_PET_INSTANCE_ID`。
- 没有 instance 时走 legacy default route。
- 环境变量里的 unknown instance 不会 fallback 到 default。

## Instance Lifecycle

创建实例：

```text
POST /api/instances
```

请求字段：

- `sourceKind`：当前允许 `codex` 或 `custom`。
- `sourceId`：稳定 source id。
- `displayName`：显示名。
- `workspaceLabel`：可选短标签，不得是路径。
- `workspaceHash`：可选稳定 hash。

限制：

- 当前 hard limit 为 12 只 pet，包括 default。
- 超出 hard limit 返回 `409 instance_limit_reached`。
- default instance 不能 detach。

## Security Boundaries

- API 只接受 localhost 调用。
- 必须带 Bearer token。
- `sound` 只能是白名单 ID：`none`、`success_chime`、`warning_chime`、`error_chime`、`need_input_chime`。
- 禁止传本地路径、相对路径、绝对路径、URL 或任意资源名作为 sound。
- Agent 不能直接控制桌宠 UI。
- Agent 不能执行桌宠内部脚本。
- Agent 不能读取 token、settings、workspace path 或 config path。
- 高频事件必须节流，只在状态阶段变化时发送。

错误响应和 diagnostics 不应回显：

```text
token
Authorization header
raw payload
完整 /Users/... 路径
workspace path
非法 sound 原值
```

## Error Handling

| Status | reasonCode | Meaning | Agent behavior |
| --- | --- | --- | --- |
| 400 | `schema_invalid` | payload 不符合 PetEvent schema | 修正 payload，不要盲目重试。 |
| 400 | `whitelist_invalid` | action / sound / light effect 非白名单 | 使用 capability 中的 ID。 |
| 400 | `instance_id_invalid` | instance id 格式非法 | 修正 instance id，不要重试。 |
| 401 | `auth_missing` / `auth_invalid` | token 缺失或错误 | 提示配置 token，不打印完整 token。 |
| 404 | `instance_not_found` | instance 不存在 | 重新 attach 或让用户选择目标猫。 |
| 409 | `instance_limit_reached` | pet 数量达到 hard limit | 提示用户 detach 不需要的实例。 |
| 429 | `rate_limited` / `queue_full` | 事件过快或队列满 | 退避 2-5 秒后重试。 |
| 503 | `bridge_unavailable` | bridge 不可用 | 提示启动桌宠或检查端口。 |
| connection refused | `desktop_not_running` | app 未运行 | 提示用户启动 app。 |

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

## Rate-limit Guidance

- `thinking` / `running` 只在阶段开始或状态变化时发送。
- 不要按日志行、文件、测试用例或 tool call 发送事件。
- `success` / `warning` / `error` / `need_input` 只在任务状态发生明确变化时发送。
- 429 后至少等待 2 秒再试。

## Examples

- `examples/http/curl-agent-smoke.sh`
- `examples/http/node-http-agent-smoke.mjs`
- `examples/http/python_http_agent_smoke.py`

这些示例只用于本地 contract smoke，不是 SDK。

## Allowed Claim

如果 V3 contract smoke 通过，只允许声明：

```text
V3.2 third-party contract v3 smoke passed.
```

这不等于真实第三方 agent 产品集成已验证。若没有真实第三方产品、版本、生命周期触发路径和 evidence，不得声明：

```text
Third-party agent integration verified
```
