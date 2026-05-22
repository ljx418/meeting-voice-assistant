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

test("canvas and inspector create governed patch proposals without direct runtime calls", async ({ page }) => {
  const browserRequests: Array<{ path: string; method: string }> = [];
  page.on("request", (request) => {
    browserRequests.push({ path: new URL(request.url()).pathname, method: request.method() });
  });

  await page.goto("/");
  await expect(page.getByTestId("workflow-console")).toBeVisible();
  await expect(page.getByTestId("station-board")).toBeVisible();

  const proposalResponse = page.waitForResponse((response) => {
    const url = new URL(response.url());
    return url.pathname.includes("/bff/workflows/") && url.pathname.endsWith("/patches") && response.request().method() === "POST";
  });
  await page.locator("button.library-node").filter({ hasText: "角色一致性检查" }).first().click();
  const proposal = await proposalResponse;
  expect(proposal.ok()).toBeTruthy();
  const proposalBody = (await proposal.json()) as { workflow_template_id: string; workflow_patch_id: string };
  await page.getByRole("button", { name: "Patch", exact: true }).click();
  await expect(page.getByTestId("editing-panel")).toBeVisible();
  await expect(page.getByTestId("patch-status")).toHaveText("proposed");
  await page.request.post(`/bff/workflows/${proposalBody.workflow_template_id}/patches/${proposalBody.workflow_patch_id}/reject`, {
    data: { user_confirmed: true, source: "workflow_console", reason: "canvas smoke cleanup" },
  });

  await page.getByRole("button", { name: "节点配置", exact: true }).click();
  const proposalPostCount = browserRequests.filter((request) => request.method === "POST" && request.path.includes("/bff/workflows/") && request.path.endsWith("/patches")).length;
  await page.getByTestId("inspector-prompt-input").fill("增强角色一致性和镜头衔接");
  expect(browserRequests.filter((request) => request.method === "POST" && request.path.includes("/bff/workflows/") && request.path.endsWith("/patches")).length).toBe(proposalPostCount);
  const inspectorProposal = page.waitForResponse((response) =>
    response.url().includes("/bff/workflows/") && response.url().includes("/patches") && response.request().method() === "POST",
  );
  await page.getByTestId("inspector-generate-patch-button").click();
  const inspectorProposalResponse = await inspectorProposal;
  expect(inspectorProposalResponse.ok()).toBeTruthy();
  const inspectorProposalBody = (await inspectorProposalResponse.json()) as { workflow_template_id: string; workflow_patch_id: string };
  await page.request.post(`/bff/workflows/${inspectorProposalBody.workflow_template_id}/patches/${inspectorProposalBody.workflow_patch_id}/reject`, {
    data: { user_confirmed: true, source: "workflow_console", reason: "inspector smoke cleanup" },
  });

  expect(browserRequests.map((request) => request.path)).not.toContain("/v1/rpc");
  expect(browserRequests.map((request) => request.path)).not.toContain("/v1/events/subscribe");
  const bodyText = (await page.locator("body").textContent()) || "";
  const html = await page.content();
  for (const value of SENSITIVE_TEXT) {
    expect(bodyText).not.toContain(value);
    expect(html).not.toContain(value);
  }
  await expect(page.getByText("自动应用")).toHaveCount(0);
  await expect(page.getByText("自动发布")).toHaveCount(0);
  await expect(page.getByText("已帮你修改并发布")).toHaveCount(0);
});
