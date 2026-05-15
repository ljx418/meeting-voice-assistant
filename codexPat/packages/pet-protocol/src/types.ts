export type PetEventLevel =
  | "idle"
  | "thinking"
  | "running"
  | "success"
  | "warning"
  | "error"
  | "need_input"
  | "sleeping";

export type PetSourceKind = "codex" | "claude_code" | "custom" | "system";
export type PetEventVia = "http" | "cli" | "mcp" | "skill" | "internal";
export type PetAction = PetEventLevel;
export type PetSound = "none" | "success_chime" | "warning_chime" | "error_chime" | "need_input_chime";

export type LightEffect =
  | "none"
  | "thinking_blue"
  | "running_cyan"
  | "success_green"
  | "warning_amber"
  | "error_red"
  | "need_input_purple"
  | "sleeping_warm_dim";

export type PetEvent = {
  source: {
    id: string;
    kind: PetSourceKind;
    name?: string;
  };
  level: PetEventLevel;
  title?: string;
  message?: string;
  action?: PetAction;
  sound?: PetSound;
  durationMs?: number;
  hardware?: {
    light?: {
      effect?: LightEffect;
      color?: string;
      brightness?: number;
    };
  };
  metadata?: Record<string, string | number | boolean | null | Record<string, string | number | boolean | null>>;
};

export type AcceptedPetEvent = PetEvent & {
  via: "http";
  receivedAt: string;
};
