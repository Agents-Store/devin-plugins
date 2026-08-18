---
name: data-fetching
description: Next.js data fetching, caching, and mutation patterns. This skill should be used when the user asks about "data fetching in Next.js", "Server Actions", "server-side data fetching", "caching strategies", "'use cache' directive", "revalidation", "ISR", "streaming with Suspense", "fetch in Server Components", or needs guidance on how to load and mutate data in Next.js App Router.
---

# Data Fetching, Caching & Mutations

Next.js App Router provides multiple approaches to fetch, cache, and mutate data. Server Components fetch data on the server by default. Server Actions handle mutations. The `use cache` directive (Next.js 16+) provides fine-grained caching control.

## Server Component Data Fetching

Fetch data directly in async Server Components. No `useEffect` or `getServerSideProps` needed:

```tsx
// app/posts/page.tsx — Server Component
export default async function PostsPage() {
  const posts = await db.post.findMany()

  return (
    <ul>
      {posts.map(post => (
        <li key={post.id}>{post.title}</li>
      ))}
    </ul>
  )
}
```

With the `fetch` API:

```tsx
export default async function Page() {
  const res = await fetch('https://api.example.com/posts')
  const posts = await res.json()
  return <PostList posts={posts} />
}
```

## Parallel vs Sequential Data Fetching

**Sequential** — requests run one after another (default when awaited inline):

```tsx
export default async function Page() {
  const user = await getUser()       // Waits for this...
  const posts = await getPosts(user.id)  // ...then this
  return <Profile user={user} posts={posts} />
}
```

**Parallel** — initiate all requests simultaneously with `Promise.all`:

```tsx
export default async function Page() {
  const [user, posts, comments] = await Promise.all([
    getUser(),
    getPosts(),
    getComments(),
  ])
  return <Dashboard user={user} posts={posts} comments={comments} />
}
```

Prefer parallel fetching when requests are independent. This reduces total loading time.

## Streaming with Suspense

Stream parts of the page as they become ready using `<Suspense>`:

```tsx
import { Suspense } from 'react'

export default function Page() {
  return (
    <div>
      <h1>Dashboard</h1>
      <Suspense fallback={<p>Loading analytics...</p>}>
        <Analytics />  {/* Streams in when ready */}
      </Suspense>
      <Suspense fallback={<p>Loading feed...</p>}>
        <ActivityFeed />  {/* Streams independently */}
      </Suspense>
    </div>
  )
}
```

Alternatively, use `loading.tsx` for route-level loading states (automatically wraps the page in `<Suspense>`).

### Suspense Key Pattern for Dynamic Content

When content depends on URL parameters (search, pagination), use the `key` prop to force Suspense to re-show the fallback when params change. Without this, stale content stays visible while new data loads:

```tsx
// app/users/page.tsx
export default async function UsersPage({
  searchParams,
}: {
  searchParams: Promise<{ q?: string; page?: string }>
}) {
  const { q, page } = await searchParams

  return (
    <div>
      <SearchInput defaultValue={q} />
      {/* key changes → Suspense remounts → fallback shows → fresh data streams in */}
      <Suspense key={`${q}-${page}`} fallback={<TableSkeleton />}>
        <UserTable query={q} page={Number(page) || 1} />
      </Suspense>
    </div>
  )
}
```

Use the `use` API to stream data from Server to Client Components:

```tsx
// app/page.tsx — Server Component
import { Posts } from './posts'

export default function Page() {
  const postsPromise = getPosts()  // Start fetch, don't await
  return <Posts postsPromise={postsPromise} />
}
```

```tsx
// app/posts.tsx — Client Component
'use client'

import { use } from 'react'

export function Posts({ postsPromise }: { postsPromise: Promise<Post[]> }) {
  const posts = use(postsPromise)  // Suspends until resolved
  return <ul>{posts.map(p => <li key={p.id}>{p.title}</li>)}</ul>
}
```

## Server Actions & Mutations

> For form validation with Zod, `useActionState` patterns, `useFormStatus`, and optimistic UI, see the `form-handling` skill.

Define server-side mutations with `'use server'`:

```tsx
// app/actions.ts
'use server'

import { revalidatePath } from 'next/cache'
import { redirect } from 'next/navigation'

export async function createPost(formData: FormData) {
  const title = formData.get('title') as string
  const content = formData.get('content') as string

  await db.post.create({ data: { title, content } })

  revalidatePath('/posts')
  redirect('/posts')
}
```

Use in forms (progressive enhancement — works without JavaScript):

```tsx
// app/posts/new/page.tsx
import { createPost } from '../actions'

export default function NewPostPage() {
  return (
    <form action={createPost}>
      <input name="title" required />
      <textarea name="content" required />
      <button type="submit">Create Post</button>
    </form>
  )
}
```

Use in Client Components for programmatic mutations:

```tsx
'use client'

import { createPost } from '../actions'
import { useActionState } from 'react'

export function CreatePostForm() {
  const [state, formAction, pending] = useActionState(createPost, null)

  return (
    <form action={formAction}>
      <input name="title" required />
      <button type="submit" disabled={pending}>
        {pending ? 'Creating...' : 'Create'}
      </button>
    </form>
  )
}
```

## Revalidation Strategies

### Path-based Revalidation

Invalidate all cached data for a specific route:

```tsx
'use server'
import { revalidatePath } from 'next/cache'

export async function updatePost(id: string, data: FormData) {
  await db.post.update({ where: { id }, data: { /* ... */ } })
  revalidatePath('/posts')         // Revalidate the list
  revalidatePath(`/posts/${id}`)   // Revalidate the specific page
}
```

### Tag-based Revalidation

Revalidate specific data across multiple routes. Tag-based revalidation is more precise than path-based or time-based approaches — it invalidates exactly the cached entries you need without re-rendering unrelated content:

```tsx
// lib/data.ts — tag each fetch with a resource-specific tag
export async function getPost(id: string) {
  const res = await fetch(`https://api.example.com/posts/${id}`, {
    next: { tags: [`post-${id}`, 'posts'] },
  })
  return res.json()
}
```

```tsx
// lib/actions.ts — after mutation, invalidate only the affected tag
'use server'
import { revalidateTag } from 'next/cache'

export async function updatePost(id: string, formData: FormData) {
  await db.post.update({ where: { id }, data: { /* ... */ } })
  revalidateTag(`post-${id}`, 'max')  // Only this post's cache is busted
}
```

> Since Next.js 16, the single-argument `revalidateTag(tag)` form is **deprecated**. The second argument is a cacheLife profile (`'max'` recommended, or `'hours'`/`'days'`/a custom profile/an inline `{ expire: 3600 }` object) that enables stale-while-revalidate behavior.

### `updateTag()` and `refresh()` (Next.js 16, Server Actions only)

Two Server-Actions-only APIs from `next/cache` complement `revalidateTag`:

```tsx
'use server'
import { updateTag, refresh } from 'next/cache'

export async function updatePost(id: string, formData: FormData) {
  await db.post.update({ where: { id }, data: { /* ... */ } })
  updateTag(`post-${id}`)  // Expire AND re-read fresh data in the same request
}
```

- `updateTag(tag)` — expires the tag **and** reads fresh data within the same request (read-your-writes). Use for form mutations where the user must see their change immediately — this supersedes bare `revalidateTag` in most Server Action examples.
- `refresh()` — refreshes only uncached data; the server-side counterpart of `router.refresh()`.

**When to use which revalidation:**
- `updateTag()` — Server Action mutations where the user must immediately see their own change (read-your-writes)
- `revalidateTag(tag, profile)` — surgical SWR invalidation of specific data across all routes that use it
- `refresh()` — re-fetch uncached data from a Server Action without touching the cache
- `revalidatePath()` — broader, invalidates all cached data for a specific URL path
- `export const revalidate = N` — background regeneration on a timer (ISR), no mutation trigger needed

Prefer tag-based revalidation for mutations because it's precise. Use `revalidatePath` when you need to refresh an entire page. Use ISR when data changes externally (not via your app's mutations).

### Time-based Revalidation (ISR)

Automatically regenerate pages at a set interval:

```tsx
// app/posts/page.tsx
export const revalidate = 60  // Revalidate every 60 seconds

export default async function PostsPage() {
  const posts = await getPosts()
  return <PostList posts={posts} />
}
```

## `use cache` Directive (Next.js 16+)

Cache Components let you cache at the function or component level. **Prerequisite:** `use cache` only works with Cache Components enabled in `next.config.ts` — the examples below fail without it:

```ts
// next.config.ts
import type { NextConfig } from 'next'

const nextConfig: NextConfig = {
  cacheComponents: true,
}

export default nextConfig
```

Constraints: all cached functions/components must be `async`, and `cookies()`/`headers()`/`searchParams` cannot be read inside a cached scope (read them outside and pass the values as arguments — otherwise you get a `next-request-in-use-cache` error).

Variants: `'use cache: remote'` stores entries in the platform cache handler (e.g. Redis/KV) so they survive across serverless instances; `'use cache: private'` is a rare variant for runtime request data. The default in-memory runtime cache does **not** persist across serverless requests.

> For the full Cache Components model — cache keys, profiles, Partial Prefetching, new ISR behavior, and migration — see [references/cache-components.md](references/cache-components.md).

### Data-level Caching

```tsx
'use cache'

export async function getUser(id: string) {
  const user = await db.user.findUnique({ where: { id } })
  return user
}
```

### Component-level Caching

```tsx
'use cache'

export default async function UserProfile({ id }: { id: string }) {
  const user = await db.user.findUnique({ where: { id } })
  return <div>{user.name}</div>
}
```

### Cache with Lifetime

```tsx
import { cacheLife } from 'next/cache'

export async function getProducts() {
  'use cache'
  cacheLife('hours')
  const products = await db.product.findMany()
  return products
}
```

Cache lifetime profiles: `'default'`, `'seconds'`, `'minutes'`, `'hours'`, `'days'`, `'weeks'`, `'max'`.

### Cache with Tags

```tsx
import { cacheTag } from 'next/cache'

export async function getPost(id: string) {
  'use cache'
  cacheTag(`post-${id}`, 'posts')
  const post = await db.post.findUnique({ where: { id } })
  return post
}
```

## Request Memoization

React automatically memoizes `fetch` calls with the same URL and options during a single render pass. For non-fetch functions, use `React.cache`:

```tsx
import { cache } from 'react'

export const getUser = cache(async (id: string) => {
  const user = await db.user.findUnique({ where: { id } })
  return user
})
```

Now multiple components calling `getUser('123')` in the same request only execute the query once.

## Optimistic UI with Server Actions

Update the UI immediately before the server confirms, then roll back on failure. This makes mutations feel instant:

```tsx
// components/like-button.tsx
'use client'

import { useState, useTransition } from 'react'
import { likePost } from '@/lib/actions'

export function LikeButton({ postId, initialLikes }: { postId: string; initialLikes: number }) {
  const [likes, setLikes] = useState(initialLikes)
  const [isPending, startTransition] = useTransition()

  function handleLike() {
    setLikes(prev => prev + 1)  // Optimistic update — instant feedback
    startTransition(async () => {
      try {
        await likePost(postId)
      } catch {
        setLikes(prev => prev - 1)  // Rollback on failure
      }
    })
  }

  return (
    <button onClick={handleLike} disabled={isPending}>
      {likes} likes
    </button>
  )
}
```

```tsx
// lib/actions.ts
'use server'
import { updateTag } from 'next/cache'

export async function likePost(postId: string) {
  await db.post.update({ where: { id: postId }, data: { likes: { increment: 1 } } })
  updateTag(`post-${postId}`)  // read-your-writes: the user sees the new count immediately
}
```

The pattern: update local state first, fire the Server Action in a transition, revert if it fails. The Server Action handles revalidation so subsequent page loads reflect the real value.

For forms, `useOptimistic` (React 19) provides a similar pattern:

```tsx
'use client'
import { useOptimistic } from 'react'

function TodoList({ todos, addTodo }: { todos: Todo[]; addTodo: (text: string) => Promise<void> }) {
  const [optimisticTodos, addOptimistic] = useOptimistic(
    todos,
    (state, newTodo: string) => [...state, { id: 'temp', text: newTodo, pending: true }]
  )

  async function handleSubmit(formData: FormData) {
    const text = formData.get('text') as string
    addOptimistic(text)
    await addTodo(text)
  }

  return (
    <form action={handleSubmit}>
      <input name="text" />
      <ul>{optimisticTodos.map(t => <li key={t.id} style={{ opacity: t.pending ? 0.5 : 1 }}>{t.text}</li>)}</ul>
    </form>
  )
}
```

## Rendering Strategy Summary

| Strategy | When | How |
|----------|------|-----|
| Static (SSG) | Content rarely changes | Default for pages without dynamic data |
| ISR | Semi-dynamic content | `export const revalidate = 60` |
| Dynamic (SSR) | Per-request data | Use `cookies()`, `headers()`, or `searchParams` |
| Streaming | Progressive loading | `<Suspense>` boundaries or `loading.tsx` |
| Cache Components (`use cache`, 16+) | Fine-grained cache control | Opt in via `cacheComponents: true`, then `'use cache'` + `cacheLife()` + `cacheTag()` |

Next.js 16 is dynamic-by-default — implicit `fetch` caching was removed, so caching is always explicit. 16.3 adds `partialPrefetching: true` as the second flag of the Instant Navigations model (see [references/cache-components.md](references/cache-components.md)).
