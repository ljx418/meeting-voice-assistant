# 任务列表

## audio_analyzer 模块 (已完成)

**目标**: 基于音频转文本信息调用 LLM 进行识别，使用 langchain、langgraph 进行任务编排

**状态**: ✅ 已完成

**目录结构**:
```
app/core/audio_analyzer/
├── __init__.py      # 包导出
├── config.py        # LLM 配置（MiniMax/DeepSeek + dotenv）
├── prompt.py       # 分析提示词模板
├── state.py        # LangGraph 状态定义
├── graph.py        # LangGraph 工作流 + LLM 缓存
├── llm_client.py   # LLM 客户端（自动切换）
└── analyzer.py     # 主分析器类
```

## 前端文本分析功能 (已完成)

**功能**:
- SummaryPanel 新增文本输入区域，支持拖拽/粘贴文本
- 调用 `/api/v1/analyze` 接口进行深度分析
- 展示：会议主题、章节划分、发言人员角色、摘要、关键要点、行动项

**API 接口**:

### POST /api/v1/analyze
分析文本内容，返回结构化结果。

**请求**:
```json
{
  "text": "会议转写文本内容...",
  "session_id": "可选的会话 ID"
}
```

**响应**:
```json
{
  "success": true,
  "theme": "会议主题（一句话概括）",
  "summary": "会议摘要",
  "chapters": [{"章节名称": "...", "起始位置": "...", "结束位置": "..."}],
  "speaker_roles": [{"speaker": "SPEAKER_00", "role": "角色", "reasoning": "判断依据"}],
  "topics": ["主题标签"],
  "key_points": ["关键点"],
  "action_items": ["行动项"]
}
```

**LLM 缓存**:
- 位置: `backend/llm_cache/{session_id}/`
- 文件: `llm_request.txt` (请求)、`llm_response.json` (响应)、`meta.json` (元数据)

## 工作流程

1. **语音识别 (ASR)**: 用户上传音频 → FunASR 识别 → 转写结果展示在 FileUploader
2. **深度分析 (LLM)**: 用户复制/拖拽转写文本到 SummaryPanel → 点击"开始分析" → 调用 LLM → 展示主题/章节/角色等

## 待验证

- [ ] 拖拽/粘贴文本到 SummaryPanel 进行分析
- [ ] 验证分析结果正确显示（主题、章节、角色等）
