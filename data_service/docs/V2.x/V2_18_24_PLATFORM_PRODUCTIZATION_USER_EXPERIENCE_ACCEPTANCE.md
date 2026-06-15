# V2.18-V2.24 用户体验验收场景

## 1. 体验目标

本阶段结束后，用户不应该再把 `data_service` 看成一堆分散的 artifact 和工具，而应看到一个本地项目智能平台：

```text
用户能看懂项目；
Agent 能找到工具；
维护者能治理输出；
大项目能增量刷新；
CI 能守住契约。
```

## 2. 场景 A：项目维护者打开 Console

### 用户目标

快速知道项目当前状态。

### 用户操作

```text
1. 导入项目。
2. 打开 Platform Console。
3. 查看 Overview / Evidence / Architecture / Agent / Runtime / Patch Preview。
```

### 用户应该看到

- 项目摘要。
- 当前 snapshot。
- 公开入口。
- 主要 blocker。
- 证据覆盖。
- 下一步建议。

### 验收标准

- 不需要打开 raw JSON。
- blocker 和 needs_review 清晰可见。
- 每个关键结论可追踪 source artifact。

## 3. 场景 B：外部 Agent 选择 MCP 工具链

### 用户目标

让 Agent 知道下一步该调用什么工具。

### 用户操作

```text
goal = coding_task_preparation
```

### 用户应该看到

- 推荐调用链。
- 每个工具的输入。
- 前置条件。
- 输出 artifact。
- 失败恢复建议。

### 验收标准

- 不推荐不存在或未配置工具。
- 调用链能从当前 registry 生成。
- 失败时返回 next_actions。

## 4. 场景 C：大项目小改动后增量刷新

### 用户目标

修改少量文件后快速刷新项目智能。

### 用户操作

```text
1. 生成 snapshot A。
2. 修改一个 fixture 文件。
3. 生成 snapshot B。
4. 请求 incremental build plan。
```

### 用户应该看到

- changed files。
- reused artifacts。
- refreshed artifacts。
- invalidated artifacts。
- full rebuild reason（如适用）。

### 验收标准

- changed file 不丢失。
- cache decision 有 reason。
- 不能静默跳过失败。

## 5. 场景 D：Provider 能力判断

### 用户目标

知道某个语义 provider 是否真的可执行。

### 用户操作

```text
读取 provider capabilities。
```

### 用户应该看到

- health_known。
- configured。
- execution_supported。
- status。
- unavailable reason。

### 验收标准

- health-known 不等于 execution-ready。
- optional unavailable 不得 accepted。
- AST baseline 必须 ready。

## 6. 场景 E：治理反馈闭环

### 用户目标

纠正一条错误 finding 或 context recommendation。

### 用户操作

```text
1. 对 target 提 feedback。
2. 生成 correction rule。
3. 审核 approve。
4. 读取 report/context。
5. revoke rule。
```

### 用户应该看到

- approved 后 read output 有 applied_rules。
- revoke 后 applied_rules 消失。
- 原始 artifact hash 不变。

### 验收标准

- missing target 被拒绝。
- overlay 是 read-time，不改写源 artifact。

## 7. 场景 F：发布前检查

### 用户目标

确认当前版本可以发布或进入下一阶段。

### 用户操作

```text
运行 production readiness gate。
```

### 用户应该看到

- unit / contract / artifact / frontend / e2e 分层结果。
- warning budget。
- redaction gate。
- release readiness conclusion。

### 验收标准

- skipped 不等于 passed。
- redaction failure 阻塞 release。
- 报告引用真实命令和结果。
