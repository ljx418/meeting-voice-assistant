# V2.30 Phase 96B 预实施审计报告：Architecture Intent 公共合同

阶段：V2.30 / Phase 96B
审计结论：通过，可以进入实现。

## 1. PRD 偏差检查

当前 V2.25-V2.30 coverage matrix 明确记录：

```text
Public HTTP/MCP/CLI contracts = not_implemented
```

本阶段正是对该缺口进行补齐，不扩大 PRD 范围，不重新定义 Phase 91-96 artifact 语义。

## 2. 架构边界检查

允许新增：

- `backend/data_service/code_assets/architecture_intent/service.py`
- `backend/data_service/mcp_code_architecture_intent_tools.py`
- `backend/data_service/cli_code_architecture_intent.py`
- `backend/app/api/v1/code_assets_architecture_intent.py`
- focused tests。

允许小范围修改：

- `backend/app/api/__init__.py`
- `backend/data_service/mcp_code_tools.py`
- `backend/data_service/cli_code.py`

禁止修改：

- `backend/app/api/v1/data_service.py`
- `backend/data_service/service.py`

## 3. 虚假验收风险

| 风险 | 审计要求 |
| --- | --- |
| 只测 HTTP，不测 MCP/CLI | 三端 parity 为硬门槛 |
| 只测 mock repo | 必须跑 data_service，HarnessOS 可读时必须跑 HarnessOS |
| 公共 payload 泄露绝对路径 | redaction check 为硬门槛 |
| governance 修改原始 artifact | hash gate 为硬门槛 |
| 未实现却改 coverage 为 accepted | 验收审计前不得修改 accepted 状态 |

## 4. 进入实现条件

- 开发计划、验收计划、预实施审计已落盘。
- 无 fatal / major 文档偏差。
- 本阶段只补公共合同，不修改已验收 artifact 语义。
