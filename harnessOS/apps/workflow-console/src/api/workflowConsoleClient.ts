import type {
  ArtifactSummary,
  WorkflowPatchDiff,
  WorkflowPatchProposal,
  WorkflowBoard,
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

  listStationOutputs(stationRunId: string): Promise<ArtifactSummary[]> {
    return this.get<ArtifactSummary[]>(`/stations/${encodeURIComponent(stationRunId)}/outputs`);
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

  proposeAgentPatch(templateId: string, payload: Record<string, unknown>): Promise<WorkflowPatchProposal> {
    return this.post<WorkflowPatchProposal>(`/workflows/${encodeURIComponent(templateId)}/patches/propose`, payload);
  }

  connectEvents(channels: string[], onEvent: (event: WorkflowEvent) => void): EventSource {
    const url = `${this.basePath}/events/subscribe?channels=${encodeURIComponent(channels.join(","))}`;
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
