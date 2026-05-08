# Backend Guide

本后端只承载会议语音助手能力：上传、实时转写、说话人处理、LLM 会议分析、会话状态和前端 API。

## 知识服务边界

知识治理能力已迁移到独立 `data_service` 仓库：

- workspace / source lifecycle
- LLMWiki
- GraphRAG
- Source Trace
- Quality Governance
- MCP / CLI / HTTP contract

本后端保留 `/api/v1/knowledge/*` 代理路由，用于把控制台请求转发到外部 Local Knowledge Governance Service。不要在本仓库恢复已迁出的内嵌知识服务实现。

## 常用命令

```bash
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000
python3 -c "import app.main; import app.api.v1.data_service; print('meeting backend imports ok')"
```

## 配置

知识服务相关配置使用 `KNOWLEDGE_SERVICE_` 前缀，默认 HTTP 地址为 `http://localhost:8003/api/v1/knowledge`。会议后端不应该直接使用旧内嵌图谱配置或访问旧图谱服务端口。
