# PetEvent 协议

## 协议定位

`PetEvent` 是外部 Agent 写入“状态意图”的协议，不是 UI 控制协议。

- Agent 只能发送结构化事件。
- Agent 不能直接控制 UI。
- Agent 不能执行本地脚本。
- Agent 不能传入任意本地资源路径。
- `action`、`sound`、`hardware.light.effect` 都必须是白名单 ID。
- `title` 和 `message` 不保证展示，由桌面端根据低打扰策略决定。
- `durationMs` 是建议展示时长，不是强制动画控制。

## Schema 策略

协议事实源必须是 JSON Schema 或等价跨语言 schema。

要求：

- TypeScript 类型从同一协议生成，或通过同一 fixtures 测试保持一致。
- Rust struct / validator 从同一协议生成，或通过同一 fixtures 测试保持一致。
- 不假设 Rust 可以直接调用 TypeScript/Zod schema。
- `packages/pet-protocol` 应同时提供 JSON Schema、TypeScript 类型和 capabilities 常量。
- 桌面 Rust side 与 petctl 都必须基于同一协议校验 PetEvent。

## TypeScript 类型草案

```ts
export type PetEventLevel =
  | "thinking"
  | "running"
  | "success"
  | "warning"
  | "error"
  | "need_input"
  | "idle"
  | "sleeping";

export type PetSourceKind =
  | "codex"
  | "claude_code"
  | "custom"
  | "system";

export type PetEventVia =
  | "http"
  | "cli"
  | "mcp"
  | "skill"
  | "internal";

export type PetAction =
  | "idle"
  | "thinking"
  | "running"
  | "success"
  | "warning"
  | "error"
  | "sleeping"
  | "need_input";

export type PetSound =
  | "none"
  | "success_chime"
  | "warning_chime"
  | "error_chime"
  | "need_input_chime";

export type LightEffect =
  | "none"
  | "thinking_pulse"
  | "running_flow"
  | "success_green"
  | "warning_amber"
  | "error_red"
  | "need_input_pulse"
  | "sleeping_dim";

export interface PetEvent {
  id?: string;
  source: {
    id: string;
    kind: PetSourceKind;
    name?: string;
  };
  via?: PetEventVia;
  level: PetEventLevel;
  title?: string;
  message?: string;
  action?: PetAction;
  sound?: PetSound;
  durationMs?: number;
  hardware?: {
    light?: {
      effect?: LightEffect;
      color?: string;
      blink?: number;
      brightness?: number;
    };
  };
  metadata?: Record<string, string | number | boolean | null>;
  createdAt?: string;
}
```

## JSON 示例

```json
{
  "source": {
    "id": "codex.local",
    "kind": "codex",
    "name": "Codex"
  },
  "level": "success",
  "title": "测试通过",
  "message": "pnpm test 已通过",
  "action": "success",
  "sound": "success_chime",
  "durationMs": 3000,
  "metadata": {
    "project": "agent-desktop-pet"
  }
}
```

Phase 3 的外部 HTTP payload 不允许携带 `via`；Rust HTTP 接收端会在验收通过后补为 `via: "http"`。

## 字段规则

- `source.id`：必填，长度 1 到 64，只允许字母、数字、点、短横线、下划线。
- `source.kind`：必填，只表示事件来源，必须是 `codex | claude_code | custom | system`。
- `via`：表示传输方式或接入层，必须是 `http | cli | mcp | skill | internal`；Phase 3 不允许外部 payload 自由传入，由 Rust HTTP 接收端补为 `http`。
- `level`：必填，必须是白名单枚举。
- `title`：可选，最多 80 字符；未传时桌面端按 `level` 提供默认 title。
- `message`：可选，最多 500 字符。
- `action`：可选，必须是白名单；未传则由 `level` 映射。
- `sound`：可选，必须是白名单；未传则由 `level` 映射。`sound` 是请求意图，不是强制播放命令；桌面端会按 level、静音和 cooldown 做最终决策。
- `durationMs`：可选，默认建议 5000，Phase 3 范围 1000 到 30000；它是建议展示时长，不保证动画强制播放这么久。
- `hardware.light.effect`：Post-MVP 预留，可选，必须是白名单；MVP 校验但不执行硬件效果。
- `hardware.light.color`：Post-MVP 预留，可选，必须是 `#RRGGBB`。
- `hardware.light.blink`：Post-MVP 预留，可选，0 到 10。
- `hardware.light.brightness`：Post-MVP 预留，可选，0 到 100。
- `metadata`：可选，最多 4KB；Phase 3 允许 primitive 或浅层对象，不允许数组和深层嵌套，最多 20 个 key。
- `createdAt`：由桌面端接收时补齐，外部传入可忽略。

## 默认映射

```text
thinking   -> action thinking    sound none          default title "Agent 正在思考"
running    -> action running     sound none          default title "Agent 正在执行"
success    -> action success     sound success_chime default title "任务完成"
warning    -> action warning     sound warning_chime default title "需要注意"
error      -> action error       sound error_chime   default title "任务失败"
need_input -> action need_input  sound need_input_chime default title "需要用户介入"
idle       -> action idle        sound none          default title "空闲"
sleeping   -> action sleeping    sound none          default title "休息中"
```

展示默认策略：

```text
thinking   -> 不弹文本，不播放声音
running    -> 不弹文本，不播放声音
success    -> 不弹文本或只显示极短反馈，可选轻提示音
warning    -> 可显示短文本，声音受冷却限制
error      -> 可显示短文本和声音
need_input -> 默认显示短文本和声音
idle       -> 不弹文本
sleeping   -> 不弹文本，不播放声音
```

Phase 6 声音安全策略：

- 只播放应用 bundle 内置音频资源。
- 外部事件只能传 sound ID，不能传本地路径、相对路径、绝对路径或 URL。
- `thinking` / `running` 即使携带 sound，也按低打扰策略不播放。
- 静音开启时所有声音都跳过。
- 高频提示在 cooldown 内不重复播放。
- diagnostics 只返回 sound ID、播放决策和状态，不暴露 bundle 路径或文件路径。

## 非法事件处理

- JSON Schema 校验失败：HTTP `400`，记录安全日志，不进入 Rust Ingress Queue。
- token 缺失或错误：HTTP `401`。
- 速率超限：HTTP `429`。
- 白名单字段非法：HTTP `400`，不做 fallback。
- 队列满：HTTP `429`，明确表示事件未接收。

## HTTP API

```text
GET  /api/health
POST /api/events
GET  /api/capabilities
GET  /api/diagnostics
```

所有写接口必须包含：

```text
Authorization: Bearer <local-token>
Content-Type: application/json
```

`GET /api/diagnostics` 也必须包含 `Authorization: Bearer <local-token>`。`GET /api/health` 和 `GET /api/capabilities` 不需要 token，但不得返回 token 或配置路径。

`POST /api/events` 成功统一返回 `202 Accepted`：

```json
{
  "ok": true,
  "accepted": true,
  "eventId": "evt_...",
  "queued": true
}
```

错误响应包含 `reasonCode`、`reasonField` 和泛化 `reason`。`reason` 不允许直接使用 JSON Schema 库的原始错误字符串，因为原始错误可能回显用户提交的路径、URL 或非法字段值。

```json
{
  "ok": false,
  "accepted": false,
  "reasonCode": "schema_invalid",
  "reasonField": "source.id",
  "reason": "source id is invalid"
}
```

常见 `reasonField`：

```text
payload
source.id
level
action
sound
hardware.light.effect
auth
rate_limit
queue
bridge
```

用户可见错误文案必须安全化：

- 非法 sound：`sound is not an accepted ID`
- 非法 level：`level is not an accepted value`
- 非法 action：`action is not an accepted ID`
- 非法硬件灯效：`hardware light effect is not an accepted ID`
- 非法 source id：`source id is invalid`
- 通用 schema 错误：`payload failed schema validation`
- 缺少 token：`authorization bearer token is required`
- token 错误：`authorization bearer token is invalid`
- 限流：`source rate limit exceeded`
- 队列满：`event queue is full`

Phase 4 diagnostics 只保留事件摘要，不保存原始 payload、metadata 全量或 message 全文。V2.1-A 起，diagnostics rejected summary 和 HTTP error response 均不得回显非法 sound 原文、URL、本地路径或非法 `source.id`；schema/白名单错误必须通过 `reasonCode` + `reasonField` + 泛化 `reason` 表达。
