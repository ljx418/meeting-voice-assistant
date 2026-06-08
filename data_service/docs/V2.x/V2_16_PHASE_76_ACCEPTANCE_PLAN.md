# V2.16 Phase 76 验收计划：Provider Capability Registry

## 1. 验收目标

验证 Phase 76 是否真实建立 provider 能力边界，并防止以下虚假通过：

- provider health 名称被当作 execution-ready。
- optional provider 未配置却被标记 accepted。
- AST mandatory provider 缺失仍通过。
- public payload 泄露绝对路径或 secret。
- HTTP 通过但 MCP / CLI 不一致。

## 2. 必测场景

### 场景 A：Service 真实构建

输入真实 codebase fixture，调用 service build：

- `capability_registry.json` 存在。
- `decision_records.jsonl` 存在。
- `schema_version == v2.16`。
- `summary.provider_count > 0`。
- `python_ast` provider 为 mandatory、configured、execution_supported、available。
- optional provider 状态不能是 accepted fake。

### 场景 B：HTTP / MCP / CLI parity

通过三端分别 build/read provider registry，比较：

- `schema_version`
- `workspace_id`
- `codebase_id`
- `snapshot_id`
- `summary`
- provider ids
- artifact refs count
- warnings / unresolved count

### 场景 C：负向 provider contract

已知但无 execution adapter 的 provider 必须满足：

- `execution_supported == false`
- `status in unavailable | unsupported`
- `error.code in PROVIDER_UNSUPPORTED | PROVIDER_NOT_CONFIGURED`
- 不得 fallback 到 AST provider 并声明成功。

### 场景 D：安全输出

序列化 public payload 后不得包含：

- 当前 repo 绝对路径。
- workspace 绝对路径。
- `api_key`、`token`、`Authorization`、`secret`。
- raw traceback。

### 场景 E：回归保护

至少运行：

```text
backend/tests/test_v2_11_coding_agent_actionability.py
backend/tests/test_v2_12_safe_patch_planning.py
backend/tests/test_v2_13_15_coding_agent_remaining.py
backend/tests/test_public_surface_guard.py
```

## 3. 真实数据验收

本阶段优先使用现有真实 fixture 仓库流程，同时至少对当前 data_service 仓库执行一次本地 service-level 构建检查。若 sandbox 限制导致完整真实仓写入无法执行，必须在审计报告中明确标记为 environment-limited，不能声明完整 E2E accepted。

## 4. PRD 规格检视

验收报告必须回答：

- 是否只完成 Phase 76。
- 是否错误声明 Phase 77-82 能力。
- 是否存在 provider fake accepted。
- 是否污染 source registry 或旧 V2 artifacts。
- 是否产生新的高风险流程需要人工确认。

## 5. 失败处理

出现以下情况必须打回开发计划：

- AST provider 不可用。
- optional provider 被误标 accepted。
- 三端稳定字段不一致。
- public payload 泄露路径或 secret。
- V2.11-V2.15 回归失败且无法证明与本阶段无关。
