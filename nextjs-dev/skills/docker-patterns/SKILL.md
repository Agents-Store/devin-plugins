---
name: docker-patterns
description: >
  Docker configuration patterns for Next.js applications. This skill should be used when the user asks
  to "dockerize Next.js", "create a Dockerfile for Next.js", "set up Docker for Next.js", "docker compose
  for Next.js", "build Next.js with Docker", "deploy Next.js in Docker", "Next.js standalone Docker",
  or needs to containerize a Next.js application for development or production.
---

# Docker Patterns for Next.js

Patterns for containerizing Next.js applications using the standalone output mode. Covers development, production, and docker-compose configurations.

## Prerequisites

- Docker 20+ and Docker Compose v2+
- Next.js 14+ project with App Router
- `pnpm` (or `npm`/`yarn` — adjust commands accordingly)

## Step 1: Enable Standalone Output

Set `output: 'standalone'` in `next.config.ts` — this creates a self-contained build that includes only the necessary dependencies, reducing the Docker image size significantly.

```ts
import type { NextConfig } from 'next'

const nextConfig: NextConfig = {
  output: 'standalone',
}

export default nextConfig
```

## Step 2: Production Dockerfile (Multi-Stage)

Multi-stage build that produces a minimal production image (~150MB vs ~1GB without standalone).

```dockerfile
FROM node:22-alpine AS base

RUN corepack enable && corepack prepare pnpm@latest --activate

# --- Dependencies ---
FROM base AS deps
WORKDIR /app
COPY package.json pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile

# --- Build ---
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN pnpm build

# --- Production ---
FROM node:22-alpine AS runner
WORKDIR /app

ENV NODE_ENV=production

RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000
ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

CMD ["node", "server.js"]
```

Key points:
- `deps` stage caches `node_modules` — rebuilds only when `package.json`/`pnpm-lock.yaml` change
- `builder` stage compiles the app — `standalone` output bundles server + minimal deps into `.next/standalone`
- `runner` stage copies only `standalone` + `static` + `public` — no `node_modules`, no source code
- Non-root `nextjs` user for security

## Step 3: Development Dockerfile

Simpler single-stage image for development with hot reload via volume mounts.

```dockerfile
FROM node:22-alpine

RUN corepack enable && corepack prepare pnpm@latest --activate

WORKDIR /app

COPY package.json pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile

COPY . .

EXPOSE 3000

CMD ["pnpm", "dev"]
```

## Step 4: Docker Compose

Define both dev and production services. Use `docker compose up dev` for development or `docker compose up app` for production.

```yaml
services:
  # Development — hot reload via volume mounts
  dev:
    build:
      context: .
      dockerfile: Dockerfile.dev
    ports:
      - "3000:3000"
    volumes:
      - .:/app
      - /app/node_modules
      - /app/.next
    env_file:
      - .env.local
    restart: unless-stopped

  # Production — standalone build
  app:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    env_file:
      - .env.local
    restart: unless-stopped
```

Volume mount notes for `dev` service:
- `.:/app` — mounts source code for hot reload
- `/app/node_modules` — anonymous volume prevents host `node_modules` from overwriting container's
- `/app/.next` — anonymous volume prevents build cache conflicts

## Step 5: .dockerignore

Exclude files that should not be copied into the Docker build context.

```
node_modules
.next
.git
.gitignore
.claude
.cursor
.vercel
*.md
deploy.sh
scripts
docs
```

Keep `.env.local` out of the image — pass it via `env_file` in docker-compose or `--env-file` at runtime. Never bake secrets into the image.

## Common Patterns

### With External Services (Directus, PostgreSQL, etc.)

```yaml
services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    env_file:
      - .env.local
    depends_on:
      directus:
        condition: service_healthy

  directus:
    image: directus/directus:latest
    ports:
      - "8055:8055"
    environment:
      DB_CLIENT: sqlite3
      DB_FILENAME: /directus/database/data.db
      ADMIN_EMAIL: admin@example.com
      ADMIN_PASSWORD: admin
    healthcheck:
      test: ["CMD", "wget", "--spider", "http://localhost:8055/server/health"]
      interval: 10s
      timeout: 5s
      retries: 3
```

### Build Arguments for Environment-Specific Builds

```dockerfile
# In Dockerfile builder stage
ARG NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL
RUN pnpm build
```

```yaml
# In docker-compose.yml
services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
      args:
        NEXT_PUBLIC_API_URL: https://api.example.com
```

Use `ARG` + `ENV` for `NEXT_PUBLIC_*` variables — they are inlined at build time, so they must be available during `pnpm build`.

### Health Check

```yaml
services:
  app:
    # ...
    healthcheck:
      test: ["CMD", "wget", "--spider", "http://localhost:3000/api/health"]
      interval: 30s
      timeout: 5s
      retries: 3
      start_period: 10s
```

## Commands

```bash
# Build and start dev
docker compose up dev --build

# Build and start production
docker compose up app --build

# Build production image only
docker compose build app

# Run in background
docker compose up app -d

# View logs
docker compose logs app --tail 50

# Stop all
docker compose down
```

## Troubleshooting

| Issue | Cause | Fix |
|-------|-------|-----|
| `public: not found` in COPY | No `public/` directory in project | Create `public/` with at least one file, or use `COPY --from=builder /app/public ./public 2>/dev/null \|\| true` |
| Hot reload not working in dev | Volume mount not matching | Ensure `.:/app` is set and `/app/node_modules` is an anonymous volume |
| `NEXT_PUBLIC_*` vars empty at runtime | These are inlined at build time | Pass them as `ARG` in Dockerfile and set during `docker compose build` |
| Image too large (>500MB) | Not using standalone output | Set `output: 'standalone'` in `next.config.ts` |
| Permission denied errors | Running as root | Use non-root user with `--chown` on COPY commands |

## What This Skill Does NOT Cover

- CI/CD pipeline Docker builds — see deployment guides
- Kubernetes or Docker Swarm orchestration
- Multi-architecture builds (ARM/x86) — use `docker buildx`
- Docker registry publishing
