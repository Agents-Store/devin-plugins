---
name: api-reference
description: Next.js framework API quick reference — key functions, configuration options, and TypeScript types. This skill should be used when the user asks about "Next.js API", "Next.js functions", "next.config options", "generateMetadata API", "Next.js TypeScript types", or needs a quick lookup of Next.js framework APIs.
disable-model-invocation: true
---

# Next.js API Quick Reference

Curated reference of the most-used Next.js framework APIs. For the complete API reference, see the [official docs](https://nextjs.org/docs/app/api-reference).

## Navigation & Routing Functions

### `redirect(path, type?)`
Server-side redirect. Throws internally — do not wrap in try/catch.

```tsx
import { redirect } from 'next/navigation'

export default async function Page() {
  const session = await getSession()
  if (!session) redirect('/login')
  // ...
}
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `path` | string | Required | URL to redirect to |
| `type` | `'replace'` \| `'push'` | `'replace'` | Navigation type |

### `notFound()`
Trigger the nearest `not-found.tsx` boundary.

```tsx
import { notFound } from 'next/navigation'

export default async function Page({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params
  const post = await getPost(id)
  if (!post) notFound()
  return <div>{post.title}</div>
}
```

### `useRouter()` (Client Component only)
Programmatic navigation in Client Components.

```tsx
'use client'
import { useRouter } from 'next/navigation'

export default function Form() {
  const router = useRouter()
  // router.push('/dashboard')
  // router.replace('/login')
  // router.refresh()  — re-fetch server data without full page reload
  // router.back()
  // router.prefetch('/about')
}
```

### `usePathname()` (Client Component only)
Returns current pathname as a string.

### `useSearchParams()` (Client Component only)
Returns a read-only `URLSearchParams` object. Wrap in `<Suspense>` to avoid de-opting the entire page to client-side rendering.

## Request Functions (Server only)

### `cookies()`
Read and set cookies in Server Components, Server Actions, and Route Handlers.

```tsx
import { cookies } from 'next/headers'

export default async function Page() {
  const cookieStore = await cookies()
  const theme = cookieStore.get('theme')?.value
}
```

### `headers()`
Read request headers (read-only in Server Components).

```tsx
import { headers } from 'next/headers'

export default async function Page() {
  const headersList = await headers()
  const userAgent = headersList.get('user-agent')
}
```

## Metadata API

### Static Metadata

```tsx
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Page Title',
  description: 'Page description',
  openGraph: { title: 'OG Title', images: ['/og.png'] },
  robots: { index: true, follow: true },
}
```

### `generateMetadata()`

```tsx
import type { Metadata } from 'next'

export async function generateMetadata({
  params,
}: {
  params: Promise<{ id: string }>
}): Promise<Metadata> {
  const { id } = await params
  const post = await getPost(id)
  return { title: post.title, description: post.excerpt }
}
```

### `generateStaticParams()`

```tsx
export async function generateStaticParams() {
  const posts = await getPosts()
  return posts.map((post) => ({ id: post.id.toString() }))
}
```

## Cache & Revalidation

| Function | Import | Usage |
|----------|--------|-------|
| `revalidatePath(path, type?)` | `next/cache` | Invalidate cached data for a path. `type: 'layout'` revalidates all child pages |
| `revalidateTag(tag, profile)` | `next/cache` | SWR invalidation of tagged data. `profile` is a cacheLife profile name or `{ expire }` object; the single-argument form is deprecated in 16 |
| `updateTag(tag)` | `next/cache` | Server Actions only. Expire + immediate refresh in the same request (read-your-writes) |
| `refresh()` | `next/cache` | Server Actions only. Refresh uncached data; server-side counterpart of `router.refresh()` |

## Server Lifecycle & Auth Interrupts

- **`after(callback)`** from `next/server` (stable since 15.1) — run work after the response (or prerender) finishes. Usable in Server Components, Server Actions, Route Handlers, and Proxy. In Server Components, read `cookies()`/`headers()` **before** calling `after()` and close over the values — they cannot be read inside the callback.
- **`connection()`** from `next/server` — `await connection()` to mark rendering as dynamic before non-API dynamic work (e.g. `Math.random()`, `Date.now()`).
- **`forbidden()` / `unauthorized()`** from `next/navigation` with `forbidden.tsx`/`unauthorized.tsx` — render 403/401 pages. **Experimental** — require `experimental: { authInterrupts: true }` (still not stable in 16.3).

## Root Params (16.3)

`import { lang } from 'next/root-params'` — awaitable accessors for root dynamic segments (e.g. `app/[lang]/`), typed per segment, usable from any Server Component. Replaces `unstable_rootParams` (removed in 16.0).

For Image, Font, Script, next.config.ts, proxy API, cache functions with code examples, and advanced configuration, see [references/advanced-api.md](references/advanced-api.md).
