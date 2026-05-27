import type { Meta, StoryObj } from "@storybook/react";
import "@xyflow/react/dist/style.css";
import "../../design-system/tokens.css";
import "../../design-system/components.css";
import "./workflow-components.css";
import "./workflow-canvas.css";
import { WorkflowCanvas } from "./WorkflowCanvas.js";

const meta = {
  title: "Workflow/React Flow Canvas",
  component: WorkflowCanvas,
  args: {
    mode: "overview",
  },
} satisfies Meta<typeof WorkflowCanvas>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Overview: Story = {};

export const Proposal: Story = {
  args: { mode: "proposal" },
};

export const Running: Story = {
  args: { mode: "running" },
};
