# V2.16 用户体验与用户验收场景

## 1. 文档目标

本文件说明 V2.16 阶段结束后，用户实际可以怎样使用本项目、能看到什么内容、如何判断体验是否达标。

V2.16 的体验目标不是“生成更多 JSON”，而是让用户把本项目当作一个本地 Coding Agent 审查台：

```text
导入项目
  -> 理解项目状态
  -> 输入开发任务
  -> 查看影响范围、证据、风险和 blocker
  -> 运行受控 runtime profile
  -> 查看大项目架构抽象
  -> 查看 patch preview、diff、rollback
  -> 决定是否人工批准下一步高风险动作
```

## 2. 阶段结束后的目标体验

### 2.1 用户能直接理解项目

用户打开 Workbench v2 后，应能在一个页面里看到：

- 项目是什么。
- 当前识别到的公开能力有哪些。
- 关键入口、模块、测试、文档在哪里。
- 哪些证据来自代码。
- 哪些结论只是文档声明。
- 哪些结论需要人工 review。
- 哪些 blocker 阻止系统继续自动化。

体验判定：

> 用户不需要先读 raw JSON，也不需要手动 grep 全仓，就能形成第一轮项目判断。

### 2.2 用户能判断 provider 是否真的可用

用户查看 provider 能力矩阵时，应能区分：

- provider 只是系统已知。
- provider 已配置。
- provider 有 execution adapter。
- provider 当前可执行。
- provider 缺凭据。
- provider 不支持执行。
- provider 被安全策略阻止。

体验判定：

> 用户不会把“health-known”误以为“真实执行成功”。

### 2.3 用户能让 Coding Agent 做改动前准备

用户输入一个开发任务后，应能看到：

- 任务解释。
- 影响范围。
- 候选修改文件。
- 相关 public surface。
- 相关 symbol / reference / test。
- patch options。
- validation profiles。
- rollback 建议。
- 风险和 blocker。

体验判定：

> Coding Agent 可以基于这些信息开始读代码和规划修改，但不能绕过证据或安全门禁。

### 2.4 用户能安全运行验证

用户选择 runtime profile 后，应能看到：

- 该 profile 会运行什么命令模板。
- 允许哪些参数。
- 是否需要审批。
- 是否禁用网络。
- 是否会写源码。
- 运行结果是 passed、failed、timeout、blocked 还是 profile_not_approved。
- 脱敏后的 stdout / stderr 摘要。

体验判定：

> 系统只运行受控 profile，不接受任意命令。

### 2.5 用户能审计大项目

对 HarnessOS 或同类大项目，系统应能展示：

- 文档声明的目标架构。
- 代码事实能支撑的当前结构。
- pattern evidence。
- accepted / needs_review / blocked 分类。
- blocker 具体原因。
- 下一步需要补什么证据、文档或 runtime profile。

体验判定：

> 系统可以解释为什么某些架构结论不能 accepted，而不是输出漂亮但不可验证的架构图。

### 2.6 用户能审查 patch preview

用户选择 patch plan 后，应能看到：

- patch preview 状态。
- 会涉及哪些文件。
- diff 内容。
- rollback 文件范围。
- validation profile。
- 是否允许 apply。
- 如果不允许，为什么 blocked。

体验判定：

> preview 阶段不修改源码；没有人工高风险审批，apply 必须 blocked。

## 3. 用户验收场景 A：陌生项目接手

### 3.1 背景

一个新开发者或外部 Coding Agent 接手 `data_service`，希望先理解项目，而不是立即改代码。

### 3.2 用户操作

```text
1. 导入 repo。
2. 构建已有项目事实。
3. 构建 V2.16 provider matrix。
4. 构建 Workbench v2。
5. 打开 HTML 报告。
```

### 3.3 用户应该看到

页面上至少包含：

- 项目摘要。
- 当前能力地图。
- HTTP/MCP/CLI 入口摘要。
- provider 能力矩阵。
- evidence coverage。
- 风险分层视图。
- blocker board。
- 下一步建议。

### 3.4 验收样例

用户问题：

```text
这个项目的代码资产导入能力在哪里？我应该从哪些文件开始看？
```

系统应回答或展示：

- 相关 capability。
- 相关 HTTP/MCP/CLI surface。
- handler / symbol / file。
- evidence link 或 line range。
- 如果证据不足，显示 `needs_review`。

通过标准：

- 人类 5 分钟内能理解项目主入口和主要风险。
- 页面不是 raw JSON 堆叠。
- 关键结论有 evidence 或 `needs_review`。

## 4. 用户验收场景 B：Coding Agent 改动准备

### 4.1 背景

用户准备让 Coding Agent 实现一个小功能：

```text
给 codebase import 增加路径校验，并同步 HTTP/MCP/CLI 行为。
```

### 4.2 用户操作

```text
1. 输入任务文本。
2. 生成 impact analysis。
3. 生成 task-to-edit plan。
4. 生成 safe patch plan。
5. 生成 runtime profile 建议。
6. 打开 Workbench v2。
```

### 4.3 用户应该看到

- 候选修改文件。
- 相关 public surface。
- 相关 tests。
- 相关 provider facts。
- patch options。
- validation profile。
- blocker。
- next actions。

### 4.4 验收样例

系统对候选修改建议必须说明：

```text
建议修改文件 A，因为它包含 handler X。
建议检查文件 B，因为它包含 MCP tool registry。
建议运行 profile pytest_file，参数是 tests/test_x.py。
```

通过标准：

- 每条建议都有 evidence 或 `needs_review`。
- low confidence 不得显示成 ready。
- runtime 失败必须显示失败原因。
- 不能把 import/reference 写成 runtime call。

## 5. 用户验收场景 C：维护者审查改动风险

### 5.1 背景

维护者想知道某个 patch plan 是否可以继续推进。

### 5.2 用户操作

```text
1. 选择 patch plan。
2. 查看 risk lanes。
3. 查看 runtime profile result。
4. 查看 blocker board。
5. 查看 rollback plan。
```

### 5.3 用户应该看到

- 改动涉及哪些 public surface。
- 是否影响 HTTP/MCP/CLI 对齐。
- 哪些测试应该运行。
- runtime profile 是 passed / failed / timeout / blocked。
- 哪些 blocker 必须处理。

### 5.4 验收样例

如果 runtime profile 失败，页面必须显示：

```text
状态：failed
失败 profile：pytest_file
失败原因：测试断言失败或环境缺失
下一步：查看 redacted stderr，或改用 structured blocker
```

通过标准：

- failed / timeout 不能伪装 passed。
- blocker 不得隐藏。
- redacted logs 不泄露绝对路径、secret、raw traceback。

## 6. 用户验收场景 D：大项目架构审计

### 6.1 背景

用户希望审计 HarnessOS 或类似大型项目，判断目标架构与当前代码事实之间的差异。

### 6.2 用户操作

```text
1. 导入大项目。
2. 构建文档声明和代码事实。
3. 运行 Large-Project Abstraction Advisor。
4. 打开大项目审计报告。
```

### 6.3 用户应该看到

- 文档声明的目标架构。
- 代码事实能支撑的当前架构。
- pattern evidence。
- accepted / needs_review / blocked 分类。
- blocker 原因。
- 缺失证据。
- 下一步建议。

### 6.4 验收样例

如果系统无法 accepted 某个架构 claim，应输出：

```text
状态：blocked
原因：只有文档声明，没有代码入口或 symbol evidence
缺失证据：entrypoint / registry / handler / runtime profile
下一步：补充入口映射或运行受控 profile
```

通过标准：

- 不允许 HarnessOS-only hardcoding。
- document claim 不能伪装成 code fact。
- blocker 必须比“识别失败”更具体。
- accepted claim 必须有代码证据。

## 7. 用户验收场景 E：Patch Sandbox Preview

### 7.1 背景

用户想让系统根据 safe patch plan 生成补丁预览，但还不想真正改代码。

### 7.2 用户操作

```text
1. 选择 safe patch plan。
2. 生成 patch sandbox preview。
3. 查看 diff。
4. 查看 rollback。
5. 查看 validation profile。
6. 决定是否审批 apply。
```

### 7.3 用户应该看到

- preview id。
- preview 状态。
- 修改文件列表。
- diff artifact。
- rollback artifact。
- validation profiles。
- approval state。
- blocked reason。

### 7.4 验收样例

未审批时必须显示：

```text
apply_status: blocked
reason: human approval required
mutates_source: false
rollback_ready: true
```

通过标准：

- preview 不修改源码。
- source hash before == source hash after。
- rollback 覆盖 previewed files。
- 没有人工审批，apply 必须 blocked。
- 默认不做 git commit / push / reset / restore。

## 8. 用户验收场景 F：审计交付

### 8.1 背景

用户要把 V2.16 阶段交给另一个 ChatGPT 或人工审计者复核。

### 8.2 用户操作

```text
1. 生成 closure report。
2. 更新 coverage matrix。
3. 更新 real repo E2E matrix。
4. 导出 Workbench / Mermaid / artifact refs。
5. 把文档包交给审计者。
```

### 8.3 用户应该看到

- 每个 PRD 条目的状态。
- 每个 accepted 条目的测试命令。
- 每个 accepted 条目的 artifact path。
- 真实仓 E2E 结果。
- HTTP/MCP/CLI parity。
- redaction 结果。
- false-green audit。
- open findings。

### 8.4 验收样例

Coverage matrix 中每个 accepted row 必须包含：

```text
status: accepted
test_command: ...
artifact_path: ...
data_service_e2e: passed
large_project_e2e: passed | structured_blocker
audit_report: ...
```

通过标准：

- 审计者可以只读文档判断阶段是否完成。
- planning baseline 不得伪装 implementation closure。
- pending row 不得通过 Phase 82。

## 9. 用户体验失败条件

以下情况即使测试通过，也不得通过用户体验验收：

- 页面仍然主要依赖 raw JSON。
- 用户看不到 blocker。
- 用户看不到 evidence 或 `needs_review`。
- 用户不知道 provider 为什么不可用。
- 用户不知道 runtime 为什么 blocked。
- 用户不知道 patch 是否真的修改了源码。
- 大项目报告只给结论，不解释证据缺口。
- 图表中出现 artifact 中不存在的新事实。

## 10. 最终用户体验判定

V2.16 通过用户体验验收，当且仅当：

1. 用户可以通过页面理解项目状态。
2. 用户可以通过 provider matrix 理解能力边界。
3. 用户可以通过 Workbench v2 审查开发任务。
4. 用户可以通过 runtime profile 安全验证。
5. 用户可以通过大项目报告理解架构差异和 blocker。
6. 用户可以通过 patch sandbox 查看 diff、rollback 和审批状态。
7. 用户可以通过 closure 文档把阶段交给第三方审计。
