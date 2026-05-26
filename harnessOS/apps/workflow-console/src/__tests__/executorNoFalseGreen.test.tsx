import assert from "node:assert/strict";
import { readFileSync, readdirSync, statSync } from "node:fs";
import { join } from "node:path";
import test from "node:test";

const forbiddenClaims = [
  ["controlled executor", "ready"].join(" "),
  ["Agent executor", "ready"].join(" "),
  ["autonomous workflow editing", "ready"].join(" "),
  ["production-ready external app", "support"].join(" "),
  ["complete AgentTalkWindow", "ready"].join(" "),
  ["complete Workflow Studio", "ready"].join(" "),
  ["full low-code canvas editing", "ready"].join(" "),
];

const forbiddenCopy = [["自动", "应用"].join(""), ["自动", "发布"].join(""), ["Agent 已", "执行"].join(""), ["Agent 已", "发布"].join("")];

function sourceFiles(root: string): string[] {
  const entries = readdirSync(root);
  const files: string[] = [];
  for (const entry of entries) {
    if (entry === "__tests__") {
      continue;
    }
    const fullPath = join(root, entry);
    const stat = statSync(fullPath);
    if (stat.isDirectory()) {
      files.push(...sourceFiles(fullPath));
    } else if (/\.(ts|tsx|js|jsx|css)$/.test(entry)) {
      files.push(fullPath);
    }
  }
  return files;
}

test("workflow console source has no executor callable routes", () => {
  const source = sourceFiles("src").map((file) => readFileSync(file, "utf8")).join("\n");
  for (const forbidden of ["/agent/execute", "/execute", "/kill-switch", "/rollback", "/admin-override", "connector.call", "external_llm.call"]) {
    assert(!source.includes(forbidden), `${forbidden} appeared in workflow-console source`);
  }
});

test("workflow console copy avoids executor false-green language", () => {
  const source = sourceFiles("src").map((file) => readFileSync(file, "utf8")).join("\n");
  for (const claim of forbiddenClaims) {
    assert(!source.includes(claim), `${claim} appeared in workflow-console source`);
  }
  for (const copy of forbiddenCopy) {
    assert(!source.includes(copy), `${copy} appeared in workflow-console source`);
  }
});
