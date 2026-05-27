import type { Meta, StoryObj } from "@storybook/react";
import "@xyflow/react/dist/style.css";
import "../../design-system/tokens.css";
import "../../design-system/components.css";
import "../workflow/workflow-components.css";
import "../workflow/workflow-canvas.css";
import "../panels/panels.css";
import "./workflow-studio-layout.css";
import { WorkflowStudioLayout } from "./WorkflowStudioLayout.js";

const meta = {
  title: "Workflow Studio/Layout",
  component: WorkflowStudioLayout,
  args: {
    state: "overview",
  },
} satisfies Meta<typeof WorkflowStudioLayout>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Overview: Story = {};
export const AgentDraftProposal: Story = { args: { state: "agent-draft-proposal" } };
export const FolderDebugScan: Story = { args: { state: "folder-debug-scan" } };
export const RunningBoard: Story = { args: { state: "running-board" } };
export const ArtifactsQuality: Story = { args: { state: "artifacts-quality" } };
export const GovernanceEvidence: Story = { args: { state: "governance-evidence" } };
