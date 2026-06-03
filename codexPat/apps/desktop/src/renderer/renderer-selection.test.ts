import assert from "node:assert/strict";
import { describe, test } from "node:test";
import { manifestForRuntimeRenderer, resolveRuntimeRendererKind } from "./renderer-selection";

describe("V5.5 runtime renderer selection", () => {
  test("defaults to bundled gltf when no renderer is selected", () => {
    const result = resolveRuntimeRendererKind(() => null);
    assert.equal(result.selectedKind, "gltf");
    assert.equal(result.fallbackUsed, false);
    assert.equal(manifestForRuntimeRenderer(result.selectedKind).rendererKind, "gltf");
    assert.equal(manifestForRuntimeRenderer(result.selectedKind).packId, "gltf-prototype-cat");
  });

  test("selects bundled gltf when explicitly requested", () => {
    const result = resolveRuntimeRendererKind(() => "gltf");
    assert.equal(result.selectedKind, "gltf");
    assert.equal(result.fallbackUsed, false);
    assert.equal(manifestForRuntimeRenderer(result.selectedKind).packId, "gltf-prototype-cat");
  });

  test("falls unsupported or invalid renderer choices back to css", () => {
    const unavailable = resolveRuntimeRendererKind(() => "rive");
    const invalid = resolveRuntimeRendererKind(() => "https://example.invalid/renderer");

    assert.equal(unavailable.selectedKind, "css");
    assert.equal(unavailable.fallbackUsed, true);
    assert.equal(unavailable.reasonCode, "renderer_kind_unavailable");
    assert.equal(invalid.selectedKind, "css");
    assert.equal(invalid.fallbackUsed, true);
    assert.equal(invalid.reasonCode, "renderer_kind_invalid");
  });
});
