# V2.39 Phase 116 Scale Profile Acceptance Audit Report

## 1. 审计结论

结论：通过。

Phase 116 已完成大型项目 scale profile 的实现与验收闭环，可以进入 Phase 117 pre-implementation audit。该结论只覆盖 V2.39 / Phase 116，不代表 V2.40-V2.45 已完成。

## 2. 本阶段实现范围

- `architecture_scale_profile.json` 升级为 `schema_version = v2.39_scale`。
- 支持 scan budget：`max_files`、`max_loc`、`max_file_size_mb`、`timeout_seconds`、`shard_size`。
- 支持 `ready` / `partial` 状态和 structured blockers。
- 新增落盘 artifacts：
  - `scale/scan_budget_report.json`
  - `scale/paginated_readback_index.json`
  - `scale/scan_shards/files_0001.jsonl`
  - `scale/scan_shards/languages_0001.jsonl`
- 新增 readback API：
  - HTTP `GET /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/scale/readback`
  - MCP `knowledge_code_architecture_scale_readback`
  - CLI `knowledge code architecture scale-readback`
- 同步 frontend MCP contract snapshot，避免 registry / console drift。

## 3. 真实项目 E2E 验收

验收使用真实项目路径，不使用 mock-only 数据：

| Project | Result | File Count | LOC | Status | Blockers | Readback Rows | Path Leak |
| --- | --- | ---: | ---: | --- | ---: | ---: | --- |
| `/Users/Zhuanz/Desktop/workspace/data_service` | pass | 1117 | 193102 | partial | 2 | 1117 | false |
| `/Users/Zhuanz/Desktop/workspace/harnessOS` | pass | 2718 | 413561 | partial | 2 | 2718 | false |
| `/Users/Zhuanz/Desktop/workspace/codexPat` | pass | 1038 | 156446 | partial | 2 | 1038 | false |

说明：上述项目在本阶段验收中均按低预算触发 `partial` 和 `SCAN_BUDGET_EXCEEDED` blocker。该行为符合 Phase 116 要求：大型项目超预算必须返回 structured blocker，不得伪装成 `ready`。

## 4. 自动化测试

已执行：

```text
python3 -m py_compile \
  backend/data_service/code_assets/architecture/scale_profile.py \
  backend/data_service/code_assets/architecture/service.py \
  backend/data_service/code_assets/architecture/persistence.py \
  backend/app/api/v1/code_assets_architecture.py \
  backend/data_service/mcp_code_architecture_tools.py \
  backend/data_service/cli_code_architecture.py
```

结果：通过。

```text
pytest -q \
  backend/tests/test_v2_6_architecture_scale_profile.py \
  backend/tests/test_public_surface_guard.py \
  backend/tests/test_session_ingest_query_build_contract_plan.py \
  backend/tests/test_data_service_mcp.py
```

结果：`22 passed, 25 skipped`。

```text
git diff --check -- \
  backend/data_service/code_assets/architecture/scale_profile.py \
  backend/data_service/code_assets/architecture/service.py \
  backend/data_service/code_assets/architecture/persistence.py \
  backend/app/api/v1/code_assets_architecture.py \
  backend/data_service/mcp_code_architecture_tools.py \
  backend/data_service/cli_code_architecture.py \
  backend/tests/test_v2_6_architecture_scale_profile.py \
  backend/tests/test_public_surface_guard.py \
  backend/tests/test_session_ingest_query_build_contract_plan.py \
  backend/tests/test_data_service_mcp.py \
  frontend/src/data/mcpContract.ts \
  docs/V2.x/V2_39_PHASE_116_SCALE_PROFILE_DEVELOPMENT_PLAN.md \
  docs/V2.x/V2_39_PHASE_116_SCALE_PROFILE_ACCEPTANCE_PLAN.md \
  docs/V2.x/V2_39_PHASE_116_SCALE_PROFILE_PRE_IMPLEMENTATION_AUDIT_REPORT.md
```

结果：通过。

## 5. PRD 规格检视

| Requirement | Status | Evidence |
| --- | --- | --- |
| 大型项目 scale profile | pass | 三个真实项目生成 profile |
| scan budget / structured blocker | pass | 三个真实项目均返回 partial + blocker |
| shard artifact 落盘 | pass | readback index + files/languages shards |
| paginated readback | pass | HTTP/MCP/CLI readback 测试覆盖 |
| HTTP/MCP/CLI parity | pass | focused regression passed |
| public payload path redaction | pass | E2E `absolute_path_leak=false` |
| frontend MCP contract 同步 | pass | `test_console_mcp_contract_snapshot_matches_registry` passed |

## 6. False-Green 审计

已拒绝以下虚假验收路径：

- 未使用真实项目：已使用 data_service、HarnessOS、codexPat。
- 超预算项目伪装为 ready：实际输出 `partial`。
- 只生成 profile 不可分页读取：已验证 readback。
- HTTP 通过但 MCP/CLI 未测：已覆盖三端。
- artifact_refs 只包含 profile：已扩展 budget/readback/shard refs。
- public payload 泄露绝对路径：E2E 检查为 false。
- registry / frontend contract 漂移：已修复并回归。

## 7. 架构边界审计

- 未向 `backend/app/api/v1/data_service.py` 添加 V2.39 core route。
- 未向 `backend/data_service/service.py` 添加 V2.39 core logic。
- 核心逻辑保持在 `backend/data_service/code_assets/architecture/scale_profile.py` 和 `ArchitectureService` 薄封装内。
- 公开入口保持在 focused architecture router / MCP / CLI 文件。
- 未修改 source registry 语义。

## 8. 剩余风险

- Phase 116 不实现真正增量扫描。
- Phase 116 不实现多语言 AST/LSP provider。
- Phase 116 不实现 workflow/runtime extractor。
- HarnessOS 的架构理解仍依赖后续 Phase 117-122 增强。

这些风险均属于 V2.40-V2.45 后续阶段，不阻塞 Phase 116 通过。

## 9. 下一步

进入 Phase 117 / V2.40 pre-implementation audit。进入实现前必须重新确认：

- Python AST provider 为 mandatory baseline。
- TS/JS fixture baseline 可验收。
- tree-sitter / LSP 未配置时只能 `provider_unavailable`，不得 accepted。
- data_service / HarnessOS / codexPat 真实回归路径仍可用。
