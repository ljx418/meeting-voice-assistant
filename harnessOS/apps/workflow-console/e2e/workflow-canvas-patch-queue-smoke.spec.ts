import { expect, test } from "@playwright/test";

test("patch queue refreshes from BFF truth and blocks stale event truth", async ({ page }) => {
  const requests: string[] = [];
  page.on("request", (request) => requests.push(new URL(request.url()).pathname));
  page.on("dialog", (dialog) => dialog.accept());

  await page.goto("/");
  await expect(page.getByTestId("workflow-console")).toBeVisible();
  await page.locator("button.library-node").filter({ hasText: "角色一致性检查" }).first().click();
  await page.getByRole("button", { name: "Patch", exact: true }).click();
  await expect(page.getByTestId("editing-panel").first()).toBeVisible();
  await expect(page.getByTestId("patch-status").first()).toHaveText(/proposed|blocked|stale/);

  expect(requests.some((path) => path.includes("/bff/workflows/") && path.endsWith("/patches"))).toBeTruthy();
  expect(requests).not.toContain("/v1/rpc");
  expect(requests).not.toContain("/v1/events/subscribe");
});
