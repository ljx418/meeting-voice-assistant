import * as THREE from "three";
import { invoke } from "@tauri-apps/api/core";
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader.js";
import type { GLTF } from "three/examples/jsm/loaders/GLTFLoader.js";
import type { RendererKind, SafeActionId, PlaybackIntent } from "../assets/asset-manifest";
import type { PetRenderer, SafeRendererProfile } from "./renderer-contract";

const PROTOTYPE_GLB_URL = "/assets/3d/agent-desktop-pet-cat-prototype.glb";
const BUNDLED_GLTF_PACK_ID = "gltf-prototype-cat";
const PROCEDURAL_3D_PACK_IDS = new Set([BUNDLED_GLTF_PACK_ID, "v5-12-runtime-gltf"]);

type RuntimeAssetData = {
  mimeType: string;
  base64: string;
};

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
  private importedPackId: string | undefined;
  private loadedObject: THREE.Object3D | undefined;
  private objectUrl: string | undefined;
  private requestVersion = 0;
  private visible = true;
  private cssFallbackElement: HTMLElement | undefined;
  private proceduralFallbackActive = false;
  private useProceduralModel = false;

  mount(container: HTMLElement, profile: SafeRendererProfile) {
    this.container = container;
    this.useProceduralModel = PROCEDURAL_3D_PACK_IDS.has(profile.packId);
    this.importedPackId = this.useProceduralModel ? undefined : profile.packId;
    container.dataset.rendererKind = "gltf";
    container.dataset.assetPackId = profile.packId;

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(35, 1, 0.1, 20);
    setZUpPetCamera(camera);

    const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true, preserveDrawingBuffer: true });
    renderer.setSize(184, 184);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
    container.appendChild(renderer.domElement);

    // Ambient light for base illumination
    scene.add(new THREE.AmbientLight(0xffffff, 0.85));
    // Main directional light from upper-front
    const mainLight = new THREE.DirectionalLight(0xffffff, 1.35);
    mainLight.position.set(1, 2, 3);
    scene.add(mainLight);
    // Hemisphere light for natural sky/ground bounce
    scene.add(new THREE.HemisphereLight(0xffffff, 0x888888, 0.55));

    this.scene = scene;
    this.camera = camera;
    this.renderer = renderer;
    this.setScale(profile.scale);
    this.showProceduralFallback(this.useProceduralModel ? "procedural_3d_default" : "renderer_loading");

    if (this.useProceduralModel) {
      // The bundled/test GLB fixture is intentionally minimal. Keep the visible default path
      // on the higher-quality procedural model while preserving real imported GLTF rendering.
    } else if (this.importedPackId) {
      void this.loadImportedModel(this.importedPackId, this.activeActionId, ++this.requestVersion);
    } else {
      this.loadPrototypeFallback();
    }

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
    if (this.importedPackId) {
      void this.loadImportedModel(this.importedPackId, actionId, ++this.requestVersion);
      return;
    }
    this.playClip(actionId, playback);
  }

  setScale(scale: number) {
    this.container?.style.setProperty("--pet-renderer-scale", String(clampScale(scale)));
  }

  captureDataURL(): string | null {
    if (!this.renderer || !this.scene || !this.camera) {
      return null;
    }
    try {
      this.renderer.render(this.scene, this.camera);
      return this.renderer.domElement.toDataURL("image/png");
    } catch {
      return null;
    }
  }

  setVisible(visible: boolean) {
    if (!this.container) {
      return;
    }
    this.visible = visible;
    this.container.hidden = !visible;
    if (visible) {
      this.clock.getDelta();
      this.startAnimation();
    } else {
      this.stopAnimation();
    }
  }

  dispose() {
    if (this.frameId !== undefined) {
      this.stopAnimation();
    }
    this.renderer?.dispose();
    if (this.objectUrl) {
      URL.revokeObjectURL(this.objectUrl);
    }
    if (this.container) {
      this.container.innerHTML = "";
      delete this.container.dataset.rendererKind;
      delete this.container.dataset.assetPackId;
      delete this.container.dataset.safeActionId;
      delete this.container.dataset.playbackPriority;
      delete this.container.dataset.rendererReasonCode;
    }
    this.container = undefined;
    this.renderer = undefined;
    this.scene = undefined;
    this.camera = undefined;
    this.mixer = undefined;
    this.loadedObject = undefined;
    this.importedPackId = undefined;
    this.objectUrl = undefined;
    this.cssFallbackElement = undefined;
    this.proceduralFallbackActive = false;
    this.useProceduralModel = false;
    this.clips.clear();
    this.frameId = undefined;
    this.requestVersion += 1;
  }

  private async loadImportedModel(packId: string, actionId: SafeActionId, requestVersion: number) {
    try {
      const asset = await invoke<RuntimeAssetData>("runtime_personalized_asset_data", {
        packId,
        actionId
      });
      if (this.requestVersion !== requestVersion) {
        return;
      }
      const bytes = decodeBase64(asset.base64);
      const objectUrl = URL.createObjectURL(new Blob([bytes], { type: asset.mimeType }));
      new GLTFLoader().load(objectUrl, (gltf: GLTF) => {
        if (this.requestVersion !== requestVersion) {
          URL.revokeObjectURL(objectUrl);
          return;
        }
        if (this.objectUrl) {
          URL.revokeObjectURL(this.objectUrl);
        }
        this.objectUrl = objectUrl;
        this.applyLoadedGltf(gltf);
        if (this.container) {
          delete this.container.dataset.rendererReasonCode;
        }
      }, undefined, () => {
        URL.revokeObjectURL(objectUrl);
        if (this.container) {
          this.container.dataset.rendererReasonCode = "asset_runtime_read_failed";
        }
        this.showCssFallback();
        this.loadPrototypeFallback();
      });
    } catch {
      if (this.container) {
        this.container.dataset.rendererReasonCode = "asset_runtime_read_failed";
      }
      this.showCssFallback();
      this.loadPrototypeFallback();
    }
  }

  private loadPrototypeFallback() {
    this.showProceduralFallback("prototype_fallback");
    new GLTFLoader().load(PROTOTYPE_GLB_URL, (gltf: GLTF) => {
      this.applyLoadedGltf(gltf);
      if (this.container?.dataset.rendererReasonCode === "asset_runtime_fallback_failed") {
        delete this.container.dataset.rendererReasonCode;
      }
    }, undefined, () => {
      if (this.container) {
        this.container.dataset.rendererReasonCode = "asset_runtime_fallback_failed";
      }
      this.showCssFallback();
    });
  }

  private applyLoadedGltf(gltf: GLTF) {
    if (!this.scene) {
      return;
    }
    this.hideCssFallback();
    if (this.loadedObject) {
      this.scene.remove(this.loadedObject);
    }
    const model = gltf.scene;
    normalizeModelForViewport(model, this.camera);
    this.scene.add(model);
    this.loadedObject = model;
    this.proceduralFallbackActive = false;
    this.mixer = gltf.animations.length ? new THREE.AnimationMixer(model) : undefined;
    this.clips = new Map(gltf.animations.map((clip: THREE.AnimationClip) => [clip.name, clip]));
    if (this.mixer) {
      this.playClip(this.activeActionId, this.activePlayback);
    }
    this.verifyNonblankFrame();
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

  private startAnimation() {
    if (this.frameId === undefined && this.visible) {
      this.frameId = window.requestAnimationFrame(this.animate);
    }
  }

  private stopAnimation() {
    if (this.frameId !== undefined) {
      window.cancelAnimationFrame(this.frameId);
      this.frameId = undefined;
    }
  }

  private animate = () => {
    this.frameId = undefined;
    if (!this.renderer || !this.scene || !this.camera) {
      return;
    }
    if (!this.visible) {
      return;
    }
    if (this.proceduralFallbackActive && this.loadedObject) {
      animateProceduralCat(this.loadedObject, this.activeActionId, performance.now() / 1000);
    }
    this.mixer?.update(this.clock.getDelta());
    this.renderer.render(this.scene, this.camera);
    this.startAnimation();
  };

  private showProceduralFallback(reasonCode?: string) {
    if (!this.scene) {
      return;
    }
    this.hideCssFallback();
    if (this.loadedObject) {
      this.scene.remove(this.loadedObject);
    }
    const cat = createProceduralCatModel();
    this.scene.add(cat);
    this.loadedObject = cat;
    this.mixer = undefined;
    this.clips.clear();
    this.proceduralFallbackActive = true;
    if (this.container && reasonCode) {
      this.container.dataset.rendererReasonCode = reasonCode;
    }
  }

  private verifyNonblankFrame() {
    const requestVersion = this.requestVersion;
    window.requestAnimationFrame(() => {
      window.requestAnimationFrame(() => {
        if (requestVersion !== this.requestVersion || !this.renderer || !this.scene || !this.camera) {
          return;
        }
        this.renderer.render(this.scene, this.camera);
        if (canvasLooksBlank(this.renderer.domElement)) {
          this.showProceduralFallback("asset_runtime_blank_frame_fallback");
        }
      });
    });
  }

  private showCssFallback() {
    if (!this.container || this.cssFallbackElement) {
      return;
    }
    if (this.renderer?.domElement) {
      this.renderer.domElement.hidden = true;
    }
    const fallback = document.createElement("span");
    fallback.className = "gltf-css-fallback";
    fallback.setAttribute("aria-hidden", "true");
    fallback.innerHTML = `
      <span class="cat" aria-hidden="true">
        <span class="cat-shadow"></span>
        <span class="cat-tail"></span>
        <span class="cat-body"></span>
        <span class="cat-head">
          <span class="cat-ear cat-ear-left"></span>
          <span class="cat-ear cat-ear-right"></span>
          <span class="cat-eye cat-eye-left"></span>
          <span class="cat-eye cat-eye-right"></span>
          <span class="cat-muzzle"></span>
        </span>
      </span>
    `;
    this.container.appendChild(fallback);
    this.cssFallbackElement = fallback;
  }

  private hideCssFallback() {
    if (this.renderer?.domElement) {
      this.renderer.domElement.hidden = false;
    }
    this.cssFallbackElement?.remove();
    this.cssFallbackElement = undefined;
  }
}

function createProceduralCatModel() {
  const root = new THREE.Group();
  root.name = "AgentDesktopPet_Procedural3DCat";

  const bodyMaterial = new THREE.MeshStandardMaterial({ color: 0xf5a24d, roughness: 0.72, metalness: 0.02 });
  const darkerMaterial = new THREE.MeshStandardMaterial({ color: 0xc66a2c, roughness: 0.78 });
  const creamMaterial = new THREE.MeshStandardMaterial({ color: 0xffe1b8, roughness: 0.68 });
  const innerEarMaterial = new THREE.MeshStandardMaterial({ color: 0xf6a0a8, roughness: 0.7 });
  const eyeMaterial = new THREE.MeshStandardMaterial({ color: 0x17120d, roughness: 0.38 });
  const eyeHighlightMaterial = new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.18 });
  const noseMaterial = new THREE.MeshStandardMaterial({ color: 0xf05b69, roughness: 0.55 });
  const whiskerMaterial = new THREE.MeshStandardMaterial({ color: 0x3a2418, roughness: 0.5 });

  const body = makeSphere("body", [0, -0.02, -0.32], [0.56, 0.45, 0.62], bodyMaterial, 32);
  const head = makeSphere("head", [0, -0.34, 0.38], [0.47, 0.39, 0.43], bodyMaterial, 32);
  const belly = makeSphere("belly", [0, -0.45, -0.33], [0.31, 0.055, 0.37], creamMaterial, 24);
  root.add(body, head, belly);

  const leftEar = makeCone("left-ear", [-0.29, -0.24, 0.79], [0.2, 0.32, 0.2], bodyMaterial);
  leftEar.rotation.set(0.25, -0.1, 0.35);
  const rightEar = makeCone("right-ear", [0.29, -0.24, 0.79], [0.2, 0.32, 0.2], bodyMaterial);
  rightEar.rotation.set(0.25, 0.1, -0.35);
  const leftInnerEar = makeCone("left-inner-ear", [-0.29, -0.305, 0.775], [0.112, 0.12, 0.105], innerEarMaterial);
  leftInnerEar.rotation.copy(leftEar.rotation);
  const rightInnerEar = makeCone("right-inner-ear", [0.29, -0.305, 0.775], [0.112, 0.12, 0.105], innerEarMaterial);
  rightInnerEar.rotation.copy(rightEar.rotation);
  root.add(leftEar, rightEar, leftInnerEar, rightInnerEar);

  root.add(
    makeSphere("left-eye", [-0.16, -0.69, 0.47], [0.058, 0.024, 0.082], eyeMaterial, 24),
    makeSphere("right-eye", [0.16, -0.69, 0.47], [0.058, 0.024, 0.082], eyeMaterial, 24),
    makeSphere("left-eye-highlight", [-0.138, -0.71, 0.505], [0.017, 0.008, 0.021], eyeHighlightMaterial, 16),
    makeSphere("right-eye-highlight", [0.182, -0.71, 0.505], [0.017, 0.008, 0.021], eyeHighlightMaterial, 16),
    makeSphere("left-muzzle", [-0.105, -0.735, 0.27], [0.14, 0.062, 0.105], creamMaterial, 24),
    makeSphere("right-muzzle", [0.105, -0.735, 0.27], [0.14, 0.062, 0.105], creamMaterial, 24),
    makeSphere("nose", [0, -0.81, 0.37], [0.058, 0.028, 0.043], noseMaterial, 16)
  );

  for (const [index, x] of [-0.16, 0.16].entries()) {
    const direction = x < 0 ? -1 : 1;
    const side = index === 0 ? "left" : "right";
    root.add(
      makeCylinderBetween([x, -0.78, 0.31], [direction * 0.56, -0.82, 0.39], 0.008, whiskerMaterial),
      makeCylinderBetween([x, -0.79, 0.27], [direction * 0.58, -0.86, 0.27], 0.008, whiskerMaterial),
      makeCylinderBetween([x, -0.78, 0.23], [direction * 0.52, -0.82, 0.15], 0.008, whiskerMaterial)
    );
    for (let stripe = 0; stripe < 3; stripe += 1) {
      const z = 0.58 + stripe * 0.065;
      const stripeMesh = makeCylinderBetween(
        [direction * 0.06, -0.705, z],
        [direction * (0.25 + stripe * 0.025), -0.695, z + 0.025],
        0.011,
        darkerMaterial
      );
      stripeMesh.name = `${side}-forehead-stripe-${stripe + 1}`;
      root.add(stripeMesh);
    }
  }

  for (const [name, x, y] of [
    ["front-left-paw", -0.26, -0.36],
    ["front-right-paw", 0.26, -0.36],
    ["back-left-paw", -0.32, 0.24],
    ["back-right-paw", 0.32, 0.24]
  ] as const) {
    root.add(makeSphere(name, [x, y, -0.88], [0.15, 0.17, 0.1], creamMaterial, 20));
  }

  const tail = new THREE.Group();
  tail.name = "tail";
  tail.position.set(0, 0.38, -0.36);
  const tailPoints: [number, number, number][] = [
    [0, 0, 0],
    [0.12, 0.22, 0.12],
    [0.25, 0.26, 0.32],
    [0.26, 0.12, 0.52]
  ];
  for (let index = 0; index < tailPoints.length - 1; index += 1) {
    tail.add(makeCylinderBetween(tailPoints[index], tailPoints[index + 1], 0.058, darkerMaterial));
  }
  tail.add(makeSphere("tail-tip", tailPoints[tailPoints.length - 1], [0.085, 0.085, 0.085], darkerMaterial, 1));
  root.add(tail);

  root.rotation.x = -0.08;
  root.scale.setScalar(1.18);
  return root;
}

function makeSphere(name: string, position: [number, number, number], scale: [number, number, number], material: THREE.Material, segments: number) {
  const mesh = new THREE.Mesh(new THREE.SphereGeometry(1, segments, Math.max(12, Math.floor(segments / 2))), material);
  mesh.name = name;
  mesh.position.set(...position);
  mesh.scale.set(...scale);
  return mesh;
}

function makeCone(name: string, position: [number, number, number], scale: [number, number, number], material: THREE.Material) {
  const mesh = new THREE.Mesh(new THREE.ConeGeometry(1, 1, 3), material);
  mesh.name = name;
  mesh.position.set(...position);
  mesh.scale.set(...scale);
  return mesh;
}

function makeCylinderBetween(start: [number, number, number], end: [number, number, number], radius: number, material: THREE.Material) {
  const startVector = new THREE.Vector3(...start);
  const endVector = new THREE.Vector3(...end);
  const direction = endVector.clone().sub(startVector);
  const mesh = new THREE.Mesh(new THREE.CylinderGeometry(radius, radius, direction.length(), 8), material);
  mesh.position.copy(startVector.clone().add(endVector).multiplyScalar(0.5));
  mesh.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), direction.normalize());
  return mesh;
}

function animateProceduralCat(model: THREE.Object3D, actionId: SafeActionId, time: number) {
  const urgency = actionId === "running" ? 2.6 : actionId === "error" || actionId === "warning" ? 3.4 : 1;
  const bob = Math.sin(time * Math.PI * urgency) * (actionId === "sleeping" ? 0.012 : 0.035);
  model.position.y = bob;
  model.rotation.z = actionId === "error"
    ? Math.sin(time * 16) * 0.08
    : actionId === "thinking"
      ? Math.sin(time * 3.2) * 0.04
      : 0;
  const tail = model.getObjectByName("tail");
  if (tail) {
    tail.rotation.z = Math.sin(time * 3.6) * 0.2;
  }
}

function canvasLooksBlank(canvas: HTMLCanvasElement) {
  const context = canvas.getContext("webgl2") ?? canvas.getContext("webgl");
  if (!context) {
    return true;
  }
  const width = canvas.width;
  const height = canvas.height;
  if (width <= 0 || height <= 0) {
    return true;
  }
  const sampleWidth = Math.min(width, 96);
  const sampleHeight = Math.min(height, 96);
  const pixels = new Uint8Array(sampleWidth * sampleHeight * 4);
  context.readPixels(
    Math.floor((width - sampleWidth) / 2),
    Math.floor((height - sampleHeight) / 2),
    sampleWidth,
    sampleHeight,
    context.RGBA,
    context.UNSIGNED_BYTE,
    pixels
  );
  let visiblePixels = 0;
  for (let index = 3; index < pixels.length; index += 4) {
    if (pixels[index] > 8) {
      visiblePixels += 1;
    }
  }
  return visiblePixels / (sampleWidth * sampleHeight) < 0.005;
}

function clampScale(value: number) {
  if (!Number.isFinite(value)) return 1;
  return Math.min(2, Math.max(0.5, value));
}

function decodeBase64(value: string) {
  const binary = window.atob(value);
  const bytes = new Uint8Array(binary.length);
  for (let index = 0; index < binary.length; index += 1) {
    bytes[index] = binary.charCodeAt(index);
  }
  return bytes;
}

function normalizeModelForViewport(model: THREE.Object3D, camera: THREE.PerspectiveCamera | undefined) {
  model.rotation.set(0, 0, 0);
  model.updateMatrixWorld(true);

  const box = new THREE.Box3().setFromObject(model);
  if (box.isEmpty()) {
    return;
  }

  const center = new THREE.Vector3();
  const size = new THREE.Vector3();
  box.getCenter(center);
  box.getSize(size);
  model.position.sub(center);

  const maxDimension = Math.max(size.x, size.y, size.z);
  if (Number.isFinite(maxDimension) && maxDimension > 0) {
    model.scale.setScalar(1.7 / maxDimension);
  }

  if (camera) {
    setZUpPetCamera(camera);
  }
}

function setZUpPetCamera(camera: THREE.PerspectiveCamera) {
  camera.up.set(0, 0, 1);
  camera.position.set(0, -3.2, 0.35);
  camera.lookAt(0, 0, 0.2);
  camera.updateProjectionMatrix();
}
