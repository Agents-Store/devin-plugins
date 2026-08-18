# Configuration Reference

Complete `trigger.config.ts` options.

## Full Configuration

```ts
import { defineConfig } from "@trigger.dev/sdk";

export default defineConfig({
  // Required
  project: "proj_xxxxx",

  // Task directories (default: ["./src/trigger"])
  dirs: ["./src/trigger"],

  // Runtime: "node" (default), "node-22", or "bun"
  runtime: "node",

  // Log level: "debug" | "info" | "log" | "warn" | "error" | "none"
  logLevel: "info",

  // Default machine preset for all tasks
  defaultMachine: "small-1x",

  // Default max duration in seconds
  maxDuration: 300,

  // Default retry configuration
  retries: {
    enabledInDev: false,
    default: {
      maxAttempts: 3,
      factor: 2,
      minTimeoutInMs: 1000,
      maxTimeoutInMs: 10000,
    },
  },

  // Build extensions
  build: {
    extensions: [],
    external: [],  // npm packages to exclude from bundle
  },

  // Lifecycle hooks
  onStartAttempt: async ({ payload, ctx }) => {},
  onSuccess: async ({ payload, output, ctx }) => {},
  onFailure: async ({ payload, error, ctx }) => {},

  // Telemetry / OpenTelemetry instrumentation
  telemetry: {
    instrumentations: [],
  },

  // Self-hosted: optional explicit URL
  triggerUrl: process.env.TRIGGER_API_URL,
});
```

## Build Extensions Reference

| Extension | Import | Purpose |
|-----------|--------|---------|
| `prismaExtension` | `@trigger.dev/build/extensions/prisma` | Prisma ORM support |
| `playwright` | `@trigger.dev/build/extensions/playwright` | Browser automation |
| `puppeteer` | `@trigger.dev/build/extensions/puppeteer` | Headless Chrome |
| `ffmpeg` | `@trigger.dev/build/extensions/core` | Video/audio processing |
| `pythonExtension` | `@trigger.dev/build/extensions/python` | Run Python scripts |
| `aptGet` | `@trigger.dev/build/extensions/core` | System packages |
| `additionalFiles` | `@trigger.dev/build/extensions/core` | Include extra files |
| `additionalPackages` | `@trigger.dev/build/extensions/core` | Include extra npm packages |
| `syncEnvVars` | `@trigger.dev/build/extensions/core` | Dynamic env var sync |
| `syncVercelEnvVars` | `@trigger.dev/build/extensions/vercel` | Sync from Vercel |
| `emitDecoratorMetadata` | `@trigger.dev/build/extensions/core` | TypeScript decorators |
| `audioWaveform` | `@trigger.dev/build/extensions/core` | Audio waveform generation |
| `esbuildPlugin` | `@trigger.dev/build/extensions/core` | Custom esbuild plugins |

## Debugging Configuration

```bash
# Dry run to check config without starting
npx trigger.dev@latest dev --log-level debug
```

## build.external

Exclude packages from the bundle (native modules, large deps):

```ts
build: {
  external: ["sharp", "canvas"],
}
```
