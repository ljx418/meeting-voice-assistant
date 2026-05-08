# Voice Service

## 概述

独立的 FunASR 说话人分离服务，通过 HTTP、CLI、MCP stdio 和 WebSocket 对外提供能力。

## 架构

```
主后端 (8000)  --WebSocket-->  FunASR 服务 (8001)
                                   |
                                   v
                            FunASR 模型 (本地)
```

## 启动

```bash
cd ~/Desktop/workspace/voice_service
pip3 install -r requirements.txt
python3 -m funasr_service.cli serve-http --host 0.0.0.0 --port 8001
```

## API 端点

| 端点 | 方法 | 描述 |
|------|------|------|
| `/health` | GET | 健康检查 |
| `/recognize` | POST | 文件识别 |
| `/ws/realtime` | WebSocket | 流式 ASR 识别 |

## CLI

```bash
python3 -m funasr_service.cli health
python3 -m funasr_service.cli recognize /path/to/audio.wav --json
python3 -m funasr_service.cli serve-mcp
```

## WebSocket 消息

### 请求
```json
{"audio": "<base64>", "enable_spks": true}
```

### 响应
```json
{
  "text": "识别文本",
  "spks": [{"id": 0, "name": "spk_0"}],
  "start_time": 0.0,
  "end_time": 3.0
}
```
