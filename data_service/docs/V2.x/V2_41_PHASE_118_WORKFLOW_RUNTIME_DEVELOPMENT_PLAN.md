# V2.41 Phase 118 Workflow / Runtime Extractor Development Plan

## 1. 阶段目标

Phase 118 的目标是在 V2.39 scale profile 和 V2.40 language provider facts 之上，建立泛化的 workflow / runtime / entrypoint candidate extractor。

本阶段只输出 candidate facts，不输出 production runtime topology，不声明完整执行链路。

## 2. 输入

- V2.0 repo snapshot `files.jsonl`
- V2.39 scale profile / shard readback
- V2.40 language provider status / symbol facts / reference facts
- 项目 profile / taxonomy 中的 workflow patterns（如果存在）
- 真实项目：
  - `/Users/Zhuanz/Desktop/workspace/data_service`
  - `/Users/Zhuanz/Desktop/workspace/harnessOS`
  - `/Users/Zhuanz/Desktop/workspace/codexPat`

## 3. 输出 Artifacts

落盘目录：

```text
workspace/assets/codebase/{codebase_id}/architecture/v2_41/
```

文件：

```text
workflow_candidates.jsonl
runtime_adapter_candidates.jsonl
entrypoint_candidates.jsonl
workflow_runtime_summary.json
```

## 4. Candidate 类型

必须支持：

- `workflow_manifest`
- `pipeline_config`
- `agent_registry`
- `runtime_adapter`
- `cli_entrypoint`
- `tui_entrypoint`
- `console_entrypoint`
- `mcp_tool_registry`
- `http_route_registry`

每条 candidate 必须包含：

- `schema_version = v2.41_workflow_runtime`
- `workspace_id`
- `codebase_id`
- `snapshot_id`
- `candidate_id`
- `candidate_type`
- `label`
- `path`
- `line_range`
- `determinism`
- `confidence`
- `extractor`
- `evidence_refs`
- `needs_review`

## 5. 实现计划

1. 新增 `backend/data_service/code_assets/architecture/workflow_runtime_v2.py`。
2. 从 snapshot files 中读取配置、脚本、Python/TS/JS 入口文件。
3. 实现确定性 extractor：
   - GitHub Actions / CI manifests
   - Docker / compose / package scripts
   - Python `argparse` / Typer / Click hints
   - FastAPI route registry hints
   - MCP tool registry hints
4. 实现启发式 extractor：
   - agent / workflow / runtime / adapter 命名文件
   - TUI / console / terminal 入口文件
   - profile/taxonomy pattern 命中
5. 接入 `ArchitectureService`。
6. 暴露 HTTP/MCP/CLI：
   - HTTP `POST /architecture/workflow-runtime/build`
   - HTTP `GET /architecture/workflow-runtime`
   - MCP `knowledge_code_architecture_workflow_runtime_build`
   - MCP `knowledge_code_architecture_workflow_runtime`
   - CLI `knowledge code architecture workflow-runtime-build`
   - CLI `knowledge code architecture workflow-runtime`

## 6. 架构边界

- 不输出 production runtime topology。
- 不输出 full call graph。
- 不输出 data flow / control flow / type inference。
- candidate 不等于 accepted runtime fact。
- HarnessOS 只能作为真实回归样例，不得在通用 extractor 中硬编码 HarnessOS path、术语或目录。

## 7. 进入实现前审计项

- Phase 116 / 117 acceptance audit 均存在。
- V2.40 language provider regression 通过。
- 三个真实项目路径存在或 structured unavailable。
- 没有 open fatal / major 文档风险。
