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

test("Agent handoff routes proposals to user-confirmed operation panels", async ({ page }) => {
  const browserRequests: Array<{ path: string; method: string; body?: string }> = [];
  page.on("request", (request) => {
    const url = new URL(request.url());
    browserRequests.push({ path: url.pathname, method: request.method(), body: request.postData() || undefined });
  });
  page.on("dialog", async (dialog) => {
    await dialog.accept();
  });

  await page.goto("/");
  await expect(page.getByTestId("workflow-console")).toBeVisible();
  await expect(page.getByTestId("agent-talk-panel")).toBeVisible();

  await page.getByTestId("agent-message-input").fill("帮我优化当前节点");
  await page.getByTestId("agent-send-button").click();
  await expect(page.getByTestId("agent-action-proposal-card").first()).toBeVisible();

  const approvalHandoffResponse = page.waitForResponse((response) => response.url().includes("/agent/action-proposals/") && response.url().endsWith("/handoff"));
  await page.getByRole("button", { name: "前往审批面板", exact: true }).click();
  const approvalHandoff = await approvalHandoffResponse;
  expect(approvalHandoff.ok(), await approvalHandoff.text()).toBeTruthy();
  await expect(page.getByTestId("approval-panel")).toBeVisible();
  await expect(page.getByTestId("agent-handoff-banner")).toContainText("来自 Agent 建议");
  expect(browserRequests.some((request) => request.path.includes("/approvals/") && request.path.includes("/respond"))).toBe(false);
  const approvalResponse = page.waitForResponse((response) => response.url().includes("/approvals/") && response.url().includes("/respond"));
  await page.getByTestId("approval-approve-button").first().click();
  expect((await approvalResponse).ok()).toBeTruthy();

  await page.getByRole("button", { name: "Agent 助手", exact: true }).click();
  const contextHandoffResponse = page.waitForResponse((response) => response.url().includes("/agent/action-proposals/") && response.url().endsWith("/handoff"));
  await page.getByRole("button", { name: "前往上下文面板", exact: true }).click();
  expect((await contextHandoffResponse).ok()).toBeTruthy();
  await expect(page.getByTestId("context-panel")).toBeVisible();
  expect(browserRequests.some((request) => request.path.includes("/context/update"))).toBe(false);
  const contextResponse = page.waitForResponse((response) => response.url().includes("/context/update"));
  await page.getByTestId("context-update-button").dispatchEvent("click");
  expect((await contextResponse).ok()).toBeTruthy();

  await page.getByRole("button", { name: "Agent 助手", exact: true }).click();
  const editingHandoffResponse = page.waitForResponse((response) => response.url().includes("/agent/action-proposals/") && response.url().endsWith("/handoff"));
  await page
    .getByTestId("agent-action-proposal-card")
    .filter({ hasText: "查看 Diff" })
    .getByRole("button", { name: "前往编辑面板", exact: true })
    .click();
  const editingHandoff = await editingHandoffResponse;
  expect(editingHandoff.ok(), await editingHandoff.text()).toBeTruthy();
  await expect(page.getByTestId("editing-panel").first()).toBeVisible();
  expect(browserRequests.some((request) => request.path.endsWith("/apply"))).toBe(false);
  const applyResponse = page.waitForResponse((response) => response.url().includes("/patches/") && response.url().endsWith("/apply"));
  await page.getByTestId("patch-apply-button").first().click();
  const applyResult = await applyResponse;
  expect(applyResult.ok(), await applyResult.text()).toBeTruthy();

  const postBodies = browserRequests.filter((request) => request.method === "POST").map((request) => request.body || "").join("\n");
  expect(postBodies).toContain('"user_confirmed":true');
  expect(postBodies).toContain('"source":"approval_panel"');
  expect(postBodies).toContain('"source":"context_panel"');
  expect(postBodies).toContain('"source":"editing_panel"');
  expect(postBodies).toContain('"proposal_id"');
  expect(postBodies).toContain('"handoff_id"');

  expect(browserRequests.some((request) => request.path.includes("/v1/rpc"))).toBe(false);
  expect(browserRequests.some((request) => request.path.includes("/v1/events/subscribe"))).toBe(false);
  const bodyText = (await page.locator("body").textContent()) || "";
  const html = await page.content();
  for (const value of SENSITIVE_TEXT) {
    expect(bodyText).not.toContain(value);
    expect(html).not.toContain(value);
  }
});
