import type { Preview } from "@storybook/react";
import "@xyflow/react/dist/style.css";
import "../src/design-system/tokens.css";
import "../src/design-system/components.css";

const preview: Preview = {
  parameters: {
    controls: {
      matchers: {
        color: /(background|color)$/i,
        date: /Date$/i,
      },
    },
    layout: "fullscreen",
  },
};

export default preview;
