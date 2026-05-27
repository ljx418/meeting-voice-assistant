import { expect, test } from "@playwright/test";

const STATES = [
  ["overview", "workflow-studio-overview.png"],
  ["agent-draft-proposal", "agent-draft-proposal.png"],
  ["folder-debug-scan", "folder-debug-scan.png"],
  ["running-board", "running-board.png"],
  ["artifacts-quality", "artifacts-quality.png"],
  ["governance-evidence", "governance-evidence.png"],
] as const;

test.describe("Workflow Studio visual acceptance", () => {
  for (const [state, filename] of STATES) {
    test(`${state} screenshot`, async ({ page }) => {
      const requests: string[] = [];
      page.on("request", (request) => requests.push(request.url()));

      await page.setViewportSize({ width: 1440, height: 960 });
      await page.goto(`/?studio=${state}`);
      await expect(page.getByTestId("workflow-studio-layout")).toBeVisible();
      await page.screenshot({ path: `docs/visual-acceptance/${filename}`, fullPage: true });

      const bodyText = await page.locator("body").innerText();
      for (const forbidden of [
        "/v1/rpc",
        "/v1/events/subscribe",
        "capability_token",
        "subscription_token",
        "Authorization",
        "Bearer",
        "secret",
        "raw_trace_payload",
        "raw_artifact_content",
        "raw_connector_payload",
        "raw prompt",
        "upstream signed URL",
        "自动应用",
        "自动发布",
        "Agent 已执行",
        "Agent 已发布",
        "complete Workflow Studio ready",
        "Agent executor ready",
        "controlled executor ready",
      ]) {
        expect(bodyText).not.toContain(forbidden);
      }
      expect(requests.some((url) => url.includes("/v1/rpc") || url.includes("/v1/events/subscribe"))).toBe(false);
    });
  }
});
