import Ajv2020 from "ajv/dist/2020.js";
import schema from "../schemas/pet-event.schema.json" with { type: "json" };
import type { PetEvent } from "./types.js";

const AjvCtor = Ajv2020 as unknown as { new (options: { allErrors: boolean }): any };
const ajv = new AjvCtor({ allErrors: true });
const validatePetEventSchema = ajv.compile(schema);

export function isPetEvent(value: unknown): value is PetEvent {
  return validatePetEventSchema(value);
}

export function validatePetEvent(value: unknown) {
  const valid = validatePetEventSchema(value);
  return {
    valid,
    errors: valid ? [] : [...(validatePetEventSchema.errors ?? [])]
  };
}
