import type {
  ArtifactSummary,
  ApprovalSummary,
  OperationResult,
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

  listQuality(instanceId: string): Promise<QualitySummary[]> {
    return this.get<QualitySummary[]>(`/instances/${encodeURIComponent(instanceId)}/quality`);
  }

  listApprovals(instanceId: string): Promise<ApprovalSummary[]> {
    return this.get<ApprovalSummary[]>(`/instances/${encodeURIComponent(instanceId)}/approvals`);
  }

  respondApproval(
    instanceId: string,
    approvalId: string,
    payload: { decision: "approve" | "reject"; reason?: string; user_confirmed: true; source: "approval_panel" },
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
    payload: { op: "set"; path: `business.${string}`; value: unknown; expected_revision?: number },
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

  proposePatch(templateId: string, payload: Record<string, unknown>): Promise<WorkflowPatchProposal> {
    return this.post<WorkflowPatchProposal>(`/workflows/${encodeURIComponent(templateId)}/patches/propose`, payload);
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
    return this.post<WorkflowPatchProposal>(`/workflows/${encodeURIComponent(templateId)}/patches/propose`, payload);
  }

  connectEvents(channels: string[], onEvent: (event: WorkflowEvent) => void): EventSource {
    const params = new URLSearchParams({ channels: channels.join(","), follow: "true" });
    const url = `${this.basePath}/events/subscribe?${params.toString()}`;
    const source = new EventSource(url);
    source.onmessage = (message) => {
      try {
        onEvent(JSON.parse(message.data) as WorkflowEvent);
      } catch {
        onEvent({ type: "event.parse_failed", data: { id: message.lastEventId } });
      }
    };
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
