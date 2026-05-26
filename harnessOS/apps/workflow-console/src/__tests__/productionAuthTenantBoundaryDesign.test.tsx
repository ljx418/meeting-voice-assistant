import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";
import { WorkflowConsoleClient } from "../api/workflowConsoleClient.js";

interface IdentityField {
  field: string;
  current_status: string;
  client_supplied_allowed: boolean;
  server_bound_required: boolean;
}

interface AuthTenantContract {
  runtime_enabled: boolean;
  production_auth_implementation_enabled: boolean;
  tenant_control_plane_enabled: boolean;
  oauth_sso_implementation_enabled: boolean;
  identity_fields: IdentityField[];
  oauth_sso_gap_contract: Array<{ capability: string; status: string }>;
}

function loadContract(): AuthTenantContract {
  return JSON.parse(readFileSync("../../docs/design/V4.0/v4_0_s_production_auth_tenant_boundary_design_contract.json", "utf8")) as AuthTenantContract;
}

test("production auth tenant contract stays design-only", () => {
  const contract = loadContract();
  assert.equal(contract.runtime_enabled, false);
  assert.equal(contract.production_auth_implementation_enabled, false);
  assert.equal(contract.tenant_control_plane_enabled, false);
  assert.equal(contract.oauth_sso_implementation_enabled, false);
});

test("production auth tenant contract separates dev-local scope fields from production gaps", () => {
  const fields = new Map(loadContract().identity_fields.map((field) => [field.field, field]));
  for (const field of ["app_id", "project_id", "workspace_id"]) {
    assert.equal(fields.get(field)?.current_status, "current_dev_local_scope_guard");
  }
  for (const field of ["tenant_id", "user_id", "service_account_id"]) {
    assert.equal(fields.get(field)?.current_status, "production_gap");
    assert.equal(fields.get(field)?.client_supplied_allowed, false);
    assert.equal(fields.get(field)?.server_bound_required, true);
  }
});

test("OAuth and SSO capabilities remain gaps", () => {
  for (const item of loadContract().oauth_sso_gap_contract) {
    assert(["gap_only", "planned_future"].includes(item.status), item.capability);
    assert.notEqual(item.status, "implemented", item.capability);
  }
});

test("workflow console client does not expose production auth or tenant routes", async () => {
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
    for (const forbidden of ["/oauth", "/sso", "/oidc", "/saml", "/login/callback", "/tenant", "/admin/tenant", "/token/rotate", "/token/revoke"]) {
      assert(!call.includes(forbidden), `${forbidden} appeared in frontend BFF call`);
    }
  }
});
