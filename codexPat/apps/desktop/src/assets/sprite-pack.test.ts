import assert from "node:assert/strict";
import { describe, test } from "node:test";
import { CORE_ACTION_IDS } from "./asset-manifest";
import { validateAssetManifest } from "./asset-pack-validator";
import { SPRITE_V2_FRAMES, renderSpriteFrame } from "./bundled-packs/sprite-v2";
import { SPRITE_V2_ASSET_MANIFEST } from "./bundled-packs/sprite-v2.manifest";
import { RendererRegistry } from "../renderer/renderer-registry";

describe("V5.1 bundled sprite asset pack", () => {
  test("validates sprite v2 manifest", () => {
    const result = validateAssetManifest(SPRITE_V2_ASSET_MANIFEST);
    assert.equal(result.ok, true);
    assert.equal(result.errors.length, 0);
  });

  test("covers every core action with a bundled sprite frame", () => {
    for (const actionId of CORE_ACTION_IDS) {
      assert.equal(SPRITE_V2_FRAMES[actionId].actionId, actionId);
      assert.equal(typeof renderSpriteFrame(SPRITE_V2_FRAMES[actionId]), "string");
    }
  });

  test("sprite frames do not contain remote paths or script-like content", () => {
    const combined = CORE_ACTION_IDS.map((actionId) => renderSpriteFrame(SPRITE_V2_FRAMES[actionId])).join("\n");
    assert.equal(/https?:\/\//i.test(combined), false);
    assert.equal(/file:\/\//i.test(combined), false);
    assert.equal(/\/Users\//.test(combined), false);
    assert.equal(/<script/i.test(combined), false);
    assert.equal(/javascript:/i.test(combined), false);
  });

  test("sprite and gltf renderers are selected without changing css fallback behavior", () => {
    const registry = new RendererRegistry();
    const sprite = registry.create("sprite");
    const gltf = registry.create("gltf");
    const rive = registry.create("rive");

    assert.equal(sprite.selectedKind, "sprite");
    assert.equal(sprite.fallbackUsed, false);
    assert.equal(gltf.selectedKind, "gltf");
    assert.equal(gltf.fallbackUsed, false);
    assert.equal(rive.selectedKind, "css");
    assert.equal(rive.fallbackUsed, true);
  });
});
