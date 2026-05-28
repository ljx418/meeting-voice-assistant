import { mkdirSync, writeFileSync } from "node:fs";
import { dirname, resolve } from "node:path";

const outputPath = resolve("docs/V5.x/evidence/v5_1-sprite-visual-fixture-2026-05-28.html");
const actions = [
  ["idle", "Idle", "#8d99a8", "#667386"],
  ["thinking", "Thinking", "#8fa0ad", "#3f6f85"],
  ["running", "Running", "#7da0b8", "#245f7a"],
  ["success", "Success", "#88b59b", "#34795a"],
  ["warning", "Warning", "#c2aa72", "#80621f"],
  ["error", "Error", "#a47482", "#6b2538"],
  ["need_input", "Need Input", "#9b8cc4", "#604293"],
  ["sleeping", "Sleeping", "#8792a3", "#536071"]
];

mkdirSync(dirname(outputPath), { recursive: true });
writeFileSync(outputPath, renderHtml(), "utf8");
console.log(JSON.stringify({ ok: true, output: "docs/V5.x/evidence/v5_1-sprite-visual-fixture-2026-05-28.html", actionCount: actions.length }, null, 2));

function renderHtml() {
  return `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>V5.1 Sprite Visual Fixture</title>
<style>
body { margin: 0; font-family: Inter, system-ui, sans-serif; background: #f8fafc; color: #18212f; }
main { padding: 24px; }
.grid { display: grid; grid-template-columns: repeat(4, minmax(160px, 1fr)); gap: 16px; max-width: 900px; }
.tile { background: white; border: 1px solid #dbe3ee; border-radius: 8px; padding: 14px; }
.tile h2 { margin: 0 0 10px; font-size: 14px; }
svg { display: block; width: 100%; height: 150px; }
</style>
</head>
<body>
<main>
<h1>V5.1 Sprite Visual Fixture</h1>
<p>Bundled static 2D sprite smoke for core pet states.</p>
<section class="grid">
${actions.map(([id, label, body, accent]) => `<article class="tile" data-action="${id}"><h2>${label}</h2>${svg(label, body, accent)}</article>`).join("\n")}
</section>
</main>
</body>
</html>
`;
}

function svg(label, body, accent) {
  return `<svg viewBox="0 0 160 150" role="img" aria-label="${label}">
<ellipse cx="80" cy="130" rx="46" ry="9" fill="rgba(15,23,42,0.14)"/>
<path d="M113 92 C145 77 146 112 122 108" fill="none" stroke="${accent}" stroke-width="15" stroke-linecap="round"/>
<ellipse cx="80" cy="60" rx="42" ry="36" fill="${body}"/>
<path d="M48 40 L57 16 L70 41 Z" fill="${accent}"/>
<path d="M91 41 L105 16 L113 40 Z" fill="${accent}"/>
<rect x="49" y="28" width="63" height="55" rx="25" fill="${body}"/>
<circle cx="68" cy="58" r="5" fill="#111827"/><circle cx="94" cy="58" r="5" fill="#111827"/>
<path d="M77 70 q4 4 8 0" stroke="#111827" stroke-width="3" fill="none" stroke-linecap="round"/>
<text x="18" y="142" font-size="12" fill="${accent}" font-weight="700">${label}</text>
</svg>`;
}

