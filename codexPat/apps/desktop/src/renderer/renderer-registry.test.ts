import assert from "node:assert/strict";
import { describe, test } from "node:test";
import { RendererRegistry } from "./renderer-registry";

describe("V5.0 renderer registry", () => {
  test("selects css renderer as the default fallback", () => {
    const registry = new RendererRegistry();
    const result = registry.create("css");
    assert.equal(result.selectedKind, "css");
    assert.equal(result.fallbackUsed, false);
    assert.equal(result.renderer.kind, "css");
  });

  test("falls unavailable renderer kind back to css", () => {
    const registry = new RendererRegistry();
    const result = registry.create("rive");
    assert.equal(result.requestedKind, "rive");
    assert.equal(result.selectedKind, "css");
    assert.equal(result.fallbackUsed, true);
    assert.equal(result.renderer.kind, "css");
  });

  test("css renderer accepts safe boundary inputs only", () => {
    const registry = new RendererRegistry();
    const result = registry.create("css");
    const container = {
      dataset: {} as Record<string, string>,
      style: {
        values: new Map<string, string>(),
        setProperty(name: string, value: string) {
          this.values.set(name, value);
        },
        removeProperty(name: string) {
          this.values.delete(name);
        }
      },
      hidden: false
    } as unknown as HTMLElement;

    result.renderer.mount(container, {
      profileId: "default-cat",
      rendererKind: "css",
      packId: "css-default",
      scale: 1
    });
    result.renderer.setAction("running", { loop: true, priority: "base" });
    result.renderer.setVisible(true);

    assert.equal(container.dataset.rendererKind, "css");
    assert.equal(container.dataset.assetPackId, "css-default");
    assert.equal(container.dataset.safeActionId, "running");
    assert.equal(JSON.stringify(container.dataset).includes("Authorization"), false);
    assert.equal(JSON.stringify(container.dataset).includes("/Users/"), false);
  });
});
