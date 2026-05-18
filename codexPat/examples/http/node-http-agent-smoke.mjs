#!/usr/bin/env node

const url = (process.env.AGENT_DESKTOP_PET_URL || "http://127.0.0.1:17321").replace(/\/+$/, "");
const token = process.env.AGENT_DESKTOP_PET_TOKEN;
const level = process.argv[2] || "success";

const allowed = new Set(["thinking", "running", "success", "warning", "error", "need_input"]);
const sounds = {
  success: "success_chime",
  warning: "warning_chime",
  error: "error_chime",
  need_input: "need_input_chime"
};

if (!token) {
  console.error("AGENT_DESKTOP_PET_TOKEN is required. Token will not be printed.");
  process.exit(2);
}

if (!allowed.has(level)) {
  console.error(`Unsupported level: ${level}`);
  process.exit(2);
}

const payload = {
  source: {
    id: "http-node.local",
    kind: "custom",
    name: "HTTP Node Smoke"
  },
  level,
  title: `Node HTTP smoke: ${level}`,
  sound: sounds[level] || "none"
};

try {
  const response = await fetch(`${url}/api/events`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json"
    },
    body: JSON.stringify(payload)
  });
  const body = await response.text();
  console.log(body);
  process.exit(response.ok ? 0 : 1);
} catch (error) {
  console.error(error instanceof Error ? error.message : String(error));
  process.exit(4);
}

