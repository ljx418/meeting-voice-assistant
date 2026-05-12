# Data Service V1.6 Acceptance Plan

更新时间：2026-05-12

## Acceptance Standard

每个 V1.6 子阶段必须同时通过功能验收、公开面验收、契约验收、回归验收和文档一致性验收。

## Public Surface Acceptance

每个阶段都必须记录：

- MCP tool count before / after。
- CLI top-level commands before / after。
- HTTP routes before / after。
- target HTTP route allowlist before / after。
- new public surface, if any, must match the phase scope。

任何未在阶段计划中声明的 MCP tool、HTTP route 或 CLI command 都是 blocking issue。

## Contract Acceptance

检查项：

- MCP / CLI / HTTP / target HTTP payload consistency。
- envelope / error contract consistency。
- `artifact_ref` consistency。
- operation lifecycle consistency。
- stable external IDs only。
- debug/console-only internal path fields clearly marked non-contract。

## Regression Acceptance

每个实现阶段至少需要：

- focused tests for the changed capability group。
- API regression where HTTP is touched。
- MCP regression where MCP registry, handler or shared contract is touched。
- CLI parser regression where CLI is touched。
- combined data_service/API/MCP regression before phase acceptance。
- frontend `npm run build` and screenshot acceptance when `/knowledge` changes。
- drawio XML validation when diagrams change。

## Documentation Acceptance

每个阶段完成后必须同步：

- `README.md`
- `development-plan.md`
- `acceptance-plan.md`
- `current-vs-target-gap.md`
- `current-vs-target-gap.drawio`
- related contract / convergence plan

文档不得将 planned 能力描述为 implemented。文档必须持续使用 MCP-first local knowledge governance microservice 定位。

## Final V1.6 Acceptance

V1.6 最终验收必须确认：

- V1.5 compatibility routes retained。
- V1.6 newly opened surfaces match accepted phase reports。
- no hidden upper-layer application dependency。
- `/knowledge` remains service governance console。
- V1.6 docs and diagrams match actual implementation。
