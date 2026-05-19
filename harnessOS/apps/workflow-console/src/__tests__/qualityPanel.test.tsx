import assert from "node:assert/strict";
import test from "node:test";
import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { QualityPanel } from "../components/QualityPanel.js";

test("QualityPanel is read-only and redacts issue metadata", () => {
  const html = renderToStaticMarkup(
    <QualityPanel
      evaluations={[
        {
          evaluation_id: "qe_1",
          status: "failed",
          score: 0.4,
          rubric_id: "rubric_storyboard",
          issues: [{ raw_artifact_content: "raw bytes", message: "角色一致性不足" }],
          suggestions: [{ secret: "secret value", message: "增强角色设定" }],
        },
      ]}
    />,
  );
  assert.match(html, /质量面板/);
  assert.match(html, /只读刷新/);
  assert.match(html, /rubric_storyboard/);
  assert(!html.includes("raw bytes"));
  assert(!html.includes("secret value"));
  assert(!html.includes("quality.evaluation.create"));
  assert(!html.includes("quality.evaluation.attach"));
});
