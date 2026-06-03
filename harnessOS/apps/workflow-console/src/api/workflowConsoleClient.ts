import type {
  ArtifactSummary,
  AgentActionHandoff,
  AgentHandoffAuditRecord,
  AgentActionProposal,
  AgentTalkInteractionState,
  ApprovalSummary,
  AgentTalkSession,
  AgentTalkSuggestion,
  CanvasPatchIntent,
  CanvasDraftProjection,
  GovernanceReviewSummary,
  FolderSummaryArtifact,
  FolderSummaryAuthorization,
  FolderSummaryProposal,
  FolderSummaryQualityReport,
  FolderSummaryRun,
  FolderSummaryScanResult,
  ControlledRuntimeResult,
  NodeCatalogItem,
  OperationResult,
  OperationEvidenceRecord,
  PatchQueueDTO,
  PatchActionResult,
  PublishVersionResult,
  QualitySummary,
  WorkflowPatchDiff,
  WorkflowPatchProposal,
  WorkflowBoard,
  WorkflowContextSummary,
  WorkflowEvent,
  WorkflowInstanceSummary,
  WorkflowStatus,
  WorkflowSummary,
  WorkflowVersionSummary,
} from "./types.js";

export class WorkflowConsoleClient {
  constructor(private readonly basePath = "/bff") {}

  listWorkflows(): Promise<WorkflowSummary[]> {
    return this.get<WorkflowSummary[]>("/workflows");
  }

  createFolderSummaryProposal(payload: { folder_path: string; source: "workflow_console" }): Promise<FolderSummaryProposal> {
    return this.post<FolderSummaryProposal>("/v4_1/folder-summary/proposals", payload);
  }

  authorizeFolderSummaryRead(payload: {
    folder_path: string;
    user_confirmed: true;
    source: "workflow_console" | "folder_input_inspector";
  }): Promise<FolderSummaryAuthorization> {
    return this.post<FolderSummaryAuthorization>("/v4_1/folder-summary/authorize", payload);
  }

  debugFolderSummaryScan(payload: { authorization_id: string }): Promise<FolderSummaryScanResult> {
    return this.post<FolderSummaryScanResult>("/v4_1/folder-summary/debug-scan", payload);
  }

  applyFolderSummaryProposal(
    proposalId: string,
    payload: { authorization_id?: string; user_confirmed: true; source: "workflow_console" | "editing_panel" },
  ): Promise<{ operation: string; status: string; resource: FolderSummaryProposal; redaction_status: "redacted" }> {
    return this.post<{ operation: string; status: string; resource: FolderSummaryProposal; redaction_status: "redacted" }>(
      `/v4_1/folder-summary/proposals/${encodeURIComponent(proposalId)}/apply`,
      payload,
    );
  }

  publishFolderSummaryProposal(
    proposalId: string,
    payload: { user_confirmed: true; source: "workflow_console" | "editing_panel" },
  ): Promise<{ operation: string; status: string; resource: FolderSummaryProposal; redaction_status: "redacted" }> {
    return this.post<{ operation: string; status: string; resource: FolderSummaryProposal; redaction_status: "redacted" }>(
      `/v4_1/folder-summary/proposals/${encodeURIComponent(proposalId)}/publish`,
      payload,
    );
  }

  runFolderSummaryWorkflow(
    proposalId: string,
    payload: { authorization_id: string; user_confirmed: true; source: "workflow_console" | "run_panel" },
  ): Promise<FolderSummaryRun> {
    return this.post<FolderSummaryRun>(`/v4_1/folder-summary/proposals/${encodeURIComponent(proposalId)}/start-local-workflow`, payload);
  }

  getFolderSummaryInstance(instanceId: string): Promise<FolderSummaryRun> {
    return this.get<FolderSummaryRun>(`/v4_1/folder-summary/instances/${encodeURIComponent(instanceId)}`);
  }

  rerunFolderSummaryNode(
    instanceId: string,
    payload: { station_id: "markdown_parse"; user_confirmed: true; source: "run_panel" },
  ): Promise<FolderSummaryRun> {
    return this.post<FolderSummaryRun>(`/v4_1/folder-summary/instances/${encodeURIComponent(instanceId)}/rerun-node`, payload);
  }

  createFolderSummaryAgentDebugProposal(instanceId: string, payload: { requested_change: string }): Promise<Record<string, unknown>> {
    return this.post<Record<string, unknown>>(
      `/v4_1/folder-summary/instances/${encodeURIComponent(instanceId)}/agent-debug-proposal`,
      payload,
    );
  }

  listFolderSummaryOperationEvidence(instanceId: string): Promise<OperationEvidenceRecord[]> {
    return this.get<OperationEvidenceRecord[]>(`/v4_1/folder-summary/instances/${encodeURIComponent(instanceId)}/operation-evidence`);
  }

  getFolderSummaryGovernanceReview(instanceId: string): Promise<GovernanceReviewSummary> {
    return this.get<GovernanceReviewSummary>(`/v4_1/folder-summary/instances/${encodeURIComponent(instanceId)}/governance-review`);
  }

  listFolderSummaryArtifacts(instanceId: string): Promise<FolderSummaryArtifact[]> {
    return this.get<FolderSummaryArtifact[]>(`/v4_1/folder-summary/instances/${encodeURIComponent(instanceId)}/artifacts`);
  }

  getFolderSummaryQualityReport(instanceId: string): Promise<FolderSummaryQualityReport> {
    return this.get<FolderSummaryQualityReport>(`/v4_1/folder-summary/instances/${encodeURIComponent(instanceId)}/quality-report`);
  }

  startControlledRuntimeLocalFolderSummary(payload: {
    folder_path: string;
    user_confirmed: true;
    source: "workflow_console" | "run_panel" | "command_palette" | "tui";
  }): Promise<ControlledRuntimeResult> {
    return this.post<ControlledRuntimeResult>("/v4_2/runtime/workflows/local-folder-summary/start", payload);
  }

  getControlledRuntimeInstance(instanceId: string): Promise<ControlledRuntimeResult> {
    return this.get<ControlledRuntimeResult>(`/v4_2/runtime/instances/${encodeURIComponent(instanceId)}`);
  }

  rerunControlledRuntimeStation(
    instanceId: string,
    payload: { station_id: "markdown_parse"; user_confirmed: true; source: "workflow_console" | "run_panel" | "command_palette" | "tui" },
  ): Promise<ControlledRuntimeResult> {
    return this.post<ControlledRuntimeResult>(`/v4_2/runtime/instances/${encodeURIComponent(instanceId)}/rerun-station`, payload);
  }

  continueControlledRuntimeDownstream(
    instanceId: string,
    payload: { user_confirmed: true; source: "workflow_console" | "run_panel" | "command_palette" | "tui" },
  ): Promise<ControlledRuntimeResult> {
    return this.post<ControlledRuntimeResult>(`/v4_2/runtime/instances/${encodeURIComponent(instanceId)}/continue-downstream`, payload);
  }

  getWorkflow(templateId: string): Promise<WorkflowSummary> {
    return this.get<WorkflowSummary>(`/workflows/${encodeURIComponent(templateId)}`);
  }

  listWorkflowVersions(templateId: string): Promise<WorkflowVersionSummary[]> {
    return this.get<WorkflowVersionSummary[]>(`/workflows/${encodeURIComponent(templateId)}/versions`);
  }

  listInstances(): Promise<WorkflowInstanceSummary[]> {
    return this.get<WorkflowInstanceSummary[]>("/instances");
  }

  getInstanceStatus(instanceId: string): Promise<WorkflowStatus> {
    return this.get<WorkflowStatus>(`/instances/${encodeURIComponent(instanceId)}/status`);
  }

  getBoard(instanceId: string): Promise<WorkflowBoard> {
    return this.get<WorkflowBoard>(`/instances/${encodeURIComponent(instanceId)}/board`);
  }

  getCanvasProjection(instanceId: string): Promise<CanvasDraftProjection> {
    return this.get<CanvasDraftProjection>(`/instances/${encodeURIComponent(instanceId)}/canvas-projection`);
  }

  listNodeCatalog(templateId: string): Promise<NodeCatalogItem[]> {
    return this.get<NodeCatalogItem[]>(`/workflows/${encodeURIComponent(templateId)}/node-catalog`);
  }

  listQuality(instanceId: string): Promise<QualitySummary[]> {
    return this.get<QualitySummary[]>(`/instances/${encodeURIComponent(instanceId)}/quality`);
  }

  listApprovals(instanceId: string): Promise<ApprovalSummary[]> {
    return this.get<ApprovalSummary[]>(`/instances/${encodeURIComponent(instanceId)}/approvals`);
  }

  respondApproval(
    instanceId: string,
    approvalId: string,
    payload: {
      decision: "approve" | "reject";
      reason?: string;
      user_confirmed: true;
      source: "approval_panel";
      proposal_id?: string;
      handoff_id?: string;
    },
  ): Promise<OperationResult<ApprovalSummary>> {
    return this.post<OperationResult<ApprovalSummary>>(
      `/instances/${encodeURIComponent(instanceId)}/approvals/${encodeURIComponent(approvalId)}/respond`,
      payload,
    );
  }

  getContext(instanceId: string): Promise<WorkflowContextSummary> {
    return this.get<WorkflowContextSummary>(`/instances/${encodeURIComponent(instanceId)}/context`);
  }

  updateContext(
    instanceId: string,
    payload: {
      op: "set";
      path: `business.${string}`;
      value: unknown;
      expected_revision?: number;
      user_confirmed?: true;
      source?: "context_panel";
      proposal_id?: string;
      handoff_id?: string;
    },
  ): Promise<OperationResult<WorkflowContextSummary>> {
    return this.post<OperationResult<WorkflowContextSummary>>(
      `/instances/${encodeURIComponent(instanceId)}/context/update`,
      payload as Record<string, unknown>,
    );
  }

  emitBusinessEvent(
    instanceId: string,
    payload: {
      event_type: `business.${string}`;
      payload?: Record<string, unknown>;
      event_id?: string;
      idempotency_key?: string;
      binding?: { target_path: `context.business.${string}`; payload_path: `event.payload.${string}`; mode?: "set" };
      user_confirmed?: true;
      source?: "context_panel";
      proposal_id?: string;
      handoff_id?: string;
    },
  ): Promise<OperationResult<{ context: WorkflowContextSummary }>> {
    return this.post<OperationResult<{ context: WorkflowContextSummary }>>(
      `/instances/${encodeURIComponent(instanceId)}/business-events`,
      payload as Record<string, unknown>,
    );
  }

  listStationOutputs(stationRunId: string): Promise<ArtifactSummary[]> {
    return this.get<ArtifactSummary[]>(`/stations/${encodeURIComponent(stationRunId)}/outputs`);
  }

  listInstanceStationOutputs(instanceId: string, stationRunId: string): Promise<ArtifactSummary[]> {
    return this.get<ArtifactSummary[]>(
      `/instances/${encodeURIComponent(instanceId)}/stations/${encodeURIComponent(stationRunId)}/outputs`,
    );
  }

  getArtifactMetadata(artifactId: string): Promise<ArtifactSummary> {
    return this.get<ArtifactSummary>(`/artifacts/${encodeURIComponent(artifactId)}/metadata`);
  }

  getArtifactLineage(artifactId: string): Promise<Record<string, unknown>> {
    return this.get<Record<string, unknown>>(`/artifacts/${encodeURIComponent(artifactId)}/lineage`);
  }

  proposePatch(templateId: string, payload: CanvasPatchIntent): Promise<WorkflowPatchProposal> {
    return this.post<WorkflowPatchProposal>(`/workflows/${encodeURIComponent(templateId)}/patches`, payload as unknown as Record<string, unknown>);
  }

  listWorkflowPatchQueue(templateId: string, instanceId?: string): Promise<PatchQueueDTO[]> {
    const query = instanceId ? `?workflow_instance_id=${encodeURIComponent(instanceId)}` : "";
    return this.get<PatchQueueDTO[]>(`/workflows/${encodeURIComponent(templateId)}/patches${query}`);
  }

  listInstancePatches(instanceId: string): Promise<PatchQueueDTO[]> {
    return this.get<PatchQueueDTO[]>(`/instances/${encodeURIComponent(instanceId)}/patches`);
  }

  getPatchDiff(templateId: string, patchId: string): Promise<WorkflowPatchDiff> {
    return this.get<WorkflowPatchDiff>(
      `/workflows/${encodeURIComponent(templateId)}/patches/${encodeURIComponent(patchId)}/diff`,
    );
  }

  getInstancePatchDiff(instanceId: string, patchId: string): Promise<WorkflowPatchDiff> {
    return this.get<WorkflowPatchDiff>(
      `/instances/${encodeURIComponent(instanceId)}/patches/${encodeURIComponent(patchId)}/diff`,
    );
  }

  proposeAgentPatch(templateId: string, payload: Record<string, unknown>): Promise<WorkflowPatchProposal> {
    return this.post<WorkflowPatchProposal>(`/workflows/${encodeURIComponent(templateId)}/patches`, payload);
  }

  getAgentSession(instanceId: string): Promise<AgentTalkSession> {
    return this.get<AgentTalkSession>(`/instances/${encodeURIComponent(instanceId)}/agent/session`);
  }

  getAgentInteractionState(instanceId: string): Promise<AgentTalkInteractionState> {
    return this.get<AgentTalkInteractionState>(`/instances/${encodeURIComponent(instanceId)}/agent/interaction-state`);
  }

  sendAgentMessage(
    instanceId: string,
    payload: {
      content: string;
      created_by?: string;
      selected_station_id?: string;
      selected_station_name?: string;
      target_station_id?: string;
      target_station_name?: string;
    },
  ): Promise<AgentTalkSession> {
    return this.post<AgentTalkSession>(`/instances/${encodeURIComponent(instanceId)}/agent/messages`, payload);
  }

  listAgentSuggestions(instanceId: string): Promise<AgentTalkSuggestion[]> {
    return this.get<AgentTalkSuggestion[]>(`/instances/${encodeURIComponent(instanceId)}/agent/suggestions`);
  }

  dismissAgentSuggestion(instanceId: string, suggestionId: string): Promise<AgentTalkSuggestion> {
    return this.post<AgentTalkSuggestion>(
      `/instances/${encodeURIComponent(instanceId)}/agent/suggestions/${encodeURIComponent(suggestionId)}/dismiss`,
      {},
    );
  }

  listAgentActionProposals(instanceId: string): Promise<AgentActionProposal[]> {
    return this.get<AgentActionProposal[]>(`/instances/${encodeURIComponent(instanceId)}/agent/action-proposals`);
  }

  createAgentActionProposal(
    instanceId: string,
    payload: {
      intent_type: string;
      title?: string;
      summary?: string;
      target_panel?: string;
      payload?: Record<string, unknown>;
      risk_flags?: string[];
      requires_approval?: boolean;
    },
  ): Promise<AgentActionProposal> {
    return this.post<AgentActionProposal>(`/instances/${encodeURIComponent(instanceId)}/agent/action-proposals`, payload);
  }

  dismissAgentActionProposal(instanceId: string, proposalId: string): Promise<AgentActionProposal> {
    return this.post<AgentActionProposal>(
      `/instances/${encodeURIComponent(instanceId)}/agent/action-proposals/${encodeURIComponent(proposalId)}/dismiss`,
      {},
    );
  }

  createAgentActionHandoff(
    instanceId: string,
    proposalId: string,
    payload: {
      target_panel: string;
      workflow_patch_id?: string;
      approval_id?: string;
      target_path?: `business.${string}`;
      suggested_form_prefill?: Record<string, unknown>;
    },
  ): Promise<AgentActionHandoff> {
    return this.post<AgentActionHandoff>(
      `/instances/${encodeURIComponent(instanceId)}/agent/action-proposals/${encodeURIComponent(proposalId)}/handoff`,
      payload,
    );
  }

  getAgentActionHandoff(instanceId: string, handoffId: string): Promise<AgentActionHandoff> {
    return this.get<AgentActionHandoff>(
      `/instances/${encodeURIComponent(instanceId)}/agent/action-handoffs/${encodeURIComponent(handoffId)}`,
    );
  }

  listAgentActionHandoffs(instanceId: string): Promise<AgentActionHandoff[]> {
    return this.get<AgentActionHandoff[]>(`/instances/${encodeURIComponent(instanceId)}/agent/action-handoffs`);
  }

  dismissAgentActionHandoff(instanceId: string, handoffId: string): Promise<AgentActionHandoff> {
    return this.post<AgentActionHandoff>(
      `/instances/${encodeURIComponent(instanceId)}/agent/action-handoffs/${encodeURIComponent(handoffId)}/dismiss`,
      {},
    );
  }

  listAgentActionHandoffAudit(instanceId: string, handoffId: string): Promise<AgentHandoffAuditRecord[]> {
    return this.get<AgentHandoffAuditRecord[]>(
      `/instances/${encodeURIComponent(instanceId)}/agent/action-handoffs/${encodeURIComponent(handoffId)}/audit`,
    );
  }

  listOperationEvidence(instanceId: string): Promise<OperationEvidenceRecord[]> {
    return this.get<OperationEvidenceRecord[]>(`/instances/${encodeURIComponent(instanceId)}/agent/operation-evidence`);
  }

  getOperationEvidence(instanceId: string, evidenceId: string): Promise<OperationEvidenceRecord> {
    return this.get<OperationEvidenceRecord>(
      `/instances/${encodeURIComponent(instanceId)}/agent/operation-evidence/${encodeURIComponent(evidenceId)}`,
    );
  }

  getGovernanceReview(instanceId: string): Promise<GovernanceReviewSummary> {
    return this.get<GovernanceReviewSummary>(`/instances/${encodeURIComponent(instanceId)}/agent/governance-review`);
  }

  applyPatch(
    templateId: string,
    patchId: string,
    payload: {
      workflow_instance_id?: string;
      user_confirmed: true;
      source: "editing_panel" | "workflow_console";
      proposal_id?: string;
      handoff_id?: string;
    },
  ): Promise<OperationResult<PatchActionResult>> {
    return this.post<OperationResult<PatchActionResult>>(
      `/workflows/${encodeURIComponent(templateId)}/patches/${encodeURIComponent(patchId)}/apply`,
      payload,
    );
  }

  rejectPatch(
    templateId: string,
    patchId: string,
    payload: {
      workflow_instance_id?: string;
      reason?: string;
      user_confirmed: true;
      source: "editing_panel" | "workflow_console";
      proposal_id?: string;
      handoff_id?: string;
    },
  ): Promise<OperationResult<PatchActionResult>> {
    return this.post<OperationResult<PatchActionResult>>(
      `/workflows/${encodeURIComponent(templateId)}/patches/${encodeURIComponent(patchId)}/reject`,
      payload,
    );
  }

  publishWorkflow(
    templateId: string,
    payload: {
      workflow_instance_id?: string;
      version: string;
      expected_draft_revision: number;
      user_confirmed: true;
      source: "editing_panel" | "workflow_console";
      proposal_id?: string;
      handoff_id?: string;
    },
  ): Promise<OperationResult<PublishVersionResult>> {
    return this.post<OperationResult<PublishVersionResult>>(`/workflows/${encodeURIComponent(templateId)}/publish`, payload);
  }

  connectEvents(channels: string[], onEvent: (event: WorkflowEvent) => void): EventSource {
    const params = new URLSearchParams({ channels: channels.join(","), follow: "true" });
    const heartbeatInterval = (import.meta as unknown as { env?: Record<string, string | undefined> }).env?.VITE_EVENT_HEARTBEAT_INTERVAL;
    if (heartbeatInterval) {
      params.set("heartbeat_interval", heartbeatInterval);
    }
    const url = `${this.basePath}/events/subscribe?${params.toString()}`;
    const source = new EventSource(url);
    const handleMessage = (message: MessageEvent<string>) => {
      try {
        const parsed = JSON.parse(message.data) as WorkflowEvent;
        onEvent({ ...parsed, id: parsed.id || message.lastEventId, type: parsed.type || message.type });
      } catch {
        onEvent({ type: "event.parse_failed", data: { id: message.lastEventId } });
      }
    };
    source.onmessage = handleMessage;
    if (typeof source.addEventListener === "function") {
      for (const eventType of EVENT_SOURCE_TYPES) {
        source.addEventListener(eventType, handleMessage as EventListener);
      }
    }
    return source;
  }

  private async get<T>(path: string): Promise<T> {
    const response = await fetch(`${this.basePath}${path}`, {
      headers: { accept: "application/json" },
    });
    if (!response.ok) {
      throw new Error(`Workflow Console request failed: ${response.status}`);
    }
    return (await response.json()) as T;
  }

  private async post<T>(path: string, payload: Record<string, unknown>): Promise<T> {
    const response = await fetch(`${this.basePath}${path}`, {
      method: "POST",
      headers: {
        accept: "application/json",
        "content-type": "application/json",
      },
      body: JSON.stringify(payload),
    });
    if (!response.ok) {
      throw new Error(`Workflow Console request failed: ${response.status}`);
    }
    return (await response.json()) as T;
  }
}

export const workflowConsoleClient = new WorkflowConsoleClient();

const EVENT_SOURCE_TYPES = [
  "workflow.instance.started",
  "workflow.instance.completed",
  "workflow.instance.failed",
  "station.run.started",
  "station.run.completed",
  "station.run.failed",
  "station.run.waiting_approval",
  "approval.required",
  "approval.approved",
  "approval.rejected",
  "artifact.registered",
  "business.event.received",
  "workflow.context.updated",
  "workflow.patch.proposed",
  "workflow.patch." + "applied",
  "workflow.patch." + "rejected",
  "agent.session.updated",
  "agent.message.created",
  "agent.suggestion.created",
  "agent.suggestion.dismissed",
  "agent.action_proposal.created",
  "agent.action_proposal.dismissed",
  "agent.handoff_created",
  "agent.handoff_opened",
  "operation.evidence.created",
  "governance.review.updated",
];
