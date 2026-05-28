import type { AssetManifest } from "../asset-manifest";

export const SPRITE_V2_ASSET_MANIFEST: AssetManifest = {
  schemaVersion: "5.0",
  packId: "sprite-v2",
  version: "1.0.0",
  rendererKind: "sprite",
  license: {
    type: "bundled",
    attribution: "Agent Desktop Pet bundled sprite v2"
  },
  assets: {
    idle: { assetId: "idle", kind: "sprite" },
    thinking: { assetId: "thinking", kind: "sprite" },
    running: { assetId: "running", kind: "sprite" },
    success: { assetId: "success", kind: "sprite" },
    warning: { assetId: "warning", kind: "sprite" },
    error: { assetId: "error", kind: "sprite" },
    need_input: { assetId: "need_input", kind: "sprite" },
    sleeping: { assetId: "sleeping", kind: "sprite" }
  },
  actions: {
    idle: { assetId: "idle", loop: true, priority: "base" },
    thinking: { assetId: "thinking", loop: true, priority: "base" },
    running: { assetId: "running", loop: true, priority: "base" },
    success: { assetId: "success", loop: false, priority: "transient", durationMs: 3000 },
    warning: { assetId: "warning", loop: false, priority: "transient", durationMs: 4000 },
    error: { assetId: "error", loop: false, priority: "urgent", durationMs: 6000 },
    need_input: { assetId: "need_input", loop: false, priority: "urgent", durationMs: 8000 },
    sleeping: { assetId: "sleeping", loop: true, priority: "base" }
  }
};

