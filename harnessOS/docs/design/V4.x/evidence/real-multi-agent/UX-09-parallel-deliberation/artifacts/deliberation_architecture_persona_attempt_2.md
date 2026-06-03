# 罗马广场讨论工作流 — 架构审查工位产物

## 目标理解

本工位聚焦于 **系统边界** 与 **演进风险** 两个维度，对"HarnessOS 产品形态选择"提供架构视角的分析判断。

核心问题本质是一个 **前端能力内聚度 vs. 解耦灵活性** 的架构权衡：

| 选项 | 核心定义 | 架构边界特征 |
|------|----------|---------------|
| 选项A | 完整 Web 低代码 Studio | 单体式前端，边界内聚，强调 WYSIWYG 体验完整性 |
| 选项B | Headless Core + 多 Head 工作流 | 前后分离，后端纯逻辑，前端通过标准化协议外延 |

---

## 输入引用

> **背景约束 1**：V4.1 已证明本地 Markdown 文件夹总结工作流  
> **背景约束 2**：V4.2 已证明 Headless interaction 和 dev/local controlled runtime  
> **背景约束 3**：V4.3 已证明串行视频工作流的 AgentDescriptor 和工位产物  
> **缺失能力**：项目仍不能声明 Agent executor、production external app support gap 或 full multi-Agent orchestration gap

这些约束揭示了一个关键的 **架构信号**：当前项目的核心能力验证集中在**后端逻辑层**，而前端展示层经历了多次迭代但尚未收敛到稳定形态。

---

## 关键输出

### 维度一：系统边界分析

**架构主张：选择选项B（Headless Core + 多 Head）**

理由如下：

```
┌─────────────────────────────────────────────────────────────┐
│  当前架构现状                                               │
├─────────────────────────────────────────────────────────────┤
│  ✓ 后端逻辑已解耦 (AgentDescriptor, 工位产物抽象)           │
│  ✓ 运行控制已外置 (dev/local controlled runtime)          │
│  ✗ 前端形态尚未收敛 (Studio/TUI/Drawio/Report 并行探索)   │
├─────────────────────────────────────────────────────────────┤
│  边界最优策略：将前端差异视为 Core 的 "多个 Display Head"  │
│  → 让 Core 保持 "Headless"，通过标准化 Display Protocol   │
│    连接不同的 View 实现                                    │
└─────────────────────────────────────────────────────────────┘
```

**核心论点**：当前 V4.x 系列已验证后端 Core 的 Headless 特性，若继续投入完整 Web Studio，等同于将前端展示层与核心逻辑层绑定，形成新的单体耦合。这会模糊系统边界，削弱 V4.2 已建立的运行时可控性优势。

### 维度二：演进风险评估

| 风险项 | 选项A风险 | 选项B风险 |
|--------|-----------|-----------|
| **能力演进路线** | Studio 功能膨胀导致 Core 边界模糊，多 Agent 编排能力被拖慢 | 需要投资 Display Protocol，但协议一旦稳定，扩展成本下降 |
| **工程资源瓶颈** | Web Studio 需要完整的 UX/可视化工程团队 | 各 Head 可独立迭代，借用现有生态工具（TUI/Drawio/HTML）|
| **外部生态集成** | 封闭于单一 WebView，难以对接第三方 App | Headless Protocol 可支持外部 App 通过标准接口接入 |
| **V4.4 目标达成** | 与 "external app support" 目标冲突 | 天然对齐 "production external app support gap" |

**风险量化结论**：选项A 的风险集中度高（单点失败），且与项目明确缺失的能力存在冲突；选项B 的风险分散但可通过协议设计规避。

---

## 质量风险

### 识别到的架构质量问题

1. **Protocol 完整性缺失**
   - 当前 Heads（TUI/Drawio/HTML/Web Console）的 Display Protocol 尚未标准化
   - 若迁移到选项B，投资需先补足 Protocol 定义，否则陷入下一个锁定循环

2. **多 Head 一致性治理**
   - 多个 Head 可能各自实现差异化的交互语义
   - 需要引入统一的 AgentState 契约层来保证行为一致性

3. **DevEx vs ProdEx 的边界模糊**
   - Headless Core 的初衷是 dev/local controlled runtime
   - 从 TUI/Drawio 演进到 Production Heads 时，需确保运行时安全边界不模糊

### 风险缓解建议

- 将 Display Protocol 纳入 V4.4 的核心里程碑，而非附属探索
- 建立 Agent Contract Schema 作为所有 Head 的共享契约
- 在 Headless Core 层抽象出 Layered Runtime（DevLayer / ProdLayer）以隔离风险

---

## 下一工位建议

### 传递给 Orchestrator 的归因要点

1. **架构立场优先**：建议采用选项B，核心依据是 V4.2 已验证的 Headless 架构应作为系统边界的锚点，不应因为前端探索而回退耦合。

2. **依赖关系**：Display Protocol 标准化是选项B成立的前提