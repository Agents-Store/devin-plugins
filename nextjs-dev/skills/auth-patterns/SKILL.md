---
name: auth-patterns
description: >
  Next.js authentication and authorization patterns. Use when the user asks about
  "authentication in Next.js", "NextAuth.js", "Auth.js", "Better Auth",
  "middleware auth guards", "protected routes", "session management",
  "role-based access", "login page", "signup form", "JWT sessions", "cookies auth",
  or needs guidance on implementing auth in App Router applications.
---

# Authentication Patterns

Authentication in Next.js spans multiple layers: proxy (middleware), layouts, pages, Server Actions, and Route Handlers. This skill covers where and how to check auth at each layer.

## Choosing an Auth Library

| Option | Use when | Notes |
|--------|----------|-------|
| **Better Auth** | New projects | Recommended path — see "Better Auth (Recommended for New Projects)" below. The Auth.js project is now part of Better Auth |
| **Own sessions** (`jose` + cookies, below) | Simple credentials login, full control, no extra dependency | You own password hashing, rotation and CSRF review |
| **NextAuth.js v4** (`next-auth@latest`, `4.24.15`) | Existing projects; a credentials login against an existing token API (for example a Directus backend) | A working path with Next.js 16, not a deprecated one: `npm i next-auth` still installs v4. Config, `proxy.ts` guard and its limits: [references/nextauth-and-authjs.md](references/nextauth-and-authjs.md) |
| **Auth.js v5** (`next-auth@beta`) | Existing projects already on it | Still a beta (`5.0.0-beta.32`) in maintenance mode — the Better Auth team ships security patches and critical fixes only |

The proxy / DAL / Server Action / Route Handler layering in this skill is library-independent: `getSession()` changes, and so does where a role comes from (Better Auth has none by default, see its section).

## Authentication Flow Overview

1. **User submits credentials** → Server Action validates and creates session
2. **Session stored** in encrypted cookie (stateless) or database (stateful)
3. **Proxy/middleware checks** session on every request → redirects if unauthorized
4. **Server Components** read session to render user-specific UI
5. **Server Actions/Route Handlers** verify session before mutations

## Sign-up / Login with Server Actions

### 1. Define Validation Schema

```typescript
// lib/schemas.ts
import { z } from 'zod'

export const SignupSchema = z.object({
  name: z.string().min(2, 'Name must be at least 2 characters').trim(),
  email: z.string().email('Please enter a valid email').trim(),
  password: z.string().min(8, 'Password must be at least 8 characters'),
})

export const LoginSchema = z.object({
  email: z.string().email('Please enter a valid email'),
  password: z.string().min(1, 'Password is required'),
})
```

### 2. Server Action for Signup

```typescript
// app/actions/auth.ts
'use server'

import { SignupSchema } from '@/lib/schemas'
import { createSession } from '@/lib/session'
import { redirect } from 'next/navigation'
import bcrypt from 'bcrypt'

export type AuthState = {
  message: string
  errors?: Record<string, string[]>
}

export async function signup(prevState: AuthState, formData: FormData): Promise<AuthState> {
  const parsed = SignupSchema.safeParse({
    name: formData.get('name'),
    email: formData.get('email'),
    password: formData.get('password'),
  })

  if (!parsed.success) {
    return { message: 'Validation failed', errors: parsed.error.flatten().fieldErrors }
  }

  // Check if user exists
  const existingUser = await db.user.findUnique({ where: { email: parsed.data.email } })
  if (existingUser) {
    return { message: 'Email already registered', errors: { email: ['Email already in use'] } }
  }

  // Create user
  const hashedPassword = await bcrypt.hash(parsed.data.password, 10)
  const user = await db.user.create({
    data: { name: parsed.data.name, email: parsed.data.email, password: hashedPassword },
  })

  // Create session and redirect
  await createSession(user.id)
  redirect('/dashboard')
}
```

### 3. Signup Form Component

```tsx
// app/(auth)/signup/page.tsx
'use client'

import { useActionState } from 'react'
import { signup, type AuthState } from '@/app/actions/auth'

const initialState: AuthState = { message: '' }

export default function SignupPage() {
  const [state, formAction, pending] = useActionState(signup, initialState)

  return (
    <form action={formAction}>
      <div>
        <label htmlFor="name">Name</label>
        <input id="name" name="name" type="text" required />
        {state.errors?.name && <p className="text-red-500">{state.errors.name[0]}</p>}
      </div>
      <div>
        <label htmlFor="email">Email</label>
        <input id="email" name="email" type="email" required />
        {state.errors?.email && <p className="text-red-500">{state.errors.email[0]}</p>}
      </div>
      <div>
        <label htmlFor="password">Password</label>
        <input id="password" name="password" type="password" required />
        {state.errors?.password && <p className="text-red-500">{state.errors.password[0]}</p>}
      </div>
      <button type="submit" disabled={pending}>
        {pending ? 'Creating account...' : 'Sign Up'}
      </button>
      {state.message && !state.errors && <p>{state.message}</p>}
    </form>
  )
}
```

## Session Management

### Stateless Sessions (JWT in Cookies)

Use `jose` for JWT encryption compatible with Edge Runtime:

```typescript
// lib/session.ts
import 'server-only'
import { SignJWT, jwtVerify } from 'jose'
import { cookies } from 'next/headers'

const secretKey = process.env.SESSION_SECRET!
const encodedKey = new TextEncoder().encode(secretKey)

export async function createSession(userId: string) {
  const expiresAt = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000) // 7 days
  const session = await new SignJWT({ userId })
    .setProtectedHeader({ alg: 'HS256' })
    .setIssuedAt()
    .setExpirationTime('7d')
    .sign(encodedKey)

  const cookieStore = await cookies()
  cookieStore.set('session', session, {
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'lax',
    expires: expiresAt,
    path: '/',
  })
}

export async function getSession() {
  const cookieStore = await cookies()
  const session = cookieStore.get('session')?.value
  if (!session) return null

  try {
    const { payload } = await jwtVerify(session, encodedKey, { algorithms: ['HS256'] })
    return payload as { userId: string }
  } catch {
    return null
  }
}

export async function deleteSession() {
  const cookieStore = await cookies()
  cookieStore.delete('session')
}
```

**Cookie options checklist:**
- `httpOnly: true` — prevents client-side JS access
- `secure: true` — HTTPS only in production
- `sameSite: 'lax'` — CSRF protection
- `path: '/'` — available on all routes

### Session Refresh

Extend session expiration when the user is active:

```typescript
// lib/session.ts
export async function refreshSession() {
  const session = await getSession()
  if (!session) return

  // Recreate with fresh expiration
  await createSession(session.userId)
}
```

## Proxy Auth Guard (Next.js 16)

Check session in `proxy.ts` to protect routes before they render:

```typescript
// proxy.ts
import { NextRequest, NextResponse } from 'next/server'
import { getSession } from '@/lib/session'

const protectedRoutes = ['/dashboard', '/settings', '/account']
const authRoutes = ['/login', '/signup']

export async function proxy(request: NextRequest) {
  const path = request.nextUrl.pathname
  const isProtected = protectedRoutes.some(route => path.startsWith(route))
  const isAuthRoute = authRoutes.some(route => path.startsWith(route))

  const session = await getSession()

  // Redirect unauthenticated users to login
  if (isProtected && !session) {
    const loginUrl = new URL('/login', request.url)
    loginUrl.searchParams.set('callbackUrl', path)
    return NextResponse.redirect(loginUrl)
  }

  // Redirect authenticated users away from auth pages
  if (isAuthRoute && session) {
    return NextResponse.redirect(new URL('/dashboard', request.url))
  }

  return NextResponse.next()
}
```

## Session in Server Components

```tsx
// app/dashboard/page.tsx
import { getSession } from '@/lib/session'
import { redirect } from 'next/navigation'

export default async function DashboardPage() {
  const session = await getSession()

  if (!session) {
    redirect('/login')
  }

  const user = await db.user.findUnique({ where: { id: session.userId } })

  return <h1>Welcome, {user?.name}</h1>
}
```

## Protecting Server Actions

Always verify auth before mutations:

```typescript
// app/actions/posts.ts
'use server'

import { getSession } from '@/lib/session'

export async function deletePost(postId: string) {
  const session = await getSession()
  if (!session) {
    throw new Error('Unauthorized')
  }

  // Verify ownership
  const post = await db.post.findUnique({ where: { id: postId } })
  if (post?.authorId !== session.userId) {
    throw new Error('Forbidden')
  }

  await db.post.delete({ where: { id: postId } })
}
```

## Protecting Route Handlers

```typescript
// app/api/posts/route.ts
import { getSession } from '@/lib/session'

export async function GET() {
  const session = await getSession()
  if (!session) {
    return Response.json({ error: 'Unauthorized' }, { status: 401 })
  }

  const posts = await db.post.findMany({ where: { authorId: session.userId } })
  return Response.json(posts)
}
```

## Role-Based Access Control (RBAC)

Extend session with roles:

```typescript
// lib/session.ts
export async function createSession(userId: string, role: string) {
  const session = await new SignJWT({ userId, role })
    .setProtectedHeader({ alg: 'HS256' })
    .setExpirationTime('7d')
    .sign(encodedKey)
  // ... set cookie
}
```

```typescript
// lib/dal.ts — Data Access Layer with role checks
import 'server-only'
import { getSession } from '@/lib/session'

export async function requireAdmin() {
  const session = await getSession()
  if (!session || session.role !== 'admin') {
    throw new Error('Forbidden: Admin access required')
  }
  return session
}

export async function requireAuth() {
  const session = await getSession()
  if (!session) {
    throw new Error('Unauthorized')
  }
  return session
}
```

```tsx
// app/admin/page.tsx
import { requireAdmin } from '@/lib/dal'

export default async function AdminPage() {
  const session = await requireAdmin() // Throws if not admin
  return <h1>Admin Dashboard</h1>
}
```

## Better Auth (Recommended for New Projects)

The Auth.js project has joined Better Auth. The Better Auth team continues to handle security patches and critical issues for Auth.js, but for new projects they strongly recommend Better Auth; if an existing Auth.js setup works well there is no urgent need to migrate (migration guide: https://authjs.dev/getting-started/migrate-to-better-auth).

```bash
npm install better-auth
```

```bash
# .env — generate the secret with: openssl rand -base64 32
BETTER_AUTH_SECRET=<at least 32 characters of high entropy>
BETTER_AUTH_URL=http://localhost:3000
```

```typescript
// lib/auth.ts
import { betterAuth } from 'better-auth'
import { nextCookies } from 'better-auth/next-js'
import { Pool } from 'pg'

export const auth = betterAuth({
  database: new Pool({ connectionString: process.env.DATABASE_URL }), // or a Drizzle / Prisma adapter
  emailAndPassword: { enabled: true },
  socialProviders: {
    github: {
      clientId: process.env.GITHUB_CLIENT_ID!,
      clientSecret: process.env.GITHUB_CLIENT_SECRET!,
    },
  },
  plugins: [nextCookies()], // lets Server Actions set cookies — must be the last plugin
})
```

Without a `database` option Better Auth runs in stateless-session mode, but most plugins require a database. Generate the schema with the Better Auth CLI (`npx auth@latest generate`; for Prisma or Drizzle it writes the ORM schema, for the built-in database support it writes an SQL file).

```typescript
// app/api/auth/[...all]/route.ts
import { auth } from '@/lib/auth'
import { toNextJsHandler } from 'better-auth/next-js'

export const { GET, POST } = toNextJsHandler(auth)
```

```typescript
// lib/auth-client.ts — import from better-auth/react
import { createAuthClient } from 'better-auth/react'

export const authClient = createAuthClient()
// Client Components: authClient.signIn.email({ email, password }), authClient.signUp.email({ name, email, password }),
// authClient.signIn.social({ provider: 'github' }), authClient.signOut(), authClient.useSession()
```

Read the session on the server (Server Components, Server Actions, Route Handlers) with `auth.api.getSession`:

```typescript
// lib/session.ts — replaces getSession() for the session lookup (it returns { session, user }, and has no role: see below)
import 'server-only'
import { auth } from '@/lib/auth'
import { headers } from 'next/headers'

export async function getSession() {
  return auth.api.getSession({ headers: await headers() })
}
```

```tsx
// app/dashboard/page.tsx
import { getSession } from '@/lib/session'
import { redirect } from 'next/navigation'

export default async function DashboardPage() {
  const session = await getSession()
  if (!session) redirect('/login')
  return <h1>Welcome, {session.user.name}</h1>
}
```

Note that `session.user.id` replaces the `session.userId` field of the hand-rolled session above, and that this is a drop-in replacement only for the *session lookup*, not for everything the hand-rolled payload carried. **There is no `session.role`**: Better Auth's user has no role field by default, so the `requireAdmin()` of the RBAC section does not work until you add one. Either enable the `admin` plugin (adds `user.role`), or declare your own column and read it as `session.user.role`:

```typescript
// lib/auth.ts — inside betterAuth({ ... })
user: {
  additionalFields: {
    // input: false is essential: without it a user could send their own role at sign-up
    role: { type: 'string', required: false, defaultValue: 'user', input: false },
  },
},
```

Server Components cannot set cookies, so the cookie cache refreshes only when a Server Action or Route Handler runs.

Optimistic redirect in `proxy.ts` — check only that a session cookie exists, never treat it as proof of authentication:

```typescript
// proxy.ts
import { NextRequest, NextResponse } from 'next/server'
import { getSessionCookie } from 'better-auth/cookies'

export async function proxy(request: NextRequest) {
  // Optimistic only: the cookie may be forged or expired. Real checks live in the DAL / pages / actions.
  if (!getSessionCookie(request)) {
    return NextResponse.redirect(new URL('/login', request.url))
  }
  return NextResponse.next()
}

export const config = { matcher: ['/dashboard/:path*'] }
```

If you changed Better Auth's cookie name or prefix, pass the same settings to `getSessionCookie`. In Next.js 16 the proxy runs on the Node.js runtime, so full validation with `auth.api.getSession({ headers: request.headers })` is possible there too, at the cost of a database hit per matched request.

**With `cacheComponents: true`:** `getSession()` reads `headers()`, so it is request-time data. Call it inside a component wrapped in `<Suspense>` (or opt a route out with `export const instant = false` while migrating), never inside a `'use cache'` scope — extract the `userId` first and pass it into the cached function. See the "Authentication with Cache Components" guide at https://nextjs.org/docs/app/guides/authentication-with-cache-components.

## NextAuth v4 and Auth.js v5 — Existing Projects

Both keep working for projects that already use them; neither is the recommendation for new work. The full recipes are in [references/nextauth-and-authjs.md](references/nextauth-and-authjs.md):

- **NextAuth v4** — Credentials provider against a token API with refresh, `types/next-auth.d.ts`, `app/api/auth/[...nextauth]/route.ts`, `SessionProvider`, the `proxy.ts` guard (`getToken` in Next.js 16, not `middleware.ts`), a login page, and the limits that decide whether v4 fits (only the NextAuth route may refresh, and it needs a tab polling it; two tabs can race on a single-use refresh token; the access token is readable in the browser).
- **Auth.js v5** (`next-auth@beta`) — `auth.ts` with `handlers`, `auth()` in Server Components. Maintenance mode under Better Auth.

## Auth Check Layers — When to Use Which

| Layer | Purpose | Catches |
|-------|---------|---------|
| **Proxy** | Redirect before render | Unauthenticated page visits |
| **Layout** | Shared auth UI (show/hide nav items) | Nothing — layouts don't block |
| **Page** | Server-side auth check + redirect | Direct page access |
| **Server Action** | Verify before mutation | Unauthorized form submissions |
| **Route Handler** | Verify before API response | Unauthorized API calls |
| **Data Access Layer** | Centralized auth + data | All data access points |

**Best practice:** Use proxy for redirects, DAL for data access. Don't rely solely on proxy — it can be bypassed by direct Server Action calls.

## What This Skill Does NOT Cover

- Specific OAuth provider setup (Google, GitHub, etc.) — see the Better Auth or Auth.js docs
- Database adapter configuration for Better Auth / Auth.js
- Multi-tenancy and organization-based access
- Two-factor authentication (2FA) implementation
- Social login UI components
