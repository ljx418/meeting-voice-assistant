# LLMWiki 模块评估报告

## 1. 评估背景

基于 `docs/llmwiki_claude_code_plan.md` 开发计划，对当前项目 LLMWiki 实现进行差距评估。

---

## 2. 当前代码位置

当前代码**散布在多处，非独立模块**：

| 位置 | 职责 |
|------|------|
| `backend/app/core/wiki/` | 核心服务 (service.py, file_indexer.py, enhanced_search.py) |
| `backend/app/storage/wiki_db.py` | 存储层 SQLite CRUD |
| `backend/app/api/v1/wiki/` | API 路由 (pages, categories, tags, generate, search, workflow) |
| `backend/app/models/wiki.py` | Pydantic 模型 |
| `frontend/src/api/wiki.ts` | 前端 API 客户端 |
| `frontend/src/composables/useLLMWiki.ts` | 前端状态管理 |

**注意**: `llmwiki/` 独立模块**不存在**。现有代码是 `backend/app` 的一部分。

---

## 3. 当前已实现功能

### 已完成
- Wiki 页面 CRUD（分类、标签、版本控制）
- 简单搜索（LIKE 模式，非 FTS5）
- 会议转写 → Wiki 页面生成（LLM 驱动）
- GraphRAG 实体/关系提取与索引
- 文件信息提取（正则模式，只支持 .txt/.md/.json/.jsonl/.csv/.yaml/.xml/.eml/.msg）
- 增强搜索（结合 GraphRAG 语义搜索）
- 知识关联分析（基于关键词共现）

### 技术限制
- 使用 SQLite（`wiki.db`）但无 FTS5 全文索引
- 无 n-gram 中文检索
- 无独立抽取器框架

---

## 4. 与开发计划差距

| 要求 | 状态 | 说明 |
|------|------|------|
| 独立模块 `llmwiki/` | ❌ | 嵌入在 `backend/app` 中 |
| 4 个核心动作 (ingest/search/read_page/rebuild) | ❌ | 只有 API 端点，无 engine.py |
| 多格式支持 (md/txt/html/csv/json/pdf/pptx/chat json) | ❌ | 仅有正则提取，无标准化 extractors/ |
| SQLite + FTS5 | ❌ | 用 LIKE 非 FTS5 |
| 中文检索 (n-gram) | ❌ | 无 cjk.py 模块 |
| wiki 页面生成 (source_note/topic/conversation_note/index) | ⚠️ | 仅有 meeting 生成，无 compiler/ |
| MCP stdio server | ❌ | 无 mcp_stdio.py |
| CLI 工具 | ❌ | 无 cli.py |

---

## 5. MCP 支持现状

**完全不支持**。项目中未发现任何 MCP 相关代码。

---

## 6. 独立拆分可行性

**低可行性**，原因：

1. **强耦合**：依赖 `app.config`、`app.storage.wiki_db`、`app.models.wiki`、GraphRAG HTTP API
2. **目录结构不匹配**：计划要求 `llmwiki/`、`vault/`、`tests/`、`samples/` 分离，现有代码扁平分布
3. **缺失核心模块**：无 `engine.py`、`extractors/`、`compiler/`、`search/fts.py`、`config.py`

---

## 7. 实现进度评估

| 维度 | 评估 |
|------|------|
| 实现进度 | ~15%（仅有基础 CRUD + 简单搜索） |
| 架构符合度 | 低（散布各处，非独立模块） |
| 核心 API | 缺失（无 engine.py） |
| 抽取器 | 缺失（无 extractors/） |
| 编译器 | 缺失（无 compiler/） |
| 搜索 | 弱（无 FTS5+n-gram） |
| wiki 生成 | 部分（仅 meeting 来源） |
| MCP | 未实现 |
| CLI | 未实现 |

---

## 8. 建议行动

按 Phase 顺序实现：

1. **Phase 0**：创建 `llmwiki/` 目录骨架、pyproject.toml、models.py、config.py
2. **Phase 1**：实现存储层（SQLite + FTS5 + schema）
3. **Phase 2**：实现抽取器（markdown, text, html, csv, json, pdf_pypdf, pptx_zip）
4. **Phase 3**：标准化与分段（normalize.py + passage splitter + cjk n-gram）
5. **Phase 4**：编译器（classifier, page_builder, merger, linker 生成四类页面）
6. **Phase 5**：搜索层（fts.py + ranker.py + cjk.py）
7. **Phase 6**：核心引擎 + CLI（engine.py + cli.py）
8. **Phase 7**：MCP server（mcp_stdio.py）

现有 `backend/app/core/wiki/` 代码可提取部分工具方法（如 slug 生成），但整体需重构。

---

## 9. 参考文档

- 开发计划：`docs/llmwiki_claude_code_plan.md`
- 当前架构：`backend/app/core/wiki/`
- 现有存储：`backend/app/storage/wiki_db.py`