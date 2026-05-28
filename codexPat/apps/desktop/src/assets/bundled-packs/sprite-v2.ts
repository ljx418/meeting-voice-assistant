import type { CoreActionId } from "../asset-manifest";

export type SpriteFrame = {
  actionId: CoreActionId;
  label: string;
  palette: {
    body: string;
    accent: string;
    eye: string;
  };
  pose: "sit" | "tilt" | "run" | "jump" | "alert" | "crouch" | "ask" | "sleep";
};

export const SPRITE_V2_FRAMES: Record<CoreActionId, SpriteFrame> = {
  idle: frame("idle", "Idle", "#8d99a8", "#667386", "#111827", "sit"),
  thinking: frame("thinking", "Thinking", "#8fa0ad", "#3f6f85", "#0f2937", "tilt"),
  running: frame("running", "Running", "#7da0b8", "#245f7a", "#102a43", "run"),
  success: frame("success", "Success", "#88b59b", "#34795a", "#102a1f", "jump"),
  warning: frame("warning", "Warning", "#c2aa72", "#80621f", "#2d2108", "alert"),
  error: frame("error", "Error", "#a47482", "#6b2538", "#230710", "crouch"),
  need_input: frame("need_input", "Need Input", "#9b8cc4", "#604293", "#21123f", "ask"),
  sleeping: frame("sleeping", "Sleeping", "#8792a3", "#536071", "#1f2937", "sleep")
};

export function renderSpriteFrame(frame: SpriteFrame) {
  const earOffset = frame.pose === "alert" ? "-8" : frame.pose === "sleep" ? "7" : "0";
  const bodyY = frame.pose === "jump" ? "48" : frame.pose === "crouch" || frame.pose === "sleep" ? "68" : "58";
  const headY = frame.pose === "jump" ? "18" : frame.pose === "crouch" ? "38" : frame.pose === "sleep" ? "45" : "28";
  const tilt = frame.pose === "tilt" ? " rotate(-7 80 60)" : frame.pose === "ask" ? " rotate(5 80 60)" : "";
  const tail = frame.pose === "run" ? "M115 88 C148 70 150 118 124 111" : "M113 92 C145 77 146 112 122 108";
  const eyes = frame.pose === "sleep"
    ? `<path d="M62 58 h12 M88 58 h12" stroke="${frame.palette.eye}" stroke-width="5" stroke-linecap="round"/>`
    : `<circle cx="68" cy="58" r="5" fill="${frame.palette.eye}"/><circle cx="94" cy="58" r="5" fill="${frame.palette.eye}"/>`;
  const mark = stateMark(frame);

  return `<svg viewBox="0 0 160 150" role="img" aria-label="${escapeAttr(frame.label)}">
  <ellipse cx="80" cy="130" rx="46" ry="9" fill="rgba(15,23,42,0.14)"/>
  <path d="${tail}" fill="none" stroke="${frame.palette.accent}" stroke-width="15" stroke-linecap="round"/>
  <g transform="translate(0 ${frame.pose === "run" ? "-2" : "0"})">
    <ellipse cx="80" cy="${bodyY}" rx="42" ry="${frame.pose === "crouch" || frame.pose === "sleep" ? "28" : "36"}" fill="${frame.palette.body}"/>
    <g transform="translate(0 ${earOffset})${tilt}">
      <path d="M48 ${Number(headY) + 12} L57 ${Number(headY) - 12} L70 ${Number(headY) + 13} Z" fill="${frame.palette.accent}"/>
      <path d="M91 ${Number(headY) + 13} L105 ${Number(headY) - 12} L113 ${Number(headY) + 12} Z" fill="${frame.palette.accent}"/>
      <rect x="49" y="${headY}" width="63" height="55" rx="25" fill="${frame.palette.body}"/>
      ${eyes}
      <path d="M77 70 q4 4 8 0" stroke="${frame.palette.eye}" stroke-width="3" fill="none" stroke-linecap="round"/>
    </g>
  </g>
  ${mark}
</svg>`;
}

function frame(
  actionId: CoreActionId,
  label: string,
  body: string,
  accent: string,
  eye: string,
  pose: SpriteFrame["pose"]
): SpriteFrame {
  return { actionId, label, palette: { body, accent, eye }, pose };
}

function stateMark(frame: SpriteFrame) {
  const common = `fill="${frame.palette.accent}" opacity="0.92"`;
  if (frame.actionId === "thinking") return `<circle cx="126" cy="34" r="5" ${common}/><circle cx="137" cy="24" r="3" ${common}/>`;
  if (frame.actionId === "running") return `<path d="M24 102 h25 M18 116 h31" stroke="${frame.palette.accent}" stroke-width="5" stroke-linecap="round"/>`;
  if (frame.actionId === "success") return `<path d="M126 39 l8 8 17 -19" stroke="${frame.palette.accent}" stroke-width="6" fill="none" stroke-linecap="round" stroke-linejoin="round"/>`;
  if (frame.actionId === "warning") return `<path d="M136 24 l18 34 h-36 z" fill="${frame.palette.accent}"/><circle cx="136" cy="49" r="2" fill="white"/><path d="M136 34 v10" stroke="white" stroke-width="4" stroke-linecap="round"/>`;
  if (frame.actionId === "error") return `<path d="M124 30 l25 25 M149 30 l-25 25" stroke="${frame.palette.accent}" stroke-width="7" stroke-linecap="round"/>`;
  if (frame.actionId === "need_input") return `<path d="M132 58 q0 -17 12 -17 q11 0 11 10 q0 8 -9 12 q-5 3 -5 9" stroke="${frame.palette.accent}" stroke-width="6" fill="none" stroke-linecap="round"/><circle cx="141" cy="83" r="4" fill="${frame.palette.accent}"/>`;
  if (frame.actionId === "sleeping") return `<text x="123" y="39" font-family="Arial" font-size="22" font-weight="700" fill="${frame.palette.accent}">Z</text>`;
  return "";
}

function escapeAttr(value: string) {
  return value.replace(/[&"]/g, (char) => char === "&" ? "&amp;" : "&quot;");
}
