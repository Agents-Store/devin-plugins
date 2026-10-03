---
name: init-project
description: This skill should be used when the user asks to "set up Directus + Next.js project", "initialize Directus Next.js stack", "configure Directus with Next.js", "connect Directus to Next.js", "bootstrap Directus Next.js app", "create Next.js app with Directus", "scaffold Directus + Next.js", "start new project with Directus", "create a new Directus Next.js project", or needs to set up environment variables and verify connections for the Directus + Next.js stack.
---

# Initialize Directus + Next.js Stack

Bootstrap checklist: versions, environment, dependencies, client, verification. How each tool works is in `directus-dev` and `nextjs-dev`; this skill says which of their pieces to use and in what order.

## 1. Versions

| Piece | Version | Why |
|-------|---------|-----|
| Directus | 12 (MCP needs 11.12 or later) | MCP is switched on in Settings → AI. The health endpoint needs a token in 12, use `/server/ping` |
| `@directus/sdk` | 26 | Needs Node 22 or later |
| Next.js | `^16.3.8` | `proxy.ts` replaces the deprecated middleware file; earlier 16.3 patches miss security fixes |
| Node.js | 22 or later | The SDK's floor (Next.js itself needs 20.9) |

## 2. Environment File

```bash
cp templates/.env.example .env.local
```

| Variable | How to obtain |
|----------|---------------|
| `NEXT_PUBLIC_DIRECTUS_URL` | Directus address (`http://localhost:8055` for the local Docker stack) |
| `DIRECTUS_ADMIN_TOKEN` | Create a dedicated user in Directus with a policy that grants only what the server code reads and writes, then generate a static token on the user's page. The name is historical: an administrator token is for local development only |
| `DIRECTUS_URL`, `DIRECTUS_TOKEN`, `NEXT_PUBLIC_CMS_URL` | Already in `.env.example` as `${...}` references to the two rows above. The recipes of `directus-dev` and `nextjs-dev` read these names (client, NextAuth, the images block of `next.config.ts`), so do not delete them |
| `NEXTAUTH_URL`, `NEXTAUTH_SECRET` | NextAuth path only: `http://localhost:3000`, and `openssl rand -base64 32` |
| `REVALIDATION_SECRET` | `openssl rand -base64 32`; the Directus Flow sends it in a header (see `deployment`) |

`.env.local` is not committed. A variable with the `NEXT_PUBLIC_` prefix is shipped to the browser: only the address may have it, never a token.

## 3. Local Directus (optional)

Follow `directus-dev` → skill `docker-local-dev` (Compose file, `.env`, `/server/ping` check). Set `LOCAL_FRONTEND_ORIGIN=http://localhost:3000` there so CORS and Live Preview accept the Next.js dev server, then use the local address as `NEXT_PUBLIC_DIRECTUS_URL`.

## 4. Dependencies

```bash
npm install @directus/sdk@26 server-only
```

`server-only` makes the build fail when a Client Component imports the Directus client. Add `next-auth@4` or `better-auth` only when you build login (see `authentication`).

## 5. Client and Types

Create `lib/directus.ts` and `types/directus.ts` as described in `directus-dev` → skill `sdk-patterns` → `references/ssr-client.md`, reading `DIRECTUS_URL` and `DIRECTUS_TOKEN` (they expand to this stack's `NEXT_PUBLIC_DIRECTUS_URL` and `DIRECTUS_ADMIN_TOKEN`). Two things from that file decide how the rest works:

- `rest()` has **no `cache` option** (passing `cache` to `rest()` is TS2353). Caching is set per request: see "Cache" in `directus-to-nextjs`.
- Core collections are read with their own commands (`readCollections()`; `readItems` refuses `directus_*` collections).

Fill `types/directus.ts` from the real schema: call the Directus MCP `schema` tool and mirror each collection.

## 6. Images

Allow the Directus host in `next.config.ts` (`images.remotePatterns`, and `dangerouslyAllowLocalIP` for a local Directus): see `nextjs-dev` → skill `data-fetching` → `references/headless-cms.md`. How file URLs are built, and why they carry no token, is in "Assets" of `directus-to-nextjs`.

## 7. Verify Connections

1. **Directus is up:** `curl "$NEXT_PUBLIC_DIRECTUS_URL/server/ping"` answers `pong`.
2. **MCP:** call the Directus MCP `schema` tool with no parameters. It lists the collections. If it fails, check Settings → AI → Model Context Protocol and the token.
3. **SDK and token:** a temporary route that reads a core collection and pings:

```typescript
// app/api/directus-check/route.ts: temporary, delete it after the check
import directus from '@/lib/directus';
import { readCollections, serverPing } from '@directus/sdk';

export async function GET() {
  const [pong, collections] = await Promise.all([
    directus.request(serverPing()),
    directus.request(readCollections()),
  ]);
  return Response.json({ pong, collections: collections.length });
}
```

Open `/api/directus-check` with `npm run dev`. A `401` or `403` from Directus means the token is wrong or its user may not read the schema.

## 8. Project CLAUDE.md

Copy `templates/CLAUDE.md.template` to the project root as `CLAUDE.md` and replace `[PROJECT_NAME]` and `[DIRECTUS_URL]`.
