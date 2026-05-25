# V1.3 Agent Workflow Contract Discovery

文档状态：草案。当前不实现真实 Agent，不声明 workflow ready。

## 目标

定义 V1.3 Agent Workflow 产品层的最小对象，使后续阶段可以实现：

```text
用户目标 -> workflow draft -> 用户确认 -> workflow run -> artifacts
```

## 最小 DTO

```ts
type AgentTask = {
  task_id: string;
  workspace_id: string;
  user_goal: string;
  status: "draft" | "awaiting_approval" | "running" | "completed" | "failed";
  workflow_id?: string;
};

type Workflow = {
  workflow_id: string;
  name: string;
  template_id: string;
  status: "draft" | "ready" | "disabled";
  required_permissions: string[];
  steps: WorkflowStep[];
};

type WorkflowRun = {
  run_id: string;
  workflow_id: string;
  status: "pending" | "running" | "completed" | "failed" | "cancelled";
  artifacts: SummaryArtifact[];
};

type WorkflowStep = {
  step_id: string;
  name: string;
  status: "pending" | "running" | "completed" | "failed" | "skipped";
  input_ref?: string;
  output_ref?: string;
  logs?: string[];
};

type Tool = {
  tool_id: string;
  name: string;
  input_schema_ref: string;
  output_schema_ref: string;
  requires_approval: boolean;
};

type SummaryArtifact = {
  artifact_id: string;
  title: string;
  artifact_type: "folder_summary" | "root_summary";
  markdown: string;
  evidence_refs: Array<{
    source_id: string;
    unit_id?: string;
    evidence_id?: string;
    relative_path?: string;
  }>;
};
```

## V1.3-A 允许

- 新增合同文档。
- 新增前端 adapter shell。
- 新增 disabled Agent Workflow UI。
- 显示 workflow draft 概念和权限说明。

## V1.3-A 禁止

- 不读取本地目录。
- 不执行 workflow。
- 不让 Agent 自由调用工具。
- 不声明 Agent ready。
- 不声明 Workflow ready。
