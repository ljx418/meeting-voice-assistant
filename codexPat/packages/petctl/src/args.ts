import type { LightEffect, PetAction, PetEvent, PetEventLevel, PetSound, PetSourceKind } from "@agent-desktop-pet/pet-protocol";

export type NotifyArgs = {
  command: "notify";
  json: boolean;
  pretty: boolean;
  token?: string;
  url?: string;
  instance?: string;
  payloadOptions: PayloadOptions;
};

export type AttachArgs = {
  command: "attach";
  target: "codex";
  json: boolean;
  pretty: boolean;
  printEnv: boolean;
  token?: string;
  url?: string;
  name?: string;
  workspaceLabel?: string;
  workspaceHash?: string;
};

export type ListArgs = {
  command: "list";
  json: boolean;
  pretty: boolean;
  token?: string;
  url?: string;
};

export type DetachArgs = {
  command: "detach";
  json: boolean;
  pretty: boolean;
  token?: string;
  url?: string;
  instance?: string;
};

export type CodexLaunchArgs = {
  command: "codex";
  action: "launch";
  json: boolean;
  pretty: boolean;
  token?: string;
  url?: string;
  name?: string;
  workspaceLabel?: string;
  workspaceHash?: string;
  bin: string;
  monitor: "none" | "jsonl";
  noTitle: boolean;
  passthrough: string[];
};

export type CodexSessionStartArgs = {
  command: "codex";
  action: "session";
  sessionAction: "start";
  json: boolean;
  pretty: boolean;
  token?: string;
  url?: string;
  name?: string;
  workspaceLabel?: string;
  workspaceHash?: string;
  mode: "exec" | "tui";
  monitor: "none" | "jsonl" | "hooks";
  bin: string;
  noTitle: boolean;
  passthrough: string[];
};

export type CodexSessionStatusArgs = {
  command: "codex";
  action: "session";
  sessionAction: "status";
  json: boolean;
  pretty: boolean;
  instance?: string;
};

export type CodexDoctorArgs = {
  command: "codex";
  action: "doctor";
  json: boolean;
  pretty: boolean;
  token?: string;
  url?: string;
};

export type CodexProbeArgs = {
  command: "codex";
  action: "probe";
  probeTarget: "active-window";
  terminal: "terminal" | "iterm2";
  json: boolean;
  pretty: boolean;
};

export type CodexBindPreviewArgs = {
  command: "codex";
  action: "bind";
  bindAction: "active-window";
  terminal: "terminal";
  preview: true;
  json: boolean;
  pretty: boolean;
};

export type CodexBindConfirmArgs = {
  command: "codex";
  action: "bind";
  bindAction: "confirm";
  candidate?: string;
  name?: string;
  token?: string;
  url?: string;
  json: boolean;
  pretty: boolean;
};

export type CodexBindArgs = CodexBindPreviewArgs | CodexBindConfirmArgs;

export type CodexRouteTestArgs = {
  command: "codex";
  action: "route";
  routeAction: "test";
  binding?: string;
  level?: PetEventLevel;
  token?: string;
  url?: string;
  json: boolean;
  pretty: boolean;
};

export type CodexRouteArgs = CodexRouteTestArgs;

export type PetctlArgs = NotifyArgs | AttachArgs | ListArgs | DetachArgs | CodexLaunchArgs | CodexSessionStartArgs | CodexSessionStatusArgs | CodexDoctorArgs | CodexProbeArgs | CodexBindArgs | CodexRouteArgs;

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

export function parseArgs(argv: string[]): PetctlArgs {
  const [command, ...rest] = argv;
  if (command === "attach") {
    return parseAttachArgs(rest);
  }
  if (command === "list") {
    return parseListArgs(rest);
  }
  if (command === "detach") {
    return parseDetachArgs(rest);
  }
  if (command === "codex") {
    return parseCodexArgs(rest);
  }
  if (command !== "notify") {
    throw new Error("usage: petctl <notify|attach|list|detach|codex> [options]");
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
      case "--instance":
        args.instance = readValue(rest, ++index, flag);
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

function parseCodexArgs(rest: string[]): CodexLaunchArgs | CodexSessionStartArgs | CodexSessionStatusArgs | CodexDoctorArgs | CodexProbeArgs | CodexBindArgs | CodexRouteArgs {
  const [action, ...options] = rest;
  if (action === "session") {
    return parseCodexSessionArgs(options);
  }
  if (action === "doctor") {
    return parseCodexDoctorArgs(options);
  }
  if (action === "probe") {
    return parseCodexProbeArgs(options);
  }
  if (action === "bind") {
    return parseCodexBindArgs(options);
  }
  if (action === "route") {
    return parseCodexRouteArgs(options);
  }
  if (action !== "launch") {
    throw new Error("usage: petctl codex <launch|session|doctor|probe|bind|route> [options]");
  }
  const args: CodexLaunchArgs = {
    command: "codex",
    action: "launch",
    json: false,
    pretty: false,
    bin: "codex",
    monitor: "none",
    noTitle: false,
    passthrough: []
  };

  for (let index = 0; index < options.length; index += 1) {
    const flag = options[index];
    if (flag === "--") {
      args.passthrough = options.slice(index + 1);
      break;
    }
    switch (flag) {
      case "--json":
        args.json = true;
        break;
      case "--pretty":
        args.pretty = true;
        break;
      case "--token":
        args.token = readValue(options, ++index, flag);
        break;
      case "--url":
        args.url = readValue(options, ++index, flag);
        break;
      case "--name":
        args.name = readValue(options, ++index, flag);
        break;
      case "--workspace-label":
        args.workspaceLabel = readValue(options, ++index, flag);
        break;
      case "--workspace-hash":
        args.workspaceHash = readValue(options, ++index, flag);
        break;
      case "--bin":
        args.bin = readValue(options, ++index, flag);
        break;
      case "--monitor": {
        const monitor = readValue(options, ++index, flag);
        if (monitor !== "none" && monitor !== "jsonl") {
          throw new Error("--monitor must be none or jsonl");
        }
        args.monitor = monitor;
        break;
      }
      case "--no-title":
        args.noTitle = true;
        break;
      default:
        throw new Error(`unknown option: ${flag}`);
    }
  }

  if (!args.bin || args.bin.startsWith("--")) {
    throw new Error("--bin requires a value");
  }

  return args;
}

function parseCodexSessionArgs(options: string[]): CodexSessionStartArgs | CodexSessionStatusArgs {
  const [sessionAction, ...flags] = options;
  if (sessionAction === "status") {
    const args: CodexSessionStatusArgs = {
      command: "codex",
      action: "session",
      sessionAction,
      json: false,
      pretty: false
    };
    for (let index = 0; index < flags.length; index += 1) {
      const flag = flags[index];
      switch (flag) {
        case "--json":
          args.json = true;
          break;
        case "--pretty":
          args.pretty = true;
          break;
        case "--instance":
          args.instance = readValue(flags, ++index, flag);
          break;
        default:
          throw new Error(`unknown option: ${flag}`);
      }
    }
    return args;
  }
  if (sessionAction !== "start") {
    throw new Error("usage: petctl codex session <start|status> [options]");
  }

  const args: CodexSessionStartArgs = {
    command: "codex",
    action: "session",
    sessionAction,
    json: false,
    pretty: false,
    mode: "exec",
    monitor: "jsonl",
    bin: "codex",
    noTitle: false,
    passthrough: []
  };
  let modeSet = false;
  let monitorSet = false;

  for (let index = 0; index < flags.length; index += 1) {
    const flag = flags[index];
    if (flag === "--") {
      args.passthrough = flags.slice(index + 1);
      break;
    }
    switch (flag) {
      case "--json":
        args.json = true;
        break;
      case "--pretty":
        args.pretty = true;
        break;
      case "--token":
        args.token = readValue(flags, ++index, flag);
        break;
      case "--url":
        args.url = readValue(flags, ++index, flag);
        break;
      case "--name":
        args.name = readValue(flags, ++index, flag);
        break;
      case "--workspace-label":
        args.workspaceLabel = readValue(flags, ++index, flag);
        break;
      case "--workspace-hash":
        args.workspaceHash = readValue(flags, ++index, flag);
        break;
      case "--mode": {
        const mode = readValue(flags, ++index, flag);
        if (mode !== "exec" && mode !== "tui") {
          throw new Error("--mode must be exec or tui");
        }
        args.mode = mode;
        modeSet = true;
        break;
      }
      case "--monitor": {
        const monitor = readValue(flags, ++index, flag);
        if (monitor !== "none" && monitor !== "jsonl" && monitor !== "hooks") {
          throw new Error("--monitor must be none, jsonl, or hooks");
        }
        args.monitor = monitor;
        monitorSet = true;
        break;
      }
      case "--bin":
        args.bin = readValue(flags, ++index, flag);
        break;
      case "--no-title":
        args.noTitle = true;
        break;
      default:
        throw new Error(`unknown option: ${flag}`);
    }
  }

  if (!modeSet) {
    throw new Error("petctl codex session start requires --mode");
  }
  if (!monitorSet) {
    throw new Error("petctl codex session start requires --monitor");
  }
  if (args.mode === "exec" && args.monitor !== "jsonl") {
    throw new Error("--mode exec requires --monitor jsonl");
  }
  if (args.mode === "tui" && args.monitor === "jsonl") {
    throw new Error("--mode tui requires --monitor hooks or none");
  }
  if (!args.bin || args.bin.startsWith("--")) {
    throw new Error("--bin requires a value");
  }
  if (args.passthrough.length === 0) {
    throw new Error("petctl codex session start requires a command after --");
  }

  return args;
}

function parseCodexRouteArgs(options: string[]): CodexRouteArgs {
  const [routeAction, ...flags] = options;
  if (routeAction !== "test") {
    throw new Error("usage: petctl codex route test --binding <bindingId> --level <level> [--json|--pretty]");
  }
  const args: CodexRouteTestArgs = {
    command: "codex",
    action: "route",
    routeAction,
    json: false,
    pretty: false
  };

  for (let index = 0; index < flags.length; index += 1) {
    const flag = flags[index];
    switch (flag) {
      case "--json":
        args.json = true;
        break;
      case "--pretty":
        args.pretty = true;
        break;
      case "--binding":
        args.binding = readValue(flags, ++index, flag);
        break;
      case "--level":
        args.level = readValue(flags, ++index, flag) as PetEventLevel;
        break;
      case "--token":
        args.token = readValue(flags, ++index, flag);
        break;
      case "--url":
        args.url = readValue(flags, ++index, flag);
        break;
      default:
        throw new Error(`unknown option: ${flag}`);
    }
  }

  if (!args.binding) {
    throw new Error("petctl codex route test requires --binding");
  }
  if (!args.level) {
    throw new Error("petctl codex route test requires --level");
  }
  return args;
}

function parseCodexBindArgs(options: string[]): CodexBindArgs {
  const [bindAction, ...flags] = options;
  if (bindAction === "active-window") {
    const args: CodexBindPreviewArgs = {
      command: "codex",
      action: "bind",
      bindAction,
      terminal: "terminal",
      preview: true,
      json: false,
      pretty: false
    };
    let terminalSet = false;
    let previewSet = false;

    for (let index = 0; index < flags.length; index += 1) {
      const flag = flags[index];
      switch (flag) {
        case "--json":
          args.json = true;
          break;
        case "--pretty":
          args.pretty = true;
          break;
        case "--preview":
          previewSet = true;
          break;
        case "--terminal": {
          const terminal = readValue(flags, ++index, flag);
          if (terminal !== "terminal") {
            throw new Error("--terminal must be terminal for V4.2 codex bind");
          }
          args.terminal = terminal;
          terminalSet = true;
          break;
        }
        default:
          throw new Error(`unknown option: ${flag}`);
      }
    }

    if (!terminalSet) {
      throw new Error("petctl codex bind active-window requires --terminal");
    }
    if (!previewSet) {
      throw new Error("confirmation_required");
    }
    return args;
  }

  if (bindAction === "confirm") {
    const args: CodexBindConfirmArgs = {
      command: "codex",
      action: "bind",
      bindAction,
      json: false,
      pretty: false
    };

    for (let index = 0; index < flags.length; index += 1) {
      const flag = flags[index];
      switch (flag) {
        case "--json":
          args.json = true;
          break;
        case "--pretty":
          args.pretty = true;
          break;
        case "--candidate":
          args.candidate = readValue(flags, ++index, flag);
          break;
        case "--name":
          args.name = readValue(flags, ++index, flag);
          break;
        case "--token":
          args.token = readValue(flags, ++index, flag);
          break;
        case "--url":
          args.url = readValue(flags, ++index, flag);
          break;
        default:
          throw new Error(`unknown option: ${flag}`);
      }
    }

    if (!args.candidate) {
      throw new Error("petctl codex bind confirm requires --candidate");
    }
    return args;
  }

  throw new Error("usage: petctl codex bind <active-window|confirm> [options]");
}

function parseCodexProbeArgs(options: string[]): CodexProbeArgs {
  const [probeTarget, ...flags] = options;
  if (probeTarget !== "active-window") {
    throw new Error("usage: petctl codex probe active-window --terminal <terminal|iterm2> [--json|--pretty]");
  }
  const args: CodexProbeArgs = {
    command: "codex",
    action: "probe",
    probeTarget,
    terminal: "terminal",
    json: false,
    pretty: false
  };
  let terminalSet = false;

  for (let index = 0; index < flags.length; index += 1) {
    const flag = flags[index];
    switch (flag) {
      case "--json":
        args.json = true;
        break;
      case "--pretty":
        args.pretty = true;
        break;
      case "--terminal": {
        const terminal = readValue(flags, ++index, flag);
        if (terminal !== "terminal" && terminal !== "iterm2") {
          throw new Error("--terminal must be terminal or iterm2");
        }
        args.terminal = terminal;
        terminalSet = true;
        break;
      }
      default:
        throw new Error(`unknown option: ${flag}`);
    }
  }

  if (!terminalSet) {
    throw new Error("petctl codex probe active-window requires --terminal");
  }

  return args;
}

function parseCodexDoctorArgs(options: string[]): CodexDoctorArgs {
  const args: CodexDoctorArgs = {
    command: "codex",
    action: "doctor",
    json: false,
    pretty: false
  };

  for (let index = 0; index < options.length; index += 1) {
    const flag = options[index];
    switch (flag) {
      case "--json":
        args.json = true;
        break;
      case "--pretty":
        args.pretty = true;
        break;
      case "--token":
        args.token = readValue(options, ++index, flag);
        break;
      case "--url":
        args.url = readValue(options, ++index, flag);
        break;
      default:
        throw new Error(`unknown option: ${flag}`);
    }
  }

  return args;
}

function parseAttachArgs(rest: string[]): AttachArgs {
  const [target, ...options] = rest;
  if (target !== "codex") {
    throw new Error("usage: petctl attach codex [options]");
  }
  const args: AttachArgs = {
    command: "attach",
    target: "codex",
    json: false,
    pretty: false,
    printEnv: false
  };

  for (let index = 0; index < options.length; index += 1) {
    const flag = options[index];
    switch (flag) {
      case "--json":
        args.json = true;
        break;
      case "--pretty":
        args.pretty = true;
        break;
      case "--print-env":
        args.printEnv = true;
        break;
      case "--token":
        args.token = readValue(options, ++index, flag);
        break;
      case "--url":
        args.url = readValue(options, ++index, flag);
        break;
      case "--name":
        args.name = readValue(options, ++index, flag);
        break;
      case "--workspace-label":
        args.workspaceLabel = readValue(options, ++index, flag);
        break;
      case "--workspace-hash":
        args.workspaceHash = readValue(options, ++index, flag);
        break;
      default:
        throw new Error(`unknown option: ${flag}`);
    }
  }

  return args;
}

function parseListArgs(rest: string[]): ListArgs {
  const args: ListArgs = {
    command: "list",
    json: false,
    pretty: false
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
      default:
        throw new Error(`unknown option: ${flag}`);
    }
  }

  return args;
}

function parseDetachArgs(rest: string[]): DetachArgs {
  const args: DetachArgs = {
    command: "detach",
    json: false,
    pretty: false
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
      case "--instance":
        args.instance = readValue(rest, ++index, flag);
        break;
      default:
        throw new Error(`unknown option: ${flag}`);
    }
  }

  if (!args.instance) {
    throw new Error("petctl detach requires --instance");
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
