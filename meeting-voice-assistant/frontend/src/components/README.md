# 组件文档

## 组件列表

| 组件 | 文件 | 描述 |
|------|------|------|
| AudioRecorder | `AudioRecorder.vue` | 录音按钮 + 状态显示 |
| AudioWaveform | `AudioWaveform.vue` | 音频波形可视化 |
| ControlBar | `ControlBar.vue` | 连接控制栏 |
| FileUploader | `FileUploader.vue` | 文件上传组件 |
| MeetingInfo | `MeetingInfo.vue` | 会议信息展示 |
| SummaryPanel | `SummaryPanel.vue` | 摘要展示面板 |
| TranscriptPanel | `TranscriptPanel.vue` | 转写结果面板 |

## 组件关系

```
ControlBar
├── AudioRecorder
│   └── AudioWaveform
├── FileUploader
└── MeetingInfo

TranscriptPanel
SummaryPanel
```

## AudioRecorder

录音按钮组件，显示录音状态和音频级别。

**Props:**
```typescript
interface Props {
  isRecording: boolean
  audioLevel: number  // 0-1
}
```

**Events:**
```typescript
interface Emits {
  (e: 'start'): void
  (e: 'stop'): void
}
```

## TranscriptPanel

实时显示转写结果，支持多段落展示。

**Props:**
```typescript
interface Props {
  segments: TranscriptSegment[]
}
```

## SummaryPanel

显示会议摘要、关键点、行动项。

**Props:**
```typescript
interface Props {
  summary: MeetingSummary | null
}
```

## FileUploader

文件上传组件，支持拖拽。

**Props:**
```typescript
interface Props {
  uploading: boolean
  progress: number  // 0-100
}
```

**Events:**
```typescript
interface Emits {
  (e: 'upload', file: File): void
}
```
