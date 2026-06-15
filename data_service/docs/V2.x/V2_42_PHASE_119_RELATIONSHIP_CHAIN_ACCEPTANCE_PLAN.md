# V2.42 Phase 119 Relationship Chain v3 Acceptance Plan

## 1. 验收定义

Phase 119 通过条件：relationship chains 落盘、可读回、三端一致，且 forbidden edge scan 证明没有被错误接受的 runtime/data/control/type/topology 关系。

## 2. 自动化测试

Focused:

```text
backend/tests/test_v2_42_relationship_chain_v3.py
```

必须验证：

- data_service 至少 10 条 accepted chain 或明确 blocker。
- 每条 accepted chain 有 nodes、edges、evidence_refs。
- edge type 均在 allowlist。
- forbidden edge type scan 通过。
- heuristic edge 不得被标记为 deterministic runtime call。
- public payload 无绝对路径、secret、raw traceback。
- HTTP/MCP/CLI build/read parity。

Regression:

```text
backend/tests/test_v2_41_workflow_runtime_candidates.py
backend/tests/test_v2_40_language_provider_contract.py
backend/tests/test_public_surface_guard.py
backend/tests/test_session_ingest_query_build_contract_plan.py
backend/tests/test_data_service_mcp.py
```

## 3. 真实项目 E2E

- data_service：至少 10 条 accepted chain。
- HarnessOS：accepted chain 或 precise structured blocker。
- codexPat：relationship chain 或 blocker；非 HTTP/MCP 项目不得硬失败。

## 4. False-Green Rejection

拒绝：

- import/reference 被称为 runtime call。
- 空链路标 accepted。
- chain 缺 evidence_refs。
- forbidden edge type 出现在 accepted edge 中。
- 只跑 mock fixture，不跑真实项目。

## 5. 出门条件

- Focused + regression tests pass。
- artifact inspection pass。
- PRD/spec review 无 fatal / major。
- False-green audit 无 fatal / major。
