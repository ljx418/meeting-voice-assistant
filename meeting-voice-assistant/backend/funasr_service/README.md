# FunASR 服务

## 概述

独立的 FunASR 说话人分离服务，提供 WebSocket 接口。

## 架构

```
主后端 (8000)  --WebSocket-->  FunASR 服务 (8001)
                                   |
                                   v
                            FunASR 模型 (本地)
```

## 启动

```bash
cd backend/funasr_service
pip3 install -r requirements.txt
python3 -m uvicorn main:app --host 0.0.0.0 --port 8001
```

## API 端点

| 端点 | 方法 | 描述 |
|------|------|------|
| `/asr` | WebSocket | 流式 ASR 识别 |
| `/health` | GET | 健康检查 |

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
