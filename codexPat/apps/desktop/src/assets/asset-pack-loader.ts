import type { AssetManifest, ManifestValidationResult } from "./asset-manifest";
import { validateAssetManifest } from "./asset-pack-validator";

export type AssetPackActivationResult = {
  activeManifest: AssetManifest;
  validation: ManifestValidationResult;
  preservedPrevious: boolean;
};

export function activateAssetManifest(
  currentManifest: AssetManifest,
  candidate: unknown
): AssetPackActivationResult {
  const validation = validateAssetManifest(candidate);
  if (!validation.ok || !validation.manifest) {
    return {
      activeManifest: currentManifest,
      validation,
      preservedPrevious: true
    };
  }

  return {
    activeManifest: validation.manifest,
    validation,
    preservedPrevious: false
  };
}

