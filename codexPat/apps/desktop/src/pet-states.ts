export type CatState =
  | "idle"
  | "thinking"
  | "running"
  | "success"
  | "warning"
  | "error"
  | "need_input"
  | "sleeping";

export type CatStateConfig = {
  id: CatState;
  label: string;
  cssClass: string;
  priority: number;
  durationMs: number | "indefinite";
  interruptible: boolean;
  lockMs: number;
  cooldownMs: number;
  next: CatState;
};

export const CAT_STATE_ORDER: CatState[] = [
  "idle",
  "thinking",
  "running",
  "success",
  "warning",
  "error",
  "need_input",
  "sleeping"
];

export const CAT_STATE_CONFIG: Record<CatState, CatStateConfig> = {
  need_input: {
    id: "need_input",
    label: "Need Input",
    cssClass: "cat-state-need-input",
    priority: 100,
    durationMs: 8000,
    interruptible: false,
    lockMs: 3000,
    cooldownMs: 3000,
    next: "idle"
  },
  error: {
    id: "error",
    label: "Error",
    cssClass: "cat-state-error",
    priority: 90,
    durationMs: 6000,
    interruptible: false,
    lockMs: 2500,
    cooldownMs: 3000,
    next: "idle"
  },
  warning: {
    id: "warning",
    label: "Warning",
    cssClass: "cat-state-warning",
    priority: 70,
    durationMs: 4000,
    interruptible: true,
    lockMs: 0,
    cooldownMs: 2000,
    next: "idle"
  },
  success: {
    id: "success",
    label: "Success",
    cssClass: "cat-state-success",
    priority: 60,
    durationMs: 3000,
    interruptible: true,
    lockMs: 0,
    cooldownMs: 2000,
    next: "idle"
  },
  running: {
    id: "running",
    label: "Running",
    cssClass: "cat-state-running",
    priority: 40,
    durationMs: 8000,
    interruptible: true,
    lockMs: 0,
    cooldownMs: 2000,
    next: "idle"
  },
  thinking: {
    id: "thinking",
    label: "Thinking",
    cssClass: "cat-state-thinking",
    priority: 35,
    durationMs: 7000,
    interruptible: true,
    lockMs: 0,
    cooldownMs: 2000,
    next: "idle"
  },
  idle: {
    id: "idle",
    label: "Idle",
    cssClass: "cat-state-idle",
    priority: 10,
    durationMs: "indefinite",
    interruptible: true,
    lockMs: 0,
    cooldownMs: 0,
    next: "idle"
  },
  sleeping: {
    id: "sleeping",
    label: "Sleeping",
    cssClass: "cat-state-sleeping",
    priority: 5,
    durationMs: "indefinite",
    interruptible: true,
    lockMs: 0,
    cooldownMs: 5000,
    next: "idle"
  }
};

export function labelForState(state: CatState) {
  return CAT_STATE_CONFIG[state].label;
}
