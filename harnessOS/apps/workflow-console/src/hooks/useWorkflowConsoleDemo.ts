import { useMemo, useState } from "react";
import type { AgentTalkFixture } from "../api/agentTalkTypes.js";
import {
  demoBoard,
  demoAgentTalkFixture,
  demoEvents,
  demoHighRiskPatchDiff,
  demoInstances,
  demoPatchDiff,
  demoPatchProposal,
  demoStatus,
  demoVersions,
  demoWorkflows,
} from "../api/demoData.js";
import type {
  WorkflowBoard,
  WorkflowEvent,
  WorkflowInstanceSummary,
  WorkflowPatchDiff,
  WorkflowPatchProposal,
  WorkflowStatus,
  WorkflowSummary,
  WorkflowVersionSummary,
} from "../api/types.js";

export interface WorkflowConsoleDemoState {
  workflows: WorkflowSummary[];
  versions: WorkflowVersionSummary[];
  instances: WorkflowInstanceSummary[];
  selectedWorkflowId: string;
  selectedVersionId: string;
  selectedInstanceId: string;
  board: WorkflowBoard;
  status: WorkflowStatus;
  events: WorkflowEvent[];
  patchProposal: WorkflowPatchProposal;
  patchDiff: WorkflowPatchDiff;
  highRiskPatchDiff: WorkflowPatchDiff;
  agentTalkFixture: AgentTalkFixture;
  setSelectedWorkflowId: (value: string) => void;
  setSelectedVersionId: (value: string) => void;
  setSelectedInstanceId: (value: string) => void;
}

export function useWorkflowConsoleDemo(): WorkflowConsoleDemoState {
  const [selectedWorkflowId, setSelectedWorkflowId] = useState(demoWorkflows[0]?.workflow_template_id || "");
  const [selectedVersionId, setSelectedVersionId] = useState(demoVersions[0]?.workflow_version_id || "");
  const [selectedInstanceId, setSelectedInstanceId] = useState(demoInstances[0]?.workflow_instance_id || "");

  return useMemo(
    () => ({
      workflows: demoWorkflows,
      versions: demoVersions,
      instances: demoInstances,
      selectedWorkflowId,
      selectedVersionId,
      selectedInstanceId,
      board: demoBoard,
      status: demoStatus,
      events: demoEvents,
      patchProposal: demoPatchProposal,
      patchDiff: demoPatchDiff,
      highRiskPatchDiff: demoHighRiskPatchDiff,
      agentTalkFixture: demoAgentTalkFixture,
      setSelectedWorkflowId,
      setSelectedVersionId,
      setSelectedInstanceId,
    }),
    [selectedWorkflowId, selectedVersionId, selectedInstanceId],
  );
}
