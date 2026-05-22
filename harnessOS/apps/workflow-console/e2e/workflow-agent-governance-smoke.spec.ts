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

test("Agent action governance queue stays proposal-only in browser", async ({ page }) => {
  const browserRequests: Array<{ path: string; method: string }> = [];
  page.on("request", (request) => {
    const url = new URL(request.url());
    browserRequests.push({ path: url.pathname, method: request.method() });
  });

  await page.goto("/");
  await expect(page.getByTestId("workflow-console")).toBeVisible();
  await expect(page.getByTestId("agent-talk-panel")).toBeVisible();

  await page.getByTestId("agent-message-input").fill("帮我优化当前节点");
  const response = page.waitForResponse((item) => {
    const url = new URL(item.url());
    return url.pathname.endsWith("/agent/messages") && item.request().method() === "POST";
  });
  await page.getByTestId("agent-send-button").click();
  expect((await response).ok()).toBeTruthy();

  await expect(page.getByTestId("agent-action-proposal-card").first()).toBeVisible();
  await page.getByRole("button", { name: "查看详情", exact: true }).first().click();
  await page.getByRole("button", { name: "查看 Diff", exact: true }).first().click();
  await expect(page.getByTestId("editing-panel")).toBeVisible();

  const requestPaths = browserRequests.map((request) => `${request.method} ${request.path}`);
  expect(requestPaths.some((item) => item.includes("/v1/rpc"))).toBe(false);
  expect(requestPaths.some((item) => item.includes("/v1/events/subscribe"))).toBe(false);
  expect(requestPaths.some((item) => item.includes("/apply"))).toBe(false);
  expect(requestPaths.some((item) => item.includes("/publish"))).toBe(false);
  expect(requestPaths.some((item) => item.includes("/respond"))).toBe(false);
  expect(requestPaths.some((item) => item.includes("/context/update"))).toBe(false);
  expect(requestPaths.some((item) => item.includes("/business-events"))).toBe(false);
  for (const value of SENSITIVE_TEXT) {
    const bodyText = (await page.locator("body").textContent()) || "";
    const html = await page.content();
    expect(bodyText).not.toContain(value);
    expect(html).not.toContain(value);
  }
  for (const copy of ["自动应用", "自动发布", "已帮你修改并发布"]) {
    await expect(page.getByText(copy)).toHaveCount(0);
  }
});
