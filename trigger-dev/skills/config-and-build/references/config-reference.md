# Configuration Reference

Complete `trigger.config.ts` options.

## Full Configuration

```ts
import { defineConfig } from "@trigger.dev/sdk";

export default defineConfig({
  // Required
  project: "proj_xxxxx",

  // Required: default max run duration in seconds (minimum 5). dev and deploy fail without it.
  maxDuration: 300,

  // Task directories (auto-detects folders named "trigger")
  dirs: ["./src/trigger"],

  // Runtime: "node" (current LTS from 4.7.2), "node-22", "node-24", "node-26" (4.5.7+), or "bun"
  runtime: "node",

  // Log level: "debug" | "info" | "log" | "warn" | "error" | "none"
  logLevel: "info",

  // Default machine preset for all deployed tasks (default "small-1x")
  machine: "small-1x",

  // Project-wide queue TTL (v4.4.4+); per-task and per-trigger values win
  ttl: "1h",

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

  // Telemetry / OpenTelemetry instrumentation
  telemetry: {
    instrumentations: [],
  },

  // Self-hosted with a self-signed certificate: extra CA file, path starts with "./"
  extraCACerts: "./certs/ca.crt",
});
```

The config has no URL key. The API URL comes from `TRIGGER_API_URL`, the CLI profile (`login -a <url>`), or `configure({ baseURL })`.

## Global Lifecycle Hooks

Hooks are not config keys. The config keys `onSuccess`, `onFailure`, `onStart` and `init` still parse but are deprecated. Register global hooks with the `tasks` API in an `init.ts` file inside a directory from `dirs` — see **Global lifecycle hooks** in the **task-development** skill (`references/advanced-tasks.md`).

## Build Extensions Reference

Install `@trigger.dev/build` at the same version as the SDK for everything except Python (`@trigger.dev/python`).

| Extension | Import | Purpose |
|-----------|--------|---------|
| `prismaExtension` | `@trigger.dev/build/extensions/prisma` | Prisma ORM support; `mode` is required (`legacy`, `engine-only`, `modern`) |
| `playwright` | `@trigger.dev/build/extensions/playwright` | Browser automation |
| `puppeteer` | `@trigger.dev/build/extensions/puppeteer` | Headless Chrome |
| `lightpanda` | `@trigger.dev/build/extensions/lightpanda` | Lightpanda headless browser |
| `ffmpeg` | `@trigger.dev/build/extensions/core` | Video/audio processing |
| `pythonExtension` | `@trigger.dev/python/extension` | Run Python scripts (`npm add @trigger.dev/python`) |
| `aptGet` | `@trigger.dev/build/extensions/core` | System packages |
| `additionalFiles` | `@trigger.dev/build/extensions/core` | Include extra files |
| `additionalPackages` | `@trigger.dev/build/extensions/core` | Include extra npm packages |
| `syncEnvVars` | `@trigger.dev/build/extensions/core` | Dynamic env var sync |
| `syncVercelEnvVars`, `syncNeonEnvVars`, `syncSupabaseEnvVars` | `@trigger.dev/build/extensions/core` | Sync from Vercel / Neon / Supabase |
| `emitDecoratorMetadata` | `@trigger.dev/build/extensions/typescript` | TypeScript decorators |
| `audioWaveform` | `@trigger.dev/build/extensions/audioWaveform` | Audio waveform generation |
| `esbuildPlugin` | `@trigger.dev/build/extensions` | Custom esbuild plugins |

`@trigger.dev/build` has no Python or Vercel-specific entry: the Python extension lives in the separate `@trigger.dev/python` package, and the Vercel sync is `syncVercelEnvVars` from `core`.

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
