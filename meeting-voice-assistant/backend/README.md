# 会议语音助手 - 后端

## 概述

FastAPI 后端服务，提供实时语音识别、文件上传、会议分析功能。

## 技术栈

- **框架**: FastAPI + uvicorn
- **ASR 引擎**: DashScope (云) / FunASR (本地)
- **LLM**: 阿里云 DashScope (qwen-plus)
- **WebSocket**: 实时双向通信

## 核心模块

| 模块 | 路径 | 说明 |
|------|------|------|
| API 路由 | `app/api/v1/` | WebSocket、文件上传、健康检查 |
| ASR 适配器 | `app/core/asr/` | 多引擎统一接口 |
| 音频分析 | `app/core/audio_analyzer/` | 波形分析、LLM 分析 |
| 说话人识别 | `app/core/realtime_spk/` | 实时说话人分离 |
| 音频缓存 | `app/core/audio_cache.py` | 录音文件存储 |
| LLM 分析 | `app/core/llm_analyzer.py` | 会议摘要生成 |
| 会议解析 | `app/core/parser/` | 语义解析 |

## 快速开始

```bash
cd backend
pip3 install -r requirements.txt

# 配置环境变量
cp app/.env.example app/.env
# 编辑 app/.env 填入 API 密钥

# 启动服务
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## API 文档

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 目录结构

```
app/
├── api/v1/           # API 路由
├── core/             # 核心业务逻辑
│   ├── asr/         # ASR 适配器
│   ├── audio_analyzer/
│   ├── realtime_spk/
│   └── parser/
├── models/           # Pydantic 模型
├── utils/            # 工具函数
├── config.py         # 配置管理
└── main.py          # 应用入口
```

## 环境变量

| 变量 | 说明 | 必需 |
|------|------|------|
| `DASHSCOPE_API_KEY` | 阿里云 API 密钥 | 是 |
| `ASR_ENGINE` | ASR 引擎: `dashscope` / `funasr` | 是 |
| `FUNASR_ENDPOINT` | FunASR 服务地址 | 否 |
| `LLM_PROVIDER` | LLM 提供商 | 否 |
| `LLM_MODEL` | LLM 模型 | 否 |
