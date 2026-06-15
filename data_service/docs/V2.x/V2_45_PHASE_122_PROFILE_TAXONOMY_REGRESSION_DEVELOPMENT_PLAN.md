# V2.45 Phase 122 Profile / Taxonomy + Continuous Regression Development Plan

## 1. 阶段目标

Phase 122 固化 project profile、taxonomy registry、real repo regression matrix 和 no-hardcode audit，使 data_service、HarnessOS、codexPat 成为持续回归集。

## 2. 输出 Artifacts

```text
workspace/assets/codebase/{codebase_id}/architecture/v2_45/
  project_profiles/{profile_id}.json
  taxonomy_registry.json
  real_repo_regression_matrix.json
  no_hardcode_audit.json
  closure_audit_report.md
```

## 3. 实现计划

1. 新增 profile registry：project family、terms、entrypoint_patterns、workflow_patterns、authority_rules。
2. 新增 taxonomy registry：capability terms、architecture terms、risk labels。
3. 生成真实项目 regression matrix。
4. 实现 no-hardcode audit：检查通用模块是否出现 HarnessOS/codexPat/data_service 专用路径或术语。
5. 更新 coverage matrix accepted rows。
6. 输出 V2.39-V2.45 closure audit。

## 4. 边界

- profile 可包含 HarnessOS 术语。
- 通用 extractor 不得硬编码 HarnessOS 术语。
- regression unavailable 必须 structured unavailable，不得 accepted。
