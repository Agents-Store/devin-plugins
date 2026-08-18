---
name: init-project
description: This skill should be used when the user asks to "set up Directus + Next.js + Trigger.dev project", "initialize directus nextjs trigger.dev stack", "bootstrap the 3-service stack", "configure directus next.js and trigger.dev together", "connect trigger.dev to a directus nextjs app", "scaffold stack with background tasks", "start a new project with background jobs", or needs to set up environment variables and verify connections for the Directus + Next.js + Trigger.dev stack.
---

# Initialize Directus + Next.js + Trigger.dev Stack

Set up the project environment, install dependencies, create the Directus SDK client, initialize Trigger.dev, and verify all three service connections.

## 1. Copy Environment File

Copy `templates/.env.example` to `.env.local` in the project root. Guide the user through setting each variable:

```bash
cp templates/.env.example .env.local
```

| Variable | How to obtain |
|----------|---------------|
| `NEXT_PUBLIC_DIRECTUS_URL` | Directus instance URL (e.g. `https://cms.example.com` or `http://localhost:8055` for Docker) |
| `DIRECTUS_ADMIN_TOKEN` | Directus Settings → Access Tokens → create a static token |
| `NEXTAUTH_URL` | `http://localhost:3000` for local dev |
| `NEXTAUTH_SECRET` | Run `openssl rand -base64 32` |
| `REVALIDATION_SECRET` | Run `openssl rand -base64 32` (used by Directus webhooks and Trigger tasks) |
| `TRIGGER_SECRET_KEY` | Trigger.dev dashboard → API Keys → DEV secret key (or a Personal Access Token — see `.env.example` note) |
| `TRIGGER_API_URL` | Self-hosted Trigger.dev URL (e.g. `https://trigger.your-domain.com`) |
| `TRIGGER_PROJECT_REF` | Trigger.dev project page → `proj_xxxxx` ref |

## 2. Install Dependencies

```bash
npm install @directus/sdk server-only
npm install @trigger.dev/sdk @trigger.dev/react-hooks
```

- `@directus/sdk` — Composable Directus client for fetching data
- `server-only` — Prevents accidental import of server code in Client Components
- `@trigger.dev/sdk` — Trigger.dev SDK for defining tasks and calling `tasks.trigger()`
- `@trigger.dev/react-hooks` — Realtime hooks for showing task run status in Client Components

## 3. Create Directus Client

Create `lib/directus.ts`:

```typescript
import 'server-only';
import { createDirectus, rest, staticToken } from '@directus/sdk';
import type { Schema } from '@/types/directus';

const directus = createDirectus<Schema>(process.env.NEXT_PUBLIC_DIRECTUS_URL!)
  .with(staticToken(process.env.DIRECTUS_ADMIN_TOKEN!))
  .with(rest({ cache: 'no-store' }));

export default directus;
```

**Critical:** Always pass `{ cache: 'no-store' }` to `rest()`. Next.js extends the native fetch API with `force-cache` by default — without this option, Directus API responses are cached indefinitely and return stale data.

## 4. Create TypeScript Schema

Create `types/directus.ts` with interface stubs. Use the Directus MCP `schema` tool to discover collections, then define matching interfaces:

```typescript
export interface Schema {
  // Add collections as you create them:
  // posts: Post[];
  // authors: Author[];
}
```

## 5. Configure Next.js Image Handling

Add the Directus domain to `next.config.ts` so `next/image` can optimize Directus assets:

```typescript
const nextConfig = {
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: new URL(process.env.NEXT_PUBLIC_DIRECTUS_URL!).hostname,
      },
    ],
  },
};

export default nextConfig;
```

## 6. Initialize Trigger.dev in the Project

Run the Trigger.dev CLI initializer from the project root:

```bash
npx trigger.dev@latest init
```

The CLI will:
- Prompt for the Trigger.dev API URL (paste `TRIGGER_API_URL` from `.env.local`) — select **Self-hosted** when asked
- Prompt for the project ref (paste `TRIGGER_PROJECT_REF`)
- Create a `/trigger` directory with an example task
- Generate `trigger.config.ts` at the project root
- Add `@trigger.dev/sdk` to `package.json` (already installed in step 2)

**Verify `trigger.config.ts`** looks roughly like:

```typescript
import { defineConfig } from '@trigger.dev/sdk/v3';

export default defineConfig({
  project: process.env.TRIGGER_PROJECT_REF!,
  runtime: 'node',
  logLevel: 'log',
  maxDuration: 3600,
  retries: {
    enabledInDev: true,
    default: {
      maxAttempts: 3,
      factor: 2,
      minTimeoutInMs: 1000,
      maxTimeoutInMs: 10000,
      randomize: true,
    },
  },
  dirs: ['./trigger'],
});
```

If the generated config uses a hardcoded `project: "proj_xxxxx"` string, replace it with `process.env.TRIGGER_PROJECT_REF!` so the value flows through `.env.local`.

## 7. Authenticate the Trigger.dev CLI

For CLI commands (`dev`, `deploy`) to reach the self-hosted instance:

```bash
npx trigger.dev@latest login --api-url $TRIGGER_API_URL
```

A browser window opens. After login, verify:

```bash
npx trigger.dev@latest whoami
```

If this fails, make sure `TRIGGER_API_URL` is reachable from the developer machine and that the user has a dashboard account on the self-hosted instance.

## 8. Start the Trigger Dev Server

In a separate terminal, run:

```bash
npx trigger.dev@latest dev
```

This connects to the self-hosted platform, registers tasks in `/trigger`, and watches for changes. Leave it running alongside `npm run dev`.

## 9. Verify All Three Connections

| Service | How to verify |
|---------|---------------|
| **Directus MCP** | Call the `schema` MCP tool — a successful response lists all collections |
| **Directus SDK** | Add a temporary Server Component that calls `directus.request(readItems('directus_collections'))` and logs the count |
| **Trigger.dev MCP** | Call the Trigger MCP `list_projects` (or equivalent) tool — should return the connected project |
| **Trigger.dev SDK** | Ensure `npx trigger.dev@latest dev` shows the example task registered |
| **Next.js** | `npm run dev` starts without errors and the default page renders |

Run the example Trigger task end-to-end:

```bash
# In the dev terminal, you should see the task registered.
# Then from any Server Action or route handler:
```

```typescript
// app/api/test-trigger/route.ts
import { tasks } from '@trigger.dev/sdk/v3';
import { NextResponse } from 'next/server';
import type { exampleTask } from '@/trigger/example';

export const dynamic = 'force-dynamic';

export async function GET() {
  const handle = await tasks.trigger<typeof exampleTask>('example', { name: 'world' });
  return NextResponse.json(handle);
}
```

Hitting `http://localhost:3000/api/test-trigger` returns a run handle; the dev terminal shows the task executing.

## 10. Generate Project CLAUDE.md

Copy `templates/CLAUDE.md.template` to the project root as `CLAUDE.md`. Replace placeholders:
- `[PROJECT_NAME]` — the project name
- `[DIRECTUS_URL]` — the Directus instance URL
- `[TRIGGER_API_URL]` — the Trigger.dev self-hosted URL

## 11. Docker Local Dev (Optional)

If the user wants a local Directus instance, create `docker-compose.yml`:

```yaml
services:
  directus:
    image: directus/directus:latest
    ports:
      - '8055:8055'
    environment:
      SECRET: 'change-this-secret'
      ADMIN_EMAIL: 'admin@example.com'
      ADMIN_PASSWORD: 'change-this-password'
      DB_CLIENT: 'postgres'
      DB_HOST: 'postgres'
      DB_PORT: '5432'
      DB_DATABASE: 'directus'
      DB_USER: 'directus'
      DB_PASSWORD: 'directus'
      CORS_ENABLED: 'true'
      CORS_ORIGIN: 'http://localhost:3000'
    depends_on:
      - postgres
    volumes:
      - ./directus/uploads:/directus/uploads

  postgres:
    image: postgres:16
    environment:
      POSTGRES_DB: 'directus'
      POSTGRES_USER: 'directus'
      POSTGRES_PASSWORD: 'directus'
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

Start with `docker compose up -d`, then set `NEXT_PUBLIC_DIRECTUS_URL=http://localhost:8055` in `.env.local`.

For the self-hosted Trigger.dev webapp + supervisor, use the compose setup from the `trigger-dev` plugin's deployment skill — do not duplicate it here.
