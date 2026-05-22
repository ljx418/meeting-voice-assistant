import { defineConfig, devices } from "@playwright/test";

const bffPort = Number(process.env.WORKFLOW_CONSOLE_BFF_PORT || 18040);
const previewPort = Number(process.env.WORKFLOW_CONSOLE_PREVIEW_PORT || 4174);

export default defineConfig({
  testDir: "./e2e",
  timeout: 45_000,
  workers: 1,
  expect: {
    timeout: 8_000,
  },
  fullyParallel: false,
  retries: 0,
  use: {
    baseURL: `http://127.0.0.1:${previewPort}`,
    trace: "retain-on-failure",
  },
  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
    },
  ],
  webServer: [
    {
      command: "../../.venv/bin/python e2e/bff_smoke_server.py",
      url: `http://127.0.0.1:${bffPort}/__test/health`,
      cwd: ".",
      timeout: 30_000,
      reuseExistingServer: !process.env.CI,
      env: {
        ...process.env,
        HARNESS_V3_5_DEV_MODE: "1",
        WORKFLOW_CONSOLE_BFF_PORT: String(bffPort),
      },
    },
    {
      command: `npm run preview -- --host 127.0.0.1 --port ${previewPort}`,
      url: `http://127.0.0.1:${previewPort}`,
      cwd: ".",
      timeout: 30_000,
      reuseExistingServer: !process.env.CI,
      env: {
        ...process.env,
        VITE_BFF_PROXY_TARGET: `http://127.0.0.1:${bffPort}`,
        VITE_HARNESSOS_DEMO_MODE: "false",
      },
    },
  ],
});
