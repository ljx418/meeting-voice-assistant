# ResearchNotebook V1.5-A AI Provider Contract Plan

日期：2026-05-27

## 阶段目标

冻结真实 AI provider 合同，证明后端可以真实调用模型，并为 V1.5-B/C/D 的 AI Guide、Studio 和引用问答质量验收提供可靠基础。

## Entry Gate

Provider 路径已确认：

- 使用 OpenAI-compatible 接口接入 MiniMax。
- 用户可提供 MiniMax API key。
- base URL 和 model 不写死在代码中，由本机环境变量提供。

进入 PASS 前必须满足：

1. `DATA_SERVICE_AI_PROVIDER=openai_compatible`。
2. `DATA_SERVICE_AI_PROVIDER_NAME=minimax`。
3. `DATA_SERVICE_AI_BASE_URL` 已配置。
4. `DATA_SERVICE_AI_MODEL` 已配置。
5. `DATA_SERVICE_AI_API_KEY` 已配置。
6. provider health probe 能完成真实模型调用。

如果缺少配置或真实模型调用失败，本阶段保持 BLOCKED。

## 计划实现

- data_service 增加 AI provider adapter。
- 定义 provider config：
  - provider
  - provider_name
  - model
  - base_url
  - timeout_ms
  - max_tokens
  - temperature
  - api_key 来源
- 增加 `GET /api/workspaces/-/ai-provider/health` provider health probe。
- 增加真实模型 smoke。
- 定义稳定错误：
  - missing_provider_config
  - missing_api_key
  - auth_failed
  - provider_timeout
  - provider_unavailable
  - rate_limited
  - model_not_found
  - response_schema_mismatch
- 确认 deterministic fallback 只能作为 UX fallback，不可作为 AI quality pass。

## 验收标准

- provider health probe PASS。
- 真实模型调用 PASS。
- 缺少 API key 返回稳定错误。
- 缺少 base URL / model / provider 返回稳定错误。
- 超时返回稳定错误。
- fixtures / docs / logs 不包含 API key。
- smoke fixture 保存到 `fixtures/real/v1_5/ai-provider/`，且只包含脱敏结果。
- `npm run check` PASS。
- 后端 provider focused tests PASS。

## PRD 规格检视

PRD 指定 AI 驱动研究助手，并在技术栈中提到 Claude API。当前项目采用 OpenAI-compatible MiniMax 作为实际 provider 路径。V1.5-A 必须证明真实 AI provider 可用，否则后续阶段不能声明 AI Guide / Studio quality ready。

## 风险评估

当前预估：

- 规格漂移风险：MEDIUM，provider 路径已确认，但真实 smoke 未通过。
- 虚假验收风险：HIGH，直到真实 provider smoke 通过。

## 审计意见

允许执行 V1.5-A provider contract。禁止进入 V1.5-B/C/D/E，直到 MiniMax 真实调用 smoke PASS。
