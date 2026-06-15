# V2.31 Phase 97 预实施审计：Task-Aware Navigation Index

审计日期：2026-06-10
结论：通过，可以进入 Phase 97 实现。

## 1. 规格对齐

Phase 97 对齐 V2.31-V2.36 PRD 的第一阶段：

- 只建立任务导航索引。
- 只做 task -> capability/surface/symbol/test/doc 候选。
- 不做轻量调用图、影响分析、token ledger 或 Agent handoff。

## 2. 架构边界

计划新增 focused package：

```text
backend/data_service/code_assets/coding_agent_navigation/
```

允许最小改动：

- `backend/app/api/v1/code_assets_coding_agent.py`
- `backend/data_service/mcp_code_tools.py` 或 focused helper
- `backend/data_service/cli_code.py` 或 focused helper

不允许：

- 修改 `backend/app/api/v1/data_service.py`。
- 修改 `backend/data_service/service.py`。
- 改写 V2.0-V2.30 输入 artifacts。

## 3. 真实数据前提

Phase 97 使用真实仓库：

- data_service：当前 workspace 项目。
- HarnessOS：`/Users/Zhuanz/Desktop/workspace/harnessOS`，若路径或 artifacts 不可用，必须输出 blocker，不得伪造成功。

## 4. 风险审计

| 风险 | 等级 | 处理 |
| --- | --- | --- |
| token overlap 被当作 accepted evidence | major | token-only candidate 必须 needs_review |
| 缺失上游 artifact 静默成功 | major | 必需 artifact 缺失返回 blocking error |
| 阶段越界实现 relationship graph | major | Phase 97 禁止输出 relationships.jsonl |
| public path leak | major | repo-relative path gate |

## 5. 审计结论

无 open fatal/major。可以进入 Phase 97 业务实现。
