# V1.8-A Agent Task Contract Plan

日期：2026-05-30

## 目标

定义 Agent 接收用户研究任务后的机器可读合同，使 Agent 先生成 draft，经用户确认后再运行。

## AgentTask DTO

```ts
type AgentTask = {
  task_id: string;
  workspace_id?: string;
  user_intent: string;
  target_path_labels?: string[];
  target_path_refs?: string[];
  target_urls?: string[];
  source_policy: {
    allowed_types: Array<"pdf" | "txt" | "markdown" | "url">;
    recursive_folder_scan: boolean;
    require_user_authorization: boolean;
    skip_unsupported_types: boolean;
  };
  expected_outputs: Array<
    | "notebook_guide"
    | "source_grounded_qa"
    | "studio_notes"
    | "study_guide"
    | "briefing_doc"
    | "faq"
    | "validation_report"
  >;
  status: "draft" | "approved" | "running" | "completed" | "failed";
};
```

规则：

- `target_path_labels` 只用于展示，例如 `Desktop/技术分享/11-数字人`。
- `target_path_refs` 是授权后的 opaque reference，不得是 raw absolute path。
- 最终 report / fixtures 不得写入 raw `target_paths`、`/Users`、`file://`、cache path 或 artifact physical path。
- AgentTask 处于 `draft` 状态时，不得 scan / import / source read。

## WorkflowRun DTO

```ts
type WorkflowRun = {
  run_id: string;
  task_id: string;
  workspace_id: string;
  status: "pending" | "running" | "completed" | "failed" | "blocked";
  started_at?: string;
  finished_at?: string;
  steps: WorkflowStep[];
  artifact_refs: string[];
  validation_report_id?: string;
  final_decision?: "PASS_LIMITED" | "FAIL" | "BLOCKED";
};
```

## WorkflowStep DTO

```ts
type WorkflowStep = {
  step_id: string;
  name: string;
  status: "pending" | "running" | "completed" | "failed" | "skipped";
  started_at?: string;
  finished_at?: string;
  input_summary?: object;
  output_summary?: object;
  error_code?: string;
  error_message?: string;
  retry_count: number;
  artifact_refs: string[];
};
```

规则：

- 每个 step 必须有可读 `name` 和机器可读 `status`。
- step log 只能记录 input/output summary，不得 dump raw source content。
- step 失败必须记录 `error_code` 和 `error_message`。
- retry 必须递增 `retry_count`，不得覆盖原失败事实。

## ValidationAssertion DTO

```ts
type ValidationAssertion = {
  assertion_id: string;
  name: string;
  expected: unknown;
  actual: unknown;
  status: "PASS" | "FAIL" | "NOT_RUN" | "DEGRADED_ACCEPTED";
  evidence_ref?: string;
};
```

## ValidationReport DTO

```ts
type ValidationReport = {
  report_id: string;
  task_id: string;
  workspace_id: string;
  run_id?: string;
  source_summary: object;
  guide_result: object;
  qa_result: object;
  studio_result: object;
  citation_result: object;
  frontend_shell_result?: object;
  step_results: WorkflowStep[];
  assertions: ValidationAssertion[];
  raw_fixture_refs: string[];
  final_decision: "PASS_LIMITED" | "FAIL" | "BLOCKED";
  accepted_debts: string[];
  still_not_ready: string[];
};
```

规则：

- `assertions` 必须记录 expected / actual / status；不能只写“通过”。
- `raw_fixture_refs` 只能引用已脱敏 fixture 文件名或相对路径。
- `final_decision=PASS_LIMITED` 只代表受限路径合同通过，不代表普通用户 UX ready。
- draft 成功不等于 workflow 可运行。
- WorkflowRun 成功不等于 Guide / QA / Studio 内容质量人工通过。

## 验收标准

- 自然语言任务可转换为 draft。
- draft 不直接读取本地目录。
- draft 包含授权要求。
- draft 包含 allowed source types。
- draft 包含 expected outputs。
- 未确认前不会运行。
- 未确认前不会 scan / import / source read。
- WorkflowRun 可以串联 AgentTask、WorkflowStep、ValidationReport。
- ValidationReport 每个 assertion 都有 expected / actual / status。
- fixtures / reports 不含 raw local path。
- 不调用 `/api/v1/knowledge/*`。

## 必跑命令

```bash
npm run check
npm run smoke:v1.8-agent-task
```

## 风险

- 规格漂移：LOW。
- 虚假验收：MEDIUM。原因是 draft 成功不代表 workflow 可运行，WorkflowRun 成功也不代表内容质量人工通过。
