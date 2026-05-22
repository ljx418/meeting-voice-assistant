import { expect, test } from "@playwright/test";

test("inspector typing is local and generate patch posts exactly once", async ({ page }) => {
  const patchPosts: string[] = [];
  page.on("request", (request) => {
    const path = new URL(request.url()).pathname;
    if (request.method() === "POST" && path.includes("/bff/workflows/") && path.endsWith("/patches")) {
      patchPosts.push(request.postData() || "");
    }
  });

  await page.goto("/");
  await expect(page.getByTestId("workflow-console")).toBeVisible();
  await page.getByRole("button", { name: "节点配置", exact: true }).click();
  const before = patchPosts.length;
  await page.getByTestId("inspector-prompt-input").fill("增强角色一致性");
  expect(patchPosts.length).toBe(before);
  await page.getByTestId("inspector-generate-patch-button").click();
  await expect.poll(() => patchPosts.length).toBe(before + 1);
  for (const forbidden of ["viewport", "selectedNode", "panelCollapsed", "activeTab", "Authorization", "raw_trace_payload"]) {
    expect(patchPosts.at(-1) || "").not.toContain(forbidden);
  }
});
