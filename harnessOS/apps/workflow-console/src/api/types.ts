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

export type PatchStatus = "proposed" | "applied" | "rejected";

export interface WorkflowPatchProposal {
  workflow_patch_id: string;
  workflow_template_id: string;
  workflow_draft_id: string;
  operation: string;
  status: PatchStatus;
  proposed_by?: string;
  requires_approval?: boolean;
  risk_flags?: string[];
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
  status: PatchStatus;
  resulting_draft_revision?: number;
  publish_version?: string;
  blocked_reason?: string;
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
}
