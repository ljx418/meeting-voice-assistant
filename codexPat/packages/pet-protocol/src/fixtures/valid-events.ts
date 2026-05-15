import type { PetEvent } from "../types.js";

export const VALID_PET_EVENTS: PetEvent[] = [
  {
    source: {
      id: "custom.local",
      kind: "custom",
      name: "Custom Agent"
    },
    level: "success",
    title: "测试通过",
    message: "可选说明",
    action: "success",
    sound: "success_chime",
    durationMs: 3000,
    hardware: {
      light: {
        effect: "success_green",
        color: "#00FF88",
        brightness: 80
      }
    },
    metadata: {
      taskId: "local-test"
    }
  },
  {
    source: {
      id: "codex.local",
      kind: "codex"
    },
    level: "running",
    durationMs: 8000,
    sound: "none"
  }
];
