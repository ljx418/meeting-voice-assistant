import { expect, test } from "@playwright/test";

test("visible frontend controls provide local feedback or navigation", async ({ page }) => {
  await page.goto("/", { waitUntil: "domcontentloaded" });
  await expect(page.getByTestId("workflow-console")).toBeVisible();

  await page.getByLabel("搜索节点").fill("Planner");
  await expect(page.locator(".library-node")).toHaveCount(1);
  await expect(page.locator(".library-node")).toContainText("Planner Agent");

  await page.getByLabel("搜索节点").fill("no-such-node-template");
  await expect(page.getByText("没有匹配节点")).toBeVisible();
  await page.getByLabel("搜索节点").fill("");

  await page.getByRole("button", { name: "+ 自定义节点" }).click();
  await expect(page.getByText("自定义节点编辑器属于后续能力")).toBeVisible();

  await page.locator(".quick-prompts button", { hasText: "解释当前流程" }).click();
  await expect(page.getByTestId("agent-message-input")).toHaveValue("解释当前流程");

  await page.getByRole("button", { name: "查看详情" }).first().click();
  await expect(page.getByTestId("agent-action-proposal-detail")).toBeVisible();
  await expect(page.getByTestId("agent-action-proposal-detail")).toContainText("详情仅用于导航和审查");

  await page.locator(".quick-prompts button", { hasText: "查看 Diff" }).click();
  await expect(page.getByTestId("editing-panel")).toBeVisible();

  await expect(page.getByTestId("v41-scenario-stepper")).toContainText("Desktop/技术分享 递归总结");
  await expect(page.getByTestId("v41-next-action")).toBeVisible();
  await page.getByTestId("canvas-minimap-toggle").click();
  await expect(page.locator(".react-flow__minimap")).toBeVisible();
});
