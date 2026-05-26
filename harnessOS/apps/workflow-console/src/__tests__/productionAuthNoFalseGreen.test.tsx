import assert from "node:assert/strict";
import { readFileSync, readdirSync, statSync } from "node:fs";
import { join } from "node:path";
import test from "node:test";

const forbiddenClaims = [
  ["enterprise auth", "ready"].join(" "),
  ["multi-tenant control plane", "ready"].join(" "),
  ["OAuth", "ready"].join(" "),
  ["SSO", "ready"].join(" "),
  ["production-ready external app", "support"].join(" "),
  ["controlled executor", "ready"].join(" "),
  ["Agent executor", "ready"].join(" "),
];

const forbiddenCopy = [
  ["生产", "可用"].join(""),
  ["生产认证", "已完成"].join(""),
  ["企业认证", "可用"].join(""),
  ["企业级认证", "已完成"].join(""),
  ["多租户控制台", "已完成"].join(""),
  ["OAuth ", "已接入"].join(""),
  ["SSO ", "已接入"].join(""),
  ["生产接入", "已完成"].join(""),
  ["生产客户可", "接入"].join(""),
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

test("workflow console source has no production auth implementation routes", () => {
  const source = sourceFiles("src").map((file) => readFileSync(file, "utf8")).join("\n");
  for (const forbidden of ["/oauth", "/sso", "/oidc", "/saml", "/login/callback", "/tenant", "/admin/tenant", "/token/rotate", "/token/revoke"]) {
    assert(!source.includes(forbidden), `${forbidden} appeared in workflow-console source`);
  }
});

test("workflow console copy avoids production auth false-green language", () => {
  const source = sourceFiles("src").map((file) => readFileSync(file, "utf8")).join("\n");
  for (const claim of forbiddenClaims) {
    assert(!source.includes(claim), `${claim} appeared in workflow-console source`);
  }
  for (const copy of forbiddenCopy) {
    assert(!source.includes(copy), `${copy} appeared in workflow-console source`);
  }
});
