# V1.5 PhaseA2：Quality MCP Handler 模块化报告

日期：2026-05-08

## 目标

完成 V1.5-PhaseA 的第二步：把 Quality Governance MCP 的 tool schema 和 handler 从 `mcp_stdio.py` 中拆出，继续压缩 MCP stdio 入口职责，同时保持 legacy tool 与 V2 envelope tool 的外部契约兼容。

## 本阶段变更

- 新增 `backend/data_service/mcp_quality_tools.py`。
- `mcp_stdio.py` 改为通过 `QUALITY_TOOL_SPECS` 注册质量治理工具。
- `mcp_stdio.py` 改为通过 `handle_quality_tool(...)` 分发质量治理 MCP 调用。
- 保留以下 legacy tool 的输入与输出：
  - `knowledge_quality_summary`
  - `knowledge_correction_plan`
  - `knowledge_quality_feedback`
  - `knowledge_correction_rules`
  - `knowledge_review_correction_rule`
- 保留对应 V2 envelope tool 对 legacy tool 的复用路径：
  - `knowledge_quality_summary_v2`
  - `knowledge_correction_plan_v2`
  - `knowledge_quality_feedback_v2`
  - `knowledge_correction_rules_v2`
  - `knowledge_review_correction_rule_v2`

## 验收结果

### 自动化回归

```bash
backend/.venv/bin/python -m py_compile backend/data_service/mcp_stdio.py backend/data_service/mcp_quality_tools.py backend/data_service/mcp_session_tools.py
```

结果：通过。

```bash
backend/.venv/bin/python -m pytest backend/tests/test_data_service_mcp.py -q
```

结果：

```text
16 passed
```

```bash
backend/.venv/bin/python -m pytest backend/tests/test_data_service.py backend/tests/test_data_service_api.py backend/tests/test_data_service_mcp.py -q
```

结果：

```text
94 passed
```

### 出门验证

通过 MCP handler 直接执行：

```text
knowledge_quality_feedback
-> knowledge_correction_rules
-> knowledge_review_correction_rule(status="approved")
-> knowledge_correction_plan
-> knowledge_quality_summary
-> knowledge_quality_feedback_v2
```

结果摘要：

```json
{
  "feedback_action": "merge_suggest",
  "rules_total_count": 1,
  "reviewed_status": "approved",
  "plan_action_count": 1,
  "summary_feedback_count": 1,
  "v2_status": "ok",
  "v2_data_action": "merge_suggest"
}
```

## 当前边界

PhaseA1 和 PhaseA2 已完成 Session 与 Quality 两类高密度 MCP handler 的模块化。下一步 PhaseA3 应继续拆分 workspace/source/build handler，并抽出共享 envelope/error/helper 模块，避免 `mcp_stdio.py` 继续承载 lifecycle 细节。
