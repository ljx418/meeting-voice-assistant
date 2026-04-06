# Composables 文档

## 概述

Vue 3 组合式函数封装复用逻辑。

## 文件

| 文件 | 职责 |
|------|------|
| `useAudioRecorder.ts` | 录音采集控制 |
| `useWebSocket.ts` | WebSocket 连接管理 |

## useAudioRecorder

```typescript
const {
  isRecording,        // 是否正在录音
  audioLevel,         // 当前音频级别 (0-1)
  startRecording,     // 开始录音
  stopRecording,      // 停止录音
  getAudioChunk,      // 获取音频块 (Promise)
} = useAudioRecorder({
  onAudioData?: (chunk: Blob) => void
})
```

### 使用示例

```typescript
const recorder = useAudioRecorder({
  onAudioData: (chunk) => {
    ws.sendAudio(chunk)
  }
})

// 开始
await recorder.startRecording()

// 停止
const finalChunk = await recorder.stopRecording()
```

## useWebSocket

```typescript
const {
  isConnected,       // 连接状态
  connect,            // 建立连接
  disconnect,         // 断开连接
  send,               // 发送消息
  sendAudio,          // 发送音频
  onMessage,           // 消息回调
} = useWebSocket(options)
```

### 使用示例

```typescript
const ws = useWebSocket({
  url: 'ws://localhost:8000/api/v1/ws/voice',
  onMessage: (msg) => {
    if (msg.type === 'transcript') {
      store.addTranscript(msg.data)
    }
  }
})

await ws.connect()
ws.send({ type: 'control', action: 'start' })
```
