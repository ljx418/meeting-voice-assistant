import { readFileSync } from "node:fs";
import { resolve } from "node:path";

const glbPath = resolve("apps/desktop/public/assets/3d/agent-desktop-pet-cat-prototype.glb");
const bytes = readFileSync(glbPath);
const result = inspectGlb(bytes);

const cases = [
  ["glb magic", result.magic === "glTF"],
  ["glb version", result.version === 2],
  ["has scene", Array.isArray(result.json.scenes) && result.json.scenes.length > 0],
  ["has nodes", Array.isArray(result.json.nodes) && result.json.nodes.length >= 10],
  ["has meshes", Array.isArray(result.json.meshes) && result.json.meshes.length >= 3],
  ["has idle animation", (result.json.animations || []).some((item) => item.name === "idle")],
  ["no external uri", !JSON.stringify(result.json).includes("\"uri\"")],
  ["no forbidden text", !/(https?:\/\/|file:\/\/|\/Users\/|Authorization|api-token|raw payload|workspace path|config path|<script|javascript:)/i.test(JSON.stringify(result.json))]
];

const failed = cases.filter(([, ok]) => !ok);
console.log(JSON.stringify({ status: failed.length ? "failed" : "passed", cases: cases.map(([name, ok]) => ({ name, result: ok ? "passed" : "failed" })) }, null, 2));
if (failed.length) process.exit(1);

function inspectGlb(buffer) {
  const magic = buffer.subarray(0, 4).toString("utf8");
  const version = buffer.readUInt32LE(4);
  const jsonLength = buffer.readUInt32LE(12);
  const jsonType = buffer.readUInt32LE(16);
  if (jsonType !== 0x4E4F534A) throw new Error("missing JSON chunk");
  const json = JSON.parse(buffer.subarray(20, 20 + jsonLength).toString("utf8").trim());
  return { magic, version, json };
}

