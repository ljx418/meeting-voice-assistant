# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

这是一个基于 Web 的实时语音识别会议助手，采用前后端分离架构。

- **前端**: Vue 3 + TypeScript + Vite
- **后端**: Python FastAPI + WebSocket
- **ASR 引擎**: 阿里云 DashScope / FunASR (本地说话人分离)
- **LLM**: 阿里云 DashScope (qwen-plus)

## 技术路线

### ASR 引擎

| 引擎 | 模型 | 接口 | 文件大小限制 | 说话人分离 | 延迟 |
|------|------|------|-------------|-----------|------|
| `dashscope_file` | qwen3-asr-flash | HTTP | 512MB | ❌ | 取决于文件大小 |
| `dashscope_realtime` | qwen3-asr-flash-realtime | WebSocket | 无限制 | ❌ | ~2秒 |
| `funasr` | Paraformer + CAM++ | HTTP | 无限制 | ✅ | CPU 较慢 |

**推荐**: 需要说话人分离时使用 `funasr`，否则使用 `dashscope_file`。

### LLM 分析

- 模型: `qwen-plus` (DashScope)
- 用途: 会议摘要、关键点提取、行动项识别、主题分类

## 运行命令

```bash
# 后端 (主服务)
cd backend
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# FunASR 服务 (说话人分离，需要单独启动)
cd backend
python3 -m uvicorn funasr_service.main:app --host 0.0.0.0 --port 8001

# 前端
cd frontend
npm run dev
```

## 目录结构

```
backend/
├── app/
│   ├── api/v1/
│   │   ├── ws.py              # WebSocket 语音识别
│   │   ├── upload.py          # 文件上传
│   │   └── health.py          # 健康检查
│   ├── core/
│   │   ├── asr/               # ASR 适配器
│   │   │   ├── base.py        # 基类定义 (ASRAdapterBase, ASRResult)
│   │   │   ├── factory.py     # 工厂类 (ASRFactory)
│   │   │   ├── dashscope.py   # DashScope 文件识别 (6MB)
│   │   │   ├── dashscope_file.py  # DashScope 大文件识别 (512MB)
│   │   │   ├── realtime.py    # DashScope 实时识别
│   │   │   ├── funasr_adapter.py  # FunASR 本地说话人分离
│   │   │   └── mock.py        # Mock 测试
│   │   ├── audio_cache.py     # 音频缓存
│   │   ├── llm_analyzer.py    # LLM 分析
│   │   └── parser/             # 会议信息解析
│   ├── config.py              # 配置管理
│   └── main.py                # FastAPI 入口
├── funasr_service/            # FunASR 说话人分离微服务
│   ├── main.py                # FastAPI 入口
│   ├── api.py                 # API 路由
│   ├── model_loader.py         # 模型加载
│   └── config.py              # 服务配置
├── audio_cache/               # 音频缓存目录
├── transcripts/               # 转写文本保存目录
└── requirements.txt
```

## 配置说明

### 环境变量 (.env) - `backend/app/.env`

```env
# ASR 引擎: mock, dashscope, dashscope_file, dashscope_realtime, funasr
ASR_ENGINE=funasr

# FunASR 配置 (当 ASR_ENGINE=funasr 时使用)
FUNASR_ENDPOINT=http://localhost:8001

# DashScope 配置 (当使用 DashScope 引擎时使用)
DASHSCOPE_API_KEY=sk-xxx

# LLM 配置
LLM_PROVIDER=dashscope
LLM_API_KEY=sk-xxx
LLM_MODEL=qwen-plus

# 音频配置
AUDIO_CACHE_ENABLED=true
AUDIO_CACHE_DIR=./audio_cache
```

## 核心架构

### ASR 适配器模式

所有 ASR 引擎实现统一的 `ASRAdapterBase` 接口：

```python
class ASRAdapterBase:
    async def initialize() -> None
    async def close() -> None
    async def recognize_stream(...) -> AsyncGenerator[ASRResult, None]
    async def recognize_file(file_path: Path) -> AsyncGenerator[ASRResult, None]
```

使用 `ASRFactory.create("engine_name")` 创建适配器实例。

### ASRResult 数据结构

```python
@dataclass
class ASRResult:
    text: str           # 识别文本
    start_time: float   # 开始时间 (秒)
    end_time: float     # 结束时间 (秒)
    speaker: str         # 说话人 ID ("speaker_0", "speaker_1")
    confidence: float   # 置信度
    is_final: bool      # 是否最终结果
```

## API 端点

| 端点 | 方法 | 描述 |
|------|------|------|
| `/api/v1/ws/voice` | WebSocket | 实时语音识别 |
| `/api/v1/upload` | POST | 文件上传 (最大512MB) |
| `/api/v1/health` | GET | 健康检查 |

## FunASR 服务

FunASR 提供本地说话人分离功能，需要独立部署：

```bash
# 启动 FunASR 服务
cd backend
python3 -m uvicorn funasr_service.main:app --host 0.0.0.0 --port 8001

# 测试
curl http://localhost:8001/health
```

**注意**: 首次运行会自动下载模型（约 1GB），需要网络连接。

## WebSocket 消息格式

### 客户端 → 服务端

```json
{"type": "control", "action": "start"}
{"type": "control", "action": "stop"}
```

音频数据: 二进制 (PCM 16kHz 16-bit mono)

### 服务端 → 客户端

```json
{
  "type": "transcript",
  "data": {
    "text": "识别文本",
    "start_time": 0.0,
    "end_time": 2.5,
    "speaker": "speaker_1",
    "confidence": 0.95
  }
}
```
