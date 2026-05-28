import assert from "node:assert/strict";
import { describe, test } from "node:test";
import { CSS_DEFAULT_ASSET_MANIFEST } from "../assets/bundled-packs/css-default.manifest";
import { resolveCatAction } from "./cat-action-resolver";

describe("V5.0 cat action resolver", () => {
  test("maps core CatState values to safe action ids", () => {
    for (const state of ["idle", "thinking", "running", "success", "warning", "error", "need_input", "sleeping"] as const) {
      const result = resolveCatAction(state, CSS_DEFAULT_ASSET_MANIFEST);
      assert.equal(result.actionId, state);
    }
  });

  test("falls missing optional action back to idle with sanitized warning", () => {
    const result = resolveCatAction("idle", CSS_DEFAULT_ASSET_MANIFEST, { optionalActionId: "blink" });
    assert.equal(result.actionId, "idle");
    assert.equal(result.warnings.some((item) => item.code === "optional_action_fallback" && item.actionId === "blink"), true);
    assert.equal(JSON.stringify(result.warnings).includes("/Users/"), false);
    assert.equal(JSON.stringify(result.warnings).includes("Authorization"), false);
  });

  test("does not let transient success overwrite active error", () => {
    const result = resolveCatAction("success", CSS_DEFAULT_ASSET_MANIFEST, { currentState: "error" });
    assert.equal(result.actionId, "error");
    assert.equal(result.warnings.some((item) => item.code === "success_preserved_active_priority"), true);
  });

  test("does not let transient success overwrite active need_input", () => {
    const result = resolveCatAction("success", CSS_DEFAULT_ASSET_MANIFEST, { currentState: "need_input" });
    assert.equal(result.actionId, "need_input");
  });
});

