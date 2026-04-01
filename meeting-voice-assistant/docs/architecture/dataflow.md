# 数据流

## 音频数据流

```
前端采集                    后端处理                      ASR 输入
─────────────────────────────────────────────────────────────────────

┌──────────────┐        ┌──────────────┐        ┌──────────────┐
│  MediaRecorder│        │   16kHz 重采样 │        │   音频块     │
│  (浏览器)     │        │   (如果需要)   │        │   合并缓冲   │
└──────┬───────┘        └──────┬───────┘        └──────┬───────┘
       │ (原始音频)              │ (处理后)              │ (缓冲后)
       │ 48kHz/32kHz            │ 16kHz                │ 约 1s
       ▼                        ▼                      ▼
┌──────────────┐        ┌──────────────┐        ┌──────────────┐
│ ArrayBuffer  │   -->  │ ByteString   │   -->  │ ONNX Inference│
│ (WebSocket)  │        │ (WebSocket)  │        │ / API Call   │
└──────────────┘        └──────────────┘        └──────────────┘
```

## 消息数据流

### 1. 实时转写

```
[麦克风] --> [MediaRecorder] --> [WebSocket Client] --> [WebSocket Server]
                                                              │
                                                              ▼
                                                         [ASR Engine]
                                                              │
                                                              ▼
[TranscriptPanel] <-- [JSON Response] <-- [Transcript Result]
```

### 2. 会议信息检测

```
[Transcript Result]
        │
        ▼
[Semantic Parser]
   ├── SpeakerParser  (说话人识别)
   ├── RoleParser     (角色识别)
   ├── ChapterParser  (章节检测)
   └── TopicParser    (主题提取)
        │
        ▼
[MeetingInfo Message] --> [前端 MeetingInfo 组件]
```

## 状态机

### 前端录音状态

```
                    ┌─────────────┐
                    │    IDLE     │  (初始状态)
                    └──────┬──────┘
                           │ startRecording()
                           ▼
                    ┌─────────────┐
           ┌───────>│  RECORDING  │  (录音中)
           │        └──────┬──────┘
           │               │ stopRecording()
           │               ▼
           │        ┌─────────────┐
           │        │   ENDED     │  (录音结束)
           │        └─────────────┘
           │
           │ pauseRecording()
           ▼
    ┌─────────────┐
    │   PAUSED    │ (暂停)
    └──────┬──────┘
           │
           │ resumeRecording()
           └─────── (回到 RECORDING)
```

### WebSocket 会话状态

```
    ┌─────────────┐
    │  CONNECTING │  (正在连接)
    └──────┬──────┘
           │ 连接成功
           ▼
    ┌─────────────┐
    │  CONNECTED  │──────────┐
    └──────┬──────┘          │
           │                 │ 断开/错误
           ▼                 ▼
    ┌─────────────┐    ┌─────────────┐
    │  RECORDING  │    │ DISCONNECTED│
    └──────┬──────┘    └─────────────┘
           │
           ▼
    ┌─────────────┐
    │   ENDED     │
    └─────────────┘
```
