---
name: deployment
description: This skill should be used when the user wants to "set up Docker for Directus", "run Directus locally with Docker", "configure content-change webhooks", "set up ISR revalidation with Directus", "auto-rebuild on content change", "production checklist for Directus + Next.js", or needs local dev and integration patterns for the Directus + Next.js stack. For platform-specific deployment (Vercel, Dokploy, etc.), see the respective deployment plugin.
---

# Deployment: Local Dev + Integration Patterns

Set up local development with Docker Compose for Directus, configure content-change revalidation, and prepare for production. For hosting platform specifics (Vercel, Dokploy, Netlify, etc.), see the respective deployment plugin — this skill covers local dev and cross-service integration patterns only.

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

```bash
# Start Directus + PostgreSQL
docker compose up -d

# Verify Directus is running
curl http://localhost:8055/server/health

# Start Next.js dev server
npm run dev
```

Access points:
- Directus Admin: `http://localhost:8055`
- Next.js App: `http://localhost:3000`

### Local .env.local

```bash
NEXT_PUBLIC_DIRECTUS_URL=http://localhost:8055
DIRECTUS_ADMIN_TOKEN=your-local-static-token
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=dev-secret-change-in-production
REVALIDATION_SECRET=dev-revalidation-secret
```

Create the admin static token in Directus Admin → Settings → Access Tokens after first startup.

## next.config.ts for Production

Ensure the production Directus domain is in `images.remotePatterns` so `next/image` can optimize Directus assets:

```typescript
const nextConfig = {
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'cms.yourdomain.com',
      },
      {
        protocol: 'http',
        hostname: 'localhost',
        port: '8055',
      },
    ],
  },
};
```

## On-Demand ISR Revalidation

For instant content updates without a full rebuild, use Next.js on-demand revalidation triggered by Directus:

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

2. In Directus Flow: add a Webhook operation pointing to:
   ```
   https://yourdomain.com/api/revalidate?secret=YOUR_REVALIDATION_SECRET
   ```
   With body: `{ "collection": "{{ $trigger.collection }}" }`

3. Add `REVALIDATION_SECRET` to your hosting platform's environment variables.

## Content-Change Webhooks (Directus Automate)

Set up a Directus Flow to notify the Next.js app when content changes:

1. In Directus: Settings → Flows → create a new Flow:
   - **Trigger**: Event Hook → `items.create`, `items.update` on content collections (e.g. `posts`, `pages`)
   - **Condition** (optional): Check `{{ $trigger.payload.status }} == "published"` to only trigger on publish
   - **Operation**: Webhook → POST to the ISR revalidation endpoint (above)

This gives instant content updates: editor publishes in Directus → Flow fires → `/api/revalidate` invalidates the cache → next visitor sees fresh content.

For hosting platforms that support deploy hooks (full rebuild on content change), configure those via the platform's deployment plugin.

## Production Directus Hosting

Directus in production needs:
- SSL/TLS enabled
- `CORS_ORIGIN` set to your production Next.js domain
- A static access token with minimum necessary permissions (not full admin)
- File storage configured (S3, Cloudflare R2, or local with persistent volume)
- Persistent PostgreSQL with backups

The hosting approach (Docker on VPS, managed cloud, container platform) depends on your infrastructure — see your deployment plugin for platform-specific setup.

## Production Checklist

- [ ] Directus running with SSL and persistent storage
- [ ] `CORS_ORIGIN` on Directus includes the production Next.js domain
- [ ] Static token created with appropriate permissions (not full admin for production)
- [ ] All environment variables set in your hosting platform (Directus URL, admin token, NextAuth secrets)
- [ ] `next.config.ts` `images.remotePatterns` includes the production Directus hostname
- [ ] ISR revalidation webhook set up for instant content updates
- [ ] `NEXTAUTH_SECRET` is a strong random value (not the dev placeholder)
- [ ] Docker volumes backed up for Directus uploads
- [ ] `REVALIDATION_SECRET` set in both Directus env and Next.js hosting env
