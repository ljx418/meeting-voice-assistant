# V2.39 Phase 116 Development Plan：大型项目性能优化

## 1. 目标

Phase 116 在现有 V2.6 architecture scale profile 基础上补齐 V2.39 所需的大型项目性能基线：

- scan budget policy。
- scale profile v2.39 字段。
- artifact shard。
- paginated readback index。
- partial / blocked / ready 状态。
- structured blocker。

## 2. 实现边界

- 复用 `backend/data_service/code_assets/architecture/scale_profile.py`。
- 复用 `ArchitectureService.build_scale_profile` 和现有 HTTP/MCP/CLI scale profile 入口。
- 不新增 legacy 大文件核心逻辑。
- 不修改 V2.0-V2.38 上游 artifact。
- 不扫描目标项目绝对路径到 public payload。

## 3. 开发动作

1. 扩展 scale profile builder：
   - 增加 `schema_version = v2.39_scale`。
   - 增加 `budget`、`status`、`blockers`、`partial`、`generated_or_vendor_count`、`large_file_count`。
   - 生成 `scan_budget_report`。

2. 增加 shard writer：
   - 生成 `architecture/scale/scan_shards/files_0001.jsonl`。
   - 生成 `architecture/scale/scan_shards/languages_0001.jsonl`。
   - 生成 `paginated_readback_index.json`。

3. 增加 readback：
   - 支持 page、page_size。
   - 返回 total、items、next_page。

4. 增加 public payload：
   - 展示 budget、status、blockers、shard counts、pagination refs。
   - 不返回绝对路径。

5. 增加 focused tests：
   - ready / partial / blocked。
   - shard readback。
   - budget exceeded。
   - redaction。

## 4. 不做内容

- 不做完整多语言 AST/LSP。
- 不做 workflow/runtime extractor。
- 不做 relationship chain v3。
- 不做 drawio 语义解析。

这些属于 Phase 117-122。
