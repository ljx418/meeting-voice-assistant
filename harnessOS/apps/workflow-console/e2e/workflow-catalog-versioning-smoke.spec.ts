import { expect, test } from "@playwright/test";

test("node catalog is loaded through BFF and no direct runtime route is used", async ({ page }) => {
  const requests: string[] = [];
  page.on("request", (request) => requests.push(new URL(request.url()).pathname));

  await page.goto("/");
  await expect(page.getByTestId("workflow-console")).toBeVisible();
  await expect(page.locator("button.library-node").filter({ hasText: "角色一致性检查" }).first()).toBeVisible();

  expect(requests.some((path) => path.includes("/bff/workflows/") && path.endsWith("/node-catalog"))).toBeTruthy();
  expect(requests).not.toContain("/v1/rpc");
  expect(requests).not.toContain("/v1/events/subscribe");
  const html = await page.content();
  for (const forbidden of ["capability_token", "subscription_token", "Authorization", "raw_connector_payload"]) {
    expect(html).not.toContain(forbidden);
  }
});
