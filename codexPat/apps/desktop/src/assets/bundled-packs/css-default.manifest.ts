import type { AssetManifest } from "../asset-manifest";

export const CSS_DEFAULT_ASSET_MANIFEST: AssetManifest = {
  schemaVersion: "5.0",
  packId: "css-default",
  version: "1.0.0",
  rendererKind: "css",
  license: {
    type: "bundled",
    attribution: "Agent Desktop Pet"
  },
  assets: {
    idle: { assetId: "idle", kind: "css" },
    thinking: { assetId: "thinking", kind: "css" },
    running: { assetId: "running", kind: "css" },
    success: { assetId: "success", kind: "css" },
    warning: { assetId: "warning", kind: "css" },
    error: { assetId: "error", kind: "css" },
    need_input: { assetId: "need_input", kind: "css" },
    sleeping: { assetId: "sleeping", kind: "css" }
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

