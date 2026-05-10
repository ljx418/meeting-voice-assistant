# V3.0 Code Review Cleanup Checklist

文档状态：V3.0 CLOSEOUT REVIEW CHECKLIST。V2 清理检查文档已归档到 `docs/history/v2-phase-docs/architecture/code-review-cleanup-checklist_v2.md`。

## 1. Core / Gateway

- [ ] 新业务逻辑未写入 Core。
- [ ] Gateway 未新增业务专用旁路。
- [ ] Runtime 调用都经过 RuntimeAdapter。
- [ ] RPC method 遵守 JSON-RPC result/error 互斥。

## 2. Scope Isolation

- [ ] 新 records 写入包含 `app_id/project_id/workspace_id`。
- [ ] list/query 默认按 ScopeContext 过滤。
- [ ] namespace isolation tests 覆盖同名 session/job/artifact。

## 3. Pack / Connector

- [ ] 新 workflow 来自 Pack manifest。
- [x] PackAssemblyResult 返回 status、missing_dependencies、conflicts、blocked_reason、next_actions。
- [ ] Connector 通过 ConnectorRegistry 接入。
- [x] Connector descriptor 包含 trust_level、execution_mode、allowed_paths、allowed_commands、network_policy、secret_ref、app_scope。

## 4. Job / Artifact / Governance

- [ ] JobRecord 包含 scope、progress、failure_context、artifact_ids。
- [ ] ArtifactRecord 包含 scope、external_asset_uri、preview_uri、thumbnail_uri、parent_ids、metadata。
- [ ] 大文件、视频、音频、图片不能通过 `artifact.read` 全文读取。
- [ ] 高风险 tool/job/artifact persistence 经过 Policy / Approval / Trace。

## 5. Meeting / Knowledge

- [ ] Meeting MCP / FunASR MCP 不再硬编码路径。
- [ ] Meeting legacy facade 内部走 Pack workflow。
- [ ] Knowledge MCP 只调用 lifecycle/v2 tools。
- [ ] Knowledge workflow 不直接读写 data_service 内部目录。
