---
name: sitemap-robots
description: Sitemap and robots.txt configuration for Next.js App Router. This skill should be used when the user asks about "sitemap", "sitemap.xml", "robots.txt", "robots.ts", "next-sitemap", "XML sitemap", "sitemap generation", "block crawlers", "crawl budget", or needs to configure how search engines discover and crawl their pages.
---

# Sitemap & Robots.txt

Next.js App Router has built-in support for `sitemap.ts` and `robots.ts` — file conventions that generate `sitemap.xml` and `robots.txt` at build/request time.

## sitemap.ts — Basic

Create `app/sitemap.ts` to generate `/sitemap.xml`:

```tsx
// app/sitemap.ts
import type { MetadataRoute } from 'next'

const BASE_URL = process.env.NEXT_PUBLIC_SITE_URL || 'https://yourdomain.com'

export default function sitemap(): MetadataRoute.Sitemap {
  return [
    { url: BASE_URL, lastModified: new Date(), changeFrequency: 'daily', priority: 1 },
    { url: `${BASE_URL}/about`, lastModified: new Date(), changeFrequency: 'monthly', priority: 0.8 },
    { url: `${BASE_URL}/blog`, lastModified: new Date(), changeFrequency: 'weekly', priority: 0.9 },
    { url: `${BASE_URL}/contact`, lastModified: new Date(), changeFrequency: 'yearly', priority: 0.5 },
  ]
}
```

## sitemap.ts — Dynamic (CMS/Database)

Fetch pages from your CMS or database:

```tsx
// app/sitemap.ts
import type { MetadataRoute } from 'next'

const BASE_URL = process.env.NEXT_PUBLIC_SITE_URL || 'https://yourdomain.com'

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  // Fetch dynamic pages from CMS
  const posts = await getAllPosts()
  const products = await getAllProducts()

  const postEntries: MetadataRoute.Sitemap = posts.map((post) => ({
    url: `${BASE_URL}/blog/${post.slug}`,
    lastModified: new Date(post.updatedAt),
    changeFrequency: 'weekly',
    priority: 0.7,
  }))

  const productEntries: MetadataRoute.Sitemap = products.map((product) => ({
    url: `${BASE_URL}/products/${product.slug}`,
    lastModified: new Date(product.updatedAt),
    changeFrequency: 'daily',
    priority: 0.8,
  }))

  return [
    { url: BASE_URL, lastModified: new Date(), changeFrequency: 'daily', priority: 1 },
    ...postEntries,
    ...productEntries,
  ]
}
```

## Multiple Sitemaps (Large Sites)

For sites with more than 50,000 URLs, use `generateSitemaps` to split into multiple sitemap files:

```tsx
// app/sitemap.ts
import type { MetadataRoute } from 'next'

const URLS_PER_SITEMAP = 50000

export async function generateSitemaps() {
  const totalProducts = await getProductCount()
  const sitemapCount = Math.ceil(totalProducts / URLS_PER_SITEMAP)

  return Array.from({ length: sitemapCount }, (_, i) => ({ id: i }))
}

export default async function sitemap(
  props: { id: Promise<string> }
): Promise<MetadataRoute.Sitemap> {
  const id = Number(await props.id)
  const start = id * URLS_PER_SITEMAP
  const products = await getProducts({ offset: start, limit: URLS_PER_SITEMAP })

  return products.map((product) => ({
    url: `https://yourdomain.com/products/${product.slug}`,
    lastModified: new Date(product.updatedAt),
  }))
}
```

This generates `/sitemap/0.xml`, `/sitemap/1.xml`, etc. Next.js does **not** generate a sitemap index for these files, so `/sitemap.xml` is not a list of them. Do one of:

- List every generated URL in `robots.ts` — the `sitemap` field accepts an array of URLs
- Submit each generated sitemap in Google Search Console → Sitemaps
- Serve your own index from a route handler:

```ts
// app/sitemap-index.xml/route.ts
const BASE_URL = process.env.NEXT_PUBLIC_SITE_URL || 'https://yourdomain.com'
const URLS_PER_SITEMAP = 50000 // keep equal to the constant in app/sitemap.ts (or share it from a module)

export async function GET() {
  const sitemapCount = Math.ceil((await getProductCount()) / URLS_PER_SITEMAP)
  const entries = Array.from(
    { length: sitemapCount },
    (_, i) => `<sitemap><loc>${BASE_URL}/sitemap/${i}.xml</loc></sitemap>`
  ).join('')

  return new Response(
    `<?xml version="1.0" encoding="UTF-8"?><sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">${entries}</sitemapindex>`,
    { headers: { 'Content-Type': 'application/xml' } }
  )
}
```

## Nested Sitemaps

Place `sitemap.ts` in route segments for section-specific sitemaps:

```
app/
  sitemap.ts              → /sitemap.xml (main pages)
  blog/sitemap.ts         → /blog/sitemap.xml (blog posts)
  products/sitemap.ts     → /products/sitemap.xml (products)
```

## robots.ts — Basic

```tsx
// app/robots.ts
import type { MetadataRoute } from 'next'

export default function robots(): MetadataRoute.Robots {
  return {
    rules: { userAgent: '*', allow: '/', disallow: ['/api/', '/admin/'] },
    sitemap: `${process.env.NEXT_PUBLIC_SITE_URL}/sitemap.xml`,
  }
}
```

## robots.ts — Production vs Staging

Block indexing on non-production environments:

```tsx
// app/robots.ts
import type { MetadataRoute } from 'next'

export default function robots(): MetadataRoute.Robots {
  const baseUrl = process.env.NEXT_PUBLIC_SITE_URL || 'https://yourdomain.com'
  const isProduction = process.env.VERCEL_ENV === 'production'

  if (!isProduction) {
    return { rules: { userAgent: '*', disallow: ['/'] } }
  }

  return {
    rules: [
      // Do not disallow /_next/ — it serves the JS, CSS and images Google needs to render pages
      { userAgent: '*', allow: '/', disallow: ['/api/', '/admin/'] },
      { userAgent: 'GPTBot', disallow: ['/'] },
      { userAgent: 'ClaudeBot', disallow: ['/'] },
      { userAgent: 'CCBot', disallow: ['/'] },
      { userAgent: 'Google-Extended', disallow: ['/'] },
    ],
    sitemap: `${baseUrl}/sitemap.xml`,
  }
}
```

## Do Not Block `/_next/`

Next.js serves its JavaScript, CSS and optimized images from `/_next/static` and `/_next/image`. Googlebot renders pages with JavaScript, and Google Search cannot render JavaScript or CSS from files that robots.txt blocks, which can hurt how the page is understood and indexed. Keep `/_next/` crawlable and disallow only real private paths (`/api/`, `/admin/`, ...).

## AI Crawler Management (2025-2026)

Crawlers to manage in `robots.txt`. Separate training crawlers from search and user-initiated fetchers:

| Crawler | Purpose | Recommendation |
|---------|---------|----------------|
| `Googlebot` | Google Search indexing | Allow |
| `Bingbot` | Bing Search indexing | Allow |
| `GPTBot` | OpenAI training data | Block (unless opted in) |
| `OAI-SearchBot` | ChatGPT search results; opted-out sites are not shown in ChatGPT search answers | Allow (traffic) |
| `ChatGPT-User` | User-initiated fetches from ChatGPT; OpenAI says robots.txt rules may not apply | Cannot be controlled via robots.txt |
| `ClaudeBot` | Anthropic training data | Block (unless opted in) |
| `Claude-SearchBot` | Anthropic search result quality and relevance | Allow (traffic) |
| `Claude-User` | User-initiated fetches when a Claude user asks about a page | Allow (a user asked for your page) |
| `CCBot` | Common Crawl / AI training | Block (unless opted in) |
| `Google-Extended` | Control token for Gemini training and grounding. Does **not** affect Google Search inclusion, ranking or AI Overviews | Block (unless opted in) |
| `Applebot-Extended` | Apple AI training | Block (unless opted in) |

Anthropic documents its three crawlers at support.claude.com (Anthropic's crawler article, updated 2026-04); each one is controlled by its own `User-agent` entry in robots.txt. Differentiate beneficial crawlers (drive traffic) from training scrapers (use your content without attribution).

## Multilingual Sitemap (Hreflang)

```tsx
// app/sitemap.ts
import type { MetadataRoute } from 'next'

const BASE_URL = process.env.NEXT_PUBLIC_SITE_URL || 'https://yourdomain.com'
const LOCALES = ['en', 'de', 'fr']
const ROUTES = ['', '/about', '/blog']

export default function sitemap(): MetadataRoute.Sitemap {
  const entries: MetadataRoute.Sitemap = []

  for (const locale of LOCALES) {
    for (const route of ROUTES) {
      entries.push({
        url: `${BASE_URL}/${locale}${route}`,
        lastModified: new Date(),
        alternates: {
          languages: Object.fromEntries([
            ...LOCALES.map((l) => [l, `${BASE_URL}/${l}${route}`]),
            ['x-default', `${BASE_URL}/en${route}`],
          ]),
        },
      })
    }
  }

  return entries
}
```

## When to Use next-sitemap

The built-in `sitemap.ts` covers most use cases. Consider `next-sitemap` only for:

- Complex `transform` functions that modify URLs based on external data
- Server-side sitemap generation (App Router `sitemap.ts` is already server-rendered)
- Legacy Pages Router projects

For new App Router projects, prefer the built-in approach.

## Priority & changeFrequency Guide

| Page Type | Priority | changeFrequency |
|-----------|----------|-----------------|
| Homepage | 1.0 | daily |
| Category pages | 0.8-0.9 | weekly |
| Blog posts | 0.6-0.7 | weekly |
| Product pages | 0.7-0.8 | daily |
| Static pages (about, contact) | 0.5-0.6 | monthly |
| Legal pages (terms, privacy) | 0.3 | yearly |

Note: Google has stated that `priority` and `changeFrequency` are largely ignored. `lastModified` with an accurate date is the most useful signal. Include priority for other search engines that may still use it.

## Verification

After setting up sitemap and robots:

1. Visit `/sitemap.xml` — valid XML with all pages
2. Visit `/robots.txt` — correct rules
3. Submit sitemap URL in Google Search Console → Sitemaps
4. Check Google Search Console → Settings → Crawl stats for crawl activity
