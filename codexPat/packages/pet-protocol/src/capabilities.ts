import type { LightEffect, PetAction, PetEventLevel, PetSourceKind, PetSound } from "./types.js";

export const PET_SOURCE_KINDS = ["codex", "claude_code", "custom", "system"] as const satisfies readonly PetSourceKind[];

export const PET_EVENT_LEVELS = [
  "idle",
  "thinking",
  "running",
  "success",
  "warning",
  "error",
  "need_input",
  "sleeping"
] as const satisfies readonly PetEventLevel[];

export const PET_ACTIONS = [...PET_EVENT_LEVELS] as const satisfies readonly PetAction[];

export const PET_SOUNDS = [
  "none",
  "success_chime",
  "warning_chime",
  "error_chime",
  "need_input_chime"
] as const satisfies readonly PetSound[];

export const LIGHT_EFFECTS = [
  "none",
  "thinking_blue",
  "running_cyan",
  "success_green",
  "warning_amber",
  "error_red",
  "need_input_purple",
  "sleeping_warm_dim"
] as const satisfies readonly LightEffect[];

export const PET_CAPABILITIES = {
  levels: PET_EVENT_LEVELS,
  actions: PET_ACTIONS,
  sounds: {
    playback: true,
    acceptedIds: PET_SOUNDS
  },
  hardware: {
    light: false,
    acceptedEffects: LIGHT_EFFECTS
  }
} as const;
