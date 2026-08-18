---
name: troubleshoot
description: Next.js common errors, debugging techniques, and solutions. This skill should be used when the user asks about "Next.js errors", "hydration error", "Next.js not working", "build errors", "debug Next.js", "'use client' errors", "deployment issues", or encounters problems during Next.js development.
---

# Troubleshooting Next.js

Diagnostics and fixes for common Next.js issues. Start with the quick diagnostics checklist, then check the categorized error tables.

## Quick Diagnostics Checklist

1. **Check Next.js version**: `npx next --version` — ensure 14+ for stable App Router
2. **Check Node.js version**: `node -v` — 20.9+ required for Next.js 16
3. **Clear cache**: `rm -rf .next && npm run dev`
4. **Check TypeScript**: `npx tsc --noEmit` — catch type errors early
5. **Check console**: Both browser console and terminal for error messages
6. **Check MCP**: If using `next-devtools-mcp`, call `nextjs_call` with `get_errors`

## Hydration Errors

The most common Next.js issue. Occurs when server-rendered HTML doesn't match client-rendered output. Since Next.js 16.2, the dev overlay shows a labeled `+Client`/`-Server` diff pinpointing the exact mismatching markup.

| Error | Cause | Fix |
|-------|-------|-----|
| "Text content does not match" | Different text on server vs client | Avoid `Date.now()`, `Math.random()` in Server Components. Use `useEffect` for client-only values |
| "Expected server HTML to contain a matching `<div>`" | DOM structure mismatch | Check for `<p>` inside `<p>`, `<div>` inside `<p>`, or conditional rendering based on `window` |
| "Hydration failed because the initial UI does not match" | Browser extensions or invalid HTML nesting | Validate HTML nesting. Suppress specific elements with `suppressHydrationWarning` |

### Common Hydration Causes

```tsx
// BAD: Different output on server vs client
export default function Clock() {
  return <p>Time: {new Date().toLocaleTimeString()}</p>
}

// GOOD: Use client-only rendering for dynamic values
'use client'
import { useState, useEffect } from 'react'

export default function Clock() {
  const [time, setTime] = useState<string>()
  useEffect(() => {
    setTime(new Date().toLocaleTimeString())
  }, [])
  return <p>Time: {time ?? 'Loading...'}</p>
}
```

```tsx
// BAD: Checking window in render
export default function Component() {
  const isDesktop = window.innerWidth > 768  // Fails on server
  return isDesktop ? <Desktop /> : <Mobile />
}

// GOOD: Use CSS media queries or useEffect
'use client'
import { useState, useEffect } from 'react'

export default function Component() {
  const [isDesktop, setIsDesktop] = useState(false)
  useEffect(() => {
    setIsDesktop(window.innerWidth > 768)
  }, [])
  return isDesktop ? <Desktop /> : <Mobile />
}
```

### Locale-Dependent Date Rendering

`toLocaleDateString()` produces different output on server vs client because locale settings differ. Three approaches, from best to simplest:

**Approach 1 — ISO initial render + client upgrade (recommended):**

Render a stable ISO string on the server, then upgrade to the user's locale format after hydration. No mismatch, no flash of wrong content for most users:

```tsx
// components/formatted-date.tsx
'use client'

import { useState, useEffect } from 'react'

export function FormattedDate({ dateString }: { dateString: string }) {
  const [formatted, setFormatted] = useState(() => {
    // Stable initial render — matches server output
    return new Date(dateString).toISOString().split('T')[0]
  })

  useEffect(() => {
    // After hydration, upgrade to user's locale format
    setFormatted(new Date(dateString).toLocaleDateString())
  }, [dateString])

  return <time dateTime={dateString}>{formatted}</time>
}
```

Use in a Server Component page:
```tsx
// app/blog/[id]/page.tsx — Server Component
import { FormattedDate } from '@/components/formatted-date'

export default async function BlogPost({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params
  const post = await getPost(id)
  return (
    <article>
      <h1>{post.title}</h1>
      <FormattedDate dateString={post.date} />
      <p>{post.content}</p>
    </article>
  )
}
```

**Approach 2 — Fixed locale (simpler but less flexible):**

Pin the locale so server and client produce identical output:

```tsx
'use client'

export function FormattedDate({ dateString }: { dateString: string }) {
  return (
    <time dateTime={dateString}>
      {new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric', month: 'long', day: 'numeric',
      })}
    </time>
  )
}
```

**Approach 3 — `suppressHydrationWarning` (last resort):**

```tsx
<time dateTime={post.date} suppressHydrationWarning>
  {new Date(post.date).toLocaleDateString()}
</time>
```

Only use `suppressHydrationWarning` for leaf elements where the mismatch is cosmetic (e.g., date formatting). It does not fix the mismatch — it silences the warning and shows the client output after hydration.

## `'use client'` Errors

| Error | Cause | Fix |
|-------|-------|-----|
| "useState is not a function" | Using hooks in a Server Component | Add `'use client'` to the file |
| "You're importing a component that needs useState" | Importing a client library in a Server Component | Create a wrapper Client Component |
| "Event handlers cannot be passed to Client Component props from Server Components" | Passing `onClick` from Server to Client Component | Define event handlers inside the Client Component |
| "Functions cannot be passed directly to Client Components" | Trying to pass a function as props | Move the function into the Client Component or use Server Actions |

## Build Errors

| Error | Cause | Fix |
|-------|-------|-----|
| "Dynamic server usage" | Using `cookies()`, `headers()`, or `searchParams` in a statically generated page | Add `export const dynamic = 'force-dynamic'` or restructure to fetch dynamically |
| "generateStaticParams is required for dynamic routes with output: export" | Missing static params for static export | Add `generateStaticParams` or remove `output: 'export'` |
| "Module not found: Can't resolve 'fs'" | Using Node.js modules in client code | Move to Server Component or Route Handler |
| "`params` is now a Promise" | Next.js 15+ async params not awaited | `const { id } = await params` |

## Data Fetching Errors

| Error | Cause | Fix |
|-------|-------|-----|
| "async/await is not yet supported in Client Components" | Using `async` in a Client Component | Fetch in a Server Component and pass data as props, or use `use()` hook |
| "cookies was called outside a request scope" | Accessing `cookies()` at build time | Ensure it's inside a request handler (page, layout, route handler, or Server Action) |
| "Error: NEXT_REDIRECT" | `redirect()` caught in try/catch | Call `redirect()` outside try/catch blocks — it throws intentionally |
| Stale data after mutation | Cache not revalidated | Call `revalidatePath()` or `revalidateTag()` after mutations |

## Image Issues (`next/image`)

| Symptom | Cause | Fix |
|---------|-------|-----|
| Broken/missing images, no visible error | Upstream image source returns 403 — `next/image` proxies through `/_next/image` so the HTTP error is hidden from the browser | Check network tab for `/_next/image` requests returning 403/401. If the upstream (e.g., Directus, S3) requires auth, include `access_token` or API key in the image URL |
| "Invalid src prop" or "hostname not configured" | Remote image domain missing from config | Add the domain to `images.remotePatterns` in `next.config.ts` |
| Images load in `<img>` but not `<Image>` | `next/image` optimizer can't fetch the upstream URL | Verify the upstream URL is reachable from the server (not just the browser). Common with private networks or auth-protected CDNs. Next 16 blocks optimization of local-IP upstreams by default — set `images.dangerouslyAllowLocalIP: true` for private networks |
| Blurry or low-quality images | Wrong `sizes` prop or default quality | Set `sizes` to match actual display size. In Next 16, `quality` values other than 75 require `images.qualities` config — the prop is coerced to the closest configured value, so raising `quality` alone silently no-ops |

**Debugging tip:** When images appear broken with no error, always check `/_next/image` requests in the browser Network tab — the HTTP status reveals whether the issue is upstream auth (403), missing config (400), or network (502/504).

## Performance Issues

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| Slow initial load | Large client bundle | Move components to Server Components; use `dynamic()` for heavy libraries |
| Layout shift on load | Images without dimensions | Add `width`/`height` to `<Image>` or use `fill` |
| Flash of unstyled text | External font stylesheet | Use `next/font` instead of `<link>` |
| Slow navigation | No prefetching | Ensure `<Link>` is used (auto-prefetch); check `prefetch={false}` isn't set |
| High memory in production | Memory leaks in proxy | Avoid storing state in the proxy closure; check for global variable accumulation |

## Deployment Issues

For platform-specific deployment issues (Vercel, Dokploy, Netlify, etc.), see the respective deployment plugin (`vercel-dev`, `dokploy-dev`). Common cross-platform issues:

| Issue | Fix |
|-------|-----|
| Build fails with memory error | Add `NODE_OPTIONS=--max_old_space_size=4096` to build env |
| Environment variables not available at build | Use `NEXT_PUBLIC_` prefix for client-side vars; redeploy after adding env vars |
| API routes timing out | Increase function timeout in your platform settings or stream the response; `export const runtime = 'edge'` only where the platform supports it |
| `revalidateTag` deprecation warning | Add a cacheLife profile argument (`revalidateTag(tag, 'max')`) or use `updateTag()` in Server Actions |
| `output: 'standalone'` not generating `server.js` | Verify config, clear `.next/`, rebuild |
| Static files not found in standalone | Copy `public/` and `.next/static/` to the standalone output |
| Port conflicts | Set `PORT` env var or use `-p` flag |
| CORS errors | Add headers in `next.config.ts` `headers()` or `proxy.ts` |

## Diagnostic Commands

```bash
# Check Next.js version
npx next --version

# Generate route types + full type check
npx next typegen && npx tsc --noEmit

# Clean build
rm -rf .next node_modules/.cache && npm run build

# Debug prerender errors
npx next build --debug-prerender

# Check bundle (Turbopack analyzer, 16.1+)
npx next experimental-analyze

# Debug with the Node inspector
npx next dev --inspect
```

## When to Escalate

- **Persistent 500 errors**: Check server logs, not just browser. Use `next-devtools-mcp` `get_errors` tool
- **Memory leaks**: Profile with `--inspect` flag and Chrome DevTools
- **MCP connection failures**: Verify Next.js 16+, dev server running, and `next-devtools-mcp` in `.mcp.json`
- **Webpack/Turbopack crashes**: Turbopack is the default in 16 — reproduce with `next dev --webpack` / `next build --webpack` to isolate bundler issues
- **Deployment-specific bugs**: Test with `next build && next start` locally before deploying
