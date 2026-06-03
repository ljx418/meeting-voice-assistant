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
  "raw prompt",
  "upstream signed URL",
];

test("visible user journey deploys, runs, and adjusts a workflow through Agent proposal", async ({ page }) => {
  const browserRequests: Array<{ path: string; method: string; body?: string }> = [];
  const bffResponses: string[] = [];
  const bffResponseReads: Array<Promise<void>> = [];
  page.on("request", (request) => {
    const url = new URL(request.url());
    browserRequests.push({ path: url.pathname, method: request.method(), body: request.postData() || undefined });
  });
  page.on("response", (response) => {
    const readResponse = (async () => {
      const url = new URL(response.url());
      if (!url.pathname.startsWith("/bff/")) {
        return;
      }
      const contentType = response.headers()["content-type"] || "";
      if (!contentType.includes("application/json")) {
        return;
      }
      try {
        bffResponses.push(await response.text());
      } catch {
        // Ignore responses that finish after Playwright starts test teardown.
      }
    })();
    bffResponseReads.push(readResponse);
  });
  page.on("dialog", async (dialog) => {
    await dialog.accept();
  });

  const deployed = await (await page.request.post("http://127.0.0.1:18040/__test/simple-workflow/deploy")).json();
  expect(deployed.status).toBe("ok");
  expect(deployed.workflow_template_id).toBeTruthy();
  expect(deployed.workflow_version_id).toBeTruthy();
  expect(deployed.workflow_instance_id).toBeTruthy();
  expect(deployed.completed_run_count).toBeGreaterThanOrEqual(1);
  expect(deployed.output_artifact_count).toBeGreaterThanOrEqual(1);

  await page.goto("/");
  await page.waitForTimeout(350);
  await expect(page.getByTestId("workflow-console")).toBeVisible();
  await page.getByTestId("workflow-selector").selectOption(deployed.workflow_template_id);
  await expect(page.getByTestId("workflow-instance-selector")).toHaveValue(deployed.workflow_instance_id);
  await expect(page.getByTestId("workflow-status")).toContainText(deployed.runtime_status);
  await expect(page.getByTestId("station-board")).toBeVisible();
  await expect.poll(() => page.getByTestId("station-card").count()).toBeGreaterThanOrEqual(deployed.station_count);
  await page.getByRole("button", { name: "产物", exact: true }).click();
  await expect(page.getByTestId("artifact-panel")).not.toHaveText("");

  await page.getByRole("button", { name: "Agent 助手", exact: true }).click();
  await expect(page.getByTestId("agent-talk-panel")).toBeVisible();
  await page.getByTestId("agent-message-input").fill("给这个工作流增加一个质量检查节点");
  const agentMessageResponse = page.waitForResponse((response) => {
    const url = new URL(response.url());
    return url.pathname.endsWith(`/instances/${deployed.workflow_instance_id}/agent/messages`) && response.request().method() === "POST";
  });
  await page.getByTestId("agent-send-button").click();
  const agentMessage = await agentMessageResponse;
  expect(agentMessage.ok(), await agentMessage.text()).toBeTruthy();
  await expect(page.getByTestId("agent-message-list")).toContainText("新增质量检查节点的 Patch proposal");
  await expect(page.getByTestId("agent-action-proposal-card").filter({ hasText: "生成节点调整建议" })).toBeVisible();
  await expect(page.getByTestId("station-board").getByText("质量检查节点")).toHaveCount(0);

  expect(browserRequests.some((request) => request.path.endsWith("/apply"))).toBe(false);
  const beforeApplyStationCount = await page.getByTestId("station-card").count();

  await page.getByTestId("agent-action-proposal-card").filter({ hasText: "生成节点调整建议" }).getByRole("button", { name: "前往编辑面板" }).click();
  await expect(page.getByTestId("editing-panel")).toBeVisible();
  await expect(page.getByTestId("patch-status")).toHaveText("proposed");
  await expect(page.getByTestId("editing-panel")).toContainText("add_station");
  await expect(page.getByTestId("editing-panel")).toContainText("质量检查节点");
  expect(await page.getByTestId("station-card").count()).toBe(beforeApplyStationCount);

  const applyResponse = page.waitForResponse((response) => {
    const url = new URL(response.url());
    return url.pathname.includes("/patches/") && url.pathname.endsWith("/apply") && response.request().method() === "POST";
  });
  await page.getByTestId("patch-apply-button").click();
  expect((await applyResponse).ok()).toBeTruthy();
  await expect(page.getByTestId("workflow-console")).toBeVisible({ timeout: 7000 });
  await expect(page.getByTestId("station-board").getByText("质量检查节点")).toBeVisible({ timeout: 7000 });
  await expect.poll(() => page.getByTestId("station-card").count()).toBeGreaterThan(beforeApplyStationCount);

  const postBodies = browserRequests.filter((request) => request.method === "POST").map((request) => request.body || "").join("\n");
  expect(postBodies).toContain('"user_confirmed":true');
  expect(postBodies).toContain('"source":"editing_panel"');
  expect(postBodies).toContain('"handoff_id"');
  expect(browserRequests.some((request) => request.path.includes("/v1/rpc"))).toBe(false);
  expect(browserRequests.some((request) => request.path.includes("/v1/events/subscribe"))).toBe(false);

  const bodyText = (await page.locator("body").textContent()) || "";
  const html = await page.content();
  await Promise.allSettled(bffResponseReads);
  for (const value of SENSITIVE_TEXT) {
    expect(bodyText).not.toContain(value);
    expect(html).not.toContain(value);
    expect(bffResponses.join("\n")).not.toContain(value);
  }
  for (const copy of ["自动应用", "自动发布", "Agent 已执行", "Agent 已发布", "已帮你修改并发布"]) {
    await expect(page.getByText(copy)).toHaveCount(0);
  }
});
