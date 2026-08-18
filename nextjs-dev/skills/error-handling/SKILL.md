---
name: error-handling
description: >
  Next.js error handling patterns and error boundaries. Use when the user asks about
  "error.tsx", "global-error.tsx", "not-found.tsx", "error boundaries", "error handling",
  "loading.tsx", "loading states", "fallback UI", "error recovery", "catchError",
  "retry", or needs guidance on graceful error handling in App Router applications.
---

# Error Handling

Next.js divides errors into two categories: **expected errors** (validation failures, not-found) and **uncaught exceptions** (bugs, crashes). Handle them differently.

## Expected Errors — Return Values, Not Exceptions

For expected errors (form validation, failed API calls), return error state instead of throwing:

### Server Actions with useActionState

```typescript
// app/actions.ts
'use server'

export async function createPost(prevState: any, formData: FormData) {
  const title = formData.get('title')
  const content = formData.get('content')

  const res = await fetch('https://api.example.com/posts', {
    method: 'POST',
    body: JSON.stringify({ title, content }),
  })
  const json = await res.json()

  if (!res.ok) {
    return { message: 'Failed to create post' }
  }

  // Success — redirect or return success state
}
```

```tsx
// app/ui/form.tsx
'use client'

import { useActionState } from 'react'
import { createPost } from '@/app/actions'

const initialState = { message: '' }

export function Form() {
  const [state, formAction, pending] = useActionState(createPost, initialState)

  return (
    <form action={formAction}>
      <label htmlFor="title">Title</label>
      <input type="text" id="title" name="title" required />
      <label htmlFor="content">Content</label>
      <textarea id="content" name="content" required />
      {state?.message && <p aria-live="polite">{state.message}</p>}
      <button disabled={pending}>Create Post</button>
    </form>
  )
}
```

### Server Components — Conditional Rendering

```tsx
// app/page.tsx
export default async function Page() {
  const res = await fetch('https://...')
  const data = await res.json()

  if (!res.ok) {
    return 'There was an error.'
  }

  return <div>{/* render data */}</div>
}
```

### Not Found — `notFound()` + `not-found.tsx`

Call `notFound()` in any route segment to trigger the nearest `not-found.tsx`:

```tsx
// app/blog/[slug]/page.tsx
import { notFound } from 'next/navigation'
import { getPostBySlug } from '@/lib/posts'

export default async function Page({
  params,
}: {
  params: Promise<{ slug: string }>
}) {
  const { slug } = await params
  const post = getPostBySlug(slug)

  if (!post) {
    notFound()
  }

  return <div>{post.title}</div>
}
```

```tsx
// app/blog/[slug]/not-found.tsx
export default function NotFound() {
  return <div>404 - Page Not Found</div>
}
```

You can also have a root-level `app/not-found.tsx` for all unmatched routes.

## Uncaught Exceptions — Error Boundaries

For unexpected errors (bugs), use `error.tsx` files that create React error boundaries.

### `error.tsx` — Route-Level Error Boundary

Place `error.tsx` in any route segment. It catches errors from that segment and its children:

```tsx
// app/dashboard/error.tsx
'use client' // Error boundaries must be Client Components

import { useEffect } from 'react'

export default function ErrorPage({
  error,
  retry,
}: {
  error: Error & { digest?: string }
  retry: () => void
}) {
  useEffect(() => {
    // Log the error to an error reporting service
    console.error(error)
  }, [error])

  return (
    <div>
      <h2>Something went wrong!</h2>
      <button onClick={() => retry()}>Try again</button>
    </div>
  )
}
```

**Key points:**
- Must be a Client Component (`'use client'`)
- `error.digest` — a hash of the error for server-side identification
- `retry()` — re-fetches data and re-renders the segment (`router.refresh()` + reset in a transition); stable in 16.3, named `unstable_retry` in 16.2. Preferred for recovery
- `reset()` still exists — use it to clear the error state without re-fetching data
- Errors bubble up to the nearest parent error boundary

### `global-error.tsx` — Root Error Boundary

Catches errors in the root layout. Must define its own `<html>` and `<body>`:

```tsx
// app/global-error.tsx
'use client'

export default function GlobalError({
  error,
  retry,
}: {
  error: Error & { digest?: string }
  retry: () => void
}) {
  return (
    <html>
      <body>
        <h2>Something went wrong!</h2>
        <button onClick={() => retry()}>Try again</button>
      </body>
    </html>
  )
}
```

### `catchError` — Component-Level Error Boundary

For granular error handling within a page (not at the route level). Stable since Next.js 16.3 (was `unstable_catchError` in 16.2):

```tsx
// app/custom-error-boundary.tsx
'use client'

import { catchError, type ErrorInfo } from 'next/error'

function ErrorFallback(
  props: { title: string },
  { error, retry }: ErrorInfo
) {
  return (
    <div>
      <h2>{props.title}</h2>
      <p>{error.message}</p>
      <button onClick={() => retry()}>Try again</button>
    </div>
  )
}

export default catchError(ErrorFallback)
```

`catchError` boundaries do not interfere with `notFound()`/`redirect()` and clear automatically on client navigation.

Use it as a wrapper in any layout or page:

```tsx
// app/dashboard/page.tsx
import ErrorBoundary from './custom-error-boundary'
import { DashboardWidget } from './widget'

export default function DashboardPage() {
  return (
    <div>
      <ErrorBoundary title="Widget Error">
        <DashboardWidget />
      </ErrorBoundary>
    </div>
  )
}
```

### Error Boundary Nesting

Errors bubble up to the nearest `error.tsx`:

```
app/
├── layout.tsx           # NOT caught by app/error.tsx
├── error.tsx            # Catches errors from page.tsx and children
├── page.tsx
└── dashboard/
    ├── error.tsx        # Catches dashboard errors first
    ├── page.tsx
    └── settings/
        └── page.tsx     # Error bubbles to dashboard/error.tsx
```

**Important:** `error.tsx` does NOT catch errors thrown in the same segment's `layout.tsx`. To catch layout errors, place `error.tsx` in the parent segment.

## Loading States — `loading.tsx`

Create instant loading UI with route-level Suspense:

```tsx
// app/dashboard/loading.tsx
export default function Loading() {
  return (
    <div className="animate-pulse">
      <div className="h-8 bg-gray-200 rounded w-1/4 mb-4" />
      <div className="h-64 bg-gray-200 rounded" />
    </div>
  )
}
```

`loading.tsx` wraps the `page.tsx` in a `<Suspense>` boundary automatically. The layout renders immediately while the page streams in.

## Event Handler Errors

Error boundaries only catch errors during rendering. For event handlers, catch manually:

```tsx
'use client'

import { useState } from 'react'

export function DeleteButton({ id }: { id: string }) {
  const [error, setError] = useState<string | null>(null)

  const handleDelete = async () => {
    try {
      await fetch(`/api/posts/${id}`, { method: 'DELETE' })
    } catch (e) {
      setError('Failed to delete')
    }
  }

  return (
    <>
      {error && <p className="text-red-500">{error}</p>}
      <button onClick={handleDelete}>Delete</button>
    </>
  )
}
```

**Exception:** errors inside `startTransition` (from `useTransition`) **do** bubble to the nearest error boundary.

## Decision Matrix

| Scenario | Pattern |
|----------|---------|
| Form validation failure | Return error from Server Action → `useActionState` |
| Resource not found | `notFound()` → `not-found.tsx` |
| API returns error response | Conditional rendering in Server Component |
| Unexpected crash in route | `error.tsx` boundary |
| Root layout crash | `global-error.tsx` |
| Crash in specific component | `catchError` wrapper |
| Event handler failure | `try/catch` + `useState` |
| Error logging | `useEffect` in `error.tsx` → send to Sentry/etc. |

## What This Skill Does NOT Cover

- HTTP error responses from Route Handlers (see `api-design`)
- Build-time errors and type errors (see `troubleshoot`)
- Form validation patterns in detail (see `form-handling`)
