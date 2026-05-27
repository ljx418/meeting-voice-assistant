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

test("governed patch apply and publish browser smoke", async ({ page }) => {
  const browserRequests: string[] = [];
  const bffResponses: string[] = [];
  const responseReads: Promise<void>[] = [];
  page.on("request", (request) => {
    const url = new URL(request.url());
    browserRequests.push(url.pathname);
  });
  page.on("response", (response) => {
    const url = new URL(response.url());
    if (!url.pathname.startsWith("/bff/")) {
      return;
    }
    const contentType = response.headers()["content-type"] || "";
    if (contentType.includes("application/json")) {
      responseReads.push(
        response
          .text()
          .then((text) => {
            bffResponses.push(text);
          })
          .catch(() => {
            // Some browser responses may be disposed by navigation; redaction checks use successfully captured payloads.
          }),
      );
    }
  });
  page.on("dialog", async (dialog) => {
    await dialog.accept();
  });

  const health = await (await page.request.get("http://127.0.0.1:18040/__test/health")).json();
  await page.goto("/");
  await expect(page.getByTestId("workflow-console")).toBeVisible();
  await expect(page.getByTestId("workflow-instance-selector")).toHaveValue(health.workflow_instance_id);
  await expect(page.getByTestId("station-board")).toBeVisible();

  await page.getByRole("button", { name: "Patch", exact: true }).click();
  await expect(page.getByTestId("editing-panel")).toBeVisible();
  const patchStatus = (await page.getByTestId("patch-status").textContent()) || "";
  if (patchStatus.trim() !== "applied") {
    await expect(page.getByTestId("patch-status")).toHaveText("proposed");
    await expect(page.getByTestId("patch-apply-button")).toBeEnabled();
    const applyResponse = page.waitForResponse((response) => {
      const url = new URL(response.url());
      return (
        url.pathname.startsWith(`/bff/workflows/${health.workflow_template_id}/patches/`) &&
        url.pathname.endsWith("/apply") &&
        response.request().method() === "POST"
      );
    });
    await page.getByTestId("patch-apply-button").click();
    expect((await applyResponse).ok()).toBeTruthy();
    await expect(page.getByTestId("workflow-console")).toBeVisible({ timeout: 7000 });
    await page.getByRole("button", { name: "Patch", exact: true }).click();
    await expect(page.getByTestId("patch-status")).toHaveText("applied", { timeout: 7000 });
  }

  const publishVersion = `2.0.${Date.now()}`;
  await page.getByTestId("publish-version-input").fill(publishVersion);
  const publishResponse = page.waitForResponse((response) =>
    response.url().includes(`/bff/workflows/${health.workflow_template_id}/publish`) &&
    response.request().method() === "POST",
  );
  await page.getByTestId("publish-version-button").click();
  expect((await publishResponse).ok()).toBeTruthy();
  await expect(page.getByTestId("workflow-console")).toBeVisible({ timeout: 7000 });
  await expect(page.getByTestId("workflow-version-selector")).toContainText(publishVersion, { timeout: 7000 });

  const fakeEventResponse = await page.request.post("http://127.0.0.1:18040/__test/emit-fake-status-event", {
    data: { workflow_instance_id: health.workflow_instance_id, status: "forged_patch_applied" },
  });
  expect(fakeEventResponse.ok()).toBeTruthy();
  await page.getByRole("button", { name: "事件", exact: true }).click();
  await expect(page.getByTestId("event-feed")).toContainText("workflow.context.updated", { timeout: 7000 });
  await expect(page.getByTestId("workflow-status")).not.toContainText("forged_patch_applied");

  expect(browserRequests).not.toContain("/v1/rpc");
  expect(browserRequests).not.toContain("/v1/events/subscribe");
  const bodyText = (await page.locator("body").textContent()) || "";
  const html = await page.content();
  await Promise.all(responseReads);
  for (const value of SENSITIVE_TEXT) {
    expect(bodyText).not.toContain(value);
    expect(html).not.toContain(value);
    expect(bffResponses.join("\n")).not.toContain(value);
  }
  await expect(page.getByText("自动应用")).toHaveCount(0);
  await expect(page.getByText("自动发布")).toHaveCount(0);
  await expect(page.getByText("已帮你修改并发布")).toHaveCount(0);
});
