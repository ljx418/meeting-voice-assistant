import assert from "node:assert/strict";
import test from "node:test";
import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { ContextPanel } from "../components/ContextPanel.js";

test("ContextPanel renders redacted business context only", () => {
  const html = renderToStaticMarkup(
    <ContextPanel
      context={{
        workflow_instance_id: "wfi_1",
        revision: 3,
        business: {
          selected_node: "分镜生成",
          raw_trace_payload: "raw trace",
          Authorization: "Bearer secret",
        },
      }}
    />,
  );
  assert.match(html, /业务上下文/);
  assert.match(html, /context.business/);
  assert.match(html, /selected_node/);
  assert(!html.includes("raw trace"));
  assert(!html.includes("Bearer secret"));
  assert(!html.includes("context.system"));
  assert(!html.includes("context.runtime"));
});
