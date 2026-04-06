# 状态管理文档

## 概述

使用 Pinia 管理全局状态。

## Store: meeting

### State

```typescript
interface MeetingState {
  status: SessionStatus
  sessionId: string | null
  transcripts: TranscriptSegment[]
  summary: MeetingSummary | null
  speakers: Speaker[]
  error: string | null
}

type SessionStatus =
  | 'idle'
  | 'connecting'
  | 'connected'
  | 'recording'
  | 'processing'
  | 'completed'
  | 'error'
```

### Actions

```typescript
// 连接 WebSocket
async function connect(): Promise<void>

// 断开连接
function disconnect(): void

// 开始录音
async function startRecording(): Promise<void>

// 停止录音
async function stopRecording(): Promise<void>

// 添加转写段落
function addTranscript(segment: TranscriptSegment): void

// 设置摘要
function setSummary(summary: MeetingSummary): void

// 清空状态
function reset(): void
```

### Getters

```typescript
// 是否可以开始录音
const canStartRecording: boolean

// 转写文本（合并所有段落）
const fullText: string

// 错误信息
const errorMessage: string | null
```
