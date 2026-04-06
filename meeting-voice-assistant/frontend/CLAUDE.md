# AI 代理指令 - 前端

## 模块职责

前端负责：
1. 录音采集 (MediaRecorder API)
2. WebSocket 实时通信
3. 识别结果实时展示
4. 状态管理 (Pinia)

## 关键文件

| 文件 | 用途 |
|------|------|
| `composables/useAudioRecorder.ts` | 录音控制核心 |
| `composables/useWebSocket.ts` | WebSocket 连接管理 |
| `stores/meeting.ts` | 全局状态 |
| `api/websocket.ts` | WebSocket 客户端封装 |
| `api/types.ts` | 类型定义 |

## 组件关系

```
App.vue
├── ControlBar.vue           # 连接/录音控制
├── AudioRecorder.vue        # 录音按钮
│   └── AudioWaveform.vue    # 波形显示
├── TranscriptPanel.vue       # 转写结果
├── MeetingInfo.vue          # 会议信息
├── SummaryPanel.vue          # 摘要结果
└── FileUploader.vue          # 文件上传
```

## WebSocket 消息流

```typescript
// 连接
const ws = useWebSocket()
await ws.connect()

// 发送控制
ws.send({ type: 'control', action: 'start' })

// 发送音频 (每 100ms)
ws.sendAudio(audioChunk)

// 接收结果
ws.onMessage((msg) => {
  if (msg.type === 'transcript') {
    store.addTranscript(msg.data)
  }
})
```

## 代码规范

- 使用 `<script setup lang="ts">` 语法
- 组件文件名使用 PascalCase
- Composables 使用 use 前缀
- 类型定义放在 `api/types.ts`
