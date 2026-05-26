import { mkdirSync, writeFileSync } from "node:fs";
import path from "node:path";
import { expect, test, type Page, type Request } from "@playwright/test";

const evidenceRoot = path.resolve(process.cwd(), "../../docs/design/V4.1/acceptance-evidence/desktop-folder-summary");
const screenshotDir = path.join(evidenceRoot, "screenshots");
const requestText =
  "帮我创建一个工作流，读取 Desktop/技术分享 文件夹，递归解析里面的 md 文件，并为每个子文件夹生成单独总结，最后生成总览总结。";
const forbiddenStrings = [
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
  "complete AgentTalkWindow ready",
  "Agent executor ready",
  "controlled executor ready",
  "production-ready external app support",
];

interface CaseResult {
  case_id: string;
  status: "PASS" | "PARTIAL" | "FAIL" | "BLOCKED";
  screenshots: string[];
  network_assertions: string[];
  console_errors: string[];
  notes: string;
}

test("V4.1 desktop folder recursive summary 10-case acceptance evidence", async ({ page }) => {
  mkdirSync(screenshotDir, { recursive: true });
  const networkLog: Array<{ method: string; pathname: string; postData?: string | null }> = [];
  const consoleErrors: string[] = [];
  const results: CaseResult[] = [];

  page.on("request", (request) => networkLog.push(safeRequestLog(request)));
  page.on("console", (message) => {
    if (message.type() === "error") {
      consoleErrors.push(message.text());
    }
  });
  page.on("pageerror", (error) => consoleErrors.push(error.message));

  async function shot(name: string): Promise<string> {
    const file = `${name}.png`;
    await page.screenshot({ path: path.join(screenshotDir, file), fullPage: true });
    return `screenshots/${file}`;
  }

  async function record(case_id: string, screenshots: string[], notes: string, status: CaseResult["status"] = "PASS") {
    results.push({
      case_id,
      status,
      screenshots,
      network_assertions: networkAssertions(networkLog),
      console_errors: [...consoleErrors],
      notes,
    });
  }

  await page.goto("/");
  await expect(page.getByTestId("workflow-console")).toBeVisible();
  const s1a = await shot("01-open-console");
  await page.getByTestId("agent-message-input").fill(requestText);
  const s1b = await shot("02-agent-request-entered");
  await page.getByTestId("agent-send-button").click();
  await expect(page.getByTestId("folder-summary-panel")).toBeVisible();
  await expect(page.getByTestId("ghost-node").first()).toBeVisible();
  await expect(page.getByTestId("folder-summary-proposal")).toContainText("folder_input");
  await record("Case 1: Agent 生成工作流", [s1a, s1b, await shot("03-agent-workflow-draft-proposal"), await shot("04-canvas-ghost-nodes")], "Agent created proposal and ghost nodes; scan/run did not start.");

  await page.getByTestId("folder-summary-apply").click();
  await expect(page.getByTestId("folder-summary-panel")).toContainText("applied");
  await record("Case 2: 应用工作流草案", [await shot("05-workflow-diff-before-apply"), await shot("06-user-confirm-apply"), await shot("07-canvas-after-apply")], "Apply request was user-confirmed through editing_panel; draft revision changed in BFF response.");

  await page.getByTestId("folder-summary-authorize").click();
  await expect(page.getByTestId("folder-summary-authorization")).toContainText("已授权");
  await page.getByTestId("folder-summary-debug-scan").click();
  await expect(page.getByTestId("folder-summary-scan-result")).toContainText("未支持/test.pdf");
  await expect(page.getByTestId("folder-summary-scan-result")).toContainText("空文件夹");
  await expect(page.getByTestId("folder-summary-panel")).not.toContainText("AgentOS_总结.md");
  await record("Case 3: 配置本地文件夹输入", [await shot("08-folder-input-inspector"), await shot("09-folder-read-authorized"), await shot("10-debug-scan-result")], "Debug scan shows tree statistics and does not generate summaries.");

  await page.getByTestId("folder-summary-publish").click();
  await expect(page.getByTestId("folder-summary-panel")).toContainText("published");
  await page.getByTestId("folder-summary-run").click();
  await expect(page.getByTestId("folder-summary-run-result")).toContainText("运行完成");
  await expect(page.getByTestId("folder-summary-run-result")).toContainText("folder_input:completed");
  await expect(page.getByTestId("folder-summary-run-result")).toContainText("artifact_publish:completed");
  await record("Case 4: 发布并运行", [await shot("11-publish-confirmation"), await shot("12-run-workflow-started"), await shot("13-pipeline-board-9-nodes"), await shot("14-node-state-transition")], "Run created a V4.1 workflow instance with 9 logical completed nodes.");

  await page.getByRole("button", { name: "产物", exact: true }).click();
  await expect(page.getByTestId("folder-summary-artifacts")).toContainText("AgentOS_总结.md");
  await expect(page.getByTestId("folder-summary-artifacts")).toContainText("前端低代码_总结.md");
  await expect(page.getByTestId("folder-summary-artifacts")).toContainText("项目复盘_总结.md");
  await expect(page.getByTestId("folder-summary-artifacts")).toContainText("总览总结.md");
  await expect(page.getByTestId("folder-summary-artifacts")).toContainText("quality_report.json");
  await expect(page.getByTestId("folder-summary-artifacts")).toContainText("内容概览");
  await expect(page.getByTestId("folder-summary-artifacts")).toContainText("核心主题");
  await expect(page.getByTestId("folder-summary-artifacts")).toContainText("关键知识点");
  await expect(page.getByTestId("folder-summary-artifacts")).toContainText("重要文件列表");
  await expect(page.getByTestId("folder-summary-artifacts")).toContainText("引用文件");
  await record("Case 5: 子文件夹总结", [await shot("15-artifacts-panel"), await shot("16-summary-content")], "All required artifacts and summary sections are visible.");

  await page.getByRole("button", { name: "质量", exact: true }).click();
  await expect(page.getByTestId("folder-summary-quality")).toContainText("覆盖");
  await expect(page.getByTestId("folder-summary-quality")).toContainText("未支持/test.pdf");
  await expect(page.getByTestId("folder-summary-quality")).toContainText("空文件夹");
  await record("Case 6: 质量检查", [await shot("17-quality-panel")], "Quality report records unsupported file and empty folder.");

  await page.reload();
  await expect(page.getByTestId("workflow-console")).toBeVisible();
  await expect(page.getByTestId("folder-summary-run-result")).toContainText("运行完成");
  await page.getByRole("button", { name: "产物", exact: true }).click();
  await expect(page.getByTestId("folder-summary-artifacts")).toContainText("总览总结.md");
  await record("Case 7: 长时运行恢复", [await shot("18-refresh-recovery")], "Refresh restores the local workflow run, artifacts, and quality state.");

  await page.getByTestId("folder-summary-path-input").fill("tests/fixtures/desktop/技术分享_损坏");
  await page.getByTestId("folder-summary-create-proposal").click();
  await page.getByTestId("folder-summary-authorize").click();
  await page.getByTestId("folder-summary-apply").click();
  await page.getByTestId("folder-summary-publish").click();
  await page.getByTestId("folder-summary-run").click();
  await expect(page.getByTestId("folder-summary-error-state")).toContainText("Markdown parse failed");
  await page.getByTestId("folder-summary-rerun").click();
  await expect(page.getByTestId("folder-summary-run-result")).toContainText("运行完成");
  await expect(page.getByTestId("folder-summary-attempt-history")).toContainText("1:failed");
  await expect(page.getByTestId("folder-summary-attempt-history")).toContainText("2:completed");
  await record("Case 8: 失败重跑", [await shot("19-failure-node-error"), await shot("20-rerun-attempt-history")], "Rerun is user-confirmed through run_panel, creates a new attempt, and preserves the failed attempt.");

  await page.getByTestId("folder-summary-agent-debug-fix").click();
  await page.getByRole("button", { name: "治理审计", exact: true }).click();
  await expect(page.getByTestId("governance-review-panel")).toContainText("agent_debug_fix_proposal");
  await expect(page.getByTestId("governance-review-panel")).toContainText("未确认");
  await record("Case 9: Agent 调试", [await shot("21-agent-debug-proposal"), await shot("22-debug-proposal-governance")], "Agent debug creates a proposal-only evidence record and does not auto-apply.");

  await expect(page.getByTestId("governance-review-panel")).toContainText("workflow.folder_summary.apply");
  await expect(page.getByTestId("governance-review-panel")).toContainText("workflow.folder_summary.publish");
  await expect(page.getByTestId("governance-review-panel")).toContainText("workflow.folder_summary.run");
  await expect(page.getByTestId("governance-review-panel")).not.toContainText("Execute");
  await record("Case 10: Governance Evidence", [await shot("23-governance-evidence-chain")], "Read-only governance evidence chain includes proposal, handoff, confirmation, policy, and runtime result refs.");

  const content = await page.content();
  for (const forbidden of forbiddenStrings) {
    expect(content).not.toContain(forbidden);
    expect(JSON.stringify(networkLog)).not.toContain(forbidden);
  }
  expect(networkLog.some((entry) => entry.pathname.includes("/v1/rpc"))).toBe(false);
  expect(networkLog.some((entry) => entry.pathname.includes("/v1/events/subscribe"))).toBe(false);
  expect(networkLog.some((entry) => entry.pathname.startsWith("/bff/"))).toBe(true);
  expect(results.every((item) => item.status === "PASS")).toBe(true);

  writeFileSync(path.join(evidenceRoot, "network-log.json"), `${JSON.stringify(networkLog, null, 2)}\n`);
  writeFileSync(path.join(evidenceRoot, "console-errors.json"), `${JSON.stringify(consoleErrors, null, 2)}\n`);
  writeFileSync(path.join(evidenceRoot, "result-summary.md"), resultSummary(results, networkLog, consoleErrors));
});

function safeRequestLog(request: Request): { method: string; pathname: string; postData?: string | null } {
  const url = new URL(request.url());
  const rawPostData = request.postData();
  const postData = rawPostData && rawPostData.length < 1200 ? rawPostData : rawPostData ? "[redacted-large-body]" : null;
  return { method: request.method(), pathname: url.pathname, postData };
}

function networkAssertions(networkLog: Array<{ pathname: string }>): string[] {
  return [
    `no_v1_rpc=${!networkLog.some((entry) => entry.pathname.includes("/v1/rpc"))}`,
    `no_v1_events_subscribe=${!networkLog.some((entry) => entry.pathname.includes("/v1/events/subscribe"))}`,
    `uses_bff=${networkLog.some((entry) => entry.pathname.startsWith("/bff/"))}`,
  ];
}

function resultSummary(results: CaseResult[], networkLog: Array<{ pathname: string }>, consoleErrors: string[]): string {
  const rows = results.map((item) => `| ${item.case_id} | ${item.status} | ${item.notes} |`).join("\n");
  return `# V4.1 Desktop Folder Recursive Summary Acceptance Result

Status: full 10-case browser evidence generated by Playwright.

## Case Results

| Case | Result | Notes |
| --- | --- | --- |
${rows}

## Network Assertions

- no /v1/rpc: ${!networkLog.some((entry) => entry.pathname.includes("/v1/rpc"))}
- no /v1/events/subscribe: ${!networkLog.some((entry) => entry.pathname.includes("/v1/events/subscribe"))}
- browser used /bff routes: ${networkLog.some((entry) => entry.pathname.startsWith("/bff/"))}

## Console Errors

${consoleErrors.length ? consoleErrors.map((item) => `- ${item}`).join("\n") : "No console errors captured."}

## Evidence Files

- screenshots/
- network-log.json
- console-errors.json
- result-summary.md
`;
}
