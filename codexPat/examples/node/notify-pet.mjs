#!/usr/bin/env node
import { spawnSync } from "node:child_process";

const status = process.argv[2];

const events = {
  running: {
    level: "running",
    title: "Node 任务正在执行",
    message: "Node workflow started",
    sound: "none"
  },
  success: {
    level: "success",
    title: "Node 任务完成",
    message: "Node workflow completed",
    sound: "success_chime"
  },
  error: {
    level: "error",
    title: "Node 任务失败",
    message: "Node workflow failed",
    sound: "error_chime"
  },
  need_input: {
    level: "need_input",
    title: "Node 任务需要确认",
    message: "Node workflow needs user input",
    sound: "need_input_chime"
  }
};

if (!status || !events[status]) {
  console.error("Usage: node examples/node/notify-pet.mjs <running|success|error|need_input>");
  process.exit(2);
}

const event = events[status];
const args = [
  "notify",
  "--source-id",
  "node.local",
  "--source-kind",
  "custom",
  "--source-name",
  "Node Script",
  "--level",
  event.level,
  "--title",
  event.title,
  "--message",
  event.message,
  "--sound",
  event.sound
];

const result = spawnSync("petctl", args, {
  stdio: "inherit",
  shell: false
});

if (result.error) {
  console.error(`petctl failed: ${result.error.message}`);
  process.exit(4);
}

process.exit(result.status ?? 1);

