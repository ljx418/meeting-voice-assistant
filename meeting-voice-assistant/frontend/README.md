# 会议语音助手 - 前端

## 概述

Vue 3 + TypeScript 前端，提供实时语音识别界面。

## 技术栈

- **框架**: Vue 3 (Composition API)
- **构建**: Vite
- **状态管理**: Pinia
- **样式**: CSS (自定义)

## 核心功能

| 功能 | 组件/模块 |
|------|-----------|
| 录音控制 | `AudioRecorder.vue`, `useAudioRecorder.ts` |
| WebSocket 通信 | `useWebSocket.ts`, `api/websocket.ts` |
| 实时转写 | `TranscriptPanel.vue` |
| 波形显示 | `AudioWaveform.vue` |
| 会议信息 | `MeetingInfo.vue` |
| 摘要展示 | `SummaryPanel.vue` |
| 文件上传 | `FileUploader.vue` |

## 快速开始

```bash
cd frontend
npm install
npm run dev
```

访问 http://localhost:5173

## 目录结构

```
src/
├── api/
│   ├── websocket.ts    # WebSocket 客户端封装
│   └── types.ts        # TypeScript 类型定义
├── components/         # Vue 组件
├── composables/        # 组合式函数
│   ├── useAudioRecorder.ts  # 录音逻辑
│   └── useWebSocket.ts       # WebSocket 连接
├── stores/
│   └── meeting.ts      # Pinia 状态管理
├── App.vue
└── main.ts
```

## 状态管理 (Pinia Store)

`meeting.ts` store 管理以下状态：

```typescript
interface MeetingState {
  status: 'idle' | 'connecting' | 'connected' | 'recording' | 'processing' | 'completed' | 'error'
  sessionId: string | null
  transcripts: TranscriptSegment[]
  summary: MeetingSummary | null
  speakers: Speaker[]
}
```
