# V2.31 Phase 97 开发计划：Task-Aware Navigation Index

阶段：V2.31 / Phase 97
范围：任务感知导航索引与 task query artifact。
状态：pre-implementation planning。

## 1. 阶段目标

Phase 97 的目标是把既有 codebase facts、public surfaces、symbols、tests、architecture intent artifacts 转换为可被任务查询消费的导航索引。

本阶段只做：

- task taxonomy。
- task -> capability / surface / symbol / test / doc 候选匹配。
- ranked candidates。
- task query artifact 落盘和读回。
- 最小 HTTP/MCP/CLI 读取入口。

本阶段不做：

- lightweight call graph。
- impact graph。
- test selection ranking v2。
- token ledger。
- Copilot handoff。

这些属于 Phase 98-101。

## 2. 开发设计

新增 focused package：

```text
backend/data_service/code_assets/coding_agent_navigation/
  __init__.py
  persistence.py
  task_taxonomy.py
  navigation_index.py
  service.py
```

扩展接口：

```text
backend/app/api/v1/code_assets_coding_agent.py
backend/data_service/mcp_code_tools.py 或 focused MCP helper
backend/data_service/cli_code.py 或 focused CLI helper
```

若接口文件开始膨胀，后续 Phase 101 再拆独立 `mcp_code_task_navigation_tools.py` 和 `cli_code_task_navigation.py`。Phase 97 允许最小挂载，但核心逻辑必须留在 focused package。

## 3. 输入 artifacts

- `snapshot.json`
- `files.jsonl`
- `surfaces.jsonl`
- `symbols.jsonl`
- `evidence.jsonl`
- `overview.json`
- 可选：architecture intent report/context/proof graph。

缺失可选 artifacts 时不得失败，应返回 warnings 或 blockers。缺失 snapshot/surfaces/symbols 时为 blocking error。

## 4. 输出 artifacts

```text
workspace/assets/codebase/{codebase_id}/coding_agent/task_navigation/
  navigation_index.json
  task_queries/{task_id}.json
```

## 5. 任务分类规则

最小 task types：

```text
api
mcp_tool
cli
workflow
provider
bugfix
test
docs
architecture_review
unknown
```

分类基于关键词和已知 surface 类型，禁止 LLM-only 判定。

## 6. Ranking 规则

候选优先级：

1. exact surface/tool/command/path match。
2. capability match。
3. symbol qualified/name match。
4. test path/name match。
5. document/report/context hint。
6. token overlap only，必须标 `needs_review`，不得作为 accepted。

## 7. 架构门禁

- 不修改 `backend/app/api/v1/data_service.py`。
- 不修改 `backend/data_service/service.py`。
- 不修改 V2.0-V2.30 输入 artifacts。
- public payload 只返回 repo-relative path。
- 无 evidence 的 candidate 必须 `needs_review`。
