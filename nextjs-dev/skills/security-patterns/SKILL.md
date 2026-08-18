---
name: security-patterns
description: >
  Next.js security best practices for production applications. Use when the user asks about
  "Next.js security", "CSRF protection", "CSP headers", "Content Security Policy",
  "XSS prevention", "environment variable safety", "server-only", "security headers",
  "CORS", "rate limiting", "input sanitization", or needs guidance on securing a Next.js app.
---

# Security Patterns

## Environment Variable Safety

Only variables prefixed with `NEXT_PUBLIC_` are exposed to the browser. All others are server-only.

```bash
# .env.local
DATABASE_URL="postgresql://..."          # Server only — NEVER sent to browser
API_SECRET="sk-..."                      # Server only
NEXT_PUBLIC_APP_URL="https://myapp.com"  # Available in browser code
```

**Prevent accidental server code in client bundles** with the `server-only` package:

```bash
npm install server-only
```

```typescript
// lib/db.ts
import 'server-only'  // Build error if imported in a Client Component
import { Pool } from 'pg'

export const db = new Pool({ connectionString: process.env.DATABASE_URL })
```

If a Client Component imports this file (directly or transitively), the build will fail with a clear error.

## Content Security Policy (CSP)

Use `proxy.ts` (Next.js 16) to add CSP headers with a nonce:

```typescript
// proxy.ts
import { NextRequest, NextResponse } from 'next/server'

export function proxy(request: NextRequest) {
  const nonce = Buffer.from(crypto.randomUUID()).toString('base64')
  const isDev = process.env.NODE_ENV === 'development'

  const cspHeader = `
    default-src 'self';
    script-src 'self' 'nonce-${nonce}' 'strict-dynamic'${isDev ? " 'unsafe-eval'" : ''};
    style-src 'self' 'nonce-${nonce}';
    img-src 'self' blob: data:;
    font-src 'self';
    object-src 'none';
    base-uri 'self';
    form-action 'self';
    frame-ancestors 'none';
    upgrade-insecure-requests;
  `

  const contentSecurityPolicyHeaderValue = cspHeader
    .replace(/\s{2,}/g, ' ')
    .trim()

  const requestHeaders = new Headers(request.headers)
  requestHeaders.set('x-nonce', nonce)
  requestHeaders.set('Content-Security-Policy', contentSecurityPolicyHeaderValue)

  const response = NextResponse.next({
    request: { headers: requestHeaders },
  })
  response.headers.set('Content-Security-Policy', contentSecurityPolicyHeaderValue)

  return response
}
```

Filter proxy to skip static assets:

```typescript
// proxy.ts (add at the bottom)
export const config = {
  matcher: [
    {
      source: '/((?!api|_next/static|_next/image|favicon.ico).*)',
      missing: [
        { type: 'header', key: 'next-router-prefetch' },
        { type: 'header', key: 'purpose', value: 'prefetch' },
      ],
    },
  ],
}
```

Read the nonce in a layout to pass it to Script components:

```tsx
// app/layout.tsx
import { headers } from 'next/headers'
import Script from 'next/script'

export default async function RootLayout({ children }: { children: React.ReactNode }) {
  const headersList = await headers()
  const nonce = headersList.get('x-nonce') ?? ''

  return (
    <html lang="en">
      <body>
        {children}
        <Script
          src="https://analytics.example.com/script.js"
          strategy="afterInteractive"
          nonce={nonce}
        />
      </body>
    </html>
  )
}
```

> **Note:** In Next.js 16, the nonce is automatically applied to framework scripts. You only need to set it manually on third-party `<Script>` components.

## Security Headers

Add security headers via `next.config.js`:

```javascript
// next.config.js
const securityHeaders = [
  { key: 'X-DNS-Prefetch-Control', value: 'on' },
  { key: 'Strict-Transport-Security', value: 'max-age=63072000; includeSubDomains; preload' },
  { key: 'X-Frame-Options', value: 'SAMEORIGIN' },
  { key: 'X-Content-Type-Options', value: 'nosniff' },
  { key: 'Referrer-Policy', value: 'strict-origin-when-cross-origin' },
  { key: 'Permissions-Policy', value: 'camera=(), microphone=(), geolocation=()' },
]

module.exports = {
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: securityHeaders,
      },
    ]
  },
}
```

## CSRF Protection

**Server Actions** have built-in CSRF protection — Next.js validates the `Origin` header automatically. No additional setup needed.

**Route Handlers** require manual CSRF protection for state-changing operations:

```typescript
// app/api/data/route.ts
import { headers } from 'next/headers'

export async function POST(request: Request) {
  const headersList = await headers()
  const origin = headersList.get('origin')
  const host = headersList.get('host')

  // Verify origin matches host
  if (!origin || new URL(origin).host !== host) {
    return new Response('CSRF validation failed', { status: 403 })
  }

  // Process request...
}
```

## CORS for Route Handlers

```typescript
// app/api/data/route.ts
const ALLOWED_ORIGINS = ['https://myapp.com', 'https://admin.myapp.com']

export async function GET(request: Request) {
  const origin = request.headers.get('origin') ?? ''
  const data = await getData()

  return Response.json(data, {
    headers: {
      'Access-Control-Allow-Origin': ALLOWED_ORIGINS.includes(origin) ? origin : '',
      'Access-Control-Allow-Methods': 'GET, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    },
  })
}

export async function OPTIONS() {
  return new Response(null, {
    status: 204,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    },
  })
}
```

## XSS Prevention

- **Avoid `dangerouslySetInnerHTML`** — use it only for trusted content (e.g., sanitized CMS output)
- If you must render HTML, sanitize first:

```typescript
import DOMPurify from 'isomorphic-dompurify'

export function RichContent({ html }: { html: string }) {
  const clean = DOMPurify.sanitize(html)
  return <div dangerouslySetInnerHTML={{ __html: clean }} />
}
```

- React automatically escapes string values in JSX — `{userInput}` is safe
- Never construct HTML strings from user input in Server Components

## Input Validation in Server Actions

Always validate and sanitize input on the server — never trust client-side validation alone:

```typescript
'use server'

import { z } from 'zod'

const CommentSchema = z.object({
  content: z.string()
    .min(1, 'Comment cannot be empty')
    .max(1000, 'Comment too long')
    .transform(s => s.trim()),
  postId: z.string().uuid('Invalid post ID'),
})

export async function addComment(formData: FormData) {
  const parsed = CommentSchema.safeParse({
    content: formData.get('content'),
    postId: formData.get('postId'),
  })

  if (!parsed.success) {
    return { errors: parsed.error.flatten().fieldErrors }
  }

  // Safe to use parsed.data — validated and typed
  await db.comment.create({ data: parsed.data })
}
```

## Data Access Layer

Centralize authorization checks — don't scatter them across routes:

```typescript
// lib/dal.ts (Data Access Layer)
import 'server-only'
import { auth } from '@/lib/auth'
import { redirect } from 'next/navigation'

export async function getUser() {
  const session = await auth()
  if (!session?.user) {
    redirect('/login')
  }
  return session.user
}

export async function getUserPosts() {
  const user = await getUser() // Auth check built in
  return db.post.findMany({ where: { authorId: user.id } })
}
```

## Production Security Checklist

- [ ] No secrets in `NEXT_PUBLIC_*` variables
- [ ] `server-only` package on all server modules (db, auth, secrets)
- [ ] CSP headers with nonces for inline scripts
- [ ] Security headers (HSTS, X-Frame-Options, X-Content-Type-Options)
- [ ] Zod validation on all Server Actions and Route Handlers
- [ ] CSRF check on Route Handlers that mutate state
- [ ] `HttpOnly`, `Secure`, `SameSite` flags on auth cookies
- [ ] No `dangerouslySetInnerHTML` with unsanitized content
- [ ] Rate limiting on auth endpoints and public APIs
- [ ] `poweredByHeader: false` in `next.config.js`

## What This Skill Does NOT Cover

- Authentication/authorization flows (see `auth-patterns`)
- Database security (ORM-specific — use Prisma/Drizzle docs)
- DDoS protection (infrastructure-level — use Vercel/Cloudflare)
- Secrets management services (Vault, AWS Secrets Manager)
