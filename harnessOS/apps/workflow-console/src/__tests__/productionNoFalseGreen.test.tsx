import assert from "node:assert/strict";
import { readFileSync, readdirSync, statSync } from "node:fs";
import { join } from "node:path";
import test from "node:test";

const forbiddenClaims = [
  ["production-ready external app", "support"].join(" "),
  ["enterprise auth", "ready"].join(" "),
  ["multi-tenant control plane", "ready"].join(" "),
  ["controlled executor", "ready"].join(" "),
  ["Agent executor", "ready"].join(" "),
  ["complete Workflow Studio", "ready"].join(" "),
  ["complete AgentTalkWindow", "ready"].join(" "),
];

const forbiddenCopy = [
  ["企业级认证", "已完成"].join(""),
  ["多租户控制台", "已完成"].join(""),
  ["生产接入", "已完成"].join(""),
  ["已支持生产客户", "接入"].join(""),
  ["production", "ready"].join(" "),
];

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

test("workflow console source has no production implementation routes", () => {
  const source = sourceFiles("src").map((file) => readFileSync(file, "utf8")).join("\n");
  for (const forbidden of ["/oauth", "/sso", "/tenant", "/admin/tenant", "/production/onboarding", "/token/rotate", "/token/revoke", "/quota", "/audit/export"]) {
    assert(!source.includes(forbidden), `${forbidden} appeared in workflow-console source`);
  }
});

test("workflow console copy avoids production false-green language", () => {
  const source = sourceFiles("src").map((file) => readFileSync(file, "utf8")).join("\n");
  for (const claim of forbiddenClaims) {
    assert(!source.includes(claim), `${claim} appeared in workflow-console source`);
  }
  for (const copy of forbiddenCopy) {
    assert(!source.includes(copy), `${copy} appeared in workflow-console source`);
  }
});
