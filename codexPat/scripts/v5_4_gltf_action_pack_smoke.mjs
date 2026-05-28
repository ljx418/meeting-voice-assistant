import { readFileSync } from "node:fs";
import { resolve } from "node:path";

const glbPath = resolve("apps/desktop/public/assets/3d/agent-desktop-pet-cat-prototype.glb");
const requiredClips = ["idle", "thinking", "running", "success", "warning", "error", "need_input", "sleeping"];
const bytes = readFileSync(glbPath);
const result = inspectGlb(bytes);
const jsonText = JSON.stringify(result.json);
const animations = Array.isArray(result.json.animations) ? result.json.animations : [];
const clipNames = animations.map((item) => item.name);
const channelSignatures = new Map(animations.map((animation) => [animation.name, animationSignature(result, animation)]));
const uniqueSignatures = new Set([...channelSignatures.values()]);

const cases = [
  ["glb magic", result.magic === "glTF"],
  ["glb version", result.version === 2],
  ["all core action clips present", requiredClips.every((name) => clipNames.includes(name))],
  ["core clips have channels", requiredClips.every((name) => (animations.find((item) => item.name === name)?.channels || []).length > 0)],
  ["core clips are not all identical", uniqueSignatures.size >= 4],
  ["no external uri", !jsonText.includes("\"uri\"")],
  ["no forbidden text", !/(https?:\/\/|file:\/\/|\/Users\/|Authorization|api-token|raw payload|workspace path|config path|<script|javascript:)/i.test(jsonText)]
];

const failed = cases.filter(([, ok]) => !ok);
console.log(JSON.stringify({
  status: failed.length ? "failed" : "passed",
  clips: clipNames,
  cases: cases.map(([name, ok]) => ({ name, result: ok ? "passed" : "failed" }))
}, null, 2));
if (failed.length) process.exit(1);

function inspectGlb(buffer) {
  const magic = buffer.subarray(0, 4).toString("utf8");
  const version = buffer.readUInt32LE(4);
  const jsonLength = buffer.readUInt32LE(12);
  const jsonType = buffer.readUInt32LE(16);
  if (jsonType !== 0x4E4F534A) throw new Error("missing JSON chunk");
  const binHeaderOffset = 20 + jsonLength;
  const binLength = buffer.readUInt32LE(binHeaderOffset);
  const binType = buffer.readUInt32LE(binHeaderOffset + 4);
  if (binType !== 0x004E4942) throw new Error("missing BIN chunk");
  const json = JSON.parse(buffer.subarray(20, 20 + jsonLength).toString("utf8").trim());
  const binary = buffer.subarray(binHeaderOffset + 8, binHeaderOffset + 8 + binLength);
  return { magic, version, json, binary };
}

function animationSignature(result, animation) {
  return (animation.samplers || [])
    .map((sampler) => accessorSummary(result, sampler.output))
    .join("|");
}

function accessorSummary(result, accessorIndex) {
  const accessor = result.json.accessors[accessorIndex];
  const view = result.json.bufferViews[accessor.bufferView];
  const offset = (view.byteOffset || 0) + (accessor.byteOffset || 0);
  const components = accessor.type === "VEC4" ? 4 : accessor.type === "VEC3" ? 3 : 1;
  const values = [];
  for (let index = 0; index < accessor.count * components; index += 1) {
    values.push(Number(result.binary.readFloatLE(offset + index * 4).toFixed(4)));
  }
  return values.join(",");
}
