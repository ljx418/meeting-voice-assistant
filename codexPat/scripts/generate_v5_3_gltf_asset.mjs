import { mkdirSync, writeFileSync } from "node:fs";
import { dirname, resolve } from "node:path";

const outputPath = resolve("apps/desktop/public/assets/3d/agent-desktop-pet-cat-prototype.glb");
const licensePath = resolve("apps/desktop/public/assets/3d/LICENSE-ASSET.md");

const materials = [
  { name: "Cat warm orange", color: [1.0, 0.54, 0.24, 1] },
  { name: "Cat darker orange", color: [0.82, 0.34, 0.12, 1] },
  { name: "Cat cream", color: [1.0, 0.86, 0.62, 1] },
  { name: "Cat black eyes", color: [0.02, 0.018, 0.015, 1] },
  { name: "Cat coral nose", color: [0.95, 0.18, 0.25, 1] }
];

const meshes = [
  createSphereMesh("low_poly_sphere"),
  createConeMesh("low_poly_cone"),
  createCylinderMesh("low_poly_cylinder")
];

const chunks = [];
const json = {
  asset: {
    version: "2.0",
    generator: "Agent Desktop Pet V5.3 scripted GLB generator"
  },
  scenes: [{ nodes: [0] }],
  scene: 0,
  nodes: [
    { name: "AgentDesktopPetCat_Root", children: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], extras: { asset_name: "Agent Desktop Pet generated prototype cat model", stage: "V5.4 scripted GLB action prototype", external_resources: "none", animation_clips: "idle,thinking,running,success,warning,error,need_input,sleeping" } },
    node("Cat_Body", 0, 0, [0, 0, 0.78], [0.55, 0.46, 0.62]),
    node("Cat_Head", 0, 0, [0, -0.32, 1.48], [0.5, 0.42, 0.45]),
    node("Cat_Belly", 0, 2, [0, -0.43, 0.78], [0.30, 0.055, 0.36]),
    node("Cat_Left_Ear", 1, 0, [-0.33, -0.18, 1.9], [0.24, 0.24, 0.42], [0, 0, 0.35, 0.94]),
    node("Cat_Right_Ear", 1, 0, [0.33, -0.18, 1.9], [0.24, 0.24, 0.42], [0, 0, -0.35, 0.94]),
    node("Cat_Left_Eye", 0, 3, [-0.17, -0.70, 1.62], [0.055, 0.025, 0.08]),
    node("Cat_Right_Eye", 0, 3, [0.17, -0.70, 1.62], [0.055, 0.025, 0.08]),
    node("Cat_Nose", 0, 4, [0, -0.83, 1.48], [0.065, 0.030, 0.045]),
    node("Cat_Front_Left_Paw", 0, 2, [-0.28, -0.34, 0.18], [0.17, 0.20, 0.13]),
    node("Cat_Front_Right_Paw", 0, 2, [0.28, -0.34, 0.18], [0.17, 0.20, 0.13]),
    node("Cat_Tail", 2, 1, [0.18, 0.62, 1.12], [0.08, 0.08, 0.78], [0.45, 0.12, -0.18, 0.87]),
    node("Cat_Tail_Tip", 0, 1, [0.32, 0.60, 1.52], [0.095, 0.095, 0.095])
  ],
  meshes: [],
  materials: materials.map((material) => ({
    name: material.name,
    pbrMetallicRoughness: {
      baseColorFactor: material.color,
      metallicFactor: 0,
      roughnessFactor: 0.82
    }
  })),
  buffers: [{ byteLength: 0 }],
  bufferViews: [],
  accessors: [],
  animations: []
};

for (const mesh of meshes) {
  json.meshes.push({
    name: mesh.name,
    primitives: [{
      attributes: {
        POSITION: addAccessor(mesh.positions, "VEC3", 5126),
        NORMAL: addAccessor(mesh.normals, "VEC3", 5126)
      },
      indices: addAccessor(mesh.indices, "SCALAR", 5123),
      material: 0
    }]
  });
}

addClip("idle", [
  translationChannel(0, [0, 2.5, 5], [[0, 0, 0], [0, 0, 0.035], [0, 0, 0]]),
  rotationChannel(11, [0, 1.25, 2.5, 3.75, 5], [0, 0.12, 0, -0.12, 0], "z")
]);
addClip("thinking", [
  translationChannel(0, [0, 1, 2], [[0, 0, 0], [0, 0, 0.02], [0, 0, 0]]),
  rotationChannel(2, [0, 1, 2], [-0.12, 0.12, -0.12], "x"),
  rotationChannel(11, [0, 1, 2], [-0.06, 0.06, -0.06], "z")
]);
addClip("running", [
  translationChannel(0, [0, 0.25, 0.5, 0.75, 1], [[0, 0, 0], [0.035, 0, 0.06], [0, 0, 0], [-0.035, 0, 0.06], [0, 0, 0]]),
  rotationChannel(11, [0, 0.25, 0.5, 0.75, 1], [0.2, -0.2, 0.2, -0.2, 0.2], "z")
]);
addClip("success", [
  translationChannel(0, [0, 0.35, 0.7, 1.2], [[0, 0, 0], [0, 0, 0.18], [0, 0, 0.04], [0, 0, 0]]),
  rotationChannel(2, [0, 0.35, 0.7, 1.2], [0, 0.18, -0.08, 0], "x")
]);
addClip("warning", [
  translationChannel(0, [0, 0.3, 0.6, 0.9, 1.2], [[0, 0, 0], [-0.04, 0, 0], [0.04, 0, 0], [-0.03, 0, 0], [0, 0, 0]]),
  rotationChannel(2, [0, 0.3, 0.6, 0.9, 1.2], [-0.18, 0.18, -0.18, 0.12, 0], "z")
]);
addClip("error", [
  translationChannel(0, [0, 0.45, 0.9, 1.35], [[0, 0, 0], [0, 0, -0.05], [0, 0, 0.02], [0, 0, -0.03]]),
  rotationChannel(2, [0, 0.45, 0.9, 1.35], [0.2, -0.14, 0.12, 0.18], "z")
]);
addClip("need_input", [
  translationChannel(0, [0, 0.5, 1, 1.5], [[0, 0, 0], [0, -0.025, 0.09], [0, 0, 0], [0, -0.025, 0.09]]),
  rotationChannel(2, [0, 0.5, 1, 1.5], [-0.1, -0.24, -0.1, -0.24], "x")
]);
addClip("sleeping", [
  translationChannel(0, [0, 2, 4], [[0, 0, -0.04], [0, 0, -0.075], [0, 0, -0.04]]),
  rotationChannel(2, [0, 2, 4], [0.18, 0.22, 0.18], "x"),
  rotationChannel(11, [0, 2, 4], [-0.18, -0.22, -0.18], "z")
]);

const bin = concatBuffers(chunks);
json.buffers[0].byteLength = bin.byteLength;
const glb = createGlb(json, bin);

mkdirSync(dirname(outputPath), { recursive: true });
writeFileSync(outputPath, glb);
writeFileSync(licensePath, licenseText(), "utf8");
console.log(JSON.stringify({ ok: true, glb: "apps/desktop/public/assets/3d/agent-desktop-pet-cat-prototype.glb", license: "apps/desktop/public/assets/3d/LICENSE-ASSET.md", animations: json.animations.map((animation) => animation.name) }, null, 2));

function node(name, mesh, material, translation, scale, rotation) {
  const value = { name, mesh, translation, scale };
  if (rotation) value.rotation = rotation;
  return value;
}

function addAccessor(array, type, componentType) {
  const byteOffset = pushArray(array);
  const bufferView = json.bufferViews.push({ buffer: 0, byteOffset, byteLength: array.byteLength }) - 1;
  const accessor = { bufferView, componentType, count: countFor(type, array), type };
  if (type === "VEC3" && componentType === 5126) {
    accessor.min = vec3Min(array);
    accessor.max = vec3Max(array);
  }
  if (type === "SCALAR" && componentType === 5126) {
    accessor.min = [Math.min(...array)];
    accessor.max = [Math.max(...array)];
  }
  return json.accessors.push(accessor) - 1;
}

function addClip(name, channelSpecs) {
  const samplers = [];
  const channels = [];
  for (const spec of channelSpecs) {
    const sampler = samplers.push({
      input: addAccessor(new Float32Array(spec.times), "SCALAR", 5126),
      output: addAccessor(new Float32Array(spec.values.flat()), spec.type, 5126),
      interpolation: "LINEAR"
    }) - 1;
    channels.push({ sampler, target: { node: spec.node, path: spec.path } });
  }
  json.animations.push({ name, samplers, channels });
}

function translationChannel(nodeIndex, times, values) {
  return { node: nodeIndex, path: "translation", times, values, type: "VEC3" };
}

function rotationChannel(nodeIndex, times, radians, axis) {
  return {
    node: nodeIndex,
    path: "rotation",
    times,
    values: radians.map((value) => axisQuaternion(axis, value)),
    type: "VEC4"
  };
}

function axisQuaternion(axis, radians) {
  const half = radians / 2;
  const sin = Math.sin(half);
  const cos = Math.cos(half);
  if (axis === "x") return [sin, 0, 0, cos];
  if (axis === "y") return [0, sin, 0, cos];
  return [0, 0, sin, cos];
}

function pushArray(array) {
  const offset = chunks.reduce((sum, item) => sum + item.byteLength, 0);
  chunks.push(Buffer.from(array.buffer));
  const padding = (4 - (array.byteLength % 4)) % 4;
  if (padding) chunks.push(Buffer.alloc(padding));
  return offset;
}

function countFor(type, array) {
  if (type === "VEC4") return array.length / 4;
  if (type === "VEC3") return array.length / 3;
  return array.length;
}

function vec3Min(array) {
  const min = [Infinity, Infinity, Infinity];
  for (let i = 0; i < array.length; i += 3) {
    min[0] = Math.min(min[0], array[i]);
    min[1] = Math.min(min[1], array[i + 1]);
    min[2] = Math.min(min[2], array[i + 2]);
  }
  return min;
}

function vec3Max(array) {
  const max = [-Infinity, -Infinity, -Infinity];
  for (let i = 0; i < array.length; i += 3) {
    max[0] = Math.max(max[0], array[i]);
    max[1] = Math.max(max[1], array[i + 1]);
    max[2] = Math.max(max[2], array[i + 2]);
  }
  return max;
}

function createSphereMesh(name) {
  const positions = [];
  const normals = [];
  const indices = [];
  const lat = 6;
  const lon = 10;
  for (let y = 0; y <= lat; y++) {
    const v = y / lat;
    const theta = v * Math.PI;
    for (let x = 0; x <= lon; x++) {
      const u = x / lon;
      const phi = u * Math.PI * 2;
      const nx = Math.sin(theta) * Math.cos(phi);
      const ny = Math.sin(theta) * Math.sin(phi);
      const nz = Math.cos(theta);
      positions.push(nx, ny, nz);
      normals.push(nx, ny, nz);
    }
  }
  for (let y = 0; y < lat; y++) {
    for (let x = 0; x < lon; x++) {
      const a = y * (lon + 1) + x;
      const b = a + lon + 1;
      indices.push(a, b, a + 1, b, b + 1, a + 1);
    }
  }
  return { name, positions: new Float32Array(positions), normals: new Float32Array(normals), indices: new Uint16Array(indices) };
}

function createConeMesh(name) {
  const positions = [0, 0, 1, -0.7, -0.5, 0, 0.7, -0.5, 0, 0, 0.75, 0];
  const normals = [0, 0, 1, -0.6, -0.4, 0.7, 0.6, -0.4, 0.7, 0, 1, 0];
  const indices = [0, 1, 2, 0, 2, 3, 0, 3, 1, 1, 3, 2];
  return { name, positions: new Float32Array(positions), normals: new Float32Array(normals), indices: new Uint16Array(indices) };
}

function createCylinderMesh(name) {
  const positions = [];
  const normals = [];
  const indices = [];
  const segments = 8;
  for (let z of [-1, 1]) {
    for (let i = 0; i < segments; i++) {
      const a = i / segments * Math.PI * 2;
      const x = Math.cos(a);
      const y = Math.sin(a);
      positions.push(x, y, z);
      normals.push(x, y, 0);
    }
  }
  for (let i = 0; i < segments; i++) {
    const next = (i + 1) % segments;
    indices.push(i, i + segments, next, next, i + segments, next + segments);
  }
  return { name, positions: new Float32Array(positions), normals: new Float32Array(normals), indices: new Uint16Array(indices) };
}

function concatBuffers(buffers) {
  return Buffer.concat(buffers.map((item) => Buffer.from(item)));
}

function createGlb(gltf, binary) {
  const jsonBytes = Buffer.from(JSON.stringify(gltf), "utf8");
  const jsonPadding = (4 - (jsonBytes.byteLength % 4)) % 4;
  const binPadding = (4 - (binary.byteLength % 4)) % 4;
  const jsonChunk = Buffer.concat([jsonBytes, Buffer.alloc(jsonPadding, 0x20)]);
  const binChunk = Buffer.concat([binary, Buffer.alloc(binPadding)]);
  const totalLength = 12 + 8 + jsonChunk.byteLength + 8 + binChunk.byteLength;
  const header = Buffer.alloc(12);
  header.writeUInt32LE(0x46546C67, 0);
  header.writeUInt32LE(2, 4);
  header.writeUInt32LE(totalLength, 8);
  const jsonHeader = Buffer.alloc(8);
  jsonHeader.writeUInt32LE(jsonChunk.byteLength, 0);
  jsonHeader.writeUInt32LE(0x4E4F534A, 4);
  const binHeader = Buffer.alloc(8);
  binHeader.writeUInt32LE(binChunk.byteLength, 0);
  binHeader.writeUInt32LE(0x004E4942, 4);
  return Buffer.concat([header, jsonHeader, jsonChunk, binHeader, binChunk]);
}

function licenseText() {
  return `# Agent Desktop Pet Generated Prototype Cat Model

Asset: agent-desktop-pet-cat-prototype.glb

Attribution: Agent Desktop Pet generated prototype cat model

## Origin

This model is a project-authored generated asset created by a local JavaScript GLB generator for V5.3.

## Permissions

The Agent Desktop Pet project may use, modify, bundle, and distribute this generated asset as part of project prototypes, demos, and packaged builds.

## Asset Notes

- No third-party model, texture, image, shader asset, or external media is used.
- No network asset location is referenced.
- No local image, model, texture, credential material, auth header material, workspace location, or config location is referenced.
- The asset is intended as a prototype validation asset, not a final commercial-quality character model.
`;
}
