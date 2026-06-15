# V2.30 Phase 96B 验收审计报告：Architecture Intent 公共合同

审计日期：2026-06-10
阶段：V2.30 / Phase 96B
结论：accepted

## 1. 实现范围

新增公共合同实现：

- HTTP router：`backend/app/api/v1/code_assets_architecture_intent.py`
- MCP tools：`backend/data_service/mcp_code_architecture_intent_tools.py`
- CLI commands：`backend/data_service/cli_code_architecture_intent.py`
- Service facade：`backend/data_service/code_assets/architecture_intent/service.py`
- Contract test：`backend/tests/test_v2_30_architecture_intent_public_contracts.py`

## 2. 自动化测试

Focused test：

```text
PYTHONPATH=backend python3 -m pytest -q backend/tests/test_v2_30_architecture_intent_public_contracts.py
```

结果：

```text
1 passed
```

Phase 91-96B 回归：

```text
PYTHONPATH=backend python3 -m pytest -q backend/tests/test_v2_25_architecture_source_model.py backend/tests/test_v2_26_diagram_to_claim_parser.py backend/tests/test_v2_27_code_proof_graph.py backend/tests/test_v2_28_intent_inference.py backend/tests/test_v2_29_diagram_code_verification.py backend/tests/test_v2_30_architecture_intent_report_context_governance.py backend/tests/test_v2_30_architecture_intent_public_contracts.py
```

结果：

```text
9 passed
```

公共合同基线回归：

```text
PYTHONPATH=backend python3 -m pytest -q backend/tests/test_data_service_api.py::test_phaseg27_knowledge_entrypoint_exposes_build_write_aliases_only backend/tests/test_data_service_mcp.py::test_console_mcp_contract_snapshot_matches_registry backend/tests/test_data_service_mcp.py::test_phaseg14_quality_cli_stage3_commands_documented backend/tests/test_public_surface_guard.py::test_v16a_mcp_registry_matches_v15_public_surface_baseline backend/tests/test_public_surface_guard.py::test_v16a_knowledge_cli_parser_matches_v15_public_surface_baseline backend/tests/test_public_surface_guard.py::test_v16_current_http_route_inventory_matches_v15_baseline_plus_accepted_overlays backend/tests/test_session_graphrag_contract.py::test_v16d1_session_contract_baseline_and_d2_surface_boundaries_remain_explicit backend/tests/test_target_http_session_query.py::test_v16d5_session_query_surface_auth_and_cli_inventory backend/tests/test_v16_closure_acceptance.py::test_closure_cli_current_accepted_baseline_is_unchanged
```

结果：

```text
9 passed
```

全量后端测试：

```text
PYTHONPATH=backend python3 -m pytest -q backend/tests
```

结果：

```text
479 passed, 617 warnings in 229.24s
```

## 3. 真实仓库 E2E

### data_service

| 指标 | 值 |
| --- | ---: |
| duration_seconds | 16.4 |
| snapshot_id | snap_bc0a26b967739d1126b2 |
| verification_count | 11442 |
| intent_candidate_count | 9 |
| report_node_count | 69 |
| HTTP/MCP snapshot match | true |
| HTTP/CLI snapshot match | true |
| HTTP/MCP verification match | true |
| HTTP/CLI verification match | true |
| CLI rc | 0 |
| no_path_leak | true |

### HarnessOS

| 指标 | 值 |
| --- | ---: |
| duration_seconds | 104.75 |
| snapshot_id | snap_22db358076d5ef40605a |
| verification_count | 6766 |
| intent_candidate_count | 9 |
| report_node_count | 69 |
| HTTP/MCP snapshot match | true |
| HTTP/CLI snapshot match | true |
| HTTP/MCP verification match | true |
| HTTP/CLI verification match | true |
| CLI rc | 0 |
| no_path_leak | true |

## 4. PRD 规格检视

| 规格项 | 结果 |
| --- | --- |
| HTTP build/read | pass |
| MCP build/read | pass |
| CLI read | pass |
| 三端 stable fields 一致 | pass |
| governance confirm/revoke overlay | pass |
| public output no absolute path leak | pass |
| 不改写 Phase 91-95 artifact 语义 | pass |

## 5. False-Green 审计

| 风险 | 结果 |
| --- | --- |
| 只测 HTTP 冒充三端通过 | 未发生 |
| 只用 mock repo | 未发生，已跑 data_service 与 HarnessOS |
| 公共 payload 泄露本机绝对路径 | 未发现 |
| CLI 输出非法 JSON | 未发生 |
| MCP tool spec 未注册 | 未发生 |
| confirm/revoke 作为 artifact mutation | 未发生，保持 read-time overlay |
| 公共合同 baseline 未同步 | 未发生，public surface guard、MCP console contract、CLI inventory 均已通过 |

## 6. 出门结论

Phase 96B 已补齐 V2.25-V2.30 architecture intent 的 HTTP/MCP/CLI 公共合同。

覆盖矩阵中的 `Public HTTP/MCP/CLI contracts` 可以从 `not_implemented` 更新为 `accepted`。
