import type { Meta, StoryObj } from "@storybook/react";
import "../../design-system/tokens.css";
import "../../design-system/components.css";
import "./panels.css";
import { BottomRunPanel } from "./RightPanels.js";

const meta = {
  title: "Panels/Bottom Run Panel",
  component: BottomRunPanel,
  args: {
    activeTab: "artifacts",
  },
} satisfies Meta<typeof BottomRunPanel>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Artifacts: Story = {};
export const Quality: Story = { args: { activeTab: "quality" } };
export const Evidence: Story = { args: { activeTab: "evidence" } };
