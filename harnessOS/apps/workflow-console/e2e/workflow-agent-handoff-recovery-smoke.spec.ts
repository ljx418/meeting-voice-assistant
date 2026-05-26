import { expect, test } from "@playwright/test";

test("Agent handoff recovery opens panel without mutation", async ({ page }) => {
  const browserRequests: Array<{ path: string; method: string }> = [];
  page.on("request", (request) => {
    const url = new URL(request.url());
    browserRequests.push({ path: url.pathname, method: request.method() });
  });

  await page.goto("/");
  await expect(page.getByTestId("workflow-console")).toBeVisible();
  await page.getByTestId("agent-message-input").fill("帮我优化当前节点");
  await page.getByTestId("agent-send-button").click();
  await expect(page.getByTestId("agent-action-proposal-card").first()).toBeVisible();
  const handoff = await page.evaluate(async () => {
    const instanceId = (document.querySelector("[data-testid='workflow-instance-selector']") as HTMLSelectElement | null)?.value;
    const proposals = await fetch(`/bff/instances/${instanceId}/agent/action-proposals`).then((response) => response.json());
    const proposal = proposals.find((item: { target_panel?: string; workflow_patch_id?: string }) => item.target_panel === "editing" && item.workflow_patch_id);
    return fetch(`/bff/instances/${instanceId}/agent/action-proposals/${proposal.proposal_id}/handoff`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ target_panel: "editing_panel", workflow_patch_id: proposal.workflow_patch_id }),
    }).then((response) => response.json());
  });
  expect(handoff.handoff_id).toBeTruthy();

  await page.goto(`/?handoff_id=${handoff.handoff_id}`);
  await expect(page.getByTestId("editing-panel").first()).toBeVisible();
  await expect(page.getByTestId("agent-handoff-banner").first()).toContainText("来自 Agent 建议");

  expect(browserRequests.some((request) => request.path.endsWith("/apply"))).toBe(false);
  expect(browserRequests.some((request) => request.path.includes("/approvals/") && request.path.includes("/respond"))).toBe(false);
  expect(browserRequests.some((request) => request.path.includes("/context/update"))).toBe(false);
  expect(browserRequests.some((request) => request.path.includes("/v1/rpc"))).toBe(false);
  expect(browserRequests.some((request) => request.path.includes("/v1/events/subscribe"))).toBe(false);
});
