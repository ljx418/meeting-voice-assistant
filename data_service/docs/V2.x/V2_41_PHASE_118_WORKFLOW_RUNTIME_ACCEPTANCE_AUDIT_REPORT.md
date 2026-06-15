# V2.41 Phase 118 Workflow / Runtime Extractor Acceptance Audit Report

## 1. 审计结论

结论：通过。

Phase 118 已完成 workflow / runtime / entrypoint candidate extractor 的实现与验收闭环，可以进入 Phase 119 pre-implementation audit。该结论只覆盖 V2.41 / Phase 118，不代表 V2.42-V2.45 已完成。

## 2. 本阶段实现范围

- 新增 V2.41 workflow/runtime artifacts：
  - `architecture/v2_41/workflow_candidates.jsonl`
  - `architecture/v2_41/runtime_adapter_candidates.jsonl`
  - `architecture/v2_41/entrypoint_candidates.jsonl`
  - `architecture/v2_41/workflow_runtime_summary.json`
- 新增 candidate extractors：
  - workflow manifest
  - pipeline config
  - package scripts
  - Python CLI entrypoint hints
  - TUI / console hints
  - runtime adapter / provider / plugin hints
  - agent registry hints
- 新增读取入口：
  - HTTP `POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/workflow-runtime/build`
  - HTTP `GET /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/workflow-runtime`
  - MCP `knowledge_code_architecture_workflow_runtime_build`
  - MCP `knowledge_code_architecture_workflow_runtime`
  - CLI `knowledge code architecture workflow-runtime-build`
  - CLI `knowledge code architecture workflow-runtime`
- 同步 frontend MCP contract snapshot，避免 registry / console drift。

## 3. 真实项目 E2E 验收

验收使用真实项目路径，不使用 mock-only 数据：

| Project | Result | File Count | LOC | Workflow | Runtime / Agent | Entrypoint | Topology Claims | Heuristic Missing Review | Path Leak |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `/Users/Zhuanz/Desktop/workspace/data_service` | pass | 1129 | 195109 | 0 | 457 | 187 | 0 | 0 | false |
| `/Users/Zhuanz/Desktop/workspace/harnessOS` | pass | 2718 | 413561 | 0 | 1649 | 800 | 0 | 0 | false |
| `/Users/Zhuanz/Desktop/workspace/codexPat` | pass | 1048 | 158189 | 0 | 510 | 191 | 0 | 0 | false |

说明：

- 真实项目中 workflow manifest 未命中，但 focused fixture 已覆盖 `.github/workflows/*.yml` 的确定性抽取。
- 三个真实项目均产出 runtime / agent / entrypoint candidate。
- 所有 heuristic candidate 均带 `needs_review`。
- 没有任何 candidate 被标记为 production runtime topology。

## 4. 自动化测试

已执行：

```text
python3 -m py_compile \
  backend/data_service/code_assets/architecture/workflow_runtime_v2.py \
  backend/data_service/code_assets/architecture/service.py \
  backend/app/api/v1/code_assets_architecture.py \
  backend/data_service/mcp_code_architecture_tools.py \
  backend/data_service/cli_code_architecture.py
```

结果：通过。

```text
PYTHONPATH=backend pytest -q backend/tests/test_v2_41_workflow_runtime_candidates.py
```

结果：`2 passed`。

```text
PYTHONPATH=backend pytest -q \
  backend/tests/test_v2_41_workflow_runtime_candidates.py \
  backend/tests/test_v2_40_language_provider_contract.py \
  backend/tests/test_public_surface_guard.py \
  backend/tests/test_session_ingest_query_build_contract_plan.py \
  backend/tests/test_data_service_mcp.py
```

结果：`19 passed, 25 skipped`。

MCP frontend registry parity：

```text
same: True
missing: []
extra: []
```

## 5. PRD 规格检视

| Requirement | Status | Evidence |
| --- | --- | --- |
| workflow manifest extractor | pass | focused fixture `.github/workflows/ci.yml` |
| runtime adapter candidate extractor | pass | focused fixture + 三个真实项目 |
| agent registry candidate extractor | pass | focused fixture + 三个真实项目 |
| CLI/TUI/console candidate extractor | pass | focused fixture + 三个真实项目 |
| candidate evidence | pass | focused tests 验证 repo-relative path + line_range |
| no production runtime topology | pass | E2E `topology_claim_count=0` |
| heuristic candidate needs review | pass | E2E `heuristic_without_review=0` |
| HTTP/MCP/CLI parity | pass | focused tests 覆盖 build/read 三端 |
| public payload path redaction | pass | 三个真实项目 E2E `path_leak=false` |

## 6. False-Green 审计

已拒绝以下虚假验收路径：

- candidate 被称为 production runtime topology：artifact 固定 `topology_claim=false`。
- heuristic candidate 未标记 review：tests 和 E2E 均检查。
- import/reference 被称为 runtime call：本阶段不输出 call edge。
- HarnessOS 专用术语硬编码：extractor 只使用通用 path/text pattern。
- 只测 mock fixture：已跑 data_service、HarnessOS、codexPat。
- HTTP 通过但 MCP/CLI 未测：三端均覆盖。
- public payload 泄露绝对路径：E2E 检查为 false。

## 7. 架构边界审计

- 未向 `backend/app/api/v1/data_service.py` 添加 V2.41 core route。
- 未向 `backend/data_service/service.py` 添加 V2.41 core logic。
- 核心 provider 逻辑位于 `backend/data_service/code_assets/architecture/workflow_runtime_v2.py`。
- 公开入口保持在 focused architecture router / MCP / CLI 文件。
- V2.41 artifacts 写入 `assets/codebase/{codebase_id}/architecture/v2_41/`，不污染 source registry。
- 本阶段未声称 full call graph、data flow、control flow、type inference 或 production runtime topology。

## 8. 剩余风险

- 真实项目中 workflow manifest 未命中，需要后续 profile/taxonomy 阶段持续扩展 pattern catalog。
- runtime/agent/entrypoint candidate 数量较大，排序和关系链过滤属于 Phase 119 / Phase 121 的后续职责。
- 本阶段只输出 candidate，不证明调用链路或运行时拓扑。

这些风险均属于 V2.42-V2.45 后续阶段，不阻塞 Phase 118 通过。

## 9. 下一步

进入 Phase 119 / V2.42 pre-implementation audit。进入实现前必须确认：

- relationship chain 不得输出 full call graph。
- deterministic / heuristic edge 必须分级。
- forbidden edge type scan 必须自动化。
- data_service 至少 10 条 accepted chain；HarnessOS/codexPat 必须输出 accepted chain 或 structured blocker。
