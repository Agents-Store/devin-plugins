# Advanced Next.js API Reference

Extended API reference for core components, proxy, image loading, font configuration, and advanced config options.

## Table of Contents

- [Image Component](#image-component)
- [Font Optimization](#font-optimization)
- [Script Component](#script-component)
- [next.config.ts Key Options](#nextconfigts-key-options)
- [Proxy API (proxy.ts)](#proxy-api-proxyts)
- [Image Loader Configuration](#image-loader-configuration)
- [Font Configuration](#font-configuration)
- [Advanced next.config.ts Options](#advanced-nextconfigts-options)

## Image Component

```tsx
import Image from 'next/image'

<Image
  src="/hero.jpg"
  alt="Hero image"
  width={800}
  height={400}
  priority           // Load eagerly (for above-the-fold)
  placeholder="blur" // Show blur while loading (requires blurDataURL for remote)
  sizes="(max-width: 768px) 100vw, 50vw"
/>
```

## Font Optimization

```tsx
import { Inter, Roboto_Mono } from 'next/font/google'

const inter = Inter({ subsets: ['latin'], display: 'swap' })
const robotoMono = Roboto_Mono({ subsets: ['latin'], variable: '--font-mono' })

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${inter.className} ${robotoMono.variable}`}>
      <body>{children}</body>
    </html>
  )
}
```

## Script Component

```tsx
import Script from 'next/script'

<Script src="https://analytics.example.com/script.js" strategy="afterInteractive" />
```

Strategies: `beforeInteractive`, `afterInteractive` (default), `lazyOnload`, `worker`.

## next.config.ts Key Options

```ts
import type { NextConfig } from 'next'

const nextConfig: NextConfig = {
  images: {
    remotePatterns: [
      { protocol: 'https', hostname: 'images.example.com' },
    ],
  },
  async redirects() {
    return [{ source: '/old', destination: '/new', permanent: true }]
  },
  async rewrites() {
    return [{ source: '/api/:path*', destination: 'https://backend.example.com/:path*' }]
  },
  async headers() {
    return [{ source: '/:path*', headers: [{ key: 'X-Frame-Options', value: 'DENY' }] }]
  },
  output: 'standalone',
  env: { CUSTOM_KEY: 'value' },
}

export default nextConfig
```

## Cache & Revalidation Functions

### `revalidatePath(path, type?)`

```tsx
import { revalidatePath } from 'next/cache'

revalidatePath('/posts')          // Revalidate specific path
revalidatePath('/posts', 'layout') // Revalidate layout and all child pages
revalidatePath('/', 'layout')      // Revalidate everything
```

### `revalidateTag(tag, profile)`

```tsx
import { revalidateTag } from 'next/cache'

revalidateTag('posts', 'max')           // SWR invalidation with a cacheLife profile
revalidateTag('posts', { expire: 3600 }) // Inline expire override
```

The single-argument form is deprecated since Next.js 16.

### `updateTag(tag)` / `refresh()` (Server Actions only)

```tsx
import { updateTag, refresh } from 'next/cache'

updateTag('posts')  // Expire + immediately re-read fresh data (read-your-writes)
refresh()           // Refresh uncached data — server-side router.refresh()
```

### `unstable_cache()` (legacy)

Legacy API superseded by `'use cache'` (Cache Components). Still valid for data that must persist across deploys:

```tsx
import { unstable_cache } from 'next/cache'

const getCachedUser = unstable_cache(
  async (id: string) => db.user.findUnique({ where: { id } }),
  ['user'],
  { revalidate: 3600, tags: ['user'] }
)
```

## Proxy API (proxy.ts)

Define `proxy.ts` at the project root with `export function proxy(request: NextRequest)` (named or default export). Proxy runs on the **Node.js runtime only** (a `runtime` segment config throws in proxy files). `middleware.ts` is deprecated since Next.js 16 — migrate with `npx @next/codemod@canary middleware-to-proxy .`. A `NextProxy` type is available from `'next/server'`.

### `NextRequest`

Extends the standard `Request` with additional properties:

| Property | Type | Description |
|----------|------|-------------|
| `nextUrl` | `NextURL` | Parsed URL with Next.js specific properties (`basePath`, `buildId`, `pathname`, `searchParams`) |
| `cookies` | `RequestCookies` | Cookie access (`get`, `getAll`, `set`, `delete`, `has`, `clear`) |

> `geo` and `ip` were removed in Next.js 15.0. Use platform helpers (`geolocation()`/`ipAddress()` from `@vercel/functions`) or read the `x-forwarded-for` header.

### `NextResponse`

| Method | Description |
|--------|-------------|
| `NextResponse.next()` | Continue past the proxy to the route |
| `NextResponse.redirect(url)` | Redirect to a different URL |
| `NextResponse.rewrite(url)` | Rewrite request to a different URL (URL stays the same) |
| `NextResponse.json(data)` | Return a JSON response |

### Proxy Matcher

```ts
export const config = {
  matcher: [
    // Match specific paths
    '/dashboard/:path*',
    '/api/:path*',
    // Match all except static files and _next
    '/((?!_next/static|_next/image|favicon.ico).*)',
  ],
}
```

### Setting Cookies in Proxy

```ts
// proxy.ts
export function proxy(request: NextRequest) {
  const response = NextResponse.next()
  response.cookies.set('visited', 'true', {
    httpOnly: true,
    secure: true,
    sameSite: 'lax',
    maxAge: 60 * 60 * 24, // 1 day
  })
  return response
}
```

### Setting Headers in Proxy

```ts
// proxy.ts
export function proxy(request: NextRequest) {
  const requestHeaders = new Headers(request.headers)
  requestHeaders.set('x-request-id', crypto.randomUUID())

  const response = NextResponse.next({
    request: { headers: requestHeaders },
  })
  response.headers.set('x-response-time', Date.now().toString())
  return response
}
```

## Image Loader Configuration

### Remote Patterns

```ts
// next.config.ts
const nextConfig = {
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: '**.example.com',  // Wildcard subdomain
        port: '',
        pathname: '/images/**',
      },
    ],
    // Image sizes for responsive images
    deviceSizes: [640, 750, 828, 1080, 1200, 1920, 2048, 3840],
    imageSizes: [16, 32, 48, 64, 96, 128, 256, 384],
    // Formats
    formats: ['image/avif', 'image/webp'],
    // Custom loader
    loader: 'custom',
    loaderFile: './lib/image-loader.ts',
  },
}
```

**Next.js 16 image defaults changed:**
- `qualities` defaults to `[75]` — a `quality` prop is coerced to the closest configured value, so add values (e.g. `qualities: [50, 75, 90]`) to use other qualities
- `minimumCacheTTL` default is now `14400` (4 hours, up from 60 seconds)
- Local `src` values with query strings require `images.localPatterns`
- Optimization of private-network (local IP) upstreams is blocked by default — set `images.dangerouslyAllowLocalIP: true` when needed
- `maximumRedirects` is now 3
- `images.domains` is deprecated (use `remotePatterns`); `next/legacy/image` is deprecated

### Custom Image Loader

```ts
// lib/image-loader.ts
export default function cloudinaryLoader({
  src,
  width,
  quality,
}: {
  src: string
  width: number
  quality?: number
}) {
  const params = ['f_auto', 'c_limit', `w_${width}`, `q_${quality || 'auto'}`]
  return `https://res.cloudinary.com/demo/image/upload/${params.join(',')}${src}`
}
```

## Font Configuration

### Local Fonts

```tsx
import localFont from 'next/font/local'

const myFont = localFont({
  src: [
    { path: './fonts/MyFont-Regular.woff2', weight: '400', style: 'normal' },
    { path: './fonts/MyFont-Bold.woff2', weight: '700', style: 'normal' },
    { path: './fonts/MyFont-Italic.woff2', weight: '400', style: 'italic' },
  ],
  display: 'swap',
  variable: '--font-my-font',
})
```

### Font Options

| Option | Type | Description |
|--------|------|-------------|
| `subsets` | `string[]` | Character subsets (`'latin'`, `'cyrillic'`, etc.) |
| `weight` | `string \| string[]` | Font weights (`'400'`, `['400', '700']`) |
| `style` | `string \| string[]` | Font styles (`'normal'`, `'italic'`) |
| `display` | `string` | CSS `font-display` (`'swap'`, `'block'`, `'fallback'`, `'optional'`) |
| `variable` | `string` | CSS variable name (`'--font-sans'`) |
| `preload` | `boolean` | Whether to preload (default: `true`) |
| `adjustFontFallback` | `boolean` | Adjust fallback font metrics (default: `true`) |

## Advanced next.config.ts Options

### Turbopack Configuration

```ts
const nextConfig = {
  turbopack: {
    rules: {
      '*.svg': {
        loaders: ['@svgr/webpack'],
        as: '*.js',
      },
    },
    resolveAlias: {
      underscore: 'lodash',
    },
  },
}
```

### Webpack Configuration

```ts
const nextConfig = {
  webpack: (config, { buildId, dev, isServer, defaultLoaders, nextRuntime, webpack }) => {
    config.plugins.push(new webpack.DefinePlugin({ 'process.env.BUILD_ID': JSON.stringify(buildId) }))
    return config
  },
}
```

### Instrumentation

```ts
// instrumentation.ts (project root)
export async function register() {
  if (process.env.NEXT_RUNTIME === 'nodejs') {
    // Initialize server-side monitoring (e.g., Sentry, OpenTelemetry)
  }
}
```

### Security Headers

```ts
const securityHeaders = [
  { key: 'X-DNS-Prefetch-Control', value: 'on' },
  { key: 'Strict-Transport-Security', value: 'max-age=63072000; includeSubDomains; preload' },
  { key: 'X-Frame-Options', value: 'SAMEORIGIN' },
  { key: 'X-Content-Type-Options', value: 'nosniff' },
  { key: 'Referrer-Policy', value: 'origin-when-cross-origin' },
  { key: 'Permissions-Policy', value: 'camera=(), microphone=(), geolocation=()' },
]

const nextConfig = {
  async headers() {
    return [{ source: '/:path*', headers: securityHeaders }]
  },
}
```

### Content Security Policy

```ts
// proxy.ts
import { NextResponse } from 'next/server'

export function proxy(request: NextRequest) {
  const nonce = Buffer.from(crypto.randomUUID()).toString('base64')
  const csp = `
    default-src 'self';
    script-src 'self' 'nonce-${nonce}' 'strict-dynamic';
    style-src 'self' 'nonce-${nonce}';
    img-src 'self' blob: data:;
    font-src 'self';
    object-src 'none';
    base-uri 'self';
    form-action 'self';
    frame-ancestors 'none';
    upgrade-insecure-requests;
  `.replace(/\n/g, '')

  const response = NextResponse.next()
  response.headers.set('Content-Security-Policy', csp)
  response.headers.set('x-nonce', nonce)
  return response
}
```
