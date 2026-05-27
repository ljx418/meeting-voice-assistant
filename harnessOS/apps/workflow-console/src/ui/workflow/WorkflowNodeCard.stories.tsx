import type { Meta, StoryObj } from "@storybook/react";
import { CompletedNodeCard, FailedNodeCard, GhostNodeCard, PendingNodeCard, RunningNodeCard, WaitingApprovalNodeCard, WorkflowNodeCard } from "./WorkflowNodeCard.js";
import "../../design-system/tokens.css";
import "../../design-system/components.css";
import "./workflow-components.css";

function NodeStatesGallery() {
  return (
    <main style={{ background: "var(--hos-bg-canvas)", minHeight: "100vh", padding: "var(--hos-space-6)" }}>
      <div style={{ display: "flex", flexWrap: "wrap", gap: "var(--hos-space-6)" }}>
        <GhostNodeCard />
        <PendingNodeCard />
        <RunningNodeCard />
        <CompletedNodeCard />
        <FailedNodeCard />
        <WaitingApprovalNodeCard />
        <WorkflowNodeCard
          attemptCount={1}
          icon="入"
          inputArtifact="folder_ref"
          name="文件夹输入"
          outputArtifact="folder_ref"
          qualityStatus="passed"
          selected
          status="completed"
          type="Input"
        />
      </div>
    </main>
  );
}

const meta = {
  title: "Workflow/Node Cards",
  component: NodeStatesGallery,
} satisfies Meta<typeof NodeStatesGallery>;

export default meta;
type Story = StoryObj<typeof meta>;

export const States: Story = {};
