import { useCallback, useEffect, useMemo, useState } from "react";
import { demoHighRiskPatchDiff, demoPatchDiff, demoPatchProposal } from "../api/demoData.js";
import type { AgentTalkFixture } from "../api/agentTalkTypes.js";
import type {
  ArtifactSummary,
  ApprovalSummary,
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
  status: WorkflowStatus | null;
  stationOutputs: ArtifactSummary[];
  approvals: ApprovalSummary[];
  quality: QualitySummary[];
  context: WorkflowContextSummary | null;
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
  respondApproval: (approvalId: string, decision: "approve" | "reject", reason?: string) => Promise<void>;
  setBusinessContextValue: (path: `business.${string}`, value: unknown, expectedRevision?: number) => Promise<void>;
  emitBusinessEvent: (
    eventType: `business.${string}`,
    payload?: Record<string, unknown>,
    binding?: { target_path: `context.business.${string}`; payload_path: `event.payload.${string}`; mode?: "set" },
  ) => Promise<void>;
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
  const [status, board] = selectedInstanceId
    ? await Promise.all([client.getInstanceStatus(selectedInstanceId), client.getBoard(selectedInstanceId)])
    : [null, null];
  const firstRunId = firstStationRunId(board);
  const [stationOutputs, approvals, quality, context] = selectedInstanceId
    ? await Promise.all([
        firstRunId ? listOutputsForInstance(client, selectedInstanceId, firstRunId) : Promise.resolve([]),
        client.listApprovals(selectedInstanceId),
        client.listQuality(selectedInstanceId),
        client.getContext(selectedInstanceId),
      ])
    : [[], [], [], null];
  return {
    workflows,
    versions,
    instances,
    selectedWorkflowId,
    selectedVersionId,
    selectedInstanceId,
    board,
    status,
    stationOutputs,
    approvals,
    quality,
    context,
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
    `${workflowPatch}applied`,
  ].includes(event.type);
}

export async function refreshWorkflowConsoleRuntimeState(
  client: WorkflowConsoleClient,
  current: LoadedWorkflowConsoleData,
): Promise<LoadedWorkflowConsoleData> {
  if (!current.selectedInstanceId) {
    return current;
  }
  const [status, board, approvals, quality, context] = await Promise.all([
    client.getInstanceStatus(current.selectedInstanceId),
    client.getBoard(current.selectedInstanceId),
    client.listApprovals(current.selectedInstanceId),
    client.listQuality(current.selectedInstanceId),
    client.getContext(current.selectedInstanceId),
  ]);
  const runId = firstStationRunId(board);
  const stationOutputs = runId ? await listOutputsForInstance(client, current.selectedInstanceId, runId) : [];
  return { ...current, status, board, approvals, quality, context, stationOutputs };
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
    status: null,
    stationOutputs: [],
    approvals: [],
    quality: [],
    context: null,
  });
  const [loading, setLoading] = useState(!demoEnabled);
  const [error, setError] = useState<string | null>(null);
  const [events, setEvents] = useState<WorkflowEvent[]>([]);
  const [eventState, setEventState] = useState<WorkflowConsoleDataState["eventState"]>("idle");

  const applyAsyncUpdate = useCallback(
    (updater: (current: LoadedWorkflowConsoleData) => Promise<LoadedWorkflowConsoleData>) => {
      setLoading(true);
      setError(null);
      setLoaded((current) => {
        void updater(current)
          .then((updated) => {
            setLoaded((latest) => ({ ...latest, ...updated }));
          })
          .catch((caught: unknown) => {
            setError(caught instanceof Error ? caught.message : "Workflow Console request failed");
          })
          .finally(() => setLoading(false));
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
                return { ...current, ...updated };
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
      }
    : {
        ...loaded,
        mode: "real" as const,
        loading,
        empty: !loading && !error && (loaded.workflows.length === 0 || loaded.instances.length === 0),
        error,
        eventState,
        events,
        patchProposal: demoPatchProposal,
        patchDiff: demoPatchDiff,
        highRiskPatchDiff: demoHighRiskPatchDiff,
        agentTalkFixture: undefined,
        setSelectedWorkflowId: (value: string) =>
          applyAsyncUpdate(async (current) => {
            const versions = value ? await client.listWorkflowVersions(value) : [];
            const selectedVersionId = versions[0]?.workflow_version_id || "";
            const selectedInstanceId =
              current.instances.find((item) => item.workflow_template_id === value && (!selectedVersionId || item.workflow_version_id === selectedVersionId))
                ?.workflow_instance_id || "";
            return loadInstanceRuntimeState(client, { ...current, selectedWorkflowId: value, versions, selectedVersionId }, selectedInstanceId);
          }),
        setSelectedVersionId: (value: string) =>
          applyAsyncUpdate(async (current) => {
            const selectedInstanceId =
              current.instances.find((item) => item.workflow_template_id === current.selectedWorkflowId && item.workflow_version_id === value)
                ?.workflow_instance_id || "";
            return loadInstanceRuntimeState(client, { ...current, selectedVersionId: value }, selectedInstanceId);
          }),
        setSelectedInstanceId: (value: string) => applyAsyncUpdate((current) => loadInstanceRuntimeState(client, current, value)),
        respondApproval: async (approvalId: string, decision: "approve" | "reject", reason?: string) => {
          await client.respondApproval(loaded.selectedInstanceId, approvalId, {
            decision,
            reason,
            user_confirmed: true,
            source: "approval_panel",
          });
          applyAsyncUpdate((current) => refreshWorkflowConsoleRuntimeState(client, current));
        },
        setBusinessContextValue: async (path: `business.${string}`, value: unknown, expectedRevision?: number) => {
          await client.updateContext(loaded.selectedInstanceId, { op: "set", path, value, expected_revision: expectedRevision });
          applyAsyncUpdate((current) => refreshWorkflowConsoleRuntimeState(client, current));
        },
        emitBusinessEvent: async (
          eventType: `business.${string}`,
          payload?: Record<string, unknown>,
          binding?: { target_path: `context.business.${string}`; payload_path: `event.payload.${string}`; mode?: "set" },
        ) => {
          await client.emitBusinessEvent(loaded.selectedInstanceId, { event_type: eventType, payload, binding });
          applyAsyncUpdate((current) => refreshWorkflowConsoleRuntimeState(client, current));
        },
      };

  return useMemo(() => state, [state]);
}
