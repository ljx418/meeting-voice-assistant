import { useCallback, useEffect, useMemo, useState } from "react";
import type { AgentTalkFixture } from "../api/agentTalkTypes.js";
import type {
  AgentActionProposal,
  AgentActionHandoff,
  AgentTalkInteractionState,
  AgentTalkSession,
  AgentTalkSuggestion,
  ArtifactSummary,
  ApprovalSummary,
  CanvasPatchIntent,
  CanvasDraftProjection,
  GovernanceReviewSummary,
  NodeCatalogItem,
  OperationEvidenceRecord,
  PatchQueueDTO,
  QualitySummary,
  WorkflowBoard,
  WorkflowContextSummary,
  WorkflowEvent,
  WorkflowInstanceSummary,
  WorkflowPatchDiff,
  WorkflowPatchProposal,
  WorkflowStatus,
  WorkflowSummary,
  WorkflowVersionSummary,
} from "../api/types.js";
import { WorkflowConsoleClient, workflowConsoleClient } from "../api/workflowConsoleClient.js";
import { useWorkflowConsoleDemo } from "./useWorkflowConsoleDemo.js";

export type WorkflowConsoleMode = "real" | "demo";

export interface LoadedWorkflowConsoleData {
  workflows: WorkflowSummary[];
  versions: WorkflowVersionSummary[];
  instances: WorkflowInstanceSummary[];
  selectedWorkflowId: string;
  selectedVersionId: string;
  selectedInstanceId: string;
  board: WorkflowBoard | null;
  canvasProjection?: CanvasDraftProjection | null;
  nodeCatalog?: NodeCatalogItem[];
  patchQueue?: PatchQueueDTO[];
  status: WorkflowStatus | null;
  stationOutputs: ArtifactSummary[];
  approvals: ApprovalSummary[];
  quality: QualitySummary[];
  context: WorkflowContextSummary | null;
  patchProposal?: WorkflowPatchProposal;
  patchDiff?: WorkflowPatchDiff;
  agentSession?: AgentTalkSession;
  agentInteractionState?: AgentTalkInteractionState | null;
  agentSuggestions?: AgentTalkSuggestion[];
  agentActionProposals?: AgentActionProposal[];
  activeAgentHandoff?: AgentActionHandoff | null;
  operationEvidence?: OperationEvidenceRecord[];
  governanceReview?: GovernanceReviewSummary | null;
}

export interface WorkflowConsoleDataState extends LoadedWorkflowConsoleData {
  mode: WorkflowConsoleMode;
  loading: boolean;
  empty: boolean;
  error: string | null;
  events: WorkflowEvent[];
  patchProposal?: WorkflowPatchProposal;
  patchDiff?: WorkflowPatchDiff;
  highRiskPatchDiff?: WorkflowPatchDiff;
  agentTalkFixture?: AgentTalkFixture;
  eventState: "idle" | "connecting" | "connected" | "reconnecting" | "error" | "disconnected";
  setSelectedWorkflowId: (value: string) => void;
  setSelectedVersionId: (value: string) => void;
  setSelectedInstanceId: (value: string) => void;
  respondApproval: (approvalId: string, decision: "approve" | "reject", reason?: string, handoff?: AgentActionHandoff | null) => Promise<void>;
  setBusinessContextValue: (path: `business.${string}`, value: unknown, expectedRevision?: number, handoff?: AgentActionHandoff | null) => Promise<void>;
  emitBusinessEvent: (
    eventType: `business.${string}`,
    payload?: Record<string, unknown>,
    binding?: { target_path: `context.business.${string}`; payload_path: `event.payload.${string}`; mode?: "set" },
    handoff?: AgentActionHandoff | null,
  ) => Promise<void>;
  applyPatch: (patchId: string, handoff?: AgentActionHandoff | null) => Promise<void>;
  rejectPatch: (patchId: string, reason?: string, handoff?: AgentActionHandoff | null) => Promise<void>;
  publishWorkflowVersion: (version: string, expectedDraftRevision: number, handoff?: AgentActionHandoff | null) => Promise<void>;
  proposeCanvasPatch: (intent: CanvasPatchIntent) => Promise<void>;
  sendAgentMessage: (content: string) => Promise<void>;
  dismissAgentSuggestion: (suggestionId: string) => Promise<void>;
  dismissAgentActionProposal: (proposalId: string) => Promise<void>;
  createAgentActionHandoff: (proposal: AgentActionProposal, targetPanel: AgentActionHandoff["target_panel"]) => Promise<AgentActionHandoff>;
}

export function isDemoMode(env: Record<string, unknown> = {}): boolean {
  return String(env.VITE_HARNESSOS_DEMO_MODE || "").trim().toLowerCase() === "true";
}

export async function loadWorkflowConsoleData(client: WorkflowConsoleClient): Promise<LoadedWorkflowConsoleData> {
  const workflows = await client.listWorkflows();
  const selectedWorkflowId = workflows[0]?.workflow_template_id || "";
  const versions = selectedWorkflowId ? await client.listWorkflowVersions(selectedWorkflowId) : [];
  const instances = await client.listInstances();
  const selectedVersionId = versions[0]?.workflow_version_id || "";
  const selectedInstanceId = instances[0]?.workflow_instance_id || "";
  const [status, runtimeBoard, canvasProjection] = selectedInstanceId
    ? await Promise.all([client.getInstanceStatus(selectedInstanceId), client.getBoard(selectedInstanceId), getCanvasProjectionOptional(client, selectedInstanceId)])
    : [null, null, null];
  const board = runtimeBoard && canvasProjection ? projectBoardForCanvas(runtimeBoard, canvasProjection) : runtimeBoard;
  const firstRunId = firstStationRunId(board);
  const [stationOutputs, approvals, quality, context] = selectedInstanceId
    ? await Promise.all([
        firstRunId ? listOutputsForInstance(client, selectedInstanceId, firstRunId) : Promise.resolve([]),
        client.listApprovals(selectedInstanceId),
        client.listQuality(selectedInstanceId),
        client.getContext(selectedInstanceId),
      ])
    : [[], [], [], null];
  const nodeCatalog = selectedWorkflowId ? await getNodeCatalogOptional(client, selectedWorkflowId) : [];
  const [patchState, agentState, governanceState] = selectedInstanceId
    ? await Promise.all([
        loadPatchState(client, selectedWorkflowId, selectedInstanceId),
        loadAgentState(client, selectedInstanceId),
        loadGovernanceState(client, selectedInstanceId),
      ])
    : [{}, {}, {}];
  return {
    workflows,
    versions,
    instances,
    selectedWorkflowId,
    selectedVersionId,
    selectedInstanceId,
    board,
    canvasProjection,
    nodeCatalog,
    status,
    stationOutputs,
    approvals,
    quality,
    context,
    ...patchState,
    ...agentState,
    ...governanceState,
  };
}

export function shouldRefreshForEvent(event: WorkflowEvent): boolean {
  const workflowInstance = "workflow.instance.";
  const stationRun = "station.run.";
  const workflowPatch = "workflow.patch.";
  return [
    `${workflowInstance}started`,
    `${workflowInstance}completed`,
    `${workflowInstance}failed`,
    `${stationRun}started`,
    `${stationRun}completed`,
    `${stationRun}failed`,
    `${stationRun}waiting_approval`,
    "approval.required",
    "approval.approved",
    "approval.rejected",
    "artifact.registered",
    "business.event.received",
    "workflow.context.updated",
    `${workflowPatch}proposed`,
    `${workflowPatch}applied`,
    `${workflowPatch}rejected`,
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
  ].includes(event.type);
}

export async function refreshWorkflowConsoleRuntimeState(
  client: WorkflowConsoleClient,
  current: LoadedWorkflowConsoleData,
): Promise<LoadedWorkflowConsoleData> {
  if (!current.selectedInstanceId) {
    return current;
  }
  const [status, runtimeBoard, canvasProjection, approvals, quality, context] = await Promise.all([
    client.getInstanceStatus(current.selectedInstanceId),
    client.getBoard(current.selectedInstanceId),
    getCanvasProjectionOptional(client, current.selectedInstanceId),
    client.listApprovals(current.selectedInstanceId),
    client.listQuality(current.selectedInstanceId),
    client.getContext(current.selectedInstanceId),
  ]);
  const board = runtimeBoard && canvasProjection ? projectBoardForCanvas(runtimeBoard, canvasProjection) : runtimeBoard;
  const [versions, patchState] = await Promise.all([
    current.selectedWorkflowId && typeof client.listWorkflowVersions === "function"
      ? client.listWorkflowVersions(current.selectedWorkflowId)
      : Promise.resolve(current.versions),
    current.selectedWorkflowId ? loadPatchState(client, current.selectedWorkflowId, current.selectedInstanceId) : Promise.resolve({}),
  ]);
  const [agentState, governanceState] = await Promise.all([
    loadAgentState(client, current.selectedInstanceId),
    loadGovernanceState(client, current.selectedInstanceId),
  ]);
  const runId = firstStationRunId(board);
  const stationOutputs = runId ? await listOutputsForInstance(client, current.selectedInstanceId, runId) : [];
  return { ...current, versions, status, board, canvasProjection, approvals, quality, context, stationOutputs, ...patchState, ...agentState, ...governanceState };
}

async function loadAgentState(
  client: WorkflowConsoleClient,
  instanceId: string,
): Promise<{ agentSession?: AgentTalkSession; agentInteractionState?: AgentTalkInteractionState | null; agentSuggestions?: AgentTalkSuggestion[]; agentActionProposals?: AgentActionProposal[] }> {
  const candidate = client as WorkflowConsoleClient & {
    getAgentSession?: (instanceId: string) => Promise<AgentTalkSession>;
    getAgentInteractionState?: (instanceId: string) => Promise<AgentTalkInteractionState>;
    listAgentSuggestions?: (instanceId: string) => Promise<AgentTalkSuggestion[]>;
    listAgentActionProposals?: (instanceId: string) => Promise<AgentActionProposal[]>;
  };
  if (!candidate.getAgentSession || !candidate.listAgentSuggestions) {
    return {};
  }
  const [agentSession, agentInteractionState, agentSuggestions, agentActionProposals] = await Promise.all([
    candidate.getAgentSession(instanceId),
    candidate.getAgentInteractionState ? candidate.getAgentInteractionState(instanceId) : Promise.resolve(null),
    candidate.listAgentSuggestions(instanceId),
    candidate.listAgentActionProposals ? candidate.listAgentActionProposals(instanceId) : Promise.resolve([]),
  ]);
  return { agentSession, agentInteractionState, agentSuggestions, agentActionProposals };
}

async function getCanvasProjectionOptional(client: WorkflowConsoleClient, instanceId: string): Promise<CanvasDraftProjection | null> {
  const candidate = client as WorkflowConsoleClient & {
    getCanvasProjection?: (instanceId: string) => Promise<CanvasDraftProjection>;
  };
  if (!candidate.getCanvasProjection) {
    return null;
  }
  return candidate.getCanvasProjection(instanceId);
}

async function getNodeCatalogOptional(client: WorkflowConsoleClient, templateId: string): Promise<NodeCatalogItem[]> {
  const candidate = client as WorkflowConsoleClient & {
    listNodeCatalog?: (templateId: string) => Promise<NodeCatalogItem[]>;
  };
  if (!candidate.listNodeCatalog) {
    return [];
  }
  return candidate.listNodeCatalog(templateId);
}

async function loadGovernanceState(
  client: WorkflowConsoleClient,
  instanceId: string,
): Promise<{ operationEvidence?: OperationEvidenceRecord[]; governanceReview?: GovernanceReviewSummary | null }> {
  const candidate = client as WorkflowConsoleClient & {
    listOperationEvidence?: (instanceId: string) => Promise<OperationEvidenceRecord[]>;
    getGovernanceReview?: (instanceId: string) => Promise<GovernanceReviewSummary>;
  };
  if (!candidate.listOperationEvidence || !candidate.getGovernanceReview) {
    return {};
  }
  const [operationEvidence, governanceReview] = await Promise.all([
    candidate.listOperationEvidence(instanceId),
    candidate.getGovernanceReview(instanceId),
  ]);
  return { operationEvidence, governanceReview };
}

async function loadPatchState(
  client: WorkflowConsoleClient,
  templateId: string,
  instanceId: string,
): Promise<{ patchQueue?: PatchQueueDTO[]; patchProposal?: WorkflowPatchProposal; patchDiff?: WorkflowPatchDiff }> {
  const candidate = client as WorkflowConsoleClient & {
    listWorkflowPatchQueue?: (templateId: string, instanceId?: string) => Promise<PatchQueueDTO[]>;
    listInstancePatches?: (instanceId: string) => Promise<PatchQueueDTO[]>;
  };
  if ((!candidate.listWorkflowPatchQueue && !candidate.listInstancePatches) || !templateId || !instanceId) {
    return {};
  }
  const patches = candidate.listWorkflowPatchQueue
    ? await candidate.listWorkflowPatchQueue(templateId, instanceId)
    : await candidate.listInstancePatches!(instanceId);
  const patchProposal =
    patches.find((patch) => patch.selected && patch.status !== "stale") ||
    patches.find((patch) => patch.status === "proposed" && !patch.requires_approval) ||
    patches.find((patch) => patch.status === "applied") ||
    patches.find((patch) => patch.status === "proposed") ||
    patches[0];
  if (!patchProposal?.workflow_patch_id) {
    return { patchQueue: patches };
  }
  const patchDiff = await client.getPatchDiff(templateId, patchProposal.workflow_patch_id);
  return { patchQueue: patches, patchProposal, patchDiff };
}

function listOutputsForInstance(client: WorkflowConsoleClient, instanceId: string, stationRunId: string): Promise<ArtifactSummary[]> {
  const candidate = client as WorkflowConsoleClient & {
    listInstanceStationOutputs?: (instanceId: string, stationRunId: string) => Promise<ArtifactSummary[]>;
  };
  if (candidate.listInstanceStationOutputs) {
    return candidate.listInstanceStationOutputs(instanceId, stationRunId);
  }
  if (!client.listStationOutputs) {
    return Promise.resolve([]);
  }
  return client.listStationOutputs(stationRunId);
}

function firstStationRunId(board: WorkflowBoard | null): string {
  return board?.stations?.find((station) => station.runs?.[0])?.runs?.[0]?.station_run_id || "";
}

export function projectBoardForCanvas(runtimeBoard: WorkflowBoard, projection: CanvasDraftProjection): WorkflowBoard {
  const runtimeStations = new Map(runtimeBoard.stations.map((station) => [station.station.station_id, station]));
  return {
    ...runtimeBoard,
    stations: projection.nodes.map((node) => {
      const existing = runtimeStations.get(node.station_id);
      if (existing) {
        return existing;
      }
      return {
        station: {
          station_id: node.station_id,
          name: node.name,
          role: node.role || node.station_kind,
        },
        status: "draft_only",
        runs: [],
      };
    }),
  };
}

function mergeLoadedState(current: LoadedWorkflowConsoleData, updated: LoadedWorkflowConsoleData): LoadedWorkflowConsoleData {
  return { ...current, ...updated };
}

async function loadInstanceRuntimeState(
  client: WorkflowConsoleClient,
  current: LoadedWorkflowConsoleData,
  selectedInstanceId: string,
): Promise<LoadedWorkflowConsoleData> {
  if (!selectedInstanceId) {
    return { ...current, selectedInstanceId, board: null, status: null, stationOutputs: [], approvals: [], quality: [], context: null };
  }
  const next = { ...current, selectedInstanceId };
  return refreshWorkflowConsoleRuntimeState(client, next);
}

export function useWorkflowConsoleData(client: WorkflowConsoleClient = workflowConsoleClient): WorkflowConsoleDataState {
  const demo = useWorkflowConsoleDemo();
  const demoEnabled = isDemoMode((import.meta as unknown as { env?: Record<string, unknown> }).env || {});
  const [loaded, setLoaded] = useState<LoadedWorkflowConsoleData>({
    workflows: [],
    versions: [],
    instances: [],
    selectedWorkflowId: "",
    selectedVersionId: "",
        selectedInstanceId: "",
        board: null,
        canvasProjection: null,
        nodeCatalog: [],
        patchQueue: [],
        status: null,
        stationOutputs: [],
        approvals: [],
        quality: [],
        context: null,
        patchProposal: undefined,
        patchDiff: undefined,
	        agentSession: undefined,
	        agentInteractionState: null,
	        agentSuggestions: [],
        agentActionProposals: [],
        operationEvidence: [],
        governanceReview: null,
  });
  const [loading, setLoading] = useState(!demoEnabled);
  const [error, setError] = useState<string | null>(null);
  const [events, setEvents] = useState<WorkflowEvent[]>([]);
  const [eventState, setEventState] = useState<WorkflowConsoleDataState["eventState"]>("idle");

  const applyAsyncUpdate = useCallback(
    (updater: (current: LoadedWorkflowConsoleData) => Promise<LoadedWorkflowConsoleData>) => {
      setError(null);
      setLoaded((current) => {
        void updater(current)
          .then((updated) => {
            setLoaded((latest) => mergeLoadedState(latest, updated));
          })
          .catch((caught: unknown) => {
            setError(caught instanceof Error ? caught.message : "Workflow Console request failed");
          });
        return current;
      });
    },
    [],
  );

  useEffect(() => {
    if (demoEnabled) {
      return;
    }
    let active = true;
    setLoading(true);
    setError(null);
    loadWorkflowConsoleData(client)
      .then((data) => {
        if (!active) {
          return;
        }
        setLoaded(data);
      })
      .catch((caught: unknown) => {
        if (!active) {
          return;
        }
        setError(caught instanceof Error ? caught.message : "Workflow Console request failed");
      })
      .finally(() => {
        if (active) {
          setLoading(false);
        }
      });
    return () => {
      active = false;
    };
  }, [client, demoEnabled]);

  useEffect(() => {
    if (demoEnabled || !loaded.selectedInstanceId || error) {
      return;
    }
    let refreshTimer: ReturnType<typeof setTimeout> | undefined;
    setEventState("connecting");
    const source = client.connectEvents(
      ["approval", "artifact", "workflow_patch", "business", "workflow_context"],
      (event) => {
        setEvents((current) => [{ ...event, source: "live" as const }, ...current].slice(0, 50));
        if (shouldRefreshForEvent(event)) {
          if (refreshTimer) {
            clearTimeout(refreshTimer);
          }
          refreshTimer = setTimeout(() => {
            void refreshWorkflowConsoleRuntimeState(client, loaded).then((updated) => {
              setLoaded((current) => {
                if (current.selectedInstanceId !== updated.selectedInstanceId) {
                  return current;
                }
                return mergeLoadedState(current, updated);
              });
            });
          }, 250);
        }
      },
    );
    source.onopen = () => setEventState("connected");
    source.onerror = () => setEventState((current) => (current === "connected" ? "reconnecting" : "error"));
    return () => {
      if (refreshTimer) {
        clearTimeout(refreshTimer);
      }
      source.close();
      setEventState("disconnected");
    };
  }, [client, demoEnabled, error, loaded.selectedInstanceId]);

  useEffect(() => {
    if (demoEnabled || !loaded.selectedInstanceId || loaded.activeAgentHandoff) {
      return;
    }
    const handoffId = recoveryHandoffId();
    if (!handoffId) {
      return;
    }
    let active = true;
    client
      .getAgentActionHandoff(loaded.selectedInstanceId, handoffId)
      .then((handoff) => {
        if (active) {
          setLoaded((current) => ({ ...current, activeAgentHandoff: handoff }));
        }
      })
      .catch((caught: unknown) => setError(caught instanceof Error ? caught.message : "Agent handoff recovery failed"));
    return () => {
      active = false;
    };
  }, [client, demoEnabled, loaded.activeAgentHandoff, loaded.selectedInstanceId]);

  const state = demoEnabled
    ? {
        ...demo,
        mode: "demo" as const,
        loading: false,
        empty: false,
        error: null,
        eventState: "idle" as const,
        respondApproval: async () => undefined,
        setBusinessContextValue: async () => undefined,
        emitBusinessEvent: async () => undefined,
        applyPatch: async () => undefined,
        rejectPatch: async () => undefined,
        publishWorkflowVersion: async () => undefined,
        proposeCanvasPatch: async () => undefined,
        sendAgentMessage: async () => undefined,
        dismissAgentSuggestion: async () => undefined,
        dismissAgentActionProposal: async () => undefined,
        createAgentActionHandoff: async () => {
          throw new Error("Demo mode does not create runtime handoffs");
        },
        stationOutputs: [],
        approvals: demo.board.approvals || [],
        quality: demo.board.quality_evaluations || [],
        context: demo.agentTalkFixture?.context_summary
          ? {
              workflow_instance_id: demo.selectedInstanceId,
              revision: 1,
              business: demo.agentTalkFixture.context_summary.business,
            }
          : null,
	        operationEvidence: [],
	        governanceReview: null,
	        agentInteractionState: null,
	      }
    : {
        ...loaded,
        mode: "real" as const,
        loading,
        empty: !loading && !error && (loaded.workflows.length === 0 || loaded.instances.length === 0),
        error,
        eventState,
        events,
        patchProposal: loaded.patchProposal,
        patchQueue: loaded.patchQueue || [],
        patchDiff: loaded.patchDiff,
        highRiskPatchDiff: undefined,
	        agentTalkFixture: undefined,
	        agentSession: loaded.agentSession,
	        agentInteractionState: loaded.agentInteractionState || null,
	        agentSuggestions: loaded.agentSuggestions || [],
        agentActionProposals: loaded.agentActionProposals || [],
        operationEvidence: loaded.operationEvidence || [],
        governanceReview: loaded.governanceReview || null,
        setSelectedWorkflowId: (value: string) =>
          applyAsyncUpdate(async (current) => {
            const versions = value ? await client.listWorkflowVersions(value) : [];
            const nodeCatalog = value ? await getNodeCatalogOptional(client, value) : [];
            const selectedVersionId = versions[0]?.workflow_version_id || "";
            const selectedInstanceId =
              current.instances.find((item) => item.workflow_template_id === value && (!selectedVersionId || item.workflow_version_id === selectedVersionId))
                ?.workflow_instance_id || "";
            return loadInstanceRuntimeState(client, { ...current, selectedWorkflowId: value, versions, selectedVersionId, nodeCatalog }, selectedInstanceId);
          }),
        setSelectedVersionId: (value: string) =>
          applyAsyncUpdate(async (current) => {
            const selectedInstanceId =
              current.instances.find((item) => item.workflow_template_id === current.selectedWorkflowId && item.workflow_version_id === value)
                ?.workflow_instance_id || "";
            return loadInstanceRuntimeState(client, { ...current, selectedVersionId: value }, selectedInstanceId);
          }),
        setSelectedInstanceId: (value: string) => applyAsyncUpdate((current) => loadInstanceRuntimeState(client, current, value)),
        respondApproval: async (approvalId: string, decision: "approve" | "reject", reason?: string, handoff?: AgentActionHandoff | null) => {
          await client.respondApproval(loaded.selectedInstanceId, approvalId, {
            decision,
            reason,
            user_confirmed: true,
            source: "approval_panel",
            proposal_id: handoff?.proposal_id,
            handoff_id: handoff?.handoff_id,
          });
          applyAsyncUpdate((current) => refreshWorkflowConsoleRuntimeState(client, current));
        },
        setBusinessContextValue: async (path: `business.${string}`, value: unknown, expectedRevision?: number, handoff?: AgentActionHandoff | null) => {
          await client.updateContext(loaded.selectedInstanceId, {
            op: "set",
            path,
            value,
            expected_revision: expectedRevision,
            user_confirmed: true,
            source: "context_panel",
            proposal_id: handoff?.proposal_id,
            handoff_id: handoff?.handoff_id,
          });
          applyAsyncUpdate((current) => refreshWorkflowConsoleRuntimeState(client, current));
        },
        emitBusinessEvent: async (
          eventType: `business.${string}`,
          payload?: Record<string, unknown>,
          binding?: { target_path: `context.business.${string}`; payload_path: `event.payload.${string}`; mode?: "set" },
          handoff?: AgentActionHandoff | null,
        ) => {
          await client.emitBusinessEvent(loaded.selectedInstanceId, {
            event_type: eventType,
            payload,
            binding,
            user_confirmed: true,
            source: "context_panel",
            proposal_id: handoff?.proposal_id,
            handoff_id: handoff?.handoff_id,
          });
          applyAsyncUpdate((current) => refreshWorkflowConsoleRuntimeState(client, current));
        },
        applyPatch: async (patchId: string, handoff?: AgentActionHandoff | null) => {
          await client.applyPatch(loaded.selectedWorkflowId, patchId, {
            workflow_instance_id: loaded.selectedInstanceId,
            user_confirmed: true,
            source: "editing_panel",
            proposal_id: handoff?.proposal_id,
            handoff_id: handoff?.handoff_id,
          });
          const updated = await refreshWorkflowConsoleRuntimeState(client, loaded);
          setLoaded((current) => mergeLoadedState(current, updated));
        },
        rejectPatch: async (patchId: string, reason?: string, handoff?: AgentActionHandoff | null) => {
          await client.rejectPatch(loaded.selectedWorkflowId, patchId, {
            workflow_instance_id: loaded.selectedInstanceId,
            reason,
            user_confirmed: true,
            source: "editing_panel",
            proposal_id: handoff?.proposal_id,
            handoff_id: handoff?.handoff_id,
          });
          applyAsyncUpdate((current) => refreshWorkflowConsoleRuntimeState(client, current));
        },
        publishWorkflowVersion: async (version: string, expectedDraftRevision: number, handoff?: AgentActionHandoff | null) => {
          await client.publishWorkflow(loaded.selectedWorkflowId, {
            workflow_instance_id: loaded.selectedInstanceId,
            version,
            expected_draft_revision: expectedDraftRevision,
            user_confirmed: true,
            source: "editing_panel",
            proposal_id: handoff?.proposal_id,
            handoff_id: handoff?.handoff_id,
          });
          applyAsyncUpdate((current) => refreshWorkflowConsoleRuntimeState(client, current));
        },
        proposeCanvasPatch: async (intent: CanvasPatchIntent) => {
          const proposal = await client.proposePatch(loaded.selectedWorkflowId, intent);
          setLoaded((current) => ({ ...current, patchProposal: proposal, patchDiff: undefined }));
          const [diff, updated] = await Promise.all([
            client.getPatchDiff(loaded.selectedWorkflowId, proposal.workflow_patch_id),
            refreshWorkflowConsoleRuntimeState(client, loaded),
          ]);
          setLoaded((current) => ({ ...mergeLoadedState(current, updated), patchProposal: proposal, patchDiff: diff }));
        },
        sendAgentMessage: async (content: string) => {
          const agentSession = await client.sendAgentMessage(loaded.selectedInstanceId, { content, created_by: "workflow_console" });
          setLoaded((current) => ({
            ...current,
            agentSession,
            agentSuggestions: agentSession.suggestions,
            agentActionProposals: current.agentActionProposals,
          }));
          applyAsyncUpdate((current) => refreshWorkflowConsoleRuntimeState(client, current));
        },
        dismissAgentSuggestion: async (suggestionId: string) => {
          await client.dismissAgentSuggestion(loaded.selectedInstanceId, suggestionId);
          applyAsyncUpdate((current) => refreshWorkflowConsoleRuntimeState(client, current));
        },
        dismissAgentActionProposal: async (proposalId: string) => {
          await client.dismissAgentActionProposal(loaded.selectedInstanceId, proposalId);
          applyAsyncUpdate((current) => refreshWorkflowConsoleRuntimeState(client, current));
        },
        createAgentActionHandoff: async (proposal: AgentActionProposal, targetPanel: AgentActionHandoff["target_panel"]) => {
          const resource = proposal.resource_refs || {};
          const handoff = await client.createAgentActionHandoff(loaded.selectedInstanceId, proposal.proposal_id, {
            target_panel: targetPanel,
            workflow_patch_id: typeof proposal.workflow_patch_id === "string" ? proposal.workflow_patch_id : undefined,
            approval_id: typeof resource.approval_id === "string" ? resource.approval_id : undefined,
            target_path: targetPanel === "context_panel" ? "business.operator_note" : undefined,
            suggested_form_prefill: proposal.payload_summary,
          });
          setLoaded((current) => ({ ...current, activeAgentHandoff: handoff }));
          return handoff;
        },
      };

  return useMemo(() => state, [state]);
}

function recoveryHandoffId(): string {
  if (typeof window === "undefined") {
    return "";
  }
  return new URLSearchParams(window.location.search).get("handoff_id") || "";
}
