import assert from "node:assert/strict";
import test from "node:test";
import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { ConsoleShell } from "../components/ConsoleShell.js";
import { WorkflowConsoleClient } from "../api/workflowConsoleClient.js";
import { demoBoard, demoEvents, demoInstances, demoStatus, demoVersions, demoWorkflows } from "../api/demoData.js";
import type { FolderSummaryProposal, FolderSummaryRun } from "../api/types.js";

const proposal: FolderSummaryProposal = {
  proposal_id: "v41_folder_proposal_test",
  workflow_template_id: "v41_local_folder_summary_template",
  workflow_draft_id: "v41_local_folder_summary_draft",
  workflow_instance_id: null,
  draft_revision: 1,
  status: "proposed",
  requested_path: "Desktop/技术分享",
  nodes: [
    "folder_input",
    "folder_scan",
    "markdown_filter",
    "markdown_parse",
    "folder_group",
    "per_folder_summary",
    "overview_summary",
    "quality_check",
    "artifact_publish",
  ].map((station_id) => ({ station_id, name: station_id, status: "pending" })),
  edges: [],
  risk_flags: ["local_file_read"],
  requires_user_confirmation: true,
  created_at: "2026-05-25T00:00:00Z",
  updated_at: "2026-05-25T00:00:00Z",
  redaction_status: "redacted",
};

const run: FolderSummaryRun = {
  workflow_instance_id: "v41_folder_instance_test",
  proposal_id: proposal.proposal_id,
  authorization_id: "folder_auth_test",
  status: "completed",
  nodes: proposal.nodes.map((node) => ({ ...node, status: "completed", updated_at: "2026-05-25T00:00:00Z" })),
  artifacts: [
    { artifact_id: "art_agentos", name: "AgentOS_总结.md", kind: "markdown_summary", content: "## 内容概览\n## 核心主题\n## 关键知识点\n## 重要文件列表\n## 引用文件", redaction_status: "redacted" },
    { artifact_id: "art_quality", name: "quality_report.json", kind: "quality_report", content: '{"unsupported_files":["未支持/test.pdf"]}', redaction_status: "redacted" },
  ],
  quality_report: {
    status: "passed",
    summary_coverage: { expected_folder_count: 3, generated_summary_count: 3 },
    unsupported_files: ["未支持/test.pdf"],
    empty_folders: ["空文件夹"],
    markdown_file_count: 5,
    child_folder_count: 5,
    redaction_status: "redacted",
  },
  created_at: "2026-05-25T00:00:00Z",
  updated_at: "2026-05-25T00:00:00Z",
  redaction_status: "redacted",
};

test("folder summary workflow renders proposal controls, ghost nodes, artifacts and quality report", () => {
  const html = renderToStaticMarkup(
    <ConsoleShell
      workflows={demoWorkflows}
      versions={demoVersions}
      instances={demoInstances}
      selectedWorkflowId={demoWorkflows[0].workflow_template_id}
      selectedVersionId={demoVersions[0].workflow_version_id}
      selectedInstanceId={demoInstances[0].workflow_instance_id}
      board={demoBoard}
      status={demoStatus}
      events={demoEvents}
      folderSummaryProposal={proposal}
      folderSummaryAuthorization={{
        authorization_id: "folder_auth_test",
        requested_path: "Desktop/技术分享",
        resolved_path_label: "tests/fixtures/desktop/技术分享",
        allowed_root: "dev_local_desktop_fixture",
        status: "authorized",
        created_at: "2026-05-25T00:00:00Z",
        expires_at: "2026-05-25T02:00:00Z",
        redaction_status: "redacted",
      }}
      folderSummaryScan={{
        folder_tree: [{ path: "AgentOS/01-架构.md", kind: "file" }],
        total_file_count: 6,
        markdown_file_count: 5,
        child_folder_count: 5,
        unsupported_file_count: 1,
        unsupported_files: ["未支持/test.pdf"],
        empty_folders: ["空文件夹"],
        redaction_status: "redacted",
      }}
      folderSummaryRun={run}
      onWorkflowChange={() => undefined}
      onVersionChange={() => undefined}
      onInstanceChange={() => undefined}
    />,
  );

  assert.match(html, /本地 Markdown 文件夹总结/);
  assert.match(html, /应用到草稿/);
  assert.match(html, /发布版本/);
  assert.match(html, /运行工作流/);
  assert.match(html, /Desktop\/技术分享 递归总结/);
  assert.match(html, /查看产物/);
  assert.match(html, /folder_input/);
  assert.match(html, /artifact_publish/);
  assert.match(html, /AgentOS_总结.md/);
  assert.match(html, /未支持\/test.pdf/);
  assert.match(html, /空文件夹/);
  for (const forbidden of ["自动应用", "自动发布", "Agent 已执行", "Agent 已发布", "/v1/rpc", "/v1/events/subscribe"]) {
    assert(!html.includes(forbidden), `${forbidden} appeared in folder summary workflow UI`);
  }
});

test("folder summary client uses BFF-only V4.1 routes", async () => {
  const calls: Array<{ path: string; method: string; body?: string }> = [];
  const originalFetch = globalThis.fetch;
  globalThis.fetch = (async (input: RequestInfo | URL, init?: RequestInit) => {
    calls.push({ path: String(input), method: init?.method || "GET", body: typeof init?.body === "string" ? init.body : undefined });
    return new Response(JSON.stringify({ proposal_id: "v41_folder_proposal_test" }), { status: 200, headers: { "content-type": "application/json" } });
  }) as typeof fetch;
  try {
    const client = new WorkflowConsoleClient("/bff");
    await client.createFolderSummaryProposal({ folder_path: "Desktop/技术分享", source: "workflow_console" });
    assert.equal(calls[0].method, "POST");
    assert.equal(calls[0].path, "/bff/v4_1/folder-summary/proposals");
    assert(!calls[0].path.includes("/v1/rpc"));
    assert(!calls[0].path.includes("/v1/events/subscribe"));
  } finally {
    globalThis.fetch = originalFetch;
  }
});
