# 会议语音助手

实时语音识别会议助手，支持语音转文本、说话人分离识别、会议摘要分析。

## 功能特性

- **实时语音识别** - WebSocket 实时转写，延迟 ~2-3 秒
- **文件上传识别** - 支持最大 512MB 音频文件
- **说话人分离** - 识别不同发言人（FunASR 本地模型）
- **会议摘要** - LLM 自动生成摘要、关键点、行动项

## 技术栈

| 模块 | 技术 |
|------|------|
| 前端 | Vue 3 + TypeScript + Vite + Pinia |
| 后端 | Python FastAPI + WebSocket |
| ASR | DashScope (云) / FunASR (本地说话人分离) |
| LLM | 阿里云 DashScope (qwen-plus) |

## 快速开始

### 1. 安装依赖

```bash
# 前端
cd frontend && npm install

# 后端
cd backend && pip3 install -r requirements.txt

# FunASR 服务 (可选，用于说话人分离)
cd backend/funasr_service && pip3 install -r requirements.txt
```

### 2. 配置环境变量

编辑 `backend/app/.env`:

```env
# API 密钥
DASHSCOPE_API_KEY=your_api_key

# ASR 引擎: dashscope_file (云) / funasr (本地说话人分离)
ASR_ENGINE=funasr

# FunASR 服务地址 (使用 funasr 引擎时)
FUNASR_ENDPOINT=http://localhost:8001
```

### 3. 启动服务

```bash
# 启动 FunASR 服务 (说话人分离)
cd backend
python3 -m uvicorn funasr_service.main:app --host 0.0.0.0 --port 8001

# 新开终端 - 启动后端
cd backend
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# 新开终端 - 启动前端
cd frontend && npm run dev
```

### 4. 访问

- 前端: http://localhost:5173
- 后端 API: http://localhost:8000
- FunASR 服务: http://localhost:8001

## 项目结构

```
meeting-voice-assistant/
├── frontend/                    # Vue 3 前端
│   ├── src/
│   │   ├── components/          # Vue 组件
│   │   ├── composables/         # 组合式函数
│   │   ├── stores/              # Pinia 状态管理
│   │   └── api/                 # API 接口
│   └── package.json
│
├── backend/                     # FastAPI 后端
│   ├── app/
│   │   ├── api/v1/             # API 路由
│   │   │   ├── ws.py           # WebSocket 实时识别
│   │   │   ├── upload.py       # 文件上传
│   │   │   └── health.py       # 健康检查
│   │   ├── core/
│   │   │   ├── asr/            # ASR 适配器
│   │   │   ├── audio_cache.py  # 音频缓存
│   │   │   └── llm_analyzer.py # LLM 分析
│   │   ├── config.py           # 配置管理
│   │   └── main.py             # 应用入口
│   ├── funasr_service/         # FunASR 说话人分离服务
│   │   ├── main.py             # 服务入口
│   │   ├── api.py              # API 路由
│   │   └── model_loader.py     # 模型加载
│   ├── audio_cache/             # 音频缓存
│   ├── transcripts/             # 转写文本
│   └── requirements.txt
│
├── docs/                        # 技术文档
└── scripts/                     # 辅助脚本
```

## 使用指南

### 实时语音识别

1. 打开前端页面，点击"开始录音"
2. 说话，实时看到识别结果
3. 点击"停止"，获取会议摘要

### 文件上传识别

1. 前端点击"上传文件"
2. 选择音频/视频文件（最大 512MB）
3. 等待识别完成，查看转写结果和摘要

### 切换 ASR 引擎

编辑 `backend/app/.env`:

```env
# 使用云端 DashScope (不支持说话人分离)
ASR_ENGINE=dashscope_file

# 使用本地 FunASR (支持说话人分离)
ASR_ENGINE=funasr
```

## API 接口

| 接口 | 方法 | 描述 |
|------|------|------|
| `/api/v1/ws/voice` | WebSocket | 实时语音识别 |
| `/api/v1/upload` | POST | 文件上传识别 |
| `/api/v1/health` | GET | 健康检查 |

## 常见问题

**Q: FunASR 说话人分离需要 GPU 吗？**
A: 不需要，但 CPU 推理较慢（约 0.5x 实时速度）。

**Q: 如何区分不同发言人？**
A: 使用 `ASR_ENGINE=funasr`，FunASR 会自动识别并标注 "发言人 A", "发言人 B" 等。

**Q: 支持哪些音频格式？**
A: mp3, mp4, wav, m4a, ogg, flac, webm。

## License

MIT
