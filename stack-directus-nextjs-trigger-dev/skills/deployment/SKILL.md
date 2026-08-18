---
name: deployment
description: This skill should be used when the user wants to "set up Docker for Directus locally", "deploy trigger.dev tasks", "run local dev for the 3-service stack", "configure content-change webhooks with trigger.dev", "CI/CD for trigger tasks", "production checklist for directus + nextjs + trigger.dev", or needs local dev and integration deployment patterns. For platform-specific hosting (Vercel, Dokploy, etc.), see the respective deployment plugin.
---

# Deployment: Local Dev + Trigger Task Deploys + Integration Patterns

Set up local development with Docker Compose for Directus, deploy Trigger.dev tasks, configure content-change revalidation, and prepare for production. For hosting platform specifics (Vercel, Dokploy, Netlify, etc.), see the respective deployment plugin — this skill covers local dev, Trigger.dev task deployment, and cross-service integration patterns.

## Docker Compose for Local Directus

Create `docker-compose.yml` in the project root:

```yaml
services:
  directus:
    image: directus/directus:latest
    ports:
      - '8055:8055'
    environment:
      SECRET: 'change-this-to-a-random-secret'
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
      CONTENT_SECURITY_POLICY_DIRECTIVES__FRAME_SRC: 'http://localhost:3000'
    depends_on:
      postgres:
        condition: service_healthy
    volumes:
      - ./directus/uploads:/directus/uploads
      - ./directus/extensions:/directus/extensions

  postgres:
    image: postgres:16
    environment:
      POSTGRES_DB: 'directus'
      POSTGRES_USER: 'directus'
      POSTGRES_PASSWORD: 'directus'
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ['CMD-SHELL', 'pg_isready -U directus']
      interval: 5s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
```

### Start Local Development

Three terminals:

```bash
# Terminal 1: Start Directus + PostgreSQL
docker compose up -d
curl http://localhost:8055/server/health

# Terminal 2: Start the Trigger.dev dev server (watches /trigger)
npx trigger.dev@latest dev

# Terminal 3: Start Next.js dev server
npm run dev
```

Access points:
- Directus Admin: `http://localhost:8055`
- Next.js App: `http://localhost:3000`
- Trigger.dev dashboard: whatever `TRIGGER_API_URL` points at (usually a separate self-hosted instance)

### Local .env.local

```bash
NEXT_PUBLIC_DIRECTUS_URL=http://localhost:8055
DIRECTUS_ADMIN_TOKEN=your-local-static-token
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=dev-secret-change-in-production
REVALIDATION_SECRET=dev-revalidation-secret
TRIGGER_SECRET_KEY=tr_dev_local_or_shared_dev_env_secret
TRIGGER_API_URL=https://trigger.your-domain.com
TRIGGER_PROJECT_REF=proj_xxxxxxxxxxx
```

Create the Directus admin static token after first startup. Re-use a shared dev env secret from the self-hosted Trigger.dev dashboard — local dev workloads show up in the **development** environment.

## Next.js Production Deployment

Deploy the Next.js frontend using your hosting platform of choice. Set these env vars in your platform's environment management:

| Variable | Value |
|----------|-------|
| `NEXT_PUBLIC_DIRECTUS_URL` | Production Directus URL |
| `DIRECTUS_ADMIN_TOKEN` | Production static token |
| `NEXTAUTH_URL` | Production Next.js URL |
| `NEXTAUTH_SECRET` | Strong random secret |
| `REVALIDATION_SECRET` | Shared secret for ISR webhook |
| `TRIGGER_SECRET_KEY` | Production env secret key `tr_prod_xxx` |
| `TRIGGER_API_URL` | Self-hosted Trigger.dev URL |
| `TRIGGER_PROJECT_REF` | Project ref from Trigger.dev dashboard |

For platform-specific deployment steps, see your deployment plugin (`dokploy-dev`, `vercel-dev`, etc.).

### next.config.ts for Production

Ensure the production Directus domain is in `images.remotePatterns`:

```typescript
const nextConfig = {
  images: {
    remotePatterns: [
      { protocol: 'https', hostname: 'cms.yourdomain.com' },
      { protocol: 'http', hostname: 'localhost', port: '8055' },
    ],
  },
};
```

## Deploying Trigger.dev Tasks

Trigger.dev tasks deploy **separately** from the Next.js app. The task code lives in `/trigger/` and runs on the Trigger.dev platform — not on your Next.js hosting.

### Production Deploy

```bash
# Deploy to the production environment on the self-hosted instance
npx trigger.dev@latest deploy --self-hosted --profile prod
```

The CLI reads `trigger.config.ts`, bundles everything under `/trigger/`, pushes the image to the self-hosted registry, and the supervisor spins up task workers.

Required for this command to succeed:
- `TRIGGER_API_URL` set in the environment
- Authenticated via `npx trigger.dev@latest login --api-url $TRIGGER_API_URL` OR a Personal Access Token in `TRIGGER_ACCESS_TOKEN`
- The self-hosted registry reachable from the machine running the deploy

### CI/CD (GitHub Actions)

```yaml
# .github/workflows/trigger-deploy.yml
name: Deploy Trigger.dev tasks
on:
  push:
    branches: [main]
    paths:
      - 'trigger/**'
      - 'trigger.config.ts'
      - 'package.json'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
      - run: npm ci
      - run: npx trigger.dev@latest deploy --self-hosted
        env:
          TRIGGER_ACCESS_TOKEN: ${{ secrets.TRIGGER_ACCESS_TOKEN }}
          TRIGGER_API_URL: ${{ secrets.TRIGGER_API_URL }}
```

**Important:** `TRIGGER_ACCESS_TOKEN` in CI must be a Personal Access Token (`tr_pat_...`), not an environment secret key. Create it in the Trigger.dev dashboard → Personal Access Tokens.

### Environment Variables for Deployed Tasks

Tasks run on the Trigger.dev platform, not on your Next.js hosting — they need their own env vars. Set them in the Trigger.dev dashboard:

- Go to the project → Environment Variables
- Add each variable per environment (development / staging / production)
- Key vars tasks typically need: `NEXT_PUBLIC_DIRECTUS_URL`, `DIRECTUS_ADMIN_TOKEN`, `NEXT_PUBLIC_SITE_URL`, `REVALIDATION_SECRET`, plus any third-party API keys

## Self-Hosted Trigger.dev Infrastructure

The Trigger.dev webapp + supervisor run on your own server. For the compose files, network topology, and update procedure, **defer to the `trigger-dev` plugin's `deployment` skill** — do not re-derive that content here. This stack plugin only covers integration with a self-hosted instance that is already running.

## On-Demand ISR Revalidation

1. Create `app/api/revalidate/route.ts`:

```typescript
import { revalidateTag } from 'next/cache';
import { NextRequest } from 'next/server';

export async function POST(request: NextRequest) {
  const secret = request.nextUrl.searchParams.get('secret');
  if (secret !== process.env.REVALIDATION_SECRET) {
    return Response.json({ error: 'Invalid secret' }, { status: 401 });
  }
  const body = await request.json();
  const collection = body.collection || body.payload?.collection;
  if (collection) {
    revalidateTag(collection);
    return Response.json({ revalidated: true, collection });
  }
  return Response.json({ error: 'No collection specified' }, { status: 400 });
}
```

2. In Directus Flow: Webhook operation pointing to:
   ```
   https://yourdomain.com/api/revalidate?secret=YOUR_REVALIDATION_SECRET
   ```
   Body: `{ "collection": "{{ $trigger.collection }}" }`

3. Add `REVALIDATION_SECRET` to your hosting platform's environment variables.

### Trigger Task → Revalidate

When a Trigger.dev task mutates Directus (AI enrichment, scheduled sync), the task itself should POST to `/api/revalidate` to invalidate the affected routes:

```typescript
// inside a Trigger task's run() function
await fetch(`${process.env.NEXT_PUBLIC_SITE_URL}/api/revalidate?secret=${process.env.REVALIDATION_SECRET}`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ collection: 'posts' }),
});
```

This closes the loop: task writes → revalidation → users see fresh content.

## Production Checklist

- [ ] Directus running with SSL and persistent storage
- [ ] `CORS_ORIGIN` on Directus includes the production Next.js domain
- [ ] Directus static token created with appropriate permissions (not full admin)
- [ ] All Next.js env vars set in your hosting platform
- [ ] `next.config.ts` `images.remotePatterns` includes the production Directus hostname
- [ ] ISR revalidation webhook set up (Directus Flow → `/api/revalidate`)
- [ ] Self-hosted Trigger.dev webapp + supervisor running (separate infra)
- [ ] Trigger.dev tasks deployed (`npx trigger.dev@latest deploy --self-hosted`)
- [ ] `TRIGGER_ACCESS_TOKEN` (PAT) stored as a CI secret for automated task deploys
- [ ] Task env vars set in Trigger.dev dashboard (Directus URL, admin token, revalidation secret, API keys)
- [ ] Route handlers that call `tasks.trigger()` have `export const dynamic = 'force-dynamic'`
- [ ] Scheduled tasks attached to production environment in the Trigger.dev dashboard
- [ ] `NEXTAUTH_SECRET` is a strong random value (not the dev placeholder)
- [ ] Docker volumes backed up for Directus uploads
