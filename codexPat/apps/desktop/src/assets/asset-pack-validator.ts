import {
  CORE_ACTION_IDS,
  OPTIONAL_ACTION_IDS,
  type AssetManifest,
  type ManifestValidationIssue,
  type ManifestValidationResult,
  isRendererKind,
  isSafeActionId
} from "./asset-manifest";

const SAFE_ID_PATTERN = /^[A-Za-z0-9._-]{1,64}$/;
const SAFE_VERSION_PATTERN = /^[A-Za-z0-9._+-]{1,32}$/;
const REMOTE_URL_PATTERN = /\b(?:https?|wss?):\/\/|file:\/\//i;
const ABSOLUTE_PATH_PATTERN = /(?:^|[\s"'=])(?:\/Users\/|\/var\/|\/tmp\/|\/private\/|\/Volumes\/|[A-Za-z]:[\\/])/;
const PATH_ESCAPE_PATTERN = /(?:^|[\\/])\.\.(?:[\\/]|$)/;
const SCRIPT_LIKE_PATTERN = /\b(?:eval|Function|script|javascript:|shell|exec|spawn|chmod|curl|bash|zsh|powershell)\b/i;
const EXECUTABLE_EXT_PATTERN = /\.(?:sh|bash|zsh|command|app|exe|dll|dylib|so|js|mjs|cjs)$/i;
const RAW_PAYLOAD_KEY_PATTERN = /(?:raw|payload|petevent|agent|codex|hook|terminal|mcp|http|prompt|tool.*command|authorization|token|workspace|config|transcript_path)/i;

export function validateAssetManifest(input: unknown): ManifestValidationResult {
  const errors: ManifestValidationIssue[] = [];
  const warnings: ManifestValidationIssue[] = [];

  if (!isRecord(input)) {
    return {
      ok: false,
      errors: [issue("error", "manifest_not_object", "$", "manifest must be an object")],
      warnings,
      optionalFallbacks: {}
    };
  }

  const manifest = input as Partial<AssetManifest>;
  validateSafeString(manifest.schemaVersion, "schemaVersion", /^5\.0$/, errors);
  validateSafeString(manifest.packId, "packId", SAFE_ID_PATTERN, errors);
  validateSafeString(manifest.version, "version", SAFE_VERSION_PATTERN, errors);

  if (typeof manifest.rendererKind !== "string" || !isRendererKind(manifest.rendererKind)) {
    errors.push(issue("error", "renderer_kind_unknown", "rendererKind", "renderer kind is not supported"));
  }

  if (!isRecord(manifest.license)) {
    errors.push(issue("error", "field_invalid", "license", "license is required"));
  } else {
    validateSafeString(manifest.license.type, "license.type", SAFE_ID_PATTERN, errors);
    validateSafeText(manifest.license.attribution, "license.attribution", errors);
  }

  if (!isRecord(manifest.assets)) {
    errors.push(issue("error", "field_invalid", "assets", "assets must be an object"));
  }

  if (!isRecord(manifest.actions)) {
    errors.push(issue("error", "field_invalid", "actions", "actions must be an object"));
  }

  scanForbidden(input, "$", errors);

  const assets = isRecord(manifest.assets) ? manifest.assets : {};
  const actions = isRecord(manifest.actions) ? manifest.actions : {};
  validateAssets(assets, errors);
  validateActions(actions, assets, errors);

  for (const actionId of CORE_ACTION_IDS) {
    if (!isRecord(actions[actionId])) {
      errors.push(issue("error", "core_action_missing", `actions.${actionId}`, "required core action is missing"));
    }
  }

  const optionalFallbacks: ManifestValidationResult["optionalFallbacks"] = {};
  for (const actionId of OPTIONAL_ACTION_IDS) {
    if (!isRecord(actions[actionId])) {
      optionalFallbacks[actionId] = "idle";
      warnings.push(issue("warning", "optional_action_missing", `actions.${actionId}`, "optional action falls back to idle"));
    }
  }

  return {
    ok: errors.length === 0,
    manifest: errors.length === 0 ? input as AssetManifest : undefined,
    errors,
    warnings,
    optionalFallbacks
  };
}

function validateAssets(assets: Record<string, unknown>, errors: ManifestValidationIssue[]) {
  for (const [assetKey, asset] of Object.entries(assets)) {
    if (!SAFE_ID_PATTERN.test(assetKey)) {
      errors.push(issue("error", "field_invalid", `assets.${assetKey}`, "asset key is not a safe identifier"));
    }
    if (!isRecord(asset)) {
      errors.push(issue("error", "field_invalid", `assets.${assetKey}`, "asset entry must be an object"));
      continue;
    }
    validateSafeString(asset.assetId, `assets.${assetKey}.assetId`, SAFE_ID_PATTERN, errors);
    validateSafeString(asset.kind, `assets.${assetKey}.kind`, /^(css|clip|sprite|gltf)$/, errors);
  }
}

function validateActions(actions: Record<string, unknown>, assets: Record<string, unknown>, errors: ManifestValidationIssue[]) {
  for (const [actionId, action] of Object.entries(actions)) {
    if (!isSafeActionId(actionId)) {
      errors.push(issue("error", "field_invalid", `actions.${actionId}`, "action is not a safe action id"));
    }
    if (!isRecord(action)) {
      errors.push(issue("error", "field_invalid", `actions.${actionId}`, "action entry must be an object"));
      continue;
    }
    validateSafeString(action.assetId, `actions.${actionId}.assetId`, SAFE_ID_PATTERN, errors);
    if (typeof action.assetId === "string" && !isRecord(assets[action.assetId])) {
      errors.push(issue("error", "asset_missing", `actions.${actionId}.assetId`, "action asset does not exist"));
    }
    if (typeof action.loop !== "boolean") {
      errors.push(issue("error", "field_invalid", `actions.${actionId}.loop`, "loop must be boolean"));
    }
    validateSafeString(action.priority, `actions.${actionId}.priority`, /^(base|transient|urgent)$/, errors);
    if ("durationMs" in action && (!Number.isInteger(action.durationMs) || Number(action.durationMs) < 0 || Number(action.durationMs) > 60000)) {
      errors.push(issue("error", "field_invalid", `actions.${actionId}.durationMs`, "durationMs must be an integer between 0 and 60000"));
    }
  }
}

function validateSafeString(value: unknown, field: string, pattern: RegExp, errors: ManifestValidationIssue[]) {
  if (typeof value !== "string" || !pattern.test(value)) {
    errors.push(issue("error", "field_invalid", field, "field is not a safe string"));
  }
}

function validateSafeText(value: unknown, field: string, errors: ManifestValidationIssue[]) {
  if (typeof value !== "string" || value.length < 1 || value.length > 160 || /[\u0000-\u001F\u007F]/.test(value)) {
    errors.push(issue("error", "field_invalid", field, "field is not safe text"));
  }
}

function scanForbidden(value: unknown, field: string, errors: ManifestValidationIssue[]) {
  if (typeof value === "string") {
    if (
      REMOTE_URL_PATTERN.test(value) ||
      ABSOLUTE_PATH_PATTERN.test(value) ||
      PATH_ESCAPE_PATTERN.test(value) ||
      SCRIPT_LIKE_PATTERN.test(value) ||
      EXECUTABLE_EXT_PATTERN.test(value)
    ) {
      errors.push(issue("error", "forbidden_content", field, "forbidden content rejected"));
    }
    return;
  }

  if (Array.isArray(value)) {
    value.forEach((item, index) => scanForbidden(item, `${field}[${index}]`, errors));
    return;
  }

  if (!isRecord(value)) {
    return;
  }

  for (const [key, nested] of Object.entries(value)) {
    const nestedField = `${field}.${sanitizeFieldName(key)}`;
    if (RAW_PAYLOAD_KEY_PATTERN.test(key)) {
      errors.push(issue("error", "forbidden_content", nestedField, "forbidden payload-like field rejected"));
    }
    scanForbidden(nested, nestedField, errors);
  }
}

function issue(
  severity: ManifestValidationIssue["severity"],
  code: ManifestValidationIssue["code"],
  field: string,
  reason: string
): ManifestValidationIssue {
  return { severity, code, field, reason };
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function sanitizeFieldName(value: string) {
  return /^[A-Za-z0-9._-]{1,80}$/.test(value) ? value : "field";
}

