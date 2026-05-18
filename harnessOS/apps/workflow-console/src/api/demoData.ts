import type { AgentTalkFixture } from "./agentTalkTypes.js";
import type { WorkflowConsoleEmbedBootstrap, WorkflowConsoleEmbedDefinition } from "./embedTypes.js";
import type {
  WorkflowBoard,
  WorkflowEvent,
  WorkflowInstanceSummary,
  WorkflowPatchDiff,
  WorkflowPatchProposal,
  WorkflowStatus,
  WorkflowSummary,
  WorkflowVersionSummary,
} from "./types.js";

export const demoWorkflows: WorkflowSummary[] = [
  {
    workflow_template_id: "wf_reference_storyboard",
    name: "AI 短视频生成工作流",
    latest_version_id: "wfv_reference_storyboard_v1",
  },
];

export const demoVersions: WorkflowVersionSummary[] = [
  {
    workflow_template_id: "wf_reference_storyboard",
    workflow_version_id: "wfv_reference_storyboard_v1",
    version: "1.0.0",
  },
];

export const demoInstances: WorkflowInstanceSummary[] = [
  {
    workflow_instance_id: "wfi_reference_demo",
    workflow_template_id: "wf_reference_storyboard",
    workflow_version_id: "wfv_reference_storyboard_v1",
    status: "completed",
  },
];

export const demoStatus: WorkflowStatus = {
  workflow_instance_id: "wfi_reference_demo",
  status: "running",
  current_station_ids: ["station_render"],
  station_counts: { completed: 3, warning: 1, queued: 2, waiting_approval: 1, idle: 1 },
  job_counts: { completed: 3, queued: 2 },
  artifact_count: 6,
  quality_count: 3,
};

export const demoBoard: WorkflowBoard = {
  workflow_instance: demoInstances[0],
  current_station_ids: [],
  stations: [
    {
      station: { station_id: "station_input", name: "用户输入", role: "input" },
      status: "completed",
      runs: [
        {
          station_run_id: "sr_input_1",
          station_id: "station_input",
          status: "completed",
          job: { job_id: "job_input_1", status: "completed", progress: 1 },
          output_artifacts: [{ artifact_id: "art_brief_1", kind: "brief", name: "主题需求" }],
          trace_summary: { trace_id: "trace_input", summary: "input collected" },
        },
      ],
      output_artifacts: [{ artifact_id: "art_brief_1", kind: "brief", name: "主题需求" }],
      trace_summary: { trace_id: "trace_input", summary: "input collected" },
    },
    {
      station: { station_id: "station_outline", name: "剧情大纲生成", role: "planner" },
      status: "completed",
      runs: [
        {
          station_run_id: "sr_outline_1",
          station_id: "station_outline",
          status: "completed",
          job: { job_id: "job_outline_1", status: "completed", progress: 1 },
          input_artifacts: [{ artifact_id: "art_brief_1", kind: "brief", name: "主题需求" }],
          output_artifacts: [{ artifact_id: "art_outline_1", kind: "outline", name: "剧情大纲" }],
          trace_summary: { trace_id: "trace_outline", summary: "outline station completed" },
        },
      ],
      output_artifacts: [{ artifact_id: "art_outline_1", kind: "outline", name: "剧情大纲" }],
      trace_summary: { trace_id: "trace_outline", summary: "outline station completed" },
    },
    {
      station: { station_id: "station_script", name: "脚本生成", role: "writer" },
      status: "completed",
      runs: [
        {
          station_run_id: "sr_script_1",
          station_id: "station_script",
          status: "completed",
          job: { job_id: "job_script_1", status: "completed", progress: 1 },
          input_artifacts: [{ artifact_id: "art_outline_1", kind: "outline", name: "剧情大纲" }],
          output_artifacts: [{ artifact_id: "art_script_1", kind: "script", name: "分镜脚本" }],
          quality: [{ evaluation_id: "qe_script_1", status: "passed", score: 0.92 }],
          trace_summary: { trace_id: "trace_script", summary: "script station completed" },
        },
      ],
      input_artifacts: [{ artifact_id: "art_outline_1", kind: "outline", name: "剧情大纲" }],
      output_artifacts: [{ artifact_id: "art_script_1", kind: "script", name: "分镜脚本" }],
      quality: [{ evaluation_id: "qe_script_1", status: "passed", score: 0.92 }],
      trace_summary: { trace_id: "trace_script", summary: "script station completed" },
    },
    {
      station: { station_id: "station_storyboard", name: "分镜生成", role: "director" },
      status: "warning",
      runs: [
        {
          station_run_id: "sr_storyboard_1",
          station_id: "station_storyboard",
          status: "completed",
          job: { job_id: "job_storyboard_1", status: "completed", progress: 1 },
          input_artifacts: [{ artifact_id: "art_script_1", kind: "script", name: "分镜脚本" }],
          output_artifacts: [{ artifact_id: "art_storyboard_1", kind: "storyboard", name: "storyboard_v1.json" }],
          quality: [{ evaluation_id: "qe_storyboard_1", status: "failed", score: 0.64 }],
          trace_summary: { trace_id: "trace_storyboard", summary: "storyboard generated with warnings" },
        },
      ],
      input_artifacts: [{ artifact_id: "art_script_1", kind: "script", name: "分镜脚本" }],
      output_artifacts: [{ artifact_id: "art_storyboard_1", kind: "storyboard", name: "storyboard_v1.json" }],
      quality: [{ evaluation_id: "qe_storyboard_1", status: "failed", score: 0.64 }],
      trace_summary: { trace_id: "trace_storyboard", summary: "storyboard generated with warnings" },
    },
    {
      station: { station_id: "station_render", name: "视频渲染", role: "connector" },
      status: "queued",
      runs: [
        {
          station_run_id: "sr_render_1",
          station_id: "station_render",
          status: "queued",
          input_artifacts: [{ artifact_id: "art_storyboard_1", kind: "storyboard", name: "storyboard_v1.json" }],
          trace_summary: { trace_id: "trace_render", summary: "render waiting for connector" },
        },
      ],
      input_artifacts: [{ artifact_id: "art_storyboard_1", kind: "storyboard", name: "storyboard_v1.json" }],
      trace_summary: { trace_id: "trace_render", summary: "render waiting for connector" },
    },
    {
      station: { station_id: "station_quality", name: "质量评估", role: "evaluator" },
      status: "queued",
      runs: [
        {
          station_run_id: "sr_quality_1",
          station_id: "station_quality",
          status: "queued",
          quality: [{ evaluation_id: "qe_quality_1", status: "manual_required", score: 0.78 }],
          trace_summary: { trace_id: "trace_quality", summary: "quality pending" },
        },
      ],
      quality: [{ evaluation_id: "qe_quality_1", status: "manual_required", score: 0.78 }],
      trace_summary: { trace_id: "trace_quality", summary: "quality pending" },
    },
    {
      station: { station_id: "station_review", name: "人工审批", role: "reviewer" },
      status: "waiting_approval",
      runs: [
        {
          station_run_id: "sr_review_1",
          station_id: "station_review",
          status: "waiting_approval",
          input_artifacts: [{ artifact_id: "art_script_1", kind: "script", name: "分镜脚本" }],
          approvals: [{ approval_id: "appr_review_1", status: "pending" }],
          trace_summary: { trace_id: "trace_review", summary: "waiting for approval" },
        },
      ],
      approvals: [{ approval_id: "appr_review_1", status: "pending" }],
      trace_summary: { trace_id: "trace_review", summary: "waiting for approval" },
    },
    {
      station: { station_id: "station_publish", name: "发布输出", role: "publisher" },
      status: "idle",
      runs: [
        {
          station_run_id: "sr_publish_1",
          station_id: "station_publish",
          status: "idle",
          trace_summary: { trace_id: "trace_publish", summary: "not published" },
        },
      ],
      trace_summary: { trace_id: "trace_publish", summary: "not published" },
    },
  ],
  jobs: [
    { job_id: "job_input_1", status: "completed", progress: 1 },
    { job_id: "job_outline_1", status: "completed", progress: 1 },
    { job_id: "job_script_1", status: "completed", progress: 1 },
    { job_id: "job_storyboard_1", status: "completed", progress: 1 },
  ],
  artifacts: [
    { artifact_id: "art_brief_1", kind: "brief", name: "主题需求" },
    { artifact_id: "art_outline_1", kind: "outline", name: "剧情大纲" },
    { artifact_id: "art_script_1", kind: "script", name: "分镜脚本" },
    { artifact_id: "art_storyboard_1", kind: "storyboard", name: "storyboard_v1.json" },
  ],
  approvals: [{ approval_id: "appr_review_1", status: "pending" }],
  quality_evaluations: [
    { evaluation_id: "qe_script_1", status: "passed", score: 0.91 },
    { evaluation_id: "qe_storyboard_1", status: "failed", score: 0.64 },
    { evaluation_id: "qe_quality_1", status: "manual_required", score: 0.78 },
  ],
  trace_summary: { trace_id: "trace_workflow", summary: "redacted workflow trace summary" },
};

export const demoEvents: WorkflowEvent[] = [
  { type: "workflow.instance.completed", source: "demo", timestamp: "2026-05-18T00:00:00Z", data: { workflow_instance_id: "wfi_reference_demo" } },
  { type: "approval.required", source: "demo", timestamp: "2026-05-18T00:01:00Z", data: { approval_id: "appr_review_1" } },
  { type: "workflow.patch.proposed", source: "demo", timestamp: "2026-05-18T00:02:00Z", data: { workflow_patch_id: "wfp_add_review_note" } },
  { type: "quality.evaluated", source: "trace_only", timestamp: "2026-05-18T00:03:00Z", data: { evaluation_id: "qe_script_1" } },
];

export const demoPatchProposal: WorkflowPatchProposal = {
  workflow_patch_id: "wfp_add_review_note",
  workflow_template_id: "wf_reference_storyboard",
  workflow_draft_id: "wfd_reference_storyboard",
  operation: "update_station_prompt",
  status: "proposed",
  proposed_by: "user",
  requires_approval: false,
  risk_flags: [],
};

export const demoPatchDiff: WorkflowPatchDiff = {
  workflow_patch_id: "wfp_add_review_note",
  workflow_draft_id: "wfd_reference_storyboard",
  base_revision: 4,
  operation: "update_station_prompt",
  before_summary: "审核节点仅检查审批状态。",
  after_summary: "审核节点增加对工件摘要和质量分数的检查说明。",
  risk_flags: [],
  requires_approval: false,
  redacted: true,
};

export const demoHighRiskPatchDiff: WorkflowPatchDiff = {
  workflow_patch_id: "wfp_remove_approval",
  workflow_draft_id: "wfd_reference_storyboard",
  base_revision: 4,
  operation: "update_approval_point",
  before_summary: "审核节点需要人工审批。",
  after_summary: "尝试移除审核节点的人工审批。",
  risk_flags: ["approval_removed"],
  requires_approval: true,
  redacted: true,
};

export const demoEmbedDefinition: WorkflowConsoleEmbedDefinition = {
  schemaVersion: "v4.0-c",
  embedId: "embed_reference_agent_talk",
  appId: "reference_app",
  defaultProjectId: "demo",
  defaultWorkspaceId: "local",
  capabilityMode: "bff",
  transportMode: "bff_proxy",
  allowedEventChannels: ["workflow", "approval", "workflow_patch", "workflow_context", "business"],
  allowedActions: ["explain_workflow", "summarize_events", "show_patch_diff", "show_approval_notice", "show_context_summary"],
  demo_only: true,
  fixture_only: true,
  not_runtime_e2e: true,
};

export const demoEmbedBootstrap: WorkflowConsoleEmbedBootstrap = {
  sessionId: "sess_reference_demo",
  threadId: "thread_reference_demo",
  bff_eventsource_url: "/bff/events/subscribe?channels=workflow,approval,workflow_patch",
  allowedActions: demoEmbedDefinition.allowedActions,
  demo_only: true,
  fixture_only: true,
  not_runtime_e2e: true,
};

export const demoAgentTalkFixture: AgentTalkFixture = {
  workflow_instance_id: "wfi_reference_demo",
  title: "Agent 助手",
  allowed_actions: demoEmbedDefinition.allowedActions,
  events: demoEvents,
  patch_proposal: demoPatchProposal,
  patch_diff: demoPatchDiff,
  context_summary: {
    workflow_instance_id: "wfi_reference_demo",
    business: {
      selected_station: "station_review",
      operator_note: "等待用户确认审核节点。",
    },
    demo_only: true,
    fixture_only: true,
    not_runtime_e2e: true,
  },
  approval_notice: {
    approval_id: "appr_review_1",
    status: "pending",
    message: "审核节点需要用户确认。请前往审批面板处理。",
  },
  demo_only: true,
  fixture_only: true,
  not_runtime_e2e: true,
};
