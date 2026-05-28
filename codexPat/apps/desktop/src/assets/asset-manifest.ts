export const CORE_ACTION_IDS = [
  "idle",
  "thinking",
  "running",
  "success",
  "warning",
  "error",
  "need_input",
  "sleeping"
] as const;

export const OPTIONAL_ACTION_IDS = ["blink", "walk", "stretch", "tease"] as const;

export const SAFE_ACTION_IDS = [...CORE_ACTION_IDS, ...OPTIONAL_ACTION_IDS] as const;

export const RENDERER_KINDS = ["css", "sprite", "gltf", "rive", "live2d"] as const;

export type CoreActionId = (typeof CORE_ACTION_IDS)[number];
export type OptionalActionId = (typeof OPTIONAL_ACTION_IDS)[number];
export type SafeActionId = (typeof SAFE_ACTION_IDS)[number];
export type RendererKind = (typeof RENDERER_KINDS)[number];

export type PlaybackPriority = "base" | "transient" | "urgent";

export type PlaybackIntent = {
  loop: boolean;
  priority: PlaybackPriority;
  durationMs?: number;
};

export type AssetManifestLicense = {
  type: string;
  attribution: string;
};

export type AssetManifestAsset = {
  assetId: string;
  kind: "css" | "clip" | "sprite" | "gltf";
};

export type AssetManifestAction = PlaybackIntent & {
  assetId: string;
};

export type AssetManifest = {
  schemaVersion: "5.0";
  packId: string;
  version: string;
  rendererKind: RendererKind;
  license: AssetManifestLicense;
  assets: Record<string, AssetManifestAsset>;
  actions: Partial<Record<SafeActionId, AssetManifestAction>>;
};

export type ManifestValidationIssueCode =
  | "manifest_not_object"
  | "field_invalid"
  | "renderer_kind_unknown"
  | "core_action_missing"
  | "optional_action_missing"
  | "asset_missing"
  | "forbidden_content";

export type ManifestValidationIssueSeverity = "error" | "warning";

export type ManifestValidationIssue = {
  severity: ManifestValidationIssueSeverity;
  code: ManifestValidationIssueCode;
  field: string;
  reason: string;
};

export type ManifestValidationResult = {
  ok: boolean;
  manifest?: AssetManifest;
  errors: ManifestValidationIssue[];
  warnings: ManifestValidationIssue[];
  optionalFallbacks: Partial<Record<OptionalActionId, CoreActionId>>;
};

export function isSafeActionId(value: string): value is SafeActionId {
  return (SAFE_ACTION_IDS as readonly string[]).includes(value);
}

export function isRendererKind(value: string): value is RendererKind {
  return (RENDERER_KINDS as readonly string[]).includes(value);
}

export function isCoreActionId(value: string): value is CoreActionId {
  return (CORE_ACTION_IDS as readonly string[]).includes(value);
}

export function isOptionalActionId(value: string): value is OptionalActionId {
  return (OPTIONAL_ACTION_IDS as readonly string[]).includes(value);
}

