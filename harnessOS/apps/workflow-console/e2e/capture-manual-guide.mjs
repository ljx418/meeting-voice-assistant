import { chromium } from "playwright";
import { mkdir } from "node:fs/promises";
import path from "node:path";

const baseUrl = process.env.WORKFLOW_CONSOLE_URL || "http://127.0.0.1:4174";
const bffUrl = process.env.WORKFLOW_CONSOLE_BFF_URL || "http://127.0.0.1:18040";
const outputDir = path.resolve(process.cwd(), "../../docs/design/V4.0/manual-guide-screenshots");

async function screenshot(page, name) {
  await page.waitForTimeout(350);
  await page.screenshot({
    path: path.join(outputDir, name),
    fullPage: true,
  });
}

async function clickTab(page, name) {
  await page.getByRole("button", { name, exact: true }).click();
  await page.waitForTimeout(250);
}

const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ viewport: { width: 1440, height: 980 }, deviceScaleFactor: 1 });
page.on("dialog", async (dialog) => {
  await dialog.accept();
});

try {
  await mkdir(outputDir, { recursive: true });

  const deployedResponse = await page.request.post(`${bffUrl}/__test/simple-workflow/deploy`);
  if (!deployedResponse.ok()) {
    throw new Error(`Failed to seed workflow: ${deployedResponse.status()} ${await deployedResponse.text()}`);
  }
  const deployed = await deployedResponse.json();

  await page.goto(baseUrl);
  await page.getByTestId("workflow-console").waitFor({ state: "visible" });
  await screenshot(page, "01-open-workflow-console.png");

  await page.getByTestId("workflow-selector").selectOption(deployed.workflow_template_id);
  await page.getByTestId("workflow-instance-selector").waitFor({ state: "visible" });
  await page.waitForFunction(
    (instanceId) => {
      const selector = document.querySelector('[data-testid="workflow-instance-selector"]');
      return selector instanceof HTMLSelectElement && selector.value === instanceId;
    },
    deployed.workflow_instance_id,
  );
  await page.getByTestId("workflow-status").waitFor({ state: "visible" });
  await screenshot(page, "02-select-deployed-workflow.png");

  await page.getByTestId("station-board").waitFor({ state: "visible" });
  await screenshot(page, "03-review-station-board.png");

  await clickTab(page, "产物");
  await page.getByTestId("artifact-panel").waitFor({ state: "visible" });
  await screenshot(page, "04-review-runtime-artifacts.png");

  await clickTab(page, "Trace");
  await page.getByTestId("trace-panel").waitFor({ state: "visible" });
  await screenshot(page, "05-review-redacted-trace.png");

  await page.getByRole("button", { name: "Agent 助手", exact: true }).click();
  await page.getByTestId("agent-talk-panel").waitFor({ state: "visible" });
  await screenshot(page, "06-open-canvas-copilot.png");

  await page.getByTestId("agent-message-input").fill("给这个工作流增加一个质量检查节点");
  await screenshot(page, "07-type-agent-adjustment-request.png");

  await page.getByTestId("agent-send-button").click();
  await page.getByTestId("agent-action-proposal-card").filter({ hasText: "生成节点调整建议" }).waitFor({ state: "visible" });
  const nodeProposalCard = page.getByTestId("agent-action-proposal-card").filter({ hasText: "生成节点调整建议" }).last();
  await nodeProposalCard.scrollIntoViewIfNeeded();
  await screenshot(page, "08-agent-proposal-created.png");

  await nodeProposalCard.getByRole("button", { name: "前往编辑面板" }).click();
  await page.getByTestId("editing-panel").waitFor({ state: "visible" });
  await page.getByTestId("editing-panel").getByText("add_station").first().waitFor({ state: "visible" });
  await page.getByTestId("editing-panel").getByText("质量检查节点").first().waitFor({ state: "visible" });
  await screenshot(page, "09-review-patch-before-apply.png");

  await page.getByTestId("patch-apply-button").click();
  await page.getByTestId("station-board").getByText("质量检查节点").waitFor({ state: "visible" });
  await screenshot(page, "10-apply-patch-and-refresh-board.png");

  await page.getByTestId("station-card").first().getByRole("button", { name: "查看节点输出" }).click();
  await page.getByRole("button", { name: "节点配置", exact: true }).click();
  await page.getByTestId("inspector-prompt-input").fill("请增强当前节点的质量检查标准，关注角色一致性和输出完整性。");
  await screenshot(page, "11-inspector-local-dirty-state.png");

  await page.getByTestId("inspector-generate-patch-button").click();
  await page.getByTestId("editing-panel").waitFor({ state: "visible" });
  await screenshot(page, "12-inspector-generated-patch.png");

  await clickTab(page, "审批");
  await page.getByTestId("approval-panel").waitFor({ state: "visible" });
  await screenshot(page, "13-review-approval-panel.png");

  await clickTab(page, "上下文");
  await page.getByTestId("context-panel").waitFor({ state: "visible" });
  await screenshot(page, "14-review-context-panel.png");

  await clickTab(page, "治理审计");
  await page.getByTestId("governance-review-panel").waitFor({ state: "visible" });
  await screenshot(page, "15-review-governance-evidence.png");

  await page.getByRole("button", { name: "Agent 助手", exact: true }).click();
  await page.getByTestId("agent-talk-panel").waitFor({ state: "visible" });
  await page.getByTestId("agent-message-input").fill("解释当前流程并总结最近事件");
  await page.getByTestId("agent-send-button").click();
  await page.getByTestId("agent-message-list").waitFor({ state: "visible" });
  await screenshot(page, "16-agent-readonly-explain-summary.png");
} finally {
  await browser.close();
}
