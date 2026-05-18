# V1.0 Protocol And Security

## PetEvent

V1.0 使用 JSON Schema 作为 PetEvent 协议事实源：

```text
packages/pet-protocol/schemas/pet-event.schema.json
```

最小事件：

```json
{
  "source": {
    "id": "custom.local",
    "kind": "custom",
    "name": "Custom Agent"
  },
  "level": "success",
  "title": "任务完成",
  "message": "测试通过",
  "action": "success",
  "sound": "success_chime",
  "durationMs": 3000
}
```

`source.kind` 白名单：

```text
codex
claude_code
custom
system
```

`level` / `action` 白名单：

```text
idle
thinking
running
success
warning
error
need_input
sleeping
```

`sound` 白名单：

```text
none
success_chime
warning_chime
error_chime
need_input_chime
```

`hardware.light.effect` 在 V1.0 只校验和保留，不控制硬件。

## HTTP API

```text
GET  /api/health
GET  /api/capabilities
POST /api/events
GET  /api/diagnostics
```

安全要求：

- API 只监听 `127.0.0.1`。
- `POST /api/events` 必须 `Authorization: Bearer <local-token>`。
- `GET /api/diagnostics` 必须 `Authorization: Bearer <local-token>`。
- `GET /api/health` 和 `GET /api/capabilities` 不返回 token 或敏感路径。

成功写入返回 `202 Accepted`：

```json
{
  "ok": true,
  "accepted": true,
  "eventId": "evt_...",
  "queued": true
}
```

错误语义：

```text
400 schema_invalid / whitelist_invalid / payload_too_large
401 auth_missing / auth_invalid
429 rate_limited / queue_full
503 bridge_unavailable / port_bind_failed
```

## petctl

默认写入：

```text
http://127.0.0.1:17321/api/events
```

示例：

```bash
petctl notify \
  --source-id custom.local \
  --source-kind custom \
  --level success \
  --title "测试通过" \
  --sound success_chime
```

JSON stdin：

```bash
petctl notify --json < event.json
```

token 优先级：

```text
--token
AGENT_DESKTOP_PET_TOKEN
desktop app config api-token.json
```

URL 优先级：

```text
--url
AGENT_DESKTOP_PET_URL
http://127.0.0.1:17321
```

## 安全边界

- Agent 只能发送结构化 PetEvent。
- Agent 不能直接控制 UI。
- Agent 不能执行桌宠内脚本。
- Agent 不能传入本地声音路径、资源路径、相对路径、绝对路径或 URL。
- 动作、声音、硬件效果必须使用白名单 ID。
- 非法事件写入 rejected summary，但不进入状态机。
- diagnostics 不保存原始 payload，不保存 metadata 全量，不保存 message 全文，不暴露声音文件路径。
- rejected summary 和 HTTP error response 不得直接回显 JSON Schema 库原始错误；非法路径、URL、非法 sound 原文和非法 `source.id` 必须被泛化为 `reasonCode`、`reasonField` 和安全 `reason`。

## Safe Sound

内置声音映射：

```text
success_chime    -> bundle asset
warning_chime    -> bundle asset
error_chime      -> bundle asset
need_input_chime -> bundle asset
none             -> no playback
```

播放策略：

- `thinking` / `running` / `idle` / `sleeping` 默认不播放声音。
- `success` 轻提示。
- `warning` 轻提示。
- `error` 短促明显提示。
- `need_input` 明显提示，但受 cooldown 控制。
- 静音开启时所有声音都不播放。
- `PetEvent.sound` 是请求意图，不是强制播放命令。
