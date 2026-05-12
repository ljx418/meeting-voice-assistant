# Quality Contract

更新时间：2026-05-12

## 定位

PhaseG8 固化 Quality Summary / Correction Plan 的当前公开契约和漂移护栏。PhaseG9 继续固化 Quality Feedback / Correction Rules / Review 的当前公开契约。PhaseG10 将现有 Quality HTTP feedback / rules / review 兼容入口迁移到 shared contract helper。PhaseG11 将 HTTP correction plan 兼容入口迁移到 shared contract helper。PhaseG12 固化 Quality CLI planned 入口迁移窗口。PhaseG13 开放 Quality CLI 只读 preview。PhaseG14 开放 Quality CLI 写入型命令。PhaseG15 提供 `knowledge quality ...` entrypoint-ready alias。PhaseG17 冻结 `knowledge` 顶层命令只包含 `quality`。PhaseG18 在该护栏上只开放 `knowledge query` 一个最小能力组 alias。PhaseG19 开放 `knowledge workspace list/describe` 只读 alias。PhaseG20 开放 `knowledge source list` 只读 alias。PhaseG21 开放 `knowledge build status` 只读 alias。PhaseG22 开放 `knowledge graph snapshot` 只读 alias。PhaseG23 开放 `knowledge trace source` 只读 alias。当前阶段不新增 MCP tool 或 HTTP route。

MCP 仍是默认主入口。HTTP `/api/v1/knowledge/quality/*` 是既有兼容入口。CLI `data_service quality` 当前已开放 Stage 2 只读 preview 和 Stage 3 写入型治理命令。PhaseG15 已提供 `knowledge_main` entrypoint-ready alias，供后续 console script `knowledge = data_service.__main__:knowledge_main` 绑定。PhaseG23 之后，`knowledge` 顶层只允许 `quality`、`query`、只读 `workspace`、只读 `source`、只读 `build`、只读 `graph snapshot` 与只读 `trace source`；本文档主要约束 quality 子树。

## 当前公开入口

| 能力 | MCP | HTTP 兼容入口 | CLI |
| --- | --- | --- | --- |
| Quality Summary | `knowledge_quality_summary` / `knowledge_quality_summary_v2` | 未开放 `/api/v1/knowledge/quality/summary` | `data_service quality summary` / `knowledge quality summary` |
| Correction Plan | `knowledge_correction_plan` / `knowledge_correction_plan_v2` | `/api/v1/knowledge/quality/corrections/plan` | `data_service quality correction-plan` / `knowledge quality correction-plan` |
| Quality Feedback | `knowledge_quality_feedback` / `knowledge_quality_feedback_v2` | `/api/v1/knowledge/quality/feedback`、`/api/v1/knowledge/quality/feedback/list` | `data_service quality feedback` / `feedback-list`；`knowledge quality feedback` / `feedback-list` |
| Correction Rules | `knowledge_correction_rules` / `knowledge_correction_rules_v2` | `/api/v1/knowledge/quality/corrections`、`/api/v1/knowledge/quality/corrections/build` | `data_service quality rules` / `rules-build`；`knowledge quality rules` / `rules-build` |
| Correction Rule Review | `knowledge_review_correction_rule` / `knowledge_review_correction_rule_v2` | `/api/v1/knowledge/quality/corrections/review` | `data_service quality review` / `knowledge quality review` |

## MCP Request Contract

### `knowledge_quality_summary`

```json
{
  "workspace_id": "workspace-id",
  "workspace": "/compat/workspace/path"
}
```

- `workspace_id` 是目标稳定主语义。
- `workspace` 是兼容 path 入口，保留给旧客户端和本地调试。
- 当前无 required field。
- 当前不接受 `limit`、`status`、`rebuild` 等额外业务参数。

### `knowledge_correction_plan`

```json
{
  "workspace_id": "workspace-id",
  "workspace": "/compat/workspace/path",
  "rebuild": false
}
```

- `workspace_id` 是目标稳定主语义。
- `workspace` 是兼容 path 入口。
- `rebuild` 是 boolean，默认 `false`；为 `true` 时重新从 approved correction rules 构建 plan。
- 当前无 required field。

### `knowledge_quality_feedback`

```json
{
  "workspace_id": "workspace-id",
  "workspace": "/compat/workspace/path",
  "target_type": "entity",
  "target_id": "entity-id",
  "action": "rename_suggest",
  "label": "Old Label",
  "suggested_value": "New Label",
  "reason": "Operator note",
  "metadata": {}
}
```

- required fields：`target_type`、`target_id`、`action`。
- `workspace_id` 是目标稳定主语义。
- `workspace` 是兼容 path 入口。
- `metadata` 必须是 object；未传时按空 object 处理。
- 当前支持的可规则化 action 包括 `rename_suggest`、`merge_suggest`、`mark_noise`、`needs_review`。其他 action 可作为 feedback 记录保留，但不会生成 correction rule。

### `knowledge_correction_rules`

```json
{
  "workspace_id": "workspace-id",
  "workspace": "/compat/workspace/path",
  "limit": 100,
  "status": "draft"
}
```

- `limit` 默认 `100`，MCP handler 边界为 `1..500`。
- `status` 可选，允许值为 `draft`、`approved`、`rejected`、`archived`、`revoked`。
- 当前无 required field。

### `knowledge_review_correction_rule`

```json
{
  "workspace_id": "workspace-id",
  "workspace": "/compat/workspace/path",
  "rule_id": "rule-id",
  "status": "approved",
  "reviewer": "operator",
  "note": "review note"
}
```

- required fields：`rule_id`、`status`。
- `status` 允许值为 `draft`、`approved`、`rejected`、`archived`、`revoked`。
- review 只更新治理规则状态，并刷新 approved correction plan；不改写原始 source 数据。

## MCP Response Contract

### `knowledge_quality_summary`

稳定顶层字段：

```json
{
  "workspace": "/compat/workspace/path",
  "quality": {},
  "quality_feedback": [],
  "quality_correction_rules": [],
  "quality_correction_plan": {}
}
```

稳定 quality 子字段：

- `quality.manual_feedback`
- `quality.correction_rules`
- `quality.correction_plan`

### `knowledge_correction_plan`

稳定顶层字段：

```json
{
  "schema_version": "1.0",
  "workspace": "/compat/workspace/path",
  "generated_at": "2026-05-11T00:00:00Z",
  "source_rule_count": 0,
  "actions": [],
  "summary": {},
  "notes": []
}
```

稳定 summary 子字段：

- `summary.action_count`
- `summary.action_counts`
- `summary.target_engine_counts`
- `summary.target_type_counts`
- `summary.impacted_action_count`
- `summary.impact_counts`

稳定 action 子字段：

- `action_id`
- `source_rule_id`
- `source_feedback_id`
- `target_type`
- `target_id`
- `action`
- `current_label`
- `proposed_value`
- `target_engines`
- `impact.summary`

### `knowledge_quality_feedback`

稳定顶层字段：

```json
{
  "feedback_id": "feedback-id",
  "created_at": "2026-05-11T00:00:00Z",
  "workspace": "/compat/workspace/path",
  "target_type": "entity",
  "target_id": "entity-id",
  "action": "rename_suggest",
  "label": "Old Label",
  "suggested_value": "New Label",
  "reason": "Operator note",
  "metadata": {}
}
```

### `knowledge_correction_rules`

稳定顶层字段：

```json
{
  "workspace": "/compat/workspace/path",
  "rules_path": "/debug/rules/path",
  "items": [],
  "total_count": 0,
  "filtered_count": 0,
  "summary": {},
  "generated_at": "2026-05-11T00:00:00Z",
  "schema_version": "1.0"
}
```

稳定 rule 子字段：

- `rule_id`
- `rule_type`
- `status`
- `target_type`
- `target_id`
- `current_label`
- `proposed_value`
- `reason`
- `source_feedback_id`
- `created_at`
- `metadata`

稳定 summary 子字段：

- `summary.rule_count`
- `summary.status_counts`
- `summary.rule_type_counts`
- `summary.target_type_counts`

### `knowledge_review_correction_rule`

稳定顶层字段：

```json
{
  "workspace": "/compat/workspace/path",
  "rules_path": "/debug/rules/path",
  "rule": {},
  "summary": {},
  "correction_plan": {}
}
```

稳定 correction_plan 子字段：

- `correction_plan.summary`
- `correction_plan.source_rule_count`

## PhaseG8 约束

- 不新增 MCP tool；`knowledge_quality_summary` 和 `knowledge_correction_plan` 继续复用现有 registry。
- 不新增 HTTP route；`/api/v1/knowledge/quality/summary` 不应提前开放。
- 不新增 CLI `quality` command。
- 不改变 `knowledge_quality_summary` 和 `knowledge_correction_plan` 的稳定字段集合。
- 后续如果开放目标 HTTP / CLI quality 入口，必须复用现有 MCP handler 或先抽取 shared contract helper，不能在 API / CLI 层重新组装 payload。

## PhaseG9 约束

- 不新增 MCP tool；`knowledge_quality_feedback`、`knowledge_correction_rules`、`knowledge_review_correction_rule` 继续复用现有 registry。
- 不新增 HTTP route；现有 `/api/v1/knowledge/quality/feedback`、`/feedback/list`、`/corrections`、`/corrections/build`、`/corrections/review` 保持兼容。
- 不新增 CLI `quality` command。
- 不改变 feedback / rules / review 的稳定字段集合。
- Review 必须保持 non-destructive governance 语义：只更新规则状态并刷新 correction plan，不重写 source data。

## PhaseG10 约束

- 不新增 MCP tool、HTTP route 或 CLI `quality` command。
- HTTP `/quality/feedback` 必须复用 `record_quality_feedback_payload`。
- HTTP `/quality/feedback/list` 必须复用 `quality_feedback_list_payload`。
- HTTP `/quality/corrections` 必须复用 `quality_correction_rules_payload`。
- HTTP `/quality/corrections/build` 必须复用 `quality_correction_rules_build_payload`。
- HTTP `/quality/corrections/review` 必须复用 `quality_correction_rule_review_payload`。
- API 层只保留 request parsing、workspace resolve 和 HTTP error mapping，不重新组装 feedback / rules / review payload。

## PhaseG11 约束

- 不新增 MCP tool、HTTP route 或 CLI `quality` command。
- HTTP `/quality/corrections/plan` 必须复用 `quality_correction_plan_payload`。
- API 层只保留 request parsing 和 workspace resolve，不直接调用 `service.build_quality_correction_plan()` 组装 HTTP response。
- `quality_correction_plan_payload` 当前保持 build 语义，与既有 HTTP `/quality/corrections/plan` 行为一致；不引入 `rebuild` 请求字段。

## PhaseG12 Quality CLI planned 迁移窗口

PhaseG12 时 `data_service` CLI 只有 `ingest`、`summary`、`distill`、`boundary`、`graphrag-execute`、`query`。PhaseG12 只固化目标 CLI 迁移窗口，不开放 `quality` 子命令。PhaseG13 已进入 Stage 2，只开放只读 CLI preview。

目标 CLI 命令形态：

```text
data_service quality summary --workspace-id research-vault
data_service quality correction-plan --workspace-id research-vault --rebuild
data_service quality feedback --workspace-id research-vault --target-type entity --target-id entity-1 --action rename_suggest --suggested-value "Canonical"
data_service quality feedback-list --workspace-id research-vault --target-type entity --limit 50
data_service quality rules --workspace-id research-vault --status draft --limit 50
data_service quality rules-build --workspace-id research-vault
data_service quality review --workspace-id research-vault --rule-id rule_123 --status approved --reviewer operator --note "accepted"
```

迁移窗口：

- Stage 1：已完成；CLI `quality` 不开放，MCP 和 HTTP 为 quality 能力入口。
- Stage 2：PhaseG13 已进入；开放只读 CLI preview，支持 `summary`、`correction-plan`、`feedback-list`、`rules`，并复用 `data_service.quality_contract` helper。
- Stage 3：PhaseG14 已进入；开放写入型 CLI command，包括 `feedback`、`rules-build`、`review`；必须保留 non-destructive governance 语义。
- Stage 4：PhaseG15 已进入；提供目标 `knowledge quality ...` entrypoint-ready alias；旧 `data_service quality ...` 继续作为兼容入口。

PhaseG12 约束：

- 不新增 MCP tool、HTTP route 或 CLI `quality` command。
- 不改变当前 `data_service` CLI 已开放命令集合。
- 未来 CLI `quality` 命令必须复用 `data_service.quality_contract` helper 或现有 MCP handler，不能在 CLI 层重新组装 payload。
- 写入型 CLI 命令必须显式复用现有 status enum、required fields 和 non-destructive governance 语义。

## PhaseG13 Quality CLI 只读 preview

PhaseG13 只开放 `data_service quality` 下的只读 preview 子命令，作为 PhaseG12 Stage 2 的最小实现。

已开放命令：

```text
data_service quality summary --workspace-id research-vault
data_service quality correction-plan --workspace-id research-vault --rebuild
data_service quality feedback-list --workspace-id research-vault --target-type entity --limit 50
data_service quality rules --workspace-id research-vault --status draft --limit 50
```

PhaseG13 约束：

- PhaseG13 开放只读 CLI preview，但不新增 MCP tool 或 HTTP route。
- 写入型 CLI command 在 PhaseG13 仍不开放：`feedback`、`rules-build`、`review` 保留到 Stage 3。
- CLI 层只做 argparse、workspace resolve 和 JSON 输出，不重新组装 quality payload。
- `summary` 必须复用 `quality_summary_payload`。
- `correction-plan` 必须复用 `quality_correction_plan_preview_payload`；默认只读已有 plan，传入 `--rebuild` 时才重建。
- `feedback-list` 必须复用 `quality_feedback_list_payload`。
- `rules` 必须复用 `quality_correction_rules_payload`，并复用现有 status enum。
- `--workspace-id` 是 `--workspace` 的兼容别名；当前仍解析为本地 workspace directory，目标 workspace registry 语义留到后续 `knowledge quality ...` alias 阶段。

## PhaseG14 Quality CLI 写入型命令

PhaseG14 开放 `data_service quality` 下的 Stage 3 写入型命令，作为现有 MCP/HTTP quality governance 的 CLI 兼容入口。

已开放命令：

```text
data_service quality feedback --workspace-id research-vault --target-type entity --target-id entity-1 --action rename_suggest --suggested-value "Canonical"
data_service quality rules-build --workspace-id research-vault
data_service quality review --workspace-id research-vault --rule-id rule_123 --status approved --reviewer operator --note "accepted"
```

PhaseG14 约束：

- PhaseG14 开放写入型 CLI command，但不新增 MCP tool 或 HTTP route。
- 写入型 CLI command 已开放：`feedback`、`rules-build`、`review`。
- `feedback` 必须复用 `record_quality_feedback_payload`，并保持 `target_type`、`target_id`、`action` 为 required。
- `rules-build` 必须复用 `quality_correction_rules_build_payload`。
- `review` 必须复用 `quality_correction_rule_review_payload`，并复用现有 status enum。
- 写入动作仍是 non-destructive governance：记录 feedback、生成可审核 correction rules、审核 rule 并刷新 approved correction plan；不直接改写原始 source。

## PhaseG15 knowledge quality alias

PhaseG15 不假设当前运行环境已经安装独立 `knowledge` 可执行文件，而是在代码层提供 entrypoint-ready alias：

```text
knowledge = data_service.__main__:knowledge_main
```

目标命令形态：

```text
knowledge quality summary --workspace-id research-vault
knowledge quality correction-plan --workspace-id research-vault --rebuild
knowledge quality feedback --workspace-id research-vault --target-type entity --target-id entity-1 --action rename_suggest --suggested-value "Canonical"
knowledge quality feedback-list --workspace-id research-vault --target-type entity --limit 50
knowledge quality rules --workspace-id research-vault --status draft --limit 50
knowledge quality rules-build --workspace-id research-vault
knowledge quality review --workspace-id research-vault --rule-id rule_123 --status approved --reviewer operator --note "accepted"
```

PhaseG15 约束：

- PhaseG15 提供 `knowledge_main` entrypoint-ready alias，但不新增 MCP tool 或 HTTP route。
- `knowledge_main` 必须复用 `data_service` CLI parser，仅切换 `prog` 为 `knowledge`。
- `knowledge quality ...` 和 `data_service quality ...` 必须共享同一套 `data_service.quality_contract` helper。
- PhaseG16 已新增 packaging 配置；`knowledge` console script 指向 `data_service.__main__:knowledge_main`。

## PhaseG17 knowledge 顶层公开面冻结

PhaseG17 修正并固化 `knowledge` console script 的公开面：当时 `knowledge` 顶层命令只允许 `quality`，避免因为复用完整 `data_service` parser 而隐式开放 `knowledge ingest/query/distill/boundary/graphrag-execute`。

PhaseG17 约束：

- `knowledge` 顶层命令只包含 `quality`。
- `data_service` 兼容 CLI 继续保留 `ingest`、`summary`、`distill`、`boundary`、`graphrag-execute`、`query`、`quality`。
- PhaseG18-G23 已按能力组逐步开放 query、workspace/source/build/graph/trace 的只读 alias；仍不得一次性开放 `knowledge distill/graph 扩展`。
- 后续新增 `knowledge workspace/source/build/graph/...` 必须按能力组单独设计、单独验收，并复用既有 MCP handler 或 shared helper。

## PhaseG18 knowledge query alias

PhaseG18 开放 `knowledge query`，作为第一个非 quality 的最小 alias 能力组：

```text
knowledge query PhaseG18 --workspace-id research-vault --mode hybrid --top-k 3
```

PhaseG18 约束：

- 不新增 MCP tool 或 HTTP route。
- `knowledge query` 必须复用 `run_query_contract`，不得在 CLI 层重新组装 query payload。
- `knowledge query` 与 `data_service query` 的响应字段集合保持一致：`mode`、`query`、`answer`、`hits`、`engine_payloads`。
- 不得一次性开放 `knowledge distill/graph 扩展`。
- 后续新增其他 `knowledge ...` alias 必须按能力组单独设计、单独验收。

## 漂移测试要求

- MCP registry 必须持续包含 `knowledge_quality_summary`、`knowledge_correction_plan` 及对应 V2 alias。
- `knowledge_quality_summary` input schema 只能声明 `workspace`、`workspace_id`。
- `knowledge_correction_plan` input schema 只能声明 `workspace`、`workspace_id`、`rebuild`。
- HTTP route 集合不得出现 `/quality/summary`。
- CLI parser 必须出现 `quality` 子命令，且包含 `summary`、`correction-plan`、`feedback-list`、`rules`、`feedback`、`rules-build`、`review`。
- `knowledge_main` 必须存在，并且 `_build_parser(prog="knowledge")` 的 `prog` 为 `knowledge`。
- packaging 配置必须声明 `knowledge = data_service.__main__:knowledge_main`。
- `_build_knowledge_parser()` 顶层 choices 当前必须严格等于 `{"quality", "query", "workspace", "source", "build", "graph", "trace"}`，且 `workspace` 子命令只允许 `create`、`list`、`describe`、`archive`，`source` 子命令只允许 `import`、`list`、`remove`，`build` 子命令只允许 `start`、`status`、`cancel`，`graph` 子命令只允许 `snapshot`，`trace` 子命令只允许 `source`，不得包含 `distill`、`session` 或 graph advanced 子命令。
- E2E 调用必须验证 quality summary 与 correction plan 的稳定顶层字段和核心子字段。
- `knowledge_quality_feedback` input schema 必须持续声明 `target_type`、`target_id`、`action` 为 required。
- `knowledge_correction_rules` input schema 必须持续把 `status` enum 限定为 `draft`、`approved`、`rejected`、`archived`、`revoked`。
- `knowledge_review_correction_rule` input schema 必须持续声明 `rule_id`、`status` 为 required。
- E2E 调用必须验证 feedback / rules / review 的稳定顶层字段和核心子字段。
- HTTP route tests 必须验证 feedback / rules / review 兼容入口调用 shared contract helper，且 CLI 写入型命令复用相同 helper。
- HTTP route tests 必须验证 `/quality/corrections/plan` 调用 shared contract helper，且 plan 稳定顶层字段保持不变。
- CLI migration drift tests 必须验证 `quality` 子命令只开放只读 preview，并验证本文档包含目标命令形态、Stage 1-4 迁移窗口和 shared helper 复用规则。
- CLI read-only preview tests 必须端到端调用 `summary`、`correction-plan`、`feedback-list`、`rules`，并验证四个命令均复用 `data_service.quality_contract` helper。
- CLI write command tests 必须端到端调用 `feedback`、`rules-build`、`review`，并验证三个命令均复用 `data_service.quality_contract` helper。
- alias tests 必须端到端调用 `knowledge_main(["quality", ...])`，并验证 alias 路径复用同一 quality helper。
- query alias tests 必须端到端调用 `knowledge_main(["query", ...])`，并验证 alias 路径复用 `run_query_contract`。
