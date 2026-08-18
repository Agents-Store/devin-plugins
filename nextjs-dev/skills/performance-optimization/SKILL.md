---
name: performance-optimization
description: Next.js performance optimization patterns for images, fonts, bundles, and Core Web Vitals. This skill should be used when the user asks about "Next.js performance", "optimize Next.js app", "Core Web Vitals", "bundle size", "next/image optimization", "next/font", "lazy loading", "dynamic imports", or needs to improve the speed and efficiency of their Next.js application.
---

# Performance Optimization

Next.js includes built-in optimizations for images, fonts, scripts, and rendering. Apply these patterns to achieve excellent Core Web Vitals scores.

## Image Optimization with `next/image`

The `<Image>` component automatically optimizes images with lazy loading, responsive sizing, and modern formats (WebP/AVIF).

### Basic Usage

```tsx
import Image from 'next/image'

// Local image (auto width/height detection)
import heroImage from '@/public/hero.jpg'

export default function Hero() {
  return (
    <Image
      src={heroImage}
      alt="Hero banner"
      placeholder="blur"   // Auto blur placeholder for local images
      priority              // Preload — use for above-the-fold images
    />
  )
}
```

### Remote Images

```tsx
<Image
  src="https://images.example.com/photo.jpg"
  alt="Photo"
  width={800}
  height={600}
  sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
/>
```

Configure allowed remote sources in `next.config.ts`:

```ts
const nextConfig = {
  images: {
    remotePatterns: [
      { protocol: 'https', hostname: 'images.example.com' },
    ],
  },
}
```

### Image Best Practices

| Practice | Why |
|----------|-----|
| Always set `priority` on the LCP image | Eliminates lazy-load delay for the largest visible image |
| Use `sizes` prop for responsive images | Tells the browser which size to download at each breakpoint |
| Use `placeholder="blur"` for local images | Shows a low-quality preview while loading |
| Use `fill` prop for unknown dimensions | Image fills its parent container (set `position: relative` on parent) |
| Avoid layout shift | Always provide `width`/`height` or use `fill` |

## Font Optimization with `next/font`

`next/font` self-hosts fonts with zero layout shift. Fonts are loaded at build time and served from the same domain.

### Google Fonts

```tsx
import { Inter, JetBrains_Mono } from 'next/font/google'

const inter = Inter({
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-sans',
})

const jetbrainsMono = JetBrains_Mono({
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-mono',
})

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${inter.variable} ${jetbrainsMono.variable}`}>
      <body className="font-sans">{children}</body>
    </html>
  )
}
```

### Tailwind CSS Integration

Tailwind v4 (the create-next-app default) uses CSS-first configuration — no `tailwind.config.ts` needed for font variables:

```css
/* globals.css */
@import "tailwindcss";

@theme inline {
  --font-sans: var(--font-sans);
  --font-mono: var(--font-mono);
}
```

## Dynamic Imports & Code Splitting

### Component-level Code Splitting

```tsx
import dynamic from 'next/dynamic'

// Lazy load heavy components
const Chart = dynamic(() => import('@/components/chart'), {
  loading: () => <p>Loading chart...</p>,
})

// Skip SSR for browser-only components
const Map = dynamic(() => import('@/components/map'), {
  ssr: false,
  loading: () => <div className="h-96 bg-gray-100 animate-pulse" />,
})
```

### When to Use Dynamic Imports

| Scenario | Approach |
|----------|----------|
| Heavy library (chart, editor, map) | `dynamic(() => import(...))` |
| Browser-only library (uses `window`) | `dynamic(() => import(...), { ssr: false })` |
| Modal or dialog content | `dynamic(() => import(...))` — loads on demand |
| Above-the-fold content | Do NOT dynamic import — use regular import |

### Library-level Code Splitting

```tsx
// Only import what you need
import { format } from 'date-fns'          // Tree-shakeable
import { debounce } from 'lodash-es'       // ES module version
```

Avoid importing entire libraries (`import _ from 'lodash'`). Use tree-shakeable ES module versions.

## Bundle Size Optimization

### Analyze the Bundle

```bash
# Turbopack bundle analyzer (16.1+): interactive treemap on port 4000
next experimental-analyze

# Write static analysis files instead
next experimental-analyze --output
```

The analyzer filters by route, shows import chains, and provides separate client/server views. The older `@next/bundle-analyzer` (`ANALYZE=true`) is webpack-based and only works with `next build --webpack`.

### Common Bundle Bloaters

| Issue | Fix |
|-------|-----|
| Large icon library | Import individual icons: `import { Search } from 'lucide-react'` |
| Full lodash import | Use `lodash-es` or individual imports: `import debounce from 'lodash/debounce'` |
| Moment.js | Replace with `date-fns` or `dayjs` |
| CSS-in-JS runtime | Use Tailwind CSS or CSS Modules (zero runtime) |
| Heavy markdown parser | Use `next-mdx-remote` or dynamic import |

### Keep Client Components Small

Every component marked `'use client'` adds to the client JavaScript bundle. Strategies:
- Extract only the interactive part into a Client Component
- Keep data fetching and static rendering in Server Components
- Use composition (pass Server Components as `children` to Client Components)

## React Compiler

Automatic memoization without manual `useMemo`/`useCallback`. Stable since Next.js 16, but not enabled by default:

```ts
// next.config.ts
const nextConfig = {
  reactCompiler: true,  // requires: npm install babel-plugin-react-compiler@latest
}
```

The Babel-based compiler increases build time. Next.js 16.3 adds an experimental Rust-based compiler that runs inside Turbopack (34-46% faster dev-to-ready-page vs Babel):

```ts
const nextConfig = {
  experimental: { turbopackRustReactCompiler: true },  // 16.3+
}
```

`create-next-app` offers a `--react-compiler` flag for new projects.

## Core Web Vitals

### LCP (Largest Contentful Paint)

- Set `priority` on the hero/banner image
- Preload critical fonts with `next/font`
- Avoid layout shifts that delay the largest element
- Use `<Suspense>` to stream non-critical content

### FID/INP (First Input Delay / Interaction to Next Paint)

- Minimize client-side JavaScript
- Use Server Components for non-interactive UI
- Defer heavy computations with `requestIdleCallback` or Web Workers
- Avoid blocking the main thread during hydration

### CLS (Cumulative Layout Shift)

- Always specify image dimensions (`width`/`height` or `fill`)
- Use `next/font` to prevent font-swap layout shifts
- Reserve space for dynamic content with CSS `min-height`
- Avoid injecting content above existing content

## Rendering Strategy Selection

| Content Type | Strategy | Implementation |
|-------------|----------|----------------|
| Marketing pages | Static (SSG) | Default (no dynamic data) |
| Blog posts | ISR | `export const revalidate = 3600` |
| Product pages | ISR | `export const revalidate = 60` + `revalidateTag` on update |
| User dashboard | Dynamic + Streaming | `<Suspense>` boundaries |
| Search results | Dynamic | Access `searchParams` |
| Authenticated pages | Dynamic | Access `cookies()` |

## Script Optimization

```tsx
import Script from 'next/script'

// Analytics — load after page is interactive
<Script src="https://analytics.example.com/script.js" strategy="afterInteractive" />

// Non-critical widget — load when browser is idle
<Script src="https://widget.example.com/embed.js" strategy="lazyOnload" />

// Critical third-party — load before page hydration (rare)
<Script src="https://critical.example.com/script.js" strategy="beforeInteractive" />
```

## Prefetching

Next.js automatically prefetches `<Link>` destinations when they appear in the viewport. Control this behavior:

```tsx
import Link from 'next/link'

// Prefetch enabled (default)
<Link href="/dashboard">Dashboard</Link>

// Disable prefetch for rarely visited pages
<Link href="/terms" prefetch={false}>Terms</Link>
```

Next.js 16 rewrote prefetching: layout deduplication, incremental prefetching, cancellation when links leave the viewport, and hover prioritization all happen automatically. 16.3 can inline small prefetch payloads into the page (`prefetchInlining`), and `<Link prefetch={true}>` participates in Partial Prefetching when `cacheComponents` + `partialPrefetching` are enabled (see the `data-fetching` skill's Cache Components reference).

## Production Checklist

- [ ] Hero image has `priority` prop
- [ ] All images have `width`/`height` or `fill`
- [ ] Fonts use `next/font` (no external stylesheet links)
- [ ] Heavy components use `dynamic()` import
- [ ] `'use client'` only on components that need interactivity
- [ ] Bundle analyzed with `next experimental-analyze`
- [ ] No unused dependencies in `package.json`
- [ ] `output: 'standalone'` for Docker deployments
- [ ] Static pages use ISR where appropriate
- [ ] Third-party scripts use appropriate `strategy`
