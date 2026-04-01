# WebSocket API

## 连接端点

```
ws://host:port/api/v1/ws/voice
```

## 连接流程

```
Client                                    Server
  |                                          |
  |--- WebSocket Connect ------------------>|
  |                                          |
  |<-- Welcome {session_id, config} --------|  (欢迎消息)
  |                                          |
  |--- Control {action: "start"} ---------->|
  |                                          |
  |--- Binary Audio Frame (PCM 16kHz) ----->|  (实时传输)
  |--- Binary Audio Frame ---------------->|
  |--- Binary Audio Frame ---------------->|
  |                                          |
  |<-- Transcript {transcript} -------------|  (实时返回)
  |<-- Transcript {transcript} ------------|
  |                                          |
  |--- Control {action: "stop"} ----------->|
  |                                          |
  |<-- MeetingInfo {meeting_info} ---------|  (会议总结)
  |                                          |
  |--- WebSocket Close -------------------->|
```

## 消息格式

### 1. 欢迎消息 (Server -> Client)

```json
{
  "type": "welcome",
  "session_id": "sess_abc123",
  "config": {
    "sample_rate": 16000,
    "channels": 1
  }
}
```

### 2. 控制消息 (Client -> Server)

```json
{
  "type": "control",
  "action": "start",
  "metadata": {
    "meeting_id": "meeting_001",
    "topic": "Q1项目评审",
    "participants": ["张三", "李四"]
  }
}
```

**action 可选值:**
- `start`: 开始识别
- `stop`: 停止识别
- `pause`: 暂停识别
- `resume`: 恢复识别

### 3. 识别结果 (Server -> Client)

```json
{
  "type": "transcript",
  "seq": 1,
  "data": {
    "text": "今天我们来讨论项目进度",
    "start_time": 0.0,
    "end_time": 2.5,
    "speaker": "speaker_001",
    "confidence": 0.95,
    "is_final": true
  }
}
```

### 4. 会议信息 (Server -> Client)

```json
{
  "type": "meeting_info",
  "data": {
    "detected_topic": "Q1项目进度评审",
    "detected_roles": {
      "speaker_001": "host",
      "speaker_002": "participant"
    },
    "chapter": {
      "id": "chapter_001",
      "title": "项目进展汇报"
    }
  }
}
```

### 5. 错误消息 (Server -> Client)

```json
{
  "type": "error",
  "code": "ASR_ERROR",
  "message": "ASR service unavailable"
}
```

## 音频格式

| 参数 | 值 |
|------|-----|
| 采样率 | 16000 Hz |
| 位深 | 16-bit |
| 声道 | 单声道 (mono) |
| 编码 | linear PCM |

## 错误码

| 错误码 | 说明 |
|--------|------|
| `WS_ERROR` | WebSocket 连接错误 |
| `ASR_ERROR` | ASR 服务错误 |
| `RECOGNITION_ERROR` | 识别过程错误 |
| `INVALID_FORMAT` | 音频格式错误 |
