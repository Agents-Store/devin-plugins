---
name: api-design
description: >
  Next.js API design patterns for Route Handlers and Server Actions. Use when the user asks about
  "Route Handlers", "API routes in App Router", "Server Actions vs API routes",
  "input validation", "API response patterns", "streaming responses", "SSE",
  "webhooks in Next.js", "CORS", "API versioning", or needs guidance on building APIs with Next.js.
---

# API Design

## Decision Matrix: Server Actions vs Route Handlers

| Use Case | Recommended | Why |
|----------|-------------|-----|
| Form mutation from React component | **Server Action** | Built-in progressive enhancement, CSRF protection |
| Data mutation from React component | **Server Action** | Direct integration with `useActionState`, `useOptimistic` |
| External API consumers (mobile apps, 3rd parties) | **Route Handler** | Standard REST endpoints with HTTP methods |
| Webhook receiver | **Route Handler** | Needs specific HTTP method + signature verification |
| File download endpoint | **Route Handler** | Needs custom response headers and streaming |
| OAuth callback | **Route Handler** | External service redirects to URL |
| Cron job endpoint | **Route Handler** | Called by external scheduler |

**Rule of thumb:** Server Actions for React UI mutations, Route Handlers for everything else.

## Route Handler Basics

Route Handlers live in `app/**/route.ts` files and export HTTP method functions:

```typescript
// app/api/posts/route.ts
import { NextRequest } from 'next/server'

export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams
  const page = Number(searchParams.get('page') ?? '1')
  const limit = Number(searchParams.get('limit') ?? '10')

  const posts = await db.post.findMany({
    skip: (page - 1) * limit,
    take: limit,
    orderBy: { createdAt: 'desc' },
  })

  return Response.json(posts)
}

export async function POST(request: NextRequest) {
  const body = await request.json()

  const post = await db.post.create({ data: body })

  return Response.json(post, { status: 201 })
}
```

### Dynamic Route Handlers

```typescript
// app/api/posts/[id]/route.ts
export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params
  const post = await db.post.findUnique({ where: { id } })

  if (!post) {
    return Response.json({ error: 'Post not found' }, { status: 404 })
  }

  return Response.json(post)
}

export async function DELETE(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params
  await db.post.delete({ where: { id } })
  return new Response(null, { status: 204 })
}
```

### Route Context Helper (Next.js 16)

Use `RouteContext` for strongly typed params:

```typescript
// app/api/users/[id]/route.ts
import type { NextRequest } from 'next/server'

export async function GET(_req: NextRequest, ctx: RouteContext<'/users/[id]'>) {
  const { id } = await ctx.params
  return Response.json({ id })
}
```

> Types are generated during `next dev`, `next build` or `next typegen`. `RouteContext` is globally available — no import needed.

## Input Validation with Zod

Always validate request bodies and query params:

```typescript
// app/api/posts/route.ts
import { z } from 'zod'
import { NextRequest } from 'next/server'

const CreatePostSchema = z.object({
  title: z.string().min(1).max(200),
  content: z.string().min(1),
  published: z.boolean().default(false),
})

export async function POST(request: NextRequest) {
  let body: unknown
  try {
    body = await request.json()
  } catch {
    return Response.json({ error: 'Invalid JSON' }, { status: 400 })
  }

  const parsed = CreatePostSchema.safeParse(body)
  if (!parsed.success) {
    return Response.json(
      { error: 'Validation failed', details: parsed.error.flatten().fieldErrors },
      { status: 422 }
    )
  }

  const post = await db.post.create({ data: parsed.data })
  return Response.json(post, { status: 201 })
}
```

## Response Patterns

### Consistent Error Responses

```typescript
// lib/api-utils.ts
export function apiError(message: string, status: number, details?: unknown) {
  return Response.json({ error: message, details }, { status })
}

export function apiSuccess<T>(data: T, status = 200) {
  return Response.json(data, { status })
}
```

### Headers, Cookies, Redirects

```typescript
import { cookies, headers } from 'next/headers'
import { NextRequest } from 'next/server'

export async function GET(request: NextRequest) {
  // Read cookies
  const cookieStore = await cookies()
  const token = cookieStore.get('token')

  // Read headers
  const headersList = await headers()
  const referer = headersList.get('referer')

  // Set response headers
  return Response.json({ data: 'value' }, {
    headers: {
      'Cache-Control': 'public, max-age=3600',
      'X-Custom-Header': 'value',
    },
  })
}
```

## Streaming Responses

### Server-Sent Events (SSE)

```typescript
// app/api/events/route.ts
export async function GET() {
  const encoder = new TextEncoder()

  const stream = new ReadableStream({
    async start(controller) {
      const send = (data: unknown) => {
        controller.enqueue(encoder.encode(`data: ${JSON.stringify(data)}\n\n`))
      }

      // Send events
      for (let i = 0; i < 10; i++) {
        send({ count: i, timestamp: Date.now() })
        await new Promise(resolve => setTimeout(resolve, 1000))
      }

      controller.close()
    },
  })

  return new Response(stream, {
    headers: {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache',
      Connection: 'keep-alive',
    },
  })
}
```

Client consumption:

```tsx
'use client'

import { useEffect, useState } from 'react'

export function EventStream() {
  const [events, setEvents] = useState<any[]>([])

  useEffect(() => {
    const source = new EventSource('/api/events')
    source.onmessage = (event) => {
      setEvents(prev => [...prev, JSON.parse(event.data)])
    }
    return () => source.close()
  }, [])

  return <ul>{events.map((e, i) => <li key={i}>{JSON.stringify(e)}</li>)}</ul>
}
```

### Streaming JSON

```typescript
// app/api/export/route.ts
export async function GET() {
  const encoder = new TextEncoder()

  const stream = new ReadableStream({
    async start(controller) {
      const cursor = db.post.findManyCursor({ take: 100 })

      for await (const batch of cursor) {
        controller.enqueue(encoder.encode(JSON.stringify(batch) + '\n'))
      }

      controller.close()
    },
  })

  return new Response(stream, {
    headers: { 'Content-Type': 'application/x-ndjson' },
  })
}
```

## Webhook Handler Pattern

```typescript
// app/api/webhooks/stripe/route.ts
import { NextRequest } from 'next/server'
import Stripe from 'stripe'

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!)
const webhookSecret = process.env.STRIPE_WEBHOOK_SECRET!

export async function POST(request: NextRequest) {
  const body = await request.text()
  const signature = request.headers.get('stripe-signature')!

  // 1. Verify signature
  let event: Stripe.Event
  try {
    event = stripe.webhooks.constructEvent(body, signature, webhookSecret)
  } catch (err) {
    return Response.json({ error: 'Invalid signature' }, { status: 400 })
  }

  // 2. Idempotency — check if already processed
  const existing = await db.webhookEvent.findUnique({ where: { eventId: event.id } })
  if (existing) {
    return Response.json({ received: true }) // Already processed
  }

  // 3. Process event
  switch (event.type) {
    case 'checkout.session.completed':
      await handleCheckoutComplete(event.data.object)
      break
    case 'invoice.payment_failed':
      await handlePaymentFailed(event.data.object)
      break
  }

  // 4. Record event
  await db.webhookEvent.create({ data: { eventId: event.id, type: event.type } })

  return Response.json({ received: true })
}
```

## API Versioning

Use route groups for versioning without code duplication:

```
app/api/
├── v1/
│   └── posts/
│       └── route.ts    # /api/v1/posts
└── v2/
    └── posts/
        └── route.ts    # /api/v2/posts
```

Or use a single handler with version detection:

```typescript
// app/api/posts/route.ts
export async function GET(request: NextRequest) {
  const version = request.headers.get('api-version') ?? 'v1'

  if (version === 'v2') {
    return Response.json(await getPostsV2())
  }

  return Response.json(await getPostsV1())
}
```

## File Download

```typescript
// app/api/download/[filename]/route.ts
import { readFile } from 'fs/promises'
import path from 'path'

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ filename: string }> }
) {
  const { filename } = await params
  const filePath = path.join(process.cwd(), 'uploads', filename)

  try {
    const file = await readFile(filePath)
    return new Response(file, {
      headers: {
        'Content-Type': 'application/octet-stream',
        'Content-Disposition': `attachment; filename="${filename}"`,
      },
    })
  } catch {
    return Response.json({ error: 'File not found' }, { status: 404 })
  }
}
```

## Caching Route Handlers

```typescript
// Static (cached at build time) — only GET with no dynamic inputs
export async function GET() {
  const data = await fetch('https://api.example.com/data')
  return Response.json(await data.json())
}

// Dynamic (never cached) — uses cookies, headers, or request object
export async function GET(request: NextRequest) {
  const cookieStore = await cookies()
  // This is dynamic because it reads cookies
  return Response.json({ data: 'dynamic' })
}

// Revalidation
export const revalidate = 3600 // Revalidate every hour
```

## What This Skill Does NOT Cover

- tRPC integration (use tRPC docs)
- GraphQL endpoints (use Apollo/Yoga docs)
- External API client patterns (fetch wrappers)
- Database query optimization (ORM-specific)
- WebSocket endpoints (use third-party like Pusher, Ably, or Socket.io)
