# harnessOS Target Architecture V2.0

## 1. 定位

V2.0 的正式目标架构是：

> Protocol-first Harness Core + OS-like Agent App Server + Domain Pack Platform

harnessOS 不再被定义为会议助手、CLI agent 或某个单一业务应用，而是一个本地优先、协议优先、可治理、可扩展、可迁移的 Agent Harness Core。会议、知识、投资、面试、AI 视频工作室等业务能力通过 Domain Pack 挂载；CLI、Web、Bot、Automation 通过统一协议访问 Core。

当前实现状态是 Core v1.5-E Runtime Adapter 收敛 MVP。V2.0 是目标形态，不代表当前代码已经完成 V2.0。

## 2. 采纳判断

`docs/design/V2.0/harnessos_architecture_master_spec.md` 质量总体较高，适合作为 V2.0 目标架构主干，原因如下：

- 它明确区分 Core、Protocol App Server、Runtime Adapter、Domain Pack、Connector/Tool Plane 和 Store Layer。
- 它坚持 Core 不写死业务逻辑，业务通过 Pack 接入，符合多项目迁移目标。
- 它把 Session、Thread、Turn、Item、Job、Artifact、Approval、Trace 作为一级对象，符合当前 Core v1.5 已建立的对象模型。
- 它把治理下沉到 turn、tool、job、artifact、retry/resume，而不是只做入口 preflight。
- 它把 Runtime Adapter 作为执行内核隔离层，和当前 Core v1.5-E 的 `RuntimeHandle` / `RuntimeAdapter` 方向一致。

## 3. 与 Core v1.5-E 的关系

Core v1.5-E 是 V2.0 的当前落地点，不是最终架构。

| 主题 | Core v1.5-E 当前状态 | V2.0 目标 |
| --- | --- | --- |
| 协议层 | Gateway RPC、SSE、stdio JSONL 可用；部分 Core 查询 RPC 已落地 | Core-native App Server，统一 session/thread/turn/item/job/artifact/approval/trace 方法与事件 |
| Runtime | `RuntimeHandle`、`SimpleRuntimeAdapter`、`OpenHarnessRuntimeAdapter` MVP | 完整 Runtime Adapter facade，隔离 OpenHarness/DeepAgents/SimpleRuntime 内部类型 |
| Store | `CoreSQLiteStore` 基础 CRUD；旧 JSON/JSONL stores 仍作为兼容运行源 | Store abstraction，local-file/sqlite/postgres 可替换 |
| Job | 同步 Job 记录 MVP | background Job Worker、progress、job.events、cancel/resume |
| Pack | meeting/knowledge active manifest；investment/interview/video stub | pack-owned workflow/skill/connector/policy/artifact assembly |
| Governance | turn preflight、tool policy guard、trace/approval/retry/secret MVP | turn/tool/job/artifact/retry 全链路 policy + approval + trace |
| Connector | Meeting MCP 作为真实连接器案例 | Connector Registry、health check、capability discovery、secret scope |
| SubAgent/Skill | 部分历史代码和 manifest 预留 | SubAgent Registry、Skill Registry、pack-owned specialist crew |

## 4. V2.0 目标分层

V2.0 采用六层结构：

1. Client / Gateway Layer：CLI、Web、Admin Console、Bot、Automation。
2. Protocol App Server Layer：JSON-RPC、SSE、stdio JSONL、Web Gateway / WS Proxy。
3. Harness Core Layer：Session/Thread/Turn/Item、Orchestrator、Router、Workflow、Policy、Approval、Retry、Trace、Secret、Job、Artifact。
4. Runtime Adapter Layer：OpenHarness、SimpleRuntime、未来 DeepAgents adapter。
5. Domain Pack Layer：Meeting、Knowledge、Investment、Interview、Video Studio。
6. Connector / Tool / Store Layer：MCP、native tools、filesystem/browser/data sources，以及 local-file/sqlite/postgres stores。

## 5. 当前设计缺口

V2.0 master spec 是总体蓝图，还缺以下可执行规格。后续实现前必须补齐：

- JSON-RPC method、event、error code、状态机与兼容策略未冻结。
- Pack manifest 仍缺加载优先级、版本兼容、冲突处理、启停机制和 policy bundle schema。
- Job Worker 缺 create/run/progress/events/cancel/resume/failure_context 的状态机定义。
- 治理链路缺执行顺序：turn preflight、tool invocation、job execution、artifact persistence、retry/resume 之间的 policy/approval/trace 绑定规则。
- Runtime Adapter 目标接口与当前 MVP 不完全一致，需要渐进扩展，不能一次性推翻现有 `RuntimeHandle`。
- 多项目/多租户只是字段预留，仍缺 user/tenant 权限隔离、artifact 访问边界、connector secret scope 和 pack scope。
- 顶层目录重组风险较高，短期不做大搬迁，先用 adapter/service facade 收敛边界。

## 6. 下一阶段落地顺序

V2.0 的下一阶段不新增业务功能，优先硬化平台边界：

1. Core-native session/event store：把旧 Gateway snapshot/events 降级为兼容层，统一 Core Store 查询和写入。
2. Background Job Worker：让长任务从同步 workflow 记录升级为可查询、可取消、可恢复的 job。
3. Adapter-level governance injection：把 tool metadata、policy evaluator、approval checker 注入 Runtime Adapter 默认路径。
4. Pack Assembly MVP：让 pack manifest 驱动 workflow、connector、skill、policy bundle 的注册。
5. Connector Registry MVP：把 Meeting MCP 从硬编码配置升级为 connector record、health 和 capability discovery。

## 7. 验收约束

每次阶段开发完成后必须同步：

- `CURRENT-STATUS.md`
- `current-vs-target-gap.md`
- `current-vs-target-gap.drawio`
- `test-acceptance-plan.md`
- `acceptance-test-cases.md`

每次阶段验收继续使用 `/Users/Zhuanz/Desktop/workspace/音频资料` 下真实音频验证 Meeting Pack 不回归，并在验收后清理外部会议产物和本地 `.harnessos` 验收记录。
