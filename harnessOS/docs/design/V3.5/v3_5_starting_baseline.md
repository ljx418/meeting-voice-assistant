# V3.5 Starting Baseline

文档状态：V3.5 starting baseline。  
来源：V3.5 Readiness Audit 与当前 `docs/design/V3.5/` 规划文档。

## 1. Current Planning Conclusion

V3.5 当前处于 **Application Adaptation Layer 规划阶段**，可以带约束启动 dev/local-first 实施。

当前阶段的重点不是继续描述上一阶段平台建设，而是把外部业务 App 接入 harnessOS 的必要边界定义清楚：

- protocol schema registry
- error registry
- local capability token
- native EventSource / fetch stream
- SDK default method surface
- BFF template
- Pack / Connector template
- Embed contract
- reference app example

## 2. Usable Platform Baseline

V3.5 可以假定以下平台能力可用：

| 能力 | V3.5 使用方式 |
| --- | --- |
| ScopeContext | SDK/BFF/EventSource 必须显式传递 `app_id/project_id/workspace_id`。 |
| Gateway JSON-RPC | SDK 和 BFF 通过协议入口调用，不直接访问 Core Store。 |
| Pack Assembly | Pack template 以 `pack.list` / `pack.get` 作为发现和验收入口。 |
| Connector Registry | Connector template 以 `connector.health` 作为发现和健康入口。 |
| Job / Artifact / Trace | UI 和 SDK 可以消费 job progress、artifact metadata/lineage、trace debug 信息。 |
| Approval | V3.5 需要新增统一 `approval.respond`，内部可兼容现有 approve/reject 路径。 |

## 3. Current V3.5 Missing Contracts

以下是进入正式外部 App 接入前必须补齐的 V3.5 合同：

- `events.subscribe` protocol method。
- `GET /v1/events/subscribe` native EventSource / fetch stream。
- `approval.respond` protocol method 和幂等语义。
- method/event/error schema registry。
- local capability token。
- REST run / stream scope support。
- SDK/BFF legacy/debug API blacklist。

## 4. V3.5 Boundary

V3.5 不做：

- Core 重构。
- 业务 reference path 重迁移。
- 完整 Workflow Studio。
- 完整 AgentTalkWindow。
- sibling service 开发。

V3.5 的完成证明应来自一个非业务特权路径的 reference app：通过 SDK + BFF + hooks + templates 接入，不修改 Core。
