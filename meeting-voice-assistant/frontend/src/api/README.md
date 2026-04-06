# API 客户端文档

## 概述

封装 WebSocket 通信和类型定义。

## 文件

| 文件 | 职责 |
|------|------|
| `websocket.ts` | WebSocket 客户端封装 |
| `types.ts` | TypeScript 类型定义 |

## WebSocket 使用方式

```typescript
import { useWebSocket } from './composables/useWebSocket'

const ws = useWebSocket({
  url: 'ws://localhost:8000/api/v1/ws/voice',
  onMessage: (msg) => {
    console.log('Received:', msg)
  },
  onError: (err) => {
    console.error('Error:', err)
  },
  onOpen: () => {
    console.log('Connected')
  },
})

// 连接
await ws.connect()

// 发送控制消息
ws.send({ type: 'control', action: 'start' })

// 发送音频数据
ws.sendAudio(audioChunk: Blob)

// 断开
ws.disconnect()
```

## 消息类型 (types.ts)

```typescript
// 客户端 -> 服务端
type ClientMessage =
  | { type: 'control'; action: 'start' | 'stop' | 'status' }
  | { type: 'audio'; data: string }  // base64

// 服务端 -> 客户端
type ServerMessage =
  | { type: 'welcome'; session_id: string; config: Config }
  | { type: 'transcript'; data: TranscriptSegment }
  | { type: 'final'; data: TranscriptResult }
  | { type: 'summary'; data: MeetingSummary }
  | { type: 'error'; message: string }
```

## 配置

`VITE_WS_URL` 环境变量配置 WebSocket 地址，默认 `ws://localhost:8000/api/v1/ws/voice`。