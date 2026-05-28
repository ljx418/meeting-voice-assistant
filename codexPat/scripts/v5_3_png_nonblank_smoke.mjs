import { readFileSync } from "node:fs";

const pngPath = process.argv[2];
if (!pngPath) {
  console.error("usage: node scripts/v5_3_png_nonblank_smoke.mjs <png>");
  process.exit(2);
}

const bytes = readFileSync(pngPath);
const ok = bytes.subarray(1, 4).toString("utf8") === "PNG" && bytes.byteLength > 10000;
console.log(JSON.stringify({ status: ok ? "passed" : "failed", pngBytes: bytes.byteLength }, null, 2));
if (!ok) process.exit(1);

