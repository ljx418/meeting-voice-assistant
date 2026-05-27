import type { Meta, StoryObj } from "@storybook/react";
import "../../design-system/tokens.css";
import "../../design-system/components.css";
import "./panels.css";
import { RightPanelsGallery } from "./RightPanels.js";

const meta = {
  title: "Panels/Right Panels",
  component: RightPanelsGallery,
} satisfies Meta<typeof RightPanelsGallery>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Gallery: Story = {};
