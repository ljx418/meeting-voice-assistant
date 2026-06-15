# V2.37 User Experience Acceptance

## 1. 目标体验

V2.37 结束后，用户不应该只看到目录、文件数量、入口数量和简单枚举图，而应该能看到一个项目的“目标设计、当前实现、差异与风险”。

核心体验是：

```text
导入项目
  -> 读取项目 docs 和既有代码事实
  -> 生成目标架构模型
  -> 生成当前实现模型
  -> 对每条架构声明做 evidence-backed verification
  -> 输出可读 HTML 图文报告和 Agent Architecture Brief
```

## 2. 用户能做什么

### 2.1 维护者：快速看懂项目真实架构状态

用户打开报告后，应能在 5 分钟内回答：

- 项目 docs 宣称的目标架构是什么？
- 当前代码事实支持了哪些目标架构节点？
- 哪些目标设计没有代码证据？
- 哪些代码模块缺少文档描述？
- 哪些结论只是 weak / needs_review，不能直接当事实使用？

验收：

- 报告必须包含 `Target from Docs`、`Current from Code`、`Diff / Drift`、`Needs Review` 四个区块。
- 图必须原位渲染，不展示 Mermaid 源码。
- 每个 supported claim 必须可追踪到 document evidence 和 code evidence。

### 2.2 Coding Agent：减少重复读仓和 token 消耗

Coding Agent 在执行任务前，可以请求 Architecture Brief：

```text
任务：我要修改 HarnessOS workflow runtime 的调度逻辑。
输出：
- 相关目标架构声明。
- 当前实现候选模块。
- 已证实的入口/适配器/运行时节点。
- weak / unsupported 的风险点。
- 建议先读哪些文件，为什么。
```

验收：

- Brief 不得输出无证据的强建议。
- 每条 recommendation 必须包含 evidence refs 或 `needs_review`。
- 小 token budget 下可以删除低优先级建议，但不能保留建议后删除证据。

### 2.3 架构审计者：核查文档与代码是否一致

审计者可以查看 verification matrix：

```text
claim: "系统包含 workflow runtime plane"
document evidence: docs/design/...drawio cell 或 Markdown line
code evidence: runtime package / entrypoint / adapter artifact
status: supported | weakly_supported | unsupported | contradicted
```

验收：

- `supported` 必须有双边 evidence。
- `weakly_supported` 和 `unsupported` 必须在报告中可见，不能被汇总分数隐藏。
- `code_not_documented` 必须作为单独问题呈现。

### 2.4 新成员：把项目架构当作入门地图

新成员打开 HTML 报告，应能看到：

- 项目目标架构图。
- 当前实现模块图。
- 关键差异。
- 建议阅读顺序。
- 需要人工确认的架构区域。

验收：

- 报告必须有“推荐阅读路径”或等价 section。
- 每个推荐文件都必须来自 current implementation model 或 verification row。
- 不允许 renderer 自造不存在的节点、模块、关系。

## 3. 真实项目体验样例

### data_service

预期体验：

- 用户能看到 Project Intelligence / ResearchNotebook / governance / MCP / HTTP / CLI 的目标与当前实现差异。
- 用户能定位哪些 public contract 有真实 route/tool/command evidence。
- 用户能看到 V2.37 本身的 docs 是否被识别为 current target。

### HarnessOS

预期体验：

- 用户能看到 docs 中的 workflow、runtime、agent、adapter、headless plane 目标模型。
- 用户能看到代码事实中可支持这些目标的模块、配置、入口或 blocker。
- 用户能理解为什么某些架构节点是 `weakly_supported` 或 `unsupported`，而不是看到一张简单目录图。

### codexPat

预期体验：

- 用户能验证 V2.37 不依赖 HarnessOS 专用词。
- 如果项目 docs 较弱，系统应输出 document coverage gap，而不是伪造目标架构。

## 4. 用户验收门槛

V2.37 用户体验验收通过必须满足：

1. HTML 报告可读，且图原位渲染。
2. 报告四视图区分明确：target/current/diff/needs_review。
3. 至少 data_service、HarnessOS、codexPat 三个真实项目生成报告。
4. HarnessOS 报告必须解释 workflow/runtime/agent/adaptor claim 的支持状态。
5. 不允许 HarnessOS-only hardcode。
6. supported claim 缺 document evidence 或 code evidence 时验收失败。
7. Agent Brief 可以直接作为 Copilot 类 Agent 的任务前架构上下文。

## 5. 不接受的体验

- 只展示目录树、文件数、语言统计。
- 只列出 Mermaid 源码，不渲染成图。
- 把 docs 里的图复制成“代码架构图”。
- 把 token overlap 当作 implementation proof。
- 把 unsupported claim 隐藏在汇总评分后。
- 为了让 HarnessOS 看起来通过而写项目专用规则。
