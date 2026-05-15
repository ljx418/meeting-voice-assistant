export const INVALID_PET_EVENTS: unknown[] = [
  {
    source: {
      id: "bad/source",
      kind: "custom"
    },
    level: "success"
  },
  {
    source: {
      id: "custom.local",
      kind: "custom"
    },
    level: "success",
    sound: "../../local.wav"
  },
  {
    source: {
      id: "custom.local",
      kind: "custom"
    },
    level: "running",
    durationMs: 100
  },
  {
    source: {
      id: "custom.local",
      kind: "custom"
    },
    level: "warning",
    via: "http"
  }
];
