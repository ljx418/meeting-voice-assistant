export interface WorkflowSummary {
  workflow_template_id: string;
  name: string;
  latest_version_id?: string;
}

export interface WorkflowVersionSummary {
  workflow_version_id: string;
  workflow_template_id: string;
  version: string;
}

export interface WorkflowInstanceSummary {
  workflow_instance_id: string;
  workflow_template_id: string;
  workflow_version_id: string;
  status: string;
}

export interface WorkflowStatus {
  workflow_instance_id: string;
  status: string;
  current_station_ids: string[];
  station_counts?: Record<string, number>;
  job_counts?: Record<string, number>;
  artifact_count?: number;
  quality_count?: number;
}

export interface ArtifactSummary {
  artifact_id: string;
  kind?: string;
  name?: string;
  metadata?: Record<string, unknown>;
  parent_ids?: string[];
}

export interface JobSummary {
  job_id: string;
  status: string;
  progress?: number;
}

export interface ApprovalSummary {
  approval_id: string;
  status: string;
  reason?: string;
  request_summary?: string;
  active?: boolean;
  inactive_reason?: string;
  station_run_id?: string;
  station_id?: string;
}

export interface QualitySummary {
  evaluation_id: string;
  status: string;
  score?: number;
  issues?: unknown[];
  suggestions?: unknown[];
  rubric_id?: string;
  station_run_id?: string;
  artifact_id?: string;
}

export interface TraceSummary {
  trace_id?: string;
  summary?: string;
  events?: unknown[];
  [key: string]: unknown;
}

export interface StationRunSummary {
  station_run_id: string;
  station_id: string;
  status: string;
  job?: JobSummary;
  input_artifacts?: ArtifactSummary[];
  output_artifacts?: ArtifactSummary[];
  approvals?: ApprovalSummary[];
  quality?: QualitySummary[];
  trace_summary?: TraceSummary;
}

export interface StationBoardSummary {
  station: {
    station_id: string;
    name?: string;
    role?: string;
  };
  runs: StationRunSummary[];
  status: string;
  input_artifacts?: ArtifactSummary[];
  output_artifacts?: ArtifactSummary[];
  approvals?: ApprovalSummary[];
  quality?: QualitySummary[];
  trace_summary?: TraceSummary;
}

export interface WorkflowBoard {
  workflow_instance: WorkflowInstanceSummary;
  stations: StationBoardSummary[];
  current_station_ids: string[];
  jobs?: JobSummary[];
  artifacts?: ArtifactSummary[];
  approvals?: ApprovalSummary[];
  quality_evaluations?: QualitySummary[];
  trace_summary?: TraceSummary;
}

export interface WorkflowEvent {
  id?: string;
  type: string;
  source?: "live" | "demo" | "trace_only";
  timestamp?: string;
  data?: Record<string, unknown>;
}

export type PatchStatus = "proposed" | "selected" | "applied" | "rejected" | "stale" | "blocked" | "conflicted";

export interface WorkflowPatchProposal {
  workflow_patch_id: string;
  patch_id?: string;
  workflow_template_id: string;
  workflow_draft_id: string;
  base_revision?: number;
  current_draft_revision?: number;
  operation: string;
  status: PatchStatus;
  proposed_by?: string;
  source?: "canvas" | "inspector" | "agent" | "workflow_console";
  intent_type?: "node_add" | "edge_add" | "inspector_update";
  requires_approval?: boolean;
  risk_flags?: string[];
  selected?: boolean;
  stale_reason?: string | null;
  conflict_reason?: string | null;
  created_at?: string;
  updated_at?: string;
}

export type PatchQueueDTO = WorkflowPatchProposal;

export interface NodeTemplateDescriptor {
  node_template_id: string;
  station_kind: string;
  schema_version: string;
  allowed_skill_refs: string[];
  allowed_connector_refs: string[];
  allowed_artifact_kinds: string[];
  allowed_quality_rules: string[];
  allowed_approval_policies: string[];
}

export interface StationDescriptorMapping extends NodeTemplateDescriptor {
  catalog_id: string;
  catalog_version: string;
}

export interface NodeCatalogItem extends StationDescriptorMapping {
  id: string;
  label: string;
}

export interface CanvasDraftProjection {
  projection_id: string;
  workflow_instance_id: string;
  workflow_template_id: string;
  workflow_draft_id: string;
  draft_revision: number;
  generated_at: string;
  board_status_timestamp?: string;
  status_updated_at?: string;
  patch_queue_revision?: string;
  freshness_state?: "fresh" | "stale_draft" | "stale_board" | "stale_patch" | "unknown";
  stale_reasons?: string[];
  source_refs: Record<string, unknown>;
  nodes: Array<{
    station_id: string;
    name?: string;
    role?: string;
    station_kind?: string;
    skill_refs: string[];
    connector_refs: string[];
    status?: string;
    run_count: number;
  }>;
  edges: Array<{
    edge_id: string;
    from_station_id: string;
    to_station_id: string;
    order?: number;
  }>;
  runtime_summary: Record<string, unknown>;
  patch_queue?: PatchQueueDTO[];
  pending_patch?: PatchQueueDTO | null;
  redaction_status: "redacted";
}

export interface FolderSummaryAuthorization {
  authorization_id: string;
  requested_path: string;
  resolved_path_label: string;
  allowed_root: string;
  status: string;
  created_at: string;
  expires_at: string;
  redaction_status: "redacted";
}

export interface FolderSummaryScanResult {
  folder_tree: Array<{ path: string; kind: "file" | "folder" }>;
  total_file_count: number;
  markdown_file_count: number;
  child_folder_count: number;
  unsupported_file_count: number;
  unsupported_files: string[];
  empty_folders: string[];
  redaction_status: "redacted";
}

export interface FolderSummaryProposal {
  proposal_id: string;
  workflow_template_id: string;
  workflow_draft_id: string;
  workflow_instance_id?: string | null;
  draft_revision: number;
  status: "proposed" | "applied" | "published" | "completed" | "failed";
  requested_path: string;
  nodes: Array<{ station_id: string; name: string; status: string }>;
  edges: Array<{ edge_id: string; from_station_id: string; to_station_id: string }>;
  risk_flags: string[];
  requires_user_confirmation: boolean;
  created_at: string;
  updated_at: string;
  redaction_status: "redacted";
}

export interface FolderSummaryArtifact {
  artifact_id: string;
  name: string;
  kind: string;
  content: string;
  metadata?: Record<string, unknown>;
  redaction_status: "redacted";
}

export interface FolderSummaryQualityReport {
  status: string;
  summary_coverage: { expected_folder_count: number; generated_summary_count: number };
  unsupported_files: string[];
  empty_folders: string[];
  markdown_file_count: number;
  child_folder_count: number;
  redaction_status: "redacted";
}

export interface FolderSummaryNodeAttempt {
  attempt_id: string;
  attempt: number;
  status: string;
  created_at: string;
  error?: string | null;
}

export interface FolderSummaryRun {
  workflow_instance_id: string;
  proposal_id: string;
  authorization_id: string;
  status: string;
  nodes: Array<{ station_id: string; name: string; status: string; updated_at: string; error?: string | null; attempts?: FolderSummaryNodeAttempt[] }>;
  artifacts: FolderSummaryArtifact[];
  quality_report: FolderSummaryQualityReport;
  operation_evidence?: OperationEvidenceRecord[];
  governance_review?: GovernanceReviewSummary;
  created_at: string;
  updated_at: string;
  redaction_status: "redacted";
}

export interface ControlledRuntimeEvidenceRecord extends OperationEvidenceRecord {
  operation_type?: string;
  capability_decision?: string;
  timeout_baseline?: { enabled: boolean; timeout_seconds?: number; status: string };
  kill_switch_baseline?: { enabled: boolean; scope?: string; status: string };
}

export interface ControlledRuntimeResult {
  workflow_instance_id: string;
  workflow_template_id: string;
  status: string;
  backed_by: "generic_controlled_runtime";
  user_confirmed_required: true;
  agent_mutation_allowed: false;
  nodes: FolderSummaryRun["nodes"];
  artifacts: FolderSummaryArtifact[];
  quality_report: FolderSummaryQualityReport;
  attempt_history: {
    workflow_instance_id: string;
    stations: Array<{ station_id: string; status: string; attempts: FolderSummaryNodeAttempt[] }>;
    redaction_status: "redacted";
  };
  downstream_stale: Array<{ station_id: string; reason: string; requires_user_confirmed_continue: true }>;
  operation_evidence: ControlledRuntimeEvidenceRecord[];
  timeout_baseline: { enabled: boolean; timeout_seconds?: number; status: string };
  kill_switch_baseline: { enabled: boolean; scope?: string; status: string };
  redaction_status: "redacted";
}

export interface NodeAddIntent {
  source: "canvas";
  intent_type: "node_add";
  operation: "add_station";
  workflow_instance_id?: string;
  payload: {
    station: {
      station_id: string;
      name: string;
      role?: string;
      skill_refs?: string[];
      connector_refs?: string[];
      metadata: {
        node_catalog_id: string;
        node_label: string;
        catalog_id: string;
        catalog_version: string;
        node_template_id: string;
        station_kind: string;
        schema_version: string;
        allowed_skill_refs: string[];
        allowed_connector_refs: string[];
        allowed_artifact_kinds: string[];
        allowed_quality_rules: string[];
        allowed_approval_policies: string[];
      };
    };
  };
}

export interface EdgeAddIntent {
  source: "canvas";
  intent_type: "edge_add";
  operation: "update_edge";
  workflow_instance_id?: string;
  payload: {
    edge_id: string;
    edge_patch: {
      action: "add";
      from_station_id: string;
      to_station_id: string;
      condition?: Record<string, unknown>;
      order?: number;
      metadata?: Record<string, unknown>;
    };
  };
}

export interface InspectorUpdateIntent {
  source: "inspector" | "agent";
  intent_type: "inspector_update";
  operation:
    | "update_station_prompt"
    | "update_connector"
    | "update_artifact_contract"
    | "update_quality_rule"
    | "update_approval_point";
  workflow_instance_id?: string;
  payload: Record<string, unknown>;
}

export type CanvasPatchIntent = NodeAddIntent | EdgeAddIntent | InspectorUpdateIntent;

export type AgentActionName =
  | "explain_workflow"
  | "summarize_events"
  | "summarize_quality"
  | "summarize_context"
  | "suggest_patch"
  | "show_patch_diff"
  | "show_approval_notice"
  | "show_context_summary"
  | "navigate_to_editing_panel"
  | "open_editing_panel"
  | "open_approval_panel"
  | "open_context_panel"
  | "open_quality_panel"
  | "open_artifact_panel"
  | "propose_patch"
  | "propose_context_update"
  | "propose_approval_decision"
  | "propose_station_rerun";

export interface AgentActionIntent {
  action: AgentActionName;
  executable: false;
}

export interface AgentTalkMessage {
  message_id: string;
  agent_session_id: string;
  workflow_instance_id: string;
  workflow_template_id: string;
  role: "user" | "assistant" | "system" | "event";
  source: "user" | "assistant" | "system" | "event";
  content: string;
  resource_refs?: Record<string, unknown>;
  created_at?: string;
  redaction_status: "redacted";
}

export interface AgentTalkSuggestion {
  suggestion_id: string;
  workflow_instance_id: string;
  workflow_template_id: string;
  workflow_patch_id?: string;
  type: "explain" | "summarize" | "propose_patch" | "show_diff" | "approval_notice" | "show_context_summary";
  title: string;
  summary: string;
  status: "active" | "dismissed";
  action_intent: AgentActionIntent;
  patch_intent?: CanvasPatchIntent | null;
  risk_flags?: string[];
  requires_approval?: boolean;
  created_at?: string;
  redaction_status: "redacted";
}

export interface AgentTalkSession {
  agent_session_id: string;
  workflow_instance_id: string;
  workflow_template_id: string;
  scope?: Record<string, unknown>;
  created_by?: string;
  created_at?: string;
  updated_at?: string;
  redaction_status: "redacted";
  messages: AgentTalkMessage[];
  suggestions: AgentTalkSuggestion[];
}

export interface AgentTalkInteractionState {
  workflow_instance_id: string;
  workflow_template_id: string;
  agent_session_id: string;
  selected_suggestion_id?: string | null;
  selected_proposal_id?: string | null;
  selected_handoff_id?: string | null;
  selected_patch_id?: string | null;
  selected_evidence_id?: string | null;
  stale_reasons: string[];
  refresh_generation: string;
  source_refs?: Record<string, unknown>;
  generated_at?: string;
  redaction_status: "redacted";
}

export type AgentActionPolicyClass = "display_only" | "navigation" | "proposal_only" | "forbidden";
export type AgentActionLifecycle = "proposed" | "reviewed" | "dismissed" | "converted_to_patch" | "converted_to_navigation" | "expired" | "blocked";

export interface AgentActionProposal {
  proposal_id: string;
  agent_session_id: string;
  workflow_instance_id: string;
  workflow_template_id: string;
  intent_type: AgentActionName;
  policy_class: AgentActionPolicyClass;
  lifecycle: AgentActionLifecycle;
  status: AgentActionLifecycle;
  title: string;
  summary: string;
  target_panel?: "editing" | "approval" | "context" | "quality" | "artifact" | "events" | null;
  workflow_patch_id?: string | null;
  risk_level: "low" | "medium" | "high";
  risk_flags: string[];
  requires_approval: boolean;
  policy_decision: string;
  payload_summary?: Record<string, unknown>;
  resource_refs?: Record<string, unknown>;
  created_by?: string;
  created_at?: string;
  updated_at?: string;
  redaction_status: "redacted";
}

export type AgentHandoffTargetPanel = "editing_panel" | "approval_panel" | "context_panel" | "quality_panel" | "artifact_panel";
export type AgentHandoffStatus = "active" | "opened" | "used_for_user_confirmed_action" | "dismissed" | "expired" | "stale" | "blocked";

export interface AgentActionHandoff {
  handoff_id: string;
  proposal_id: string;
  workflow_instance_id: string;
  workflow_template_id: string;
  target_panel: AgentHandoffTargetPanel;
  target_resource: Record<string, unknown>;
  suggested_form_prefill: Record<string, unknown>;
  expires_at: string;
  status: AgentHandoffStatus;
  inactive_reason?: string;
  updated_at?: string;
  created_at: string;
  created_by?: string;
  redaction_status: "redacted";
}

export interface AgentHandoffAuditRecord {
  audit_id: string;
  handoff_id: string;
  event_type: string;
  summary: string;
  data?: Record<string, unknown>;
  created_at: string;
  redaction_status: "redacted";
}

export interface WorkflowPatchDiff {
  workflow_patch_id: string;
  workflow_draft_id: string;
  base_revision: number;
  operation: string;
  target?: Record<string, unknown>;
  before_summary: string;
  after_summary: string;
  risk_flags: string[];
  requires_approval: boolean;
  redacted: boolean;
}

export interface PatchActionResult {
  workflow_patch_id: string;
  workflow_template_id?: string;
  workflow_draft_id?: string;
  status: PatchStatus;
  operation?: string;
  base_revision?: number;
  applied_revision?: number;
  resulting_draft_revision?: number;
  requires_approval?: boolean;
  risk_flags?: string[];
  blocked_reason?: string;
}

export interface PublishVersionResult {
  workflow_template_id: string;
  workflow_draft_id?: string;
  draft_status?: string;
  draft_revision?: number;
  workflow_version_id: string;
  version: string;
}

export interface WorkflowContextSummary {
  workflow_instance_id: string;
  revision: number;
  business: Record<string, unknown>;
  updated_at?: string;
  trace_id?: string;
}

export interface OperationResult<T = unknown> {
  operation: string;
  status: string;
  resource: T;
  idempotent?: boolean;
  trace_id?: string;
  evidence?: OperationEvidenceRecord;
}

export type OperationEvidenceStatus =
  | "succeeded"
  | "failed"
  | "idempotent_replayed"
  | "blocked"
  | "stale_rejected"
  | "expired_rejected";

export interface OperationRuntimeResultRef {
  type: string;
  resource_id?: string;
  workflow_instance_id?: string;
  workflow_template_id?: string;
  operation: string;
  status: string;
  trace_id?: string;
}

export interface OperationEvidenceRecord {
  evidence_id: string;
  workflow_instance_id: string;
  workflow_template_id?: string;
  operation: string;
  status: OperationEvidenceStatus;
  correlation_id: string;
  operation_id: string;
  idempotency_key: string;
  handoff_id?: string | null;
  proposal_id?: string | null;
  handoff_status_at_execution?: string | null;
  proposal_status_at_execution?: string | null;
  user_confirmed: boolean;
  source?: string;
  risk_flags: string[];
  policy_decision?: string;
  runtime_result_ref: OperationRuntimeResultRef;
  audit_refs?: Array<Record<string, unknown>>;
  created_at?: string;
  created_by?: string;
  redaction_status: "redacted";
}

export interface GovernanceReviewSummary {
  workflow_instance_id: string;
  workflow_template_id?: string;
  summary: {
    evidence_count: number;
    handoff_count: number;
    status_counts: Record<string, number>;
    operation_counts: Record<string, number>;
  };
  operation_evidence: OperationEvidenceRecord[];
  handoff_summary: Array<Record<string, unknown>>;
  audit_timeline: Array<Record<string, unknown>>;
  redaction_status: "redacted";
}
