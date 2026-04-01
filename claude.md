# 会议语音助手项目理解

## 项目概述

这是一个基于 Web 的实时语音识别会议助手，采用前后端分离架构。

- **前端**: Vue 3 + TypeScript + Vite
- **后端**: Python FastAPI + WebSocket
- **ASR 引擎**: 阿里云 DashScope (Qwen3-ASR-Flash)
- **LLM**: 阿里云 DashScope (qwen-plus)

## 目录结构

```
meeting-voice-assistant/
├── backend/
│   ├── app/
│   │   ├── api/v1/
│   │   │   ├── ws.py          # WebSocket 语音识别路由
│   │   │   ├── health.py      # 健康检查
│   │   │   ├── upload.py      # 文件上传
│   │   │   └── __init__.py
│   │   ├── core/
│   │   │   ├── asr/           # ASR 适配器
│   │   │   │   ├── base.py    # 基类定义
│   │   │   │   ├── dashscope.py  # DashScope 实现
│   │   │   │   ├── mock.py    # Mock 测试实现
│   │   │   │   └── factory.py # 工厂类
│   │   │   ├── audio_cache.py    # 音频缓存
│   │   │   ├── llm_analyzer.py   # LLM 分析
│   │   │   └── parser/           # 会议信息解析
│   │   ├── models/
│   │   │   └── audio.py      # 数据模型
│   │   ├── config.py         # 配置管理
│   │   ├── main.py           # FastAPI 入口
│   │   └── .env              # 环境变量
│   ├── audio_cache/          # 音频缓存目录
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── AudioRecorder.vue   # 录音控制组件
│   │   │   ├── AudioWaveform.vue    # 波形可视化
│   │   │   ├── ControlBar.vue       # 连接控制栏
│   │   │   ├── FileUploader.vue     # 文件上传
│   │   │   ├── MeetingInfo.vue      # 会议信息
│   │   │   └── TranscriptPanel.vue  # 转写面板
│   │   ├── composables/
│   │   │   ├── useAudioRecorder.ts  # 录音逻辑
│   │   │   └── useWebSocket.ts      # WebSocket 连接
│   │   ├── api/
│   │   │   └── websocket.ts          # WebSocket 客户端
│   │   ├── stores/
│   │   │   └── meeting.ts            # Pinia store
│   │   └── App.vue
│   └── package.json
└── docker-compose.yml
```

## 核心功能流程

### 1. 实时语音识别 (WebSocket)

**流程**:
1. 前端连接 `ws://localhost:8000/api/v1/ws/voice`
2. 后端返回 welcome 消息 (含 session_id)
3. 前端发送 `{"type": "control", "action": "start"}`
4. 前端通过 MediaRecorder 采集音频，每 100ms 发送二进制音频数据
5. 后端 `process_audio()` 累积音频 chunks
6. 后端启动 `run_recognition()` 每 3 秒发送中间结果到前端
7. 前端发送 `{"type": "control", "action": "stop"}`
8. 后端执行 `_process_after_stop()`: 保存音频 → ASR 识别 → LLM 分析
9. 返回最终分析结果

**关键代码路径**:
- `ws.py:VoiceSession` - 核心会话类
- `ws.py:handle_control()` - 处理 start/stop 控制消息
- `ws.py:run_recognition()` - 实时识别循环
- `ws.py:process_audio()` - 音频数据接收

### 2. 音频缓存

- **配置**: `AUDIO_CACHE_ENABLED=true`, `AUDIO_CACHE_DIR` 在 `.env` 中设置
- **实现**: `audio_cache.py:AudioCache` 类
- **保存时机**: `stop` 控制消息后，`_process_after_stop()` 中执行
- **文件格式**: WAV (后端会添加 WAV header)

### 3. 文件上传

- **端点**: `POST /api/v1/upload`
- **支持格式**: mp3, mp4, wav, m4a, ogg, flac, webm
- **流程**: 上传 → 保存临时文件 → ASR 识别 → LLM 分析 → 清理临时文件

### 4. ASR 引擎

**工厂类** (`factory.py`):
- 根据 `ASR_ENGINE` 环境变量创建对应适配器
- 支持: `mock` (测试), `dashscope` (生产)

**DashScope 适配器** (`dashscope.py`):
- 使用 Qwen3-ASR-Flash 模型
- `recognize_stream()` - 流式识别
- `recognize_file()` - 文件识别

## 已修复的 Bug

### 1. WebSocket 文本消息解析错误
- **问题**: FastAPI WebSocket 返回 `data["text"]` 而不是 `data["json"]`
- **修复**: `ws.py` 中检查 `"text" in data` 并使用 `json.loads(data["text"])`

### 2. stop 控制消息丢失
- **问题**: 前端 `stopRecording()` 立即调用 `mediaRecorder.stop()`，导致最后一个音频 chunk 的 `ondataavailable` 永远不会被触发
- **修复**: 使用 `setTimeout(..., 200)` 延迟停止，等待 `ondataavailable` 完成

### 3. 波形图不动
- **问题**: `monitorAudioLevel()` 中过早返回 `if (!isRecording.value) return`
- **修复**: 移除该条件，让动画循环持续运行

### 4. run_recognition() 未启动
- **问题**: `handle_control("start")` 没有启动识别循环
- **修复**: 添加 `asyncio.create_task(self.run_recognition())`

## 配置说明

### 后端 `.env` (`backend/app/.env`)
```
ASR_ENGINE=dashscope              # ASR 引擎
DASHSCOPE_API_KEY=sk-xxx         # API 密钥
AUDIO_CACHE_ENABLED=true          # 是否启用音频缓存
AUDIO_CACHE_DIR=/path/to/cache    # 缓存目录
LLM_PROVIDER=dashscope           # LLM 提供商
LLM_MODEL=qwen-plus              # LLM 模型
```

### 前端
- WebSocket URL: `ws://localhost:8000/api/v1/ws/voice`
- Vite 开发服务器: `http://localhost:5173`

## 运行命令

```bash
# 后端
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000

# 前端
cd frontend
npm run dev
```

## API 端点

| 端点 | 方法 | 描述 |
|------|------|------|
| `/api/v1/ws/voice` | WebSocket | 实时语音识别 |
| `/api/v1/upload` | POST | 文件上传 |
| `/api/v1/health` | GET | 健康检查 |
| `/api/v1/upload/formats` | GET | 支持的文件格式 |

## 技术栈版本

- **Python**: 3.9
- **Node.js**: 24.x
- **FastAPI**: 最新
- **Vue**: 3.x
- **Vite**: 5.x
