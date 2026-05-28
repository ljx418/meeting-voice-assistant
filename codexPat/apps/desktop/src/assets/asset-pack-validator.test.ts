import assert from "node:assert/strict";
import { describe, test } from "node:test";
import type { AssetManifest, CoreActionId } from "./asset-manifest";
import { CORE_ACTION_IDS } from "./asset-manifest";
import { activateAssetManifest } from "./asset-pack-loader";
import { validateAssetManifest } from "./asset-pack-validator";
import { CSS_DEFAULT_ASSET_MANIFEST } from "./bundled-packs/css-default.manifest";

describe("V5.0 asset manifest validator", () => {
  test("accepts the bundled css fallback manifest with optional fallback warnings", () => {
    const result = validateAssetManifest(CSS_DEFAULT_ASSET_MANIFEST);
    assert.equal(result.ok, true);
    assert.equal(result.errors.length, 0);
    assert.equal(result.optionalFallbacks.blink, "idle");
    assert.equal(result.optionalFallbacks.walk, "idle");
    assert.equal(result.optionalFallbacks.stretch, "idle");
    assert.equal(result.optionalFallbacks.tease, "idle");
    assert.equal(result.warnings.every((item) => item.reason.includes("idle")), true);
  });

  for (const actionId of CORE_ACTION_IDS) {
    test(`rejects missing required core action ${actionId}`, () => {
      const manifest = withoutCoreAction(actionId);
      const result = validateAssetManifest(manifest);
      assert.equal(result.ok, false);
      assert.equal(result.errors.some((item) => item.code === "core_action_missing" && item.field === `actions.${actionId}`), true);
    });
  }

  test("rejects unknown renderer kind", () => {
    const result = validateAssetManifest({ ...CSS_DEFAULT_ASSET_MANIFEST, rendererKind: "canvas2d" });
    assert.equal(result.ok, false);
    assert.equal(result.errors.some((item) => item.code === "renderer_kind_unknown"), true);
  });

  test("rejects remote URLs", () => {
    const result = validateAssetManifest(withNested("preview", "https://example.invalid/cat.png"));
    assertForbidden(result);
  });

  test("rejects absolute local paths", () => {
    const result = validateAssetManifest(withNested("assetPath", "/Users/example/cat.glb"));
    assertForbidden(result);
  });

  test("rejects relative path escape", () => {
    const result = validateAssetManifest(withNested("assetPath", "../outside/cat.png"));
    assertForbidden(result);
  });

  test("rejects script or executable-like fields", () => {
    const result = validateAssetManifest(withNested("bootstrap", "eval('bad')"));
    assertForbidden(result);
  });

  test("rejects nested raw-payload-like fields", () => {
    const result = validateAssetManifest({
      ...CSS_DEFAULT_ASSET_MANIFEST,
      metadata: {
        rawPetEvent: {
          promptText: "redacted"
        }
      }
    });
    assertForbidden(result);
    assert.equal(result.errors.some((item) => item.field.includes("rawPetEvent")), true);
  });

  test("preserves previous active pack after invalid candidate", () => {
    const candidate = withoutCoreAction("idle");
    const result = activateAssetManifest(CSS_DEFAULT_ASSET_MANIFEST, candidate);
    assert.equal(result.preservedPrevious, true);
    assert.equal(result.activeManifest.packId, CSS_DEFAULT_ASSET_MANIFEST.packId);
    assert.equal(result.validation.ok, false);
  });

  test("activates valid candidate", () => {
    const candidate: AssetManifest = {
      ...CSS_DEFAULT_ASSET_MANIFEST,
      packId: "css-default-copy",
      version: "1.0.1"
    };
    const result = activateAssetManifest(CSS_DEFAULT_ASSET_MANIFEST, candidate);
    assert.equal(result.preservedPrevious, false);
    assert.equal(result.activeManifest.packId, "css-default-copy");
    assert.equal(result.validation.ok, true);
  });
});

function withoutCoreAction(actionId: CoreActionId) {
  const manifest = structuredClone(CSS_DEFAULT_ASSET_MANIFEST) as AssetManifest;
  delete manifest.actions[actionId];
  return manifest;
}

function withNested(key: string, value: unknown) {
  return {
    ...CSS_DEFAULT_ASSET_MANIFEST,
    assets: {
      ...CSS_DEFAULT_ASSET_MANIFEST.assets,
      idle: {
        ...CSS_DEFAULT_ASSET_MANIFEST.assets.idle,
        nested: {
          [key]: value
        }
      }
    }
  };
}

function assertForbidden(result: ReturnType<typeof validateAssetManifest>) {
  assert.equal(result.ok, false);
  assert.equal(result.errors.some((item) => item.code === "forbidden_content"), true);
}

