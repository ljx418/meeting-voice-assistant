import type { WorkflowEvent, WorkflowPatchDiff, WorkflowPatchProposal } from "./types.js";

export type AgentTalkAllowedAction =
  | "explain_workflow"
  | "summarize_events"
  | "show_patch_diff"
  | "show_approval_notice"
  | "show_context_summary";

export interface AgentTalkContextSummary {
  workflow_instance_id: string;
  business: Record<string, unknown>;
  demo_only: true;
  fixture_only: true;
  not_runtime_e2e: true;
}

export interface AgentTalkFixture {
  workflow_instance_id: string;
  title: string;
  allowed_actions: AgentTalkAllowedAction[];
  events: WorkflowEvent[];
  patch_proposal: WorkflowPatchProposal;
  patch_diff: WorkflowPatchDiff;
  context_summary: AgentTalkContextSummary;
  approval_notice: {
    approval_id: string;
    status: "pending" | "inactive";
    message: string;
  };
  demo_only: true;
  fixture_only: true;
  not_runtime_e2e: true;
}
