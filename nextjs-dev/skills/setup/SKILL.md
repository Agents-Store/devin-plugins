---
name: setup
description: Verify Next.js project environment and readiness. This skill should be used when the user asks to "verify Next.js setup", "check Next.js project", "is my Next.js app configured correctly", "test Next.js environment", or needs to confirm their project is ready for development.
---

# Verify Next.js Project Setup

Confirm that a Next.js project is properly configured for modern App Router development. Run these checks in order and report results.

## Prerequisites

- Node.js 20.9+ installed (Next.js 16 minimum); TypeScript 5.1+
- A Next.js project directory with `package.json`

## Step 1: Check Next.js Version

Read `package.json` and locate the `next` dependency:

```json
{
  "dependencies": {
    "next": "^16.0.0"
  }
}
```

| Version | Status | Notes |
|---------|--------|-------|
| 16.x | Current (16.3 latest) | Cache Components, Turbopack default, `proxy.ts`, built-in MCP at `/_next/mcp` |
| 15.x | Maintenance | Backport releases only (e.g. 15.5.x); `middleware.ts` era, no built-in MCP |
| 14.x | Legacy | App Router GA, consider upgrading |
| 13.x or below | Outdated | Upgrade required for modern patterns |

## Step 2: Verify App Router Structure

Check that the project uses the `app/` directory (not just `pages/`):

```
app/
├── layout.tsx       # Root layout (required)
├── page.tsx         # Home page
├── loading.tsx      # Optional loading state
├── error.tsx        # Optional error boundary
└── not-found.tsx    # Optional 404 page
```

If only `pages/` exists, the project uses the legacy Pages Router. Recommend migrating to App Router for new features.

## Step 3: Verify TypeScript Configuration

Check for `tsconfig.json` with Next.js recommended settings:

```json
{
  "compilerOptions": {
    "target": "ES2017",
    "lib": ["dom", "dom.iterable", "esnext"],
    "jsx": "preserve",
    "module": "esnext",
    "moduleResolution": "bundler",
    "strict": true,
    "paths": {
      "@/*": ["./src/*"]
    },
    "plugins": [{ "name": "next" }]
  }
}
```

Key checks:
- `strict: true` is set
- Path aliases (`@/*`) are configured
- The `next` plugin is present for IDE support

## Step 4: Verify Next.js Config

Check for `next.config.ts` (TypeScript) or `next.config.mjs`:

```ts
import type { NextConfig } from 'next'

const nextConfig: NextConfig = {
  // Configuration options
}

export default nextConfig
```

The config file can be `next.config.ts` natively (TypeScript is fully supported). Common configuration to verify:
- `images.remotePatterns` — if using external image domains
- `cacheComponents` — must be `true` for `use cache` / Cache Components (16+)
- `experimental` — any experimental features enabled
- `output` — `'standalone'` for Docker deployments

## Step 5: Check Dev Server

Run the development server to confirm it starts:

```bash
npm run dev
# or
pnpm dev
```

Verify the server starts on `http://localhost:3000` without errors.

## Step 6: Verify MCP Integration (Next.js 16+)

For Next.js 16+, the built-in MCP endpoint is available at `/_next/mcp` when the dev server is running. Check for `.mcp.json` in the project root:

```json
{
  "mcpServers": {
    "next-devtools": {
      "command": "npx",
      "args": ["-y", "next-devtools-mcp@latest"]
    }
  }
}
```

Or install with one command: `npx add-mcp next-devtools-mcp@latest`.

If not present, recommend adding it for enhanced AI-assisted development.

## Optional: CI Type Checking

Recommend `next typegen && npx tsc --noEmit` in CI — `next typegen` generates route and `PageProps` types without a full build.

## What This Skill Does NOT Cover

- Installing Node.js or package managers — see Node.js official docs
- Creating a new project from scratch — use `npx create-next-app@latest`
- Configuring MCP servers — that belongs to project-level `.mcp.json` configuration
- Setting up CI/CD or deployment — see deployment guides
