# ResearchNotebook V1.5-A AI Provider Contract Report

日期：2026-05-27

## 执行状态

PASS。

## 当前结果

已完成 V1.5-A provider contract 最小实现：

- data_service 新增 OpenAI-compatible provider contract。
- provider 路径固定为 MiniMax compatible config。
- 新增 `GET /api/workspaces/-/ai-provider/health`。
- 新增 ResearchNotebook smoke script：`npm run smoke:v1.5-a-provider`。
- 新增后端 focused tests。

## 阻塞原因

Provider 路径已经确认：

- `DATA_SERVICE_AI_PROVIDER=openai_compatible`
- `DATA_SERVICE_AI_PROVIDER_NAME=minimax`

用户已在本机提供：

- `DATA_SERVICE_AI_BASE_URL`
- `DATA_SERVICE_AI_MODEL`
- `DATA_SERVICE_AI_API_KEY`

真实模型调用已通过：

- provider：OpenAI-compatible MiniMax。
- model：`MiniMax-M2.7`。
- smoke：`npm run smoke:v1.5-a-provider` PASS。
- provider fixture 已脱敏，不保存 API key、Authorization header 或模型文本内容。

## 验收结果

| 项目 | 状态 |
| --- | --- |
| provider health probe route | IMPLEMENTED |
| smoke:v1.5-a-provider | PASS |
| 真实模型调用 | PASS |
| missing_api_key 稳定错误 | TESTED |
| missing_provider_config 稳定错误 | TESTED |
| auth_failed 稳定错误 | NOT_RUN |
| timeout 稳定错误 | NOT_RUN |
| rate_limited 稳定错误 | REAL_PROVIDER_CONFIRMED |
| API key 脱敏检查 | TESTED_BY_UNIT |
| smoke fixture 脱敏 | PASS |
| 后端 provider focused tests | PASS |
| npm run check | PASS |

## 风险评估

- 规格漂移风险：LOW。
- 虚假验收风险：MEDIUM。

原因：V1.5-A 只证明真实 provider 可用，不证明 AI Guide / Studio / QA 输出质量。后续阶段仍必须逐项验收，不能把 provider PASS 当成 AI quality PASS。

## 下一步

进入 V1.5-B AI Notebook Guide 计划审计。

进入 V1.5-B 前必须补强：

- Overview 至少 1 条 evidence_ref。
- 每个 Key Topic 至少 1 条 evidence_ref。
- Suggested Questions 至少 3 个。
- `generation_metadata` 记录 provider、provider_name、model、prompt_version、evidence_ref_count、fallback_mode。
- provider 失败不得伪装为 AI Guide ready。
