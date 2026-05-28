import type { AssetManifest } from "../asset-manifest";

export const GLTF_PROTOTYPE_ASSET_MANIFEST: AssetManifest = {
  schemaVersion: "5.0",
  packId: "gltf-prototype-cat",
  version: "1.0.0",
  rendererKind: "gltf",
  license: {
    type: "generated",
    attribution: "Agent Desktop Pet generated prototype cat model"
  },
  assets: {
    idle: { assetId: "idle", kind: "gltf" },
    thinking: { assetId: "thinking", kind: "gltf" },
    running: { assetId: "running", kind: "gltf" },
    success: { assetId: "success", kind: "gltf" },
    warning: { assetId: "warning", kind: "gltf" },
    error: { assetId: "error", kind: "gltf" },
    need_input: { assetId: "need_input", kind: "gltf" },
    sleeping: { assetId: "sleeping", kind: "gltf" }
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

