import type { RendererKind } from "../assets/asset-manifest";
import { CssRenderer } from "./css-renderer";
import { GltfRenderer } from "./gltf-renderer";
import { SpriteRenderer } from "./sprite-renderer";
import type { PetRenderer, PetRendererFactory } from "./renderer-contract";

export type RendererRegistrySelection = {
  renderer: PetRenderer;
  requestedKind: RendererKind;
  selectedKind: RendererKind;
  fallbackUsed: boolean;
};

export class RendererRegistry {
  private readonly factories = new Map<RendererKind, PetRendererFactory>();

  constructor() {
    this.register("css", () => new CssRenderer());
    this.register("sprite", () => new SpriteRenderer());
    this.register("gltf", () => new GltfRenderer());
  }

  register(kind: RendererKind, factory: PetRendererFactory) {
    this.factories.set(kind, factory);
  }

  create(kind: RendererKind): RendererRegistrySelection {
    const factory = this.factories.get(kind);
    if (factory) {
      return {
        renderer: factory(),
        requestedKind: kind,
        selectedKind: kind,
        fallbackUsed: false
      };
    }

    return {
      renderer: this.createCssFallback(),
      requestedKind: kind,
      selectedKind: "css",
      fallbackUsed: true
    };
  }

  private createCssFallback() {
    const fallbackFactory = this.factories.get("css");
    return fallbackFactory ? fallbackFactory() : new CssRenderer();
  }
}
