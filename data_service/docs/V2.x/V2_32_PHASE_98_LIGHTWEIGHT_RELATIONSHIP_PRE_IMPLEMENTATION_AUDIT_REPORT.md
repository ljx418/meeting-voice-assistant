# V2.32 Phase 98 预实施审计：Lightweight Relationship Graph

审计日期：2026-06-10
阶段：V2.32 / Phase 98
结论：**通过，可以进入 Phase 98 实现。**

## 1. 前置状态

Phase 97 已验收：

- `navigation_index.json` 可生成。
- `task_queries/{task_id}.json` 可生成。
- data_service 5 个真实任务通过。
- HarnessOS 3 个真实任务输出 structured blocker。
- 无 open fatal / major。

证据：

```text
docs/V2.x/V2_31_PHASE_97_TASK_NAVIGATION_ACCEPTANCE_AUDIT_REPORT.md
```

## 2. PRD 对齐

Phase 98 对齐 V2.31-V2.36 PRD 中的 Lightweight Call & Impact Graph，但本阶段只做 relationship graph。

允许：

- direct AST syntax relation。
- static import relation。
- surface handler relation。
- registry/config/test reference relation。
- heuristic relation with `needs_review`。
- dynamic unresolved blocker。

不允许：

- full call graph。
- data flow / control flow。
- runtime topology。
- type inference。
- production runtime trace。

## 3. 架构边界

实现必须保持 focused package：

```text
backend/data_service/code_assets/coding_agent_navigation/
```

HTTP/MCP/CLI 只做薄挂载。

禁止修改：

```text
backend/app/api/v1/data_service.py
backend/data_service/service.py
```

禁止改写：

- V2.0-V2.30 输入 artifacts。
- Phase 97 navigation index / task query artifacts，除非显式重建 Phase 97。

## 4. 风险审计

| 风险 | 等级 | 审计意见 |
| --- | --- | --- |
| import 被误写为 runtime call | major | 必须用 `module_imports_module` + `static_reference` |
| AST candidate 被误写成完整调用图 | major | 只允许 `direct_call_ast` / `method_call_candidate` |
| HarnessOS dynamic dispatch 假成功 | major | 必须输出 blocker |
| relationship 空结果假通过 | major | 空 graph 必须 blocked |
| public path leak | major | 必须 redaction gate |

## 5. 预实施结论

无 open fatal / major。可以进入 Phase 98 实现。
