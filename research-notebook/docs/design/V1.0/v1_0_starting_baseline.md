# ResearchNotebook V1.0 Starting Baseline

文档状态：V1.0 planning baseline。
配套核心文档：`v1_0_current_gap_analysis.md` 与 `v1_0_current_gap_analysis.drawio`。

## 1. 起点

当前 `research-notebook` 仓库已经建立 V1.0 文档草案，但尚未进入正式代码实施。

已完成的输入：

- 已阅读 `data_service` backend baseline；
- 已读取 Stitch 项目 `5501162743214630907` 的设计系统和屏幕清单；
- 已建立 `docs/design/V1.0` 文档集；
- 已建立 `docs/roadmap` 中 multi-format ingestion 和 assessment contract roadmap；
- 已明确 ResearchNotebook 与 `data_service` 的仓库和职责边界。

## 2. 已有事实

`data_service` V1.6 当前可作为后端基础：

- workspace lifecycle；
- source lifecycle；
- build lifecycle；
- workspace query / distill；
- graph read surfaces；
- session lifecycle / ingest / query / build；
- quality feedback / correction rules / plan；
- stable `artifact_ref`。

ResearchNotebook 当前只能依赖 target routes：

```text
/api/workspaces/...
```

不能依赖：

- `/api/v1/knowledge/*` 作为新功能入口；
- raw local path；
- cache path；
- artifact physical path；
- GraphRAG / LLMWiki 内部存储结构。

## 3. Stitch 原型基线

Stitch 项目当前可见核心屏幕：

- 工作区主页；
- AI 研究工作台；
- Notebook AI Workspace Flow；
- 若干参考截图；
- 一份 PRD markdown artifact。

设计系统：

- light mode first；
- Roboto Flex；
- Google Blue `#0b57d0`；
- 280px fixed sidebar；
- fluid main canvas；
- research/workbench-oriented desktop layout。

## 4. V1.0 起点判断

当前不是从零开始设计产品方向，而是在以下已确认边界内收敛实现计划：

```text
Stitch prototype
  + NotebookLM source-grounded workflow
  + Obsidian workspace/graph mental model
  + data_service target HTTP routes
  -> ResearchNotebook V1.0 source-grounded personal knowledge MVP
```

V1.0 最小产品主线：

- Home；
- Workspace Source Library；
- Source Import；
- Build Status；
- Ask with Evidence；
- Source Trace / Provenance Drawer；
- Session Workbench；
- Read-only Graph Context；
- Lightweight Feedback。

## 5. 非目标

V1.0 不做：

- 后端 parser/indexer/retriever；
- `/knowledge` 产品化改造；
- 完整 source preview；
- 精确 page/slide/timestamp/json path citation backjump；
- JSON/PPT/video/audio 全量摄入；
- 面试题生成和评分；
- mastery profile；
- rich editor persistence；
- cloud sync；
- collaboration。
