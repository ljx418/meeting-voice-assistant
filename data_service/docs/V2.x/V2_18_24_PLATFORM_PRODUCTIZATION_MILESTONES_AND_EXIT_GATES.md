# V2.18-V2.24 里程碑与出门条件

## 1. 里程碑

| 里程碑 | 阶段 | 目标状态 |
| --- | --- | --- |
| M1 | V2.18 | 用户通过一个 Console 页面理解项目状态和下一步动作。 |
| M2 | V2.19 | 主要 artifacts 拥有统一 schema、validator 和 public contract。 |
| M3 | V2.20 | 外部 Agent 可通过 Tool Catalog 获得推荐 MCP 调用链。 |
| M4 | V2.21 | 大项目重复构建支持 diff-driven impact plan 和 cache decision。 |
| M5 | V2.22 | Provider 插件边界明确，optional provider 不再模糊。 |
| M6 | V2.23 | 治理反馈可转成规则并 read-time overlay 生效。 |
| M7 | V2.24 | 测试、CI、安全、发布门禁完成生产化收口。 |

## 2. 每阶段出门门槛

### V2.18

- Console view 可生成。
- HTML 安全检查通过。
- blocker / needs_review 可见。
- 不新增事实源。

### V2.19

- Validator 覆盖主要 artifact families。
- Public envelope 一致。
- Schema invalid artifact 不能 accepted。

### V2.20

- Tool Catalog 覆盖所有 MCP tools。
- Goal-based guide 返回稳定调用链。
- 不推荐 deprecated / missing tool。

### V2.21

- Snapshot diff 可读取。
- Build impact plan 可解释。
- cache reuse / invalidation 有证据。

### V2.22

- Provider SDK 可用。
- AST mandatory baseline 通过。
- optional provider unavailable 不 fake accepted。

### V2.23

- Feedback target resolver 严格。
- Rule approve / revoke 生效。
- 原始 artifact hash 不变。

### V2.24

- 测试分层完成。
- Warning budget 建立。
- Security/redaction gate 通过。
- Release readiness report 生成。

## 3. 全局停止条件

出现以下情况必须停止并重新规划：

- Console 隐藏 blocker 或 unresolved。
- Artifact validator 自动修正事实而非报告错误。
- Tool guide 推荐不存在或未配置工具。
- Incremental build 静默跳过失败。
- Provider unavailable 被标记 accepted。
- Governance rule 改写 source artifact。
- CI 为了通过而跳过真实 repo E2E。

## 4. 最终完成定义

V2.18-V2.24 可以宣布完成，当且仅当：

```text
用户能看懂；
Agent 能调用；
产物能校验；
构建能增量；
provider 能插拔；
反馈能治理；
测试能守住。
```
