# V2.45 Phase 122 Profile / Taxonomy + Continuous Regression Acceptance Plan

## 1. 验收定义

Phase 122 通过条件：profile/taxonomy/regression/no-hardcode/coverage/closure 全部完成，且无 open fatal / major。

## 2. 自动化测试

Focused:

```text
backend/tests/test_v2_45_profile_taxonomy_regression.py
```

必须验证：

- project profile 可创建、读取、应用。
- taxonomy registry 可读写。
- real_repo_regression_matrix 包含 data_service、HarnessOS、codexPat。
- no-hardcode audit 能扫描通用 extractor。
- coverage matrix accepted rows 必须有 evidence。

Regression:

```text
backend/tests/test_v2_42_relationship_chain_v3.py
backend/tests/test_v2_43_document_semantics.py
backend/tests/test_v2_44_token_budget_context_cache.py
backend/tests/test_public_surface_guard.py
backend/tests/test_data_service_mcp.py
```

## 3. 真实项目 E2E

每个项目必须记录：

- status：accepted / accepted_with_blockers / structured_unavailable
- artifact refs
- test commands
- open findings
- path redaction result

## 4. False-Green Rejection

拒绝：

- 未运行真实项目却写 pass。
- profile 规则写入通用 extractor。
- accepted coverage row 缺 evidence。
- no-hardcode audit 未执行。
