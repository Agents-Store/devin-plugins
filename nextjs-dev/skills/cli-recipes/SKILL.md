---
name: cli-recipes
description: Next.js CLI commands and common development scripts. This skill should be used when the user asks about "Next.js CLI", "next dev command", "next build", "create-next-app", "Turbopack", "Next.js command line", or needs to run Next.js commands from the terminal.
---

# Next.js CLI Recipes

Command-line recipes for creating, developing, building, and deploying Next.js applications. Current as of Next.js 16 (16.3 latest).

## Create a New Project

```bash
npx create-next-app@latest my-app
```

The first prompt asks whether to use the recommended defaults (TypeScript, ESLint, Tailwind CSS, App Router, AGENTS.md); answering no walks through each option.

Non-interactive with the defaults:

```bash
npx create-next-app@latest my-app --ts --tailwind --eslint --app --src-dir --import-alias "@/*" --yes
```

Useful flags (Next.js 16):

| Flag | Purpose |
|------|---------|
| `--biome` / `--no-linter` | Use Biome instead of ESLint, or skip linter setup |
| `--react-compiler` | Enable the React Compiler in the new project |
| `--api` | Route-handlers-only project (no UI) |
| `--empty` | Minimal empty project |
| `--agents-md` | Write AGENTS.md + CLAUDE.md for coding agents (default: on) |
| `--webpack` | Configure webpack instead of the default Turbopack |
| `--skip-install` | Skip installing dependencies |
| `--disable-git` | Skip git initialization |

From a template:

```bash
npx create-next-app@latest --example with-tailwindcss my-app
npx create-next-app@latest --example https://github.com/user/repo my-app
```

## Development Server

Turbopack is the **default bundler** in Next.js 16 for both `next dev` and `next build` — no flag needed. Opt out with `--webpack`.

```bash
# Standard dev server (Turbopack by default in 16+)
next dev

# Opt out of Turbopack
next dev --webpack

# Custom port
next dev -p 4000

# Custom hostname (default is 0.0.0.0)
next dev -H 127.0.0.1

# Attach the Node.js debugger to the correct process (16.1+)
next dev --inspect

# HTTPS (local development)
next dev --experimental-https

# Show verbose output
next dev --verbose
```

Since Next.js 16, dev output goes to `.next/dev`, so `next dev` and `next build` can run concurrently, and a lockfile prevents two `next dev` instances on one project.

## Build for Production

```bash
# Production build (Turbopack by default in 16+)
next build

# Opt out of Turbopack
next build --webpack

# Debug prerender errors with full output
next build --debug-prerender

# Build only a subset of routes (faster iteration on build issues)
next build --debug-build-paths="app/**/page.tsx"
```

Build output appears in `.next/`. For standalone output (Docker), set `output: 'standalone'` in `next.config.ts`.

`next build` still type-checks but **no longer lints** (Next.js 16) — run ESLint or Biome separately. Since 16.3, `typescript@^7` is supported for much faster type checking, and Turbopack's filesystem cache makes repeat builds up to 5.5x faster.

The build reports:
- **Route sizes** — JS sent to client per route
- **First Load JS** — Total JS for initial page load
- **Static vs Dynamic** — Which routes are statically generated vs server-rendered

## Start Production Server

```bash
# Start built application
next start

# Custom port
next start -p 4000

# Attach the Node.js debugger (16.2+)
next start --inspect

# Keep-alive timeout for proxied deployments (ms)
next start --keepAliveTimeout 70000
```

Requires `next build` first. Serves the production build with Node.js.

## Linting

**`next lint` was removed in Next.js 16**, and `next build` no longer runs linting. Migrate with the official codemod, then run ESLint (or Biome) directly:

```bash
# Migrate from next lint to the ESLint CLI
npx @next/codemod@canary next-lint-to-eslint-cli .

# Lint with ESLint directly (flat config: eslint.config.mjs)
npx eslint .

# Fix auto-fixable issues
npx eslint . --fix
```

`eslint-config-next` still catches common Next.js issues (incorrect image usage, missing `alt` attributes, incorrect `<link>`/`<script>` usage, accessibility issues), and `@next/eslint-plugin-next` now defaults to ESLint Flat Config. Biome is the supported alternative (`--biome` in create-next-app).

## Type Checking

```bash
# Generate route types, then type-check (recommended for CI)
next typegen && npx tsc --noEmit
```

`next typegen` (15.5+) generates route and `PageProps` types into `.next/types` without running a full build, and also writes `next-env.d.ts`. `next build` includes type checking as well.

## Useful Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `PORT` | Dev/prod server port | `PORT=4000 next dev` |
| `HOSTNAME` | Server hostname | `HOSTNAME=0.0.0.0 next start` |
| `NODE_ENV` | Environment | `development`, `production`, `test` |
| `NEXT_TELEMETRY_DISABLED` | Disable telemetry | `NEXT_TELEMETRY_DISABLED=1` |
| `ANALYZE` | Enable `@next/bundle-analyzer` (webpack builds only — prefer `next experimental-analyze`) | `ANALYZE=true next build --webpack` |
| `NEXT_PUBLIC_*` | Client-side env vars | `NEXT_PUBLIC_API_URL=...` |

## Package Scripts

Typical `package.json` scripts:

```json
{
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "eslint .",
    "lint:fix": "eslint . --fix",
    "type-check": "next typegen && tsc --noEmit",
    "format": "prettier --write .",
    "test": "vitest",
    "test:e2e": "playwright test"
  }
}
```

## Bundle Analysis

Use the built-in Turbopack bundle analyzer (16.1+):

```bash
# Interactive treemap UI on port 4000
next experimental-analyze

# Write static analysis files to .next/diagnostics/analyze
next experimental-analyze --output
```

The analyzer filters by route, shows import chains, and provides separate client/server views.

> `@next/bundle-analyzer` (`ANALYZE=true`) is webpack-based and only works with `next build --webpack`.

## Docker Deployment

```dockerfile
FROM node:22-alpine AS base

FROM base AS deps
WORKDIR /app
COPY package.json pnpm-lock.yaml ./
RUN corepack enable pnpm && pnpm install --frozen-lockfile

FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN corepack enable pnpm && pnpm build

FROM base AS runner
WORKDIR /app
ENV NODE_ENV=production
RUN addgroup --system --gid 1001 nodejs && adduser --system --uid 1001 nextjs
COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static
USER nextjs
EXPOSE 3000
ENV PORT=3000
CMD ["node", "server.js"]
```

Requires `output: 'standalone'` in `next.config.ts`.

## Telemetry

```bash
# Disable telemetry
next telemetry --disable

# Enable telemetry
next telemetry --enable
```

## Upgrading & Codemods

```bash
# Recommended upgrade path (16.1+): built-in upgrade command
next upgrade
next upgrade --revision canary   # or latest / a specific version

# Codemod-driven upgrade (works from any version)
npx @next/codemod@canary upgrade latest

# Run a specific codemod
npx @next/codemod@canary <transform> <path>
```

Key codemods for Next.js 16:
- `middleware-to-proxy` — rename `middleware.ts` to `proxy.ts` with the `proxy` export
- `next-lint-to-eslint-cli` — migrate from the removed `next lint` to the ESLint CLI
- Async API migrations (`params`, `cookies`, `headers`), configuration changes, and deprecated API removals
