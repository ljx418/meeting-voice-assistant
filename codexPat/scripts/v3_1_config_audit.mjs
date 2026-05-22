#!/usr/bin/env node
import { existsSync, readFileSync } from "node:fs";
import { homedir } from "node:os";
import { join } from "node:path";

const APP_IDENTIFIER = "com.agentdesktoppet.desktop";
const args = new Set(process.argv.slice(2));
const jsonMode = args.has("--json");

const configDir = configDirForPlatform();
const settingsPath = configDir ? join(configDir.real, "settings.json") : undefined;
const tokenPath = configDir ? join(configDir.real, "api-token.json") : undefined;
const settingsExists = settingsPath ? existsSync(settingsPath) : false;
const tokenExists = tokenPath ? existsSync(tokenPath) : false;
const parsedSettings = settingsExists ? readSettingsSummary(settingsPath) : { readable: false };

const summary = {
  platform: process.platform,
  appIdentifier: APP_IDENTIFIER,
  configDir: configDir?.display,
  pathSource: configDir?.source,
  settings: {
    exists: settingsExists,
    readable: parsedSettings.readable,
    hasPetInstances: parsedSettings.hasPetInstances,
    petInstanceCount: parsedSettings.petInstanceCount,
    hasMuted: parsedSettings.hasMuted,
    muted: parsedSettings.muted,
    hasPosition: parsedSettings.hasPosition,
    hasVisible: parsedSettings.hasVisible,
    hasProfiles: parsedSettings.hasProfiles,
    hasDefaultProfile: parsedSettings.hasDefaultProfile
  },
  tokenFile: {
    exists: tokenExists
  },
  tokenValuePrinted: false,
  rawSettingsPrinted: false,
  fullUserPathPrinted: false,
  authorizationHeaderPrinted: false
};

if (jsonMode) {
  console.log(JSON.stringify(summary, null, 2));
} else {
  printHumanSummary(summary);
}

function configDirForPlatform() {
  if (process.platform === "darwin") {
    return {
      real: join(homedir(), "Library", "Application Support", APP_IDENTIFIER),
      display: `~/Library/Application Support/${APP_IDENTIFIER}`,
      source: "macOS app_config_dir compatible path"
    };
  }
  if (process.platform === "win32") {
    const appData = process.env.APPDATA;
    if (!appData) {
      return {
        real: undefined,
        display: `%APPDATA%/${APP_IDENTIFIER}`,
        source: "APPDATA missing"
      };
    }
    return {
      real: join(appData, APP_IDENTIFIER),
      display: `%APPDATA%/${APP_IDENTIFIER}`,
      source: "Windows APPDATA compatible path"
    };
  }
  const base = process.env.XDG_CONFIG_HOME || join(homedir(), ".config");
  return {
    real: join(base, APP_IDENTIFIER),
    display: process.env.XDG_CONFIG_HOME
      ? `$XDG_CONFIG_HOME/${APP_IDENTIFIER}`
      : `~/.config/${APP_IDENTIFIER}`,
    source: "XDG config compatible path"
  };
}

function readSettingsSummary(path) {
  try {
    const parsed = JSON.parse(readFileSync(path, "utf8"));
    const petInstances = Array.isArray(parsed.petInstances) ? parsed.petInstances : [];
    const hasDefaultProfile = typeof parsed.defaultCatProfileId === "string";
    const hasInstanceProfiles = petInstances.some((instance) => typeof instance?.catProfileId === "string");
    return {
      readable: true,
      hasPetInstances: Array.isArray(parsed.petInstances),
      petInstanceCount: petInstances.length,
      hasMuted: typeof parsed.muted === "boolean",
      muted: typeof parsed.muted === "boolean" ? parsed.muted : undefined,
      hasPosition: "petX" in parsed || "petY" in parsed || petInstances.some((instance) => instance?.position),
      hasVisible: typeof parsed.petVisible === "boolean" || petInstances.some((instance) => typeof instance?.visible === "boolean"),
      hasProfiles: hasDefaultProfile || hasInstanceProfiles,
      hasDefaultProfile
    };
  } catch {
    return {
      readable: false,
      hasPetInstances: false,
      petInstanceCount: 0,
      hasMuted: false,
      hasPosition: false,
      hasVisible: false,
      hasProfiles: false,
      hasDefaultProfile: false
    };
  }
}

function printHumanSummary(value) {
  console.log("agent-desktop-pet config audit");
  console.log(`platform: ${value.platform}`);
  console.log(`appIdentifier: ${value.appIdentifier}`);
  console.log(`configDir: ${value.configDir ?? "unavailable"}`);
  console.log(`pathSource: ${value.pathSource ?? "unknown"}`);
  console.log(`settings.exists: ${value.settings.exists}`);
  console.log(`settings.readable: ${value.settings.readable}`);
  console.log(`settings.hasPetInstances: ${value.settings.hasPetInstances}`);
  console.log(`settings.petInstanceCount: ${value.settings.petInstanceCount ?? 0}`);
  console.log(`settings.hasMuted: ${value.settings.hasMuted}`);
  console.log(`settings.muted: ${value.settings.muted ?? "unknown"}`);
  console.log(`settings.hasPosition: ${value.settings.hasPosition}`);
  console.log(`settings.hasVisible: ${value.settings.hasVisible}`);
  console.log(`settings.hasProfiles: ${value.settings.hasProfiles}`);
  console.log(`settings.hasDefaultProfile: ${value.settings.hasDefaultProfile}`);
  console.log(`tokenFile.exists: ${value.tokenFile.exists}`);
  console.log(`tokenValuePrinted: ${value.tokenValuePrinted}`);
  console.log(`rawSettingsPrinted: ${value.rawSettingsPrinted}`);
  console.log(`fullUserPathPrinted: ${value.fullUserPathPrinted}`);
  console.log(`authorizationHeaderPrinted: ${value.authorizationHeaderPrinted}`);
}
