# Cache Components & Instant Navigations (Next.js 16 / 16.3)

The Cache Components model makes caching fully explicit: Next.js 16 is dynamic-by-default (implicit `fetch` caching and the `experimental.ppr`/`dynamicIO` flags are gone), and everything cached is opted in with the `use cache` directive. Next.js 16.3 completes the model with Partial Prefetching for instant navigations.

> **Security floor:** `next@16.3.8` fixes two Cache Components leaks — a pending `use cache` fill could hand Draft Mode content to regular requests (and persist it into prerendered pages), and a nested `'use cache'` function that reads a root param could be keyed without that param. If you use `cacheComponents`, stay on `^16.3.8` or later.

## Configuration

```ts
// next.config.ts
import type { NextConfig } from 'next'

const nextConfig: NextConfig = {
  cacheComponents: true,      // enables `use cache` (Next.js 16+)
  partialPrefetching: true,   // Instant Navigations suite (16.3+)
}

export default nextConfig
```

## `use cache` Placement

The directive works at three levels:

```tsx
// Route level — top of a page/layout file
'use cache'
export default async function Page() { /* whole route segment cached */ }

// Component level
export async function ProductCard({ id }: { id: string }) {
  'use cache'
  const product = await getProduct(id)
  return <div>{product.name}</div>
}

// Function level
export async function getProducts() {
  'use cache'
  return db.product.findMany()
}
```

Rules:
- Cached functions/components must be `async`.
- **Cache keys** are derived from the serialized arguments/props plus the build ID and function identity. Same inputs → same cache entry.
- `cookies()`, `headers()`, and `searchParams` cannot be read inside a cached scope — read them outside and pass values as arguments (`next-request-in-use-cache` error otherwise).
- Non-serializable values (functions, JSX children) pass through the cache boundary without becoming part of the key.

## Variants

| Directive | Storage | Use for |
|-----------|---------|---------|
| `'use cache'` | In-memory runtime cache (does not persist across serverless instances) | Default; most data |
| `'use cache: remote'` | Platform cache handler (e.g. Redis/KV) | Data that must survive across serverless instances/deploy targets |
| `'use cache: private'` | Browser only — never stored on the server | Rare; cache a function that reads `cookies()`/`headers()`. Cannot be part of the static shell; to ride in the App Shell its `stale` must be at least 5 minutes |

## cacheLife Profiles

```tsx
import { cacheLife } from 'next/cache'

export async function getProducts() {
  'use cache'
  cacheLife('hours')
  return db.product.findMany()
}
```

| Profile | Stale (client) | Revalidate | Expire |
|---------|----------------|------------|--------|
| `default` | 5 minutes | 15 minutes | never |
| `seconds` | 30 seconds | 1 second | 1 minute |
| `minutes` | 5 minutes | 1 minute | 1 hour |
| `hours` | 5 minutes | 1 hour | 1 day |
| `days` | 5 minutes | 1 day | 1 week |
| `weeks` | 5 minutes | 1 week | 30 days |
| `max` | 5 minutes | 30 days | 1 year |

Custom profiles are declared in `next.config.ts`:

```ts
const nextConfig: NextConfig = {
  cacheComponents: true,
  cacheLife: {
    biweekly: { stale: 60 * 60 * 24 * 14, revalidate: 60 * 60 * 24, expire: 60 * 60 * 24 * 14 },
  },
}
```

## Invalidation

```tsx
import { cacheTag } from 'next/cache'

export async function getPost(id: string) {
  'use cache'
  cacheTag(`post-${id}`, 'posts')
  return db.post.findUnique({ where: { id } })
}
```

| API | Where | Behavior |
|-----|-------|----------|
| `updateTag(tag)` | Server Actions only | Expire + immediately re-read fresh data in the same request (read-your-writes) — preferred for form mutations |
| `revalidateTag(tag, profile)` | Server Actions, Route Handlers | SWR invalidation; profile is a cacheLife name or `{ expire }` object (single-arg form deprecated in 16) |
| `refresh()` | Server Actions only | Refresh uncached data only; server-side counterpart of `router.refresh()` |

## New ISR Behavior (16.3)

With `cacheComponents` enabled, pages with `generateStaticParams` gain an instant loading shell for params that were **not** prerendered: the visitor immediately gets the static shell while the dynamic content streams in, and the result is upgraded to a fully static page in the background for subsequent visitors.

## Partial Prefetching (16.3)

With both flags enabled, `<Link prefetch={true}>` prefetches the cached (static) parts of the destination ahead of navigation, so navigations render instantly and only dynamic holes stream in. Supporting pieces of the Instant Navigations suite:

- **Instant Insights + Navigation Inspector** — devtools panels showing what is instant and why
- `@next/playwright` — `instant()` test helper to assert instant navigations in E2E tests (see the `testing-patterns` skill)
- `experimental.useOffline` + `useOffline()` from `'next/offline'` — detect offline state
- `experimental.cachedNavigations` — turned on automatically together with `cacheComponents`; it is not in the public docs, so do not set it by hand

## Route Segment Config Under Cache Components

With `cacheComponents: true`, the previous-model route segment options are removed (version history `v16.0.0` of the Route Segment Config reference). Delete them and use the Cache Components equivalent:

| Previous model (route segment config) | With `cacheComponents: true` |
|---|---|
| `export const dynamic = 'force-dynamic'` (`cacheComponents` off) | Delete it — everything is dynamic by default. Wrap request-time readers (`cookies()`, `headers()`, `searchParams`, uncached `fetch`) in `<Suspense>` |
| `export const dynamic = 'force-static'` (`cacheComponents` off) | Delete it; add `'use cache'` + `cacheLife('max')` as close to the data access as possible |
| `export const revalidate = 3600` (`cacheComponents` off) | `'use cache'` + `cacheLife('hours')` (or a custom profile / `{ stale, revalidate, expire }`) |
| `export const fetchCache = '...'` (`cacheComponents` off) | Delete it; `'use cache'` captures the `fetch` results inside its scope |
| `export const dynamicParams = false` (`cacheComponents` off) | Delete it — the build fails with `Route segment config "dynamicParams" is not compatible with nextConfig.cacheComponents`. Call `notFound()` when the param does not resolve to real data |
| `export const experimental_ppr = true` (`cacheComponents` off) | Removed in 16.0 — Partial Prerendering is part of Cache Components |

Still valid under Cache Components: `runtime`, `preferredRegion`, `maxDuration`, and the new `instant` and `prefetch` options. Two more rules change with the flag:

- `generateStaticParams` must return at least one param (an empty array raises `empty-generate-static-params`); params you do not return still get a static shell and stream the rest.
- Await `params` / `searchParams` inside a `<Suspense>` boundary (pass the promise down) so the shell can prerender.

Before/after for the most common case:

```tsx
// Before — previous model, cacheComponents off (this export is removed when it is on)
export const revalidate = 3600

export default async function Page() {
  const posts = await getPosts()
  return <PostList posts={posts} />
}
```

```tsx
// After — Cache Components (cacheComponents: true)
import { cacheLife } from 'next/cache'

export default async function Page() {
  'use cache'
  cacheLife('hours')
  const posts = await getPosts()
  return <PostList posts={posts} />
}
```

Reference: [Caching and Revalidating (Previous Model)](https://nextjs.org/docs/app/guides/caching-without-cache-components) for projects that stay on the old model, [Migrating to Cache Components](https://nextjs.org/docs/app/guides/migrating-to-cache-components) for the move.

## Request-time Values: `io()` (16.3)

Under `cacheComponents`, a synchronous read such as `new Date()`, `Math.random()` or `crypto.randomUUID()` during prerender is a build error: decide whether the value is captured once in the static shell (wrap in `'use cache'`) or produced per request (`await io()` from `next/cache`, inside a `<Suspense>` boundary):

```tsx
import { Suspense } from 'react'
import { io } from 'next/cache'

export default function Page() {
  return (
    <Suspense fallback={<p>Loading...</p>}>
      <CurrentTime />
    </Suspense>
  )
}

async function CurrentTime() {
  await io()  // keeps the value out of the static shell
  return <p>{new Date().toISOString()}</p>
}
```

In a Client Component call `use(io())` before the read. `io()` is a no-op inside cached scopes, in the browser, and without Cache Components. Prefer it over `connection()`: `connection()` waits for a real user request and therefore also blocks prefetches, while code after `io()` can still be wrapped in `'use cache'` and prefetched.

## Instant Navigations: `instant` and Instant Insights (16.3)

The `instant` segment config tells Next.js to validate that navigating into a segment renders a UI immediately (dev-time validation; only works with `cacheComponents`, not in Client Components):

```tsx
// layout.tsx | page.tsx
export const instant = true     // validate this segment
// export const instant = false // opt out: this segment is allowed to block
```

Instant Insights report each blocking read with three labelled fixes: stream it behind `<Suspense>`, cache it with `'use cache'`, or block the route with `instant = false`. `experimental.instantInsights.validationLevel` is `'warning'` by default (every Page and Default segment is validated in dev); set `'manual-warning'` to validate only segments that export `instant`.

## Per-link Prefetching and the `prefetch` Segment Config (16.3)

With `partialPrefetching`, every `<Link>` prefetches only the destination's shared App Shell. `<Link prefetch={true}>` additionally resolves cached content that depends on the link's URL (`params`, `searchParams`) before the click — use it for a few high-intent links, not a whole grid (each one can wake the server). `<Link prefetch={false}>` still disables prefetching for that link. Per segment, `export const prefetch = 'partial'` opts the destination into Partial Prefetching without the global flag, and `'force-disabled'` stops its segment data from being prefetched. Existing `prefetch={true}` links used the legacy full prefetch and change behavior when the flag is enabled; the [Adopting Partial Prefetching](https://nextjs.org/docs/app/guides/adopting-partial-prefetching) guide covers the migration (including the older `unstable_eager` option).

## Migration

Follow the official guide: [/docs/app/guides/migrating-to-cache-components](https://nextjs.org/docs/app/guides/migrating-to-cache-components). The upgrade codemod (`npx @next/codemod@canary upgrade latest` or `next upgrade`) handles most mechanical changes.
