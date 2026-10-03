---
name: deployment
description: This skill should be used when the user wants to "set up Docker for Directus with Next.js", "run Directus locally for a Next.js app", "configure content-change webhooks", "set up revalidation when Directus content changes", "auto-update the site on content change", "production checklist for Directus + Next.js", or needs the pipeline that connects Directus edits to Next.js pages and the checks before production. For platform-specific deployment (Vercel, Dokploy, etc.), see the respective deployment plugin.
---

# Deployment: Pipeline and Production Checklist

What connects the two systems when they run for real: the local setup, the path from an editor's save to a fresh page, and the list to check before production. Platform specifics (Vercel, Dokploy, Netlify) belong to the deployment plugin for that platform.

## Local Development

Run Directus with the Compose file of `directus-dev` → skill `docker-local-dev` (pinned 12.x image, PostgreSQL, Redis, loopback port, `LOCAL_` variables, liveness through `/server/ping`). The two values that tie it to this stack:

```bash
# Directus stack .env (docker-local-dev)
LOCAL_FRONTEND_ORIGIN=http://localhost:3000     # CORS, WebSockets and Live Preview accept the Next.js dev server

# Next.js .env.local
NEXT_PUBLIC_DIRECTUS_URL=http://localhost:8055  # the port you set in LOCAL_DIRECTUS_PORT
```

Verify with `curl http://localhost:8055/server/ping` (`pong`). The health endpoint answers `403` without a token in Directus 12; `/server/ping` is the liveness check.

## From an Editor's Save to a Fresh Page

```
editor saves in Directus
  -> Flow (event trigger, action) fires
  -> Flow Request operation: POST https://<app>/api/revalidate
       header x-revalidate-secret, body {"collection":"posts"}
  -> Route Handler checks the secret and the tag, calls revalidateTag(collection, { expire: 0 })
  -> the next visitor gets the new page
```

Each piece is taught where its tool lives:

| Piece | Where |
|-------|-------|
| Flow with a `request` operation, the secret in a header read from `$env` (`FLOWS_ENV_ALLOW_LIST`), where the request is made from | `directus-dev` → `flow-automation` → `references/notify-external-app.md` |
| The Route Handler (`/api/revalidate`): secret check, tag allow-list, `revalidateTag` | `nextjs-dev` → `data-fetching` → `references/headless-cms.md` |
| Which tag each Directus read carries | "Cache" in `directus-to-nextjs` |

Two things only the stack can tell you:

- **The names must agree.** A tag is a Directus collection name. The Flow lists collections, the Route Handler allows the same list, and `lib/content.ts` tags reads with them (including expanded relations: a post that embeds its author is tagged `posts` and `authors`). A collection missing from one of the three never refreshes.
- **`REVALIDATION_SECRET` lives in two places**: the Directus container (with `FLOWS_ENV_ALLOW_LIST`) and the Next.js hosting environment. Different values give `401` and a stale site, and nothing shows it unless the Flow logs its reject path (see `notify-external-app.md`).

Hosting platforms that rebuild on a deploy hook can use that hook as the Flow's URL instead; configure it through the platform's own plugin.

## Production Checklist

Directus:

- [ ] Image tag pinned to an exact 12.x version, not `latest`; `PUBLIC_URL` is the address editors open
- [ ] SSL in front of it. `IP_TRUST_PROXY` set when Directus sits behind a reverse proxy (default `false`)
- [ ] Persistent PostgreSQL with backups, and file storage that survives the container (volume or S3-compatible), backed up too
- [ ] The token in `DIRECTUS_ADMIN_TOKEN` belongs to a dedicated user with a narrow policy, not an administrator
- [ ] Public policy: only what the public site needs. If it reads `directus_files`, every file is downloadable and listable (see "Assets" in `directus-to-nextjs`)
- [ ] `CORS_ORIGIN` lists the exact production origin, only if browser code or WebSockets talk to Directus
- [ ] The license tier fits the features you use (SSO, custom permission rules). An instance that stays over its limits after the grace period loses GraphQL, WebSockets and MCP
- [ ] The revalidation Flow is active, lists every collection the pages read, and has its secret in `FLOWS_ENV_ALLOW_LIST`

Next.js:

- [ ] `next@^16.3.8`, Node 22 or later, `proxy.ts` (the middleware file is deprecated in Next.js 16)
- [ ] All variables set in the hosting platform: `NEXT_PUBLIC_DIRECTUS_URL`, `DIRECTUS_ADMIN_TOKEN`, their recipe aliases `DIRECTUS_URL`, `DIRECTUS_TOKEN` and `NEXT_PUBLIC_CMS_URL` (a platform may not expand `${...}` the way `.env.local` does, so give each name its value), the auth secrets, `REVALIDATION_SECRET`
- [ ] `images.remotePatterns` names the production Directus host with `pathname: '/assets/**'` (or `localPatterns` for the proxy route), and `dangerouslyAllowLocalIP` is off in production
- [ ] No token in any URL a browser sees (images, links, query strings)
- [ ] `/api/revalidate` rejects a wrong secret (`401`) and an unknown collection (`400`)
- [ ] `NEXTAUTH_SECRET` or `BETTER_AUTH_SECRET` is a strong random value, not the development placeholder
- [ ] `npx tsc --noEmit` passes in CI against the production schema
- [ ] After a first publish in Directus, the page changes within seconds. If not, check the Flow's reject-path log first
