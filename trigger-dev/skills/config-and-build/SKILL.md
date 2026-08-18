---
name: config-and-build
description: Configure Trigger.dev projects with trigger.config.ts, add build extensions for Prisma, Playwright, FFmpeg, Python, or customize deployment settings. Use when the user asks to "configure trigger.config.ts", "add Prisma to trigger.dev", "set up build extensions", "add FFmpeg to tasks", "configure Python in trigger.dev", or needs to customize project configuration.
---

# Trigger.dev Configuration

Configure your Trigger.dev project with `trigger.config.ts` and build extensions.

## Basic Configuration

```ts
// trigger.config.ts
import { defineConfig } from "@trigger.dev/sdk";

export default defineConfig({
  project: "<project-ref>",
  dirs: ["./src/trigger"],
  runtime: "node",          // "node", "node-22", or "bun"
  logLevel: "info",         // "debug" | "info" | "log" | "warn" | "error" | "none"

  // Project-wide TTL default (v4.4.4+) — runs expire if not dequeued in the window
  ttl: "1h",

  retries: {
    enabledInDev: false,
    default: {
      maxAttempts: 3,
      minTimeoutInMs: 1000,
      maxTimeoutInMs: 10000,
      factor: 2,
    },
  },

  build: {
    extensions: [],
  },
});
```

## TTL Defaults (v4.4.4+)

Set a project-wide TTL in `trigger.config.ts` and/or override per task. Runs expire with status `EXPIRED` if they are not dequeued in the window.

```ts
// Global default for all tasks in the project
export default defineConfig({
  project: "<project-ref>",
  ttl: "1h",  // 1 hour
});
```

```ts
// Task-level override
export const myTask = task({
  id: "my-task",
  ttl: "30m",              // overrides the 1h global default
  run: async (payload) => { /* … */ },
});

// Opt out of the global default for a specific task
export const longRunning = task({
  id: "long-running",
  ttl: 0,                  // never expire due to queue wait
  run: async (payload) => { /* … */ },
});
```

**Precedence:** per-trigger `options.ttl` > task-level `ttl` > global `ttl` in config. Pass `ttl: 0` at any level to opt out.

## Build Extensions

Build extensions require the `@trigger.dev/build` package. Install it before adding any extensions to `trigger.config.ts`:

```bash
# Install matching the SDK version
pnpm add @trigger.dev/build@4.4.3
```

Without this package, deploy will fail with `Cannot find module '@trigger.dev/build/extensions/core'`.

### Prisma

```ts
import { prismaExtension } from "@trigger.dev/build/extensions/prisma";

extensions: [
  prismaExtension({
    schema: "prisma/schema.prisma",
    migrate: true,
    directUrlEnvVarName: "DIRECT_DATABASE_URL",
  }),
]
```

### Playwright (Browser Automation)

```ts
import { playwright } from "@trigger.dev/build/extensions/playwright";

extensions: [
  playwright({ browsers: ["chromium"] }),
]
```

### Puppeteer

```ts
import { puppeteer } from "@trigger.dev/build/extensions/puppeteer";

extensions: [puppeteer()]
// Set env var: PUPPETEER_EXECUTABLE_PATH="/usr/bin/google-chrome-stable"
```

### FFmpeg (Media Processing)

```ts
import { ffmpeg } from "@trigger.dev/build/extensions/core";

extensions: [
  ffmpeg({ version: "7" }),
]
// Automatically sets FFMPEG_PATH and FFPROBE_PATH
```

### Python

```ts
import { pythonExtension } from "@trigger.dev/build/extensions/python";

extensions: [
  pythonExtension({
    scripts: ["./python/**/*.py"],
    requirementsFile: "./requirements.txt",
    devPythonBinaryPath: ".venv/bin/python",
  }),
]

// Usage in tasks:
// const result = await python.runScript("./python/process.py", ["arg1"]);
```

### System Packages (apt-get)

```ts
import { aptGet } from "@trigger.dev/build/extensions/core";

extensions: [
  aptGet({ packages: ["imagemagick", "curl"] }),
]
```

### Additional Files

```ts
import { additionalFiles } from "@trigger.dev/build/extensions/core";

extensions: [
  additionalFiles({ files: ["./assets/**", "./templates/**"] }),
]
```

### Environment Variable Sync

**This is required whenever tasks use `process.env` at runtime.** Local `.env` files are NOT automatically available in deployed environments. Without `syncEnvVars`, any `process.env.X` in task code will be `undefined` at runtime, causing silent failures like `Failed to parse URL from undefined/api/...`.

```ts
import { syncEnvVars } from "@trigger.dev/build/extensions/core";

// Sync specific vars from the CLI process env (loaded via --env-file .env)
const SYNC_VARS = ["DATABASE_URL", "API_KEY", "OPENAI_API_KEY"];

extensions: [
  syncEnvVars(async () =>
    SYNC_VARS
      .filter((name) => process.env[name])
      .map((name) => ({ name, value: process.env[name]! }))
  ),
]
```

With a secret manager:
```ts
extensions: [
  syncEnvVars(async (ctx) => {
    return [
      { name: "API_KEY", value: await getSecret(ctx.environment) },
      { name: "ENV", value: ctx.environment },
    ];
  }),
]
```

Always deploy with `--env-file .env` so the CLI process has the variables available for `syncEnvVars` to read.

## Common Extension Combinations

### Full-Stack Web App

```ts
extensions: [
  prismaExtension({ schema: "prisma/schema.prisma", migrate: true }),
  additionalFiles({ files: ["./assets/**"] }),
  syncEnvVars(async (ctx) => [...envVars]),
]
```

### AI/ML Processing

```ts
extensions: [
  pythonExtension({
    scripts: ["./ai/**/*.py"],
    requirementsFile: "./requirements.txt",
  }),
  ffmpeg({ version: "7" }),
]
```

### Web Scraping

```ts
extensions: [
  playwright({ browsers: ["chromium"] }),
  additionalFiles({ files: ["./selectors.json"] }),
]
```

## Global Lifecycle Hooks

```ts
export default defineConfig({
  onStartAttempt: async ({ payload, ctx }) => {
    console.log("Task starting:", ctx.task.id);
  },
  onSuccess: async ({ payload, output, ctx }) => {
    console.log("Task succeeded");
  },
  onFailure: async ({ payload, error, ctx }) => {
    console.error("Task failed:", error);
  },
});
```

## Machine Defaults

```ts
export default defineConfig({
  defaultMachine: "medium-1x",
  maxDuration: 300,
});
```

## Telemetry Integration

```ts
import { PrismaInstrumentation } from "@prisma/instrumentation";

export default defineConfig({
  telemetry: {
    instrumentations: [new PrismaInstrumentation()],
  },
});
```

Extensions only affect deployment, not local development.

## Deeper Reference

- @references/config-reference.md — complete configuration options
