# Cache Components & Instant Navigations (Next.js 16 / 16.3)

The Cache Components model makes caching fully explicit: Next.js 16 is dynamic-by-default (implicit `fetch` caching and the `experimental.ppr`/`dynamicIO` flags are gone), and everything cached is opted in with the `use cache` directive. Next.js 16.3 completes the model with Partial Prefetching for instant navigations.

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
| `'use cache: private'` | Per-user | Rare; runtime request data |

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
- `experimental.cachedNavigations` — cache full navigations

## Migration

Follow the official guide: [/docs/app/guides/migrating-to-cache-components](https://nextjs.org/docs/app/guides/migrating-to-cache-components). The upgrade codemod (`npx @next/codemod@canary upgrade latest` or `next upgrade`) handles most mechanical changes.
