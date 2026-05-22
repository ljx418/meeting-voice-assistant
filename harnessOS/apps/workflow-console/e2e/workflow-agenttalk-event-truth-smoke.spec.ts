import { expect, test } from "@playwright/test";

const bffBaseURL = `http://127.0.0.1:${process.env.WORKFLOW_CONSOLE_BFF_PORT || "18040"}`;

test("fake Agent event payload does not become UI truth", async ({ page, request }) => {
  const browserRequests: Array<{ path: string; method: string }> = [];
  page.on("request", (browserRequest) => {
    const url = new URL(browserRequest.url());
    browserRequests.push({ path: url.pathname, method: browserRequest.method() });
  });

  const health = await request.get(`${bffBaseURL}/__test/health`);
  const fixture = await health.json();
  await page.goto("/");
  await expect(page.getByTestId("workflow-console")).toBeVisible();

  await request.post(`${bffBaseURL}/__test/emit-fake-agent-event`, {
    data: {
      workflow_instance_id: fixture.workflow_instance_id,
      type: "agent.action_proposal.created",
    },
  });
  await page.reload();
  await expect(page.getByTestId("agent-talk-panel")).toBeVisible();

  const html = await page.content();
  expect(html).not.toContain("fake_proposal_from_event");
  expect(html).not.toContain("fake_patch_from_event");
  expect(html).not.toContain("fake_evidence_from_event");
  expect(html).not.toContain("raw_trace_payload");
  expect(browserRequests.some((item) => item.path.includes("/agent/interaction-state"))).toBe(true);
  expect(browserRequests.some((item) => item.path.includes("/agent/action-proposals"))).toBe(true);
  expect(browserRequests.some((item) => item.path.includes("/agent/operation-evidence"))).toBe(true);
  expect(browserRequests.some((item) => item.path.includes("/v1/rpc"))).toBe(false);
  expect(browserRequests.some((item) => item.path.includes("/v1/events/subscribe"))).toBe(false);
});
