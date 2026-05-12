# PhaseG7 Low Signal Audit Contract Report

日期：2026-05-11

## 目标

PhaseG7 将 Quality / Low Signal Audit 当前 HTTP 实现背后的 payload 组装逻辑抽为 shared contract helper。本阶段只让现有 HTTP `/api/v1/knowledge/quality/low-signal-audit` 复用同一个 serializer，不新增 MCP tool、CLI command 或 HTTP route。

## 变更

- 新增 `backend/data_service/quality_contract.py`：
  - `low_signal_audit_payload(service, limit=30)` 统一生成低信号审计 payload。
  - 固化 `limit` normalization：1-100，默认 30。
  - 保持响应顶层字段：`workspace / audited_at / overall_status / checks / metrics / samples / recommendations`。
- 更新 HTTP route：
  - `POST /api/v1/knowledge/quality/low-signal-audit` 改为调用 `low_signal_audit_payload`。
  - API 层不再持有 low-signal audit payload 组装逻辑。
- 新增 contract test：
  - 确认 HTTP response 与 shared helper 输出完全一致。
  - 确认仍未新增 CLI `quality` command。

## 出门验证

- `backend/.venv/bin/python -m pytest backend/tests/test_data_service_api.py::test_phaseg7_low_signal_audit_http_uses_shared_contract_helper -q`：1 passed。
- `npm run build`：通过。
- `backend/.venv/bin/python -m pytest backend/tests/test_data_service_mcp.py -q`：25 passed。
- `backend/.venv/bin/python -m pytest backend/tests/test_data_service.py backend/tests/test_data_service_api.py backend/tests/test_data_service_mcp.py -q`：112 passed。
- Draw.io XML 校验：通过。

## 对外能力检查

- 不新增 MCP tool。
- 不新增 CLI `quality` command。
- 不新增 HTTP route。
- 不改变当前 `/api/v1/knowledge/quality/low-signal-audit` 响应字段集合。

## 下一步

进入 PhaseG8：建议评估 Quality Summary / Correction Plan 这类 MCP-primary 能力是否需要 shared contract 文档和 drift tests；继续保持 MCP-first、最小粒度和兼容窗口策略。
