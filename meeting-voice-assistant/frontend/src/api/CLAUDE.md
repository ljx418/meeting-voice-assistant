# AI 代理指令 - API 模块

## WebSocket 客户端 (websocket.ts)

```typescript
interface UseWebSocketOptions {
  url: string
  onMessage: (msg: ServerMessage) => void
  onError?: (err: Event) => void
  onOpen?: () => void
  onClose?: () => void
}

function useWebSocket(options: UseWebSocketOptions): {
  connect(): Promise<void>
  send(msg: object): void
  sendAudio(chunk: Blob): void
  disconnect(): void
  isConnected(): boolean
}
```

## 消息处理流程

1. `useWebSocket` 接收原始消息
2. 根据 `msg.type` 分发到对应处理器
3. 组件通过 `onMessage` 回调接收

## 扩展指南

### 新增消息类型

1. 在 `types.ts` 添加新类型定义
2. 在 `useWebSocket.ts` 添加处理逻辑
3. 更新本文档

### 二进制数据

音频数据使用 `sendAudio(chunk: Blob)` 发送，内部自动处理 base64 编码。