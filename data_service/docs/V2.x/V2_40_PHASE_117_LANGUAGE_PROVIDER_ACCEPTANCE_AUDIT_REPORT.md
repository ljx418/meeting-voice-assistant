# V2.40 Phase 117 Language Provider Acceptance Audit Report

## 1. 审计结论

结论：通过。

Phase 117 已完成多语言 Provider Contract 的实现与验收闭环，可以进入 Phase 118 pre-implementation audit。该结论只覆盖 V2.40 / Phase 117，不代表 V2.41-V2.45 已完成。

## 2. 本阶段实现范围

- 新增 V2.40 language provider artifacts：
  - `architecture/v2_40/language_provider_status.jsonl`
  - `architecture/v2_40/symbol_facts.jsonl`
  - `architecture/v2_40/reference_facts.jsonl`
- Python AST provider 作为 mandatory baseline：
  - 输出 module/class/function/import facts。
  - 单文件语法错误隔离为 `PYTHON_SYNTAX_ERROR` warning，不导致全仓失败。
- TS/JS baseline lexical provider：
  - 输出 import/export 级别事实。
  - 所有 TS/JS baseline facts 标记 `needs_review = true`，避免把 lexical hint 当作完整 AST/LSP 事实。
- tree-sitter / LSP provider：
  - 未配置时固定输出 `provider_unavailable`。
  - 不允许计入 accepted provider。
- 新增读取入口：
  - HTTP `POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/language-providers/build`
  - HTTP `GET /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/language-providers`
  - MCP `knowledge_code_architecture_language_providers_build`
  - MCP `knowledge_code_architecture_language_providers`
  - CLI `knowledge code architecture language-providers-build`
  - CLI `knowledge code architecture language-providers`
- 同步 frontend MCP contract snapshot，避免 registry / console drift。

## 3. 真实项目 E2E 验收

验收使用真实项目路径，不使用 mock-only 数据：

| Project | Result | File Count | LOC | Python AST | TS/JS Baseline | Symbols | References | Path Leak |
| --- | --- | ---: | ---: | --- | --- | ---: | ---: | --- |
| `/Users/Zhuanz/Desktop/workspace/data_service` | pass | 1123 | 194117 | accepted | accepted | 4983 | 2830 | false |
| `/Users/Zhuanz/Desktop/workspace/harnessOS` | pass | 2718 | 413561 | accepted | accepted | 8674 | 5893 | false |
| `/Users/Zhuanz/Desktop/workspace/codexPat` | pass | 1044 | 157535 | accepted | accepted | 508 | 434 | false |

Provider unavailable 状态：

| Provider | Expected Status | Result |
| --- | --- | --- |
| tree-sitter | `provider_unavailable` unless configured | pass |
| LSP | `provider_unavailable` unless configured | pass |

说明：本阶段不声称 tree-sitter 或 LSP provider 已接入，也不声称 TS/JS lexical provider 等价于 AST/LSP。

## 4. 自动化测试

已执行：

```text
python3 -m py_compile \
  backend/data_service/code_assets/architecture/language_provider_v2.py \
  backend/data_service/code_assets/architecture/service.py \
  backend/app/api/v1/code_assets_architecture.py \
  backend/data_service/mcp_code_architecture_tools.py \
  backend/data_service/cli_code_architecture.py
```

结果：通过。

```text
PYTHONPATH=backend pytest -q backend/tests/test_v2_40_language_provider_contract.py
```

结果：`2 passed`。

```text
PYTHONPATH=backend pytest -q \
  backend/tests/test_v2_40_language_provider_contract.py \
  backend/tests/test_public_surface_guard.py \
  backend/tests/test_session_ingest_query_build_contract_plan.py \
  backend/tests/test_data_service_mcp.py
```

结果：`17 passed, 25 skipped`。

MCP frontend registry parity：

```text
same: True
missing: []
extra: []
```

## 5. PRD 规格检视

| Requirement | Status | Evidence |
| --- | --- | --- |
| Python AST mandatory provider | pass | 三个真实项目 Python AST status 均为 accepted |
| TS/JS baseline facts | pass | 三个真实项目 TS/JS baseline status 均为 accepted |
| tree-sitter / LSP optional boundary | pass | 未配置时均为 `provider_unavailable` |
| symbol facts with evidence | pass | focused tests 验证 repo-relative path + line_range |
| reference facts with evidence | pass | focused tests 验证 repo-relative path + line_range |
| syntax error isolation | pass | fixture `backend/bad_syntax.py` 输出 warning，不中断构建 |
| HTTP/MCP/CLI parity | pass | focused tests 覆盖 build/read 三端 |
| public payload path redaction | pass | 三个真实项目 E2E `path_leak=false` |
| frontend MCP contract 同步 | pass | registry parity script result `same=True` |

## 6. False-Green 审计

已拒绝以下虚假验收路径：

- 只声明 provider 名称但没有 provider output：focused tests 检查 fact counts 和 artifact readback。
- tree-sitter/LSP 未配置却 accepted：真实 E2E 与 tests 均要求 `provider_unavailable`。
- TS/JS lexical facts 伪装为高置信 AST：所有 TS/JS baseline facts 标记 `needs_review=true`。
- accepted facts 缺少证据：tests 验证 path、line_range、evidence_refs。
- 单文件语法错误导致全仓失败：tests 验证 syntax warning isolation。
- HTTP 通过但 MCP/CLI 未测：三端均覆盖。
- 真实项目缺失时伪造 accepted：E2E 脚本要求 structured unavailable；本轮三个路径均存在。

## 7. 架构边界审计

- 未向 `backend/app/api/v1/data_service.py` 添加 V2.40 core route。
- 未向 `backend/data_service/service.py` 添加 V2.40 core logic。
- 核心 provider 逻辑位于 `backend/data_service/code_assets/architecture/language_provider_v2.py`。
- 公开入口保持在 focused architecture router / MCP / CLI 文件。
- V2.40 artifacts 写入 `assets/codebase/{codebase_id}/architecture/v2_40/`，不污染 source registry。
- 本阶段未声称 full call graph、data flow、control flow、type inference 或 runtime topology。

## 8. 剩余风险

- tree-sitter provider 尚未接入，状态为 `provider_unavailable`。
- LSP provider 尚未接入，状态为 `provider_unavailable`。
- TS/JS provider 仍是 lexical baseline，不等价于完整 AST。
- workflow/runtime/agent/TUI/CLI/console 泛化抽取属于 Phase 118。
- relationship chain 增强属于 Phase 119。

这些风险均属于 V2.41-V2.45 后续阶段，不阻塞 Phase 117 通过。

## 9. 下一步

进入 Phase 118 / V2.41 pre-implementation audit。进入实现前必须确认：

- workflow/runtime candidate 不得被渲染成 production runtime topology。
- extractor 必须泛化，不得硬编码 HarnessOS。
- data_service、HarnessOS、codexPat 真实项目路径仍可用，缺失时只能 structured unavailable。
- Phase 118 必须继续保留 V2.39/V2.40 回归测试。
