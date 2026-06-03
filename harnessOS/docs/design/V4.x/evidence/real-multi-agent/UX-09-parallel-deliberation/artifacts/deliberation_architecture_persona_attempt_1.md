# 架构审查工位产物

> 来源：平行罗马广场讨论工作流  
> 工位：架构审查  
> 产出时间：2024 Q1

---

## 目标理解

**核心议题**：HarnessOS 技术栈演进路径的二选一决策

| 选项 | 路径描述 |
|------|----------|
| 方案 A | 完整 Web 低代码 Studio（重资产投入） |
| 方案 B | Headless Core + TUI/Drawio/HTML Report/Thin Web Console（多端解耦） |

**本工位职责**：从系统边界清晰度和长期演进风险两个维度提供评审意见，标记架构耦合点和潜在技术债务。

---

## 关键输出

### 1. 系统边界评估

| 维度 | 方案 A (Web Studio) | 方案 B (Headless + Multi-Head) |
|------|---------------------|--------------------------------|
| **核心依赖** | 强绑定浏览器渲染引擎 | 核心运行时与协议层解耦 |
| **边界模糊度** | 高——Studio 与 Runtime 职责交织 | 低——Core 只负责执行 descriptor，多 head 各司其职 |
| **集成成本** | 新增 external app 需穿透 Studio 层 | 新 head 通过标准协议接入，风险隔离 |

### 2. 演进风险雷达

```
风险项                              方案A    方案B
─────────────────────────────────────────────────────
Web Runtime 兼容性维护               🔴高     🟢低
多端能力同步演进难度                 🔴高     🟡中
External App 接入门槛                🔴高     🟢低
技术债务累积速度                   🔴高     🟡中
Agent Orchestration 解耦度          🔴中     🟢高
```

### 3. 关键断言

- **方案 A 的核心风险**：V4.1–V4.3 验证的能力（Markdown 本地工作流、Headless interaction、串行视频工位）将被 Web Studio 吞没，失去已验证路径的品牌独立性。
- **方案 B 的架构优势**：Headless Core 作为纯执行层（符合 V4.2 的 dev/local controlled runtime 定位），各 head 作为可替换的消费端，符合开放封闭原则。
- **边界冲突点**：若选择方案 A，需要明确 Studio 是否承载 Agent descriptor 编辑能力——这与 V4.3 已验证的"工位产物"概念存在领域重叠。

---

## 输入引用

基于讨论输入中的事实锚点：

1. **V4.1 已证明**：本地 Markdown 文件夹总结工作流 → *意味着文件协议层已稳定*
2. **V4.2 已证明**：Headless interaction 和 dev/local controlled runtime → *意味着 Core 层已具备独立运行能力*
3. **V4.3 已证明**：串行视频工作流的 AgentDescriptor 和工位产物 → *意味着 descriptor 规范已沉淀*
4. **缺失项**：无 production external app support gap、无 full multi-Agent orchestration → *这是当前核心差距*

**推断**：从 V4.1→V4.3 的演进本身即展示了"Core 解耦 + 多端消费"的路径成功，方案 B 是该路径的自然延伸。

---

## 质量风险

### 当前阶段风险（选择方案 A 时）

| 风险类别 | 描述 | 影响范围 |
|----------|------|----------|
| **边界漂移** | Studio 同时承担 editor + renderer + executor 职责，内部模块边界模糊 | 后续维护成本指数增长 |
| **验证中断** | 放弃已验证的多 head 路径，从头建设完整的 Web IDE 能力（包含 canvas、拖拽、属性面板等） | 2–3 个迭代周期内无法交付 external app 支持 |
| **外部依赖** | 重度依赖浏览器 API（如 WebRTC、WebGL）实现低代码特性 | 跨平台能力受限，无法平滑扩展到 mobile/embedded 场景 |
| **技术锁死** | 若选定 Web Studio，后续发现 external app 接入需求时，改造代价 > 新建 | 项目可能陷入"凑合用"状态 |

### 风险缓解建议

- 如短期内必须保留 UI 可视化能力，可通过*渐进式路径*：保留 Headless Core 作为主路径，通过 Drawio/HTML Report 提供轻量可视反馈，而非 построить 全功能 Studio。
- Thin Web Console 定位应严格限制为 *monitoring/debugging* 而非 *authoring*，避免重蹈方案 A 的边界膨胀覆辙。

---

## 下一工位建议

| 工位 | 建议内容 |
|------|----------|
| **产品价值** | 评估 Headless Core 路径对 ISV / Enterprise 客户的价值（API-first、可嵌入性）与 Web Studio 的终端用户易用性之间的权衡 |
| **工程架构** | 产出具象化的 Core 架构图，标注各模块职责边界，量化外部 app 支持的开发工作量 estimate |
| **风险治理** | 补充方案 A 与方案 B 在安全合规、数据隔离、multi-tenancy