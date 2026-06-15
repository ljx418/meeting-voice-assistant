# V2.41 Phase 118 Workflow / Runtime Extractor Acceptance Plan

## 1. 验收定义

Phase 118 只有在 workflow/runtime candidates 落盘、HTTP/MCP/CLI 读取一致、真实项目 E2E 完成，并且没有 production runtime topology 过度声明时才可通过。

## 2. 自动化测试

Focused tests:

```text
backend/tests/test_v2_41_workflow_runtime_candidates.py
```

测试必须验证：

- workflow manifest pattern 可抽取。
- runtime adapter / agent registry / CLI/TUI/console candidate 可抽取。
- 每条 candidate 有 repo-relative path、line_range、evidence_refs。
- heuristic candidate 必须 `needs_review`。
- public payload 不泄露绝对路径、secret、token、raw traceback。
- HTTP/MCP/CLI 输出稳定字段一致。
- 缺失 artifact 返回 `ARCHITECTURE_WORKFLOW_RUNTIME_NOT_BUILT`。

Regression tests:

```text
backend/tests/test_v2_40_language_provider_contract.py
backend/tests/test_public_surface_guard.py
backend/tests/test_session_ingest_query_build_contract_plan.py
backend/tests/test_data_service_mcp.py
```

## 3. 真实项目 E2E

必须运行：

```text
/Users/Zhuanz/Desktop/workspace/data_service
/Users/Zhuanz/Desktop/workspace/harnessOS
/Users/Zhuanz/Desktop/workspace/codexPat
```

验收要求：

- data_service：至少发现 HTTP/MCP/CLI 或 package/script 入口候选。
- HarnessOS：必须执行 workflow/runtime/agent/CLI/TUI/console extractor attempt；成功则输出 candidate，失败则输出 precise blocker。
- codexPat：非 HTTP/MCP 项目不得硬失败；应输出 desktop/app/script/entrypoint candidate 或 structured blocker。

## 4. False-Green Rejection

拒绝以下情况：

- candidate 被称为 production runtime topology。
- import/reference 被称为 runtime call。
- HarnessOS 专用术语硬编码进通用 extractor。
- 只测 mock fixture，不跑真实项目。
- accepted/readable output 缺少 evidence line range。
- HTTP 通过但 MCP/CLI 未测。
- public payload 泄露本地绝对路径。

## 5. 出门条件

- Focused tests pass。
- Regression tests pass。
- 三个真实项目 E2E 结果记录。
- Artifact inspection 证明 v2_41 artifacts 存在且可读回。
- PRD/spec review 无 fatal / major。
- False-green audit 无 fatal / major。
