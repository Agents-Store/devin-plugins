---
name: app-router-patterns
description: Next.js App Router patterns and file conventions. This skill should be used when the user asks about "Next.js routing", "App Router", "layouts and pages", "route groups", "parallel routes", "intercepting routes", "proxy", "metadata", "route handlers", or needs guidance on Next.js file-based routing architecture.
---

# Next.js App Router Patterns

The App Router is the standard routing system in Next.js. It uses a file-system based approach where folders define routes and special files define UI.

## File Conventions

Every route segment can define these special files:

| File | Purpose | Required |
|------|---------|----------|
| `page.tsx` | Unique UI for this route, makes route publicly accessible | Yes (for route to be accessible) |
| `layout.tsx` | Shared UI that wraps this segment and children | Yes (root layout required) |
| `loading.tsx` | Loading UI shown while page is loading (wraps in `<Suspense>`) | No |
| `error.tsx` | Error boundary for this segment and children | No |
| `not-found.tsx` | 404 UI when `notFound()` is called | No |
| `template.tsx` | Like layout but remounts on navigation (new instance each time) | No |
| `default.tsx` | Fallback for parallel routes when no match | Yes (in every parallel route slot, since 16) |
| `route.ts` | API endpoint (cannot coexist with `page.tsx` in same segment) | No |

> For detailed error handling, loading state, and not-found patterns, see the `error-handling` skill. For Route Handler design patterns, see `api-design`.

## Root Layout (Required)

Every Next.js app must have a root `app/layout.tsx`. It replaces `_app.tsx` and `_document.tsx`:

```tsx
export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
```

The root layout must define `<html>` and `<body>` tags. It is a Server Component by default and cannot be made a Client Component.

## Nested Layouts

Layouts nest automatically. A layout in `app/dashboard/layout.tsx` wraps all pages under `/dashboard/*`:

```
app/
├── layout.tsx          # Root layout
├── page.tsx            # Home /
└── dashboard/
    ├── layout.tsx      # Dashboard layout (wraps all dashboard pages)
    ├── page.tsx        # /dashboard
    ├── settings/
    │   └── page.tsx    # /dashboard/settings
    └── analytics/
        └── page.tsx    # /dashboard/analytics
```

Layouts preserve state and do not re-render on navigation between child routes. Use `template.tsx` instead when you need remounting.

## Route Groups

Organize routes without affecting the URL path using `(folderName)`:

```
app/
├── (marketing)/
│   ├── layout.tsx      # Marketing-specific layout
│   ├── about/page.tsx  # /about
│   └── blog/page.tsx   # /blog
├── (shop)/
│   ├── layout.tsx      # Shop-specific layout
│   ├── products/page.tsx  # /products
│   └── cart/page.tsx      # /cart
└── layout.tsx          # Root layout
```

Use route groups to:
- Organize routes by concern without affecting URL
- Apply different layouts to different groups
- Create multiple root layouts (each group can have its own root layout)

## Dynamic Routes

Use square brackets for dynamic segments:

| Pattern | Example | Matches |
|---------|---------|---------|
| `[id]` | `app/blog/[id]/page.tsx` | `/blog/1`, `/blog/abc` |
| `[...slug]` | `app/docs/[...slug]/page.tsx` | `/docs/a`, `/docs/a/b/c` |
| `[[...slug]]` | `app/docs/[[...slug]]/page.tsx` | `/docs`, `/docs/a`, `/docs/a/b` |

Access dynamic params in page components:

```tsx
export default async function Page({
  params,
}: {
  params: Promise<{ id: string }>
}) {
  const { id } = await params
  return <div>Post: {id}</div>
}
```

`params`/`searchParams` are Promises (since Next.js 15); synchronous access was removed entirely in 16 — always `await` them. This applies to `layout.tsx`, `page.tsx`, `route.ts`, and `generateMetadata`. Next.js also generates helper types like `PageProps<'/blog/[slug]'>` — run `next typegen` to generate them without a full build.

## Parallel Routes

Render multiple pages simultaneously in the same layout using named slots (`@folder`):

```
app/
└── dashboard/
    ├── layout.tsx
    ├── page.tsx
    ├── @analytics/
    │   └── page.tsx
    └── @team/
        └── page.tsx
```

```tsx
// app/dashboard/layout.tsx
export default function DashboardLayout({
  children,
  analytics,
  team,
}: {
  children: React.ReactNode
  analytics: React.ReactNode
  team: React.ReactNode
}) {
  return (
    <div>
      {children}
      <div className="grid grid-cols-2">
        {analytics}
        {team}
      </div>
    </div>
  )
}
```

Next.js 16 **requires** an explicit `default.tsx` in every slot — the build fails without it. Return `null` or call `notFound()` to reproduce the old fallback behavior.

## Intercepting Routes

Intercept a route from a different part of the app using convention prefixes:

| Convention | Matches |
|------------|---------|
| `(.)folder` | Same level |
| `(..)folder` | One level up |
| `(..)(..)folder` | Two levels up |
| `(...)folder` | From root |

Common use case — modal pattern: clicking a photo in a feed opens a modal (intercepted), but navigating directly to `/photo/123` shows the full page.

## Proxy (proxy.ts)

Define the proxy in `proxy.ts` at the project root (same level as `app/`):

```ts
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function proxy(request: NextRequest) {
  // Redirect, rewrite, or modify headers
  if (!request.cookies.has('session')) {
    return NextResponse.redirect(new URL('/login', request.url))
  }
  return NextResponse.next()
}

export const config = {
  matcher: ['/dashboard/:path*', '/api/:path*'],
}
```

`proxy` can be a named or default export; the `NextResponse` redirect/rewrite/headers API and `export const config = { matcher: [...] }` are unchanged from middleware. Proxy runs on the Node.js runtime (no `runtime` option). Use it for authentication, redirects, internationalization, and A/B testing. Keep it lightweight — it runs on every matched request.

> `middleware.ts` is deprecated since Next.js 16 (it still works for Edge cases but will be removed in a future major). Migrate with `npx @next/codemod@canary middleware-to-proxy .`.

## Metadata API

Define SEO metadata using static exports or dynamic `generateMetadata`:

```tsx
// Static metadata
export const metadata = {
  title: 'My Page',
  description: 'Page description',
  openGraph: {
    title: 'My Page',
    description: 'Page description',
    images: ['/og-image.png'],
  },
}

// Dynamic metadata
export async function generateMetadata({
  params,
}: {
  params: Promise<{ id: string }>
}) {
  const { id } = await params
  const post = await getPost(id)
  return {
    title: post.title,
    description: post.excerpt,
  }
}
```

Metadata is evaluated from root to leaf. Child metadata merges with parent metadata. Use `title.template` in layouts:

```tsx
// app/layout.tsx
export const metadata = {
  title: {
    default: 'My App',
    template: '%s | My App',
  },
}
```

## Route Handlers (API Routes)

Define API endpoints in `route.ts` files:

```ts
// app/api/posts/route.ts
import { NextRequest, NextResponse } from 'next/server'

export async function GET(request: NextRequest) {
  const posts = await getPosts()
  return NextResponse.json(posts)
}

export async function POST(request: NextRequest) {
  const body = await request.json()
  const post = await createPost(body)
  return NextResponse.json(post, { status: 201 })
}
```

Supported HTTP methods: `GET`, `POST`, `PUT`, `PATCH`, `DELETE`, `HEAD`, `OPTIONS`.

Route handlers are Server-side only. For data mutations, prefer Server Actions over API routes when the mutation originates from a React component.

## Static Generation with `generateStaticParams`

Pre-render dynamic routes at build time:

```tsx
export async function generateStaticParams() {
  const posts = await getPosts()
  return posts.map((post) => ({
    id: post.id.toString(),
  }))
}
```

Combine with `dynamicParams = false` to return 404 for params not generated at build time.
