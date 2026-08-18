---
name: init-project
description: This skill should be used when the user asks to "set up Directus + Next.js project", "initialize Directus Next.js stack", "configure Directus with Next.js", "connect Directus to Next.js", "bootstrap Directus Next.js app", "create Next.js app with Directus", "scaffold Directus + Next.js", "start new project with Directus", "create a new Directus Next.js project", or needs to set up environment variables and verify connections for the Directus + Next.js stack.
---

# Initialize Directus + Next.js Stack

Set up the project environment, install dependencies, create the Directus SDK client, and verify all connections.

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
| `REVALIDATION_SECRET` | Run `openssl rand -base64 32` (used by Directus webhooks for ISR) |

## 2. Install Dependencies

```bash
npm install @directus/sdk server-only
```

- `@directus/sdk` — Composable Directus client for fetching data
- `server-only` — Prevents accidental import of server code in Client Components

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

Update this file as new Directus collections are created. Each collection maps to an interface with fields matching the Directus field names.

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

## 6. Verify Connections

Test the Directus MCP connection by calling the `schema` tool with no parameters. A successful response lists all collections.

Test the SDK connection by adding a temporary check:

```typescript
import directus from '@/lib/directus';
import { readItems } from '@directus/sdk';

// In any Server Component or route handler:
const result = await directus.request(readItems('directus_collections'));
console.log('Connected! Collections:', result.length);
```

## 7. Generate Project CLAUDE.md

Copy `templates/CLAUDE.md.template` to the project root as `CLAUDE.md`. Replace placeholders with actual values:
- `[PROJECT_NAME]` — the project name
- `[DIRECTUS_URL]` — the Directus instance URL

## 8. Docker Local Dev (Optional)

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
