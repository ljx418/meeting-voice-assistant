import type { LightEffect, PetAction, PetEvent, PetEventLevel, PetSound, PetSourceKind } from "@agent-desktop-pet/pet-protocol";

export type NotifyArgs = {
  command: "notify";
  json: boolean;
  pretty: boolean;
  token?: string;
  url?: string;
  payloadOptions: PayloadOptions;
};

export type PayloadOptions = {
  sourceId?: string;
  sourceKind?: PetSourceKind;
  sourceName?: string;
  level?: PetEventLevel;
  title?: string;
  message?: string;
  action?: PetAction;
  sound?: PetSound;
  durationMs?: number;
  lightEffect?: LightEffect;
  lightColor?: string;
  lightBrightness?: number;
  metadata: Record<string, string>;
};

const PAYLOAD_FLAGS = new Set([
  "--source-id",
  "--source-kind",
  "--source-name",
  "--level",
  "--title",
  "--message",
  "--action",
  "--sound",
  "--duration-ms",
  "--light-effect",
  "--light-color",
  "--light-brightness",
  "--metadata"
]);

export function parseArgs(argv: string[]): NotifyArgs {
  const [command, ...rest] = argv;
  if (command !== "notify") {
    throw new Error("usage: petctl notify [options]");
  }

  const args: NotifyArgs = {
    command: "notify",
    json: false,
    pretty: false,
    payloadOptions: {
      metadata: {}
    }
  };

  for (let index = 0; index < rest.length; index += 1) {
    const flag = rest[index];
    switch (flag) {
      case "--json":
        args.json = true;
        break;
      case "--pretty":
        args.pretty = true;
        break;
      case "--token":
        args.token = readValue(rest, ++index, flag);
        break;
      case "--url":
        args.url = readValue(rest, ++index, flag);
        break;
      case "--source-id":
        args.payloadOptions.sourceId = readValue(rest, ++index, flag);
        break;
      case "--source-kind":
        args.payloadOptions.sourceKind = readValue(rest, ++index, flag) as PetSourceKind;
        break;
      case "--source-name":
        args.payloadOptions.sourceName = readValue(rest, ++index, flag);
        break;
      case "--level":
        args.payloadOptions.level = readValue(rest, ++index, flag) as PetEventLevel;
        break;
      case "--title":
        args.payloadOptions.title = readValue(rest, ++index, flag);
        break;
      case "--message":
        args.payloadOptions.message = readValue(rest, ++index, flag);
        break;
      case "--action":
        args.payloadOptions.action = readValue(rest, ++index, flag) as PetAction;
        break;
      case "--sound":
        args.payloadOptions.sound = readValue(rest, ++index, flag) as PetSound;
        break;
      case "--duration-ms":
        args.payloadOptions.durationMs = readNumber(rest, ++index, flag);
        break;
      case "--light-effect":
        args.payloadOptions.lightEffect = readValue(rest, ++index, flag) as LightEffect;
        break;
      case "--light-color":
        args.payloadOptions.lightColor = readValue(rest, ++index, flag);
        break;
      case "--light-brightness":
        args.payloadOptions.lightBrightness = readNumber(rest, ++index, flag);
        break;
      case "--metadata":
        addMetadata(args.payloadOptions.metadata, readValue(rest, ++index, flag));
        break;
      default:
        throw new Error(`unknown option: ${flag}`);
    }
  }

  if (args.json) {
    const forbidden = rest.filter((item) => PAYLOAD_FLAGS.has(item));
    if (forbidden.length > 0) {
      throw new Error(`--json cannot be combined with payload option ${forbidden[0]}`);
    }
  }

  if (Object.keys(args.payloadOptions.metadata).length > 20) {
    throw new Error("--metadata supports at most 20 keys");
  }

  return args;
}

export function buildEventFromOptions(options: PayloadOptions): PetEvent {
  const event: PetEvent = {
    source: {
      id: options.sourceId ?? "custom.local",
      kind: options.sourceKind ?? "custom",
      name: options.sourceName ?? "petctl"
    },
    level: options.level ?? "success",
    sound: options.sound ?? "none"
  };

  if (options.title !== undefined) event.title = options.title;
  if (options.message !== undefined) event.message = options.message;
  if (options.action !== undefined) event.action = options.action;
  if (options.durationMs !== undefined) event.durationMs = options.durationMs;

  if (options.lightEffect || options.lightColor || options.lightBrightness !== undefined) {
    event.hardware = {
      light: {
        effect: options.lightEffect,
        color: options.lightColor,
        brightness: options.lightBrightness
      }
    };
  }

  if (Object.keys(options.metadata).length > 0) {
    event.metadata = options.metadata;
  }

  return event;
}

function readValue(values: string[], index: number, flag: string) {
  const value = values[index];
  if (!value || value.startsWith("--")) {
    throw new Error(`${flag} requires a value`);
  }
  return value;
}

function readNumber(values: string[], index: number, flag: string) {
  const value = Number(readValue(values, index, flag));
  if (!Number.isInteger(value)) {
    throw new Error(`${flag} requires an integer`);
  }
  return value;
}

function addMetadata(metadata: Record<string, string>, pair: string) {
  const splitAt = pair.indexOf("=");
  if (splitAt <= 0) {
    throw new Error("--metadata requires key=value");
  }
  metadata[pair.slice(0, splitAt)] = pair.slice(splitAt + 1);
}
