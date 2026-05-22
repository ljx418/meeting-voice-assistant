import { expect, test } from "@playwright/test";

test("operation evidence appears after user-confirmed action and remains redacted", async ({ page }) => {
  const browserRequests: Array<{ path: string; method: string }> = [];
  page.on("request", (request) => {
    const url = new URL(request.url());
    browserRequests.push({ path: url.pathname, method: request.method() });
  });
  page.on("dialog", (dialog) => dialog.accept());

  await page.goto("/");
  await expect(page.getByTestId("workflow-console")).toBeVisible();
  await page.getByTestId("agent-message-input").fill("帮我优化当前节点");
  await page.getByTestId("agent-send-button").click();
  await expect(page.getByTestId("agent-action-proposal-card").first()).toBeVisible();

  await page.getByRole("button", { name: "Patch", exact: true }).click();
  await expect(page.getByTestId("editing-panel").first()).toBeVisible();
  await expect(page.getByTestId("patch-apply-button").first()).toBeEnabled();
  await page.getByTestId("patch-apply-button").first().click();

  await page.getByText("治理审计").first().click();
  await expect(page.getByTestId("governance-review-panel")).toBeVisible();
  const patchEvidence = page.getByTestId("operation-evidence-card").filter({ hasText: "workflow.patch.apply" }).first();
  await expect(patchEvidence).toBeVisible();
  await expect(patchEvidence).toContainText("已确认");

  const body = await page.locator("body").textContent();
  const html = await page.content();
  for (const forbidden of [
    "capability_token",
    "subscription_token",
    "Authorization",
    "Bearer",
    "raw_trace_payload",
    "raw_artifact_content",
    "raw_connector_payload",
    "secret-token-value",
    "自动应用",
    "自动发布",
  ]) {
    expect(body || "").not.toContain(forbidden);
    expect(html).not.toContain(forbidden);
  }
  expect(browserRequests.some((request) => request.path.includes("/v1/rpc"))).toBe(false);
  expect(browserRequests.some((request) => request.path.includes("/v1/events/subscribe"))).toBe(false);
});
