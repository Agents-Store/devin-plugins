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
  runtime: "node",          // "node" (current LTS), "node-22", "node-24", "node-26", or "bun"
  logLevel: "info",         // "debug" | "info" | "log" | "warn" | "error" | "none"

  // REQUIRED — seconds a run may use, at least 5. Without it `dev` and `deploy` fail with:
  // The "maxDuration" trigger.config option is now required, and must be at least 5 seconds.
  maxDuration: 300,

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

### Required and common keys

| Key | Notes |
|-----|-------|
| `project` | Required. Project ref (`proj_xxx`) |
| `maxDuration` | **Required.** Number of seconds, minimum 5. Per-task `maxDuration` overrides it |
| `dirs` | Task directories (auto-detects folders named `trigger`) |
| `runtime` | `"node"` (or unset) follows the current Node.js LTS on CLI/server 4.7.2+ (node-24 at the time of writing); pin `"node-22"`, `"node-24"` or `"node-26"` (4.5.7+) to keep a major. `"bun"` is experimental. The older `experimental-` prefixed names for Node 24 and 26 are deprecated aliases. `init` defaults to `node-24` |
| `machine` | Default machine preset for deployed tasks (default `small-1x`); a task can override it |
| `ttl` | Project-wide queue TTL (see below) |
| `retries` | `{ enabledInDev, default }` retry options |
| `extraCACerts` | `"./certs/ca.crt"` — extra CA certificate file for tasks; use it when a self-hosted instance has a self-signed certificate (path must start with `./`, relative to the project root) |
| `build` | `extensions`, `external`, `conditions`, `autoDetectExternal`, `keepNames`, `minify`, `jsx` |
| `telemetry` | OpenTelemetry `instrumentations`, `exporters`, `logExporters`, `metricExporters` |
| `processKeepAlive`, `legacyDevProcessCwdBehaviour`, `tsconfig`, `ignorePatterns`, `enableConsoleLogging` | Less common |

The config has no URL key. The API URL comes from `TRIGGER_API_URL`, the CLI profile (`login -a`), or `configure({ baseURL })` in your own code.

## TTL Defaults (v4.4.4+)

Set a project-wide TTL in `trigger.config.ts` and/or override per task. Runs expire with status `EXPIRED` if they are not dequeued in the window.

```ts
// Global default for all tasks in the project
export default defineConfig({
  project: "<project-ref>",
  maxDuration: 300,
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
# Install matching the SDK and CLI version (all @trigger.dev/* packages share one version)
pnpm add -D @trigger.dev/build@<sdk-version>   # for example ^4, or the exact SDK version
npx trigger.dev@<sdk-version> update           # aligns every @trigger.dev/* package with the CLI
```

On self-hosted, use the version of the server. The CLI warns on a mismatch during `dev` and `deploy`, and `deploy` can fail in CI when the CLI and the `@trigger.dev/*` packages differ.

Without this package, deploy will fail with `Cannot find module '@trigger.dev/build/extensions/core'`.

### Prisma

```ts
import { prismaExtension } from "@trigger.dev/build/extensions/prisma";

extensions: [
  prismaExtension({
    mode: "legacy",              // REQUIRED since 4.1.1
    schema: "prisma/schema.prisma",
    migrate: true,
    directUrlEnvVarName: "DIRECT_DATABASE_URL",
  }),
]
```

`mode` picks the Prisma generation strategy:

| `mode` | Use with |
|--------|----------|
| `"legacy"` | Prisma 6 and earlier, `prisma-client-js` provider. The extension runs `prisma generate`; supports `migrate`, `typedSql`, multi-file schemas |
| `"engine-only"` | A custom client `output` path and your own `prisma generate` (prebuild script); only installs the engines. Optional `version` |
| `"modern"` | Prisma 6.16+ (`prisma-client` provider with `engineType = "client"`) or Prisma 7. Zero config; you run `prisma generate` |

Without `mode` the types fail; at runtime the extension falls back to legacy, which is wrong for Prisma 7.

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

Install the package first: `npm add @trigger.dev/python` (versions track the SDK; peers are `@trigger.dev/sdk` and `@trigger.dev/build`).

```ts
import { pythonExtension } from "@trigger.dev/python/extension";

extensions: [
  pythonExtension({
    scripts: ["./python/**/*.py"],
    requirementsFile: "./requirements.txt",
    devPythonBinaryPath: ".venv/bin/python",
  }),
]

// Usage in tasks (the runtime helpers come from the package root):
// import { python } from "@trigger.dev/python";
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

### Other extensions

| Extension | Import | Purpose |
|-----------|--------|---------|
| `additionalPackages` | `@trigger.dev/build/extensions/core` | Install extra npm packages into the image |
| `emitDecoratorMetadata` | `@trigger.dev/build/extensions/typescript` | TypeScript decorator metadata (TypeORM, NestJS style) |
| `audioWaveform` | `@trigger.dev/build/extensions/audioWaveform` | BBC audiowaveform binary |
| `lightpanda` | `@trigger.dev/build/extensions/lightpanda` | Lightpanda headless browser (`version`, `disableTelemetry`) |
| `esbuildPlugin` | `@trigger.dev/build/extensions` | Custom esbuild plugin |
| `syncVercelEnvVars`, `syncNeonEnvVars`, `syncSupabaseEnvVars` | `@trigger.dev/build/extensions/core` | Pull env vars from Vercel / Neon / Supabase at deploy time |

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
  prismaExtension({ mode: "legacy", schema: "prisma/schema.prisma", migrate: true }),
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

Hooks do not belong in `defineConfig`: the config keys `onSuccess`, `onFailure`, `onStart` and `init` are deprecated. Register global hooks with the `tasks` API in an `init.ts` file at the root of a directory listed in `dirs` — the file is loaded before every run. The full example is in the **task-development** skill (`references/advanced-tasks.md`, "Global lifecycle hooks").

## Machine and Duration Defaults

```ts
export default defineConfig({
  project: "<project-ref>",
  machine: "medium-1x",   // default preset for all deployed tasks
  maxDuration: 300,       // required, seconds
});
```

A task can override both: `machine: "large-1x"` (or `{ preset: "large-1x" }`) and `maxDuration: 1800`.

## Telemetry Integration

```ts
import { PrismaInstrumentation } from "@prisma/instrumentation";

export default defineConfig({
  project: "<project-ref>",
  maxDuration: 300,
  telemetry: {
    instrumentations: [new PrismaInstrumentation()],
  },
});
```

Extensions only affect deployment, not local development.

## Deeper Reference

- @references/config-reference.md — complete configuration options
