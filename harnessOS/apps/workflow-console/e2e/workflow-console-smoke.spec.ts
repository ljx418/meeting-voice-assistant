import { expect, test, type Page } from "@playwright/test";

const bffBaseURL = `http://127.0.0.1:${process.env.WORKFLOW_CONSOLE_BFF_PORT || "18040"}`;
const forbiddenText = [
  "capability_token",
  "subscription_token",
  "Authorization",
  "Bearer",
  "raw_trace_payload",
  "raw_artifact_content",
  "raw_connector_payload",
  "secret-token-value",
];

test("workflow console browser smoke uses real BFF data and no false-green paths", async ({ page, request }) => {
  const browserRequestPaths: string[] = [];
  page.on("request", (browserRequest) => {
    const url = new URL(browserRequest.url());
    browserRequestPaths.push(url.pathname);
  });

  await page.goto("/");
  await expect(page.getByTestId("workflow-console")).toBeVisible();
  await expect(page.getByTestId("workflow-instance-selector")).toBeVisible();
  await expect(page.getByText("Demo / Fixture")).toHaveCount(0);
  await expect(page.getByTestId("station-board")).toBeVisible();
  expect(await page.getByTestId("station-card").count()).toBeGreaterThanOrEqual(3);

  await page.getByRole("button", { name: "审批", exact: true }).click();
  await expect(page.getByTestId("approval-panel")).toBeVisible();
  if (await page.getByTestId("approval-approve-button").first().isEnabled()) {
    const approvalResponsePromise = page.waitForResponse((response) => response.url().includes("/approvals/") && response.url().includes("/respond"));
    await page.getByTestId("approval-approve-button").first().click();
    const approvalResponse = await approvalResponsePromise;
    const approvalResponseText = await approvalResponse.text();
    expect(approvalResponse.ok(), approvalResponseText).toBe(true);
  }
  await expect(page.getByTestId("workflow-status")).toContainText("completed");

  await page.getByRole("button", { name: "产物", exact: true }).click();
  await expect(page.getByTestId("artifact-panel")).toContainText(/\.json|artifact|产物|storyboard|output/i);

  await page.getByRole("button", { name: "质量", exact: true }).click();
  await expect(page.getByTestId("quality-panel")).toContainText("Quality");

  await page.getByRole("button", { name: "Trace", exact: true }).click();
  await expect(page.getByTestId("trace-panel")).not.toBeEmpty();

  await page.getByRole("button", { name: "上下文", exact: true }).click();
  await expect(page.getByTestId("context-panel")).toBeVisible();
  await page.getByTestId("context-update-button").click();
  await expect(page.getByTestId("workflow-console")).toBeVisible();
  await page.getByRole("button", { name: "上下文", exact: true }).click();
  await expect(page.getByTestId("context-panel")).toContainText("用户确认的业务备注");

  const fixture = (await (await request.get(`${bffBaseURL}/__test/health`)).json()) as { workflow_instance_id: string };
  await request.post(`${bffBaseURL}/__test/emit-fake-status-event`, {
    data: { workflow_instance_id: fixture.workflow_instance_id, status: "forged_failed" },
  });
  await page.getByRole("button", { name: "事件", exact: true }).click();
  await expect(page.getByTestId("event-feed")).toContainText("workflow.context.updated");
  await expect(page.getByTestId("workflow-status")).not.toContainText("forged_failed");

  for (const forbiddenPath of ["/v1" + "/rpc", "/v1" + "/events/subscribe"]) {
    expect(browserRequestPaths, `browser must not call ${forbiddenPath}`).not.toContain(forbiddenPath);
  }
  await expectNoForbiddenText(page);
  await expectForbiddenActionsAbsent(page);
});

async function expectNoForbiddenText(page: Page) {
  const bodyText = await page.locator("body").textContent();
  const html = await page.content();
  for (const forbidden of forbiddenText) {
    expect(bodyText || "", `DOM text leaked ${forbidden}`).not.toContain(forbidden);
    expect(html, `HTML leaked ${forbidden}`).not.toContain(forbidden);
  }
}

async function expectForbiddenActionsAbsent(page: Page) {
  for (const forbidden of [
    "workflow.template.publish",
    "自动" + "应用",
    "自动" + "发布",
    "已帮你修改并" + "发布",
    "Apply Patch",
    "Publish Version",
  ]) {
    await expect(page.getByText(forbidden, { exact: false })).toHaveCount(0);
  }
}
