# Local Knowledge Governance Service 验收计划

更新时间：2026-05-08

## 验收目标

确认本仓库已经被重新收敛为独立的 MCP-first 本地知识治理服务，并且现有 data_service / LLMWiki / GraphRAG / quality 能力在新定位下保持可用。

本轮重点不是大规模重构，而是：

- README 明确新项目目标。
- 当前文档不再把项目主要定义为会议应用中的个人知识库产品线。
- MCP / CLI / HTTP 被定义为稳定外部边界。
- `/knowledge` 被定义为服务治理控制台。
- 文档明确本服务不端到端实现会议、学习、面试、代码助手。
- 文档明确 workspace / tenant 以本地文件夹为 root，但外部稳定 ID 是 `workspace_id`。
- 文档明确本项目是最小可分粒度，可以单独拆包和迁移。

## 必跑自动化验收

从项目根目录运行：

```bash
python3 -m pytest backend/tests/test_data_service.py backend/tests/test_data_service_api.py backend/tests/test_data_service_mcp.py -q
```

通过标准：

- 测试全部通过。
- 允许出现既有环境 warning。
- 不允许出现 data_service API、MCP lifecycle、distill、GraphRAG bridge 相关失败。

## 文档验收

检查旧定位是否已从当前主文档移除。执行时搜索旧的会议应用从属定位、旧的终端用户产品定位和旧的 Phase 5.7 名称：

```bash
rg "旧会议应用从属定位|旧终端用户产品定位|旧 Phase 5.7 UI 名称" README.md backend/README.md docs/V1.x/data_service backend/data_service/KNOWLEDGE-PROJECT-OVERVIEW.md
```

通过标准：

- 当前主文档不得再把项目定义为会议应用里的终端用户知识库产品。
- `Phase 5.7` 应为 `Knowledge Service Console Productization`。
- 如历史报告仍出现旧语义，应位于历史上下文，不作为当前目标。

检查新定位：

```bash
rg "MCP-first|Knowledge Governance Service|服务治理控制台|workspace_id|root_path|最小可分" README.md backend/README.md docs/V1.x/data_service backend/data_service/KNOWLEDGE-PROJECT-OVERVIEW.md
```

通过标准：

- 能命中项目目标、边界、workspace 模型和外部 contract。

## 外部边界验收

当前稳定边界：

- MCP: `python -m data_service.mcp_stdio`
- CLI: `python -m data_service`
- HTTP: `/api/v1/knowledge/*`

通过标准：

- 文档明确这些是当前兼容入口。
- 文档明确未来目标语义以 workspace-scoped MCP / CLI / HTTP 对齐。
- 文档明确外部应用不得直接读写 `workspace/distill`、`workspace/llmwiki`、`workspace/graphrag`、`workspace/quality`。

## Workspace / Tenant 验收

通过标准：

- 文档声明 `Workspace = Tenant = 受控本地知识空间`。
- 外部稳定 ID 是 `workspace_id`。
- `root_path` 是绑定目录和控制台展示字段。
- workspace 内部布局可以演进，不是稳定 API。

## 场景边界验收

会议场景：

- 只接收已经转写后的文本、文档块或结构化会议产物。
- 不包含录音、ASR、说话人分离、实时字幕和会议 UI。

代码理解场景：

- 可以接收 README、file tree、symbols、imports、call graph、class graph、API routes、dependency graph 等分析产物。
- 不承担完整 IDE、代码托管平台或大型静态分析器职责。

## 真实知识库端到端验收

从 `backend/` 目录运行：

```bash
python3 -m data_service ingest \
  --workspace /tmp/data-service-acceptance \
  /Users/Zhuanz/Desktop/workspace/知识库/row/deepseek_split
```

通过标准：

- 能稳定读取真实 source。
- `llmwiki: success`。
- `graphrag: indexed` 或等价完成态。
- `summary / distill / llmwiki / graphrag / quality` 产物完整生成。
- 图谱规模不出现明显倒退或异常膨胀。

## MCP 回归验收

当前已通过外部 HarnessOS 真实 stdio MCP 验收的链路仍作为回归基线：

```text
knowledge_workspace_create
-> knowledge_source_import
-> knowledge_build_start
-> knowledge_build_status
-> knowledge_query_v2
-> knowledge_quality_feedback_v2
-> knowledge_correction_rules_v2
-> knowledge_review_correction_rule_v2
-> knowledge_correction_plan_v2
-> knowledge_workspace_archive
```

通过标准：

- lifecycle/v2 tools 返回统一 envelope。
- 业务可预期失败返回 `blocked` envelope。
- 同一 workspace build 不并发写产物。
- archived workspace 写操作返回 `blocked`。

## Session MCP / 会议知识验收

当前会议应用恢复链路依赖 Data Service session MCP。必须保留以下真实 stdio MCP 流程：

```text
knowledge_workspace_create
-> knowledge_session_create
-> knowledge_session_ingest(content_format="turns")
-> knowledge_session_build_start(mode="full")
-> knowledge_session_build_status
-> knowledge_graph_snapshot(scope="session")
-> knowledge_actor_summary
-> knowledge_session_query
-> knowledge_session_close
-> knowledge_session_delete
```

通过标准：

- 至少 3 个 speaker、10 个 turn 的会议转写能生成 actor/unit/topic/entity/source 节点。
- speaker 必须作为 `actor` 节点出现，不只作为普通 entity。
- actor 到 decision/task/risk/question/statement 的关系边带 `source_refs`。
- 同一 workspace 下两场会议的 graph/community/query 结果互不串扰。
- `knowledge_session_delete` 后对应 session graph 返回 disposed / not found。
- 会议应用通过 MCP 调用本服务，不 import Data Service 内部模块。

## 控制台验收

`/knowledge` 的目标定位是 Knowledge Service Console。

控制台应服务于：

- workspace / tenant 列表
- root_path 展示
- source registry
- 递归扫描文件数量
- failed / unreadable / low-signal sources
- build operations
- Distill Units
- Wiki artifacts
- GraphRAG graph quality
- Source Trace
- Quality Feedback
- Correction Rules
- Correction Plan
- MCP / HTTP / CLI 调试状态

不应作为会议、学习、面试或代码助手的终端用户入口。
