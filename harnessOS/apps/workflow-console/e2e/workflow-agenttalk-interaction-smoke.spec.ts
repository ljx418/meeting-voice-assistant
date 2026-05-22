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

test("AgentTalk interaction baseline keeps proposals user-confirmed", async ({ page }) => {
  const browserRequests: Array<{ path: string; method: string }> = [];
  page.on("request", (request) => {
    const url = new URL(request.url());
    browserRequests.push({ path: url.pathname, method: request.method() });
  });

  await page.goto("/");
  await expect(page.getByTestId("workflow-console")).toBeVisible();
  await expect(page.getByTestId("agent-talk-panel")).toBeVisible();
  await expect(page.getByTestId("agent-interaction-refresh-generation")).toBeVisible();

  await page.getByTestId("agent-message-input").fill("解释当前流程并总结最近事件");
  await page.getByTestId("agent-send-button").click();
  await expect(page.getByTestId("agent-action-proposal-card").first()).toBeVisible();

  expect(browserRequests.some((request) => request.path.endsWith("/apply"))).toBe(false);
  await page.getByRole("button", { name: "前往编辑面板", exact: true }).first().click();
  await expect(page.getByTestId("editing-panel").first()).toBeVisible();
  expect(browserRequests.some((request) => request.path.endsWith("/apply"))).toBe(false);

  await page.getByRole("button", { name: "Agent 助手", exact: true }).click();
  await page.getByRole("button", { name: "查看治理审计", exact: true }).first().click();
  await expect(page.getByTestId("governance-review-panel")).toBeVisible();
  await expect(page.getByText("只读证据链")).toBeVisible();

  expect(browserRequests.some((request) => request.path.includes("/v1/rpc"))).toBe(false);
  expect(browserRequests.some((request) => request.path.includes("/v1/events/subscribe"))).toBe(false);
  const bodyText = (await page.locator("body").textContent()) || "";
  const html = await page.content();
  for (const value of SENSITIVE_TEXT) {
    expect(bodyText).not.toContain(value);
    expect(html).not.toContain(value);
  }
  for (const copy of ["自动应用", "自动发布", "已帮你修改并发布", "Agent 已执行", "Agent 已发布"]) {
    await expect(page.getByText(copy)).toHaveCount(0);
  }
});
