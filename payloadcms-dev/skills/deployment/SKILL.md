---
name: deployment
description: This skill should be used when the user asks to "deploy Payload to production", "deploy Payload to Vercel", "dockerize a Payload app", "build without a database connection", "add rate limiting", "prevent API abuse", "optimize Payload performance", or "configure serverless database connections". Covers the production build, Vercel and Docker/Node self-host targets, building without a live DB, locking down REST/GraphQL, and query performance.
---

# PayloadCMS — Production & Deployment

Ship a PayloadCMS v3 app to production. Payload runs anywhere Next.js runs — it is a Next.js app, so `next build` is the build. This skill covers the production build, deploy targets, building without a DB connection, hardening the API against abuse, and query performance.

## 1. Production build

Payload's build is Next.js's build. The scaffolder wires `package.json` so `pnpm build` runs `next build`:

```bash
# Standard production build
pnpm build         # → next build
pnpm start         # → next start  (serves the .next output)
```

Required environment in every production environment:

```bash
# .env (production)
PAYLOAD_SECRET=<long-random-string>           # signs JWTs/tokens — keep stable, never commit
DATABASE_URI=postgres://user:pass@host:5432/db
NEXT_PUBLIC_SERVER_URL=https://cms.example.com
NODE_ENV=production
```

`PAYLOAD_SECRET` must be long and impossible to guess — rotating it logs every user out and invalidates reset tokens. Set `serverURL` in the config (absolute, protocol + domain, no path) so emails, previews, and CORS resolve correctly:

```ts
// src/payload.config.ts
export default buildConfig({
  serverURL: process.env.NEXT_PUBLIC_SERVER_URL,
  // …
})
```

Before deploying: turn off schema auto-sync and run migrations instead (`push: false` on Postgres/SQLite — see `cli-recipes` for `migrate` in CI/CD), and confirm cookies are secure when behind SSL.

## 2. Deploy targets

| Target | DB | File storage | Watch out for |
|--------|----|--------------|---------------|
| **Vercel / serverless** | External, pooled (PgBouncer, Neon, Vercel Postgres) | **Cloud adapter required** (S3/R2/Blob) — local FS is ephemeral | Function timeouts; connection exhaustion; cold starts |
| **Docker / Node self-host** | Any reachable DB | Cloud adapter or persistent volume | `output: 'standalone'`; non-root user; `sharp` in runner |
| **Payload Cloud** | Managed | Managed | Push-to-deploy; least config |

### Vercel & serverless

Serverless functions are short-lived and run concurrently, so two rules are non-negotiable:

- **File storage must be a cloud adapter.** The default writes uploads to disk, which vanishes between invocations. Use `@payloadcms/storage-s3`, `storage-vercel-blob`, etc. — see the `adapters` skill.
- **Pool the database.** Each function instance opens its own connection; without pooling you exhaust `max_connections` fast. Front Postgres with a pooler (PgBouncer in transaction mode, Neon's pooled endpoint, Supabase pooler) and point `DATABASE_URI` at the pooled port. MongoDB Atlas pools via the driver but still cap `maxPoolSize` low per instance.

Mind function execution limits — long imports, heavy `depth`, or big migrations can exceed the platform timeout. Run those out-of-band (a job/queue or a one-off Node task), not in a request.

### Docker / Node self-host

Set standalone output so the image ships only the runtime files:

```js
// next.config.mjs
const nextConfig = { output: 'standalone' }
export default nextConfig
```

A representative multi-stage Dockerfile (mirrors the official template):

```dockerfile
# Dockerfile
FROM node:22-alpine AS base

FROM base AS deps
RUN apk add --no-cache libc6-compat
WORKDIR /app
COPY package.json pnpm-lock.yaml* ./
RUN corepack enable pnpm && pnpm i --frozen-lockfile

FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
ENV NODE_ENV=production
RUN corepack enable pnpm && pnpm build      # → next build (output: standalone)

FROM base AS runner
WORKDIR /app
ENV NODE_ENV=production
RUN addgroup --system --gid 1001 nodejs \
 && adduser  --system --uid 1001 nextjs
COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static
USER nextjs
EXPOSE 3000
ENV HOSTNAME="0.0.0.0" PORT=3000
CMD ["node", "server.js"]
```

Pass `PAYLOAD_SECRET`, `DATABASE_URI`, and `NEXT_PUBLIC_SERVER_URL` at runtime (compose `environment:`, `--env-file`, or your orchestrator's secrets). On Alpine, `libc6-compat` covers native deps; if image optimization fails in standalone mode, install `sharp` in the runner stage. With a persistent volume you may keep local file storage, but a cloud storage adapter is still the safer default.

### Payload Cloud

Payload Cloud is the first-party managed host: connect a repo, push to deploy, and the DB plus file storage are provisioned for you. Lowest-config path when you don't want to manage infrastructure.

## 3. Building without a DB connection

`next build` runs static generation, which can hit your database. In CI/CD — or any build environment with no DB reachable — compile without generating static pages using the Next.js build-mode flag (there is no Payload-specific env var for this):

```bash
# Compile only — no static generation, no DB connection needed
pnpm next build --experimental-build-mode compile
```

Caveat: in `compile` mode, `NEXT_PUBLIC_*` vars are **not** inlined and read as `undefined` on the client. Resolve it one of two ways once a DB *is* reachable (e.g., at container start):

```bash
pnpm next build --experimental-build-mode generate       # generate static pages + inline env
pnpm next build --experimental-build-mode generate-env    # inline NEXT_PUBLIC_* env only
```

Alternatively, mark routes that would otherwise statically render with `export const dynamic = 'force-dynamic'` — this avoids the build-time DB hit but disables static optimization, so pages render slower.

## 4. Preventing API abuse

Payload v3 ships several config-level knobs. **Note:** the old top-level `rateLimit` config from v2 was removed in v3 — do request rate limiting in **Next.js middleware** or at a reverse proxy/CDN (Cloudflare, nginx `limit_req`), or with a package like `rate-limiter-flexible` keyed on the client IP. Don't add a `rateLimit` block to `buildConfig` — it is no longer a valid option.

| Knob | Where | Effect |
|------|-------|--------|
| `maxDepth` | Config | Caps relationship traversal app-wide (default `10`) — stops runaway circular populate |
| `defaultDepth` | Config | Depth used when a request omits `depth` |
| `graphQL.disable: true` | Config | Removes the GraphQL endpoint entirely |
| `graphQL.maxComplexity` | Config | Rejects over-complex GraphQL queries (relationship/upload fields cost 10) |
| `maxLoginAttempts` / `lockTime` | Auth collection | Locks an account after N failed logins |
| `access` | Collection/global/field | The real lock — gates every REST/GraphQL operation |
| `disable` | Collection endpoints | Removes auto-generated REST/GraphQL operations you don't expose |

- **Lock down with access control first.** Auto-generated REST and GraphQL endpoints obey each collection's `access` functions. An endpoint with no access restriction is open — test every `read`/`create`/`update`/`delete` function before going live (see the `access-control` skill).
- **Disable GraphQL in production if unused.** Set `graphQL.disable: true` to drop the endpoint, or `graphQL.maxComplexity` to bound query cost. The GraphQL playground is not served in production builds.
- **Keep `maxDepth` low.** It is the guardrail against malicious deep-populate queries that time out the server.
- **Harden auth and uploads.** Set `maxLoginAttempts`/`lockTime` on auth collections; restrict `create`/`update`/`read` on upload collections and consider antivirus scanning in a hook.

## 5. Performance

- **Index queried fields.** Add `index: true` to any field used in `where` filters or sorts to avoid full scans. Compound queries benefit from indexes on each leg.
- **Discipline `depth`.** Every level of `depth` is another round of joins/lookups. Request the lowest depth a view needs; combine with `select` to fetch only required fields.
- **Use `select` and `populate`/`defaultPopulate`.** `select` trims returned fields; `defaultPopulate` on a relationship collection controls which of its fields get pulled when populated elsewhere — both shrink payloads and DB load.
- **Paginate.** Keep `limit` modest; pass `pagination: false` only for deliberate full exports. Skip the count query with `disableCount` when you don't render a total.
- **Avoid N+1 in hooks.** Don't loop a `payload.find` per document inside a hook — batch with a single `where: { id: { in: [...] } }`. Thread `req` so nested ops reuse the transaction (see `adapters`). For hot paths, `payload.db.*` methods bypass hooks/validation: `await payload.db.updateOne({ collection, id, data, returning: false })`.
- **Reuse the Payload instance.** Call `const payload = await getPayload({ config })` — it caches and reuses one instance; never instantiate per request.
- **Cache at the framework layer.** Use Next.js ISR / `revalidate` / `revalidateTag` for read-heavy frontend pages instead of hitting Payload on every request — see `nextjs-integration`.

<example>
Production-hardened config excerpt — low depth, capped GraphQL, absolute URL:

```ts
// src/payload.config.ts
import { buildConfig } from 'payload'

export default buildConfig({
  serverURL: process.env.NEXT_PUBLIC_SERVER_URL,
  secret: process.env.PAYLOAD_SECRET || '',
  maxDepth: 5,                 // guardrail against deep-populate abuse
  defaultDepth: 1,             // shallow by default; callers opt into more
  graphQL: {
    disable: process.env.NODE_ENV === 'production' && !process.env.ENABLE_GRAPHQL,
    maxComplexity: 1000,       // reject over-complex queries when enabled
  },
  cors: [process.env.NEXT_PUBLIC_SERVER_URL || ''],
  csrf: [process.env.NEXT_PUBLIC_SERVER_URL || ''],
  // db / collections / editor / storage omitted — see `adapters`
})
```

(Rate limiting is intentionally absent here — do it in Next.js middleware or a proxy, not in `buildConfig`.)
</example>

<example>
CI build with no DB reachable, then generate static pages at container start:

```bash
# CI: compile only — no DATABASE_URI needed
pnpm next build --experimental-build-mode compile

# Runtime entrypoint (DB now reachable): finish static generation
pnpm next build --experimental-build-mode generate
node .next/standalone/server.js
```
</example>

## What this skill does NOT cover

- **Scaffolding a project, env basics, `PAYLOAD_SECRET` generation** — see the `setup` skill.
- **Database / storage / email adapter config, connection pooling specifics, transactions** — see the `adapters` skill.
- **ISR, `revalidate`, `revalidateTag`, caching at the Next.js layer** — see the `nextjs-integration` skill.
- **`migrate:create` / `migrate` in CI/CD, `push: false` workflow** — see the `cli-recipes` skill.
- **`depth`, `select`, `where`, and query construction in detail** — see the `queries` skill.
