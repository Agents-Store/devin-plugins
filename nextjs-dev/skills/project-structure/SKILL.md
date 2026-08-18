---
name: project-structure
description: >
  Next.js project architecture and file organization patterns. Use when the user asks about
  "Next.js project structure", "folder organization", "feature-based structure", "where to put
  shared code", "naming conventions", "barrel exports", "modular architecture", "colocation",
  "route groups for organization", or needs guidance on organizing a scalable Next.js codebase.
---

# Project Structure & Organization

Next.js is **unopinionated** about how you organize your project. This skill provides proven patterns for small, medium, and large applications.

## File Conventions (Next.js 16)

These files have special meaning inside `app/`:

| File | Purpose |
|------|---------|
| `layout.tsx` | Shared UI wrapping child segments (persists across navigation) |
| `page.tsx` | Public route UI |
| `loading.tsx` | Loading UI (Suspense boundary) |
| `error.tsx` | Error UI (error boundary) — see `error-handling` skill |
| `not-found.tsx` | 404 UI |
| `route.ts` | API endpoint (Route Handler) |
| `template.tsx` | Re-rendered layout (new instance on navigation) |
| `default.tsx` | Parallel route fallback |
| `global-error.tsx` | Root error boundary (must include `<html>`, `<body>`) |

Top-level files:

| File | Purpose |
|------|---------|
| `next.config.js` / `next.config.ts` | Next.js configuration |
| `proxy.ts` | Request proxy (replaces middleware in Next.js 16) |
| `instrumentation.ts` | OpenTelemetry and instrumentation |
| `.env.local` | Local environment variables |

## Recommended Structures

### Small App (< 10 routes)

Keep everything colocated in `app/`. Shared code in top-level folders:

```
src/
├── app/
│   ├── layout.tsx
│   ├── page.tsx
│   ├── about/
│   │   └── page.tsx
│   └── blog/
│       ├── page.tsx
│       └── [slug]/
│           └── page.tsx
├── components/
│   ├── header.tsx
│   └── footer.tsx
├── lib/
│   └── utils.ts
└── public/
    └── images/
```

### Medium App (10–30 routes)

Use **route groups** for organizational separation and colocate related code:

```
src/
├── app/
│   ├── layout.tsx
│   ├── page.tsx
│   ├── (marketing)/
│   │   ├── layout.tsx
│   │   ├── about/page.tsx
│   │   ├── blog/page.tsx
│   │   └── pricing/page.tsx
│   ├── (dashboard)/
│   │   ├── layout.tsx
│   │   ├── dashboard/page.tsx
│   │   ├── settings/page.tsx
│   │   └── _components/        # Private folder — not routable
│   │       ├── sidebar.tsx
│   │       └── nav.tsx
│   └── api/
│       └── webhooks/
│           └── route.ts
├── components/                  # Shared UI components
│   ├── ui/                      # Primitives (button, input, card)
│   └── shared/                  # Composed components (data-table, file-upload)
├── lib/
│   ├── db.ts                    # Database client
│   ├── utils.ts                 # Generic utilities
│   └── constants.ts
├── actions/                     # Server Actions
│   ├── auth.ts
│   └── posts.ts
└── types/
    └── index.ts
```

### Large App (30+ routes)

Use **feature-based organization** — group by domain, not by technical layer:

```
src/
├── app/
│   ├── layout.tsx
│   ├── page.tsx
│   ├── (auth)/
│   │   ├── login/page.tsx
│   │   └── register/page.tsx
│   ├── (dashboard)/
│   │   ├── layout.tsx
│   │   └── [...slug]/page.tsx
│   └── api/
│       └── webhooks/stripe/route.ts
├── features/
│   ├── auth/
│   │   ├── components/
│   │   │   ├── login-form.tsx
│   │   │   └── register-form.tsx
│   │   ├── actions/
│   │   │   └── auth-actions.ts
│   │   ├── lib/
│   │   │   └── session.ts
│   │   └── types.ts
│   ├── posts/
│   │   ├── components/
│   │   │   ├── post-card.tsx
│   │   │   └── post-list.tsx
│   │   ├── actions/
│   │   │   └── post-actions.ts
│   │   ├── queries/
│   │   │   └── get-posts.ts
│   │   └── types.ts
│   └── billing/
│       ├── components/
│       ├── actions/
│       ├── lib/
│       └── types.ts
├── components/                  # Truly shared UI only
│   └── ui/
├── lib/                         # Truly shared utilities only
│   ├── db.ts
│   └── utils.ts
└── types/
    └── globals.d.ts
```

## Key Organization Patterns

### Route Groups `(name)`

Wrap folders in parentheses to organize without affecting URLs:

```
app/
├── (marketing)/        # URL: /about, /blog — NOT /marketing/about
│   ├── layout.tsx      # Marketing-specific layout
│   ├── about/page.tsx
│   └── blog/page.tsx
├── (shop)/             # URL: /cart, /products
│   ├── layout.tsx      # Shop-specific layout (with cart sidebar)
│   ├── cart/page.tsx
│   └── products/page.tsx
```

Each route group can have its own `layout.tsx`, `loading.tsx`, and `error.tsx`.

### Private Folders `_name`

Prefix with underscore to exclude from routing. Safe for colocated utilities:

```
app/dashboard/
├── page.tsx
├── _components/        # NOT a route — colocated UI
│   ├── stats-card.tsx
│   └── recent-activity.tsx
├── _lib/               # NOT a route — colocated helpers
│   └── format-data.ts
└── _hooks/
    └── use-dashboard-data.ts
```

### Data Layer Organization

Separate data access from UI:

```typescript
// src/features/posts/queries/get-posts.ts — Data fetching
import { db } from '@/lib/db'

export async function getPosts(limit = 10) {
  return db.post.findMany({ take: limit, orderBy: { createdAt: 'desc' } })
}

// src/features/posts/actions/post-actions.ts — Mutations
'use server'
import { revalidatePath } from 'next/cache'
import { db } from '@/lib/db'

export async function createPost(formData: FormData) {
  await db.post.create({ data: { title: formData.get('title') as string } })
  revalidatePath('/posts')
}

// src/app/posts/page.tsx — Route (thin, delegates to feature)
import { getPosts } from '@/features/posts/queries/get-posts'
import { PostList } from '@/features/posts/components/post-list'

export default async function PostsPage() {
  const posts = await getPosts()
  return <PostList posts={posts} />
}
```

## Naming Conventions

| Convention | Example | Notes |
|------------|---------|-------|
| Files | `kebab-case.tsx` | `post-card.tsx`, `auth-actions.ts` |
| Components | `PascalCase` | `PostCard`, `LoginForm` |
| Hooks | `camelCase` with `use` prefix | `useDashboardData` |
| Server Actions | `camelCase` verbs | `createPost`, `deleteUser` |
| Types | `PascalCase` | `Post`, `UserSession` |
| Constants | `SCREAMING_SNAKE_CASE` | `MAX_FILE_SIZE`, `API_URL` |
| Route folders | `kebab-case` | `blog-posts/`, `user-settings/` |

## Path Aliases

Configure in `tsconfig.json` for clean imports:

```json
{
  "compilerOptions": {
    "paths": {
      "@/*": ["./src/*"],
      "@/components/*": ["./src/components/*"],
      "@/features/*": ["./src/features/*"],
      "@/lib/*": ["./src/lib/*"]
    }
  }
}
```

## Anti-patterns

- **"Utils" dumping ground** — Don't create a catch-all `utils/` with 50+ files. Split by domain or move into features.
- **Deep barrel exports** — Avoid `index.ts` re-exporting from deeply nested files. Causes circular imports and bundle bloat.
- **Mixing concerns in `app/`** — Don't put business logic, database queries, or utility functions directly in route files. Route files should be thin orchestrators.
- **Unnecessary abstraction** — Don't create `features/` for a 5-page app. Start simple, extract when it hurts.
- **Importing server code in client components** — Use `server-only` package to prevent accidental leaks. See `security-patterns` skill.

## What This Skill Does NOT Cover

- Monorepo setup with Turborepo (tool-specific)
- CI/CD and deployment configuration (see `cli-recipes`)
- Routing patterns like parallel/intercepting routes (see `app-router-patterns`)
- Component architecture decisions (see `server-client-components`)
