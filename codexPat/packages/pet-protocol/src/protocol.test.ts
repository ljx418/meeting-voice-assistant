import assert from "node:assert/strict";
import { describe, it } from "node:test";
import schema from "../schemas/pet-event.schema.json" with { type: "json" };
import { INVALID_PET_EVENTS } from "./fixtures/invalid-events.js";
import { VALID_PET_EVENTS } from "./fixtures/valid-events.js";
import { LIGHT_EFFECTS, PET_ACTIONS, PET_EVENT_LEVELS, PET_SOUNDS, PET_SOURCE_KINDS } from "./capabilities.js";
import { validatePetEvent } from "./validate.js";

function enumValues(path: string[]) {
  let cursor: any = schema;
  for (const segment of path) {
    cursor = cursor[segment];
  }
  return cursor.enum as string[];
}

describe("PetEvent JSON Schema", () => {
  it("accepts valid fixtures", () => {
    for (const event of VALID_PET_EVENTS) {
      assert.equal(validatePetEvent(event).valid, true);
    }
  });

  it("rejects invalid fixtures", () => {
    for (const event of INVALID_PET_EVENTS) {
      assert.equal(validatePetEvent(event).valid, false);
    }
  });

  it("keeps TypeScript capabilities aligned with schema enums", () => {
    assert.deepEqual([...PET_SOURCE_KINDS], enumValues(["properties", "source", "properties", "kind"]));
    assert.deepEqual([...PET_EVENT_LEVELS], enumValues(["properties", "level"]));
    assert.deepEqual([...PET_ACTIONS], enumValues(["properties", "action"]));
    assert.deepEqual([...PET_SOUNDS], enumValues(["properties", "sound"]));
    assert.deepEqual([...LIGHT_EFFECTS], enumValues(["properties", "hardware", "properties", "light", "properties", "effect"]));
  });
});
