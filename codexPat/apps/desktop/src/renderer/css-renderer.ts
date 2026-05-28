import type { RendererKind, SafeActionId, PlaybackIntent } from "../assets/asset-manifest";
import type { PetRenderer, SafeRendererProfile } from "./renderer-contract";

export class CssRenderer implements PetRenderer {
  readonly kind: RendererKind = "css";
  private container: HTMLElement | undefined;

  mount(container: HTMLElement, profile: SafeRendererProfile) {
    this.container = container;
    container.dataset.rendererKind = profile.rendererKind;
    container.dataset.assetPackId = profile.packId;
    this.setScale(profile.scale);
  }

  setAction(actionId: SafeActionId, playback: PlaybackIntent) {
    if (!this.container) {
      return;
    }
    this.container.dataset.safeActionId = actionId;
    this.container.dataset.playbackPriority = playback.priority;
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

