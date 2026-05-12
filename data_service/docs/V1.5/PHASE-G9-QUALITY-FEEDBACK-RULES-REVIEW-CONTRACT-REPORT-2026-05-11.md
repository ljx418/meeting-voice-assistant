# PhaseG9 Quality Feedback / Rules / Review Contract Report

日期：2026-05-11

## 阶段目标

PhaseG9 继续沿 Interface Convergence 主线收敛 quality 能力组。本阶段目标是固化 Quality Feedback / Correction Rules / Review 的当前 contract，补充 drift tests，避免后续 HTTP / CLI 迁移时重复组装 payload 或提前开放 planned CLI `quality` 命令。

## 已完成内容

- 扩展 `docs/V1.5/quality-contract.md`，补齐 `knowledge_quality_feedback`、`knowledge_correction_rules`、`knowledge_review_correction_rule` 的 MCP request / response 稳定字段。
- 明确当前 HTTP 兼容入口：`/quality/feedback`、`/quality/feedback/list`、`/quality/corrections`、`/quality/corrections/build`、`/quality/corrections/review`。
- 明确 CLI `quality` 命令仍为 planned，不在本阶段新增。
- 新增 PhaseG9 drift tests，覆盖 MCP registry schema、V2 alias、HTTP route 集合、CLI parser 和 E2E response shape。
- 同步更新 `docs/V1.5/interface-convergence-matrix.md`、`docs/V1.5/current-vs-target-gap.md`、`docs/V1.5/current-vs-target-gap.drawio` 与 V1.5 roadmap。

## 对外能力检查

- 未新增 MCP tool。
- 未新增 HTTP route。
- 未新增 CLI command。
- `knowledge_quality_feedback` 稳定顶层字段保持 `feedback_id / created_at / workspace / target_type / target_id / action / label / suggested_value / reason / metadata`。
- `knowledge_correction_rules` 稳定顶层字段保持 `workspace / rules_path / items / total_count / filtered_count / summary / generated_at / schema_version`。
- `knowledge_review_correction_rule` 稳定顶层字段保持 `workspace / rules_path / rule / summary / correction_plan`。
- Review 保持 non-destructive governance 语义：只更新规则状态并刷新 correction plan，不改写 source data。

## 出门验证

- `cd frontend && npm run build`：通过。
- `backend/.venv/bin/python -m pytest backend/tests/test_data_service_mcp.py -q`：`29 passed`。
- `backend/.venv/bin/python -m pytest backend/tests/test_data_service.py backend/tests/test_data_service_api.py backend/tests/test_data_service_mcp.py -q`：`116 passed`。
- drawio XML 校验：通过。
