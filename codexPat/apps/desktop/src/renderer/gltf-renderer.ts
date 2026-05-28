import * as THREE from "three";
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader.js";
import type { GLTF } from "three/examples/jsm/loaders/GLTFLoader.js";
import type { RendererKind, SafeActionId, PlaybackIntent } from "../assets/asset-manifest";
import type { PetRenderer, SafeRendererProfile } from "./renderer-contract";

const PROTOTYPE_GLB_URL = "/assets/3d/agent-desktop-pet-cat-prototype.glb";

export class GltfRenderer implements PetRenderer {
  readonly kind: RendererKind = "gltf";
  private container: HTMLElement | undefined;
  private renderer: THREE.WebGLRenderer | undefined;
  private scene: THREE.Scene | undefined;
  private camera: THREE.PerspectiveCamera | undefined;
  private mixer: THREE.AnimationMixer | undefined;
  private clips = new Map<string, THREE.AnimationClip>();
  private activeActionId: SafeActionId = "idle";
  private activePlayback: PlaybackIntent = { loop: true, priority: "base" };
  private frameId: number | undefined;
  private clock = new THREE.Clock();

  mount(container: HTMLElement, profile: SafeRendererProfile) {
    this.container = container;
    container.dataset.rendererKind = "gltf";
    container.dataset.assetPackId = profile.packId;

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(35, 1, 0.1, 20);
    camera.position.set(0, -5, 2.2);
    camera.lookAt(0, 0, 1);

    const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
    renderer.setSize(184, 184);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
    container.appendChild(renderer.domElement);

    scene.add(new THREE.HemisphereLight(0xffffff, 0x99aabb, 2.2));
    this.scene = scene;
    this.camera = camera;
    this.renderer = renderer;
    this.setScale(profile.scale);

    new GLTFLoader().load(PROTOTYPE_GLB_URL, (gltf: GLTF) => {
      const model = gltf.scene;
      model.rotation.x = Math.PI / 2;
      scene.add(model);
      this.mixer = gltf.animations.length ? new THREE.AnimationMixer(model) : undefined;
      this.clips = new Map(gltf.animations.map((clip: THREE.AnimationClip) => [clip.name, clip]));
      if (this.mixer) {
        this.playClip(this.activeActionId, this.activePlayback);
      }
    });

    this.animate();
  }

  setAction(actionId: SafeActionId, playback: PlaybackIntent) {
    if (!this.container) {
      return;
    }
    this.container.dataset.safeActionId = actionId;
    this.container.dataset.playbackPriority = playback.priority;
    this.activeActionId = actionId;
    this.activePlayback = playback;
    this.playClip(actionId, playback);
  }

  setScale(scale: number) {
    this.container?.style.setProperty("--pet-renderer-scale", String(clampScale(scale)));
  }

  setVisible(visible: boolean) {
    if (!this.container) {
      return;
    }
    this.container.hidden = !visible;
  }

  dispose() {
    if (this.frameId !== undefined) {
      window.cancelAnimationFrame(this.frameId);
    }
    this.renderer?.dispose();
    if (this.container) {
      this.container.innerHTML = "";
      delete this.container.dataset.rendererKind;
      delete this.container.dataset.assetPackId;
      delete this.container.dataset.safeActionId;
      delete this.container.dataset.playbackPriority;
    }
    this.container = undefined;
    this.renderer = undefined;
    this.scene = undefined;
    this.camera = undefined;
    this.mixer = undefined;
    this.clips.clear();
    this.frameId = undefined;
  }

  private playClip(actionId: SafeActionId, playback: PlaybackIntent) {
    if (!this.mixer) {
      return;
    }
    const clip = this.clips.get(actionId) ?? this.clips.get("idle");
    if (!clip) {
      return;
    }
    this.mixer.stopAllAction();
    const action = this.mixer.clipAction(clip);
    action.reset();
    action.setLoop(playback.loop ? THREE.LoopRepeat : THREE.LoopOnce, playback.loop ? Infinity : 1);
    action.clampWhenFinished = !playback.loop;
    action.play();
  }

  private animate = () => {
    if (!this.renderer || !this.scene || !this.camera) {
      return;
    }
    this.frameId = window.requestAnimationFrame(this.animate);
    this.mixer?.update(this.clock.getDelta());
    this.renderer.render(this.scene, this.camera);
  };
}

function clampScale(value: number) {
  if (!Number.isFinite(value)) return 1;
  return Math.min(2, Math.max(0.5, value));
}
