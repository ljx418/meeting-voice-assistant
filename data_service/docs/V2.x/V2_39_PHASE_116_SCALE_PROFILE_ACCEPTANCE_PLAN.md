# V2.39 Phase 116 Acceptance Plan：大型项目性能优化

## 1. 阶段验收目标

Phase 116 通过时，系统必须能对真实 codebase 生成可预算、可分页、可审计的大型项目 scale profile。

## 2. 自动化验收

必须通过：

```text
pytest -q backend/tests/test_v2_39_scale_profile.py
pytest -q backend/tests/test_public_surface_guard.py
git diff --check
```

如果全量测试因 Python/依赖环境阻塞，必须记录 blocker，不得伪装通过。

## 3. 真实项目验收

至少运行：

- data_service：必须生成 ready 或 partial scale profile。
- HarnessOS：必须生成 ready / partial / structured unavailable。
- codexPat：必须生成 ready / partial / structured unavailable。

## 4. Artifact 验收

必须落盘：

```text
architecture_scale_profile.json
architecture/scale/scan_budget_report.json
architecture/scale/paginated_readback_index.json
architecture/scale/scan_shards/files_0001.jsonl
architecture/scale/scan_shards/languages_0001.jsonl
```

必须能 readback：

- profile public payload。
- shard page 1。
- page size 裁剪。
- next_page。

## 5. False-green 拒绝

以下情况直接判失败：

- 超预算却标记 ready。
- partial 没有 blockers。
- shard ref 不可读。
- public payload 泄露绝对路径。
- generated/vendor skip 没有统计。
- 真实项目没跑却写 accepted。
- 修改 V2.0-V2.38 上游 artifacts。

## 6. PRD 规格检视

Phase 116 只验收 V2.39 大型项目性能基线，不得声称完成多语言 AST/LSP、workflow/runtime、relationship chain、drawio semantic 或 token optimizer。
