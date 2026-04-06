# AI 代理指令 - Composables

## useAudioRecorder

### 实现细节

使用 Web Audio API 和 MediaRecorder API：

```typescript
// 内部实现
const audioContext = new AudioContext()
const mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true })
const mediaRecorder = new MediaRecorder(mediaStream, {
  mimeType: 'audio/webm;codecs=opus'
})
```

### 配置选项

```typescript
interface RecorderOptions {
  onAudioData?: (chunk: Blob) => void  // 音频数据回调
  audioBitsPerSecond?: number           // 码率，默认 128000
  sampleRate?: number                   // 采样率，默认 16000
}
```

### 音频格式

输出：WebM/Opus 格式，前端通过 MediaRecorder 采集。

## useWebSocket

### 重连机制

自动重连：连接断开后最多重试 3 次，间隔 1s/2s/3s。

### 消息队列

连接断开时，发送的消息会进入队列，重连后自动发送。

## 注意事项

- `useAudioRecorder` 在 `stopRecording()` 后需要重新创建
- `getAudioChunk()` 返回 Promise，需 await
- 组件卸载时自动清理资源
