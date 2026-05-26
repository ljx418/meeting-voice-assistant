import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";
import { WorkflowConsoleClient } from "../api/workflowConsoleClient.js";

interface ProductionReadinessContract {
  runtime_enabled: boolean;
  production_implementation_enabled: boolean;
  production_gaps: Array<{ category: string; status: string; blocking_for_production: boolean }>;
  forbidden_implementation_routes: string[];
}

function loadContract(): ProductionReadinessContract {
  return JSON.parse(readFileSync("../../docs/design/V4.0/v4_0_r_production_readiness_preflight_contract.json", "utf8")) as ProductionReadinessContract;
}

test("production readiness preflight contract stays design-only", () => {
  const contract = loadContract();
  assert.equal(contract.runtime_enabled, false);
  assert.equal(contract.production_implementation_enabled, false);
  assert.equal(contract.production_gaps.length, 10);
  for (const gap of contract.production_gaps) {
    assert.equal(gap.status, "open_gap", gap.category);
    assert.equal(gap.blocking_for_production, true, gap.category);
  }
});

test("production preflight contract covers required gap categories", () => {
  const categories = new Set(loadContract().production_gaps.map((gap) => gap.category));
  for (const category of [
    "auth_sso_oauth",
    "multi_tenant_isolation",
    "capability_token_lifecycle",
    "secret_management",
    "audit_retention",
    "observability_metrics_alerting",
    "rate_limit_abuse_control",
    "data_residency_export_deletion",
    "external_app_onboarding",
    "incident_recovery",
  ]) {
    assert(categories.has(category), `${category} missing from production readiness preflight contract`);
  }
});

test("workflow console client does not expose production admin routes", async () => {
  const calls: string[] = [];
  const originalFetch = globalThis.fetch;
  globalThis.fetch = (async (input: RequestInfo | URL) => {
    calls.push(String(input));
    return new Response(JSON.stringify([]), { status: 200, headers: { "content-type": "application/json" } });
  }) as typeof fetch;
  try {
    const client = new WorkflowConsoleClient("/bff");
    await client.listWorkflows();
  } finally {
    globalThis.fetch = originalFetch;
  }
  assert.deepEqual(calls, ["/bff/workflows"]);
  for (const call of calls) {
    for (const forbidden of ["/oauth", "/sso", "/tenant", "/production/onboarding", "/token/rotate", "/token/revoke", "/quota", "/audit/export"]) {
      assert(!call.includes(forbidden), `${forbidden} appeared in frontend BFF call`);
    }
  }
});
