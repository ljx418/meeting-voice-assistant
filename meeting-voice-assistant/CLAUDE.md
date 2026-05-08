# CLAUDE.md

会议语音助手项目 - Claude Code 工作指南

## 项目概述

本仓库是会议语音助手应用，负责会议音频采集、ASR 转写、说话人信息、会议摘要和会议分析 UI。

知识固化、GraphRAG、LLMWiki、Source Trace、质量治理和跨应用检索不在本仓库内实现。这些能力由独立的 Local Knowledge Governance Service 提供，当前迁移目标仓库为 `~/Desktop/workspace/data_service`。

## 硬边界

- 不 import `data_service` 内部 Python 模块。
- 不直接读写 `data_service` workspace 内部文件结构。
- 不恢复已迁出的内嵌知识服务代码或旧知识消费页面。
- 会议场景只向知识服务交付转写后的文本、会议分析结果或结构化 source payload。
- 对知识服务的调用只能通过 MCP、CLI 或 HTTP contract。

## 技术栈

- 前端: Vue 3 + TypeScript + Vite + Pinia + Vue Router
- 后端: Python FastAPI + WebSocket + SQLAlchemy
- ASR 引擎: 阿里云 DashScope / FunASR
- LLM: 阿里云 DashScope
- 外部知识服务: Local Knowledge Governance Service (`~/Desktop/workspace/data_service`)

## 服务架构

```text
Frontend (:5173)
  -> Meeting Backend (:8000)
      -> ASR / speaker / LLM meeting analysis
      -> Knowledge proxy endpoints under /api/v1/knowledge
          -> external data_service (:8003 by default)
```

FunASR 作为独立语音服务运行在 `~/Desktop/workspace/voice_service`，默认 HTTP 端口 `8001`。

## 常用命令

```bash
# 后端
cd backend
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# 前端
cd frontend
npm run dev

# 外部知识服务
cd ~/Desktop/workspace/data_service
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8003
```

## 页面边界

- `/`、`/meeting`、`/console`：会议应用页面。
- `/knowledge`：Knowledge Service Console，显示外部 data_service 的 workspace、sources、build、GraphRAG、trace 和 quality 状态。
- 旧独立知识消费页面已移除。
