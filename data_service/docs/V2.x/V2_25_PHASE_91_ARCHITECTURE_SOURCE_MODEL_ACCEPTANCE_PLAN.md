# V2.25 Phase 91 验收计划：Architecture Source Model

## 1. 验收目标

确认 Phase 91 能在真实仓库上生成完整、可追踪、安全的 Architecture Source Model，为 Phase 92-96 提供可信输入。

## 2. 自动化测试

必须新增并通过：

```text
backend/tests/test_v2_25_architecture_source_model.py
```

测试覆盖：

- Markdown / drawio / code / config / test 分类。
- authority_role 分类。
- Markdown heading/list/fenced diagram source blocks。
- drawio cell extraction。
- repo-relative path。
- 无绝对路径泄露。
- source summary count 与 artifacts 一致。

## 3. 真实仓库 E2E

### data_service

必须满足：

- `architecture_sources.jsonl` 非空。
- `source_blocks.jsonl` 非空。
- `diagram_cells.jsonl` 若存在 drawio，必须非空；若没有 drawio，必须有 summary blocker。
- source types 至少覆盖 markdown、drawio 或 diagram、code、config、test。
- authority roles 至少覆盖 target、plan、acceptance、audit、implementation 中三类。

### HarnessOS

必须满足：

- 真实路径 `/Users/Zhuanz/Desktop/workspace/harnessOS` 存在。
- source model 非空。
- HarnessOS 设计文档、workflow/agent/runtime/governance 相关文档被登记或输出 blocker。
- drawio 或 diagram source 被登记；如果不存在，必须在 summary 中说明。
- 不得因为 HarnessOS 大项目复杂而 silent pass。

## 4. Artifact inspection

检查路径：

```text
workspace/assets/codebase/{codebase_id}/architecture/intent/sources/
  architecture_sources.jsonl
  diagram_cells.jsonl
  source_blocks.jsonl
  architecture_source_summary.json
```

断言：

- 所有 JSON/JSONL 可解析。
- 每条 source 有 `schema_version`、`source_id`、`source_type`、`path`、`authority_role`。
- 每条 block 有 locator。
- drawio cell 不含原始绝对路径。

## 5. PRD 规格检视

必须确认：

- Phase 91 只建立 source model，未过度实现 intent inference。
- 未把 diagram claim 写成 code fact。
- 未修改 V2.18-V2.24 已有 artifacts。
- 未新增不在计划内的 public API。

## 6. False-green 拒绝条件

以下任一出现即验收失败：

- 只用 mock 项目，不跑 data_service / HarnessOS。
- artifact 只存在 summary，不存在 source rows。
- public rows 泄露 `/Users/...` 或 `/private/tmp/...`。
- drawio cell extraction 为空但仓库实际存在 drawio 文件。
- HarnessOS 路径缺失却标记 passed。
- 把 runtime descriptor 标记为 runtime_observed。

## 7. 验收输出

验收通过后必须产出：

```text
docs/V2.x/V2_25_PHASE_91_ARCHITECTURE_SOURCE_MODEL_ACCEPTANCE_AUDIT_REPORT.md
```
