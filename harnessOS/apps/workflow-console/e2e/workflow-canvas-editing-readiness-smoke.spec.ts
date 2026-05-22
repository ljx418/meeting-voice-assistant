import { expect, test } from "@playwright/test";

const SENSITIVE_TEXT = [
  "capability_token",
  "subscription_token",
  "Authorization",
  "Bearer",
  "raw_trace_payload",
  "raw_artifact_content",
  "raw_connector_payload",
  "secret-token-value",
];

test("canvas editing readiness stays projection and proposal based", async ({ page }) => {
  const browserRequests: Array<{ path: string; method: string; body?: string | null }> = [];
  page.on("request", (request) => {
    browserRequests.push({ path: new URL(request.url()).pathname, method: request.method(), body: request.postData() });
  });
  page.on("dialog", (dialog) => dialog.accept());

  await page.goto("/");
  await expect(page.getByTestId("workflow-console")).toBeVisible();
  const beforeCards = await page.getByTestId("station-card").count();
  const beforeStatus = await page.getByTestId("workflow-status").textContent();

  const proposalResponse = page.waitForResponse((response) => {
    const url = new URL(response.url());
    return url.pathname.includes("/bff/workflows/") && url.pathname.endsWith("/patches") && response.request().method() === "POST";
  });
  await page.locator("button.library-node").filter({ hasText: "角色一致性检查" }).first().click();
  const proposal = await proposalResponse;
  expect(proposal.ok()).toBeTruthy();
  const proposalBody = (await proposal.json()) as { workflow_template_id: string; workflow_patch_id: string };
  await expect(page.getByTestId("ghost-node")).toBeVisible();
  await expect(page.getByText("Pending Proposal")).toBeVisible();
  await page.getByRole("button", { name: "Patch", exact: true }).click();
  await expect(page.getByTestId("editing-panel").first()).toBeVisible();
  await expect(page.getByTestId("patch-status").first()).toHaveText("proposed");
  await expect(page.getByTestId("workflow-status")).toHaveText(beforeStatus || "");
  await expect(page.getByTestId("station-card")).toHaveCount(beforeCards);

  const applyResponse = page.waitForResponse((response) => {
    const url = new URL(response.url());
    return url.pathname.includes("/patches/") && url.pathname.endsWith("/apply") && response.request().method() === "POST";
  });
  await page.getByTestId("patch-apply-button").first().click();
  expect((await applyResponse).ok()).toBeTruthy();
  await expect(page.getByTestId("station-card")).toHaveCount(beforeCards + 1);
  await expect(page.getByText("角色一致性检查").first()).toBeVisible();

  const invalidEdge = await page.request.post(`/bff/workflows/${proposalBody.workflow_template_id}/patches`, {
    data: {
      source: "canvas",
      intent_type: "edge_add",
      operation: "update_edge",
      payload: { edge_id: "edge_self_smoke", edge_patch: { action: "add", from_station_id: "station_b", to_station_id: "station_b" } },
    },
  });
  expect(invalidEdge.ok()).toBeFalsy();
  const edgeResponse = page.waitForResponse((response) => {
    const url = new URL(response.url());
    return url.pathname.includes("/bff/workflows/") && url.pathname.endsWith("/patches") && response.request().method() === "POST";
  });
  await page.getByTestId("edge-proposal-button").last().click();
  expect((await edgeResponse).ok()).toBeTruthy();

  await page.getByRole("button", { name: "节点配置", exact: true }).click();
  const patchPostCount = browserRequests.filter((request) => request.method === "POST" && request.path.includes("/bff/workflows/") && request.path.endsWith("/patches")).length;
  await page.getByTestId("inspector-prompt-input").fill("增强角色一致性和镜头衔接");
  expect(browserRequests.filter((request) => request.method === "POST" && request.path.includes("/bff/workflows/") && request.path.endsWith("/patches")).length).toBe(patchPostCount);
  const inspectorProposal = page.waitForResponse((response) =>
    response.url().includes("/bff/workflows/") && response.url().includes("/patches") && response.request().method() === "POST",
  );
  await page.getByTestId("inspector-generate-patch-button").click();
  expect((await inspectorProposal).ok()).toBeTruthy();

  const requestPaths = browserRequests.map((request) => request.path);
  expect(requestPaths).not.toContain("/v1/rpc");
  expect(requestPaths).not.toContain("/v1/events/subscribe");
  for (const request of browserRequests) {
    if (request.method === "POST" && request.path.includes("/bff/workflows/") && request.path.endsWith("/patches")) {
      for (const forbidden of ["position", "viewport", "zoom", "selectedNode", "panelCollapsed", "activeTab"]) {
        expect(request.body || "").not.toContain(forbidden);
      }
    }
  }
  const bodyText = (await page.locator("body").textContent()) || "";
  const html = await page.content();
  for (const value of SENSITIVE_TEXT) {
    expect(bodyText).not.toContain(value);
    expect(html).not.toContain(value);
  }
});
