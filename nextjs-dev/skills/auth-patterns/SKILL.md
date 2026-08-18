---
name: auth-patterns
description: >
  Next.js authentication and authorization patterns. Use when the user asks about
  "authentication in Next.js", "NextAuth.js", "Auth.js", "middleware auth guards",
  "protected routes", "session management", "role-based access", "login page",
  "signup form", "JWT sessions", "cookies auth", or needs guidance on implementing
  auth in App Router applications.
---

# Authentication Patterns

Authentication in Next.js spans multiple layers: proxy (middleware), layouts, pages, Server Actions, and Route Handlers. This skill covers where and how to check auth at each layer.

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

## Auth.js (NextAuth v5) Quick Setup

For a full-featured auth solution with OAuth providers:

```bash
npm install next-auth@beta
```

```typescript
// auth.ts
import NextAuth from 'next-auth'
import GitHub from 'next-auth/providers/github'

export const { handlers, signIn, signOut, auth } = NextAuth({
  providers: [GitHub],
})
```

```typescript
// app/api/auth/[...nextauth]/route.ts
import { handlers } from '@/auth'
export const { GET, POST } = handlers
```

```tsx
// Usage in Server Components
import { auth } from '@/auth'

export default async function Page() {
  const session = await auth()
  if (!session?.user) return <p>Not signed in</p>
  return <p>Welcome, {session.user.name}</p>
}
```

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

- Specific OAuth provider setup (Google, GitHub, etc.) — see Auth.js docs
- Database adapter configuration for Auth.js
- Multi-tenancy and organization-based access
- Two-factor authentication (2FA) implementation
- Social login UI components
