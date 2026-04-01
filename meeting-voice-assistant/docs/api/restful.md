# RESTful API

## 健康检查

### GET /api/v1/health

检查服务健康状态

**响应**

```json
{
  "status": "healthy",
  "asr_engine": "SenseVoice",
  "asr_mode": "local",
  "uptime": 3600.0
}
```

## 获取会话历史

### GET /api/v1/meeting/{meeting_id}/transcripts

获取会议转写记录

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| meeting_id | string | 会议 ID |

**查询参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| start_time | float | 过滤起始时间 |
| end_time | float | 过滤结束时间 |
| speaker | string | 过滤说话人 |

**响应**

```json
{
  "meeting_id": "meeting_001",
  "transcripts": [
    {
      "id": "seg_001",
      "text": "今天我们讨论项目进度",
      "start_time": 0.0,
      "end_time": 2.5,
      "speaker": "speaker_001"
    }
  ]
}
```

## 导出会议记录

### GET /api/v1/meeting/{meeting_id}/export

导出会议记录

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| meeting_id | string | 会议 ID |

**查询参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| format | string | 导出格式: json/txt/srt |

**响应**

- JSON/TXT: 返回文件内容
- SRT: 返回字幕文件 (带时间戳)
