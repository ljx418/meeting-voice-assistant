import assert from "node:assert/strict";
import test from "node:test";
import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { ArtifactSummaryPanel } from "../components/ArtifactSummaryPanel.js";
import { AgentTalkShell } from "../components/AgentTalkShell.js";
import { ConsoleShell } from "../components/ConsoleShell.js";
import { EventFeed } from "../components/EventFeed.js";
import { TraceSummaryPanel } from "../components/TraceSummaryPanel.js";
import { WorkflowEditingPanel } from "../components/WorkflowEditingPanel.js";
import {
  demoBoard,
  demoAgentTalkFixture,
  demoEmbedBootstrap,
  demoEvents,
  demoHighRiskPatchDiff,
  demoInstances,
  demoPatchDiff,
  demoPatchProposal,
  demoStatus,
  demoVersions,
  demoWorkflows,
} from "../api/demoData.js";
import type { WorkflowBoard } from "../api/types.js";

const SENSITIVE_VALUES = [
  "capability_token",
  "subscription_token",
  "Authorization",
  "secret",
  "raw_trace_payload",
  "raw_artifact_content",
  "raw_connector_payload",
  "Bearer abc",
  "super-secret",
  "raw-media-bytes",
];

test("ConsoleShell renders read-only board summaries", () => {
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
      patchProposal={demoPatchProposal}
      patchDiff={demoPatchDiff}
      highRiskPatchDiff={demoHighRiskPatchDiff}
      agentTalkFixture={demoAgentTalkFixture}
      onWorkflowChange={() => undefined}
      onVersionChange={() => undefined}
      onInstanceChange={() => undefined}
    />,
  );
  assert.match(html, /harnessOS Workflow Studio/);
  assert.match(html, /项目：VideoStudio/);
  assert.match(html, /节点库/);
  assert.match(html, /拖拽节点到画布/);
  assert.match(html, /工作流画布/);
  assert.match(html, /分镜生成/);
  assert.match(html, /WARNING/);
  assert.match(html, /节点配置/);
  assert.match(html, /Agent 工作流助手/);
  assert.match(html, /Patch Proposal/);
  assert.match(html, /前往编辑面板/);
  assert.match(html, /事件/);
  assert.match(html, /Trace/);
  assert.match(html, /产物/);
  assert.match(html, /质量/);
  assert.match(html, /审批/);
  assert.match(html, /Patch/);
  for (const forbidden of ["自动应用", "自动发布", "已帮你修改并发布", "一键修改工作流", "发布新版本"]) {
    assert(!html.includes(forbidden), `${forbidden} appeared in Workflow Studio shell`);
  }
});

test("AgentTalk shell is fixture-only and redacts timeline, patch, approval and context", () => {
  const fixture = {
    ...demoAgentTalkFixture,
    events: [
      {
        type: "business.event.received",
        source: "demo" as const,
        data: {
          Authorization: "Bearer abc",
          raw_trace_payload: "raw-trace",
          raw_connector_payload: "raw-connector",
          subscription_token: "subscription_token",
        },
      },
      {
        type: "quality.evaluated",
        source: "trace_only" as const,
        data: { raw_artifact_content: "raw-media-bytes" },
      },
    ],
    patch_diff: {
      ...demoPatchDiff,
      after_summary: "Bearer abc",
    },
    approval_notice: {
      ...demoAgentTalkFixture.approval_notice,
      message: "secret super-secret",
    },
    context_summary: {
      ...demoAgentTalkFixture.context_summary,
      business: {
        selected_station: "station_review",
        capability_token: "capability_token",
        raw_artifact_content: "raw-media-bytes",
      },
    },
  };
  const html = renderToStaticMarkup(<AgentTalkShell fixture={fixture} />);
  assert.match(html, /Agent 工作流助手/);
  assert.match(html, /分镜生成 Agent/);
  assert.match(html, /等待用户确认/);
  assert.match(html, /生成建议/);
  assert.match(html, /前往编辑面板/);
  assert.match(html, /查看 Diff/);
  for (const value of SENSITIVE_VALUES) {
    assert(!html.includes(value), `${value} leaked in AgentTalk shell`);
  }
  assert(!html.includes("context.system"));
  assert(!html.includes("context.runtime"));
});

test("Embed bootstrap exposes only BFF-local event URL and no mutation actions", () => {
  const text = JSON.stringify(demoEmbedBootstrap);
  assert(text.includes("bff_eventsource_url"));
  assert(!text.includes('"eventsource_url":'));
  assert(!text.includes("subscription_token"));
  assert(!text.includes("capability_token"));
  for (const forbidden of ["apply_patch", "publish_version", "respond_approval", "update_context", "emit_business_event", "start_workflow"]) {
    assert(!text.includes(forbidden));
  }
});

test("rendered board output redacts sensitive values", () => {
  const board: WorkflowBoard = {
    ...demoBoard,
    trace_summary: {
      trace_id: "trace_sensitive",
      summary: "Bearer abc",
      raw_trace_payload: "raw-trace",
      Authorization: "Bearer abc",
    },
    artifacts: [
      {
        artifact_id: "art_sensitive",
        kind: "binary",
        metadata: {
          capability_token: "capability_token",
          subscription_token: "subscription_token",
          secret: "super-secret",
          raw_artifact_content: "raw-media-bytes",
        },
      },
    ],
  };
  const html = renderToStaticMarkup(<ArtifactSummaryPanel artifacts={board.artifacts || []} />);
  const traceHtml = renderToStaticMarkup(<TraceSummaryPanel traceSummary={board.trace_summary} />);

  for (const value of SENSITIVE_VALUES) {
    assert(!html.includes(value), `${value} leaked in artifact panel`);
    assert(!traceHtml.includes(value), `${value} leaked in trace panel`);
  }
  assert(html.includes("[redacted]"));
  assert(traceHtml.includes("[redacted]"));
});

test("EventFeed redacts raw event payload details", () => {
  const html = renderToStaticMarkup(
    <EventFeed
      events={[
        {
          type: "approval.required",
          data: {
            approval_id: "appr_1",
            Authorization: "Bearer abc",
            raw_trace_payload: "raw-trace",
            subscription_token: "subscription_token",
          },
        },
      ]}
    />,
  );
  for (const value of SENSITIVE_VALUES) {
    assert(!html.includes(value), `${value} leaked in event feed`);
  }
  assert(html.includes("approval.required"));
  assert(html.includes("[redacted]"));
});

test("Workflow editing panel does not expose raw high-risk apply", () => {
  const html = renderToStaticMarkup(
    <WorkflowEditingPanel proposal={demoPatchProposal} diff={demoPatchDiff} highRiskDiff={demoHighRiskPatchDiff} />,
  );
  assert.match(html, /approval_removed/);
  assert.match(html, /需要治理审批/);
  assert.match(html, /disabled="">等待治理确认/);
  assert.match(html, /查看 Diff/);
  assert.match(html, /应用到草稿/);
  assert.match(html, /发布新版本/);
  assert.match(html, /disabled=""/);
  assert(!html.includes("自动应用"));
  assert(!html.includes("自动发布"));
});
