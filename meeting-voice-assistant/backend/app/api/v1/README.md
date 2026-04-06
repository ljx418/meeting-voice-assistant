# API 路由文档

## 概述

提供 RESTful 和 WebSocket 接口，用于前端通信。

## 端点列表

| 端点 | 方法 | 描述 |
|------|------|------|
| `/api/v1/ws/voice` | WebSocket | 实时语音识别 |
| `/api/v1/upload` | POST | 文件上传识别 |
| `/api/v1/upload/formats` | GET | 支持的文件格式 |
| `/api/v1/health` | GET | 服务健康检查 |
| `/api/v1/health/detailed` | GET | 详细健康状态 |

## WebSocket 消息协议

### 连接建立

```
Client -> Server: WebSocket 连接
Server -> Client: {"type": "welcome", "session_id": "xxx", "config": {...}}
```

### 控制消息

```json
// 开始录音
{"type": "control", "action": "start"}

// 停止录音
{"type": "control", "action": "stop"}

// 获取状态
{"type": "status"}
```

### 音频消息

```json
// 发送二进制音频数据 (PCM 16kHz mono)
{"type": "audio", "data": "<base64>"}

// 或直接发送二进制帧
```

### 识别结果

```json
// 中间结果
{"type": "transcript", "data": {"text": "...", "start_time": 0.0, "end_time": 3.0}}

// 最终结果
{"type": "final", "data": {"text": "...", "segments": [...]}}

// 会议摘要
{"type": "summary", "data": {"summary": "...", "key_points": [...], "action_items": [...]}}

// 错误
{"type": "error", "message": "..."}
```

## 文件上传

**请求**: `POST /api/v1/upload`
**Content-Type**: `multipart/form-data`
**表单字段**:
- `file`: 音频文件 (最大 512MB)
- `engine`: 可选，指定 ASR 引擎

**响应**:
```json
{
  "session_id": "xxx",
  "status": "processing"
}
```

轮询或使用 WebSocket 获取结果。

## 健康检查

**响应**:
```json
{
  "status": "healthy",
  "timestamp": "2026-04-06T10:00:00Z",
  "version": "1.0.0"
}
```
