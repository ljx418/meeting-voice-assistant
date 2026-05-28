import type { RendererKind, SafeActionId, PlaybackIntent } from "../assets/asset-manifest";

export type SafeRendererProfile = {
  profileId: string;
  rendererKind: RendererKind;
  packId: string;
  scale: number;
};

export type PetRenderer = {
  readonly kind: RendererKind;
  mount(container: HTMLElement, profile: SafeRendererProfile): void;
  setAction(actionId: SafeActionId, playback: PlaybackIntent): void;
  setScale(scale: number): void;
  setVisible(visible: boolean): void;
  dispose(): void;
};

export type PetRendererFactory = () => PetRenderer;

