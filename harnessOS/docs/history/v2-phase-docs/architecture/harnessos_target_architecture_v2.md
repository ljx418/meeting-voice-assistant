# harnessOS Target Architecture V2.0

## 1. 定位

V2.0 的正式目标架构是：

> Protocol-first Harness Core + OS-like Agent App Server + Domain Pack Platform

harnessOS 不再被定义为会议助手、CLI agent 或某个单一业务应用，而是一个本地优先、协议优先、可治理、可扩展、可迁移的 Agent Harness Core。会议、知识、投资、面试、AI 视频工作室等业务能力通过 Domain Pack 挂载；CLI、Web、Bot、Automation 通过统一协议访问 Core。

当前事实基线是 **Baseline v1.5-E**，当前主验收阶段已经完成 **Phase 5-D Cross-domain MCP Workflow Stabilization 集成 MVP**。Phase 4-B2 的 ComfyUI / render manifest 相关代码只作为延期 scaffold 保留。V2.0 是目标形态，不代表当前代码已经完成 V2.0 产品化能力。

## 2. 采纳判断

`docs/design/V2.0/harnessos_architecture_master_spec_v2.md` 质量总体较高，适合作为 V2.0 目标架构主干，原因如下：

- 它明确区分 Client/Gateway、Protocol App Server、Harness Core、Runtime Adapter、Domain Pack、Connector/Tool/Store Plane。
- 它坚持 Core 不写死业务逻辑，业务通过 Pack 接入，符合多项目迁移目标。
- 它把 Session、Thread、Turn、Item、Job、Artifact、Approval、Trace 作为一级对象，符合当前 Core v1.5 已建立的对象模型。
- 它把治理下沉到 turn、tool、job、artifact、retry/resume，而不是只做入口 preflight。
- 它把 Runtime Adapter 作为执行内核隔离层，和当前 Core v1.5-E 的 `RuntimeHandle` / `RuntimeAdapter` 方向一致。

## 3. 与 Baseline v1.5-E / 当前 Meeting 验收线的关系

Baseline v1.5-E 是当前产品/架构事实基线，Phase 4-B1 Meeting artifact lineage 是当前用户态主验收线。Phase 4-B2 ComfyUI 相关内容是延期保留的远程 Connector scaffold，不是当前验收主线。

| 主题 | 当前事实基线 | V2.0 目标 |
| --- | --- | --- |
| 协议层 | Gateway RPC、SSE、stdio JSONL 可用；部分 Core 查询 RPC 已落地 | Core-native App Server，统一 session/thread/turn/item/job/artifact/approval/trace 方法与事件 |
| Runtime | `RuntimeHandle`、`SimpleRuntimeAdapter`、`OpenHarnessRuntimeAdapter`、adapter-level governance injection MVP | 完整 Runtime Adapter facade，隔离 OpenHarness/DeepAgents/SimpleRuntime 内部类型 |
| Store | `CoreSQLiteStore` 基础 CRUD；`session.list/read/events/transcript` 已 Core records 优先，旧 JSON/JSONL 作为兼容回退 | Store abstraction，local-file/sqlite/postgres 可替换 |
| Job | 本地 in-process worker、job events、failure_context、cancel 终态语义已完成 MVP | 长任务统一进入 Job Service，未来可扩展 progress、resume 和外部 worker |
| Pack | Pack Visibility & Manifest MVP；meeting/knowledge/video active manifest；knowledge/video workflow 已迁入对应 pack；Meeting artifact lineage 可查询；video asset/render manifest 只作为延期 scaffold 回归；investment/interview stub | DomainPack 2.0：pack-owned workflow templates / agents / skills / connector contracts / policy bundles / artifact schemas |
| Governance | turn preflight、tool policy guard、trace/approval/retry/secret MVP | turn/tool/job/artifact/retry 全链路 policy + approval + trace |
| Connector | Meeting MCP 作为当前真实连接器验收案例；Remote ComfyUI 已进入 connector descriptor；data_service_mcp 与 funasr_mcp 已具备 gated stdio execution；Meeting -> Knowledge 真实跨域验收已通过 | Connector Registry、health check、capability discovery、secret scope；后续补 connector 超时、取消、retryable failure、server interrupted recovery 与远程执行 |
| SubAgent/Skill | 部分历史代码和 manifest 预留；下一阶段先做 Pack-owned Agent registry metadata | SubAgent Registry、Skill Registry、pack-owned specialist crew |

## 3.1 已冻结架构决策摘要

- 协议优先：CLI / Web / Bot / Automation 统一走协议层。
- Core 不承载具体业务逻辑，新业务必须通过 Pack 接入。
- Runtime 必须通过 Adapter 使用，不能直接暴露 OpenHarness 内部对象。
- SQLite 是当前主存储收敛方向，legacy JSON/JSONL 仅作兼容与导入。
- 高风险动作必须进入 Policy / Approval / Trace / Retry。
- 长任务默认进入 Job Service，重要结果默认 Artifact 化。
- Gateway 不承载业务 workflow，只负责 transport、auth、serialization 和 stream proxy。

## 4. V2.0 目标分层

V2.0 采用六大平面。旧 L1-L5 五层目标图已废弃，不再作为正式目标架构口径。

1. Client / Gateway Plane：CLI、Web、Admin Console、Bot、Automation。
2. Protocol App Server Plane：JSON-RPC、SSE、stdio JSONL、Web Gateway / WS Proxy。
3. Harness Core Plane：Session/Thread/Turn/Item、Orchestrator、Router、Workflow、Policy、Approval、Retry、Trace、Secret、Job、Artifact。
4. Runtime Adapter Plane：OpenHarness、SimpleRuntime、未来 DeepAgents adapter。
5. Domain Pack Plane：Meeting、Knowledge、Investment、Interview、Video Studio；DomainPack 2.0 承载 Typed DAG workflow templates、Pack-owned agents、skills、connector contracts、policy bundles、artifact schemas、memory scopes 和 evaluation rules。
6. Connector / Tool / Store Plane：MCP、native tools、filesystem/browser/data sources，以及 local-file/sqlite/postgres stores。

## 5. 当前设计缺口

V2.0 master spec 是总体蓝图，还缺以下可执行规格。后续实现前必须补齐：

- JSON-RPC method、event、error code、状态机与兼容策略未冻结。
- Pack manifest 仍缺加载优先级、版本兼容、冲突处理、启停机制和 policy bundle schema。
- Job Worker 已具备本地 in-process MVP；仍缺 progress/resume/external worker 的状态机定义。
- 治理链路缺执行顺序：turn preflight、tool invocation、job execution、artifact persistence、retry/resume 之间的 policy/approval/trace 绑定规则。
- Runtime Adapter 目标接口与当前 MVP 不完全一致，需要渐进扩展，不能一次性推翻现有 `RuntimeHandle`。
- 多项目/多租户只是字段预留，仍缺 user/tenant 权限隔离、artifact 访问边界、connector secret scope 和 pack scope。
- 顶层目录重组风险较高，短期不做大搬迁，先用 adapter/service facade 收敛边界。

## 6. 下一阶段落地顺序

V2.0 已从 Meeting artifact lineage 验收线转入协议、治理、Pack 平台和跨域 MCP 工作流硬化：

1. Phase 4-C Core-native RPC Router：冻结 method registry、capability registry、compat alias、event contract 和 error code。
2. Phase 4-D Tool-level Approval Automation：工具命中高风险策略时自动创建 approval request，并可通过 approval + retry 续跑。
3. Phase 5-A DomainPack 2.0 Assembly Kernel / Knowledge-primary Connector Stub：让 pack manifest 驱动 Typed DAG workflow templates、Pack-owned agents、connector contracts、skills、policy bundle 和 artifact schema 装配；`pack.list/get` 必须展示 DAG、agents、skill refs、policy bundle refs、connector refs、artifact schema、assembly status、missing dependencies 和 blocked/degraded reason；`pack.agents`、`agent.list`、`agent.get` 提供 Pack-owned Agent 查询；Knowledge Pack 采用 `data_service_mcp` Contract + Connector Stub，真实 MCP client 已在 Phase 5-C 通过 gated stdio execution 落地。
4. Phase 5-B Memory & Session Intelligence：强化 Harness Core 内部记忆、摘要、检索与会话管理能力。
5. Phase 5-C Connector Execution Runtime：补齐 connector job execution、submit/poll/cancel/collect、health、artifact lineage 和 data_service_mcp gated stdio execution。
6. Phase 5-D Cross-domain MCP Workflow Stabilization：已补齐 FunASR MCP 真实调用、Meeting workflow 转写接入和 Meeting -> Knowledge 跨域端到端编排；当前是集成 MVP，仍需补产品化入口、超时、取消、retryable failure 和运维可观测性。
7. Phase 6 Productization / Open Source / Commercial Readiness：冻结协议版本、扩展开发体验、发布流程与基础治理边界。

## 7. 验收约束

每次阶段开发完成后必须同步：

- `CURRENT-STATUS_v2.md`
- `current-vs-target-gap_v2.md`
- `current-vs-target-gap_v2.drawio`
- `test-acceptance-plan_v2.md`
- `acceptance-test-cases_v2.md`

团队标准验收样本目录约定为 `fixtures/audio_samples/`，标准验收脚本约定为 `scripts/e2e_meeting_validation.sh`。在仓库提供标准 fixture 前，可继续使用本机真实音频做阶段验收，但个人路径只能作为 local validation evidence，不得写成团队基线。

每次阶段验收必须验证 Meeting Pack 真实音频链路不回归，并在验收后清理外部会议产物和本地 `.harnessos` 验收记录。
