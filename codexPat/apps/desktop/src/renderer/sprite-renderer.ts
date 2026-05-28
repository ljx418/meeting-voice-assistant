import { SPRITE_V2_FRAMES, renderSpriteFrame } from "../assets/bundled-packs/sprite-v2";
import type { RendererKind, SafeActionId, PlaybackIntent } from "../assets/asset-manifest";
import type { PetRenderer, SafeRendererProfile } from "./renderer-contract";

export class SpriteRenderer implements PetRenderer {
  readonly kind: RendererKind = "sprite";
  private container: HTMLElement | undefined;

  mount(container: HTMLElement, profile: SafeRendererProfile) {
    this.container = container;
    container.dataset.rendererKind = "sprite";
    container.dataset.assetPackId = profile.packId;
    this.setScale(profile.scale);
  }

  setAction(actionId: SafeActionId, playback: PlaybackIntent) {
    if (!this.container) {
      return;
    }
    const coreActionId = actionId in SPRITE_V2_FRAMES ? actionId as keyof typeof SPRITE_V2_FRAMES : "idle";
    this.container.dataset.safeActionId = coreActionId;
    this.container.dataset.playbackPriority = playback.priority;
    this.container.innerHTML = renderSpriteFrame(SPRITE_V2_FRAMES[coreActionId]);
  }

  setScale(scale: number) {
    if (!this.container) {
      return;
    }
    this.container.style.setProperty("--pet-renderer-scale", String(clampScale(scale)));
  }

  setVisible(visible: boolean) {
    if (!this.container) {
      return;
    }
    this.container.hidden = !visible;
  }

  dispose() {
    if (this.container) {
      delete this.container.dataset.rendererKind;
      delete this.container.dataset.assetPackId;
      delete this.container.dataset.safeActionId;
      delete this.container.dataset.playbackPriority;
      this.container.innerHTML = "";
      this.container.style.removeProperty("--pet-renderer-scale");
    }
    this.container = undefined;
  }
}

function clampScale(value: number) {
  if (!Number.isFinite(value)) {
    return 1;
  }
  return Math.min(2, Math.max(0.5, value));
}

