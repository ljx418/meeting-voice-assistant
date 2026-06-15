# V2.37 Gap Analysis

## 1. 当前能力

V2.31-V2.36 已具备：

- snapshot / inventory / symbols / relationships / impact / reading pack / handoff。
- accepted relationship evidence floor。
- no-surface 大项目结构化 blocker。
- HTML/Mermaid 基础展示。

## 2. 关键 Gap

| Gap | 影响 | V2.37 对策 |
| --- | --- | --- |
| 架构图偏事实枚举 | 用户认为系统没有理解项目 | target/current/diff/needs_review 四视图 |
| docs 目标架构未充分利用 | HarnessOS 设计意图无法重塑 | Document Authority + Claim Graph |
| 文档和代码事实未强核查 | 设计图与实现偏差难判断 | Claim-to-Code Verification |
| 非 HTTP/MCP 项目入口弱 | workflow/runtime 项目无法解释 | Project Term Taxonomy + current model blocker |
| 报告可读性不足 | 人类审计成本高 | HTML 原位图、摘要、证据链接 |
| 容易 HarnessOS 特化 | 泛化能力下降 | no-hardcode gate + 多项目 E2E |

## 3. 不解决的 Gap

- 完整运行时拓扑。
- 完整调用图。
- 自动推断所有设计意图。
- 自动改文档或改代码。
- 生产环境动态 tracing。

## 4. 风险

### 风险 1：把文档声明当代码事实

应对：所有 supported 必须双边 evidence。

### 风险 2：把 token overlap 当强匹配

应对：token_overlap_only 只能 weakly_supported。

### 风险 3：HarnessOS 专用化

应对：项目词表只做配置；核心逻辑使用通用类型。

### 风险 4：HTML 图再度退化为源码展示

应对：验收必须检查页面无 Mermaid 源码块，图原位渲染。
