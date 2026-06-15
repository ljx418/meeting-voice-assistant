# V2.18 Phase 84 Development Plan：Product Console & Report UX

## 1. 阶段目标

Phase 84 是 V2.18-V2.24 平台产品化路线图的第一个实质开发阶段，目标是把当前分散的项目智能产物收敛成一个可读、可操作、可审计的 Platform Console。

本阶段只实现：

```text
Project Intelligence Console payload
Project Intelligence Console HTML view
HTTP / MCP / CLI read/build entrypoints
真实 data_service repo E2E
```

本阶段不实现：

- V2.19 artifact validator 全量体系。
- V2.20 MCP Tool Catalog。
- V2.21 Incremental Build。
- V2.22 Provider Plugin SDK。
- V2.23 Governance Feedback Loop。
- V2.24 CI Readiness Gate。

## 2. 输入产物

Phase 84 消费已有产物，不重新解释事实源：

- codebase registry。
- latest snapshot。
- public surface / symbols / evidence。
- architecture reports and human reports。
- context packs。
- runtime profiles / runtime runs。
- patch preview / patch plan。
- large-project advisor。

如果某个输入产物缺失，Console 必须显示 `missing` / `needs_build` / `blocked`，不得伪造 ready。

## 3. 输出产物

建议落盘路径：

```text
workspace/assets/codebase/{codebase_id}/platform/console/
  platform_console.json
  views/platform_console.html
```

最小 payload：

```json
{
  "schema_version": "v2.18",
  "artifact_type": "platform_console",
  "workspace_id": "string",
  "codebase_id": "string",
  "snapshot_id": "string",
  "artifact_id": "platform_console:{codebase_id}:{snapshot_id}",
  "status": "ready | needs_review | blocked",
  "summary": {
    "project_name": "string",
    "latest_snapshot_id": "string",
    "top_next_actions": []
  },
  "panels": [],
  "source_artifact_refs": [],
  "evidence_refs": [],
  "warnings": [],
  "needs_review": [],
  "view_refs": []
}
```

## 4. Console 面板

Phase 84 至少包含：

1. Overview：项目名、snapshot、artifact readiness。
2. Evidence：证据覆盖、缺失证据、line-level status。
3. Architecture：架构报告、文档/代码对齐、人类报告链接。
4. Agent：Context Pack、impact analysis、task plan。
5. Runtime：runtime profile 和最新运行结果。
6. Patch：patch plan / preview / apply blocked 状态。
7. Next Actions：推荐下一步工具或构建动作。

## 5. 实现边界

- Console 只消费已存在 artifact 和 public payload。
- Console 不在前端或 renderer 中推断新事实。
- Console 不隐藏 `needs_review`、`blocked`、`unresolved`。
- HTML 必须 escape 用户/文档/路径文本。
- HTML 不得包含本机绝对路径、secret、raw traceback。
- HTTP/MCP/CLI 入口只做薄 wrapper。

## 6. 代码落点建议

```text
backend/data_service/code_assets/platform/
  __init__.py
  console.py
  persistence.py
  renderer_html.py

backend/app/api/v1/code_assets_platform.py
backend/data_service/mcp_code_platform_tools.py
backend/data_service/cli_code_platform.py
```

如果为了减少路由注册改动，也可以先挂载到现有 code_assets router，但核心逻辑必须在 `code_assets/platform/*`。

## 7. 自动化测试

新增测试建议：

```text
backend/tests/test_v2_18_platform_console.py
```

覆盖：

- build console from real/minimal codebase artifacts。
- readback payload。
- HTML contains required sections。
- HTML does not include unpersisted fake fact。
- blocker / missing artifact visible。
- public payload redaction。

## 8. 真实仓库 E2E

必须使用当前真实 `data_service` repo：

1. 创建临时 workspace。
2. 导入当前 repo。
3. 生成 snapshot。
4. 构建或读取可用 V2 artifacts。
5. 构建 platform console。
6. 读取 JSON 和 HTML。
7. 验证 no-unpersisted-fact、blocker visible、redaction。

## 9. 完成定义

Phase 84 完成必须满足：

- Console artifact 落盘。
- Console HTML 落盘。
- HTTP/MCP/CLI 至少有 build/read 或 read 能力。
- 自动化测试通过。
- 真实 data_service E2E 通过。
- PRD/spec/false-green 审计通过。
