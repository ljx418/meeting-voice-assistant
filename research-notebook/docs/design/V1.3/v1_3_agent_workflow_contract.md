# V1.3 Agent Workflow Contract Discovery

文档状态：V1.3-A 合同发现阶段。当前不实现真实 Agent，不声明 workflow ready。

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
  created_at: string;
  finished_at?: string;
  run_report?: WorkflowRunReport;
  artifacts: SummaryArtifact[];
};

type WorkflowStep = {
  step_id: string;
  name: string;
  status: "pending" | "running" | "completed" | "failed" | "skipped";
  input_ref?: string;
  output_ref?: string;
  logs?: string[];
  started_at?: string;
  finished_at?: string;
  error_code?: string;
  error_message?: string;
  retry_count: number;
  artifact_refs: string[];
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
  folder_id?: string;
  collection_id: string;
  status: "draft" | "ready" | "failed" | "skipped";
  schema_version: string;
  coverage: SummaryArtifactCoverage;
  markdown: string;
  evidence_refs: EvidenceRef[];
};

type WorkflowRunReport = {
  scanned_file_count: number;
  extracted_file_count: number;
  skipped_file_count: number;
  generated_artifact_count: number;
};

type SummaryArtifactCoverage = {
  file_count: number;
  extracted_file_count: number;
  skipped_file_count: number;
  evidence_ref_count: number;
};

type EvidenceRef = {
  source_id: string;
  unit_id?: string;
  evidence_id?: string;
  relative_path?: string;
};

type FolderCollection = {
  collection_id: string;
  workspace_id: string;
  root_label: string;
  folders: FolderNode[];
  files: FolderFile[];
  skipped_files: SkippedFile[];
};

type FolderNode = {
  folder_id: string;
  parent_folder_id?: string;
  relative_path: string;
  depth: number;
  file_count: number;
  child_folder_count: number;
};

type FolderFile = {
  file_id: string;
  folder_id?: string;
  relative_path: string;
  extension: string;
  size_bytes: number;
  extraction_status: "extracted" | "skipped" | "unsupported" | "failed";
  text_preview?: string;
};

type SkippedFile = {
  relative_path: string;
  skipped_reason:
    | "hidden_file"
    | "hidden_dir"
    | "excluded_dir"
    | "unsupported_extension"
    | "secret_like_file"
    | "max_file_size_exceeded"
    | "binary_file"
    | "symlink_skipped"
    | "extract_failed"
    | "permission_denied";
};
```

## Adapter 状态

V1.3-A 时 adapter shell 返回稳定禁用状态。

V1.3-F 后，`createDraft` 已接入受限后端 route：

```ts
sources: no change
agentWorkflows.createDraft(...) -> POST /api/workspaces/{workspace_id}/agent-workflows/draft
agentWorkflows.getDraft(...) -> capability_missing
agentWorkflows.startRun(...) -> capability_missing
```

`createDraft` 只允许生成 registered `folder_summary_v1` draft。它不得访问本地目录、不得执行 workflow、不得开放任意工具调用。

`getDraft` / `startRun` 仍未作为完整 Agent runtime 启用。

## UI 状态

Agent Workflow 入口可以显示，V1.3-F 后可生成工作流草案，但必须明确：

- draft requires user approval
- no local folder access before authorization
- 不声明 Agent ready
- 不声明 Workflow ready
- 不声明 arbitrary Agent tool execution ready

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

## V1.3-A 阶段报告预期

- 规格漂移评估：LOW。
- 虚假验收评估：MEDIUM。
- MEDIUM 收敛措施：UI 必须显示 contract required / disabled / no local folder access before authorization。
