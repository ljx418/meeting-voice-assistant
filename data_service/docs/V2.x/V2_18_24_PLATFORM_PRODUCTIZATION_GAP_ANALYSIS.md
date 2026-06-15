# V2.18-V2.24 Gap Analysis：当前架构与目标架构差异

## 1. 当前优势

- 项目智能能力覆盖面广。
- MCP/HTTP/CLI 已有大量入口。
- Coding Agent actionability 和安全边界已具备。
- 大项目审计能力已能输出 structured blockers。
- 文档和验收链路完整。

## 2. 核心差距

| Gap | 当前状态 | 目标状态 | 阶段 |
| --- | --- | --- | --- |
| 用户入口分散 | 多个 HTML/JSON/report 分散 | 统一 Console | V2.18 |
| Artifact schema 不统一 | 跨阶段产物格式不完全一致 | Validator + envelope | V2.19 |
| MCP 工具难发现 | 工具数量多，调用顺序靠人工经验 | Tool Catalog + Workflow Guide | V2.20 |
| 构建偏全量 | 复用/失效规则不够显式 | Incremental Build Plan | V2.21 |
| Provider 插件不成熟 | optional provider 多为 unavailable | Provider SDK | V2.22 |
| 治理反馈未完全闭环 | 有反馈/规则基础，但体验不强 | feedback -> rule -> overlay -> revoke | V2.23 |
| CI 生产化不足 | 测试能跑，但 warning 和层级需整理 | 分层测试 + release gate | V2.24 |

## 3. 风险

### 风险 1：继续堆功能导致不可维护

应对：

- 优先做 schema、catalog、console、CI。
- 新能力必须挂到统一入口。

### 风险 2：Console 成为新事实源

应对：

- Console 只读 public payload。
- HTML 不得引入 artifact 外事实。

### 风险 3：增量构建误复用过期 artifact

应对：

- cache decision 必须有 source hash / snapshot diff / invalidation reason。

### 风险 4：Provider fake accepted

应对：

- health/config/execution 分离。
- optional unavailable 保持 structured unavailable。

### 风险 5：治理规则污染原始事实

应对：

- read-time overlay only。
- source artifact hash gate。

## 4. 审计建议

V2.18-V2.24 可以进入文档审计和后续分阶段开发计划，但每个阶段开发前必须产出 phase-specific 文档和 pre-implementation audit，不应一次性直接实现所有内容。
